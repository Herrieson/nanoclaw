from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil

from .generated_task_validator import (
    autofix_prompt_repo_asset_paths,
    autofix_verify_rules_runtime_paths,
)
from .task_normalizer import normalize_task_file


TEXT_FILE_SUFFIXES = frozenset({".md", ".py", ".yaml", ".yml", ".json", ".txt"})
ROUND_ID_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class ImportedTask:
    round_id: str
    source_task_id: str
    imported_task_id: str
    task_path: Path
    prompt_path: Path | None
    task_dir: Path | None

    def to_dict(self) -> dict[str, object]:
        return {
            "round_id": self.round_id,
            "source_task_id": self.source_task_id,
            "imported_task_id": self.imported_task_id,
            "task_path": str(self.task_path),
            "prompt_path": str(self.prompt_path) if self.prompt_path is not None else None,
            "task_dir": str(self.task_dir) if self.task_dir is not None else None,
        }


def default_round_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"round_{stamp}"


def normalize_round_id(raw_value: str) -> str:
    normalized = ROUND_ID_PATTERN.sub("_", raw_value.strip().lower()).strip("_")
    if not normalized:
        raise ValueError("round_id must contain at least one ASCII letter or digit.")
    return normalized


def discover_staged_task_paths(staging_root: Path) -> list[Path]:
    if not staging_root.exists():
        return []
    return sorted(
        path.resolve()
        for path in staging_root.rglob("tasks/*.yaml")
        if path.is_file()
    )


def import_staged_tasks(
    staging_root: Path,
    *,
    repo_root: Path,
    round_id: str,
    max_tasks: int | None = None,
) -> list[ImportedTask]:
    resolved_staging = staging_root.expanduser().resolve()
    resolved_repo = repo_root.expanduser().resolve()
    normalized_round = normalize_round_id(round_id)
    staged_task_paths = discover_staged_task_paths(resolved_staging)
    if max_tasks is not None:
        staged_task_paths = staged_task_paths[:max_tasks]

    imported: list[ImportedTask] = []
    next_index = 1
    for staged_task_path in staged_task_paths:
        source_task_id = staged_task_path.stem
        imported_task_id, next_index = _allocate_task_id(
            resolved_repo,
            normalized_round=normalized_round,
            start_index=next_index,
        )
        imported.append(
            _import_single_task(
                staged_task_path,
                repo_root=resolved_repo,
                round_id=normalized_round,
                source_task_id=source_task_id,
                imported_task_id=imported_task_id,
            )
        )
    return imported


def write_import_manifest(imported_tasks: list[ImportedTask], *, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for item in imported_tasks:
            handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")


def _allocate_task_id(
    repo_root: Path,
    *,
    normalized_round: str,
    start_index: int,
) -> tuple[str, int]:
    index = start_index
    while True:
        candidate = f"data_{normalized_round}_{index:04d}"
        if _task_id_available(repo_root, candidate):
            return candidate, index + 1
        index += 1


def _task_id_available(repo_root: Path, task_id: str) -> bool:
    candidates = (
        repo_root / "tasks" / f"{task_id}.yaml",
        repo_root / "tasks" / "prompts" / f"{task_id}.md",
        repo_root / "tasks" / task_id,
        repo_root / "assets" / task_id,
        repo_root / "results" / task_id,
    )
    return not any(path.exists() for path in candidates)


def _import_single_task(
    staged_task_path: Path,
    *,
    repo_root: Path,
    round_id: str,
    source_task_id: str,
    imported_task_id: str,
) -> ImportedTask:
    repo_tasks_root = repo_root / "tasks"
    repo_prompts_root = repo_tasks_root / "prompts"
    repo_prompts_root.mkdir(parents=True, exist_ok=True)

    destination_task_path = repo_tasks_root / f"{imported_task_id}.yaml"
    destination_prompt_path: Path | None = None
    destination_task_dir: Path | None = None

    staged_tasks_dir = staged_task_path.parent
    prompt_source_path = staged_tasks_dir / "prompts" / f"{source_task_id}.md"
    task_dir_source_path = staged_tasks_dir / source_task_id

    shutil.copy2(staged_task_path, destination_task_path)
    _rewrite_text_file(destination_task_path, source_task_id=source_task_id, imported_task_id=imported_task_id)

    if prompt_source_path.exists():
        destination_prompt_path = repo_prompts_root / f"{imported_task_id}.md"
        shutil.copy2(prompt_source_path, destination_prompt_path)
        _rewrite_text_file(
            destination_prompt_path,
            source_task_id=source_task_id,
            imported_task_id=imported_task_id,
        )

    if task_dir_source_path.exists():
        destination_task_dir = repo_tasks_root / imported_task_id
        shutil.copytree(task_dir_source_path, destination_task_dir)
        for file_path in destination_task_dir.rglob("*"):
            if not file_path.is_file() or file_path.suffix not in TEXT_FILE_SUFFIXES:
                continue
            _rewrite_text_file(
                file_path,
                source_task_id=source_task_id,
                imported_task_id=imported_task_id,
            )

    normalize_task_file(destination_task_path, create_backup=False)
    autofix_prompt_repo_asset_paths(destination_task_path, repo_root=repo_root)
    autofix_verify_rules_runtime_paths(destination_task_path, repo_root=repo_root)

    return ImportedTask(
        round_id=round_id,
        source_task_id=source_task_id,
        imported_task_id=imported_task_id,
        task_path=destination_task_path.resolve(),
        prompt_path=destination_prompt_path.resolve() if destination_prompt_path is not None else None,
        task_dir=destination_task_dir.resolve() if destination_task_dir is not None else None,
    )


def _rewrite_text_file(
    path: Path,
    *,
    source_task_id: str,
    imported_task_id: str,
) -> None:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(source_task_id, imported_task_id)
    path.write_text(updated, encoding="utf-8")
