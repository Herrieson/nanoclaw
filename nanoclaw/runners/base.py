from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from nanoclaw.config import Settings
from nanoclaw.skills import SkillDefinition


RunnerEventHandler = Callable[[dict[str, Any]], None]


@dataclass(frozen=True, slots=True)
class RunnerRequest:
    task_id: str
    run_id: str
    prompt: str
    resolved_task: dict[str, Any]
    settings: Settings
    workspace_dir: Path
    run_dir: Path
    input_dir: Path
    output_dir: Path
    state_dir: Path
    trace_path: Path
    approval_log_path: Path
    available_skills: tuple[SkillDefinition, ...] = ()
    activated_skills: tuple[SkillDefinition, ...] = ()
    prior_messages: tuple[dict[str, str], ...] = ()
    event_handler: RunnerEventHandler | None = None
    echo: bool = True
    turn: int | None = None
    bootstrapped_this_run: bool = False


@dataclass(frozen=True, slots=True)
class RunnerResult:
    status: str
    result_type: str
    final_answer: str | None
    steps_used: int
    error: str | None
    workspace_context_files: tuple[str, ...] = ()
    runtime_metadata: dict[str, Any] = field(default_factory=dict)
    runner_metadata: dict[str, Any] = field(default_factory=dict)


class AgentRunner(Protocol):
    def run(self, request: RunnerRequest) -> RunnerResult:
        ...
