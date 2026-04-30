from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from openai import OpenAI

from .evaluator import EvaluationJudgeConfig
from .task_curation import is_infra_failure_error


_FILE_BLOCK_HEADER_PATTERN = re.compile(
    r"""(?mx)
    ^```[a-zA-Z0-9_-]*[ \t]+(?:\#\s*)?((?:tasks|scripts|skills)/[^\n`]+?)\s*\n
    |
    ^```[a-zA-Z0-9_-]*\s*\n\s*(?:\#\s*)?((?:tasks|scripts|skills)/[^\n`]+?)\s*\n
    """
)
_TASK_YAML_PATTERN = re.compile(r"tasks/(data_\d+)\.ya?ml")
_WORKPLACE_OUTPUT_NAMES = ("workplace_score.json", "verify_result.json", "state.json")
_SCORE_TAG_PATTERN = re.compile(r"<score>\s*([0-9]+(?:\.[0-9]+)?)\s*</score>", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class TurnVerifier:
    turn: int
    workplace_script: str | None
    trace_prompt: str | None


@dataclass(frozen=True, slots=True)
class WorkplaceTraceVerifier:
    source_task_id: str
    imported_task_id: str
    source_path: Path
    source_line: int
    workplace_script: str | None
    trace_prompt: str | None
    turn_verifiers: tuple[TurnVerifier, ...] = ()


@dataclass(frozen=True, slots=True)
class VerifierBundle:
    verifiers: dict[str, WorkplaceTraceVerifier]
    manifest_imported_task_ids: set[str]
    manifest_task_count: int
    jsonl_record_count: int
    mapped_record_count: int

    @property
    def missing_imported_task_ids(self) -> set[str]:
        return set(self.manifest_imported_task_ids) - set(self.verifiers)


@dataclass(frozen=True, slots=True)
class WorkplaceTraceEvaluationResult:
    task_id: str
    source_task_id: str | None
    run_id: str
    run_dir: Path
    summary_path: Path
    run_status: str | None
    run_result_type: str | None
    model: str | None
    verifier_source_path: Path | None
    verifier_source_line: int | None
    workplace_available: bool
    trace_available: bool
    workplace_status: str
    workplace_score: float | None
    workplace_score_source: str | None
    workplace_data: dict[str, Any] | None
    workplace_exit_code: int | None
    workplace_stdout: str
    workplace_stderr: str
    workplace_error: str | None
    trace_status: str
    trace_score: float | None
    trace_model: str | None
    trace_attempts: int
    trace_stdout: str
    trace_error: str | None
    trace_reasoning: str | None
    objective_score: float | None
    objective_score_source: str | None
    evaluation_status: str
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_task_id": self.source_task_id,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "summary_path": str(self.summary_path),
            "run_status": self.run_status,
            "run_result_type": self.run_result_type,
            "model": self.model,
            "verifier_source_path": (
                str(self.verifier_source_path) if self.verifier_source_path is not None else None
            ),
            "verifier_source_line": self.verifier_source_line,
            "workplace_available": self.workplace_available,
            "trace_available": self.trace_available,
            "workplace_status": self.workplace_status,
            "workplace_score": self.workplace_score,
            "workplace_score_source": self.workplace_score_source,
            "workplace_data": self.workplace_data,
            "workplace_exit_code": self.workplace_exit_code,
            "workplace_stdout": self.workplace_stdout,
            "workplace_stderr": self.workplace_stderr,
            "workplace_error": self.workplace_error,
            "trace_status": self.trace_status,
            "trace_score": self.trace_score,
            "trace_model": self.trace_model,
            "trace_attempts": self.trace_attempts,
            "trace_stdout": self.trace_stdout,
            "trace_error": self.trace_error,
            "trace_reasoning": self.trace_reasoning,
            "objective_score": self.objective_score,
            "objective_score_source": self.objective_score_source,
            "evaluation_status": self.evaluation_status,
            "error": self.error,
        }

    def summary_row(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "source_task_id": self.source_task_id or "",
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "run_status": self.run_status or "",
            "run_result_type": self.run_result_type or "",
            "model": self.model or "",
            "evaluation_status": self.evaluation_status,
            "workplace_status": self.workplace_status,
            "workplace_score": "" if self.workplace_score is None else f"{self.workplace_score:.2f}",
            "workplace_score_source": self.workplace_score_source or "",
            "workplace_exit_code": "" if self.workplace_exit_code is None else str(self.workplace_exit_code),
            "workplace_error": self.workplace_error or "",
            "trace_status": self.trace_status,
            "trace_score": "" if self.trace_score is None else f"{self.trace_score:.2f}",
            "trace_model": self.trace_model or "",
            "trace_attempts": str(self.trace_attempts),
            "trace_error": self.trace_error or "",
            "objective_score": "" if self.objective_score is None else f"{self.objective_score:.2f}",
            "objective_score_source": self.objective_score_source or "",
            "error": self.error or "",
        }


