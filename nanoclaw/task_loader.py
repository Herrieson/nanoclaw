from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Settings

try:
    import yaml as _yaml
except ModuleNotFoundError:
    _yaml = None


_INT_PATTERN = re.compile(r"^-?\d+$")
_FLOAT_PATTERN = re.compile(r"^-?(?:\d+\.\d+|\d+\.\d*|\.\d+)$")


@dataclass(frozen=True, slots=True)
class TaskRuntime:
    model: str
    mode: str
    session: str | None
    memory_policy: str
    workspace_context_files: tuple[str, ...]
    max_steps: int
    temperature: float


@dataclass(frozen=True, slots=True)
class TaskSkills:
    available: tuple[str, ...]
    include: tuple[str, ...]
    auto: bool


@dataclass(frozen=True, slots=True)
class TaskDefinition:
    source_path: Path
    source_text: str
    task_id: str
    name: str
    description: str | None
    asset: str
    prompt: str
    prompt_sources: tuple[str, ...]
    skills: TaskSkills
    runtime: TaskRuntime

    def resolved_payload(
        self,
        *,
        activated_skills: tuple[dict[str, Any], ...] = (),
    ) -> dict[str, Any]:
        return {
            "id": self.task_id,
            "name": self.name,
            "description": self.description,
            "asset": self.asset,
            "prompts": {
                "sources": list(self.prompt_sources),
                "prompt": self.prompt,
            },
            "environment": {
                "asset": self.asset,
                "workspace_context_files": list(self.runtime.workspace_context_files),
            },
            "skills": {
                "available": list(self.skills.available),
                "include": list(self.skills.include),
                "auto": self.skills.auto,
                "activated": list(activated_skills),
            },
            "runtime": {
                "model": self.runtime.model,
                "mode": self.runtime.mode,
                "session": self.runtime.session,
                "memory_policy": self.runtime.memory_policy,
                "max_steps": self.runtime.max_steps,
                "temperature": self.runtime.temperature,
            },
            "source_path": str(self.source_path),
        }


class _SimpleYamlParser:
    def __init__(self, content: str) -> None:
        self.lines = content.splitlines()

    def parse(self) -> dict[str, Any]:
        payload, next_index = self._parse_mapping(0, 0)
        trailing = self._next_significant_line(next_index)
        if trailing is not None:
            raise ValueError(
                f"Unexpected trailing content at line {trailing + 1}: {self.lines[trailing]}"
            )
        return payload

    def _next_significant_line(self, start: int) -> int | None:
        for index in range(start, len(self.lines)):
            stripped = self.lines[index].lstrip(" ")
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            return index
        return None

    def _line_info(self, index: int) -> tuple[int, str]:
        raw = self.lines[index]
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        return indent, stripped

    def _parse_mapping(
        self, start: int, expected_indent: int
    ) -> tuple[dict[str, Any], int]:
        payload: dict[str, Any] = {}
        index = start

        while True:
            current = self._next_significant_line(index)
            if current is None:
                return payload, len(self.lines)

            indent, stripped = self._line_info(current)
            if indent < expected_indent:
                return payload, current
            if indent > expected_indent:
                raise ValueError(
                    f"Unexpected indentation at line {current + 1}: {self.lines[current]}"
                )

            if ":" not in stripped:
                raise ValueError(
                    f"Expected 'key: value' at line {current + 1}: {self.lines[current]}"
                )

            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if not key:
                raise ValueError(f"Empty key at line {current + 1}")

            index = current + 1

            if raw_value in {"|", ">"}:
                value, index = self._parse_block_scalar(
                    index, parent_indent=indent, folded=raw_value == ">"
                )
            elif raw_value:
                value = _parse_scalar(raw_value)
            else:
                child_line = self._next_significant_line(index)
                if child_line is None:
                    value = {}
                else:
                    child_indent, _ = self._line_info(child_line)
                    if child_indent <= indent:
                        value = {}
                    else:
                        value, index = self._parse_node(child_line, child_indent)

            payload[key] = value

    def _parse_node(self, start: int, expected_indent: int) -> tuple[Any, int]:
        current = self._next_significant_line(start)
        if current is None:
            return {}, len(self.lines)

        _, stripped = self._line_info(current)
        if stripped == "-" or stripped.startswith("- "):
            return self._parse_sequence(start, expected_indent)
        return self._parse_mapping(start, expected_indent)

    def _parse_sequence(
        self, start: int, expected_indent: int
    ) -> tuple[list[Any], int]:
        payload: list[Any] = []
        index = start

        while True:
            current = self._next_significant_line(index)
            if current is None:
                return payload, len(self.lines)

            indent, stripped = self._line_info(current)
            if indent < expected_indent:
                return payload, current
            if indent > expected_indent:
                raise ValueError(
                    f"Unexpected indentation at line {current + 1}: {self.lines[current]}"
                )
            if stripped != "-" and not stripped.startswith("- "):
                return payload, current

            raw_value = stripped[1:].strip()
            index = current + 1

            if raw_value:
                value = _parse_scalar(raw_value)
            else:
                child_line = self._next_significant_line(index)
                if child_line is None:
                    value = {}
                else:
                    child_indent, _ = self._line_info(child_line)
                    if child_indent <= indent:
                        value = {}
                    else:
                        value, index = self._parse_node(child_line, child_indent)

            payload.append(value)

    def _parse_block_scalar(
        self, start: int, parent_indent: int, *, folded: bool
    ) -> tuple[str, int]:
        first = self._next_significant_line(start)
        if first is None:
            return "", start

        first_indent, _ = self._line_info(first)
        if first_indent <= parent_indent:
            return "", start

        block_indent = first_indent
        collected: list[str] = []
        index = start

        while index < len(self.lines):
            raw = self.lines[index]
            stripped = raw.lstrip(" ")
            indent = len(raw) - len(stripped)

            if stripped and not stripped.startswith("#") and indent < block_indent:
                break

            if not stripped:
                collected.append("")
                index += 1
                continue

            if indent < block_indent:
                break

            collected.append(raw[block_indent:])
            index += 1

        if not folded:
            return "\n".join(collected).rstrip(), index

        paragraphs: list[str] = []
        current: list[str] = []
        for line in collected:
            if line:
                current.append(line)
                continue
            if current:
                paragraphs.append(" ".join(current))
                current = []
            else:
                paragraphs.append("")
        if current:
            paragraphs.append(" ".join(current))

        return "\n\n".join(paragraphs).rstrip(), index


