from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

from nanoclaw.task_curation import is_infra_failure_error


@dataclass(frozen=True, slots=True)
class ModelMetrics:
    model_name: str
    summary_path: Path
    perfect_score_rate: float
    average_objective_score: float


@dataclass(frozen=True, slots=True)
class TaskConsensusFilter:
    task_ids: set[str]
    all_perfect_total: int
    all_non_perfect_total: int
    all_perfect_removed: int
    all_non_perfect_removed: int

    @property
    def removed_total(self) -> int:
        return self.all_perfect_removed + self.all_non_perfect_removed


def discover_summary_paths(patterns: list[str], *, repo_root: Path) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        matches = sorted(repo_root.glob(pattern))
        if not matches:
            candidate = (repo_root / pattern).resolve()
            if candidate.exists():
                matches = [candidate]
        for path in matches:
            resolved_path = path.resolve()
            if resolved_path in seen or not resolved_path.is_file():
                continue
            seen.add(resolved_path)
            resolved.append(resolved_path)
    return resolved


def load_model_metrics(
    summary_paths: list[Path],
    *,
    task_filter: set[str] | None = None,
    exclude_infra_failures: bool = False,
    exclude_task_ids: set[str] | None = None,
) -> list[ModelMetrics]:
    metrics: list[ModelMetrics] = []
    for summary_path in summary_paths:
        if task_filter is None and not exclude_infra_failures and not exclude_task_ids:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            perfect_score_rate = payload.get("perfect_score_rate")
            average_objective_score = payload.get("average_objective_score")
            if not isinstance(perfect_score_rate, (int, float)):
                raise ValueError(
                    f"{summary_path} is missing numeric perfect_score_rate in evaluation_summary.json"
                )
            if not isinstance(average_objective_score, (int, float)):
                raise ValueError(
                    f"{summary_path} is missing numeric average_objective_score in evaluation_summary.json"
                )
            metrics.append(
                ModelMetrics(
                    model_name=summary_path.parent.name,
                    summary_path=summary_path,
                    perfect_score_rate=float(perfect_score_rate),
                    average_objective_score=float(average_objective_score),
                )
            )
            continue

        metrics.append(
            _load_filtered_model_metrics(
                summary_path,
                task_filter=task_filter,
                exclude_infra_failures=exclude_infra_failures,
                exclude_task_ids=exclude_task_ids,
            )
        )
    return metrics


def load_dataset_manifest_task_ids(manifest_path: Path) -> set[str]:
    if not manifest_path.exists():
        raise ValueError(f"Dataset manifest does not exist: {manifest_path}")
    task_ids: set[str] = set()
    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        task_id = payload.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"{manifest_path}:{line_number} is missing a valid task_id")
        task_ids.add(task_id.strip())
    if not task_ids:
        raise ValueError(f"Dataset manifest is empty: {manifest_path}")
    return task_ids


def sort_model_metrics(metrics: list[ModelMetrics], *, sort_by: str) -> list[ModelMetrics]:
    if sort_by == "model":
        return sorted(metrics, key=lambda item: item.model_name.lower())
    if sort_by == "perfect_score_rate":
        return sorted(metrics, key=lambda item: (-item.perfect_score_rate, item.model_name.lower()))
    if sort_by == "average_objective_score":
        return sorted(
            metrics,
            key=lambda item: (-item.average_objective_score, item.model_name.lower()),
        )
    raise ValueError(f"Unsupported sort field: {sort_by}")


