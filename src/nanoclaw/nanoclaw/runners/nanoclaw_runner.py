from __future__ import annotations

from typing import Any

from nanoclaw.core_loop import MinimalClaw

from .base import AgentRunner, RunnerRequest, RunnerResult
from .profiles import RunnerProfile


class NanoclawRunner(AgentRunner):
    def __init__(self, profile: RunnerProfile | None = None) -> None:
        self.profile = profile or RunnerProfile.nanoclaw()

    def run(self, request: RunnerRequest) -> RunnerResult:
        agent = MinimalClaw(
            request.settings,
            available_skills=request.available_skills,
            activated_skills=request.activated_skills,
        )
        agent._bootstrapped_this_run = request.bootstrapped_this_run
        try:
            final_text = agent.run(
                request.prompt,
                echo=request.echo,
                event_handler=request.event_handler,
                prior_messages=request.prior_messages,
            )
        except Exception as exc:
            report = agent.last_run_report
            error = report.error if report is not None and report.error else f"{type(exc).__name__}: {exc}"
            return RunnerResult(
                status=report.status if report is not None else "failed",
                result_type=report.result_type if report is not None else "failure",
                final_answer=report.final_answer if report is not None else None,
                steps_used=report.steps_used if report is not None else 0,
                error=error,
                workspace_context_files=agent.last_workspace_context_files,
                runtime_metadata=agent.last_runtime_metadata,
                runner_metadata=self._metadata(),
            )

        report = agent.last_run_report
        return RunnerResult(
            status=report.status if report is not None else "completed",
            result_type=report.result_type if report is not None else "final_answer",
            final_answer=final_text,
            steps_used=report.steps_used if report is not None else 0,
            error=report.error if report is not None else None,
            workspace_context_files=agent.last_workspace_context_files,
            runtime_metadata=agent.last_runtime_metadata,
            runner_metadata=self._metadata(),
        )

    def _metadata(self) -> dict[str, Any]:
        return {
            "id": self.profile.profile_id,
            "type": "nanoclaw",
            "profile": str(self.profile.source_path) if self.profile.source_path else None,
        }
