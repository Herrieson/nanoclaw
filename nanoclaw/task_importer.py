from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil
import textwrap
from typing import Any

import yaml

from .generated_task_validator import (
    autofix_prompt_repo_asset_paths,
    autofix_verify_rules_runtime_paths,
)
from .task_normalizer import normalize_task_file


TEXT_FILE_SUFFIXES = frozenset({".md", ".py", ".yaml", ".yml", ".json", ".txt"})
ROUND_ID_PATTERN = re.compile(r"[^a-z0-9]+")
SKILL_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
BUILDER_REPO_ASSET_PATTERNS = (
    re.compile(r"""(?x)["']assets/data_[A-Za-z0-9_-]+(?:/|["'])"""),
    re.compile(r"""(?x)Path\(\s*["']assets(?:/|["'])"""),
    re.compile(r"""(?x)os\.path\.join\(\s*["']assets["']"""),
    re.compile(r"""(?x)["']/workspace(?:/|["'])"""),
)


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
    existing_round_count = _count_existing_round_tasks(
        resolved_repo,
        normalized_round=normalized_round,
    )
    if existing_round_count:
        staged_task_paths = staged_task_paths[existing_round_count:]
    if max_tasks is not None:
        staged_task_paths = staged_task_paths[:max_tasks]

    imported: list[ImportedTask] = []
    next_index = existing_round_count + 1
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


def _count_existing_round_tasks(repo_root: Path, *, normalized_round: str) -> int:
    pattern = f"data_{normalized_round}_*.yaml"
    return len(list((repo_root / "tasks").glob(pattern)))


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
    staged_record_root = staged_tasks_dir.parent
    prompt_source_paths = _discover_prompt_source_paths(staged_tasks_dir, source_task_id)
    task_dir_source_path = staged_tasks_dir / source_task_id
    skill_source_dir = staged_record_root / "skills" / source_task_id

    shutil.copy2(staged_task_path, destination_task_path)
    _rewrite_text_file(destination_task_path, source_task_id=source_task_id, imported_task_id=imported_task_id)
    _rewrite_task_yaml_metadata(destination_task_path)

    for prompt_source_path in prompt_source_paths:
        destination_name = imported_task_id + prompt_source_path.name[len(source_task_id) :]
        destination_path = repo_prompts_root / destination_name
        shutil.copy2(prompt_source_path, destination_path)
        _rewrite_text_file(
            destination_path,
            source_task_id=source_task_id,
            imported_task_id=imported_task_id,
        )
        if destination_prompt_path is None:
            destination_prompt_path = destination_path

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
        _wrap_builder_for_workspace_root(destination_task_dir / "env_builder.py", imported_task_id)

    imported_skill_slugs = _import_task_local_skills(
        skill_source_dir,
        repo_root=repo_root,
        source_task_id=source_task_id,
        imported_task_id=imported_task_id,
    )

    normalize_task_file(destination_task_path, create_backup=False)
    if imported_skill_slugs:
        _merge_available_skills(destination_task_path, imported_skill_slugs)
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


