from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from typing import Sequence

from .config import Settings
from .core_loop import MinimalClaw
from .run_store import (
    RunRecorder,
    create_task_run,
    snapshot_workspace,
    utc_now_iso,
    write_final_answer,
    write_summary,
)
from .skills import (
    auto_select_skills,
    discover_skills,
    resolve_requested_skills,
    serialize_skill,
)
from .task_loader import TaskSession, load_task_definition


RUN_DIR_PATTERN = re.compile(r"^Run dir:\s+(.+)$", re.MULTILINE)
RUN_ID_PATTERN = re.compile(r"^(?P<ts>\d{8}T\d{6}Z)(?:_(?P<suffix>\d+))?$")
BATCH_ENV_DIRNAME = ".batch_env"


@dataclass(frozen=True, slots=True)
class BatchTaskSpec:
    task_path: Path
    task_id: str
    asset_name: str
    builder_path: Path | None
    sessions: tuple[TaskSession, ...] = ()

    @property
    def is_multi_turn(self) -> bool:
        return bool(self.sessions)


@dataclass(frozen=True, slots=True)
class BatchTaskResult:
    spec: BatchTaskSpec
    success: bool
    run_dir: Path | None
    returncode: int
    stdout: str
    stderr: str
    error: str | None


class ProgressTracker:
    def __init__(self, total: int) -> None:
        self.total = total
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
        suffix = (
            f" {self.completed}/{self.total} ok={self.succeeded} fail={self.failed}"
        )
        if current_task:
            suffix += f" last={current_task}"
        sys.stderr.write(f"\r[{bar}]{suffix}")
        sys.stderr.flush()


def default_worker_count() -> int:
    cpu_count = os.cpu_count() or 1
    return max(1, min(8, cpu_count))


def batch_assets_root(results_dir: Path) -> Path:
    return (results_dir.expanduser().resolve() / BATCH_ENV_DIRNAME / "assets").resolve()


def resolve_task_specs(
    patterns: Sequence[str],
    *,
    repo_root: Path,
) -> list[BatchTaskSpec]:
    settings = Settings.from_env()
    seen: set[Path] = set()
    specs: list[BatchTaskSpec] = []

    for pattern in patterns:
        matches = sorted(repo_root.glob(pattern))
        if not matches:
            candidate = (repo_root / pattern).resolve()
            if candidate.exists():
                matches = [candidate]
        for path in matches:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            task = load_task_definition(resolved, settings)
            builder_path = repo_root / "tasks" / task.task_id / "env_builder.py"
            specs.append(
                BatchTaskSpec(
                    task_path=resolved,
                    task_id=task.task_id,
                    asset_name=task.asset,
                    builder_path=builder_path if builder_path.exists() else None,
                    sessions=task.sessions,
                )
            )

    return specs


def parse_run_dir(stdout: str) -> Path | None:
    match = RUN_DIR_PATTERN.search(stdout)
    if not match:
        return None
    return Path(match.group(1).strip()).expanduser().resolve()


def find_latest_completed_run_dir(task_id: str, *, results_dir: Path) -> Path | None:
    task_results_dir = (results_dir.expanduser() / task_id).resolve()
    if not task_results_dir.exists():
        return None

    completed_run_dirs: list[Path] = []
    for run_dir in task_results_dir.iterdir():
        if not run_dir.is_dir():
            continue
        summary = _load_run_summary(run_dir)
        if summary is None:
            continue
        if str(summary.get("status") or "") != "completed":
            continue
        completed_run_dirs.append(run_dir.resolve())

    if not completed_run_dirs:
        return None
    return max(completed_run_dirs, key=_run_dir_sort_key)


def partition_task_specs_for_resume(
    specs: Sequence[BatchTaskSpec],
    *,
    results_dir: Path,
) -> tuple[list[BatchTaskSpec], dict[str, Path]]:
    pending_specs: list[BatchTaskSpec] = []
    reused_run_dirs: dict[str, Path] = {}
    for spec in specs:
        completed_run_dir = find_latest_completed_run_dir(
            spec.task_id,
            results_dir=results_dir,
        )
        if completed_run_dir is None:
            pending_specs.append(spec)
            continue
        reused_run_dirs[spec.task_id] = completed_run_dir
    return pending_specs, reused_run_dirs


