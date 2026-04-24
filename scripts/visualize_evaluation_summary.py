from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.evaluation_visualization import (
    build_task_consensus_filter,
    discover_summary_paths,
    load_dataset_manifest_task_ids,
    load_model_metrics,
    render_grouped_bar_chart_svg,
    sort_model_metrics,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize per-model evaluation_summary.json metrics as a grouped SVG bar chart."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["results/*/evaluation_summary.json"],
        help="Summary file paths or glob patterns. Defaults to results/*/evaluation_summary.json.",
    )
    parser.add_argument(
        "--output",
        default="results/evaluation_summary_comparison.svg",
        help="Output SVG path. Defaults to results/evaluation_summary_comparison.svg.",
    )
    parser.add_argument(
        "--title",
        default="Model Evaluation Comparison",
        help="Chart title.",
    )
    parser.add_argument(
        "--sort-by",
        choices=("model", "perfect_score_rate", "average_objective_score"),
        default="model",
        help="Sort order for model groups. Metric sorts are descending.",
    )
    parser.add_argument(
        "--dataset-manifest",
        default=None,
        help=(
            "Optional dataset_manifest.jsonl path. When provided, metrics are recomputed from "
            "each model's evaluation.json using only those task_ids."
        ),
    )
    parser.add_argument(
        "--exclude-infra-failures",
        action="store_true",
        help=(
            "Recompute metrics from evaluation.json and exclude each model's own infra failures "
            "from the denominator. Max-steps failures are still counted."
        ),
    )
    parser.add_argument(
        "--exclude-all-perfect-percent",
        type=float,
        default=0.0,
        help=(
            "Deterministically exclude this percentage of tasks that every included model "
            "scored perfectly on. Requires evaluation.json files."
        ),
    )
    parser.add_argument(
        "--exclude-all-non-perfect-percent",
        type=float,
        default=0.0,
        help=(
            "Deterministically exclude this percentage of tasks that no included model "
            "scored perfectly on. Requires evaluation.json files."
        ),
    )
    parser.add_argument(
        "--consensus-filter-salt",
        default="nanoclaw-evaluation-visualization",
        help="Salt used for deterministic consensus-task exclusion sampling.",
    )
    return parser


def resolve_output_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    summary_paths = discover_summary_paths(args.paths, repo_root=REPO_ROOT)
    if not summary_paths:
        parser.error("No evaluation_summary.json files matched the provided paths.")

    subtitle = None
    task_filter = None
    if args.dataset_manifest:
        manifest_path = resolve_output_path(args.dataset_manifest)
        task_filter = load_dataset_manifest_task_ids(manifest_path)

    consensus_filter = build_task_consensus_filter(
        summary_paths,
        exclude_all_perfect_percent=args.exclude_all_perfect_percent,
        exclude_all_non_perfect_percent=args.exclude_all_non_perfect_percent,
        task_filter=task_filter,
        exclude_infra_failures=args.exclude_infra_failures,
        sample_salt=args.consensus_filter_salt,
    )

    metrics = load_model_metrics(
        summary_paths,
        task_filter=task_filter,
        exclude_infra_failures=args.exclude_infra_failures,
        exclude_task_ids=consensus_filter.task_ids,
    )

    if task_filter is not None and args.exclude_infra_failures:
        subtitle = (
            f"Scores are recomputed from evaluation.json for {len(task_filter)} curated dataset "
            "task(s); each model's own infra failures are excluded from the denominator."
        )
    elif task_filter is not None:
        subtitle = (
            f"Scores are on a 0-100 scale and are recomputed from evaluation.json for "
            f"{len(task_filter)} curated dataset task(s)."
        )
    elif args.exclude_infra_failures:
        subtitle = (
            "Scores are recomputed from evaluation.json across all tasks; each model's own infra "
            "failures are excluded from the denominator."
        )
    if consensus_filter.removed_total:
        filter_note = (
            f"Consensus filter removed {consensus_filter.removed_total} task(s): "
            f"{consensus_filter.all_perfect_removed}/{consensus_filter.all_perfect_total} all-perfect, "
            f"{consensus_filter.all_non_perfect_removed}/{consensus_filter.all_non_perfect_total} all-non-perfect."
        )
        subtitle = f"{subtitle} {filter_note}" if subtitle else filter_note
    metrics = sort_model_metrics(metrics, sort_by=args.sort_by)
    svg = render_grouped_bar_chart_svg(metrics, title=args.title, subtitle=subtitle)

    output_path = resolve_output_path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")

    print(f"Wrote chart to {output_path}")
    print("")
    print("Model                           perfect_score_rate   average_objective_score")
    print("--------------------------------------------------------------------------")
    for item in metrics:
        print(
            f"{item.model_name:<30} {item.perfect_score_rate:>18.2f} {item.average_objective_score:>25.2f}"
        )
    if consensus_filter.removed_total:
        print("")
        print(
            "Consensus filter removed "
            f"{consensus_filter.removed_total} task(s): "
            f"{consensus_filter.all_perfect_removed}/{consensus_filter.all_perfect_total} all-perfect, "
            f"{consensus_filter.all_non_perfect_removed}/{consensus_filter.all_non_perfect_total} all-non-perfect."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
