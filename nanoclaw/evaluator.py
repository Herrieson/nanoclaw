from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


_VERIFY_OUTPUT_NAMES = ("verify_result.json", "state.json")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    task_id: str
    run_id: str
    run_dir: Path
    summary_path: Path
    run_status: str | None
    run_result_type: str | None
    verify_script_path: Path | None
    verify_prompt_path: Path | None
    verify_output_path: Path | None
    verify_data: dict[str, Any] | None
    verify_exit_code: int | None
    verify_stdout: str
    verify_stderr: str
    objective_score: float | None
    objective_score_source: str | None
    evaluation_status: str
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "summary_path": str(self.summary_path),
            "run_status": self.run_status,
            "run_result_type": self.run_result_type,
            "verify_script_path": (
                str(self.verify_script_path) if self.verify_script_path is not None else None
            ),
            "verify_prompt_path": (
                str(self.verify_prompt_path) if self.verify_prompt_path is not None else None
            ),
            "verify_output_path": (
                str(self.verify_output_path) if self.verify_output_path is not None else None
            ),
            "verify_data": self.verify_data,
            "verify_exit_code": self.verify_exit_code,
            "verify_stdout": self.verify_stdout,
            "verify_stderr": self.verify_stderr,
            "objective_score": self.objective_score,
            "objective_score_source": self.objective_score_source,
            "evaluation_status": self.evaluation_status,
            "error": self.error,
        }

    def summary_row(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "run_status": self.run_status or "",
            "run_result_type": self.run_result_type or "",
            "evaluation_status": self.evaluation_status,
            "objective_score": "" if self.objective_score is None else f"{self.objective_score:.2f}",
            "objective_score_source": self.objective_score_source or "",
            "verify_exit_code": "" if self.verify_exit_code is None else str(self.verify_exit_code),
            "verify_output_path": "" if self.verify_output_path is None else str(self.verify_output_path),
            "error": self.error or "",
        }


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    total_runs: int
    completed_runs: int
    skipped_incomplete_runs: int
    evaluated_runs: int
    scored_runs: int
    perfect_score_runs: int
    perfect_score_rate: float
    evaluation_issue_runs: int
    run_success_rate: float
    average_objective_score: float | None
    benchmark_score: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "completed_runs": self.completed_runs,
            "skipped_incomplete_runs": self.skipped_incomplete_runs,
            "evaluated_runs": self.evaluated_runs,
            "scored_runs": self.scored_runs,
            "perfect_score_runs": self.perfect_score_runs,
            "perfect_score_rate": self.perfect_score_rate,
            "evaluation_issue_runs": self.evaluation_issue_runs,
            "run_success_rate": self.run_success_rate,
            "average_objective_score": self.average_objective_score,
            "benchmark_score": self.benchmark_score,
        }


def discover_run_dirs(patterns: list[str], *, repo_root: Path) -> list[Path]:
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
            if resolved_path in seen or not resolved_path.is_dir():
                continue
            if not (resolved_path / "summary.json").exists():
                continue
            seen.add(resolved_path)
            resolved.append(resolved_path)
    return resolved