@dataclass(frozen=True, slots=True)
class WorkplaceTraceEvaluationSummary:
    total_runs: int
    completed_runs: int
    skipped_incomplete_runs: int
    skipped_infra_failure_runs: int
    evaluated_runs: int
    scored_runs: int
    perfect_score_runs: int
    perfect_score_rate: float
    evaluation_issue_runs: int
    run_success_rate: float
    workplace_scored_runs: int
    trace_scored_runs: int
    average_workplace_score: float | None
    average_trace_score: float | None
    average_objective_score: float | None
    benchmark_score: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "completed_runs": self.completed_runs,
            "skipped_incomplete_runs": self.skipped_incomplete_runs,
            "skipped_infra_failure_runs": self.skipped_infra_failure_runs,
            "evaluated_runs": self.evaluated_runs,
            "scored_runs": self.scored_runs,
            "perfect_score_runs": self.perfect_score_runs,
            "perfect_score_rate": self.perfect_score_rate,
            "evaluation_issue_runs": self.evaluation_issue_runs,
            "run_success_rate": self.run_success_rate,
            "workplace_scored_runs": self.workplace_scored_runs,
            "trace_scored_runs": self.trace_scored_runs,
            "average_workplace_score": self.average_workplace_score,
            "average_trace_score": self.average_trace_score,
            "average_objective_score": self.average_objective_score,
            "benchmark_score": self.benchmark_score,
        }


@dataclass(frozen=True, slots=True)
class _WorkplaceExecution:
    exit_code: int | None
    stdout: str
    stderr: str
    data: dict[str, Any] | None
    error: str | None


def load_verifier_bundle(
    jsonl_paths: list[Path],
    *,
    manifest_path: Path,
) -> VerifierBundle:
    source_to_imported = _load_source_to_imported_manifest(manifest_path)
    verifiers: dict[str, WorkplaceTraceVerifier] = {}
    jsonl_record_count = 0
    mapped_record_count = 0

    for jsonl_path in jsonl_paths:
        resolved_jsonl_path = jsonl_path.expanduser().resolve()
        with resolved_jsonl_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                jsonl_record_count += 1
                payload = json.loads(line)
                raw_output = _extract_raw_output(payload)
                if raw_output is None:
                    continue
                blocks = extract_file_blocks(raw_output)
                source_task_id = _find_source_task_id(blocks) or _extract_payload_task_id(payload)
                if source_task_id is None:
                    continue
                imported_task_id = source_to_imported.get(source_task_id)
                if imported_task_id is None:
                    continue
                mapped_record_count += 1
                verifiers[imported_task_id] = WorkplaceTraceVerifier(
                    source_task_id=source_task_id,
                    imported_task_id=imported_task_id,
                    source_path=resolved_jsonl_path,
                    source_line=line_number,
                    workplace_script=_first_block(
                        blocks,
                        [
                            f"scripts/{source_task_id}/verify_workplace.py",
                            f"tasks/{source_task_id}/verify_workplace.py",
                            f"tasks/{source_task_id}/verify_rules.py",
                        ],
                    ),
                    trace_prompt=_first_block(
                        blocks,
                        [
                            f"scripts/{source_task_id}/verify_trace.md",
                            f"tasks/{source_task_id}/verify_trace.md",
                            f"tasks/{source_task_id}/verify_prompt.md",
                        ],
                    ),
                    turn_verifiers=_extract_turn_verifiers(blocks, source_task_id=source_task_id),
                )

    return VerifierBundle(
        verifiers=verifiers,
        manifest_imported_task_ids=set(source_to_imported.values()),
        manifest_task_count=len(source_to_imported),
        jsonl_record_count=jsonl_record_count,
        mapped_record_count=mapped_record_count,
    )


def extract_file_blocks(raw_output: str) -> dict[str, str]:
    matches = list(_FILE_BLOCK_HEADER_PATTERN.finditer(raw_output))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        raw_path = match.group(1) or match.group(2)
        if raw_path is None:
            continue
        relative_path = _clean_relative_path(raw_path)
        if relative_path is None:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_output)
        content = _strip_outer_fence(raw_output[start:end])
        blocks[relative_path] = content
    return blocks


def _first_block(blocks: dict[str, str], relative_paths: list[str]) -> str | None:
    for relative_path in relative_paths:
        value = blocks.get(relative_path)
        if value is not None:
            return value
    return None


