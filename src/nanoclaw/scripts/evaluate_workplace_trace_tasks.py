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
        "--records-out",
        default=None,
        help=(
            "Self-contained JSONL output path when --no-group-by-model is used. "
            "Defaults to <json-out stem>_records.jsonl."
        ),
    )
    parser.add_argument(
        "--no-records-out",
        action="store_true",
        help="Do not write self-contained per-run records JSONL.",
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
        json_out = _resolve_path(args.json_out)
        records_out = None if args.no_records_out else _combined_records_out(args, json_out=json_out)
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
            json_out=json_out,
            csv_out=_resolve_path(args.csv_out),
            summary_out=_resolve_path(args.summary_out),
            records_out=records_out,
            bundle=bundle,
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
            records_out=None if args.no_records_out else model_dir / "records.jsonl",
            bundle=bundle,
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
    records_out: Path | None,
    bundle: Any,
) -> None:
    summary = summarize_workplace_trace_evaluations(results)
    write_workplace_trace_json(results, output_path=json_out)
    write_workplace_trace_csv(results, output_path=csv_out)
    write_workplace_trace_summary_json(summary, output_path=summary_out)
    if records_out is not None:
        _write_self_contained_records(results, bundle=bundle, output_path=records_out)
    print(f"JSON report: {json_out}")
    print(f"CSV report: {csv_out}")
    print(f"Summary report: {summary_out}")
    if records_out is not None:
        print(f"Records JSONL: {records_out}")


def _combined_records_out(args: argparse.Namespace, *, json_out: Path) -> Path:
    if args.records_out:
        return _resolve_path(args.records_out)
    return json_out.with_name(f"{json_out.stem}_records.jsonl")


def _write_self_contained_records(results, *, bundle: Any, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for result in sorted(results, key=lambda item: (item.task_id, item.run_id)):
            record = _build_self_contained_record(result, bundle=bundle)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _build_self_contained_record(result, *, bundle: Any) -> dict[str, Any]:
    run_dir = result.run_dir
    summary = _read_json_file(result.summary_path)
    resolved_task = _read_json_file(run_dir / "resolved_task.json")
    trace_path = _run_file_from_summary(
        run_dir,
        summary,
        field="trace_file",
        default="trace.jsonl",
    )
    final_answer_path = _run_file_from_summary(
        run_dir,
        summary,
        field="final_answer_file",
        default="final_answer.md",
    )
    verifier = bundle.verifiers.get(result.task_id)

    return {
        "task_id": result.task_id,
        "source_task_id": result.source_task_id,
        "run_id": result.run_id,
        "run_dir": str(run_dir),
        "summary_path": str(result.summary_path),
        "input": {
            "task_yaml": _read_text_file(run_dir / "task.yaml"),
            "resolved_task": resolved_task,
            "prompts": (resolved_task or {}).get("prompts") if isinstance(resolved_task, dict) else None,
            "sessions": (resolved_task or {}).get("sessions") if isinstance(resolved_task, dict) else None,
        },
        "model_trajectory": {
            "trace_file": str(trace_path),
            "trace_events": _read_jsonl_file(trace_path),
            "final_answer_file": str(final_answer_path),
            "final_answer": _read_text_file(final_answer_path),
            "turn_final_answers": _read_turn_final_answers(run_dir, summary),
            "workspace_before": _summary_path_value(run_dir, summary, "before_state_dir"),
            "workspace_after": _summary_path_value(run_dir, summary, "after_state_dir"),
            "turn_workspaces_after": _read_turn_workspace_paths(run_dir, summary),
        },
        "verifier": {
            "source_path": str(result.verifier_source_path) if result.verifier_source_path else None,
            "source_line": result.verifier_source_line,
            "source_task_id": verifier.source_task_id if verifier is not None else result.source_task_id,
            "imported_task_id": verifier.imported_task_id if verifier is not None else result.task_id,
            "workplace_code": verifier.workplace_script if verifier is not None else None,
        },
        "verification_result": {
            "status": result.workplace_status,
            "score": result.workplace_score,
            "score_source": result.workplace_score_source,
            "data": result.workplace_data,
            "exit_code": result.workplace_exit_code,
            "stdout": result.workplace_stdout,
            "stderr": result.workplace_stderr,
            "error": result.workplace_error,
            "objective_score": result.objective_score,
            "objective_score_source": result.objective_score_source,
            "evaluation_status": result.evaluation_status,
        },
        "evaluation": result.to_dict(),
    }


def _read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _read_jsonl_file(path: Path) -> list[Any]:
    if not path.is_file():
        return []
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError:
                rows.append({"line_number": line_number, "raw": stripped})
    return rows


def _read_text_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def _run_file_from_summary(
    run_dir: Path,
    summary: dict[str, Any] | None,
    *,
    field: str,
    default: str,
) -> Path:
    value = summary.get(field) if isinstance(summary, dict) else None
    if not isinstance(value, str) or not value.strip():
        value = default
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return run_dir / default
    return run_dir / relative


def _summary_path_value(run_dir: Path, summary: dict[str, Any] | None, field: str) -> str | None:
    value = summary.get(field) if isinstance(summary, dict) else None
    if not isinstance(value, str) or not value.strip():
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    return str(run_dir / relative)


def _read_turn_final_answers(run_dir: Path, summary: dict[str, Any] | None) -> list[dict[str, Any]]:
    turns = summary.get("turns") if isinstance(summary, dict) else None
    if not isinstance(turns, list):
        return []
    records = []
    for item in turns:
        if not isinstance(item, dict):
            continue
        file_path = _run_file_from_turn_summary(run_dir, item, field="final_answer_file")
        records.append(
            {
                "turn": item.get("turn"),
                "file": str(file_path) if file_path is not None else None,
                "content": _read_text_file(file_path) if file_path is not None else None,
            }
        )
    return records


def _read_turn_workspace_paths(run_dir: Path, summary: dict[str, Any] | None) -> list[dict[str, Any]]:
    turns = summary.get("turns") if isinstance(summary, dict) else None
    if not isinstance(turns, list):
        return []
    records = []
    for item in turns:
        if not isinstance(item, dict):
            continue
        after_path = _run_file_from_turn_summary(run_dir, item, field="after_state_dir")
        records.append(
            {
                "turn": item.get("turn"),
                "workspace_after": str(after_path) if after_path is not None else None,
            }
        )
    return records


def _run_file_from_turn_summary(run_dir: Path, item: dict[str, Any], *, field: str) -> Path | None:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    return run_dir / relative


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
    if status == "completed" and _final_answer_is_blank(run_dir, payload):
        return "failed_empty_final_answer"
    return status if isinstance(status, str) else None


def _final_answer_is_blank(run_dir: Path, summary: dict[str, object]) -> bool:
    raw_name = summary.get("final_answer_file") or "final_answer.md"
    if not isinstance(raw_name, str):
        return True
    try:
        text = (run_dir / raw_name).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True
    return not text.strip()


def _resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


if __name__ == "__main__":
    raise SystemExit(main())