def prepare_environment(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    assets_root: Path | None = None,
) -> Path:
    shared_assets_root = (repo_root / "assets").resolve()
    runtime_assets_root = (
        assets_root.expanduser().resolve()
        if assets_root is not None
        else shared_assets_root
    )
    asset_dir = (runtime_assets_root / spec.asset_name).resolve()
    source_asset_dir = (shared_assets_root / spec.asset_name).resolve()
    if spec.builder_path is None:
        if not source_asset_dir.exists():
            raise FileNotFoundError(
                f"Missing asset directory and no env_builder.py for {spec.task_id}: {source_asset_dir}"
            )
        if runtime_assets_root == shared_assets_root:
            return source_asset_dir
        if asset_dir.exists():
            shutil.rmtree(asset_dir)
        asset_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_asset_dir, asset_dir)
        return asset_dir

    if asset_dir.exists():
        shutil.rmtree(asset_dir)

    if spec.is_multi_turn:
        if spec.builder_path is None:
            raise FileNotFoundError(f"Missing env_builder.py for multi-turn task: {spec.task_id}")
        asset_dir.mkdir(parents=True, exist_ok=True)
        _run_builder_for_workspace(
            spec,
            workspace_dir=asset_dir,
            turn=spec.sessions[0].turn,
            env={
                **os.environ,
                "NANOCLAW_ASSETS_ROOT": str(runtime_assets_root),
            },
        )
        return asset_dir

    builder_workspace_root = runtime_assets_root.parent
    builder_workspace_root.mkdir(parents=True, exist_ok=True)
    wrapped_impl = spec.builder_path.with_name("_env_builder_impl.py")
    command = [sys.executable, str(wrapped_impl if wrapped_impl.exists() else spec.builder_path)]
    cwd = builder_workspace_root
    if wrapped_impl.exists():
        asset_dir.mkdir(parents=True, exist_ok=True)
        cwd = asset_dir

    subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    if not asset_dir.exists():
        raise FileNotFoundError(
            f"env_builder.py completed but asset directory was not created: {asset_dir}"
        )
    return asset_dir


def cleanup_environment(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    assets_root: Path | None = None,
) -> None:
    shared_assets_root = (repo_root / "assets").resolve()
    runtime_assets_root = (
        assets_root.expanduser().resolve()
        if assets_root is not None
        else shared_assets_root
    )
    if spec.builder_path is None and runtime_assets_root == shared_assets_root:
        return
    asset_dir = (runtime_assets_root / spec.asset_name).resolve()
    if asset_dir.exists():
        shutil.rmtree(asset_dir)


def run_single_task(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    results_dir: Path,
    assets_root: Path | None,
    model: str | None,
    cleanup_assets: bool,
    approval_mode: str | None,
) -> BatchTaskResult:
    stdout = ""
    stderr = ""
    run_dir: Path | None = None

    try:
        prepare_environment(spec, repo_root=repo_root, assets_root=assets_root)
        if spec.is_multi_turn:
            run_dir = _run_multi_turn_task(
                spec,
                repo_root=repo_root,
                results_dir=results_dir,
                assets_root=assets_root,
                model=model,
                approval_mode=approval_mode,
            )
            stdout = f"Run dir: {run_dir}\n"
            return BatchTaskResult(
                spec=spec,
                success=True,
                run_dir=run_dir,
                returncode=0,
                stdout=stdout,
                stderr=stderr,
                error=None,
            )
        command = [
            sys.executable,
            str(repo_root / "main.py"),
            "run-task",
            "--task",
            str(spec.task_path),
            "--results-dir",
            str(results_dir),
        ]
        if assets_root is not None:
            command.extend(["--assets-dir", str(assets_root)])
        if model:
            command.extend(["--model", model])
        if approval_mode:
            command.extend(["--approval-mode", approval_mode])
        process = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
        )
        stdout = process.stdout
        stderr = process.stderr
        run_dir = parse_run_dir(stdout)
        return BatchTaskResult(
            spec=spec,
            success=process.returncode == 0,
            run_dir=run_dir,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr,
            error=None if process.returncode == 0 else f"run-task exited with {process.returncode}",
        )
    except Exception as exc:
        return BatchTaskResult(
            spec=spec,
            success=False,
            run_dir=run_dir,
            returncode=1,
            stdout=stdout,
            stderr=stderr,
            error=str(exc),
        )
    finally:
        if cleanup_assets:
            cleanup_environment(spec, repo_root=repo_root, assets_root=assets_root)


def run_batch(
    specs: Sequence[BatchTaskSpec],
    *,
    repo_root: Path,
    results_dir: Path,
    assets_root: Path | None,
    model: str | None,
    workers: int,
    cleanup_assets: bool,
    approval_mode: str | None,
) -> list[BatchTaskResult]:
    tracker = ProgressTracker(total=len(specs))
    tracker.start()

    results: list[BatchTaskResult] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(
                run_single_task,
                spec,
                repo_root=repo_root,
                results_dir=results_dir,
                assets_root=assets_root,
                model=model,
                cleanup_assets=cleanup_assets,
                approval_mode=approval_mode,
            ): spec
            for spec in specs
        }
        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            tracker.advance(success=result.success, current_task=result.spec.task_id)
    return results


