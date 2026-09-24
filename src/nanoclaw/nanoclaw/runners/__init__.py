from __future__ import annotations

from .base import AgentRunner, RunnerRequest, RunnerResult
from .docker_runner import DockerRunner
from .nanoclaw_runner import NanoclawRunner
from .profiles import RunnerProfile, load_runner_profile


def build_runner(profile: RunnerProfile) -> AgentRunner:
    if profile.runner_type == "nanoclaw":
        return NanoclawRunner(profile)
    if profile.runner_type == "docker":
        return DockerRunner(profile)
    raise ValueError(f"Unsupported runner profile type: {profile.runner_type}")


__all__ = [
    "AgentRunner",
    "DockerRunner",
    "NanoclawRunner",
    "RunnerProfile",
    "RunnerRequest",
    "RunnerResult",
    "build_runner",
    "load_runner_profile",
]
