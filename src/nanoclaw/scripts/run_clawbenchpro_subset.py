from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUBSET_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "ClawBenchPro_subsets" / "smoke_40"
DEFAULT_MODEL = "qwen3.5-flash"
RUNNER_PROFILES = {
    "nanoclaw": None,
    "openclaw": REPO_ROOT / "runner_profiles" / "openclaw.yaml",
    "hermes": REPO_ROOT / "runner_profiles" / "hermes.yaml",
    "codex": REPO_ROOT / "runner_profiles" / "codex.yaml",
}


def main() -> int:
    args = build_parser().parse_args()
    subset_root = args.subset_root.expanduser().resolve()
    datasets = discover_datasets(subset_root, args.datasets)
    if not datasets:
        raise SystemExit(f"No runnable datasets found under {subset_root}")

    runners = args.runners
    models = args.models
    exit_code = 0
    for runner in runners:
        for model in models:
            model_slug = slugify(model)
            result_dir = args.results_root / subset_root.name / runner / model_slug
            eval_dir = args.eval_root / subset_root.name / runner / model_slug
            if args.run_tasks:
                exit_code = max(
                    exit_code,
                    run_tasks(
                        datasets=datasets,
                        runner=runner,
                        model=model,
                        results_dir=result_dir,
                        workers=args.workers,
                        approval_mode=args.approval_mode,
                        resume=args.resume,
                        keep_assets=args.keep_assets,
                    ),
                )
            if args.run_evals:
                exit_code = max(
                    exit_code,
                    evaluate_runs(
                        datasets=datasets,
                        results_dir=result_dir,
                        eval_dir=eval_dir,
                        workers=args.eval_workers,
                        components=args.components,
                        select_run_per_task=args.select_run_per_task,
                        allow_issues=args.allow_issues,
                    ),
                )
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and evaluate a ClawBenchPro subset package with Nanoclaw/Docker runners."
    )
    parser.add_argument(
        "subset_root",
        nargs="?",
        type=Path,
        default=DEFAULT_SUBSET_ROOT,
        help=f"Subset package root. Default: {DEFAULT_SUBSET_ROOT}",
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=None,
        help="Dataset directory names to run. Defaults to every dataset with import_manifest.jsonl.",
    )
    parser.add_argument(
        "--runners",
        nargs="+",
        choices=tuple(RUNNER_PROFILES),
        default=["nanoclaw"],
        help="Runners to execute. Default: nanoclaw.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=[DEFAULT_MODEL],
        help=f"Model names to run. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=Path("results/clawbenchpro_runs"),
        help="Root for task run outputs. Default: results/clawbenchpro_runs",
    )
    parser.add_argument(
        "--eval-root",
        type=Path,
        default=Path("results/clawbenchpro_eval"),
        help="Root for workplace evaluation outputs. Default: results/clawbenchpro_eval",
    )
    parser.add_argument("--workers", type=int, default=2, help="Task workers per runner/model.")
    parser.add_argument("--eval-workers", type=int, default=8, help="Evaluation workers.")
    parser.add_argument(
        "--approval-mode",
        choices=("reject", "approve-all", "auto-approve"),
        default=None,
        help=(
            "Override approval mode passed to task runs. "
            "Default: use each task YAML runtime.approval_mode."
        ),
    )
    parser.add_argument(
        "--components",
        choices=("full", "workplace", "trace"),
        default="workplace",
        help="Evaluation components. Default: workplace.",
    )
    parser.add_argument(
        "--select-run-per-task",
        choices=("all", "latest", "latest-completed"),
        default="latest-completed",
        help="Evaluation run selection. Default: latest-completed.",
    )
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--keep-assets", action="store_true")
    parser.add_argument("--run-tasks", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--run-evals", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--allow-issues", action=argparse.BooleanOptionalAction, default=True)
    return parser