def _load_run_summary(run_dir: Path) -> dict[str, object] | None:
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        return None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _run_multi_turn_task(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    results_dir: Path,
    assets_root: Path | None,
    model: str | None,
    approval_mode: str | None,
) -> Path:
    settings = Settings.from_env()
    task = load_task_definition(spec.task_path, settings)
    task_runtime = replace(
        task.runtime,
        model=model or task.runtime.model,
        approval_mode=approval_mode or task.runtime.approval_mode,
    )
    task = replace(task, runtime=task_runtime)
    resolved_assets_root = assets_root.expanduser().resolve() if assets_root is not None else (repo_root / "assets").resolve()
    skill_workspace_dir = resolved_assets_root / task.asset
    catalog, available_skills, activated_skills = _select_task_skills(
        task_text=task.prompt,
        settings=settings,
        workspace_dir=skill_workspace_dir,
        available_skill_names=task.skills.available if task.skills.available_explicit else None,
        requested_skill_names=task.skills.include,
        auto_skills=task.skills.auto,
    )
    layout = create_task_run(
        task,
        assets_root=resolved_assets_root,
        results_root=results_dir,
        resolved_payload=task.resolved_payload(
            activated_skills=tuple(serialize_skill(skill) for skill in activated_skills)
        ),
    )
    task_settings = replace(
        settings,
        workspace_dir=layout.workspace_dir,
        model=task.runtime.model,
        workspace_context_files=task.runtime.workspace_context_files,
        run_mode=task.runtime.mode,
        memory_policy=task.runtime.memory_policy,
        approval_mode=task.runtime.approval_mode,
        max_steps=task.runtime.max_steps,
        temperature=task.runtime.temperature,
    )

    agent = MinimalClaw(
        task_settings,
        available_skills=available_skills,
        activated_skills=activated_skills,
    )
    _materialize_skill_pool(layout.workspace_dir, available_skills)
    agent.bootstrap_workspace()
    snapshot_workspace(layout.workspace_dir, layout.before_dir)

    recorder = RunRecorder(layout)
    started_at = utc_now_iso()
    run_error: Exception | None = None
    prior_messages: list[dict[str, str]] = []
    turn_summaries: list[dict[str, object]] = []
    final_texts: list[str] = []
    total_steps_used = 0
    final_report = None

    try:
        for index, session in enumerate(task.sessions):
            if index > 0:
                _run_builder_for_workspace(
                    spec,
                    workspace_dir=layout.workspace_dir,
                    turn=session.turn,
                    env={
                        **os.environ,
                        "NANOCLAW_ASSETS_ROOT": str(resolved_assets_root),
                    },
                )

            recorder.record_event({"type": "turn_started", "turn": session.turn})
            turn_error: str | None = None
            turn_final_answer_path = layout.run_dir / f"final_answer_turn_{session.turn}.md"
            try:
                final_text = agent.run(
                    session.prompt,
                    echo=False,
                    event_handler=recorder.record_event,
                    prior_messages=tuple(prior_messages),
                )
                final_texts.append(f"## Turn {session.turn}\n\n{final_text}")
                write_final_answer(turn_final_answer_path, final_text)
                prior_messages.append({"role": "user", "content": session.prompt})
                prior_messages.append({"role": "assistant", "content": final_text})
            except Exception as exc:
                run_error = exc
                turn_error = f"{type(exc).__name__}: {exc}"
                final_text = turn_error
                final_texts.append(f"## Turn {session.turn}\n\n{turn_error}")
                write_final_answer(turn_final_answer_path, turn_error)

            report = agent.last_run_report
            final_report = report
            if report is not None:
                total_steps_used += report.steps_used
            turn_after_dir = _turn_after_dir(layout.run_dir, session.turn)
            snapshot_workspace(layout.workspace_dir, turn_after_dir)
            turn_summary = {
                "turn": session.turn,
                "prompt_source": session.prompt_source,
                "status": report.status if report else "failed",
                "result_type": report.result_type if report else "failure",
                "error": turn_error or (report.error if report else None),
                "steps_used": report.steps_used if report else 0,
                "final_answer_file": turn_final_answer_path.name,
                "after_state_dir": turn_after_dir.name,
            }
            turn_summaries.append(turn_summary)
            recorder.record_event({"type": "turn_finished", **turn_summary})
            if run_error is not None:
                break
    finally:
        snapshot_workspace(layout.workspace_dir, layout.after_dir)
        finished_at = utc_now_iso()
        write_final_answer(layout.final_answer_path, "\n\n".join(final_texts))
        all_completed = (
            run_error is None
            and len(turn_summaries) == len(task.sessions)
            and all(item.get("status") == "completed" for item in turn_summaries)
        )
        summary = {
            "task_id": task.task_id,
            "task_name": task.name,
            "description": task.description,
            "asset": task.asset,
            "asset_dir": str(layout.asset_dir),
            "task_file": str(task.source_path),
            "run_id": layout.run_id,
            "result_dir": str(layout.run_dir),
            "status": "completed" if all_completed else "failed",
            "result_type": final_report.result_type if final_report else "failure",
            "error": str(run_error) if run_error is not None else None,
            "model": task_settings.model,
            "max_steps": task_settings.max_steps,
            "temperature": task_settings.temperature,
            "run_mode": task_settings.run_mode,
            "memory_policy": task_settings.memory_policy,
            "approval_mode": task_settings.approval_mode,
            "session": task.runtime.session,
            "turns": turn_summaries,
            "workspace_context_files": list(agent.last_workspace_context_files),
            "runtime_metadata": agent.last_runtime_metadata,
            "skills": {
                "available": [serialize_skill(skill) for skill in available_skills],
                "requested": list(task.skills.include),
                "auto": task.skills.auto,
                "activated": [serialize_skill(skill) for skill in activated_skills],
            },
            "steps_used": total_steps_used,
            "started_at": started_at,
            "finished_at": finished_at,
            "final_answer_file": layout.final_answer_path.name,
            "trace_file": layout.trace_path.name,
            "before_state_dir": layout.before_dir.name,
            "after_state_dir": layout.after_dir.name,
            "multi_turn": True,
        }
        if catalog.errors:
            summary["skill_discovery_errors"] = [
                {"source_path": str(error.source_path), "error": error.error}
                for error in catalog.errors
            ]
        write_summary(layout.summary_path, summary)

    if run_error is not None:
        raise run_error
    return layout.run_dir


