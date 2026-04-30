from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable

from .base import AgentRunner, RunnerRequest, RunnerResult
from .profiles import RunnerProfile


CommandRunner = Callable[[list[str], float | None], subprocess.CompletedProcess[str]]


@dataclass(frozen=True, slots=True)
class _DockerExecution:
    container_id: str | None
    container_name: str
    exit_code: int | None
    timed_out: bool
    stdout_path: Path
    stderr_path: Path
    inspect_path: Path
    events_path: Path
    error: str | None


class DockerRunner(AgentRunner):
    def __init__(
        self,
        profile: RunnerProfile,
        *,
        command_runner: CommandRunner | None = None,
    ) -> None:
        if profile.runner_type != "docker":
            raise ValueError("DockerRunner requires a docker runner profile")
        self.profile = profile
        self._command_runner = command_runner or self._run_command

    def run(self, request: RunnerRequest) -> RunnerResult:
        request.input_dir.mkdir(parents=True, exist_ok=True)
        if request.output_dir.exists():
            shutil.rmtree(request.output_dir)
        request.output_dir.mkdir(parents=True, exist_ok=True)
        request.state_dir.mkdir(parents=True, exist_ok=True)
        self._write_input_files(request)

        execution = self._execute_container(request)
        self._copy_runner_trace(request, execution)

        final_answer_path = request.output_dir / "final_answer.md"
        final_answer = (
            final_answer_path.read_text(encoding="utf-8")
            if final_answer_path.exists()
            else None
        )

        status = "completed"
        error = execution.error
        if execution.timed_out:
            status = "failed"
            error = error or f"Docker runner timed out after {self.profile.timeout_seconds:g}s"
        elif execution.exit_code != 0:
            status = "failed"
            error = error or f"Docker runner exited with code {execution.exit_code}"
        elif final_answer is None:
            status = "failed"
            error = "Docker runner did not write /output/final_answer.md"

        return RunnerResult(
            status=status,
            result_type="final_answer" if status == "completed" else "failure",
            final_answer=final_answer,
            steps_used=0,
            error=error,
            workspace_context_files=self._workspace_context_files(request),
            runtime_metadata=self._runtime_metadata(request),
            runner_metadata=self._runner_metadata(request, execution),
        )

    def build_create_command(
        self,
        request: RunnerRequest,
        *,
        container_name: str,
    ) -> list[str]:
        command = [
            self.profile.docker_executable,
            "create",
            "--name",
            container_name,
            "--label",
            f"nanoclaw.task_id={request.task_id}",
            "--label",
            f"nanoclaw.run_id={request.run_id}",
        ]
        if request.turn is not None:
            command.extend(["--label", f"nanoclaw.turn={request.turn}"])
        if self.profile.network:
            command.extend(["--network", self.profile.network])
        if self.profile.workdir:
            command.extend(["--workdir", self.profile.workdir])
        if self.profile.cpus:
            command.extend(["--cpus", self.profile.cpus])
        if self.profile.memory:
            command.extend(["--memory", self.profile.memory])
        if self.profile.pids_limit is not None:
            command.extend(["--pids-limit", str(self.profile.pids_limit)])

        for name in self.profile.env_pass:
            if name in os.environ:
                command.extend(["-e", name])
        for name, value in sorted(self.profile.env_set.items()):
            command.extend(["-e", f"{name}={value}"])

        command.extend(
            [
                "-v",
                f"{request.workspace_dir.resolve()}:/workspace:rw",
                "-v",
                f"{request.input_dir.resolve()}:/input:ro",
                "-v",
                f"{request.output_dir.resolve()}:/output:rw",
                "-v",
                f"{request.state_dir.resolve()}:/state:rw",
            ]
        )
        command.append(str(self.profile.image))
        command.extend(self.profile.command)
        return command

    def _execute_container(self, request: RunnerRequest) -> _DockerExecution:
        container_name = _container_name(request.task_id, request.run_id, request.turn)
        stdout_path = _runner_file(request, "container_stdout.log")
        stderr_path = _runner_file(request, "container_stderr.log")
        inspect_path = _runner_file(request, "docker_inspect.json")
        events_path = _runner_file(request, "runner_events.jsonl")
        container_id: str | None = None
        exit_code: int | None = None
        timed_out = False
        error: str | None = None

        def emit(event_type: str, **payload: Any) -> None:
            _append_jsonl(
                events_path,
                {
                    "type": event_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **payload,
                },
            )

        create_command = self.build_create_command(
            request,
            container_name=container_name,
        )
        emit("docker_create_started", command=create_command)
        create_result = self._run(create_command, timeout=None)
        emit(
            "docker_create_finished",
            returncode=create_result.returncode,
            stdout=create_result.stdout,
            stderr=create_result.stderr,
        )
        if create_result.returncode != 0:
            error = create_result.stderr.strip() or create_result.stdout.strip() or "docker create failed"
            stdout_path.write_text(create_result.stdout, encoding="utf-8")
            stderr_path.write_text(create_result.stderr, encoding="utf-8")
            return _DockerExecution(
                container_id=None,
                container_name=container_name,
                exit_code=None,
                timed_out=False,
                stdout_path=stdout_path,
                stderr_path=stderr_path,
                inspect_path=inspect_path,
                events_path=events_path,
                error=error,
            )

        container_id = (create_result.stdout.strip().splitlines() or [container_name])[-1]
        start_result = self._run(
            [self.profile.docker_executable, "start", container_id],
            timeout=None,
        )
        emit("docker_start_finished", returncode=start_result.returncode)
        if start_result.returncode != 0:
            error = start_result.stderr.strip() or start_result.stdout.strip() or "docker start failed"
        else:
            try:
                wait_result = self._run(
                    [self.profile.docker_executable, "wait", container_id],
                    timeout=self.profile.timeout_seconds,
                )
                emit(
                    "docker_wait_finished",
                    returncode=wait_result.returncode,
                    stdout=wait_result.stdout,
                    stderr=wait_result.stderr,
                )
                if wait_result.returncode == 0:
                    exit_code = _parse_exit_code(wait_result.stdout)
                else:
                    error = wait_result.stderr.strip() or wait_result.stdout.strip() or "docker wait failed"
            except subprocess.TimeoutExpired:
                timed_out = True
                error = f"Docker runner timed out after {self.profile.timeout_seconds:g}s"
                emit("docker_wait_timed_out", timeout_seconds=self.profile.timeout_seconds)
                self._run([self.profile.docker_executable, "kill", container_id], timeout=None)

        self._collect_container_artifacts(
            container_id=container_id,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            inspect_path=inspect_path,
        )

        if self.profile.remove_container and container_id:
            rm_result = self._run(
                [self.profile.docker_executable, "rm", "-f", container_id],
                timeout=None,
            )
            emit("docker_rm_finished", returncode=rm_result.returncode)

        return _DockerExecution(
            container_id=container_id,
            container_name=container_name,
            exit_code=exit_code,
            timed_out=timed_out,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            inspect_path=inspect_path,
            events_path=events_path,
            error=error,
        )

    def _collect_container_artifacts(
        self,
        *,
        container_id: str,
        stdout_path: Path,
        stderr_path: Path,
        inspect_path: Path,
    ) -> None:
        logs_result = self._run(
            [self.profile.docker_executable, "logs", container_id],
            timeout=None,
        )
        stdout_path.write_text(logs_result.stdout, encoding="utf-8")
        stderr_path.write_text(logs_result.stderr, encoding="utf-8")

        inspect_result = self._run(
            [self.profile.docker_executable, "inspect", container_id],
            timeout=None,
        )
        if inspect_result.returncode == 0:
            inspect_path.write_text(inspect_result.stdout, encoding="utf-8")
        else:
            inspect_path.write_text(
                json.dumps(
                    {
                        "error": inspect_result.stderr.strip()
                        or inspect_result.stdout.strip()
                        or "docker inspect failed"
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

    def _copy_runner_trace(
        self,
        request: RunnerRequest,
        execution: _DockerExecution,
    ) -> None:
        trace_source = request.output_dir / "trace.jsonl"
        if trace_source.exists():
            request.trace_path.parent.mkdir(parents=True, exist_ok=True)
            with request.trace_path.open("a", encoding="utf-8") as destination:
                for raw_line in trace_source.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        destination.write(
                            json.dumps(
                                {
                                    "type": "runner_trace_text",
                                    "turn": request.turn,
                                    "content": line,
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                    else:
                        destination.write(line + "\n")
            return

        _append_jsonl(
            request.trace_path,
            {
                "type": "runner_finished",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "runner": self.profile.profile_id,
                "runner_type": self.profile.runner_type,
                "turn": request.turn,
                "status": "timeout" if execution.timed_out else "finished",
                "exit_code": execution.exit_code,
                "error": execution.error,
            },
        )

    def _write_input_files(self, request: RunnerRequest) -> None:
        (request.input_dir / "task.md").write_text(request.prompt, encoding="utf-8")
        (request.input_dir / "resolved_task.json").write_text(
            json.dumps(request.resolved_task, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (request.input_dir / "prior_messages.json").write_text(
            json.dumps(list(request.prior_messages), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (request.input_dir / "runner_request.json").write_text(
            json.dumps(
                {
                    "task_id": request.task_id,
                    "run_id": request.run_id,
                    "turn": request.turn,
                    "model": request.settings.model,
                    "temperature": request.settings.temperature,
                    "max_steps": request.settings.max_steps,
                    "run_mode": request.settings.run_mode,
                    "memory_policy": request.settings.memory_policy,
                    "approval_mode": request.settings.approval_mode,
                    "workspace_dir": "/workspace",
                    "output_dir": "/output",
                    "state_dir": "/state",
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def _workspace_context_files(self, request: RunnerRequest) -> tuple[str, ...]:
        selected: list[str] = []
        for relative_name in request.settings.workspace_context_files:
            path = request.workspace_dir / relative_name
            if path.exists() and path.is_file():
                selected.append(relative_name)
        return tuple(selected)

    def _runtime_metadata(self, request: RunnerRequest) -> dict[str, Any]:
        now = datetime.now().astimezone()
        return {
            "date_time": now.isoformat(),
            "timezone": str(now.tzinfo or "UTC"),
            "workspace_dir": str(request.workspace_dir.resolve()),
            "model": request.settings.model,
            "run_mode": request.settings.run_mode,
            "memory_policy": request.settings.memory_policy,
            "approval_mode": request.settings.approval_mode,
        }

    def _runner_metadata(
        self,
        request: RunnerRequest,
        execution: _DockerExecution,
    ) -> dict[str, Any]:
        return {
            "id": self.profile.profile_id,
            "type": "docker",
            "profile": str(self.profile.source_path) if self.profile.source_path else None,
            "image": self.profile.image,
            "command": list(self.profile.command),
            "container_id": execution.container_id,
            "container_name": execution.container_name,
            "exit_code": execution.exit_code,
            "timed_out": execution.timed_out,
            "timeout_seconds": self.profile.timeout_seconds,
            "input_dir": str(request.input_dir),
            "output_dir": str(request.output_dir),
            "state_dir": str(request.state_dir),
            "stdout_file": execution.stdout_path.name,
            "stderr_file": execution.stderr_path.name,
            "inspect_file": execution.inspect_path.name,
            "events_file": execution.events_path.name,
        }

    def _run(self, command: list[str], *, timeout: float | None) -> subprocess.CompletedProcess[str]:
        try:
            return self._command_runner(command, timeout)
        except FileNotFoundError as exc:
            return subprocess.CompletedProcess(
                command,
                returncode=127,
                stdout="",
                stderr=str(exc),
            )

    @staticmethod
    def _run_command(
        command: list[str],
        timeout: float | None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )


def _runner_file(request: RunnerRequest, filename: str) -> Path:
    if request.turn is None:
        return request.run_dir / filename
    return request.run_dir / f"turn_{request.turn}_{filename}"


def _container_name(task_id: str, run_id: str, turn: int | None) -> str:
    raw = f"nanoclaw-{task_id}-{run_id}"
    if turn is not None:
        raw = f"{raw}-turn-{turn}"
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw).strip("-")
    return cleaned[:120] or "nanoclaw-run"


def _parse_exit_code(stdout: str) -> int | None:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None
    try:
        return int(lines[-1])
    except ValueError:
        return None


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
