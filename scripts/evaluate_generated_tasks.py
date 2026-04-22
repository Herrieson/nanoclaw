from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.evaluator import (
    discover_run_dirs,
    EvaluationJudgeConfig,
    evaluate_run,
    summarize_evaluations,
    write_evaluation_csv,
    write_evaluation_json,
    write_evaluation_summary_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate completed generated-task runs using task-specific verify_rules.py scripts."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["results/data_*/*"],
        help="Run directory paths or glob patterns. Defaults to results/data_*/*.",
    )
    parser.add_argument(
        "--json-out",
        default="results/evaluation.json",
        help="JSON output path for detailed evaluation results.",
    )
    parser.add_argument(
        "--csv-out",
        default="results/evaluation.csv",
        help="CSV output path for summarized evaluation results.",
    )
    parser.add_argument(
        "--summary-out",
        default="results/evaluation_summary.json",
        help="JSON output path for aggregate evaluation metrics.",
    )
    parser.add_argument(
        "--enable-judge",
        action="store_true",
        help="Use verify_prompt.md plus trace.jsonl to obtain a second LLM-judge score.",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Override the auxiliary judge model.",
    )
    parser.add_argument(
        "--judge-base-url",
        default=None,
        help="Override the auxiliary judge base URL.",
    )
    parser.add_argument(
        "--judge-max-attempts",
        type=int,
        default=None,
        help="Maximum attempts for judge output parsing retries.",
    )
    return parser


def _resolve_output(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    run_dirs = discover_run_dirs(args.paths, repo_root=REPO_ROOT)
    if not run_dirs:
        parser.error("No run directories matched the provided paths.")

    judge_config = EvaluationJudgeConfig.from_env()
    if args.enable_judge:
        judge_config = EvaluationJudgeConfig(
            enabled=True,
            model=args.judge_model or judge_config.model or "gpt-4o",
            api_key=judge_config.api_key,
            base_url=args.judge_base_url if args.judge_base_url is not None else judge_config.base_url,
            max_attempts=args.judge_max_attempts or judge_config.max_attempts,
            temperature=judge_config.temperature,
        )

    results = [evaluate_run(run_dir, repo_root=REPO_ROOT, judge_config=judge_config) for run_dir in run_dirs]
    summary = summarize_evaluations(results)
    json_out = _resolve_output(args.json_out)
    csv_out = _resolve_output(args.csv_out)
    summary_out = _resolve_output(args.summary_out)
    write_evaluation_json(results, output_path=json_out)
    write_evaluation_csv(results, output_path=csv_out)
    write_evaluation_summary_json(summary, output_path=summary_out)

    print(
        f"Evaluated {summary.total_runs} run(s): {summary.completed_runs} completed, "
        f"{summary.evaluated_runs} completed objective verification, {summary.scored_runs} produced scores."
    )
    print(
        f"Perfect-score rate: {summary.perfect_score_rate:.2f}% "
        f"({summary.perfect_score_runs}/{summary.total_runs})."
    )
    if summary.benchmark_score is not None:
        print(
            f"Benchmark score: {summary.benchmark_score:.2f}/100 "
            f"(run success rate {summary.run_success_rate:.2f}%, mean objective score {summary.average_objective_score:.2f})."
        )
    else:
        print(
            f"Benchmark score: unavailable "
            f"(run success rate {summary.run_success_rate:.2f}%, no objective scores produced)."
        )
    print(f"JSON report: {json_out}")
    print(f"CSV report: {csv_out}")
    print(f"Summary report: {summary_out}")

    failures = [
        result
        for result in results
        if result.evaluation_status not in {"evaluated", "skipped_run_not_completed"}
    ]
    if failures:
        print("\nEvaluation issues:")
        for result in failures[:20]:
            print(f"- {result.task_id}/{result.run_id}: {result.evaluation_status}")
            if result.error:
                print(f"  error={result.error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