def _parse_scalar(raw: str) -> Any:
    value = raw
    if value and value[0] not in {"'", '"'}:
        comment_index = value.find(" #")
        if comment_index != -1:
            value = value[:comment_index].rstrip()

    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    if _INT_PATTERN.fullmatch(value):
        return int(value)
    if _FLOAT_PATTERN.fullmatch(value):
        return float(value)
    return value


def _load_yaml_mapping(content: str) -> dict[str, Any]:
    if _yaml is not None:
        payload = _yaml.safe_load(content)
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise ValueError("Task YAML must contain a top-level mapping")
        return payload

    return _SimpleYamlParser(content).parse()


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Field '{field_name}' must be a mapping")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Field '{field_name}' must be a string")
    return value


def _optional_bool(value: Any, field_name: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"Field '{field_name}' must be a boolean")
    return value


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if not isinstance(value, list):
        raise ValueError(f"Field '{field_name}' must be a string or list of strings")

    collected: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Field '{field_name}' must contain only strings")
        stripped = item.strip()
        if stripped:
            collected.append(stripped)
    return tuple(collected)


def _load_task_skills(value: Any) -> TaskSkills:
    if value is None:
        return TaskSkills(available=(), include=(), auto=False)
    if isinstance(value, (str, list)):
        return TaskSkills(
            available=(),
            include=_string_tuple(value, "skills"),
            auto=False,
        )

    mapping = _require_mapping(value, "skills")
    return TaskSkills(
        available=_string_tuple(mapping.get("available"), "skills.available"),
        include=_string_tuple(mapping.get("include"), "skills.include"),
        auto=_optional_bool(mapping.get("auto"), "skills.auto") or False,
    )


def _load_prompt_sources(
    payload: dict[str, Any],
    *,
    source_path: Path,
) -> tuple[str, tuple[str, ...]]:
    legacy_task = payload.get("task")
    prompts_block = payload.get("prompts")

    if legacy_task is not None and prompts_block is not None:
        raise ValueError("Use either top-level 'prompts' or legacy 'task', not both")
    if legacy_task is None and prompts_block is None:
        raise ValueError("Task must define either top-level 'prompts' or legacy 'task'")

    if prompts_block is not None:
        return _load_prompt_bundle(prompts_block, source_path=source_path)

    task_block = _require_mapping(legacy_task, "task")
    prompt_inline = _optional_string(task_block.get("prompt"), "task.prompt")
    prompt_file_raw = _optional_string(task_block.get("task_file"), "task.task_file")
    if bool(prompt_inline) == bool(prompt_file_raw):
        raise ValueError("Task must define exactly one of 'task.prompt' or 'task.task_file'")

    if prompt_file_raw:
        prompt_text, prompt_source = _read_prompt_file(source_path, prompt_file_raw)
        return prompt_text, (prompt_source,)
    return prompt_inline or "", ("<inline>",)


