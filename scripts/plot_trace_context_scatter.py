from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent


DEFAULT_DATASETS = (
    "round_01_aligned_mix_subset_100",
    "persona_aligned_mix_subset_100",
)

CATEGORY_COLORS = {
    "base": "#2563eb",
    "multi_turn": "#16a34a",
    "hard": "#dc2626",
    "skills": "#9333ea",
    "unknown": "#6b7280",
}

CATEGORY_ORDER = ("base", "multi_turn", "hard", "skills", "unknown")
CODEX_ACTION_ITEM_TYPES = {"command_execution", "web_search", "collab_tool_call"}


@dataclass(frozen=True, slots=True)
class RunPoint:
    dataset: str
    task_id: str
    category: str
    agent_rounds: int
    trace_length: int
    trace_bucket: int
    run_dir: Path


@dataclass(frozen=True, slots=True)
class AggregatedPoint:
    category: str
    agent_rounds: int
    trace_bucket: int
    count: int
    datasets: tuple[str, ...]
    task_ids: tuple[str, ...]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plot agent execution rounds vs total trace length for one model under one framework."
        )
    )
    parser.add_argument(
        "--results-root",
        default="results/docker_workplace_suite",
        help="Task results root. Defaults to results/docker_workplace_suite.",
    )
    parser.add_argument(
        "--runner",
        default="hermes",
        help=(
            "Runner/framework name under --results-root, for example hermes/openclaw/codex. "
            "Use an empty string for the built-in nanoclaw result layout."
        ),
    )
    parser.add_argument(
        "--model",
        default="qwen3.5-flash",
        help="Model name or already-slugified model directory name.",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        dest="datasets",
        help=(
            "Dataset name to include. Can be repeated. Defaults to the two 100-task subsets."
        ),
    )
    parser.add_argument(
        "--staging-root",
        default=".staging",
        help="Root containing <dataset>/eval_manifests/*.task_ids. Defaults to .staging.",
    )
    parser.add_argument(
        "--context-bin-size",
        type=int,
        default=1000,
        help=(
            "Bucket trace lengths upward by this many characters before aggregation. "
            "Default is 1000, so 1..1000 chars is plotted at 1k."
        ),
    )
    parser.add_argument(
        "--y-scale",
        choices=("linear", "log"),
        default="linear",
        help="Y-axis scale. Use log when trace lengths have large outliers.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output SVG path. Defaults to <results-root>/<runner>/trace_context_scatter_<model>.svg.",
    )
    parser.add_argument(
        "--csv-output",
        default=None,
        help="Optional CSV path for aggregated point data. Defaults next to the SVG.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    datasets = tuple(args.datasets or DEFAULT_DATASETS)
    results_root = _resolve_path(args.results_root)
    staging_root = _resolve_path(args.staging_root)
    model_slug = _slugify_model_name(args.model)
    runner = args.runner.strip()

    points = collect_run_points(
        results_root=results_root,
        runner=runner,
        model_slug=model_slug,
        datasets=datasets,
        staging_root=staging_root,
        context_bin_size=args.context_bin_size,
    )
    if not points:
        raise SystemExit(
            "No completed runs with trace.jsonl were found for "
            f"runner={runner or '<builtin>'}, model={model_slug}, datasets={', '.join(datasets)}"
        )

    aggregated_points = aggregate_points(points)
    output_path = _resolve_output_path(args.output, results_root, runner, model_slug)
    csv_output_path = _resolve_csv_output_path(args.csv_output, output_path)

    title = f"{runner or 'nanoclaw'} / {model_slug}: agent rounds vs trace length"
    subtitle = (
        f"{len(points)} completed task(s), {len(aggregated_points)} aggregated point(s); "
        f"trace length is bucketed by {args.context_bin_size} characters; "
        f"y-scale={args.y_scale}."
    )
    svg = render_scatter_svg(
        aggregated_points,
        title=title,
        subtitle=subtitle,
        y_scale=args.y_scale,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    write_points_csv(csv_output_path, aggregated_points)

    print(f"Wrote scatter chart to {output_path}")
    print(f"Wrote aggregated point data to {csv_output_path}")
    print(f"Completed runs: {len(points)}")
    print(f"Aggregated points: {len(aggregated_points)}")
    return 0


def collect_run_points(
    *,
    results_root: Path,
    runner: str,
    model_slug: str,
    datasets: tuple[str, ...],
    staging_root: Path,
    context_bin_size: int,
) -> list[RunPoint]:
    points: list[RunPoint] = []
    for dataset in datasets:
        category_by_task_id = load_task_categories(staging_root / dataset / "eval_manifests")
        model_root = _model_results_root(results_root, runner, dataset, model_slug)
        if not model_root.is_dir():
            print(f"[WARN] Missing model results dir: {_repo_relative(model_root)}", file=sys.stderr)
            continue

        for task_id, run_dir in latest_completed_run_dirs(model_root).items():
            summary_path = run_dir / "summary.json"
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            trace_path = _trace_path(run_dir, payload)
            if not trace_path.exists():
                continue
            trace_length = len(trace_path.read_text(encoding="utf-8", errors="replace"))
            trace_bucket = bucket_length(trace_length, bin_size=context_bin_size)
            points.append(
                RunPoint(
                    dataset=dataset,
                    task_id=task_id,
                    category=category_by_task_id.get(task_id, "unknown"),
                    agent_rounds=agent_execution_round_count(
                        run_dir,
                        summary=payload,
                        trace_path=trace_path,
                    ),
                    trace_length=trace_length,
                    trace_bucket=trace_bucket,
                    run_dir=run_dir,
                )
            )
    return points


def load_task_categories(manifest_root: Path) -> dict[str, str]:
    categories: dict[str, str] = {}
    if not manifest_root.is_dir():
        return categories
    for task_ids_path in sorted(manifest_root.glob("*.task_ids")):
        category = normalize_category(task_ids_path.stem)
        for raw_line in task_ids_path.read_text(encoding="utf-8").splitlines():
            task_id = raw_line.strip()
            if task_id:
                categories[task_id] = category
    return categories


def normalize_category(value: str) -> str:
    category = value.strip().replace("-", "_")
    if category.endswith("_aligned"):
        category = category[: -len("_aligned")]
    if category in CATEGORY_COLORS:
        return category
    return "unknown"


def latest_completed_run_dirs(model_root: Path) -> dict[str, Path]:
    selected: dict[str, Path] = {}
    for task_dir in sorted(path for path in model_root.iterdir() if path.is_dir()):
        if task_dir.name.startswith("."):
            continue
        completed_runs: list[Path] = []
        for run_dir in sorted(path for path in task_dir.iterdir() if path.is_dir()):
            summary_path = run_dir / "summary.json"
            if not summary_path.exists():
                continue
            try:
                payload = json.loads(summary_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if payload.get("status") != "completed":
                continue
            if _final_answer_is_blank(run_dir, payload):
                continue
            completed_runs.append(run_dir)
        if completed_runs:
            selected[task_dir.name] = sorted(completed_runs, key=lambda path: path.name)[-1]
    return selected


def completed_prompt_turn_count(summary: dict[str, object]) -> int:
    turns = summary.get("turns")
    if isinstance(turns, list) and turns:
        completed = [
            item
            for item in turns
            if isinstance(item, dict) and item.get("status") == "completed"
        ]
        return len(completed) if completed else len(turns)
    return 1


def agent_execution_round_count(
    run_dir: Path,
    *,
    summary: dict[str, object],
    trace_path: Path,
) -> int:
    steps_used = summary.get("steps_used")
    if isinstance(steps_used, int) and steps_used > 0:
        return steps_used

    prompt_turns = completed_prompt_turn_count(summary)
    action_count = (
        codex_action_count(trace_path)
        + nanoclaw_tool_call_count(trace_path)
        + openclaw_session_tool_call_count(run_dir)
        + hermes_session_tool_call_count(run_dir)
    )
    return max(1, action_count + prompt_turns)


def codex_action_count(trace_path: Path) -> int:
    count = 0
    for payload in iter_jsonl(trace_path):
        if payload.get("type") != "codex_event":
            continue
        event = payload.get("event")
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") in CODEX_ACTION_ITEM_TYPES:
            count += 1
    return count


def nanoclaw_tool_call_count(trace_path: Path) -> int:
    return sum(1 for payload in iter_jsonl(trace_path) if payload.get("type") == "tool_call")


def openclaw_session_tool_call_count(run_dir: Path) -> int:
    session_root = run_dir / "runner_state" / "home" / ".openclaw" / "agents" / "main" / "sessions"
    if not session_root.is_dir():
        return 0
    count = 0
    for session_path in sorted(session_root.glob("*.jsonl")):
        if session_path.name == "sessions.json":
            continue
        for payload in iter_jsonl(session_path):
            message = payload.get("message")
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            content = message.get("content")
            if isinstance(content, list):
                count += sum(
                    1
                    for item in content
                    if isinstance(item, dict) and item.get("type") == "toolCall"
                )
    return count


def hermes_session_tool_call_count(run_dir: Path) -> int:
    session_root = run_dir / "runner_state" / "sessions"
    if not session_root.is_dir():
        return 0
    count = 0
    for session_path in sorted(session_root.glob("*.json")):
        try:
            payload = json.loads(session_path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        messages = payload.get("messages")
        if not isinstance(messages, list):
            continue
        for message in messages:
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            tool_calls = message.get("tool_calls")
            if isinstance(tool_calls, list):
                count += len(tool_calls)
    return count


def iter_jsonl(path: Path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            yield payload


def bucket_length(length: int, *, bin_size: int) -> int:
    if bin_size <= 0:
        return max(0, length)
    if length <= 0:
        return 0
    return int(math.ceil(length / bin_size) * bin_size)


def aggregate_points(points: list[RunPoint]) -> list[AggregatedPoint]:
    counter: Counter[tuple[str, int, int]] = Counter()
    datasets_by_key: dict[tuple[str, int, int], set[str]] = {}
    task_ids_by_key: dict[tuple[str, int, int], list[str]] = {}
    for point in points:
        key = (point.category, point.agent_rounds, point.trace_bucket)
        counter[key] += 1
        datasets_by_key.setdefault(key, set()).add(point.dataset)
        task_ids_by_key.setdefault(key, []).append(point.task_id)

    aggregated = [
        AggregatedPoint(
            category=category,
            agent_rounds=turns,
            trace_bucket=trace_bucket,
            count=count,
            datasets=tuple(sorted(datasets_by_key[key])),
            task_ids=tuple(sorted(task_ids_by_key[key])),
        )
        for key, count in counter.items()
        for category, turns, trace_bucket in [key]
    ]
    return sorted(
        aggregated,
        key=lambda item: (
            CATEGORY_ORDER.index(item.category)
            if item.category in CATEGORY_ORDER
            else len(CATEGORY_ORDER),
            item.agent_rounds,
            item.trace_bucket,
        ),
    )


def render_scatter_svg(
    points: list[AggregatedPoint],
    *,
    title: str,
    subtitle: str,
    y_scale: str,
) -> str:
    width = 980
    height = 660
    margin_left = 92
    margin_right = 42
    margin_top = 92
    margin_bottom = 106
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    plot_bottom = margin_top + plot_height

    x_values = [point.agent_rounds for point in points]
    y_values = [point.trace_bucket for point in points]
    min_turn = min(x_values)
    max_turn = max(x_values)
    max_y = max(y_values) if y_values else 0
    y_axis_max = max(1000, _ceil_to_nice(max_y))
    y_axis_min = 1000 if y_scale == "log" else 0
    x_span = max(1.0, (max_turn - min_turn) + 1.0)

    def x_pos(agent_rounds: int, category: str) -> float:
        category_offsets = {
            "base": -10.0,
            "multi_turn": -3.0,
            "hard": 3.0,
            "skills": 10.0,
            "unknown": 0.0,
        }
        base = margin_left + ((agent_rounds - min_turn + 0.5) / x_span) * plot_width
        return base + category_offsets.get(category, 0.0)

    def y_pos(trace_bucket: int, category: str) -> float:
        category_offsets = {
            "base": -3.0,
            "multi_turn": 3.0,
            "hard": -3.0,
            "skills": 3.0,
            "unknown": 0.0,
        }
        if y_scale == "log":
            value = max(y_axis_min, trace_bucket)
            lower = math.log10(y_axis_min)
            upper = math.log10(y_axis_max)
            ratio = (math.log10(value) - lower) / max(0.001, upper - lower)
        else:
            ratio = trace_bucket / y_axis_max
        scaled = plot_bottom - ratio * plot_height
        return scaled + category_offsets.get(category, 0.0)

    def radius(count: int) -> float:
        return min(28.0, 4.0 + math.sqrt(count) * 4.2)

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"  <title>{escape(title)}</title>",
        "  <desc id=\"desc\">Scatter chart of agent execution rounds vs aggregated trace length.</desc>",
        f'  <rect width="{width}" height="{height}" fill="#fcfcf7" />',
        f'  <text id="title" x="{width / 2:.1f}" y="38" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#111827">'
        f"{escape(title)}</text>",
        f'  <text x="{width / 2:.1f}" y="64" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="13" fill="#4b5563">'
        f"{escape(subtitle)}</text>",
        f'  <rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="#ffffff" stroke="#d1d5db" />',
    ]

    y_ticks = _log_y_ticks(y_axis_min, y_axis_max) if y_scale == "log" else _linear_y_ticks(y_axis_max)
    for tick in y_ticks:
        if y_scale == "log":
            lower = math.log10(y_axis_min)
            upper = math.log10(y_axis_max)
            y_ratio = (math.log10(max(y_axis_min, tick)) - lower) / max(0.001, upper - lower)
        else:
            y_ratio = tick / y_axis_max
        y = plot_bottom - y_ratio * plot_height
        svg.append(
            f'  <line x1="{margin_left}" y1="{y:.2f}" x2="{width - margin_right}" y2="{y:.2f}" stroke="#e5e7eb" />'
        )
        svg.append(
            f'  <text x="{margin_left - 12}" y="{y + 4:.2f}" text-anchor="end" '
            'font-family="Arial, sans-serif" font-size="12" fill="#4b5563">'
            f"{_format_k(tick)}</text>"
        )

    for turn in range(min_turn, max_turn + 1):
        x = margin_left + ((turn - min_turn + 0.5) / x_span) * plot_width
        svg.append(
            f'  <line x1="{x:.2f}" y1="{margin_top}" x2="{x:.2f}" y2="{plot_bottom}" stroke="#f3f4f6" />'
        )
        svg.append(
            f'  <text x="{x:.2f}" y="{plot_bottom + 26}" text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="12" fill="#374151">'
            f"{turn}</text>"
        )

    svg.extend(
        [
            f'  <line x1="{margin_left}" y1="{plot_bottom}" x2="{width - margin_right}" y2="{plot_bottom}" stroke="#374151" stroke-width="1.5" />',
            f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{plot_bottom}" stroke="#374151" stroke-width="1.5" />',
            f'  <text x="{margin_left + plot_width / 2:.1f}" y="{height - 34}" text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">agent execution rounds</text>',
            f'  <text x="24" y="{margin_top + plot_height / 2:.1f}" text-anchor="middle" '
            f'transform="rotate(-90 24 {margin_top + plot_height / 2:.1f})" '
            'font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">'
            f"trace length bucket{' (log)' if y_scale == 'log' else ''}</text>",
        ]
    )

    legend_x = margin_left + 12
    legend_y = margin_top - 30
    legend_counts = Counter()
    for point in points:
        legend_counts[point.category] += point.count
    for index, category in enumerate(CATEGORY_ORDER):
        if category not in legend_counts:
            continue
        x = legend_x + index * 150
        color = CATEGORY_COLORS[category]
        svg.append(f'  <circle cx="{x}" cy="{legend_y}" r="6" fill="{color}" />')
        svg.append(
            f'  <text x="{x + 12}" y="{legend_y + 4}" font-family="Arial, sans-serif" '
            f'font-size="12" fill="#1f2937">{escape(category)} ({legend_counts[category]})</text>'
        )

    for point in sorted(points, key=lambda item: item.count):
        x = x_pos(point.agent_rounds, point.category)
        y = y_pos(point.trace_bucket, point.category)
        color = CATEGORY_COLORS.get(point.category, CATEGORY_COLORS["unknown"])
        tooltip = (
            f"{point.category}: agent_rounds={point.agent_rounds}, trace={_format_k(point.trace_bucket)}, "
            f"count={point.count}, datasets={','.join(point.datasets)}, "
            f"tasks={','.join(point.task_ids[:12])}"
        )
        svg.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{radius(point.count):.2f}" '
            f'fill="{color}" fill-opacity="0.72" stroke="#111827" stroke-opacity="0.26">'
            f"<title>{escape(tooltip)}</title></circle>"
        )
        if point.count > 1:
            svg.append(
                f'  <text x="{x:.2f}" y="{y + 4:.2f}" text-anchor="middle" '
                'font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#ffffff">'
                f"{point.count}</text>"
            )

    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def write_points_csv(path: Path, points: list[AggregatedPoint]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "category",
                "agent_execution_rounds",
                "trace_length_bucket_chars",
                "trace_length_bucket_k",
                "count",
                "datasets",
                "task_ids",
            ],
        )
        writer.writeheader()
        for point in points:
            writer.writerow(
                {
                    "category": point.category,
                    "agent_execution_rounds": point.agent_rounds,
                    "trace_length_bucket_chars": point.trace_bucket,
                    "trace_length_bucket_k": point.trace_bucket / 1000,
                    "count": point.count,
                    "datasets": " ".join(point.datasets),
                    "task_ids": " ".join(point.task_ids),
                }
            )


def _model_results_root(results_root: Path, runner: str, dataset: str, model_slug: str) -> Path:
    if runner:
        return results_root / runner / dataset / model_slug
    return results_root / dataset / model_slug


def _trace_path(run_dir: Path, summary: dict[str, object]) -> Path:
    trace_file = summary.get("trace_file")
    if isinstance(trace_file, str) and trace_file.strip():
        path = Path(trace_file)
        if not path.is_absolute():
            path = run_dir / path
        return path
    return run_dir / "trace.jsonl"


def _final_answer_is_blank(run_dir: Path, summary: dict[str, object]) -> bool:
    raw_name = summary.get("final_answer_file") or "final_answer.md"
    if not isinstance(raw_name, str) or not raw_name.strip():
        return False
    path = Path(raw_name)
    if path.is_absolute() or ".." in path.parts:
        return False
    final_answer_path = run_dir / path
    if not final_answer_path.exists():
        return False
    return not final_answer_path.read_text(encoding="utf-8", errors="replace").strip()


def _slugify_model_name(model_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", model_name.lower())


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _resolve_output_path(
    output_value: str | None,
    results_root: Path,
    runner: str,
    model_slug: str,
) -> Path:
    if output_value:
        return _resolve_path(output_value)
    root = results_root / runner if runner else results_root
    return root / f"trace_context_scatter_{model_slug}.svg"


def _resolve_csv_output_path(csv_output_value: str | None, output_path: Path) -> Path:
    if csv_output_value:
        return _resolve_path(csv_output_value)
    return output_path.with_suffix(".csv")


def _ceil_to_nice(value: int) -> int:
    if value <= 1000:
        return 1000
    magnitude = 10 ** max(0, len(str(value)) - 2)
    return int(math.ceil(value / magnitude) * magnitude)


def _linear_y_ticks(y_axis_max: int) -> list[int]:
    step = _nice_step(max(1000, y_axis_max) / 6)
    return list(range(0, y_axis_max + step, step))


def _log_y_ticks(y_axis_min: int, y_axis_max: int) -> list[int]:
    ticks: list[int] = []
    power = 10 ** int(math.floor(math.log10(max(1, y_axis_min))))
    while power <= y_axis_max:
        for factor in (1, 2, 5):
            value = factor * power
            if y_axis_min <= value <= y_axis_max:
                ticks.append(value)
        power *= 10
    if y_axis_max not in ticks:
        ticks.append(y_axis_max)
    return sorted(set(ticks))


def _nice_step(raw_step: float) -> int:
    if raw_step <= 1000:
        return 1000
    magnitude = 10 ** int(math.floor(math.log10(raw_step)))
    normalized = raw_step / magnitude
    if normalized <= 1:
        step = 1
    elif normalized <= 2:
        step = 2
    elif normalized <= 5:
        step = 5
    else:
        step = 10
    return int(step * magnitude)


def _format_k(value: int) -> str:
    if value == 0:
        return "0"
    if value % 1000 == 0:
        return f"{value // 1000}k"
    return f"{value / 1000:.1f}k"


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