def discover_datasets(subset_root: Path, requested: list[str] | None) -> list[Path]:
    names = requested or [
        path.name
        for path in sorted(subset_root.iterdir())
        if path.is_dir() and (path / "import_manifest.jsonl").is_file()
    ]
    datasets = []
    for name in names:
        dataset_root = subset_root / name
        if not (dataset_root / "import_manifest.jsonl").is_file():
            raise SystemExit(f"Missing import manifest for dataset: {dataset_root}")
        if not (dataset_root / "tasks").is_dir():
            raise SystemExit(f"Missing tasks directory for dataset: {dataset_root}")
        datasets.append(dataset_root)
    return datasets


def run_tasks(
    *,
    datasets: list[Path],
    runner: str,
    model: str,
    results_dir: Path,
    workers: int,
    approval_mode: str | None,
    resume: bool,
    keep_assets: bool,
) -> int:
    task_paths = [path for dataset in datasets for path in sorted((dataset / "tasks").glob("*.yaml"))]
    if not task_paths:
        print("[WARN] No task YAML files matched.", file=sys.stderr)
        return 1

    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_generated_tasks.py"),
        *(str(path) for path in task_paths),
        "--model",
        model,
        "--workers",
        str(max(1, workers)),
        "--results-dir",
        str(results_dir),
        "--skip-validation",
        "--skip-normalize",
        "--skip-auto-fix",
    ]
    if approval_mode:
        command.extend(["--approval-mode", approval_mode])
    if resume:
        command.append("--resume")
    if keep_assets:
        command.append("--keep-assets")
    profile = RUNNER_PROFILES[runner]
    if profile is not None:
        command.extend(["--runner-profile", str(profile)])

    print(f"[run] runner={runner} model={model} tasks={len(task_paths)} results={results_dir}")
    return subprocess.run(command, cwd=REPO_ROOT).returncode


def evaluate_runs(
    *,
    datasets: list[Path],
    results_dir: Path,
    eval_dir: Path,
    workers: int,
    components: str,
    select_run_per_task: str,
    allow_issues: bool,
) -> int:
    exit_code = 0
    for dataset in datasets:
        run_dirs = discover_run_dirs_for_dataset(dataset, results_dir)
        if not run_dirs:
            print(f"[WARN] No run dirs found for {dataset.name} under {results_dir}", file=sys.stderr)
            exit_code = max(exit_code, 1)
            continue
        dataset_eval_dir = eval_dir / dataset.name
        json_out = dataset_eval_dir / "evaluation.json"
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "evaluate_workplace_trace_tasks.py"),
            *(str(path) for path in run_dirs),
            "--verifier-jsonl",
            *(str(path) for path in sorted((dataset / "verifiers").glob("*.jsonl"))),
            "--manifest",
            str(dataset / "import_manifest.jsonl"),
            "--components",
            components,
            "--workers",
            str(max(1, workers)),
            "--select-run-per-task",
            select_run_per_task,
            "--no-group-by-model",
            "--json-out",
            str(json_out),
            "--csv-out",
            str(dataset_eval_dir / "evaluation.csv"),
            "--summary-out",
            str(dataset_eval_dir / "evaluation_summary.json"),
        ]
        if allow_issues:
            command.append("--allow-issues")
        print(f"[eval] dataset={dataset.name} runs={len(run_dirs)} output={dataset_eval_dir}")
        exit_code = max(exit_code, subprocess.run(command, cwd=REPO_ROOT).returncode)
    return exit_code


def discover_run_dirs_for_dataset(dataset: Path, results_dir: Path) -> list[Path]:
    task_ids = [
        str(row["imported_task_id"])
        for row in read_jsonl(dataset / "import_manifest.jsonl")
        if isinstance(row.get("imported_task_id"), str)
    ]
    run_dirs = []
    for task_id in task_ids:
        task_root = results_dir / task_id
        if not task_root.is_dir():
            continue
        run_dirs.extend(path for path in sorted(task_root.iterdir()) if (path / "summary.json").is_file())
    return run_dirs


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


if __name__ == "__main__":
    raise SystemExit(main())
