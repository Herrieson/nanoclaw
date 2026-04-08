from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .task_loader import TaskDefinition


APPROVAL_EVENT_TYPES = frozenset(
    {
        "approval_requested",
        "approval_response",
        "command_blocked",
        "command_execution",
    }
)


@dataclass(frozen=True, slots=True)
class TaskRunLayout:
    task: TaskDefinition
    asset_dir: Path
    run_id: str
    run_dir: Path
    workspace_dir: Path
    before_dir: Path
    after_dir: Path
    task_copy_path: Path
    resolved_task_path: Path
    trace_path: Path
    summary_path: Path
    final_answer_path: Path
    approval_log_path: Path


class RunRecorder:
    def __init__(self, layout: TaskRunLayout) -> None:
        self.layout = layout

    def record_event(self, event: dict[str, Any]) -> None:
        _append_jsonl(self.layout.trace_path, event)
        if str(event.get("type", "")) in APPROVAL_EVENT_TYPES:
            _append_jsonl(self.layout.approval_log_path, event)


def create_task_run(
    task: TaskDefinition,
    *,
    assets_root: Path,
    results_root: Path,
    resolved_payload: dict[str, Any] | None = None,
) -> TaskRunLayout:
    asset_dir = (assets_root.expanduser() / task.asset).resolve()
    if not asset_dir.exists() or not asset_dir.is_dir():
        raise FileNotFoundError(f"Asset directory not found: {asset_dir}")

    run_group_dir = (results_root.expanduser() / task.task_id).resolve()
    run_id = _new_run_id(run_group_dir)
    run_dir = run_group_dir / run_id
    workspace_dir = run_dir / "workspace"
    before_dir = run_dir / "workspace_before"
    after_dir = run_dir / "workspace_after"

    workspace_dir.mkdir(parents=True, exist_ok=False)
    _copy_tree(asset_dir, workspace_dir)

    task_copy_path = run_dir / "task.yaml"
    resolved_task_path = run_dir / "resolved_task.json"
    trace_path = run_dir / "trace.jsonl"
    summary_path = run_dir / "summary.json"
    final_answer_path = run_dir / "final_answer.md"
    approval_log_path = run_dir / "approval_log.jsonl"

    task_copy_path.write_text(task.source_text, encoding="utf-8")
    _write_json(resolved_task_path, resolved_payload or task.resolved_payload())

    return TaskRunLayout(
        task=task,
        asset_dir=asset_dir,
        run_id=run_id,
        run_dir=run_dir,
        workspace_dir=workspace_dir,
        before_dir=before_dir,
        after_dir=after_dir,
        task_copy_path=task_copy_path,
        resolved_task_path=resolved_task_path,
        trace_path=trace_path,
        summary_path=summary_path,
        final_answer_path=final_answer_path,
        approval_log_path=approval_log_path,
    )


def snapshot_workspace(source_dir: Path, destination_dir: Path) -> None:
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    shutil.copytree(source_dir, destination_dir)


def write_summary(path: Path, payload: dict[str, Any]) -> None:
    _write_json(path, payload)


def write_final_answer(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_run_id(run_group_dir: Path) -> str:
    prefix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = prefix
    suffix = 1
    while (run_group_dir / candidate).exists():
        suffix += 1
        candidate = f"{prefix}_{suffix}"
    return candidate


def _copy_tree(source_dir: Path, destination_dir: Path) -> None:
    for source_path in source_dir.rglob("*"):
        relative_path = source_path.relative_to(source_dir)
        destination_path = destination_dir / relative_path
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
