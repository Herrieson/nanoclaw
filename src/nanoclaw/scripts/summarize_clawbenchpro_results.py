from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_EVAL_ROOT = Path("results/clawbenchpro_eval")


def main() -> int:
    args = build_parser().parse_args()
    roots = [path.expanduser().resolve() for path in args.paths]
    summaries = []
    for root in roots:
        summaries.extend(discover_summaries(root))
    if not summaries:
        raise SystemExit("No evaluation_summary.json files were found.")

    rows = [summary_row(path, payload) for path, payload in summaries]
    rows.sort(key=lambda row: (row["subset"], row["runner"], row["model"], row["dataset"]))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print_table(rows)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print a compact table for ClawBenchPro workplace evaluation summaries."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[DEFAULT_EVAL_ROOT],
        help=f"Evaluation roots to scan. Default: {DEFAULT_EVAL_ROOT}",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table.")
    return parser


def discover_summaries(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    paths = [root] if root.name == "evaluation_summary.json" else sorted(root.rglob("evaluation_summary.json"))
    summaries = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            summaries.append((path, payload))
    return summaries


def summary_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if path.parent.parent.name == "merged":
        dataset = path.parent.parent.parent.name
        model = path.parent.name
        runner = "-"
        subset = "-"
    else:
        dataset = path.parent.name
        model = path.parent.parent.name if len(path.parents) > 1 else "-"
        runner = path.parent.parent.parent.name if len(path.parents) > 2 else "-"
        subset = path.parent.parent.parent.parent.name if len(path.parents) > 3 else "-"
    return {
        "subset": subset or "-",
        "runner": runner or "-",
        "model": model,
        "dataset": dataset,
        "total": payload.get("total_runs"),
        "completed": payload.get("completed_runs"),
        "scored": payload.get("scored_runs"),
        "avg": payload.get("average_objective_score"),
        "workplace_avg": payload.get("average_workplace_score"),
        "perfect_rate": payload.get("perfect_score_rate"),
        "issues": payload.get("evaluation_issue_runs"),
        "path": str(path),
    }


def print_table(rows: list[dict[str, Any]]) -> None:
    headers = [
        "subset",
        "runner",
        "model",
        "dataset",
        "total",
        "completed",
        "scored",
        "avg",
        "perfect%",
        "issues",
    ]
    table_rows = [
        [
            row["subset"],
            row["runner"],
            row["model"],
            row["dataset"],
            format_value(row["total"]),
            format_value(row["completed"]),
            format_value(row["scored"]),
            format_value(row["avg"]),
            format_value(row["perfect_rate"]),
            format_value(row["issues"]),
        ]
        for row in rows
    ]
    widths = [
        max(len(str(value)) for value in [header, *(row[index] for row in table_rows)])
        for index, header in enumerate(headers)
    ]
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in table_rows:
        print("  ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)))


def format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
