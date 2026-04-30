from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from .config import Settings
from .task_loader import load_task_definition


ABSOLUTE_REPO_PATH_PATTERN = re.compile(r"""['"]/(?:workspace|assets)(?:/|['"])""")
PROMPT_REPO_ASSET_PATH_PATTERN = re.compile(r"\bassets/data_[A-Za-z0-9_-]+(?:/|`)")
PROMPT_PATH_TOKEN_PATTERN = re.compile(
    r"assets/(?P<task_id>data_[A-Za-z0-9_-]+)(?P<suffix>/[^\s`'\"),.:;!?]*)?"
)
VERIFY_WORKSPACE_LITERAL_PATTERN = re.compile(r'(?P<quote>[\'"])/workspace(?P<suffix>/[^\'"]*)?(?P=quote)')
VERIFY_ASSET_LITERAL_PATTERN = re.compile(
    r'(?P<quote>[\'"])assets/(?P<task_id>data_[A-Za-z0-9_-]+)(?P<suffix>/[^\'"]*)?(?P=quote)'
)
VERIFY_TASKS_LITERAL_PATTERN = re.compile(
    r'(?P<quote>[\'"])tasks/(?P<task_id>data_[A-Za-z0-9_-]+)(?P<suffix>/[^\'"]*)?(?P=quote)'
)
VERIFY_ASSET_JOIN_PATTERN = re.compile(
    r'os\.path\.join\(\s*(?P<q1>[\'"])assets(?P=q1)\s*,\s*(?P<q2>["\'])'
    r'(?P<task_id>data_[A-Za-z0-9_-]+)(?P=q2)\s*\)'
)
VERIFY_ASSET_BASEDIR_PATTERN = re.compile(
    r"os\.path\.abspath\(\s*os\.path\.join\(\s*os\.path\.dirname\(__file__\)\s*,\s*"
    r"(?P<q>[\"'])\.\./\.\./assets/(?P<task_id>data_[A-Za-z0-9_-]+)(?P=q)\s*\)\s*\)"
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    task_path: Path
    task_id: str
    task_dir: Path
    asset_dir: Path
    builder_path: Path | None
    prompt_paths: tuple[Path, ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity == "warning" for issue in self.issues)


@dataclass(frozen=True, slots=True)
class PromptAutofixResult:
    task_id: str
    changed_files: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class VerifyRulesAutofixResult:
    task_id: str
    changed_files: tuple[Path, ...]


def validate_generated_task(
    task_path: Path,
    *,
    repo_root: Path,
    run_builder: bool = False,
    keep_assets: bool = False,
    settings: Settings | None = None,
    assets_root: Path | None = None,
) -> ValidationResult:
    source_path = task_path.expanduser().resolve()
    task_id = source_path.stem
    task_dir = (repo_root / "tasks" / task_id).resolve()
    shared_assets_root = (repo_root / "assets").resolve()
    runtime_assets_root = (
        assets_root.expanduser().resolve()
        if assets_root is not None
        else shared_assets_root
    )
    asset_dir = (runtime_assets_root / task_id).resolve()
    repo_asset_dir = (shared_assets_root / task_id).resolve()
    builder_path = (repo_root / "tasks" / task_id / "env_builder.py").resolve()
    if not builder_path.exists():
        builder_path = None
    prompt_paths = _fallback_prompt_paths(source_path, repo_root)

    issues: list[ValidationIssue] = []
    validation_settings = settings or Settings.from_env()

    try:
        task = load_task_definition(source_path, validation_settings)
    except Exception as exc:
        issues.append(
            ValidationIssue(
                severity="error",
                code="task_load_failed",
                message=str(exc),
            )
        )
        return ValidationResult(
            task_path=source_path,
            task_id=task_id,
            task_dir=task_dir,
            asset_dir=asset_dir,
            builder_path=builder_path,
            prompt_paths=prompt_paths,
            issues=tuple(issues),
        )

    task_id = task.task_id
    task_dir = (repo_root / "tasks" / task_id).resolve()
    asset_dir = (runtime_assets_root / task.asset).resolve()
    repo_asset_dir = (shared_assets_root / task.asset).resolve()
    expected_builder_path = (repo_root / "tasks" / task_id / "env_builder.py").resolve()
    builder_path = expected_builder_path if expected_builder_path.exists() else None
    prompt_paths = _resolve_prompt_paths(task.prompt_sources, source_path=source_path, repo_root=repo_root)

    if PROMPT_REPO_ASSET_PATH_PATTERN.search(task.prompt):
        issues.append(
            ValidationIssue(
                severity="warning",
                code="prompt_uses_repo_asset_path",
                message=(
                    "Prompt still references repository asset paths like assets/data_xx/; "
                    "generated prompts should use runtime-relative workspace paths."
                ),
            )
        )

    if builder_path is None and not asset_dir.exists() and not repo_asset_dir.exists():
        issues.append(
            ValidationIssue(
                severity="error",
                code="missing_asset_and_builder",
                message=(
                    f"Expected either {repo_asset_dir} to exist or {repo_root / 'tasks' / task_id / 'env_builder.py'} "
                    "to be present."
                ),
            )
        )

    if builder_path is not None:
        builder_text = builder_path.read_text(encoding="utf-8", errors="replace")
        if not builder_text.strip():
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="empty_builder",
                    message=f"{builder_path} is empty.",
                )
            )
        if ABSOLUTE_REPO_PATH_PATTERN.search(builder_text):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="builder_uses_absolute_repo_path",
                    message=(
                        f"{builder_path} contains hard-coded /workspace or /assets paths; "
                        "builders should write under repo-local assets/<task_id>/."
                    ),
                )
            )
        if "app.run(" in builder_text or "socket." in builder_text or "subprocess.Popen(" in builder_text:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="builder_starts_service",
                    message=(
                        f"{builder_path} appears to start a server or background process. "
                        "That is fragile under batch execution."
                    ),
                )
            )

        if run_builder:
            if asset_dir.exists():
                shutil.rmtree(asset_dir)
            builder_workspace_root = runtime_assets_root.parent
            builder_workspace_root.mkdir(parents=True, exist_ok=True)
            wrapped_impl = builder_path.with_name("_env_builder_impl.py")
            command = [sys.executable, str(wrapped_impl if wrapped_impl.exists() else builder_path)]
            cwd = builder_workspace_root
            if wrapped_impl.exists():
                asset_dir.mkdir(parents=True, exist_ok=True)
                cwd = asset_dir
            try:
                env = {
                    **os.environ,
                    "NANOCLAW_ASSETS_ROOT": str(runtime_assets_root),
                }
                processes = []
                if task.sessions:
                    if not asset_dir.exists():
                        asset_dir.mkdir(parents=True, exist_ok=True)
                    cwd = asset_dir
                    for session in task.sessions:
                        processes.append(
                            subprocess.run(
                                [*command, "--turn", str(session.turn)],
                                cwd=cwd,
                                check=True,
                                capture_output=True,
                                text=True,
                                env=env,
                            )
                        )
                else:
                    processes.append(
                        subprocess.run(
                            command,
                            cwd=cwd,
                            check=True,
                            capture_output=True,
                            text=True,
                            env=env,
                        )
                    )
                if not asset_dir.exists():
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="builder_missing_asset_dir",
                            message=(
                                f"{builder_path} exited successfully but did not create {asset_dir}."
                            ),
                        )
                    )
                elif any(process.stderr.strip() for process in processes):
                    stderr = "\n".join(
                        process.stderr.strip().splitlines()[-1]
                        for process in processes
                        if process.stderr.strip()
                    )
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            code="builder_stderr_output",
                            message=stderr,
                        )
                    )
            except subprocess.CalledProcessError as exc:
                tail = exc.stderr.strip().splitlines()[-1] if exc.stderr.strip() else str(exc)
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="builder_execution_failed",
                        message=tail,
                    )
                )
            finally:
                if builder_path is not None and asset_dir.exists() and not keep_assets:
                    shutil.rmtree(asset_dir)

    verify_rules_path = task_dir / "verify_rules.py"
    if verify_rules_path.exists():
        verify_text = verify_rules_path.read_text(encoding="utf-8", errors="replace")
        if "/workspace" in verify_text:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="verify_rules_uses_workspace_literal",
                    message=(
                        f"{verify_rules_path} still references /workspace. "
                        "verify_rules.py should use cwd-relative paths or an explicit argv base dir."
                    ),
                )
            )
        if f"assets/{task_id}" in verify_text or f'"assets", "{task_id}"' in verify_text or f"'assets', '{task_id}'" in verify_text:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="verify_rules_uses_repo_asset_path",
                    message=(
                        f"{verify_rules_path} still references assets/{task_id}. "
                        "verify_rules.py should validate against the runtime workspace, not repo assets."
                    ),
                )
            )
        if f"tasks/{task_id}" in verify_text:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="verify_rules_writes_into_task_source_tree",
                    message=(
                        f"{verify_rules_path} still writes under tasks/{task_id}. "
                        "verify output should be emitted into the runtime workspace."
                    ),
                )
            )

    return ValidationResult(
        task_path=source_path,
        task_id=task_id,
        task_dir=task_dir,
        asset_dir=asset_dir,
        builder_path=builder_path,
        prompt_paths=prompt_paths,
        issues=tuple(issues),
    )


