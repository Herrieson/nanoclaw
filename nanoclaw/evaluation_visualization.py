from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True, slots=True)
class ModelMetrics:
    model_name: str
    summary_path: Path
    perfect_score_rate: float
    average_objective_score: float


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


def load_model_metrics(summary_paths: list[Path]) -> list[ModelMetrics]:
    metrics: list[ModelMetrics] = []
    for summary_path in summary_paths:
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
    return metrics


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


def render_grouped_bar_chart_svg(metrics: list[ModelMetrics], *, title: str) -> str:
    if not metrics:
        raise ValueError("At least one model summary is required to render the chart.")

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
        "Scores are on a 0-100 scale and come from each model's evaluation_summary.json.</text>",
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