def evaluate_workplace_trace_run(
    run_dir: Path,
    *,
    verifiers: dict[str, WorkplaceTraceVerifier],
    components: str,
    judge_config: EvaluationJudgeConfig,
    workplace_env: dict[str, str] | None = None,
    workplace_timeout: float | None = 180.0,
) -> WorkplaceTraceEvaluationResult:
    resolved_run_dir = run_dir.expanduser().resolve()
    summary_path = resolved_run_dir / "summary.json"
    if not summary_path.exists():
        return _result_template(
            task_id=resolved_run_dir.parent.name,
            run_id=resolved_run_dir.name,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            evaluation_status="error",
            error=f"Missing summary.json in {resolved_run_dir}",
            judge_config=judge_config,
        )

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    task_id = str(summary.get("task_id") or resolved_run_dir.parent.name)
    run_id = str(summary.get("run_id") or resolved_run_dir.name)
    run_status = summary.get("status")
    run_result_type = summary.get("result_type")
    model = summary.get("model")
    summary_error = _summary_error(summary)
    if isinstance(run_status, str) and run_status != "completed" and is_infra_failure_error(summary_error):
        return _result_template(
            task_id=task_id,
            run_id=run_id,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=run_status,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            model=str(model) if isinstance(model, str) else None,
            evaluation_status="skipped_infra_failure",
            error=f"Run failed due to infra error; skipped workplace/trace evaluation: {summary_error}",
            judge_config=judge_config,
        )

    verifier = verifiers.get(task_id)

    if verifier is None:
        return _result_template(
            task_id=task_id,
            run_id=run_id,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=str(run_status) if isinstance(run_status, str) else None,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            model=str(model) if isinstance(model, str) else None,
            evaluation_status="missing_new_verifier",
            error=f"Missing workplace/trace verifier for {task_id}",
            judge_config=judge_config,
        )

    workspace_after = resolved_run_dir / "workspace_after"
    if not workspace_after.exists():
        return _result_template(
            task_id=task_id,
            source_task_id=verifier.source_task_id,
            run_id=run_id,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=str(run_status) if isinstance(run_status, str) else None,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            model=str(model) if isinstance(model, str) else None,
            verifier=verifier,
            evaluation_status="missing_workspace_after",
            error=f"Missing workspace_after in {resolved_run_dir}",
            judge_config=judge_config,
        )

    turn_workspace_after_dirs = _load_turn_workspace_after_dirs(summary, run_dir=resolved_run_dir)
    workplace_status = "not_requested"
    workplace_score = None
    workplace_score_source = None
    workplace_data = None
    workplace_exit_code = None
    workplace_stdout = ""
    workplace_stderr = ""
    workplace_error = None
    if components in {"full", "workplace"}:
        if verifier.turn_verifiers:
            (
                workplace_score,
                workplace_score_source,
                workplace_data,
                workplace_exit_code,
                workplace_stdout,
                workplace_stderr,
                workplace_error,
            ) = _execute_turn_workplace_verifiers(
                verifier,
                workspace_after=workspace_after,
                turn_workspace_after_dirs=turn_workspace_after_dirs,
                imported_task_id=task_id,
                env_overrides=workplace_env or {},
                timeout=workplace_timeout,
            )
            workplace_status = (
                "evaluated"
                if workplace_error is None and workplace_score is not None
                else "workplace_error"
            )
        elif verifier.workplace_script is None:
            workplace_status = "missing_workplace_verifier"
            workplace_error = f"Missing verify_workplace.py for {task_id}"
        else:
            workplace_execution = _execute_workplace_script(
                script_text=verifier.workplace_script,
                workspace_after=workspace_after,
                imported_task_id=task_id,
                source_task_id=verifier.source_task_id,
                env_overrides=workplace_env or {},
                timeout=workplace_timeout,
            )
            workplace_data = workplace_execution.data
            workplace_exit_code = workplace_execution.exit_code
            workplace_stdout = workplace_execution.stdout
            workplace_stderr = workplace_execution.stderr
            workplace_error = workplace_execution.error
            workplace_score, workplace_score_source = _derive_component_score(
                workplace_data,
                component_name="workplace",
            )
            workplace_status = (
                "evaluated"
                if workplace_error is None and workplace_score is not None
                else "workplace_error"
            )

    trace_status = "not_requested"
    trace_score = None
    trace_stdout = ""
    trace_attempts = 0
    trace_error = None
    trace_reasoning = None
    if components in {"full", "trace"}:
        if verifier.trace_prompt is None:
            trace_status = "missing_trace_verifier"
            trace_error = f"Missing verify_trace.md for {task_id}"
        else:
            trace_score, trace_stdout, trace_attempts, trace_error, trace_reasoning = _judge_trace(
                judge_config=judge_config,
                trace_prompt=verifier.trace_prompt,
                trace_path=resolved_run_dir / "trace.jsonl",
                summary_path=summary_path,
                final_answer_path=resolved_run_dir / "final_answer.md",
                task_id=task_id,
                source_task_id=verifier.source_task_id,
                workplace_data=workplace_data,
            )
            trace_status = "evaluated" if trace_error is None and trace_score is not None else "trace_judge_error"

    objective_score, objective_score_source = _combine_component_scores(
        components=components,
        workplace_score=workplace_score,
        trace_score=trace_score,
    )
    evaluation_status = "evaluated" if objective_score is not None else _derive_evaluation_status(
        workplace_status=workplace_status,
        trace_status=trace_status,
        components=components,
    )

    return WorkplaceTraceEvaluationResult(
        task_id=task_id,
        source_task_id=verifier.source_task_id,
        run_id=run_id,
        run_dir=resolved_run_dir,
        summary_path=summary_path,
        run_status=str(run_status) if isinstance(run_status, str) else None,
        run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
        model=str(model) if isinstance(model, str) else None,
        verifier_source_path=verifier.source_path,
        verifier_source_line=verifier.source_line,
        workplace_available=verifier.workplace_script is not None or any(
            item.workplace_script is not None for item in verifier.turn_verifiers
        ),
        trace_available=verifier.trace_prompt is not None or any(
            item.trace_prompt is not None for item in verifier.turn_verifiers
        ),
        workplace_status=workplace_status,
        workplace_score=workplace_score,
        workplace_score_source=workplace_score_source,
        workplace_data=workplace_data,
        workplace_exit_code=workplace_exit_code,
        workplace_stdout=workplace_stdout,
        workplace_stderr=workplace_stderr,
        workplace_error=workplace_error,
        trace_status=trace_status,
        trace_score=trace_score,
        trace_model=judge_config.model,
        trace_attempts=trace_attempts,
        trace_stdout=trace_stdout,
        trace_error=trace_error,
        trace_reasoning=trace_reasoning,
        objective_score=objective_score,
        objective_score_source=objective_score_source,
        evaluation_status=evaluation_status,
        error=_join_errors(workplace_error, trace_error) if objective_score is None else None,
    )