def autofix_prompt_repo_asset_paths(
    task_path: Path,
    *,
    repo_root: Path,
    settings: Settings | None = None,
) -> PromptAutofixResult:
    source_path = task_path.expanduser().resolve()
    validation_settings = settings or Settings.from_env()
    task = load_task_definition(source_path, validation_settings)
    prompt_paths = _resolve_prompt_paths(
        task.prompt_sources,
        source_path=source_path,
        repo_root=repo_root,
    )

    changed: list[Path] = []
    for prompt_path in prompt_paths:
        original = prompt_path.read_text(encoding="utf-8")
        updated = _rewrite_prompt_repo_asset_paths(original, task.task_id)
        if updated == original:
            continue
        prompt_path.write_text(updated, encoding="utf-8")
        changed.append(prompt_path)

    return PromptAutofixResult(task_id=task.task_id, changed_files=tuple(changed))


def autofix_verify_rules_runtime_paths(
    task_path: Path,
    *,
    repo_root: Path,
) -> VerifyRulesAutofixResult:
    source_path = task_path.expanduser().resolve()
    task_id = source_path.stem
    verify_rules_path = (repo_root / "tasks" / task_id / "verify_rules.py").resolve()
    if not verify_rules_path.exists():
        return VerifyRulesAutofixResult(task_id=task_id, changed_files=())

    original = verify_rules_path.read_text(encoding="utf-8")
    updated = _rewrite_verify_rules_runtime_paths(original, task_id)
    if updated == original:
        return VerifyRulesAutofixResult(task_id=task_id, changed_files=())

    verify_rules_path.write_text(updated, encoding="utf-8")
    return VerifyRulesAutofixResult(task_id=task_id, changed_files=(verify_rules_path,))


