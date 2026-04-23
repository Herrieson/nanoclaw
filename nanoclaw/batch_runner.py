from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
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
from .task_loader import load_task_definition


RUN_DIR_PATTERN = re.compile(r"^Run dir:\s+(.+)$", re.MULTILINE)
RUN_ID_PATTERN = re.compile(r"^(?P<ts>\d{8}T\d{6}Z)(?:_(?P<suffix>\d+))?$")
BATCH_ENV_DIRNAME = ".batch_env"


@dataclass(frozen=True, slots=True)
class BatchTaskSpec:
    task_path: Path
    task_id: str
    asset_name: str
    builder_path: Path | None


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


def _run_dir_sort_key(run_dir: Path) -> tuple[str, int, str]:
    match = RUN_ID_PATTERN.fullmatch(run_dir.name)
    if not match:
        return (run_dir.name, 0, run_dir.name)
    suffix = int(match.group("suffix") or "1")
    return (match.group("ts"), suffix, run_dir.name)
