from __future__ import annotations

import argparse
import concurrent.futures
import threading
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


class ProgressTracker:
    def __init__(self, total: int) -> None:
        self.total = total
        self.completed = 0
        self.succeeded = 0
        self.failed = 0
        # 添加线程锁以确保多线程下进度更新和输出的安全
        self._lock = threading.Lock()

    def start(self) -> None:
        self._render(current_task=None)

    def advance(self, *, success: bool, current_task: str) -> None:
        with self._lock:
            self.completed += 1
            if success:
                self.succeeded += 1
            else:
                self.failed += 1
            self._render(current_task=current_task)
            if self.completed == self.total:
                sys.stderr.write("\n")
                sys.stderr.flush()

    def _render(self, *, current_task: str | None) -> None:
        width = 24
        ratio = 0 if self.total == 0 else self.completed / self.total
        filled = int(width * ratio)
        bar = "#" * filled + "-" * (width - filled)
        suffix = (
            f" {self.completed}/{self.total} ok={self.succeeded} fail={self.failed}"
        )
        if current_task:
            suffix += f" last={current_task}"
        sys.stderr.write(f"\r[{bar}]{suffix}")
        sys.stderr.flush()


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
    # 新增并发控制参数
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers for evaluation. Default is 10.",
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

    tracker = ProgressTracker(total=len(run_dirs))
    tracker.start()
    results = []
    
    # 使用线程池进行并发评估
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_run = {
            executor.submit(evaluate_run, run_dir, repo_root=REPO_ROOT, judge_config=judge_config): run_dir
            for run_dir in run_dirs
        }

        for future in concurrent.futures.as_completed(future_to_run):
            run_dir = future_to_run[future]
            try:
                result = future.result()
                results.append(result)
                tracker.advance(
                    success=result.evaluation_status in {"evaluated", "skipped_run_not_completed"},
                    current_task=result.task_id,
                )
            except Exception as exc:
                sys.stderr.write(f"\n[Error] Evaluating {run_dir} generated an exception: {exc}\n")
                # 即使发生异常也需推进进度条，防止卡死
                tracker.advance(success=False, current_task="ERROR")

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
        if getattr(result, "evaluation_status", None) not in {"evaluated", "skipped_run_not_completed"}
    ]
    if failures:
        print("\nEvaluation issues:")
        for result in failures[:20]:
            task_id = getattr(result, "task_id", "Unknown")
            run_id = getattr(result, "run_id", "Unknown")
            status = getattr(result, "evaluation_status", "Failed/Error")
            print(f"- {task_id}/{run_id}: {status}")
            error = getattr(result, "error", None)
            if error:
                print(f"  error={error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())