def collect_task_artifacts(result: ValidationResult, *, repo_root: Path) -> tuple[Path, ...]:
    candidates = [result.task_path, *result.prompt_paths, result.task_dir, result.asset_dir]
    seen: set[Path] = set()
    resolved: list[Path] = []
    for path in candidates:
        candidate = path.resolve()
        if candidate in seen or not candidate.exists():
            continue
        try:
            candidate.relative_to(repo_root)
        except ValueError:
            continue
        seen.add(candidate)
        resolved.append(candidate)
    return tuple(resolved)


def quarantine_invalid_task(
    result: ValidationResult,
    *,
    repo_root: Path,
    quarantine_root: Path,
) -> tuple[Path, ...]:
    moved: list[Path] = []
    quarantine_root.mkdir(parents=True, exist_ok=True)
    for path in collect_task_artifacts(result, repo_root=repo_root):
        relative = path.relative_to(repo_root)
        destination = _unique_destination(quarantine_root / relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(destination))
        moved.append(destination)
    return tuple(moved)


def delete_invalid_task(
    result: ValidationResult,
    *,
    repo_root: Path,
) -> tuple[Path, ...]:
    deleted: list[Path] = []
    for path in collect_task_artifacts(result, repo_root=repo_root):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        deleted.append(path)
    return tuple(deleted)