def _load_prompt_bundle(value: Any, *, source_path: Path) -> tuple[str, tuple[str, ...]]:
    if isinstance(value, str):
        prompt_text, prompt_source = _read_prompt_file(source_path, value)
        return prompt_text, (prompt_source,)

    if isinstance(value, list):
        parts: list[str] = []
        sources: list[str] = []
        inline_index = 0
        for index, item in enumerate(value, start=1):
            if isinstance(item, str):
                prompt_text, prompt_source = _read_prompt_file(source_path, item)
                parts.append(prompt_text)
                sources.append(prompt_source)
                continue
            if not isinstance(item, dict):
                raise ValueError(
                    f"Field 'prompts[{index}]' must be a string or mapping"
                )
            file_raw = _optional_string(item.get("file"), f"prompts[{index}].file")
            inline_raw = _optional_string(item.get("inline"), f"prompts[{index}].inline")
            if bool(file_raw) == bool(inline_raw):
                raise ValueError(
                    f"Field 'prompts[{index}]' must define exactly one of 'file' or 'inline'"
                )
            if file_raw:
                prompt_text, prompt_source = _read_prompt_file(source_path, file_raw)
                parts.append(prompt_text)
                sources.append(prompt_source)
                continue
            inline_index += 1
            parts.append(inline_raw or "")
            sources.append(f"<inline:{inline_index}>")

        if not parts:
            raise ValueError("Field 'prompts' cannot be empty")
        return "\n\n".join(part.rstrip() for part in parts if part.strip()), tuple(sources)

    if isinstance(value, dict):
        mapping = _require_mapping(value, "prompts")
        parts: list[str] = []
        sources: list[str] = []
        for file_raw in _string_tuple(mapping.get("files"), "prompts.files"):
            prompt_text, prompt_source = _read_prompt_file(source_path, file_raw)
            parts.append(prompt_text)
            sources.append(prompt_source)
        for index, inline_text in enumerate(
            _string_tuple(mapping.get("inline"), "prompts.inline"),
            start=1,
        ):
            parts.append(inline_text)
            sources.append(f"<inline:{index}>")
        if not parts:
            raise ValueError("Field 'prompts' must contain at least one prompt source")
        return "\n\n".join(part.rstrip() for part in parts if part.strip()), tuple(sources)

    raise ValueError("Field 'prompts' must be a string, list, or mapping")


def _read_prompt_file(source_path: Path, relative_path: str) -> tuple[str, str]:
    prompt_path = (source_path.parent / relative_path).resolve()
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Task prompt file not found: {relative_path} ({prompt_path})"
        )
    return prompt_path.read_text(encoding="utf-8"), str(prompt_path)


def _load_environment(
    payload: dict[str, Any],
) -> tuple[str, tuple[str, ...]]:
    environment_block_raw = payload.get("environment")
    environment_block = (
        _require_mapping(environment_block_raw, "environment")
        if environment_block_raw is not None
        else {}
    )
    asset_root = _optional_string(payload.get("asset"), "asset")
    asset_env = _optional_string(environment_block.get("asset"), "environment.asset")
    if asset_root and asset_env and asset_root != asset_env:
        raise ValueError("Top-level 'asset' and 'environment.asset' must match when both set")

    asset = asset_env or asset_root or "empty"
    workspace_context_files = _string_tuple(
        environment_block.get("workspace_context_files"),
        "environment.workspace_context_files",
    )
    return asset, workspace_context_files


def load_task_definition(task_path: Path, settings: Settings) -> TaskDefinition:
    source_path = task_path.expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_path}")

    source_text = source_path.read_text(encoding="utf-8")
    payload = _load_yaml_mapping(source_text)

    task_id = _optional_string(payload.get("id"), "id") or source_path.stem
    name = _optional_string(payload.get("name"), "name") or task_id
    description = _optional_string(payload.get("description"), "description")
    prompt, prompt_sources = _load_prompt_sources(payload, source_path=source_path)
    asset, environment_workspace_context = _load_environment(payload)
    skills = _load_task_skills(payload.get("skills"))

    runtime_block_raw = payload.get("runtime")
    runtime_block = (
        _require_mapping(runtime_block_raw, "runtime")
        if runtime_block_raw is not None
        else {}
    )

    runtime = TaskRuntime(
        model=_optional_string(runtime_block.get("model"), "runtime.model")
        or settings.model,
        mode=_optional_string(runtime_block.get("mode"), "runtime.mode")
        or settings.run_mode,
        session=_optional_string(runtime_block.get("session"), "runtime.session"),
        memory_policy=_optional_string(
            runtime_block.get("memory_policy"),
            "runtime.memory_policy",
        )
        or settings.memory_policy,
        workspace_context_files=_string_tuple(
            runtime_block.get("workspace_context_files"),
            "runtime.workspace_context_files",
        )
        or environment_workspace_context
        or settings.workspace_context_files,
        max_steps=int(runtime_block.get("max_steps", settings.max_steps)),
        temperature=float(runtime_block.get("temperature", settings.temperature)),
    )

    return TaskDefinition(
        source_path=source_path,
        source_text=source_text,
        task_id=task_id,
        name=name,
        description=description,
        asset=asset,
        prompt=prompt,
        prompt_sources=prompt_sources,
        skills=skills,
        runtime=runtime,
    )


def list_task_files(tasks_dir: Path) -> tuple[Path, ...]:
    root = tasks_dir.expanduser()
    if not root.exists():
        return ()

    files = {path.resolve() for path in root.rglob("*.yaml")}
    files.update(path.resolve() for path in root.rglob("*.yml"))
    return tuple(sorted(files))