def evaluate_run(run_dir: Path, *, repo_root: Path) -> EvaluationResult:
    resolved_run_dir = run_dir.expanduser().resolve()
    summary_path = resolved_run_dir / "summary.json"
    if not summary_path.exists():
        return EvaluationResult(
            task_id=resolved_run_dir.parent.name,
            run_id=resolved_run_dir.name,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=None,
            run_result_type=None,
            verify_script_path=None,
            verify_prompt_path=None,
            verify_output_path=None,
            verify_data=None,
            verify_exit_code=None,
            verify_stdout="",
            verify_stderr="",
            objective_score=None,
            objective_score_source=None,
            evaluation_status="error",
            error=f"Missing summary.json in {resolved_run_dir}",
        )

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    task_id = str(summary.get("task_id") or resolved_run_dir.parent.name)
    run_status = summary.get("status")
    run_result_type = summary.get("result_type")
    verify_script_path = (repo_root / "tasks" / task_id / "verify_rules.py").resolve()
    verify_prompt_path = (repo_root / "tasks" / task_id / "verify_prompt.md").resolve()
    if isinstance(run_status, str) and run_status != "completed":
        return EvaluationResult(
            task_id=task_id,
            run_id=resolved_run_dir.name,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=run_status,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            verify_script_path=verify_script_path if verify_script_path.exists() else None,
            verify_prompt_path=verify_prompt_path if verify_prompt_path.exists() else None,
            verify_output_path=None,
            verify_data=None,
            verify_exit_code=None,
            verify_stdout="",
            verify_stderr="",
            objective_score=None,
            objective_score_source=None,
            evaluation_status="skipped_run_not_completed",
            error=f"Run status is {run_status}; skipped objective evaluation.",
        )
    if not verify_script_path.exists():
        return EvaluationResult(
            task_id=task_id,
            run_id=resolved_run_dir.name,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=str(run_status) if isinstance(run_status, str) else None,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            verify_script_path=None,
            verify_prompt_path=verify_prompt_path if verify_prompt_path.exists() else None,
            verify_output_path=None,
            verify_data=None,
            verify_exit_code=None,
            verify_stdout="",
            verify_stderr="",
            objective_score=None,
            objective_score_source=None,
            evaluation_status="missing_verify_script",
            error=f"Missing verify_rules.py for {task_id}",
        )

    workspace_after = resolved_run_dir / "workspace_after"
    if not workspace_after.exists():
        return EvaluationResult(
            task_id=task_id,
            run_id=resolved_run_dir.name,
            run_dir=resolved_run_dir,
            summary_path=summary_path,
            run_status=str(run_status) if isinstance(run_status, str) else None,
            run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
            verify_script_path=verify_script_path,
            verify_prompt_path=verify_prompt_path if verify_prompt_path.exists() else None,
            verify_output_path=None,
            verify_data=None,
            verify_exit_code=None,
            verify_stdout="",
            verify_stderr="",
            objective_score=None,
            objective_score_source=None,
            evaluation_status="missing_workspace_after",
            error=f"Missing workspace_after in {resolved_run_dir}",
        )

    process, verify_output_path, verify_data, error = _execute_verify_script(
        verify_script_path=verify_script_path,
        workspace_after=workspace_after,
        task_id=task_id,
    )
    objective_score, score_source = _derive_objective_score(verify_data)
    status = "evaluated"
    if error:
        status = "verify_error"
    elif verify_data is None:
        status = "missing_verify_output"

    return EvaluationResult(
        task_id=task_id,
        run_id=resolved_run_dir.name,
        run_dir=resolved_run_dir,
        summary_path=summary_path,
        run_status=str(run_status) if isinstance(run_status, str) else None,
        run_result_type=str(run_result_type) if isinstance(run_result_type, str) else None,
        verify_script_path=verify_script_path,
        verify_prompt_path=verify_prompt_path if verify_prompt_path.exists() else None,
        verify_output_path=verify_output_path,
        verify_data=verify_data,
        verify_exit_code=process.returncode if process is not None else None,
        verify_stdout=process.stdout if process is not None else "",
        verify_stderr=process.stderr if process is not None else "",
        objective_score=objective_score,
        objective_score_source=score_source,
        evaluation_status=status,
        error=error,
    )


def write_evaluation_json(results: list[EvaluationResult], *, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [result.to_dict() for result in results]
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_evaluation_csv(results: list[EvaluationResult], *, output_path: Path) -> None:
    import csv

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "run_id",
        "run_dir",
        "run_status",
        "run_result_type",
        "evaluation_status",
        "objective_score",
        "objective_score_source",
        "verify_exit_code",
        "verify_output_path",
        "error",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result.summary_row())


def summarize_evaluations(results: list[EvaluationResult]) -> EvaluationSummary:
    total_runs = len(results)
    completed_runs = sum(1 for result in results if result.run_status == "completed")
    skipped_incomplete_runs = sum(
        1 for result in results if result.evaluation_status == "skipped_run_not_completed"
    )
    evaluated_runs = sum(1 for result in results if result.evaluation_status == "evaluated")
    scored_values = [
        result.objective_score
        for result in results
        if result.evaluation_status == "evaluated" and result.objective_score is not None
    ]
    scored_runs = len(scored_values)
    perfect_score_runs = sum(
        1
        for result in results
        if result.evaluation_status == "evaluated" and result.objective_score == 100.0
    )
    evaluation_issue_runs = sum(
        1
        for result in results
        if result.evaluation_status
        not in {
            "evaluated",
            "skipped_run_not_completed",
        }
    )
    run_success_rate = round((completed_runs / total_runs) * 100, 2) if total_runs else 0.0
    perfect_score_rate = round((perfect_score_runs / total_runs) * 100, 2) if total_runs else 0.0
    average_objective_score = (
        round(sum(scored_values) / scored_runs, 2) if scored_runs else None
    )
    benchmark_score = (
        round((run_success_rate / 100.0) * average_objective_score, 2)
        if average_objective_score is not None
        else None
    )
    return EvaluationSummary(
        total_runs=total_runs,
        completed_runs=completed_runs,
        skipped_incomplete_runs=skipped_incomplete_runs,
        evaluated_runs=evaluated_runs,
        scored_runs=scored_runs,
        perfect_score_runs=perfect_score_runs,
        perfect_score_rate=perfect_score_rate,
        evaluation_issue_runs=evaluation_issue_runs,
        run_success_rate=run_success_rate,
        average_objective_score=average_objective_score,
        benchmark_score=benchmark_score,
    )


