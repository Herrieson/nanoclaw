from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.evaluation_visualization import (  # noqa: E402
    ModelMetrics,
    load_model_metrics,
    render_grouped_bar_chart_svg,
    sort_model_metrics,
)


SUMMARY_FIELDS = (
    "total_runs",
    "completed_runs",
    "skipped_incomplete_runs",
    "skipped_infra_failure_runs",
    "evaluated_runs",
    "scored_runs",
    "perfect_score_runs",
    "perfect_score_rate",
    "evaluation_issue_runs",
    "run_success_rate",
    "workplace_scored_runs",
    "trace_scored_runs",
    "average_workplace_score",
    "average_trace_score",
    "average_objective_score",
    "benchmark_score",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill per-group/category score summaries into workplace evaluation outputs."
        )
    )
    parser.add_argument(
        "eval_roots",
        nargs="+",
        help="Evaluation roots such as results/nanoclaw_workplace_suite_eval.",
    )
    parser.add_argument(
        "--render-charts",
        action="store_true",
        help="Also render dataset and per-group model comparison SVG charts from existing summaries.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    total_updated = 0
    total_rows = 0

    for raw_root in args.eval_roots:
        eval_root = _resolve_path(raw_root)
        if not eval_root.exists():
            raise SystemExit(f"Evaluation root does not exist: {eval_root}")
        updated, rows = backfill_eval_root(eval_root, render_charts=args.render_charts)
        total_updated += updated
        total_rows += rows
        print(
            f"{_repo_relative(eval_root)}: updated {updated} merged summary file(s), "
            f"wrote {rows} group score row(s)."
        )

    print(f"Done. Updated {total_updated} summary file(s), wrote {total_rows} group rows.")
    return 0


def backfill_eval_root(eval_root: Path, *, render_charts: bool) -> tuple[int, int]:
    updated = 0
    all_rows: list[dict[str, Any]] = []

    for dataset_dir in _discover_dataset_dirs(eval_root):
        dataset_rows: list[dict[str, Any]] = []
        group_root = dataset_dir / "_group_reports"
        merged_root = dataset_dir / "merged"
        if not group_root.is_dir() or not merged_root.is_dir():
            continue

        groups = sorted(path.name for path in group_root.iterdir() if path.is_dir())
        for summary_path in sorted(merged_root.glob("*/evaluation_summary.json")):
            model = summary_path.parent.name
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if not isinstance(summary, dict):
                raise ValueError(f"{summary_path} is not a JSON object")

            group_scores: dict[str, dict[str, Any]] = {}
            for group in groups:
                group_summary_path = group_root / group / model / "evaluation_summary.json"
                if not group_summary_path.exists():
                    continue
                group_summary = json.loads(group_summary_path.read_text(encoding="utf-8"))
                if not isinstance(group_summary, dict):
                    raise ValueError(f"{group_summary_path} is not a JSON object")
                normalized = {
                    field: _normalized_summary_value(field, group_summary.get(field))
                    for field in SUMMARY_FIELDS
                }
                normalized["group"] = group
                normalized["summary_path"] = _repo_relative(group_summary_path)
                normalized["evaluation_path"] = _repo_relative(
                    group_summary_path.parent / "evaluation.json"
                )
                group_scores[group] = normalized

                row = {
                    "dataset": dataset_dir.name,
                    "group": group,
                    "model": model,
                    **{
                        field: _normalized_summary_value(field, group_summary.get(field))
                        for field in SUMMARY_FIELDS
                    },
                    "summary_path": _repo_relative(group_summary_path),
                    "evaluation_path": _repo_relative(group_summary_path.parent / "evaluation.json"),
                }
                dataset_rows.append(row)

            summary["group_scores"] = group_scores
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            updated += 1

        if dataset_rows:
            dataset_rows.sort(
                key=lambda item: (
                    str(item["group"]),
                    -_float_or_zero(item.get("average_objective_score")),
                    str(item["model"]).lower(),
                )
            )
            _write_group_score_files(dataset_dir, dataset_rows)
            all_rows.extend(dataset_rows)

        if render_charts:
            render_dataset_charts(dataset_dir)

    if all_rows:
        all_rows.sort(
            key=lambda item: (
                str(item["dataset"]),
                str(item["group"]),
                -_float_or_zero(item.get("average_objective_score")),
                str(item["model"]).lower(),
            )
        )
        _write_group_score_files(eval_root, all_rows)

    return updated, len(all_rows)


def render_dataset_charts(dataset_dir: Path) -> None:
    chart_root = dataset_dir / "charts"
    chart_root.mkdir(parents=True, exist_ok=True)

    merged_paths = sorted((dataset_dir / "merged").glob("*/evaluation_summary.json"))
    if merged_paths:
        _render_chart(
            merged_paths,
            chart_root / "model_comparison.svg",
            title=f"{dataset_dir.name} Workplace Evaluation",
        )

    group_root = dataset_dir / "_group_reports"
    if not group_root.is_dir():
        return
    for group_dir in sorted(path for path in group_root.iterdir() if path.is_dir()):
        group_paths = sorted(group_dir.glob("*/evaluation_summary.json"))
        if not group_paths:
            continue
        _render_chart(
            group_paths,
            chart_root / f"{group_dir.name}_model_comparison.svg",
            title=f"{dataset_dir.name} {group_dir.name} Workplace Evaluation",
        )


def _render_chart(summary_paths: list[Path], output_path: Path, *, title: str) -> None:
    try:
        metrics = load_model_metrics(summary_paths)
    except ValueError:
        metrics = [_load_tolerant_model_metrics(path) for path in summary_paths]
    metrics = sort_model_metrics(metrics, sort_by="average_objective_score")
    output_path.write_text(
        render_grouped_bar_chart_svg(metrics, title=title),
        encoding="utf-8",
    )


def _load_tolerant_model_metrics(summary_path: Path) -> ModelMetrics:
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{summary_path} is not a JSON object")
    return ModelMetrics(
        model_name=summary_path.parent.name,
        summary_path=summary_path,
        perfect_score_rate=_float_or_zero(payload.get("perfect_score_rate")),
        average_objective_score=_float_or_zero(payload.get("average_objective_score")),
    )


def _write_group_score_files(root: Path, rows: list[dict[str, Any]]) -> None:
    json_path = root / "group_scores.json"
    csv_path = root / "group_scores.csv"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "dataset",
        "group",
        "model",
        *SUMMARY_FIELDS,
        "summary_path",
        "evaluation_path",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def _discover_dataset_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir()
        and not path.name.startswith("_")
        and (path / "merged").is_dir()
        and (path / "_group_reports").is_dir()
    )


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _float_or_zero(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _normalized_summary_value(field: str, value: Any) -> Any:
    if value is None and field in {"average_objective_score", "benchmark_score"}:
        return 0.0
    return value


if __name__ == "__main__":
    raise SystemExit(main())
