from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_workplace_chart_data import Sheet, write_xlsx  # noqa: E402


DOCKER_RUNNERS = ("openclaw", "hermes", "codex")

MODELS: tuple[tuple[str, str], ...] = (
    ("qwen36p", "qwen36plus"),
    ("qwen35p", "qwen35plus"),
    ("qwen35f", "qwen35flash"),
    ("qwen3527b", "qwen3527b"),
    ("glm5.1", "glm51"),
    ("glm4.7", "glm47"),
    ("minimax2.1", "minimaxm21"),
    ("minimax2.5", "minimaxm25"),
    ("deepseekv4pro", "deepseekv4pro"),
    ("deepseekv4flash", "deepseekv4flash"),
    ("deepseekv3.2", "deepseekv32"),
)

DATASETS: tuple[dict[str, Any], ...] = (
    {
        "name": "round_01_aligned_mix_subset_100",
        "prefix": "round01",
        "groups": (
            ("base", "base"),
            ("skills", "skills_aligned"),
            ("hard", "hard_aligned"),
            ("multiturn", "multi_turn_aligned"),
        ),
    },
    {
        "name": "persona_aligned_mix_subset_100",
        "prefix": "persona",
        "groups": (
            ("base", "base"),
            ("skills", "skills"),
            ("hard", "hard"),
            ("multiturn", "multi_turn"),
        ),
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export the final Docker workplace score matrix with one sheet per runner."
    )
    parser.add_argument(
        "--eval-root",
        default="results/docker_workplace_suite_eval",
        help="Docker workplace evaluation root.",
    )
    parser.add_argument(
        "--nanoclaw-eval-root",
        default="results/nanoclaw_workplace_suite_eval",
        help="Built-in Nanoclaw workplace evaluation root to append as a nanoclaw sheet.",
    )
    parser.add_argument(
        "--output",
        default="results/docker_workplace_suite_eval/final_score_summary.xlsx",
        help="Output workbook path.",
    )
    parser.add_argument(
        "--metric",
        default="average_objective_score",
        choices=("average_objective_score", "benchmark_score", "perfect_score_rate"),
        help=(
            "Metric to place in score cells. The default is average_objective_score, "
            "matching the chart's objective-score bars."
        ),
    )
    parser.add_argument(
        "--cell-format",
        default="score_perfect_rate",
        choices=("score", "score_perfect_rate"),
        help=(
            "Cell format. score_perfect_rate writes average_objective_score/perfect_score_rate, "
            "for example 78.00/24.00."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    eval_root = _resolve_path(args.eval_root)
    nanoclaw_eval_root = _resolve_path(args.nanoclaw_eval_root)
    output_path = _resolve_path(args.output)
    if not eval_root.exists():
        raise SystemExit(f"Evaluation root does not exist: {eval_root}")
    if not nanoclaw_eval_root.exists():
        raise SystemExit(f"Nanoclaw evaluation root does not exist: {nanoclaw_eval_root}")

    sheets = [
        build_runner_sheet(
            eval_root / runner,
            runner,
            metric=args.metric,
            cell_format=args.cell_format,
        )
        for runner in DOCKER_RUNNERS
    ]
    sheets.append(
        build_runner_sheet(
            nanoclaw_eval_root,
            "nanoclaw",
            metric=args.metric,
            cell_format=args.cell_format,
        )
    )
    sheets.append(
        build_token_usage_sheet(
            docker_eval_root=eval_root,
            nanoclaw_eval_root=nanoclaw_eval_root,
        )
    )
    write_xlsx(output_path, sheets)
    print(f"Wrote final Docker score workbook to {output_path}")
    return 0


def build_runner_sheet(
    runner_eval_root: Path,
    sheet_name: str,
    *,
    metric: str,
    cell_format: str,
) -> Sheet:
    headers = ["model"]
    for dataset in DATASETS:
        prefix = dataset["prefix"]
        for display_group, _group_dir in dataset["groups"]:
            headers.append(f"{prefix}_{display_group}")
        headers.append(f"{prefix}_overall")
    headers.append("combined_overall")
    headers.append("missing")

    rows: list[list[Any]] = [
        ["score_metric", metric],
        ["cell_format", cell_format],
        ["source_eval_root", _repo_relative(runner_eval_root)],
        [
            "note",
            (
                "Scores and perfect-score rates are 0-100. In score_perfect_rate mode, cells "
                "are average_objective_score/perfect_score_rate. Blank cells mean the "
                "corresponding summary file is missing. combined_overall is computed from both "
                "datasets."
            ),
        ],
        [],
        headers,
    ]

    for model_display, model_slug in MODELS:
        row: list[Any] = [model_display]
        missing: list[str] = []
        for dataset in DATASETS:
            dataset_name = dataset["name"]
            prefix = dataset["prefix"]
            for display_group, group_dir in dataset["groups"]:
                summary_path = (
                    runner_eval_root
                    / dataset_name
                    / "_group_reports"
                    / group_dir
                    / model_slug
                    / "evaluation_summary.json"
                )
                score = _summary_score(summary_path, metric=metric)
                row.append(
                    _summary_cell(summary_path, metric=metric, cell_format=cell_format)
                )
                if score is None:
                    missing.append(f"{prefix}_{display_group}")

            overall_summary_path = (
                runner_eval_root
                / dataset_name
                / "merged"
                / model_slug
                / "evaluation_summary.json"
            )
            score = _summary_score(overall_summary_path, metric=metric)
            row.append(
                _summary_cell(overall_summary_path, metric=metric, cell_format=cell_format)
            )
            if score is None:
                missing.append(f"{prefix}_overall")

        combined_score = _combined_score(runner_eval_root, model_slug, metric=metric)
        combined_cell = _combined_cell(
            runner_eval_root,
            model_slug,
            metric=metric,
            cell_format=cell_format,
        )
        row.append(combined_cell)
        if combined_score is None:
            missing.append("combined_overall")
        row.append(", ".join(missing))
        rows.append(row)

    return Sheet(name=sheet_name, rows=rows)


def _summary_score(summary_path: Path, *, metric: str) -> float | None:
    if not summary_path.exists():
        return None
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{summary_path} is not a JSON object")
    value = payload.get(metric)
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    return 0.0


def _summary_cell(summary_path: Path, *, metric: str, cell_format: str) -> str | float | None:
    score = _summary_score(summary_path, metric=metric)
    if score is None:
        return None
    if cell_format == "score":
        return score
    perfect_rate = _summary_score(summary_path, metric="perfect_score_rate")
    if perfect_rate is None:
        perfect_rate = 0.0
    return f"{score:.2f}/{perfect_rate:.2f}"


def _combined_score(runner_eval_root: Path, model_slug: str, *, metric: str) -> float | None:
    if metric == "average_objective_score":
        scores: list[float] = []
        for dataset in DATASETS:
            evaluation_path = (
                runner_eval_root
                / dataset["name"]
                / "merged"
                / model_slug
                / "evaluation.json"
            )
            scores.extend(_objective_scores(evaluation_path))
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)

    weighted_values: list[tuple[float, int]] = []
    for dataset in DATASETS:
        summary_path = (
            runner_eval_root
            / dataset["name"]
            / "merged"
            / model_slug
            / "evaluation_summary.json"
        )
        if not summary_path.exists():
            continue
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{summary_path} is not a JSON object")
        value = payload.get(metric)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            value = 0.0
        weight = payload.get("total_runs")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            weight = 0
        if weight > 0:
            weighted_values.append((float(value), int(weight)))
    if not weighted_values:
        return None
    total_weight = sum(weight for _value, weight in weighted_values)
    return round(sum(value * weight for value, weight in weighted_values) / total_weight, 2)


def _combined_cell(
    runner_eval_root: Path,
    model_slug: str,
    *,
    metric: str,
    cell_format: str,
) -> str | float | None:
    score = _combined_score(runner_eval_root, model_slug, metric=metric)
    if score is None:
        return None
    if cell_format == "score":
        return score
    perfect_rate = _combined_perfect_score_rate(runner_eval_root, model_slug)
    if perfect_rate is None:
        perfect_rate = 0.0
    return f"{score:.2f}/{perfect_rate:.2f}"


def _combined_perfect_score_rate(runner_eval_root: Path, model_slug: str) -> float | None:
    total = 0
    perfect = 0
    for dataset in DATASETS:
        evaluation_path = (
            runner_eval_root
            / dataset["name"]
            / "merged"
            / model_slug
            / "evaluation.json"
        )
        if not evaluation_path.exists():
            continue
        payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"{evaluation_path} is not a JSON array")
        for item in payload:
            if not isinstance(item, dict):
                continue
            total += 1
            if item.get("evaluation_status") != "evaluated":
                continue
            value = item.get("objective_score")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            if float(value) == 100.0:
                perfect += 1
    if total == 0:
        return None
    return round((perfect / total) * 100, 2)


def _objective_scores(evaluation_path: Path) -> list[float]:
    if not evaluation_path.exists():
        return []
    payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{evaluation_path} is not a JSON array")
    scores: list[float] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        if item.get("evaluation_status") != "evaluated":
            continue
        value = item.get("objective_score")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        scores.append(float(value))
    return scores


def build_token_usage_sheet(*, docker_eval_root: Path, nanoclaw_eval_root: Path) -> Sheet:
    headers = [
        "framework",
        "model",
        "dataset",
        "avg_estimated_tokens_per_task",
        "estimated_source",
        "evaluated_run_count",
        "estimated_run_count",
        "avg_api_total_tokens_exact_per_task",
        "avg_api_peak_turn_tokens_exact_per_task",
        "api_exact_run_count",
        "avg_api_input_tokens_exact",
        "avg_api_cached_input_tokens_exact",
        "avg_api_output_tokens_exact",
        "avg_api_reasoning_output_tokens_exact",
        "skipped_non_evaluated_count",
        "missing",
    ]
    rows: list[list[Any]] = [
        [
            "note",
            (
                "avg_estimated_tokens_per_task is the comparable cross-framework estimate: saved "
                "runner trace/session text length divided by 4, averaged over evaluation_status=evaluated "
                "runs only. API exact columns are filled only when trace events expose usage. "
                "avg_api_total_tokens_exact_per_task is billing-like and sums all model calls in a task; "
                "avg_api_peak_turn_tokens_exact_per_task uses only the largest single call/turn to avoid "
                "summing repeated context when comparing context scale."
            ),
        ],
        [],
        headers,
    ]

    runner_roots: tuple[tuple[str, Path], ...] = (
        *((runner, docker_eval_root / runner) for runner in DOCKER_RUNNERS),
        ("nanoclaw", nanoclaw_eval_root),
    )
    for framework, runner_root in runner_roots:
        for model_display, model_slug in MODELS:
            for dataset in DATASETS:
                dataset_name = str(dataset["name"])
                dataset_display = str(dataset["prefix"])
                row = token_usage_row(
                    runner_root,
                    framework=framework,
                    model_display=model_display,
                    model_slug=model_slug,
                    dataset_name=dataset_name,
                    dataset_display=dataset_display,
                )
                rows.append([row.get(header) for header in headers])

    return Sheet(name="token_usage", rows=rows)


def token_usage_row(
    runner_root: Path,
    *,
    framework: str,
    model_display: str,
    model_slug: str,
    dataset_name: str,
    dataset_display: str,
) -> dict[str, Any]:
    evaluation_path = runner_root / dataset_name / "merged" / model_slug / "evaluation.json"
    base_row: dict[str, Any] = {
        "framework": framework,
        "model": model_display,
        "dataset": dataset_display,
        "avg_estimated_tokens_per_task": None,
        "estimated_source": "trace_estimate",
        "evaluated_run_count": 0,
        "estimated_run_count": 0,
        "avg_api_total_tokens_exact_per_task": None,
        "avg_api_peak_turn_tokens_exact_per_task": None,
        "api_exact_run_count": 0,
        "avg_api_input_tokens_exact": None,
        "avg_api_cached_input_tokens_exact": None,
        "avg_api_output_tokens_exact": None,
        "avg_api_reasoning_output_tokens_exact": None,
        "skipped_non_evaluated_count": 0,
        "missing": "",
    }
    if not evaluation_path.exists():
        base_row["missing"] = "missing evaluation.json"
        return base_row

    payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{evaluation_path} is not a JSON array")

    estimate_totals: list[float] = []
    exact_usage: list[dict[str, float]] = []
    missing_runs = 0
    skipped_non_evaluated = 0
    evaluated_run_count = 0

    for item in payload:
        if not isinstance(item, dict):
            continue
        if item.get("evaluation_status") != "evaluated":
            skipped_non_evaluated += 1
            continue
        evaluated_run_count += 1
        run_dir_value = item.get("run_dir")
        if not isinstance(run_dir_value, str) or not run_dir_value.strip():
            missing_runs += 1
            continue
        run_dir = Path(run_dir_value)
        if not run_dir.exists():
            missing_runs += 1
            continue

        usage = _exact_usage_from_run(run_dir)
        if usage and usage["total_tokens"] > 0:
            exact_usage.append(usage)

        estimate = _estimated_tokens_from_run(run_dir)
        if estimate is not None:
            estimate_totals.append(estimate)
        else:
            missing_runs += 1

    exact_run_count = len(exact_usage)
    estimated_run_count = len(estimate_totals)
    base_row["evaluated_run_count"] = evaluated_run_count
    base_row["estimated_run_count"] = estimated_run_count
    base_row["api_exact_run_count"] = exact_run_count
    base_row["skipped_non_evaluated_count"] = skipped_non_evaluated
    if estimate_totals:
        base_row["avg_estimated_tokens_per_task"] = _avg(estimate_totals)
    base_row["avg_api_total_tokens_exact_per_task"] = _avg_usage_field(exact_usage, "total_tokens")
    base_row["avg_api_peak_turn_tokens_exact_per_task"] = _avg_usage_field(
        exact_usage,
        "peak_turn_tokens",
    )
    base_row["avg_api_input_tokens_exact"] = _avg_usage_field(exact_usage, "input_tokens")
    base_row["avg_api_cached_input_tokens_exact"] = _avg_usage_field(
        exact_usage,
        "cached_input_tokens",
    )
    base_row["avg_api_output_tokens_exact"] = _avg_usage_field(exact_usage, "output_tokens")
    base_row["avg_api_reasoning_output_tokens_exact"] = _avg_usage_field(
        exact_usage,
        "reasoning_output_tokens",
    )
    if missing_runs:
        base_row["missing"] = f"{missing_runs} run(s) missing token source"
    return base_row


def _exact_usage_from_run(run_dir: Path) -> dict[str, float] | None:
    trace_path = run_dir / "trace.jsonl"
    if not trace_path.exists():
        return None

    totals = {
        "input_tokens": 0.0,
        "cached_input_tokens": 0.0,
        "output_tokens": 0.0,
        "reasoning_output_tokens": 0.0,
        "total_tokens": 0.0,
        "peak_turn_tokens": 0.0,
    }
    found = False
    for raw_line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = None
        if isinstance(item, dict):
            event = item.get("event")
            if isinstance(event, dict) and isinstance(event.get("usage"), dict):
                usage = event["usage"]
            elif isinstance(item.get("usage"), dict):
                usage = item["usage"]
        if not isinstance(usage, dict):
            continue
        input_tokens = _numeric_value(usage.get("input_tokens"))
        cached_input_tokens = _numeric_value(usage.get("cached_input_tokens"))
        output_tokens = _numeric_value(usage.get("output_tokens"))
        reasoning_output_tokens = _numeric_value(usage.get("reasoning_output_tokens"))
        total_tokens = _numeric_value(usage.get("total_tokens"))
        if total_tokens is None:
            total_tokens = (input_tokens or 0.0) + (output_tokens or 0.0)
        if total_tokens <= 0:
            continue
        found = True
        totals["input_tokens"] += input_tokens or 0.0
        totals["cached_input_tokens"] += cached_input_tokens or 0.0
        totals["output_tokens"] += output_tokens or 0.0
        totals["reasoning_output_tokens"] += reasoning_output_tokens or 0.0
        totals["total_tokens"] += total_tokens
        totals["peak_turn_tokens"] = max(totals["peak_turn_tokens"], total_tokens)

    return totals if found else None


def _estimated_tokens_from_run(run_dir: Path) -> float | None:
    trace_files = _estimate_source_files(run_dir)
    if not trace_files:
        return None
    total_chars = 0
    for path in trace_files:
        try:
            total_chars += len(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    if total_chars <= 0:
        return None
    return float(math.ceil(total_chars / 4))


def _estimate_source_files(run_dir: Path) -> list[Path]:
    codex_trace = run_dir / "trace.jsonl"
    openclaw_session_root = run_dir / "runner_state" / "home" / ".openclaw" / "agents" / "main" / "sessions"
    hermes_session_root = run_dir / "runner_state" / "sessions"

    if openclaw_session_root.is_dir():
        files = sorted(openclaw_session_root.glob("*.trajectory.jsonl"))
        if files:
            return files
    if hermes_session_root.is_dir():
        files = sorted(hermes_session_root.glob("session_*.json"))
        if files:
            return files
    if codex_trace.exists():
        return [codex_trace]
    return []


def _avg_usage_field(rows: list[dict[str, float]], field: str) -> float | None:
    if not rows:
        return None
    return _avg([row.get(field, 0.0) for row in rows])


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


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


if __name__ == "__main__":
    raise SystemExit(main())
