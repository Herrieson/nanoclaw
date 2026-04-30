from __future__ import annotations

import argparse
import concurrent.futures
from collections import defaultdict
import json
import os
from pathlib import Path
import sys
import threading
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.evaluator import EvaluationJudgeConfig, discover_run_dirs
from nanoclaw.workplace_trace_evaluator import (
    evaluate_workplace_trace_run,
    load_verifier_bundle,
    summarize_workplace_trace_evaluations,
    write_workplace_trace_csv,
    write_workplace_trace_json,
    write_workplace_trace_summary_json,
)


DEFAULT_VERIFIER_JSONL = [
    "doc/todo/gemini3_2000_score_new_verifier_1.jsonl",
    "doc/todo/gemini3_2000_score_new_verifier_2.jsonl",
    "doc/todo/gemini3_2000_score_new_verifier_3.jsonl",
]


class ProgressTracker:
    def __init__(self, total: int, *, label: str) -> None:
        self.total = total
        self.label = label
        self.completed = 0
        self.succeeded = 0
        self.failed = 0
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
        suffix = f" {self.label} {self.completed}/{self.total} ok={self.succeeded} fail={self.failed}"
        if current_task:
            suffix += f" last={current_task}"
        sys.stderr.write(f"\r[{bar}]{suffix}")
        sys.stderr.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate generated-task runs with the new workplace/trace verifier scheme. "
            "By default this evaluates results/base grouped by model and writes to results/base_new_verifier."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["results/base/*/data_round_01_*/*"],
        help="Run directory paths or glob patterns. Defaults to results/base/*/data_round_01_*/*.",
    )
    parser.add_argument(
        "--verifier-jsonl",
        nargs="+",
        default=DEFAULT_VERIFIER_JSONL,
        help="New-verifier JSONL files containing verify_workplace.py and verify_trace.md blocks.",
    )
    parser.add_argument(
        "--manifest",
        default=".staging/round_01/import_manifest.jsonl",
        help="Import manifest mapping source data_N ids to imported task ids.",
    )
    parser.add_argument(
        "--components",
        choices=("full", "workplace", "trace"),
        default="full",
        help="Evaluation components. full averages workplace and trace, requiring both scores.",
    )
    parser.add_argument(
        "--enable-judge",
        action="store_true",
        help="Enable LLM judging for trace verification.",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Trace judge model. Defaults to NANOCLAW_EVAL_MODEL or gpt-4o.",
    )
    parser.add_argument(
        "--judge-base-url",
        default=None,
        help="Trace judge base URL.",
    )
    parser.add_argument(
        "--judge-max-attempts",
        type=int,
        default=None,
        help="Maximum trace judge parse retries.",
    )
    parser.add_argument(
        "--workplace-judge-model",
        default=None,
        help="Model exposed to generated verify_workplace.py scripts as MOCK_MODEL_NAME.",
    )
    parser.add_argument(
        "--workplace-judge-base-url",
        default=None,
        help="Base URL exposed to generated verify_workplace.py scripts as MOCK_API_BASE.",
    )
    parser.add_argument(
        "--workplace-judge-api-key",
        default=None,
        help="API key exposed to generated verify_workplace.py scripts as MOCK_API_KEY.",
    )
    parser.add_argument(
        "--workplace-timeout",
        type=float,
        default=180.0,
        help="Per-run timeout for verify_workplace.py. Default is 180 seconds.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Concurrent evaluation workers. Default is 10.",
    )
    parser.add_argument(
        "--output-root",
        default="results/base_new_verifier",
        help="Output root used when grouping by model.",
    )
    parser.add_argument(
        "--no-group-by-model",
        action="store_true",
        help="Write one combined report instead of per-model reports.",
    )
    parser.add_argument(
        "--json-out",
        default="results/new_verifier_evaluation.json",
        help="Combined JSON output path when --no-group-by-model is used.",
    )
    parser.add_argument(
        "--csv-out",
        default="results/new_verifier_evaluation.csv",
        help="Combined CSV output path when --no-group-by-model is used.",
    )
    parser.add_argument(
        "--summary-out",
        default="results/new_verifier_evaluation_summary.json",
        help="Combined summary output path when --no-group-by-model is used.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Evaluate only the first N matched run directories.",
    )
    parser.add_argument(
        "--select-run-per-task",
        choices=("all", "latest", "latest-completed"),
        default="all",
        help=(
            "Select at most one run per model/task before evaluating. "
            "`latest-completed` uses the latest completed run when available, otherwise latest."
        ),
    )
    parser.add_argument(
        "--allow-issues",
        action="store_true",
        help="Return exit code 0 after writing reports even if some runs have evaluation issues.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.components in {"full", "trace"} and not args.enable_judge:
        parser.error("--enable-judge is required when --components is full or trace.")

    manifest_path = _resolve_path(args.manifest)
    verifier_paths = [_resolve_path(path) for path in args.verifier_jsonl]
    bundle = load_verifier_bundle(verifier_paths, manifest_path=manifest_path)

    run_dirs = discover_run_dirs(args.paths, repo_root=REPO_ROOT)
    run_dirs = _select_run_dirs(run_dirs, mode=args.select_run_per_task)
    if args.max_runs is not None:
        run_dirs = run_dirs[: args.max_runs]
    if not run_dirs:
        parser.error("No run directories matched the provided paths.")

    judge_config = _build_judge_config(args)
    workplace_env = _build_workplace_env(args, judge_config)

    print(
        "Loaded new verifier bundle: "
        f"{bundle.mapped_record_count}/{bundle.manifest_task_count} manifest task(s) covered "
        f"from {bundle.jsonl_record_count} JSONL record(s)."
    )
    print(f"Matched {len(run_dirs)} run directory/directories.")

    if args.no_group_by_model:
        results = _evaluate_group(
            run_dirs,
            label="combined",
            args=args,
            judge_config=judge_config,
            workplace_env=workplace_env,
            bundle=bundle,
        )
        _write_group_outputs(
            results,
            json_out=_resolve_path(args.json_out),
            csv_out=_resolve_path(args.csv_out),
            summary_out=_resolve_path(args.summary_out),
        )
        group_exit_code = _print_group_summary("combined", results)
        return 0 if args.allow_issues else group_exit_code

    groups: dict[str, list[Path]] = defaultdict(list)
    for run_dir in run_dirs:
        groups[_infer_model_group(run_dir)].append(run_dir)

    exit_code = 0
    output_root = _resolve_path(args.output_root)
    for model_name in sorted(groups):
        results = _evaluate_group(
            groups[model_name],
            label=model_name,
            args=args,
            judge_config=judge_config,
            workplace_env=workplace_env,
            bundle=bundle,
        )
        model_dir = output_root / model_name
        _write_group_outputs(
            results,
            json_out=model_dir / "evaluation.json",
            csv_out=model_dir / "evaluation.csv",
            summary_out=model_dir / "evaluation_summary.json",
        )
        exit_code = max(exit_code, _print_group_summary(model_name, results))
    return 0 if args.allow_issues else exit_code


def _evaluate_group(
    run_dirs: list[Path],
    *,
    label: str,
    args: argparse.Namespace,
    judge_config: EvaluationJudgeConfig,
    workplace_env: dict[str, str],
    bundle: Any,
):
    tracker = ProgressTracker(total=len(run_dirs), label=label)
    tracker.start()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_run = {
            executor.submit(
                evaluate_workplace_trace_run,
                run_dir,
                verifiers=bundle.verifiers,
                components=args.components,
                judge_config=judge_config,
                workplace_env=workplace_env,
                workplace_timeout=args.workplace_timeout,
            ): run_dir
            for run_dir in run_dirs
        }
        for future in concurrent.futures.as_completed(future_to_run):
            run_dir = future_to_run[future]
            try:
                result = future.result()
                results.append(result)
                tracker.advance(
                    success=result.evaluation_status
                    in {"evaluated", "skipped_run_not_completed", "skipped_infra_failure"},
                    current_task=result.task_id,
                )
            except Exception as exc:
                sys.stderr.write(f"\n[Error] Evaluating {run_dir} generated an exception: {exc}\n")
                tracker.advance(success=False, current_task="ERROR")
    return sorted(results, key=lambda item: (item.task_id, item.run_id))


def _write_group_outputs(
    results,
    *,
    json_out: Path,
    csv_out: Path,
    summary_out: Path,
) -> None:
    summary = summarize_workplace_trace_evaluations(results)
    write_workplace_trace_json(results, output_path=json_out)
    write_workplace_trace_csv(results, output_path=csv_out)
    write_workplace_trace_summary_json(summary, output_path=summary_out)
    print(f"JSON report: {json_out}")
    print(f"CSV report: {csv_out}")
    print(f"Summary report: {summary_out}")


def _print_group_summary(model_name: str, results) -> int:
    summary = summarize_workplace_trace_evaluations(results)
    print(
        f"{model_name}: evaluated {summary.total_runs} run(s), "
        f"{summary.completed_runs} completed, {summary.scored_runs} scored."
    )
    print(
        f"{model_name}: perfect-score rate {summary.perfect_score_rate:.2f}% "
        f"({summary.perfect_score_runs}/{summary.total_runs}), "
        f"average objective score {summary.average_objective_score}."
    )
    failures = [
        result
        for result in results
        if result.evaluation_status
        not in {"evaluated", "skipped_run_not_completed", "skipped_infra_failure"}
    ]
    if failures:
        print(f"{model_name}: evaluation issues {len(failures)}. First 10:")
        for result in failures[:10]:
            print(f"- {result.task_id}/{result.run_id}: {result.evaluation_status}")
            if result.error:
                print(f"  error={result.error}")
        return 1
    return 0


def _build_judge_config(args: argparse.Namespace) -> EvaluationJudgeConfig:
    env_config = EvaluationJudgeConfig.from_env()
    if not args.enable_judge:
        return EvaluationJudgeConfig.disabled()
    return EvaluationJudgeConfig(
        enabled=True,
        model=args.judge_model or env_config.model or "gpt-4o",
        api_key=env_config.api_key,
        base_url=args.judge_base_url if args.judge_base_url is not None else env_config.base_url,
        max_attempts=args.judge_max_attempts or env_config.max_attempts,
        temperature=env_config.temperature,
    )


def _build_workplace_env(args: argparse.Namespace, judge_config: EvaluationJudgeConfig) -> dict[str, str]:
    env: dict[str, str] = {}
    api_key = (
        args.workplace_judge_api_key
        or os.getenv("MOCK_API_KEY")
        or os.getenv("NANOCLAW_EVAL_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    base_url = (
        args.workplace_judge_base_url
        or os.getenv("MOCK_API_BASE")
        or judge_config.base_url
        or os.getenv("NANOCLAW_EVAL_BASE_URL")
    )
    model = (
        args.workplace_judge_model
        or os.getenv("MOCK_MODEL_NAME")
        or judge_config.model
        or os.getenv("NANOCLAW_EVAL_MODEL")
    )
    if api_key:
        env["MOCK_API_KEY"] = api_key
    if base_url:
        env["MOCK_API_BASE"] = base_url
    if model:
        env["MOCK_MODEL_NAME"] = model
    return env


def _infer_model_group(run_dir: Path) -> str:
    try:
        relative = run_dir.resolve().relative_to(REPO_ROOT)
    except ValueError:
        relative = run_dir
    parts = relative.parts
    if (
        len(parts) >= 5
        and parts[0] == "results"
        and parts[1]
        in {"base", "skills", "skills_aligned", "hard", "hard_100", "multi_turn", "multi_turn_100"}
    ):
        return parts[2]
    if len(parts) >= 4 and parts[0] == "results":
        return parts[1]
    return run_dir.parent.parent.name


def _select_run_dirs(run_dirs: list[Path], *, mode: str) -> list[Path]:
    if mode == "all":
        return run_dirs

    grouped: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for run_dir in run_dirs:
        grouped[(_infer_model_group(run_dir), run_dir.parent.name)].append(run_dir)

    selected: list[Path] = []
    for candidates in grouped.values():
        ordered = sorted(candidates, key=lambda item: item.name)
        if mode == "latest":
            selected.append(ordered[-1])
            continue
        if mode == "latest-completed":
            completed = [
                candidate
                for candidate in ordered
                if _run_status(candidate) == "completed"
            ]
            selected.append((completed or ordered)[-1])
            continue
        raise ValueError(f"Unsupported select-run-per-task mode: {mode}")
    return sorted(selected)


def _run_status(run_dir: Path) -> str | None:
    summary_path = run_dir / "summary.json"
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    status = payload.get("status")
    return status if isinstance(status, str) else None


def _resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


if __name__ == "__main__":
    raise SystemExit(main())