def render_grouped_bar_chart_svg(
    metrics: list[ModelMetrics],
    *,
    title: str,
    subtitle: str | None = None,
) -> str:
    if not metrics:
        raise ValueError("At least one model summary is required to render the chart.")

    if subtitle is None:
        subtitle = "Scores are on a 0-100 scale and come from each model's evaluation_summary.json."

    chart_height = 420
    margin_top = 90
    margin_right = 70
    margin_bottom = 170
    margin_left = 70
    group_width = 64
    group_gap = 26
    bar_width = 22
    bar_gap = 8
    plot_width = len(metrics) * group_width + max(0, len(metrics) - 1) * group_gap
    width = margin_left + plot_width + margin_right
    height = margin_top + chart_height + margin_bottom
    plot_bottom = margin_top + chart_height

    def bar_height(value: float) -> float:
        bounded = max(0.0, min(100.0, value))
        return chart_height * (bounded / 100.0)

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"  <title>{escape(title)}</title>",
        "  <desc>Grouped bar chart comparing perfect_score_rate and average_objective_score across models.</desc>",
        f'  <rect width="{width}" height="{height}" fill="#fcfcf7" />',
        f'  <text id="title" x="{width / 2:.1f}" y="40" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2937">'
        f"{escape(title)}</text>",
        f'  <text x="{width / 2:.1f}" y="66" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="13" fill="#4b5563">'
        f"{escape(subtitle)}</text>",
        f'  <line x1="{margin_left}" y1="{plot_bottom}" x2="{width - margin_right}" y2="{plot_bottom}" stroke="#374151" stroke-width="1.5" />',
        f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{plot_bottom}" stroke="#374151" stroke-width="1.5" />',
    ]

    for tick in range(0, 101, 20):
        y = plot_bottom - bar_height(float(tick))
        svg_lines.append(
            f'  <line x1="{margin_left}" y1="{y:.2f}" x2="{width - margin_right}" y2="{y:.2f}" stroke="#d1d5db" stroke-width="1" />'
        )
        svg_lines.append(
            f'  <text x="{margin_left - 12}" y="{y + 4:.2f}" text-anchor="end" '
            'font-family="Arial, sans-serif" font-size="12" fill="#4b5563">'
            f"{tick}</text>"
        )

    legend_x = width - margin_right - 220
    legend_y = 82
    svg_lines.extend(
        [
            f'  <rect x="{legend_x}" y="{legend_y}" width="14" height="14" rx="2" fill="#2563eb" />',
            f'  <text x="{legend_x + 22}" y="{legend_y + 12}" font-family="Arial, sans-serif" font-size="12" fill="#1f2937">perfect_score_rate</text>',
            f'  <rect x="{legend_x + 144}" y="{legend_y}" width="14" height="14" rx="2" fill="#ea580c" />',
            f'  <text x="{legend_x + 166}" y="{legend_y + 12}" font-family="Arial, sans-serif" font-size="12" fill="#1f2937">average_objective_score</text>',
        ]
    )

    for index, item in enumerate(metrics):
        group_left = margin_left + index * (group_width + group_gap)
        perfect_left = group_left + 6
        average_left = perfect_left + bar_width + bar_gap
        perfect_height = bar_height(item.perfect_score_rate)
        average_height = bar_height(item.average_objective_score)
        perfect_top = plot_bottom - perfect_height
        average_top = plot_bottom - average_height
        label_x = group_left + group_width / 2

        svg_lines.extend(
            [
                f'  <rect x="{perfect_left}" y="{perfect_top:.2f}" width="{bar_width}" height="{perfect_height:.2f}" rx="3" fill="#2563eb" />',
                f'  <rect x="{average_left}" y="{average_top:.2f}" width="{bar_width}" height="{average_height:.2f}" rx="3" fill="#ea580c" />',
                f'  <text x="{perfect_left + bar_width / 2:.2f}" y="{max(margin_top - 8, perfect_top - 8):.2f}" text-anchor="middle" '
                'font-family="Arial, sans-serif" font-size="11" fill="#1f2937">'
                f"{item.perfect_score_rate:.2f}</text>",
                f'  <text x="{average_left + bar_width / 2:.2f}" y="{max(margin_top - 8, average_top - 8):.2f}" text-anchor="middle" '
                'font-family="Arial, sans-serif" font-size="11" fill="#1f2937">'
                f"{item.average_objective_score:.2f}</text>",
                f'  <text x="{label_x:.2f}" y="{plot_bottom + 26}" text-anchor="end" '
                f'transform="rotate(-35 {label_x:.2f} {plot_bottom + 26})" '
                'font-family="Arial, sans-serif" font-size="12" fill="#1f2937">'
                f"{escape(item.model_name)}</text>",
            ]
        )

    svg_lines.append("</svg>")
    return "\n".join(svg_lines) + "\n"
def build_task_consensus_filter(
    summary_paths: list[Path],
    *,
    exclude_all_perfect_percent: float = 0.0,
    exclude_all_non_perfect_percent: float = 0.0,
    task_filter: set[str] | None = None,
    exclude_infra_failures: bool = False,
    sample_salt: str = "nanoclaw-evaluation-visualization",
) -> TaskConsensusFilter:
    _validate_percent(exclude_all_perfect_percent, "exclude_all_perfect_percent")
    _validate_percent(exclude_all_non_perfect_percent, "exclude_all_non_perfect_percent")

    if exclude_all_perfect_percent <= 0 and exclude_all_non_perfect_percent <= 0:
        return TaskConsensusFilter(set(), 0, 0, 0, 0)

    task_scores_by_model: list[dict[str, bool]] = []
    for summary_path in summary_paths:
        rows = _load_filtered_evaluation_rows(
            summary_path,
            task_filter=task_filter,
            exclude_infra_failures=exclude_infra_failures,
            exclude_task_ids=None,
        )
        model_scores: dict[str, bool] = {}
        for item in rows:
            task_id = str(item.get("task_id"))
            score = _evaluated_objective_score(item)
            if score is None:
                continue
            model_scores[task_id] = score == 100.0
        task_scores_by_model.append(model_scores)

    if not task_scores_by_model:
        return TaskConsensusFilter(set(), 0, 0, 0, 0)

    common_task_ids = set(task_scores_by_model[0])
    for model_scores in task_scores_by_model[1:]:
        common_task_ids &= set(model_scores)

    all_perfect = sorted(
        task_id
        for task_id in common_task_ids
        if all(model_scores[task_id] for model_scores in task_scores_by_model)
    )
    all_non_perfect = sorted(
        task_id
        for task_id in common_task_ids
        if all(not model_scores[task_id] for model_scores in task_scores_by_model)
    )

    all_perfect_removed = _sample_task_ids(
        all_perfect,
        percent=exclude_all_perfect_percent,
        salt=f"{sample_salt}:all_perfect",
    )
    all_non_perfect_removed = _sample_task_ids(
        all_non_perfect,
        percent=exclude_all_non_perfect_percent,
        salt=f"{sample_salt}:all_non_perfect",
    )
    return TaskConsensusFilter(
        task_ids=set(all_perfect_removed) | set(all_non_perfect_removed),
        all_perfect_total=len(all_perfect),
        all_non_perfect_total=len(all_non_perfect),
        all_perfect_removed=len(all_perfect_removed),
        all_non_perfect_removed=len(all_non_perfect_removed),
    )


