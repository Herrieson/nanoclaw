from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


INFRA_FAILURE_HINTS = (
    "429",
    "access denied",
    "arrearage",
    "overdue-payment",
    "account is in good standing",
    "rate limit",
    "ratelimit",
    "too many requests",
    "online-endpoints",
    "http-status-codes",
    "temporarily unavailable",
)

VERIFIER_RUNTIME_ISSUE_STATUSES = frozenset(
    {
        "verify_error",
        "missing_verify_script",
        "missing_verify_output",
    }
)


@dataclass(frozen=True, slots=True)
class TaskAttempt:
    task_id: str
    model_name: str
    summary_path: Path
    run_status: str | None
    evaluation_status: str
    objective_score: float | None
    summary_error: str | None
    infra_failure: bool
    max_steps_failure: bool

    @property
    def solved(self) -> bool:
        return self.objective_score == 100.0

    @property
    def valid_attempt(self) -> bool:
        return not self.infra_failure

    @property
    def verifier_runtime_issue(self) -> bool:
        return self.evaluation_status in VERIFIER_RUNTIME_ISSUE_STATUSES


@dataclass(frozen=True, slots=True)
class TaskCurationRecord:
    task_id: str
    label: str
    reason: str
    mock_solved: bool
    real_models_total: int
    real_valid_attempts: int
    real_solved_count: int
    best_score: float | None
    avg_score: float | None
    max_step_fail_count: int
    infra_fail_count: int
    verifier_issue_count: int
    easy_pool_selected: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "label": self.label,
            "reason": self.reason,
            "mock_solved": self.mock_solved,
            "real_models_total": self.real_models_total,
            "real_valid_attempts": self.real_valid_attempts,
            "real_solved_count": self.real_solved_count,
            "best_score": self.best_score,
            "avg_score": self.avg_score,
            "max_step_fail_count": self.max_step_fail_count,
            "infra_fail_count": self.infra_fail_count,
            "verifier_issue_count": self.verifier_issue_count,
            "easy_pool_selected": self.easy_pool_selected,
        }


def discover_evaluation_paths(patterns: list[str], *, repo_root: Path) -> list[Path]:
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


def load_task_attempts(evaluation_paths: list[Path]) -> tuple[dict[str, list[TaskAttempt]], list[str]]:
    attempts_by_task: dict[str, list[TaskAttempt]] = {}
    model_names: set[str] = set()
    for evaluation_path in evaluation_paths:
        payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
        for item in payload:
            task_id = str(item["task_id"])
            summary_path = Path(item["summary_path"]).resolve()
            summary_payload = _read_summary_payload(summary_path)
            summary_model = summary_payload.get("model") if summary_payload is not None else None
            model_name = (
                str(summary_model).strip()
                if isinstance(summary_model, str) and str(summary_model).strip()
                else evaluation_path.parent.name
            )
            model_names.add(model_name)
            summary_error = _summary_error(summary_payload)
            infra_failure = _is_infra_failure(summary_error)
            max_steps_failure = _is_max_steps_failure(summary_error)
            objective_score = item.get("objective_score")
            if isinstance(objective_score, int):
                objective_score = float(objective_score)
            elif not isinstance(objective_score, float):
                objective_score = None
            attempt = TaskAttempt(
                task_id=task_id,
                model_name=model_name,
                summary_path=summary_path,
                run_status=item.get("run_status"),
                evaluation_status=str(item["evaluation_status"]),
                objective_score=objective_score,
                summary_error=summary_error,
                infra_failure=infra_failure,
                max_steps_failure=max_steps_failure,
            )
            attempts_by_task.setdefault(task_id, []).append(attempt)
    return attempts_by_task, sorted(model_names)


