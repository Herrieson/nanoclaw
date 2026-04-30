from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import shutil
from typing import Any

import yaml

from .config import DEFAULT_MEMORY_POLICY, DEFAULT_RUN_MODE, Settings
from .task_loader import load_task_definition


SUPPORTED_ENVIRONMENT_KEYS = frozenset({"asset", "workspace_context_files"})
SUPPORTED_RUNTIME_KEYS = frozenset(
    {
        "model",
        "mode",
        "session",
        "memory_policy",
        "approval_mode",
        "workspace_context_files",
        "max_steps",
        "temperature",
        "assets",
    }
)
SUPPORTED_SKILL_KEYS = frozenset({"available", "include", "auto"})
REMOVED_TOP_LEVEL_KEYS = frozenset({"task", "asset", "x_legacy"})
DEFAULT_RUNTIME = {
    "model": "gpt-4o",
    "mode": DEFAULT_RUN_MODE,
    "memory_policy": DEFAULT_MEMORY_POLICY,
    "approval_mode": "reject",
    "max_steps": 30,
    "temperature": 0.2,
}


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    path: Path
    changed: bool
    backup_path: Path | None
    task_id: str
    asset: str


def normalize_task_file(
    task_path: Path,
    *,
    create_backup: bool = True,
    backup_root: Path | None = None,
    settings: Settings | None = None,
) -> NormalizationResult:
    source_path = task_path.expanduser().resolve()
    original_text = source_path.read_text(encoding="utf-8")
    payload = yaml.safe_load(original_text) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Task YAML must contain a top-level mapping: {source_path}")

    normalized = normalize_task_payload(payload, source_path=source_path)
    new_text = _dump_yaml(normalized)
    changed = new_text != original_text
    backup_path: Path | None = None

    if changed and create_backup:
        backup_base = (
            backup_root.expanduser().resolve()
            if backup_root is not None
            else source_path.parent.parent / ".task_normalizer_backups"
        )
        backup_path = backup_base / source_path.relative_to(source_path.parent.parent)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, backup_path)

    if changed:
        source_path.write_text(new_text, encoding="utf-8")

    validation_settings = settings or Settings.from_env()
    task = load_task_definition(source_path, validation_settings)
    return NormalizationResult(
        path=source_path,
        changed=changed,
        backup_path=backup_path,
        task_id=task.task_id,
        asset=task.asset,
    )


def normalize_task_payload(payload: dict[str, Any], *, source_path: Path) -> dict[str, Any]:
    task_id = _extract_task_id(payload, source_path)
    prompt_sources = _normalize_prompt_sources(payload, task_id=task_id, source_path=source_path)
    environment = _normalize_environment(payload, task_id=task_id)

    normalized: dict[str, Any] = {
        "id": task_id,
        "name": str(payload.get("name") or task_id),
    }

    description = payload.get("description")
    if isinstance(description, str) and description.strip():
        normalized["description"] = description.strip()

    normalized["prompts"] = prompt_sources
    normalized["environment"] = environment
    normalized["skills"] = _normalize_skills(payload.get("skills"))
    normalized["runtime"] = _normalize_runtime(payload.get("runtime"))

    for key, value in payload.items():
        if key in normalized:
            continue
        if key in REMOVED_TOP_LEVEL_KEYS or key == "environment":
            continue
        if value in (None, "", [], {}):
            continue
        normalized[key] = value

    return normalized


def _extract_task_id(payload: dict[str, Any], source_path: Path) -> str:
    raw = payload.get("id")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return source_path.stem


def _normalize_prompt_sources(
    payload: dict[str, Any],
    *,
    task_id: str,
    source_path: Path,
) -> list[Any] | dict[str, list[str]]:
    prompts = payload.get("prompts")
    if prompts is not None:
        if isinstance(prompts, str):
            stripped = prompts.strip()
            if stripped:
                return [stripped]
        if isinstance(prompts, list) and prompts:
            return prompts
        if isinstance(prompts, dict):
            return prompts

    sessions = payload.get("sessions")
    if isinstance(sessions, list):
        session_prompts: list[str] = []
        for item in sessions:
            if not isinstance(item, dict):
                continue
            prompt = item.get("prompt")
            if isinstance(prompt, str) and prompt.strip():
                session_prompts.append(_normalize_prompt_reference(prompt))
        if session_prompts:
            return session_prompts

    legacy_task = payload.get("task")
    if isinstance(legacy_task, dict):
        task_file = legacy_task.get("task_file")
        if isinstance(task_file, str) and task_file.strip():
            return [task_file.strip()]
        inline_prompt = legacy_task.get("prompt")
        if isinstance(inline_prompt, str) and inline_prompt.strip():
            return {"inline": [inline_prompt.rstrip()]}

    prompt_path = source_path.parent / "prompts" / f"{task_id}.md"
    if prompt_path.exists():
        return [f"prompts/{task_id}.md"]

    raise FileNotFoundError(
        f"Unable to infer prompt source for {source_path}; expected {prompt_path}"
    )