def _turn_after_dir(run_dir: Path, turn: int) -> Path:
    return run_dir / f"workspace_after_turn_{turn}"


def _run_builder_for_workspace(
    spec: BatchTaskSpec,
    *,
    workspace_dir: Path,
    turn: int,
    env: dict[str, str],
) -> None:
    if spec.builder_path is None:
        raise FileNotFoundError(f"Missing env_builder.py for {spec.task_id}")
    script_path = _builder_execution_path(spec.builder_path)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(script_path), "--turn", str(turn)],
        cwd=workspace_dir,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


def _builder_execution_path(builder_path: Path) -> Path:
    wrapped_impl = builder_path.with_name("_env_builder_impl.py")
    return wrapped_impl if wrapped_impl.exists() else builder_path


def _select_task_skills(
    *,
    task_text: str,
    settings: Settings,
    workspace_dir: Path,
    available_skill_names: tuple[str, ...] | None,
    requested_skill_names: tuple[str, ...],
    auto_skills: bool,
):
    catalog = discover_skills(workspace_dir, settings.extra_skill_dirs)
    available_skills = catalog.skills
    if available_skill_names is not None:
        available_skills = (
            resolve_requested_skills(catalog.skills, available_skill_names)
            if available_skill_names
            else ()
        )

    selected = list(resolve_requested_skills(available_skills, requested_skill_names))
    selected_slugs = {skill.slug for skill in selected}
    if auto_skills:
        for skill in auto_select_skills(available_skills, task_text):
            if skill.slug in selected_slugs:
                continue
            selected.append(skill)
            selected_slugs.add(skill.slug)
    return catalog, available_skills, tuple(selected)


def _materialize_skill_pool(workspace_dir: Path, available_skills) -> None:
    skill_root = workspace_dir / ".skills"
    if skill_root.exists():
        shutil.rmtree(skill_root)
    if not available_skills:
        return
    skill_root.mkdir(parents=True, exist_ok=True)
    for skill in available_skills:
        shutil.copytree(skill.source_path.parent, skill_root / skill.slug)


def _run_dir_sort_key(run_dir: Path) -> tuple[str, int, str]:
    match = RUN_ID_PATTERN.fullmatch(run_dir.name)
    if not match:
        return (run_dir.name, 0, run_dir.name)
    suffix = int(match.group("suffix") or "1")
    return (match.group("ts"), suffix, run_dir.name)