def curate_tasks(
    attempts_by_task: dict[str, list[TaskAttempt]],
    *,
    mock_models: set[str],
    min_real_models: int,
    keep_threshold: float,
    broken_threshold: float,
    easy_pool_keep_percent: int,
    sample_salt: str,
) -> list[TaskCurationRecord]:
    if not 0 <= easy_pool_keep_percent <= 100:
        raise ValueError("easy_pool_keep_percent must be between 0 and 100.")
    if broken_threshold > keep_threshold:
        raise ValueError("broken_threshold must be less than or equal to keep_threshold.")

    real_model_names = sorted(
        {
            attempt.model_name
            for attempts in attempts_by_task.values()
            for attempt in attempts
            if attempt.model_name not in mock_models
        }
    )
    records: list[TaskCurationRecord] = []
    for task_id in sorted(attempts_by_task):
        attempts = attempts_by_task[task_id]
        mock_attempts = [attempt for attempt in attempts if attempt.model_name in mock_models]
        real_attempts = [attempt for attempt in attempts if attempt.model_name not in mock_models]
        mock_valid_attempts = [attempt for attempt in mock_attempts if attempt.valid_attempt]
        real_valid_attempts = [attempt for attempt in real_attempts if attempt.valid_attempt]
        real_scores = [
            attempt.objective_score
            for attempt in real_valid_attempts
            if attempt.objective_score is not None
        ]
        mock_solved = any(attempt.solved for attempt in mock_valid_attempts)
        real_solved_count = sum(1 for attempt in real_valid_attempts if attempt.solved)
        best_score = max(real_scores) if real_scores else None
        avg_score = round(sum(real_scores) / len(real_scores), 2) if real_scores else None
        max_step_fail_count = sum(1 for attempt in real_valid_attempts if attempt.max_steps_failure)
        infra_fail_count = sum(1 for attempt in attempts if attempt.infra_failure)
        verifier_issue_count = sum(
            1 for attempt in real_attempts if attempt.verifier_runtime_issue
        )
        all_real_models_solved = (
            len(real_model_names) > 0
            and len(real_valid_attempts) == len(real_model_names)
            and real_solved_count == len(real_model_names)
        )

        if verifier_issue_count > 0:
            label = "drop_bad_verifier_runtime"
            reason = (
                f"{verifier_issue_count} real model(s) hit verifier runtime issues"
            )
        elif not mock_valid_attempts or len(real_valid_attempts) < min_real_models:
            label = "pending"
            reason = (
                "insufficient coverage: "
                f"mock_valid={len(mock_valid_attempts)}, real_valid={len(real_valid_attempts)}"
            )
        elif mock_solved:
            label = "drop_bad_verifier"
            reason = "mock-noop reached a perfect score"
        elif all_real_models_solved:
            label = "easy_pool"
            reason = "all real models achieved a perfect score"
        elif real_solved_count > 0 or (best_score is not None and best_score >= keep_threshold):
            label = "keep"
            if real_solved_count > 0:
                reason = f"{real_solved_count} real model(s) achieved a perfect score"
            else:
                reason = f"best_score {best_score:.2f} >= keep_threshold {keep_threshold:.2f}"
        elif best_score is None or best_score < broken_threshold:
            label = "drop_broken"
            if best_score is None:
                reason = "no valid real-model score was produced"
            else:
                reason = f"best_score {best_score:.2f} < broken_threshold {broken_threshold:.2f}"
        else:
            label = "drop_ambiguous"
            reason = (
                f"best_score {best_score:.2f} is in the ambiguous band "
                f"[{broken_threshold:.2f}, {keep_threshold:.2f})"
            )

        easy_pool_selected = label == "easy_pool" and _should_sample_easy_task(
            task_id,
            keep_percent=easy_pool_keep_percent,
            sample_salt=sample_salt,
        )
        records.append(
            TaskCurationRecord(
                task_id=task_id,
                label=label,
                reason=reason,
                mock_solved=mock_solved,
                real_models_total=len(real_model_names),
                real_valid_attempts=len(real_valid_attempts),
                real_solved_count=real_solved_count,
                best_score=best_score,
                avg_score=avg_score,
                max_step_fail_count=max_step_fail_count,
                infra_fail_count=infra_fail_count,
                verifier_issue_count=verifier_issue_count,
                easy_pool_selected=easy_pool_selected,
            )
        )
    return records


def build_dataset_manifest(
    records: list[TaskCurationRecord],
    *,
    repo_root: Path,
) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    for record in records:
        if record.label == "keep":
            reason = "keep"
        elif record.label == "easy_pool" and record.easy_pool_selected:
            reason = "easy_pool_sampled"
        else:
            continue
        manifest.append(
            {
                "task_id": record.task_id,
                "task_path": str((repo_root / "tasks" / f"{record.task_id}.yaml").resolve()),
                "asset_path": str((repo_root / "assets" / record.task_id).resolve()),
                "reason": reason,
                "best_score": record.best_score,
                "real_valid_attempts": record.real_valid_attempts,
                "real_solved_count": record.real_solved_count,
            }
        )
    return manifest


def _read_summary_error(summary_path: Path) -> str | None:
    payload = _read_summary_payload(summary_path)
    return _summary_error(payload)


def _read_summary_payload(summary_path: Path) -> dict[str, object] | None:
    if not summary_path.exists():
        return None
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    return payload


def _summary_error(summary_payload: dict[str, object] | None) -> str | None:
    if summary_payload is None:
        return None
    error = summary_payload.get("error")
    return str(error) if isinstance(error, str) and error.strip() else None


def is_infra_failure_error(summary_error: str | None) -> bool:
    return _is_infra_failure(summary_error)


def _is_infra_failure(summary_error: str | None) -> bool:
    if not summary_error:
        return False
    lowered = summary_error.lower()
    return any(hint in lowered for hint in INFRA_FAILURE_HINTS)


def _is_max_steps_failure(summary_error: str | None) -> bool:
    if not summary_error:
        return False
    return "exceeded max steps" in summary_error.lower()


def _should_sample_easy_task(task_id: str, *, keep_percent: int, sample_salt: str) -> bool:
    if keep_percent <= 0:
        return False
    if keep_percent >= 100:
        return True
    digest = hashlib.sha256(f"{sample_salt}:{task_id}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 100
    return bucket < keep_percent
