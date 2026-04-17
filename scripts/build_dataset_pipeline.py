from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.task_importer import (
    default_round_id,
    import_staged_tasks,
    normalize_round_id,
    write_import_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a full dataset-build round: unzip, import, evaluate models, and curate."
    )
    parser.add_argument(
        "jsonl",
        help="Input JSONL file consumed by doc/todo/unzip.py.",
    )
    parser.add_argument(
        "--round-id",
        default=None,
        help="Stable logical round identifier. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--staging-root",
        default=".staging",
        help="Root directory for temporary unzip/import artifacts.",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=100,
        help="Maximum number of tasks to import from the staged batch.",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Real model name to run after mock-noop. Repeatable.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Worker count passed to run_generated_tasks.py.",
    )
    parser.add_argument(
        "--approval-mode",
        default="approve-all",
        help="Approval mode passed to run_generated_tasks.py.",
    )
    parser.add_argument(
        "--results-root",
        default="results",
        help="Results root directory.",
    )
    parser.add_argument(
        "--curation-output",
        default="results/curation",
        help="Output directory for curate_tasks.py.",
    )
    parser.add_argument(
        "--min-real-models",
        type=int,
        default=4,
        help="Minimum number of valid real-model attempts required by curate_tasks.py.",
    )
    parser.add_argument(
        "--keep-threshold",
        type=float,
        default=60.0,
        help="Keep threshold passed to curate_tasks.py.",
    )
    parser.add_argument(
        "--broken-threshold",
        type=float,
        default=30.0,
        help="Broken threshold passed to curate_tasks.py.",
    )
    parser.add_argument(
        "--easy-pool-keep-percent",
        type=int,
        default=30,
        help="Deterministic keep percentage for easy_pool tasks.",
    )
    parser.add_argument(
        "--sample-salt",
        default="nanoclaw",
        help="Sampling salt passed to curate_tasks.py.",
    )
    parser.add_argument(
        "--skip-mock",
        action="store_true",
        help="Skip the mock-noop baseline run.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Pass --resume to run_generated_tasks.py.",
    )
    parser.add_argument(
        "--run-builder-validation",
        action="store_true",
        help="Pass --run-builder-validation to run_generated_tasks.py.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Pass --strict to run_generated_tasks.py.",
    )
    parser.add_argument(
        "--quarantine-invalid",
        action="store_true",
        help="Pass --quarantine-invalid to run_generated_tasks.py.",
    )
    return parser


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _slugify_model_name(model_name: str) -> str:
    lowered = model_name.strip().lower()
    slug_chars = [
        char if char.isalnum() else "_"
        for char in lowered
    ]
    slug = "".join(slug_chars).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or "model"


def _run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    round_id = normalize_round_id(args.round_id or default_round_id())
    staging_root = _resolve_path(args.staging_root)
    round_root = staging_root / round_id
    unpack_root = round_root / "unpacked"
    if round_root.exists():
        parser.error(f"Round directory already exists: {round_root}")
    round_root.mkdir(parents=True, exist_ok=False)

    jsonl_path = _resolve_path(args.jsonl)
    unpack_command = [
        sys.executable,
        str((REPO_ROOT / "scripts" / "unpack_task_batch.py").resolve()),
        str(jsonl_path),
        "--output-root",
        str(unpack_root),
        "--max-records",
        str(args.max_tasks),
    ]
    _run_command(unpack_command)

    imported = import_staged_tasks(
        unpack_root,
        repo_root=REPO_ROOT,
        round_id=round_id,
        max_tasks=args.max_tasks,
    )
    if not imported:
        raise SystemExit("No tasks were imported from the staged batch.")

    import_manifest_path = round_root / "import_manifest.jsonl"
    write_import_manifest(imported, output_path=import_manifest_path)
    task_paths = [str(item.task_path) for item in imported]

    base_run_command = [
        sys.executable,
        str((REPO_ROOT / "scripts" / "run_generated_tasks.py").resolve()),
        *task_paths,
        "--approval-mode",
        args.approval_mode,
        "--workers",
        str(args.workers),
        "--evaluate",
    ]
    if args.resume:
        base_run_command.append("--resume")
    if args.run_builder_validation:
        base_run_command.append("--run-builder-validation")
    if args.strict:
        base_run_command.append("--strict")
    if args.quarantine_invalid:
        base_run_command.append("--quarantine-invalid")

    results_root = _resolve_path(args.results_root)
    model_names: list[str] = []
    if not args.skip_mock:
        model_names.append("mock-noop")
    model_names.extend(args.model)

    if not model_names:
        parser.error("No models were requested. Provide at least one --model or omit --skip-mock.")

    for model_name in model_names:
        model_results_dir = results_root / _slugify_model_name(model_name)
        command = [
            *base_run_command,
            "--model",
            model_name,
            "--results-dir",
            str(model_results_dir),
        ]
        _run_command(command)

    curate_command = [
        sys.executable,
        str((REPO_ROOT / "scripts" / "curate_tasks.py").resolve()),
        "--output-dir",
        str(_resolve_path(args.curation_output)),
        "--mock-model",
        "mock-noop",
        "--min-real-models",
        str(args.min_real_models),
        "--keep-threshold",
        str(args.keep_threshold),
        "--broken-threshold",
        str(args.broken_threshold),
        "--easy-pool-keep-percent",
        str(args.easy_pool_keep_percent),
        "--sample-salt",
        args.sample_salt,
    ]
    _run_command(curate_command)

    print(f"Round complete: {round_id}")
    print(f"Imported manifest: {import_manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