def _load_filtered_model_metrics(
    summary_path: Path,
    *,
    task_filter: set[str] | None,
    exclude_infra_failures: bool,
    exclude_task_ids: set[str] | None,
) -> ModelMetrics:
    filtered_items = _load_filtered_evaluation_rows(
        summary_path,
        task_filter=task_filter,
        exclude_infra_failures=exclude_infra_failures,
        exclude_task_ids=exclude_task_ids,
    )
    return _metrics_from_filtered_rows(summary_path, filtered_items)


def _load_filtered_evaluation_rows(
    summary_path: Path,
    *,
    task_filter: set[str] | None,
    exclude_infra_failures: bool,
    exclude_task_ids: set[str] | None,
) -> list[dict[str, object]]:
    evaluation_path = summary_path.parent / "evaluation.json"
    if not evaluation_path.exists():
        raise ValueError(f"Missing evaluation.json next to {summary_path}")

    payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{evaluation_path} does not contain a JSON array")

    filtered_items: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("task_id"))
        if task_filter is not None and task_id not in task_filter:
            continue
        if exclude_task_ids is not None and task_id in exclude_task_ids:
            continue
        if exclude_infra_failures and _row_is_infra_failure(item):
            continue
        filtered_items.append(item)
    return filtered_items


def _metrics_from_filtered_rows(
    summary_path: Path,
    filtered_items: list[dict[str, object]],
) -> ModelMetrics:
    total_runs = len(filtered_items)
    perfect_score_runs = 0
    scored_values: list[float] = []

    for item in filtered_items:
        score_value = _evaluated_objective_score(item)
        if score_value is None:
            continue
        scored_values.append(score_value)
        if score_value == 100.0:
            perfect_score_runs += 1

    perfect_score_rate = round((perfect_score_runs / total_runs) * 100, 2) if total_runs else 0.0
    average_objective_score = (
        round(sum(scored_values) / len(scored_values), 2) if scored_values else 0.0
    )
    return ModelMetrics(
        model_name=summary_path.parent.name,
        summary_path=summary_path,
        perfect_score_rate=perfect_score_rate,
        average_objective_score=average_objective_score,
    )


def _evaluated_objective_score(item: dict[str, object]) -> float | None:
    if item.get("evaluation_status") != "evaluated":
        return None
    objective_score = item.get("objective_score")
    if isinstance(objective_score, int):
        return float(objective_score)
    if isinstance(objective_score, float):
        return objective_score
    return None


def _validate_percent(value: float, name: str) -> None:
    if not 0 <= value <= 100:
        raise ValueError(f"{name} must be between 0 and 100.")


def _sample_task_ids(task_ids: list[str], *, percent: float, salt: str) -> list[str]:
    if percent <= 0 or not task_ids:
        return []
    if percent >= 100:
        return list(task_ids)
    sample_count = int(len(task_ids) * percent / 100)
    if sample_count <= 0:
        return []
    ranked = sorted(
        task_ids,
        key=lambda task_id: hashlib.sha256(f"{salt}:{task_id}".encode("utf-8")).hexdigest(),
    )
    return ranked[:sample_count]


def _row_is_infra_failure(item: dict[str, object]) -> bool:
    summary_path_value = item.get("summary_path")
    if not isinstance(summary_path_value, str) or not summary_path_value.strip():
        return False
    summary_path = Path(summary_path_value).resolve()
    if not summary_path.exists():
        return False
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(summary_payload, dict):
        return False
    error = summary_payload.get("error")
    summary_error = str(error) if isinstance(error, str) and error.strip() else None
    return is_infra_failure_error(summary_error)
