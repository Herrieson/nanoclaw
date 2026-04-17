from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.task_curation import (
    build_dataset_manifest,
    curate_tasks,
    discover_evaluation_paths,
    load_task_attempts,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Curate generated tasks using mock-noop and multi-model evaluation results."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["results/*/evaluation.json"],
        help="Evaluation report paths or glob patterns. Defaults to results/*/evaluation.json.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/curation",
        help="Directory used to write curation outputs.",
    )
    parser.add_argument(
        "--mock-model",
        action="append",
        default=["mock-noop"],
        help="Model name treated as the mock/noop baseline. Repeatable.",
    )
    parser.add_argument(
        "--min-real-models",
        type=int,
        default=4,
        help="Minimum number of non-infra real-model attempts required before labeling a task.",
    )
    parser.add_argument(
        "--keep-threshold",
        type=float,
        default=60.0,
        help="Best-score threshold for keep when no model reached a perfect score.",
    )
    parser.add_argument(
        "--broken-threshold",
        type=float,
        default=30.0,
        help="Best-score threshold below which the task is dropped as broken.",
    )
    parser.add_argument(
        "--easy-pool-keep-percent",
        type=int,
        default=30,
        help="Deterministic keep percentage for the easy_pool bucket.",
    )
    parser.add_argument(
        "--sample-salt",
        default="nanoclaw",
        help="Salt used for deterministic easy_pool sampling.",
    )
    return parser


def _resolve_output_dir(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _write_text_list(path: Path, values: list[str]) -> None:
    path.write_text("".join(f"{value}\n" for value in values), encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    evaluation_paths = discover_evaluation_paths(args.paths, repo_root=REPO_ROOT)
    if not evaluation_paths:
        parser.error("No evaluation.json files matched the provided paths.")

    attempts_by_task, model_names = load_task_attempts(evaluation_paths)
    records = curate_tasks(
        attempts_by_task,
        mock_models={item.strip() for item in args.mock_model if item.strip()},
        min_real_models=args.min_real_models,
        keep_threshold=args.keep_threshold,
        broken_threshold=args.broken_threshold,
        easy_pool_keep_percent=args.easy_pool_keep_percent,
        sample_salt=args.sample_salt,
    )
    dataset_manifest = build_dataset_manifest(records, repo_root=REPO_ROOT)

    output_dir = _resolve_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "task_curation_report.csv"
    fieldnames = [
        "task_id",
        "label",
        "reason",
        "mock_solved",
        "real_models_total",
        "real_valid_attempts",
        "real_solved_count",
        "best_score",
        "avg_score",
        "max_step_fail_count",
        "infra_fail_count",
        "easy_pool_selected",
    ]
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())

    grouped: dict[str, list[str]] = {}
    for record in records:
        grouped.setdefault(record.label, []).append(record.task_id)
    known_labels = (
        "pending",
        "drop_bad_verifier",
        "easy_pool",
        "keep",
        "drop_broken",
        "drop_ambiguous",
    )
    for label in known_labels:
        values = grouped.get(label, [])
        _write_text_list(output_dir / f"{label}.txt", sorted(values))

    manifest_path = output_dir / "dataset_manifest.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for item in dataset_manifest:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    summary = {
        "models": model_names,
        "total_tasks": len(records),
        "label_counts": {label: len(values) for label, values in sorted(grouped.items())},
        "dataset_manifest_count": len(dataset_manifest),
        "min_real_models": args.min_real_models,
        "keep_threshold": args.keep_threshold,
        "broken_threshold": args.broken_threshold,
        "easy_pool_keep_percent": args.easy_pool_keep_percent,
        "sample_salt": args.sample_salt,
    }
    summary_path = output_dir / "curation_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Loaded {len(model_names)} model report(s).")
    print(f"Curated {len(records)} task(s).")
    for label, count in sorted(summary["label_counts"].items()):
        print(f"- {label}: {count}")
    print(f"Dataset manifest: {manifest_path} ({len(dataset_manifest)} tasks)")
    print(f"Detailed report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