def _discover_prompt_source_paths(staged_tasks_dir: Path, source_task_id: str) -> list[Path]:
    prompts_dir = staged_tasks_dir / "prompts"
    if not prompts_dir.exists():
        return []
    return sorted(
        path
        for path in prompts_dir.glob(f"{source_task_id}*.md")
        if path.is_file()
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


def _import_task_local_skills(
    skill_source_dir: Path,
    *,
    repo_root: Path,
    source_task_id: str,
    imported_task_id: str,
) -> list[str]:
    if not skill_source_dir.exists() or not skill_source_dir.is_dir():
        return []

    repo_skills_root = repo_root / "skills"
    repo_skills_root.mkdir(parents=True, exist_ok=True)
    imported_slugs: list[str] = []

    base_names = sorted({path.stem for path in skill_source_dir.glob("*.md")} | {path.stem for path in skill_source_dir.glob("*.py")})
    for base_name in base_names:
        markdown_path = skill_source_dir / f"{base_name}.md"
        slug = _task_local_skill_slug(imported_task_id, base_name)
        destination_dir = repo_skills_root / slug
        if destination_dir.exists():
            shutil.rmtree(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        if markdown_path.exists():
            skill_markdown = markdown_path.read_text(encoding="utf-8")
        if not markdown_path.exists() or not skill_markdown.strip():
            skill_markdown = _fallback_skill_markdown(base_name)
        skill_markdown = skill_markdown.replace(source_task_id, imported_task_id)
        (destination_dir / "SKILL.md").write_text(
            _to_skill_document(skill_markdown, slug=slug, fallback_name=base_name),
            encoding="utf-8",
        )

        python_path = markdown_path.with_suffix(".py")
        if python_path.exists():
            shutil.copy2(python_path, destination_dir / python_path.name)
            _rewrite_text_file(
                destination_dir / python_path.name,
                source_task_id=source_task_id,
                imported_task_id=imported_task_id,
            )

        imported_slugs.append(slug)

    return imported_slugs


def _fallback_skill_markdown(base_name: str) -> str:
    display_name = base_name.replace("_", " ").replace("-", " ").title()
    script_name = f"{base_name}.py"
    return "\n".join(
        [
            f"# {display_name}",
            "",
            f"Task-local helper script `{script_name}`. Read this skill before invoking the script.",
            "",
            "Use the adjacent Python script with the arguments requested by the task prompt.",
        ]
    )


def _task_local_skill_slug(task_id: str, base_name: str) -> str:
    raw_slug = f"{task_id}__{base_name}".lower()
    normalized = SKILL_SLUG_PATTERN.sub("-", raw_slug).strip("-")
    return normalized or task_id


def _to_skill_document(skill_markdown: str, *, slug: str, fallback_name: str) -> str:
    stripped = skill_markdown.strip()
    if stripped.startswith("---\n"):
        return stripped + "\n"
    name = _extract_markdown_title(stripped) or fallback_name.replace("_", " ").replace("-", " ").title()
    description = _extract_skill_description(stripped, fallback=name)
    return "\n".join(
        [
            "---",
            f"name: {_quote_frontmatter_value(name)}",
            f"description: {description}",
            "aliases:",
            f"  - {fallback_name}",
            f"  - {slug}",
            "---",
            "",
            stripped,
            "",
        ]
    )


def _extract_markdown_title(markdown: str) -> str | None:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                return title
    return None


def _extract_skill_description(markdown: str, *, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("**"):
            continue
        return _quote_frontmatter_value(stripped[:200])
    return _quote_frontmatter_value(fallback)


def _quote_frontmatter_value(value: str) -> str:
    escaped = value.replace('"', "'")
    return f'"{escaped}"'


def _merge_available_skills(task_yaml_path: Path, skill_slugs: list[str]) -> None:
    payload = yaml.safe_load(task_yaml_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return

    skills = payload.get("skills")
    if not isinstance(skills, dict):
        skills = {}
        payload["skills"] = skills

    available = skills.get("available")
    available_items: list[str] = []
    if isinstance(available, str) and available.strip():
        available_items.append(available.strip())
    elif isinstance(available, list):
        available_items.extend(item.strip() for item in available if isinstance(item, str) and item.strip())

    seen = set(available_items)
    for slug in skill_slugs:
        if slug in seen:
            continue
        available_items.append(slug)
        seen.add(slug)

    skills["available"] = available_items
    task_yaml_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _rewrite_task_yaml_metadata(task_yaml_path: Path) -> None:
    original = task_yaml_path.read_text(encoding="utf-8")
    original = _quote_fragile_top_level_scalars(original)
    payload = yaml.safe_load(original) or {}
    if not isinstance(payload, dict):
        updated = original.replace("tasks/prompts/", "prompts/")
        if updated != original:
            task_yaml_path.write_text(updated, encoding="utf-8")
        return

    changed = False

    for key in ("prompt", "prompt_file"):
        value = payload.get(key)
        if isinstance(value, str):
            normalized = _normalize_prompt_reference(value)
            if normalized != value:
                payload[key] = normalized
                changed = True

    prompts = payload.get("prompts")
    normalized_prompts = _normalize_import_prompt_sources(prompts)
    if normalized_prompts is not None and normalized_prompts != prompts:
        payload["prompts"] = normalized_prompts
        changed = True

    sessions = payload.get("sessions")
    if isinstance(sessions, list):
        for item in sessions:
            if not isinstance(item, dict):
                continue
            prompt = item.get("prompt")
            if not isinstance(prompt, str):
                continue
            normalized = _normalize_prompt_reference(prompt)
            if normalized != prompt:
                item["prompt"] = normalized
                changed = True

    if prompts is None:
        fallback_paths: list[str] = []
        for key in ("prompt", "prompt_file"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                fallback_paths.append(_normalize_prompt_reference(value))
        if fallback_paths:
            payload["prompts"] = fallback_paths
            changed = True

    if not changed:
        if original != task_yaml_path.read_text(encoding="utf-8"):
            task_yaml_path.write_text(original, encoding="utf-8")
        return
    task_yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _quote_fragile_top_level_scalars(text: str) -> str:
    lines: list[str] = []
    changed = False
    for line in text.splitlines():
        match = re.fullmatch(r"(name|description):\s+(.+)", line)
        if not match:
            lines.append(line)
            continue
        value = match.group(2).strip()
        if value.startswith(("'", '"', "|", ">")):
            lines.append(line)
            continue
        lines.append(f"{match.group(1)}: {json.dumps(value, ensure_ascii=False)}")
        changed = True
    if not changed:
        return text
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _normalize_import_prompt_sources(prompts: Any) -> Any | None:
    if isinstance(prompts, str):
        return _normalize_prompt_reference(prompts)

    if isinstance(prompts, list):
        normalized_items: list[Any] = []
        changed = False
        for item in prompts:
            if isinstance(item, str):
                normalized = _normalize_prompt_reference(item)
                normalized_items.append(normalized)
                changed = changed or normalized != item
                continue
            if isinstance(item, dict):
                extracted = _extract_prompt_path_from_mapping(item)
                if extracted is not None:
                    normalized_items.append(extracted)
                    changed = True
                    continue
            normalized_items.append(item)
        return normalized_items if changed else prompts

    if isinstance(prompts, dict):
        files = prompts.get("files")
        if isinstance(files, str):
            return {"files": [_normalize_prompt_reference(files)]}
        if isinstance(files, list):
            normalized_files = [
                _normalize_prompt_reference(item)
                for item in files
                if isinstance(item, str) and item.strip()
            ]
            return {"files": normalized_files} if normalized_files else {"files": []}

        extracted_paths: list[str] = []
        for key in ("file", "path", "main", "user", "assistant", "system", "prompt"):
            value = prompts.get(key)
            if isinstance(value, str) and value.strip():
                extracted_paths.append(_normalize_prompt_reference(value))
        inline = prompts.get("inline")
        if isinstance(inline, list):
            if all(isinstance(item, str) and item.strip().endswith(".md") for item in inline):
                extracted_paths.extend(
                    _normalize_prompt_reference(item)
                    for item in inline
                )
        if extracted_paths:
            return extracted_paths
        return prompts

    return None


def _extract_prompt_path_from_mapping(item: dict[str, Any]) -> str | None:
    for key in ("file", "path", "main", "user", "assistant", "system", "prompt"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return _normalize_prompt_reference(value)
    return None


def _normalize_prompt_reference(value: str) -> str:
    normalized = value.strip().replace("tasks/prompts/", "prompts/")
    if "/" not in normalized and Path(normalized).suffix.lower() != ".md":
        return f"prompts/{normalized}.md"
    return normalized


def _wrap_builder_for_workspace_root(builder_path: Path, task_id: str) -> None:
    if not builder_path.exists():
        return
    original = builder_path.read_text(encoding="utf-8")
    if _builder_uses_repo_asset_paths(original):
        return

    impl_path = builder_path.with_name("_env_builder_impl.py")
    if impl_path.exists():
        return

    builder_path.rename(impl_path)
    wrapper = textwrap.dedent(
        f"""
        from __future__ import annotations

        import os
        import runpy
        from pathlib import Path


        def main() -> None:
            repo_root = Path(__file__).resolve().parents[2]
            asset_dir = repo_root / "assets" / "{task_id}"
            asset_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(asset_dir)
            runpy.run_path(str(Path(__file__).with_name("_env_builder_impl.py")), run_name="__main__")


        if __name__ == "__main__":
            main()
        """
    ).lstrip()
    builder_path.write_text(wrapper, encoding="utf-8")


def _builder_uses_repo_asset_paths(builder_text: str) -> bool:
    return any(pattern.search(builder_text) for pattern in BUILDER_REPO_ASSET_PATTERNS)