def summarize_workplace_trace_evaluations(
    results: list[WorkplaceTraceEvaluationResult],
) -> WorkplaceTraceEvaluationSummary:
    total_runs = len(results)
    completed_runs = sum(1 for result in results if result.run_status == "completed")
    skipped_incomplete_runs = sum(
        1 for result in results if result.evaluation_status == "skipped_run_not_completed"
    )
    skipped_infra_failure_runs = sum(
        1 for result in results if result.evaluation_status == "skipped_infra_failure"
    )
    evaluated_runs = sum(1 for result in results if result.evaluation_status == "evaluated")
    workplace_values = [
        result.workplace_score
        for result in results
        if result.workplace_score is not None
    ]
    trace_values = [
        result.trace_score
        for result in results
        if result.trace_score is not None
    ]
    objective_values = [
        result.objective_score
        for result in results
        if result.evaluation_status == "evaluated" and result.objective_score is not None
    ]
    scored_runs = len(objective_values)
    perfect_score_runs = sum(1 for score in objective_values if score == 100.0)
    evaluation_issue_runs = sum(
        1
        for result in results
        if result.evaluation_status
        not in {
            "evaluated",
            "skipped_run_not_completed",
            "skipped_infra_failure",
        }
    )
    run_success_rate = round((completed_runs / total_runs) * 100, 2) if total_runs else 0.0
    perfect_score_rate = round((perfect_score_runs / total_runs) * 100, 2) if total_runs else 0.0
    average_objective_score = (
        round(sum(objective_values) / scored_runs, 2) if scored_runs else None
    )
    benchmark_score = (
        round((run_success_rate / 100.0) * average_objective_score, 2)
        if average_objective_score is not None
        else None
    )
    return WorkplaceTraceEvaluationSummary(
        total_runs=total_runs,
        completed_runs=completed_runs,
        skipped_incomplete_runs=skipped_incomplete_runs,
        skipped_infra_failure_runs=skipped_infra_failure_runs,
        evaluated_runs=evaluated_runs,
        scored_runs=scored_runs,
        perfect_score_runs=perfect_score_runs,
        perfect_score_rate=perfect_score_rate,
        evaluation_issue_runs=evaluation_issue_runs,
        run_success_rate=run_success_rate,
        workplace_scored_runs=len(workplace_values),
        trace_scored_runs=len(trace_values),
        average_workplace_score=round(sum(workplace_values) / len(workplace_values), 2)
        if workplace_values
        else None,
        average_trace_score=round(sum(trace_values) / len(trace_values), 2)
        if trace_values
        else None,
        average_objective_score=average_objective_score,
        benchmark_score=benchmark_score,
    )


