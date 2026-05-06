from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.batch_runner import BatchTaskSpec, prepare_environment
from nanoclaw.config import Settings
from nanoclaw.task_loader import load_task_definition


DEFAULT_OUTPUT_ROOT = "published_datasets/nanoclaw_workplace_suite"


@dataclass(frozen=True, slots=True)
class DatasetConfig:
    name: str
    staging_root: Path
    title: str
    description: str
    group_order: tuple[str, ...]


DATASET_CONFIGS: dict[str, DatasetConfig] = {
    "round_01_aligned_mix_800": DatasetConfig(
        name="round_01_aligned_mix_800",
        staging_root=(REPO_ROOT / ".staging" / "round_01_aligned_mix_800").resolve(),
        title="Round 01 Aligned Mix 800",
        description=(
            "800-task workplace suite spanning base, hard_aligned, multi_turn_aligned, "
            "and skills_aligned groups."
        ),
        group_order=("multi_turn_aligned", "skills_aligned", "hard_aligned", "base"),
    ),
    "persona_aligned_mix_200": DatasetConfig(
        name="persona_aligned_mix_200",
        staging_root=(REPO_ROOT / ".staging" / "persona_aligned_mix_200").resolve(),
        title="Persona Aligned Mix 200",
        description=(
            "200-task workplace suite spanning base, multi_turn, hard, and skills groups."
        ),
        group_order=("base", "multi_turn", "hard", "skills"),
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Package the Nanoclaw workplace datasets into a standalone publish directory "
            "with local tasks/, assets/, manifests, provenance, and checksums."
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for the published package.",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        choices=tuple(DATASET_CONFIGS.keys()),
        help="Dataset to package. Repeatable. Defaults to both datasets.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output root.",
    )
    parser.add_argument(
        "--asset-workers",
        type=int,
        default=None,
        help=(
            "Concurrent worker count for asset generation. Defaults to min(8, CPU count). "
            "Use 1 for fully serial generation."
        ),
    )
    return parser


def _resolve_repo_path(*parts: str) -> Path:
    return (REPO_ROOT.joinpath(*parts)).resolve()


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _provenance_path_label(value: Any) -> Any:
    if not isinstance(value, str) or not value:
        return value
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSONL file: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        rows.append(json.loads(raw))
    return rows


def _write_jsonl(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_json(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_checksums(root: Path, output_path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    lines: list[str] = []
    for file_path in sorted(path for path in root.rglob("*") if path.is_file()):
        if file_path == output_path:
            continue
        relative_path = file_path.relative_to(root).as_posix()
        digest = _sha256_file(file_path)
        checksums[relative_path] = digest
        lines.append(f"{digest}  {relative_path}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksums


def _copy_provenance_files(
    *,
    staging_root: Path,
    provenance_root: Path,
) -> list[str]:
    copied: list[str] = []
    if not staging_root.exists():
        raise FileNotFoundError(f"Missing staging root: {staging_root}")

    for item in sorted(staging_root.iterdir(), key=lambda p: p.name):
        if item.is_dir():
            if item.name == "eval_manifests":
                destination = provenance_root / "eval_manifests"
                _copy_tree(item, destination)
                copied.append("eval_manifests")
            else:
                # Skip heavy record trees; the release package carries the
                # selected tasks, prompts, assets, and rewritten manifests.
                continue
        elif item.is_file():
            _copy_file(item, provenance_root / item.name)
            copied.append(item.name)
    return copied


def _dataset_task_source(task_id: str) -> Path:
    task_path = _resolve_repo_path("tasks", f"{task_id}.yaml")
    if not task_path.exists():
        raise FileNotFoundError(f"Task YAML not found: {task_path}")
    return task_path


def _dataset_task_dir_source(task_id: str) -> Path:
    task_dir = _resolve_repo_path("tasks", task_id)
    if not task_dir.exists():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")
    return task_dir


def _task_prompt_destinations(prompt_sources: tuple[str, ...]) -> list[tuple[Path, Path]]:
    repo_tasks_root = _resolve_repo_path("tasks")
    destinations: list[tuple[Path, Path]] = []
    seen: set[Path] = set()
    for prompt_source in prompt_sources:
        if prompt_source.startswith("<"):
            continue
        source_path = Path(prompt_source).expanduser().resolve()
        if source_path in seen:
            continue
        seen.add(source_path)
        try:
            relative = source_path.relative_to(repo_tasks_root)
        except ValueError as exc:
            raise ValueError(
                f"Prompt source is outside the repository tasks root: {source_path}"
            ) from exc
        destination = relative
        destinations.append((source_path, destination))
    return destinations


def _task_prompt_manifest_paths(prompt_sources: tuple[str, ...]) -> list[str]:
    repo_tasks_root = _resolve_repo_path("tasks")
    paths: list[str] = []
    seen: set[str] = set()
    for prompt_source in prompt_sources:
        if prompt_source.startswith("<"):
            manifest_path = prompt_source
        else:
            source_path = Path(prompt_source).expanduser().resolve()
            try:
                relative = source_path.relative_to(repo_tasks_root)
            except ValueError as exc:
                raise ValueError(
                    f"Prompt source is outside the repository tasks root: {source_path}"
                ) from exc
            manifest_path = f"tasks/{relative.as_posix()}"
        if manifest_path in seen:
            continue
        seen.add(manifest_path)
        paths.append(manifest_path)
    return paths


def _build_task_asset(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    assets_root: Path,
) -> Path:
    return prepare_environment(
        spec,
        repo_root=repo_root,
        assets_root=assets_root,
    )


def _package_dataset(
    config: DatasetConfig,
    *,
    output_root: Path,
    asset_workers: int,
    settings: Settings,
) -> dict[str, Any]:
    staging_root = config.staging_root
    selection_rows = _read_jsonl(staging_root / "selection_manifest.jsonl")
    import_rows = _read_jsonl(staging_root / "import_manifest.jsonl")
    if len(selection_rows) != len(import_rows):
        raise ValueError(
            f"{config.name}: selection/import manifest length mismatch "
            f"({len(selection_rows)} != {len(import_rows)})"
        )

    ordered_task_ids = [
        row["imported_task_id"]
        for row in import_rows
        if isinstance(row.get("imported_task_id"), str)
    ]

    dataset_root = output_root / config.name
    if dataset_root.exists():
        shutil.rmtree(dataset_root)
    dataset_root.mkdir(parents=True, exist_ok=False)

    tasks_root = dataset_root / "tasks"
    assets_root = dataset_root / "assets"
    skills_root = dataset_root / "skills"
    provenance_root = dataset_root / "provenance"
    eval_manifest_root = dataset_root / "eval_manifests"

    tasks_root.mkdir(parents=True, exist_ok=True)
    assets_root.mkdir(parents=True, exist_ok=True)
    skills_root.mkdir(parents=True, exist_ok=True)
    provenance_root.mkdir(parents=True, exist_ok=True)
    eval_manifest_root.mkdir(parents=True, exist_ok=True)

    copied_provenance = _copy_provenance_files(
        staging_root=staging_root,
        provenance_root=provenance_root,
    )

    package_task_rows: list[dict[str, Any]] = []
    asset_specs: list[BatchTaskSpec] = []
    prompt_sources_to_copy: dict[Path, Path] = {}
    skill_slugs_to_copy: set[str] = set()

    for index, task_id in enumerate(ordered_task_ids, start=1):
        import_row = import_rows[index - 1]
        if import_row is None:
            raise KeyError(f"{config.name}: missing import row for task id {task_id}")
        source_task_id = import_row.get("source_task_id")
        if not isinstance(source_task_id, str) or not source_task_id.strip():
            raise ValueError(f"{config.name}: invalid source_task_id for {task_id}")
        source_task_id = source_task_id.strip()
        selection_row = selection_rows[index - 1]
        selection_source_task_id = selection_row.get("source_task_id")
        if (
            isinstance(selection_source_task_id, str)
            and selection_source_task_id.strip()
            and selection_source_task_id.strip() != source_task_id
        ):
            raise ValueError(
                f"{config.name}: import/selection source_task_id mismatch at row {index}: "
                f"{source_task_id} != {selection_source_task_id}"
            )

        task_path = _dataset_task_source(task_id)
        task = load_task_definition(task_path, settings)
        task_dir_source = _dataset_task_dir_source(task_id)

        _copy_file(task_path, tasks_root / task_path.name)
        _copy_tree(task_dir_source, tasks_root / task_id)

        for source_prompt_path, relative_prompt_path in _task_prompt_destinations(task.prompt_sources):
            prompt_sources_to_copy[source_prompt_path] = relative_prompt_path
        for skill_slug in task.skills.available:
            skill_slugs_to_copy.add(skill_slug)

        builder_path = task_dir_source / "env_builder.py"
        asset_specs.append(
            BatchTaskSpec(
                task_path=task_path,
                task_id=task_id,
                asset_name=task.asset,
                builder_path=builder_path if builder_path.exists() else None,
                sessions=task.sessions,
            )
        )

        prompt_paths = _task_prompt_manifest_paths(task.prompt_sources)
        session_turns = [session.turn for session in task.sessions]
        package_task_rows.append(
            {
                "round_id": config.name,
                "task_index": index,
                "source_task_id": source_task_id,
                "imported_task_id": task_id,
                "group": import_row.get("group") or selection_row.get("group"),
                "aligned_index": import_row.get("aligned_index") or selection_row.get("aligned_index"),
                "task_path": f"tasks/{task_path.name}",
                "task_dir": f"tasks/{task_id}",
                "asset": task.asset,
                "asset_dir": f"assets/{task.asset}",
                "prompt_path": prompt_paths[0] if prompt_paths else None,
                "prompt_paths": prompt_paths,
                "prompt_count": len(prompt_paths),
                "skills_available": list(task.skills.available),
                "skill_dirs": [f"skills/{skill_slug}" for skill_slug in task.skills.available],
                "session_turns": session_turns,
                "session_count": len(session_turns),
                "has_multi_turn": len(session_turns) > 1,
                "source_manifest": {
                    "selection_manifest_row": selection_row,
                    "import_manifest_row": import_row,
                },
            }
        )

    for source_prompt_path, relative_prompt_path in sorted(
        prompt_sources_to_copy.items(),
        key=lambda item: item[1].as_posix(),
    ):
        _copy_file(source_prompt_path, tasks_root / relative_prompt_path)

    for skill_slug in sorted(skill_slugs_to_copy):
        source_skill_dir = _resolve_repo_path("skills", skill_slug)
        if not source_skill_dir.exists() or not source_skill_dir.is_dir():
            raise FileNotFoundError(
                f"{config.name}: task references missing skill directory: {source_skill_dir}"
            )
        _copy_tree(source_skill_dir, skills_root / skill_slug)

    asset_paths: list[Path] = []
    workers = max(1, asset_workers)
    if workers == 1:
        for idx, spec in enumerate(asset_specs, start=1):
            asset_path = _build_task_asset(spec, repo_root=REPO_ROOT, assets_root=assets_root)
            asset_paths.append(asset_path)
            if idx == 1 or idx == len(asset_specs) or idx % 50 == 0:
                print(
                    f"[INFO] {config.name}: built assets {idx}/{len(asset_specs)}",
                    flush=True,
                )
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _build_task_asset,
                    spec,
                    repo_root=REPO_ROOT,
                    assets_root=assets_root,
                ): spec
                for spec in asset_specs
            }
            completed = 0
            for future in as_completed(futures):
                asset_paths.append(future.result())
                completed += 1
                if completed == 1 or completed == len(asset_specs) or completed % 50 == 0:
                    print(
                        f"[INFO] {config.name}: built assets {completed}/{len(asset_specs)}",
                        flush=True,
                    )

    group_counts: dict[str, int] = {}
    for row in package_task_rows:
        group_name = str(row.get("group") or "")
        group_counts[group_name] = group_counts.get(group_name, 0) + 1

    release_selection_rows: list[dict[str, Any]] = []
    release_import_rows: list[dict[str, Any]] = []
    for row in package_task_rows:
        selection_row = dict(row["source_manifest"]["selection_manifest_row"])
        import_row = dict(row["source_manifest"]["import_manifest_row"])

        task_path = row["task_path"]
        task_dir = row["task_dir"]
        prompt_paths = row["prompt_paths"]
        asset_dir = row["asset_dir"]

        release_selection_row = {
            "round_id": config.name,
            "group": row["group"],
            "aligned_index": row["aligned_index"],
            "source_task_id": row["source_task_id"],
            "source_record": selection_row.get("source_record"),
            "destination_record": selection_row.get("destination_record"),
            "source_root": _provenance_path_label(selection_row.get("source_root")),
            "source_task_path": _provenance_path_label(selection_row.get("source_task_path")),
            "task_path": task_path,
            "task_dir": task_dir,
            "prompt_path": prompt_paths[0] if prompt_paths else None,
            "prompt_paths": prompt_paths,
            "asset": row["asset"],
            "asset_dir": asset_dir,
            "skills_available": row["skills_available"],
            "skill_dirs": row["skill_dirs"],
            "task_index": row["task_index"],
        }
        release_import_row = {
            "round_id": config.name,
            "group": row["group"],
            "aligned_index": row["aligned_index"],
            "source_task_id": row["source_task_id"],
            "imported_task_id": row["imported_task_id"],
            "task_path": task_path,
            "task_dir": task_dir,
            "prompt_path": prompt_paths[0] if prompt_paths else None,
            "prompt_paths": prompt_paths,
            "asset": row["asset"],
            "asset_dir": asset_dir,
            "session_turns": row["session_turns"],
            "session_count": row["session_count"],
            "prompt_count": row["prompt_count"],
            "skills_available": row["skills_available"],
            "skill_dirs": row["skill_dirs"],
            "has_multi_turn": row["has_multi_turn"],
            "source_import": {
                "round_id": import_row.get("round_id"),
                "group": import_row.get("group"),
                "aligned_index": import_row.get("aligned_index"),
                "source_task_id": import_row.get("source_task_id"),
            },
        }
        release_selection_rows.append(release_selection_row)
        release_import_rows.append(release_import_row)

    _write_jsonl(release_selection_rows, dataset_root / "selection_manifest.jsonl")
    _write_jsonl(release_import_rows, dataset_root / "import_manifest.jsonl")

    for group_name in config.group_order:
        group_rows = [row for row in release_import_rows if row["group"] == group_name]
        if not group_rows:
            raise ValueError(f"{config.name}: no rows found for group {group_name}")
        _write_jsonl(group_rows, eval_manifest_root / f"{group_name}.jsonl")
        (eval_manifest_root / f"{group_name}.task_ids").write_text(
            "\n".join(row["imported_task_id"] for row in group_rows) + "\n",
            encoding="utf-8",
        )

    summary = {
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_staging_root": _provenance_path_label(str(staging_root)),
        "task_count": len(package_task_rows),
        "group_order": list(config.group_order),
        "group_counts": group_counts,
        "paths": {
            "tasks": "tasks",
            "assets": "assets",
            "skills": "skills",
            "provenance": "provenance",
            "selection_manifest": "selection_manifest.jsonl",
            "import_manifest": "import_manifest.jsonl",
            "eval_manifests": "eval_manifests",
        },
        "task_ids": [row["imported_task_id"] for row in package_task_rows],
        "record_count": len(package_task_rows),
        "skill_count": len(skill_slugs_to_copy),
        "skill_slugs": sorted(skill_slugs_to_copy),
        "provenance_files": copied_provenance,
    }
    _write_json(summary, dataset_root / "manifest.json")

    readme = (
        f"# {config.title}\n\n"
        f"{config.description}\n\n"
        f"## Layout\n\n"
        f"- `tasks/`: task YAML files and task-local directories.\n"
        f"- `tasks/prompts/`: prompt files referenced by the YAML bundles.\n"
        f"- `assets/`: frozen initial workspaces generated from the task builders.\n"
        f"- `skills/`: global task-local skills referenced by the task YAML files.\n"
        f"- `eval_manifests/`: group-wise manifests and task id lists.\n"
        f"- `provenance/`: original staging manifests copied for traceability.\n"
        f"- `manifest.json`: machine-readable package summary.\n"
        f"- `checksums.sha256`: file inventory for integrity checks.\n\n"
        f"## Counts\n\n"
        f"- Tasks: {len(package_task_rows)}\n"
        + "".join(
            f"- {group_name}: {group_counts.get(group_name, 0)}\n"
            for group_name in config.group_order
        )
        + "\n"
        f"This directory is self-contained and does not depend on `.staging`.\n"
    )
    (dataset_root / "README.md").write_text(readme, encoding="utf-8")

    checksums = _write_checksums(dataset_root, dataset_root / "checksums.sha256")
    dataset_bytes = sum(path.stat().st_size for path in dataset_root.rglob("*") if path.is_file())

    dataset_manifest = {
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "root": config.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_staging_root": _provenance_path_label(str(staging_root)),
        "task_count": len(package_task_rows),
        "group_order": list(config.group_order),
        "group_counts": group_counts,
        "task_manifest": "import_manifest.jsonl",
        "selection_manifest": "selection_manifest.jsonl",
        "eval_manifests": {
            group_name: {
                "jsonl": f"eval_manifests/{group_name}.jsonl",
                "task_ids": f"eval_manifests/{group_name}.task_ids",
            }
            for group_name in config.group_order
        },
        "files": {
            "count": len(checksums),
            "bytes": dataset_bytes,
            "checksums": "checksums.sha256",
        },
        "skills": {
            "count": len(skill_slugs_to_copy),
            "slugs": sorted(skill_slugs_to_copy),
        },
    }
    _write_json(dataset_manifest, dataset_root / "manifest.json")

    return {
        "name": config.name,
        "title": config.title,
        "root": str(dataset_root.relative_to(output_root)),
        "task_count": len(package_task_rows),
        "group_counts": group_counts,
        "files": len(checksums),
        "bytes": dataset_bytes,
        "checksums": f"{config.name}/checksums.sha256",
        "skill_count": len(skill_slugs_to_copy),
    }


def _write_package_readme(output_root: Path, dataset_summaries: list[dict[str, Any]]) -> None:
    lines = [
        "# Nanoclaw Workplace Suite Package",
        "",
        "This directory packages the workplace datasets as a standalone release.",
        "",
        "## Included datasets",
        "",
    ]
    for summary in dataset_summaries:
        lines.append(f"- `{summary['name']}`: {summary['task_count']} tasks")
        for group_name, count in summary["group_counts"].items():
            lines.append(f"  - {group_name}: {count}")
    lines.extend(
        [
            "",
            "Each dataset directory contains `tasks/`, `assets/`, `eval_manifests/`,",
            "`skills/`, `provenance/`, a dataset manifest, and a checksum file.",
            "",
            "The dataset directories are self-contained snapshots and do not rely on `.staging`.",
            "",
        ]
    )
    (output_root / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _write_package_manifest(output_root: Path, dataset_summaries: list[dict[str, Any]]) -> None:
    payload = {
        "package_name": "nanoclaw_workplace_suite",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": "nanoclaw",
        "output_root": ".",
        "datasets": dataset_summaries,
    }
    _write_json(payload, output_root / "manifest.json")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    selected_datasets = args.dataset or list(DATASET_CONFIGS.keys())
    output_root = _resolve_path(args.output_root)
    if output_root.exists():
        if not args.force:
            parser.error(f"Output root already exists: {output_root}")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=False)

    asset_workers = (
        args.asset_workers
        if args.asset_workers is not None
        else max(1, min(8, (os.cpu_count() or 1)))
    )

    print(f"[INFO] Output root: {output_root}")
    print(f"[INFO] Datasets: {' '.join(selected_datasets)}")
    print(f"[INFO] Asset workers: {asset_workers}")

    settings = Settings.from_env()
    dataset_summaries: list[dict[str, Any]] = []
    for dataset_name in selected_datasets:
        config = DATASET_CONFIGS[dataset_name]
        print("==================================================")
        print(f"[INFO] Packaging dataset: {dataset_name}")
        print(f"[INFO] Source staging root: {config.staging_root}")
        summary = _package_dataset(
            config,
            output_root=output_root,
            asset_workers=asset_workers,
            settings=settings,
        )
        dataset_summaries.append(summary)
        print(
            f"[INFO] Completed {dataset_name}: {summary['task_count']} tasks, "
            f"{summary['files']} files, {summary['bytes']} bytes"
        )

    _write_package_readme(output_root, dataset_summaries)
    _write_package_manifest(output_root, dataset_summaries)

    package_checksums = _write_checksums(output_root, output_root / "checksums.sha256")
    package_bytes = sum(path.stat().st_size for path in output_root.rglob("*") if path.is_file())
    print("==================================================")
    print(f"[INFO] Package files: {len(package_checksums)}")
    print(f"[INFO] Package bytes: {package_bytes}")
    print(f"[INFO] Package manifest: {output_root / 'manifest.json'}")
    print(f"[INFO] Package checksums: {output_root / 'checksums.sha256'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
