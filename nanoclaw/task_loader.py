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
    max_steps: int
    temperature: float


@dataclass(frozen=True, slots=True)
class TaskDefinition:
    source_path: Path
    source_text: str
    task_id: str
    name: str
    description: str | None
    asset: str
    prompt: str
    prompt_source: str | None
    runtime: TaskRuntime

    def resolved_payload(self) -> dict[str, Any]:
        return {
            "id": self.task_id,
            "name": self.name,
            "description": self.description,
            "asset": self.asset,
            "task": {
                "prompt": self.prompt,
                "task_file": self.prompt_source,
            },
            "runtime": {
                "model": self.runtime.model,
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
                        value, index = self._parse_mapping(child_line, child_indent)

            payload[key] = value

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


def load_task_definition(task_path: Path, settings: Settings) -> TaskDefinition:
    source_path = task_path.expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_path}")

    source_text = source_path.read_text(encoding="utf-8")
    payload = _load_yaml_mapping(source_text)

    task_id = _optional_string(payload.get("id"), "id") or source_path.stem
    name = _optional_string(payload.get("name"), "name") or task_id
    description = _optional_string(payload.get("description"), "description")
    asset = _optional_string(payload.get("asset"), "asset") or "empty"

    task_block = _require_mapping(payload.get("task"), "task")
    prompt_inline = _optional_string(task_block.get("prompt"), "task.prompt")
    prompt_file_raw = _optional_string(task_block.get("task_file"), "task.task_file")

    if bool(prompt_inline) == bool(prompt_file_raw):
        raise ValueError("Task must define exactly one of 'task.prompt' or 'task.task_file'")

    prompt_source: str | None = None
    if prompt_file_raw:
        prompt_path = (source_path.parent / prompt_file_raw).resolve()
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Task prompt file not found: {prompt_file_raw} ({prompt_path})"
            )
        prompt = prompt_path.read_text(encoding="utf-8")
        prompt_source = str(prompt_path)
    else:
        prompt = prompt_inline or ""

    runtime_block_raw = payload.get("runtime")
    runtime_block = (
        _require_mapping(runtime_block_raw, "runtime")
        if runtime_block_raw is not None
        else {}
    )

    runtime = TaskRuntime(
        model=_optional_string(runtime_block.get("model"), "runtime.model")
        or settings.model,
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
        prompt_source=prompt_source,
        runtime=runtime,
    )


def list_task_files(tasks_dir: Path) -> tuple[Path, ...]:
    root = tasks_dir.expanduser()
    if not root.exists():
        return ()

    files = {path.resolve() for path in root.rglob("*.yaml")}
    files.update(path.resolve() for path in root.rglob("*.yml"))
    return tuple(sorted(files))