def result_to_dict(result: ValidationResult) -> dict[str, object]:
    return {
        "task_id": result.task_id,
        "task_path": str(result.task_path),
        "task_dir": str(result.task_dir),
        "asset_dir": str(result.asset_dir),
        "builder_path": str(result.builder_path) if result.builder_path is not None else None,
        "prompt_paths": [str(path) for path in result.prompt_paths],
        "issues": [
            {
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
            }
            for issue in result.issues
        ],
    }


def write_validation_report(
    results: tuple[ValidationResult, ...] | list[ValidationResult],
    *,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [result_to_dict(result) for result in results]
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _resolve_prompt_paths(
    prompt_sources: tuple[str, ...],
    *,
    source_path: Path,
    repo_root: Path,
) -> tuple[Path, ...]:
    resolved: list[Path] = []
    for item in prompt_sources:
        source = item.strip()
        if not source or "\n" in source:
            continue
        candidate = (source_path.parent / source).resolve()
        if candidate.exists():
            resolved.append(candidate)
            continue
        fallback = (repo_root / "tasks" / source).resolve()
        if fallback.exists():
            resolved.append(fallback)
    if resolved:
        return tuple(dict.fromkeys(resolved))
    return _fallback_prompt_paths(source_path, repo_root)


def _fallback_prompt_paths(source_path: Path, repo_root: Path) -> tuple[Path, ...]:
    prompt_path = (repo_root / "tasks" / "prompts" / f"{source_path.stem}.md").resolve()
    return (prompt_path,) if prompt_path.exists() else ()


def _unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    index = 1
    while True:
        candidate = path.with_name(f"{stem}.{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def _rewrite_prompt_repo_asset_paths(prompt_text: str, task_id: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        matched_task_id = match.group("task_id")
        if matched_task_id != task_id:
            return match.group(0)

        suffix = match.group("suffix")
        if not suffix:
            return "./"
        trimmed = suffix.lstrip("/")
        return trimmed if trimmed else "./"

    return PROMPT_PATH_TOKEN_PATTERN.sub(replacer, prompt_text)


def _rewrite_verify_rules_runtime_paths(verify_text: str, task_id: str) -> str:
    def workspace_replacer(match: re.Match[str]) -> str:
        quote = match.group("quote")
        suffix = match.group("suffix") or ""
        if suffix.startswith("/"):
            replacement = suffix[1:] or "."
        else:
            replacement = "."
        return f"{quote}{replacement}{quote}"

    def asset_replacer(match: re.Match[str]) -> str:
        quote = match.group("quote")
        matched_task_id = match.group("task_id")
        if matched_task_id != task_id:
            return match.group(0)
        suffix = match.group("suffix") or ""
        if suffix.startswith("/"):
            replacement = suffix[1:] or "."
        else:
            replacement = "."
        return f"{quote}{replacement}{quote}"

    def asset_join_replacer(match: re.Match[str]) -> str:
        matched_task_id = match.group("task_id")
        if matched_task_id != task_id:
            return match.group(0)
        return '"."'

    def tasks_replacer(match: re.Match[str]) -> str:
        quote = match.group("quote")
        matched_task_id = match.group("task_id")
        if matched_task_id != task_id:
            return match.group(0)
        suffix = match.group("suffix") or ""
        if suffix.startswith("/"):
            replacement = suffix[1:] or "."
        else:
            replacement = "."
        return f"{quote}{replacement}{quote}"

    def asset_basedir_replacer(match: re.Match[str]) -> str:
        matched_task_id = match.group("task_id")
        if matched_task_id != task_id:
            return match.group(0)
        return '"."'

    updated = VERIFY_WORKSPACE_LITERAL_PATTERN.sub(workspace_replacer, verify_text)
    updated = VERIFY_ASSET_LITERAL_PATTERN.sub(asset_replacer, updated)
    updated = VERIFY_TASKS_LITERAL_PATTERN.sub(tasks_replacer, updated)
    updated = VERIFY_ASSET_JOIN_PATTERN.sub(asset_join_replacer, updated)
    updated = VERIFY_ASSET_BASEDIR_PATTERN.sub(asset_basedir_replacer, updated)
    return updated