def write_workplace_trace_json(
    results: list[WorkplaceTraceEvaluationResult],
    *,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_workplace_trace_csv(
    results: list[WorkplaceTraceEvaluationResult],
    *,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "source_task_id",
        "run_id",
        "run_dir",
        "run_status",
        "run_result_type",
        "model",
        "evaluation_status",
        "workplace_status",
        "workplace_score",
        "workplace_score_source",
        "workplace_exit_code",
        "workplace_error",
        "trace_status",
        "trace_score",
        "trace_model",
        "trace_attempts",
        "trace_error",
        "objective_score",
        "objective_score_source",
        "error",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result.summary_row())


def write_workplace_trace_summary_json(
    summary: WorkplaceTraceEvaluationSummary,
    *,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_source_to_imported_manifest(manifest_path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with manifest_path.expanduser().resolve().open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            source_task_id = payload.get("source_task_id")
            imported_task_id = payload.get("imported_task_id")
            if not isinstance(source_task_id, str) or not isinstance(imported_task_id, str):
                raise ValueError(f"{manifest_path}:{line_number} is missing source/imported task ids")
            mapping[source_task_id] = imported_task_id
    return mapping


def _extract_raw_output(payload: dict[str, Any]) -> str | None:
    for key in ("raw_output", "enhanced_raw_output"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _summary_error(summary: dict[str, Any]) -> str | None:
    error = summary.get("error")
    return str(error) if isinstance(error, str) and error.strip() else None


def _load_turn_workspace_after_dirs(summary: dict[str, Any], *, run_dir: Path) -> dict[int, Path]:
    turns = summary.get("turns")
    if not isinstance(turns, list):
        return {}

    paths: dict[int, Path] = {}
    for item in turns:
        if not isinstance(item, dict):
            continue
        turn = _optional_positive_int(item.get("turn"))
        after_state_dir = item.get("after_state_dir")
        if turn is None or not isinstance(after_state_dir, str):
            continue
        relative = Path(after_state_dir.strip())
        if (
            not relative.parts
            or relative.is_absolute()
            or ".." in relative.parts
            or len(relative.parts) != 1
        ):
            continue
        paths[turn] = run_dir / relative
    return paths


def _optional_positive_int(value: Any) -> int | None:
    try:
        integer = int(value)
    except (TypeError, ValueError):
        return None
    return integer if integer > 0 else None


def _find_source_task_id(blocks: dict[str, str]) -> str | None:
    for relative_path in blocks:
        match = _TASK_YAML_PATTERN.fullmatch(relative_path)
        if match:
            return match.group(1)
    for relative_path in blocks:
        match = re.fullmatch(
            r"scripts/(data_\d+)/(?:verify_workplace\.py|verify_trace\.md|verify_turn_\d+\.py|verify_trace_turn_\d+\.md)",
            relative_path,
        )
        if match:
            return match.group(1)
    return None


def _extract_payload_task_id(payload: dict[str, Any]) -> str | None:
    task_id = payload.get("task_id")
    if isinstance(task_id, str) and re.fullmatch(r"data_\d+", task_id.strip()):
        return task_id.strip()
    return None


def _extract_turn_verifiers(blocks: dict[str, str], *, source_task_id: str) -> tuple[TurnVerifier, ...]:
    turns = sorted(
        {
            int(match.group(1))
            for relative_path in blocks
            if (
                match := re.fullmatch(
                    rf"scripts/{re.escape(source_task_id)}/verify_(?:trace_)?turn_(\d+)\.(?:py|md)",
                    relative_path,
                )
            )
        }
    )
    return tuple(
        TurnVerifier(
            turn=turn,
            workplace_script=blocks.get(f"scripts/{source_task_id}/verify_turn_{turn}.py"),
            trace_prompt=blocks.get(f"scripts/{source_task_id}/verify_trace_turn_{turn}.md"),
        )
        for turn in turns
    )


def _clean_relative_path(raw_path: str) -> str | None:
    cleaned = raw_path.strip().lstrip("#").strip().strip("`")
    for prefix in ("tasks/", "scripts/"):
        marker = cleaned.find(prefix)
        if marker >= 0:
            cleaned = cleaned[marker:]
            break
    else:
        return None
    if not cleaned.startswith(("tasks/", "scripts/")):
        return None
    if ".." in Path(cleaned).parts:
        return None
    return cleaned


def _strip_outer_fence(content: str) -> str:
    stripped = content.strip()
    while stripped.startswith("```"):
        lines = stripped.splitlines()
        if not lines:
            break
        first_line = lines[0].strip()
        if first_line == "```" or re.fullmatch(r"```[a-zA-Z0-9_-]+", first_line):
            stripped = "\n".join(lines[1:]).lstrip()
            continue
        break
    while stripped.endswith("```"):
        stripped = stripped[:-3].rstrip()
    return stripped + "\n"


def _execute_turn_workplace_verifiers(
    verifier: WorkplaceTraceVerifier,
    *,
    workspace_after: Path,
    turn_workspace_after_dirs: dict[int, Path],
    imported_task_id: str,
    env_overrides: dict[str, str],
    timeout: float | None,
) -> tuple[float | None, str | None, dict[str, Any] | None, int | None, str, str, str | None]:
    turn_results: list[dict[str, Any]] = []
    scores: list[float] = []
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    exit_codes: list[int] = []
    errors: list[str] = []

    for turn_verifier in verifier.turn_verifiers:
        if turn_verifier.workplace_script is None:
            errors.append(f"Missing verify_turn_{turn_verifier.turn}.py for {imported_task_id}")
            turn_results.append(
                {
                    "turn": turn_verifier.turn,
                    "score": None,
                    "score_source": None,
                    "error": errors[-1],
                }
            )
            continue

        turn_workspace_after = _select_turn_workspace_after(
            turn_verifier.turn,
            workspace_after=workspace_after,
            turn_workspace_after_dirs=turn_workspace_after_dirs,
        )
        if not turn_workspace_after.exists():
            errors.append(
                f"turn {turn_verifier.turn}: missing workspace snapshot {turn_workspace_after}"
            )
            turn_results.append(
                {
                    "turn": turn_verifier.turn,
                    "workspace_after_dir": turn_workspace_after.name,
                    "score": None,
                    "score_source": None,
                    "error": errors[-1],
                }
            )
            continue

        execution = _execute_workplace_script(
            script_text=turn_verifier.workplace_script,
            workspace_after=turn_workspace_after,
            imported_task_id=imported_task_id,
            source_task_id=verifier.source_task_id,
            env_overrides=env_overrides,
            timeout=timeout,
        )
        if execution.exit_code is not None:
            exit_codes.append(execution.exit_code)
        if execution.stdout:
            stdout_parts.append(f"--- turn {turn_verifier.turn} stdout ---\n{execution.stdout}")
        if execution.stderr:
            stderr_parts.append(f"--- turn {turn_verifier.turn} stderr ---\n{execution.stderr}")
        score, score_source = _derive_component_score(execution.data, component_name="workplace")
        if execution.error:
            errors.append(f"turn {turn_verifier.turn}: {execution.error}")
        if score is not None:
            scores.append(score)
        turn_results.append(
            {
                "turn": turn_verifier.turn,
                "workspace_after_dir": turn_workspace_after.name,
                "score": score,
                "score_source": score_source,
                "data": execution.data,
                "exit_code": execution.exit_code,
                "error": execution.error,
            }
        )

    if len(scores) != len(verifier.turn_verifiers):
        average_score = None
        score_source = None
    else:
        average_score = round(sum(scores) / len(scores), 2) if scores else None
        score_source = "multi_turn_workplace_average" if scores else None

    data = {
        "total_score": average_score,
        "score_source": score_source,
        "turns": turn_results,
    }
    exit_code = max(exit_codes) if exit_codes else None
    error = "; ".join(errors) if errors else None
    return (
        average_score,
        score_source,
        data,
        exit_code,
        "\n".join(stdout_parts),
        "\n".join(stderr_parts),
        error,
    )


def _select_turn_workspace_after(
    turn: int,
    *,
    workspace_after: Path,
    turn_workspace_after_dirs: dict[int, Path],
) -> Path:
    configured = turn_workspace_after_dirs.get(turn)
    if configured is not None:
        return configured
    conventional = workspace_after.parent / f"workspace_after_turn_{turn}"
    if conventional.exists():
        return conventional
    return workspace_after


def _execute_workplace_script(
    *,
    script_text: str,
    workspace_after: Path,
    imported_task_id: str,
    source_task_id: str,
    env_overrides: dict[str, str],
    timeout: float | None,
) -> _WorkplaceExecution:
    with tempfile.TemporaryDirectory(prefix=f"workplace_eval_{imported_task_id}_") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        workspace_dir = temp_dir / "workspace"
        shutil.copytree(workspace_after, workspace_dir)
        for alias in {source_task_id, imported_task_id}:
            asset_alias_dir = workspace_dir / "assets" / alias
            asset_alias_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(workspace_after, asset_alias_dir, dirs_exist_ok=True)
            (workspace_dir / "tasks" / alias).mkdir(parents=True, exist_ok=True)
            (workspace_dir / "scripts" / alias).mkdir(parents=True, exist_ok=True)

        patched_text = _replace_task_id_references(
            script_text,
            source_task_id=source_task_id,
            imported_task_id=imported_task_id,
        )
        patched_text = patched_text.replace("/workspace", str(workspace_dir))
        script_path = workspace_dir / "scripts" / imported_task_id / "verify_workplace.py"
        script_path.write_text(patched_text, encoding="utf-8")
        env = os.environ.copy()
        env.update(env_overrides)

        try:
            process = subprocess.run(
                [sys.executable, str(script_path), str(workspace_dir)],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return _WorkplaceExecution(
                exit_code=None,
                stdout=exc.stdout if isinstance(exc.stdout, str) else "",
                stderr=exc.stderr if isinstance(exc.stderr, str) else "",
                data=None,
                error=f"verify_workplace.py timed out after {timeout} seconds",
            )

        output_path = _find_workplace_output(temp_dir=temp_dir, task_id=imported_task_id)
        if output_path is not None:
            try:
                data = json.loads(output_path.read_text(encoding="utf-8"))
            except Exception as exc:
                return _WorkplaceExecution(
                    process.returncode,
                    process.stdout,
                    process.stderr,
                    None,
                    f"Failed to parse {output_path.name}: {exc}",
                )
            return _WorkplaceExecution(process.returncode, process.stdout, process.stderr, data, None)

        stdout_json = _parse_json_from_text(process.stdout)
        if stdout_json is not None:
            return _WorkplaceExecution(process.returncode, process.stdout, process.stderr, stdout_json, None)

        fallback = _execute_workplace_callable_fallback(
            script_path=script_path,
            workspace_dir=workspace_dir,
            temp_dir=temp_dir,
            task_id=imported_task_id,
            env=env,
            timeout=timeout,
        )
        if fallback.data is not None:
            return fallback

        if process.returncode != 0:
            tail = process.stderr.strip().splitlines()[-1] if process.stderr.strip() else process.stdout.strip()
            error = tail or f"verify_workplace.py exited with {process.returncode}"
        else:
            error = "verify_workplace.py completed without emitting workplace_score/verify_result/state output"
        return _WorkplaceExecution(process.returncode, process.stdout, process.stderr, None, error)


def _execute_workplace_callable_fallback(
    *,
    script_path: Path,
    workspace_dir: Path,
    temp_dir: Path,
    task_id: str,
    env: dict[str, str],
    timeout: float | None,
) -> _WorkplaceExecution:
    wrapper = f"""
import importlib.util
import json
import os
import sys
from pathlib import Path

script_path = Path({str(script_path)!r})
workspace_dir = Path({str(workspace_dir)!r})
os.chdir(workspace_dir)
sys.argv = [str(script_path), str(workspace_dir)]

spec = importlib.util.spec_from_file_location("verify_workplace_module", script_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

func = getattr(module, "verify", None) or getattr(module, "main", None)
if callable(func):
    result = func()
    if isinstance(result, dict):
        Path("workplace_score.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
"""
    try:
        process = subprocess.run(
            [sys.executable, "-c", wrapper],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return _WorkplaceExecution(
            None,
            exc.stdout if isinstance(exc.stdout, str) else "",
            exc.stderr if isinstance(exc.stderr, str) else "",
            None,
            f"verify_workplace.py callable fallback timed out after {timeout} seconds",
        )
    output_path = _find_workplace_output(temp_dir=temp_dir, task_id=task_id)
    if output_path is None:
        return _WorkplaceExecution(process.returncode, process.stdout, process.stderr, None, None)
    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _WorkplaceExecution(
            process.returncode,
            process.stdout,
            process.stderr,
            None,
            f"Failed to parse {output_path.name}: {exc}",
        )
    return _WorkplaceExecution(process.returncode, process.stdout, process.stderr, data, None)


def _find_workplace_output(*, temp_dir: Path, task_id: str) -> Path | None:
    candidates = [
        temp_dir / name for name in _WORKPLACE_OUTPUT_NAMES
    ] + [
        temp_dir / "workspace" / name for name in _WORKPLACE_OUTPUT_NAMES
    ]
    for alias in {task_id}:
        candidates.extend(
            temp_dir / "workspace" / root / alias / name
            for root in ("assets", "tasks", "scripts")
            for name in _WORKPLACE_OUTPUT_NAMES
        )
    for path in candidates:
        if path.exists():
            return path
    for name in _WORKPLACE_OUTPUT_NAMES:
        matches = sorted(temp_dir.rglob(name))
        if matches:
            return matches[0]
    return None


def _derive_component_score(
    data: dict[str, Any] | None,
    *,
    component_name: str,
) -> tuple[float | None, str | None]:
    if not isinstance(data, dict):
        return None, None

    for key in ("total_score", "score"):
        value = data.get(key)
        if isinstance(value, (int, float)):
            return _normalize_score(float(value)), f"{component_name}_{key}"

    detail_score = _score_from_details(data.get("details"))
    if detail_score is not None:
        return detail_score, f"{component_name}_details"
    detail_score = _score_from_details(data.get("score_details"))
    if detail_score is not None:
        return detail_score, f"{component_name}_score_details"

    bool_values = [
        value
        for key, value in data.items()
        if isinstance(value, bool)
        and key not in {"success", "passed"}
    ]
    if bool_values:
        true_count = sum(1 for value in bool_values if value)
        return round((true_count / len(bool_values)) * 100, 2), f"{component_name}_boolean_ratio"

    for key in ("success", "passed"):
        value = data.get(key)
        if isinstance(value, bool):
            return (100.0 if value else 0.0), f"{component_name}_{key}"
    return None, None


def _score_from_details(value: Any) -> float | None:
    if not isinstance(value, list):
        return None
    score_total = 0.0
    max_total = 0.0
    saw_score = False
    for item in value:
        if not isinstance(item, dict):
            continue
        score = item.get("score")
        max_score = item.get("max_score")
        if isinstance(score, (int, float)):
            saw_score = True
            score_total += float(score)
        if isinstance(max_score, (int, float)):
            max_total += float(max_score)
    if max_total > 0:
        return _normalize_score((score_total / max_total) * 100.0)
    if saw_score:
        return _normalize_score(score_total)
    return None


def _normalize_score(raw_score: float) -> float:
    if 0.0 <= raw_score <= 1.0:
        raw_score *= 100.0
    return round(max(0.0, min(100.0, raw_score)), 2)


def _replace_task_id_references(
    text: str,
    *,
    source_task_id: str,
    imported_task_id: str,
) -> str:
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(source_task_id)}(?![A-Za-z0-9_])"
    )
    return pattern.sub(imported_task_id, text)


def _judge_trace(
    *,
    judge_config: EvaluationJudgeConfig,
    trace_prompt: str,
    trace_path: Path,
    summary_path: Path,
    final_answer_path: Path,
    task_id: str,
    source_task_id: str,
    workplace_data: dict[str, Any] | None,
) -> tuple[float | None, str, int, str | None, str | None]:
    if not judge_config.enabled:
        return None, "", 0, "Judge disabled.", None
    if not judge_config.model:
        return None, "", 0, "Judge model is not configured.", None
    if not judge_config.api_key:
        return None, "", 0, "Judge API key is not configured.", None

    client = OpenAI(api_key=judge_config.api_key, base_url=judge_config.base_url)
    prompt = _build_trace_judge_prompt(
        task_id=task_id,
        source_task_id=source_task_id,
        trace_prompt=trace_prompt,
        trace_text=trace_path.read_text(encoding="utf-8") if trace_path.exists() else "",
        summary_text=summary_path.read_text(encoding="utf-8") if summary_path.exists() else "",
        final_answer_text=final_answer_path.read_text(encoding="utf-8") if final_answer_path.exists() else "",
        workplace_data=workplace_data,
    )
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are a strict trace-domain evaluator. Evaluate only the agent execution trace, "
                "not final workspace correctness. Return only JSON with keys `score` "
                "(number 0-100) and `reasoning` (string)."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    last_text = ""
    last_error: str | None = None
    for attempt in range(1, judge_config.max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=judge_config.model,
                messages=messages,
                temperature=judge_config.temperature,
            )
        except Exception as exc:
            last_error = str(exc)
            if attempt >= judge_config.max_attempts:
                return None, last_text, attempt, last_error, None
            messages.append({"role": "assistant", "content": f'{{"error": "{str(exc)}"}}'})
            messages.append(
                {
                    "role": "user",
                    "content": "The previous attempt failed. Return only valid JSON with `score` and `reasoning`.",
                }
            )
            continue

        last_text = response.choices[0].message.content or ""
        parsed = _parse_judge_score(last_text)
        if parsed is not None:
            return parsed[0], last_text, attempt, None, parsed[1]
        last_error = "Judge output was not valid JSON or <score> markup with a numeric score."
        if attempt >= judge_config.max_attempts:
            return None, last_text, attempt, last_error, None
        messages.append({"role": "assistant", "content": last_text})
        messages.append(
            {
                "role": "user",
                "content": "Your previous response could not be parsed. Return only JSON like {\"score\": 85, \"reasoning\": \"...\"}.",
            }
        )
    return None, last_text, judge_config.max_attempts, last_error, None


def _build_trace_judge_prompt(
    *,
    task_id: str,
    source_task_id: str,
    trace_prompt: str,
    trace_text: str,
    summary_text: str,
    final_answer_text: str,
    workplace_data: dict[str, Any] | None,
) -> str:
    workplace_json = json.dumps(workplace_data or {}, ensure_ascii=False, indent=2)
    return (
        f"Imported Task ID: {task_id}\n"
        f"Source Task ID: {source_task_id}\n\n"
        "Use the task-specific trace rubric below as the evaluation policy. "
        "Do not score final workspace correctness; that belongs to workplace verification. "
        "Ignore any output-format instructions inside the rubric and return only the required JSON.\n\n"
        f"## Trace Rubric\n{trace_prompt}\n\n"
        f"## Workplace Verification Data For Context Only\n{workplace_json}\n\n"
        f"## Run Summary\n{summary_text}\n\n"
        f"## Final Answer\n{final_answer_text}\n\n"
        f"## Full Trace\n{trace_text}\n"
    )


def _parse_judge_score(content: str) -> tuple[float, str | None] | None:
    payload = _parse_json_from_text(content)
    if payload is not None:
        score = payload.get("score")
        reasoning = payload.get("reasoning")
        if isinstance(score, (int, float)):
            return _normalize_score(float(score)), reasoning if isinstance(reasoning, str) else None
    match = _SCORE_TAG_PATTERN.search(content)
    if match:
        return _normalize_score(float(match.group(1))), content.strip()
    return None


def _parse_json_from_text(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        return payload
    for line in reversed(stripped.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        try:
            payload = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
        if isinstance(payload, dict):
            return payload
    return None


def _combine_component_scores(
    *,
    components: str,
    workplace_score: float | None,
    trace_score: float | None,
) -> tuple[float | None, str | None]:
    if components == "workplace":
        return (workplace_score, "workplace") if workplace_score is not None else (None, None)
    if components == "trace":
        return (trace_score, "trace") if trace_score is not None else (None, None)
    if workplace_score is None or trace_score is None:
        return None, None
    return round((workplace_score + trace_score) / 2.0, 2), "workplace_trace_average"


def _derive_evaluation_status(
    *,
    workplace_status: str,
    trace_status: str,
    components: str,
) -> str:
    if components == "workplace":
        return workplace_status
    if components == "trace":
        return trace_status
    if workplace_status != "evaluated":
        return workplace_status
    if trace_status != "evaluated":
        return trace_status
    return "missing_objective_score"


def _result_template(
    *,
    task_id: str,
    run_id: str,
    run_dir: Path,
    summary_path: Path,
    judge_config: EvaluationJudgeConfig,
    source_task_id: str | None = None,
    run_status: str | None = None,
    run_result_type: str | None = None,
    model: str | None = None,
    verifier: WorkplaceTraceVerifier | None = None,
    evaluation_status: str,
    error: str | None,
) -> WorkplaceTraceEvaluationResult:
    return WorkplaceTraceEvaluationResult(
        task_id=task_id,
        source_task_id=source_task_id,
        run_id=run_id,
        run_dir=run_dir,
        summary_path=summary_path,
        run_status=run_status,
        run_result_type=run_result_type,
        model=model,
        verifier_source_path=verifier.source_path if verifier is not None else None,
        verifier_source_line=verifier.source_line if verifier is not None else None,
        workplace_available=bool(verifier and verifier.workplace_script is not None),
        trace_available=bool(verifier and verifier.trace_prompt is not None),
        workplace_status="not_evaluated",
        workplace_score=None,
        workplace_score_source=None,
        workplace_data=None,
        workplace_exit_code=None,
        workplace_stdout="",
        workplace_stderr="",
        workplace_error=None,
        trace_status="not_evaluated",
        trace_score=None,
        trace_model=judge_config.model,
        trace_attempts=0,
        trace_stdout="",
        trace_error=None,
        trace_reasoning=None,
        objective_score=None,
        objective_score_source=None,
        evaluation_status=evaluation_status,
        error=error,
    )


def _join_errors(*errors: str | None) -> str | None:
    parts = [error for error in errors if error]
    return "; ".join(parts) if parts else None
