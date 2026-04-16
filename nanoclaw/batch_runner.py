from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
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


def prepare_environment(spec: BatchTaskSpec, *, repo_root: Path) -> Path:
    asset_dir = (repo_root / "assets" / spec.asset_name).resolve()
    if spec.builder_path is None:
        if not asset_dir.exists():
            raise FileNotFoundError(
                f"Missing asset directory and no env_builder.py for {spec.task_id}: {asset_dir}"
            )
        return asset_dir

    if asset_dir.exists():
        shutil.rmtree(asset_dir)

    subprocess.run(
        [sys.executable, str(spec.builder_path)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    if not asset_dir.exists():
        raise FileNotFoundError(
            f"env_builder.py completed but asset directory was not created: {asset_dir}"
        )
    return asset_dir


def cleanup_environment(spec: BatchTaskSpec, *, repo_root: Path) -> None:
    if spec.builder_path is None:
        return
    asset_dir = (repo_root / "assets" / spec.asset_name).resolve()
    if asset_dir.exists():
        shutil.rmtree(asset_dir)


def run_single_task(
    spec: BatchTaskSpec,
    *,
    repo_root: Path,
    results_dir: Path,
    model: str | None,
    cleanup_assets: bool,
    approval_mode: str | None,
) -> BatchTaskResult:
    stdout = ""
    stderr = ""
    run_dir: Path | None = None

    try:
        prepare_environment(spec, repo_root=repo_root)
        command = [
            sys.executable,
            str(repo_root / "main.py"),
            "run-task",
            "--task",
            str(spec.task_path),
            "--results-dir",
            str(results_dir),
        ]
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
            cleanup_environment(spec, repo_root=repo_root)


def run_batch(
    specs: Sequence[BatchTaskSpec],
    *,
    repo_root: Path,
    results_dir: Path,
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