def _normalize_prompt_reference(value: str) -> str:
    normalized = value.strip().replace("tasks/prompts/", "prompts/")
    if "/" not in normalized and Path(normalized).suffix.lower() != ".md":
        return f"prompts/{normalized}.md"
    return normalized


def _normalize_environment(payload: dict[str, Any], *, task_id: str) -> dict[str, Any]:
    env_raw = payload.get("environment")
    env = env_raw if isinstance(env_raw, dict) else {}
    asset = _extract_asset_name(payload, env, task_id=task_id)
    normalized_env: dict[str, Any] = {"asset": asset}

    workspace_context_files = env.get("workspace_context_files")
    if isinstance(workspace_context_files, list):
        filtered = [
            item.strip()
            for item in workspace_context_files
            if isinstance(item, str) and item.strip()
        ]
        if filtered:
            normalized_env["workspace_context_files"] = filtered
    elif isinstance(workspace_context_files, str) and workspace_context_files.strip():
        normalized_env["workspace_context_files"] = [workspace_context_files.strip()]

    return normalized_env


def _normalize_skills(raw_skills: Any) -> dict[str, Any]:
    normalized: dict[str, Any] = {"available": None}

    if isinstance(raw_skills, dict):
        available = raw_skills.get("available")
        if available not in (None, "", [], {}):
            normalized["available"] = available
        include = raw_skills.get("include")
        if include not in (None, "", [], {}):
            normalized["include"] = include
        auto = raw_skills.get("auto")
        if auto not in (None, "", [], {}):
            normalized["auto"] = auto
        return normalized

    if isinstance(raw_skills, str) and raw_skills.strip():
        normalized["include"] = [raw_skills.strip()]
        return normalized

    if isinstance(raw_skills, list) and raw_skills:
        normalized["include"] = raw_skills
        return normalized

    return normalized


def _normalize_runtime(raw_runtime: Any) -> dict[str, Any]:
    normalized = dict(DEFAULT_RUNTIME)
    if not isinstance(raw_runtime, dict):
        return normalized

    for key in SUPPORTED_RUNTIME_KEYS:
        value = raw_runtime.get(key)
        if value in (None, "", [], {}):
            continue
        normalized[key] = value
    return normalized


def _extract_asset_name(payload: dict[str, Any], env: dict[str, Any], *, task_id: str) -> str:
    for candidate in (
        payload.get("asset"),
        env.get("asset"),
        *_iter_environment_asset_candidates(env.get("assets")),
    ):
        normalized = _normalize_asset_candidate(candidate, task_id=task_id)
        if normalized:
            return normalized
    return task_id


def _iter_environment_asset_candidates(raw_assets: Any) -> list[Any]:
    if raw_assets is None:
        return []
    if isinstance(raw_assets, list):
        candidates: list[Any] = []
        for item in raw_assets:
            if isinstance(item, str):
                candidates.append(item)
                continue
            if isinstance(item, dict):
                for key in ("source", "src", "path"):
                    if key in item:
                        candidates.append(item[key])
        return candidates
    return [raw_assets]


def _normalize_asset_candidate(raw_value: Any, *, task_id: str) -> str | None:
    if not isinstance(raw_value, str):
        return None

    value = raw_value.strip().strip("\"'")
    if not value:
        return None

    normalized_path = PurePosixPath(value.rstrip("/"))
    name = normalized_path.name
    stem = normalized_path.stem

    if name == "env_builder.py":
        parent_name = normalized_path.parent.name
        return parent_name if parent_name else task_id

    if "." in name:
        if stem.startswith("data_"):
            return stem
        return task_id

    if name in {"workspace", "/workspace"}:
        return task_id

    if "assets" in normalized_path.parts:
        parts = list(normalized_path.parts)
        index = parts.index("assets")
        if index + 1 < len(parts):
            return parts[index + 1]

    if "/" in value:
        return name or task_id

    return value


def _dump_yaml(payload: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    )
    return dumped.replace("  available: null\n", "  available:\n")