def write_evaluation_summary_json(summary: EvaluationSummary, *, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _execute_verify_script(
    *,
    verify_script_path: Path,
    workspace_after: Path,
    task_id: str,
) -> tuple[subprocess.CompletedProcess[str] | None, Path | None, dict[str, Any] | None, str | None]:
    with tempfile.TemporaryDirectory(prefix=f"eval_{task_id}_") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        workspace_dir = temp_dir / "workspace"
        shutil.copytree(workspace_after, workspace_dir)
        legacy_assets_task_dir = workspace_dir / "assets" / task_id
        legacy_assets_task_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(workspace_after, legacy_assets_task_dir, dirs_exist_ok=True)
        legacy_tasks_task_dir = workspace_dir / "tasks" / task_id
        legacy_tasks_task_dir.mkdir(parents=True, exist_ok=True)

        original_text = verify_script_path.read_text(encoding="utf-8", errors="replace")
        patched_text = original_text.replace("/workspace", str(workspace_dir))
        patched_script_path = workspace_dir / "tasks" / task_id / "verify_rules.py"
        patched_script_path.parent.mkdir(parents=True, exist_ok=True)
        patched_script_path.write_text(patched_text, encoding="utf-8")

        process = subprocess.run(
            [sys.executable, str(patched_script_path), str(workspace_dir)],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
        )

        verify_output_path = _find_verify_output(temp_dir=temp_dir, task_id=task_id)
        verify_data = None
        if verify_output_path is not None:
            try:
                verify_data = json.loads(verify_output_path.read_text(encoding="utf-8"))
            except Exception as exc:
                return process, verify_output_path, None, f"Failed to parse {verify_output_path.name}: {exc}"
            return process, verify_output_path, verify_data, None

        stdout_json = _parse_stdout_json(process.stdout)
        if stdout_json is not None:
            return process, None, stdout_json, None

        fallback_process, fallback_output_path, fallback_data = _execute_verify_callable_fallback(
            patched_script_path=patched_script_path,
            workspace_dir=workspace_dir,
            task_id=task_id,
            temp_dir=temp_dir,
        )
        if fallback_output_path is not None and fallback_data is not None:
            return fallback_process, fallback_output_path, fallback_data, None

        error = None
        if process.returncode != 0:
            tail = process.stderr.strip().splitlines()[-1] if process.stderr.strip() else process.stdout.strip()
            error = tail or f"verify_rules.py exited with {process.returncode}"
        else:
            error = "verify_rules.py completed without emitting verify_result/state output"
        return process, None, None, error


def _find_verify_output(*, temp_dir: Path, task_id: str) -> Path | None:
    candidates = [
        temp_dir / name for name in _VERIFY_OUTPUT_NAMES
    ] + [
        temp_dir / "workspace" / name for name in _VERIFY_OUTPUT_NAMES
    ] + [
        temp_dir / "workspace" / "assets" / task_id / name for name in _VERIFY_OUTPUT_NAMES
    ] + [
        temp_dir / "workspace" / "tasks" / task_id / name for name in _VERIFY_OUTPUT_NAMES
    ]
    for path in candidates:
        if path.exists():
            return path

    fallback = sorted(temp_dir.rglob("verify_result.json")) + sorted(temp_dir.rglob("state.json"))
    return fallback[0] if fallback else None


def _execute_verify_callable_fallback(
    *,
    patched_script_path: Path,
    workspace_dir: Path,
    task_id: str,
    temp_dir: Path,
) -> tuple[subprocess.CompletedProcess[str], Path | None, dict[str, Any] | None]:
    wrapper = f"""
import importlib.util
import json
import os
import sys
from pathlib import Path

script_path = Path({str(patched_script_path)!r})
workspace_dir = Path({str(workspace_dir)!r})
os.chdir(workspace_dir)
sys.argv = [str(script_path), str(workspace_dir)]

spec = importlib.util.spec_from_file_location("verify_rules_module", script_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

func = getattr(module, "verify", None) or getattr(module, "main", None)
if callable(func):
    result = func()
    if isinstance(result, dict):
        Path("verify_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
"""
    process = subprocess.run(
        [sys.executable, "-c", wrapper],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
    )
    verify_output_path = _find_verify_output(temp_dir=temp_dir, task_id=task_id)
    if verify_output_path is None:
        return process, None, None
    try:
        verify_data = json.loads(verify_output_path.read_text(encoding="utf-8"))
    except Exception:
        return process, verify_output_path, None
    return process, verify_output_path, verify_data


def _parse_stdout_json(stdout: str) -> dict[str, Any] | None:
    text = stdout.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        return payload
    for line in reversed(text.splitlines()):
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _derive_objective_score(verify_data: dict[str, Any] | None) -> tuple[float | None, str | None]:
    if not isinstance(verify_data, dict):
        return None, None

    score = verify_data.get("score")
    if isinstance(score, (int, float)):
        bounded = max(0.0, min(100.0, float(score)))
        return bounded, "verify_score"

    bool_values = [
        value
        for key, value in verify_data.items()
        if isinstance(value, bool)
        and key not in {"success", "passed"}
    ]
    if bool_values:
        true_count = sum(1 for value in bool_values if value)
        ratio = true_count / len(bool_values)
        return round(ratio * 100, 2), "boolean_ratio"

    for key in ("success", "passed"):
        value = verify_data.get(key)
        if isinstance(value, bool):
            return (100.0 if value else 0.0), key

    status = verify_data.get("status")
    if isinstance(status, str):
        lowered = status.strip().lower()
        if lowered in {"success", "passed", "complete", "completed"}:
            return 100.0, "status"
        if lowered in {"partial"}:
            return 50.0, "status"
        if lowered in {"failed", "error"}:
            return 0.0, "status"

    return None, None
