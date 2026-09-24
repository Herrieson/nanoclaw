from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
except ModuleNotFoundError:
    _yaml = None


DEFAULT_DOCKER_COMMAND = (
    "/opt/nanoclaw-adapter/run_task",
    "--task",
    "/input/task.md",
    "--resolved-task",
    "/input/resolved_task.json",
    "--workspace",
    "/workspace",
    "--output",
    "/output",
    "--state",
    "/state",
)


@dataclass(frozen=True, slots=True)
class RunnerProfile:
    profile_id: str
    runner_type: str
    source_path: Path | None = None
    image: str | None = None
    command: tuple[str, ...] = ()
    docker_executable: str = "docker"
    workdir: str | None = "/workspace"
    network: str | None = None
    timeout_seconds: float = 900.0
    remove_container: bool = True
    env_pass: tuple[str, ...] = ()
    env_set: dict[str, str] = field(default_factory=dict)
    cpus: str | None = None
    memory: str | None = None
    pids_limit: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def nanoclaw(cls) -> "RunnerProfile":
        return cls(profile_id="nanoclaw", runner_type="nanoclaw")


def load_runner_profile(path: str | Path | None) -> RunnerProfile:
    if path is None:
        return RunnerProfile.nanoclaw()

    source_path = Path(path).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Runner profile not found: {source_path}")

    payload = _load_profile_payload(source_path)
    profile_id = _optional_string(payload.get("id"), "id") or source_path.stem
    runner_type = (_optional_string(payload.get("type"), "type") or "").lower()
    if not runner_type:
        runner_type = "docker" if payload.get("image") else "nanoclaw"

    if runner_type == "nanoclaw":
        return RunnerProfile(
            profile_id=profile_id,
            runner_type="nanoclaw",
            source_path=source_path,
            raw=payload,
        )

    if runner_type != "docker":
        raise ValueError(f"Unsupported runner profile type: {runner_type}")

    image = _optional_string(payload.get("image"), "image")
    if not image:
        raise ValueError("Docker runner profile must define a non-empty 'image'")

    env_block = _mapping(payload.get("env"), "env")
    resources_block = _mapping(payload.get("resources"), "resources")

    command = _string_tuple(payload.get("command"), "command") or DEFAULT_DOCKER_COMMAND
    env_pass = _string_tuple(env_block.get("pass"), "env.pass")
    env_set = {
        str(key): str(value)
        for key, value in _mapping(env_block.get("set"), "env.set").items()
    }

    timeout_seconds = float(payload.get("timeout_seconds", 900.0))
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    pids_limit_raw = resources_block.get("pids_limit")
    pids_limit = int(pids_limit_raw) if pids_limit_raw is not None else None

    return RunnerProfile(
        profile_id=profile_id,
        runner_type="docker",
        source_path=source_path,
        image=image,
        command=command,
        docker_executable=_optional_string(
            payload.get("docker_executable"),
            "docker_executable",
        )
        or "docker",
        workdir=_optional_string(payload.get("workdir"), "workdir") or "/workspace",
        network=_optional_string(payload.get("network"), "network"),
        timeout_seconds=timeout_seconds,
        remove_container=bool(payload.get("remove_container", True)),
        env_pass=env_pass,
        env_set=env_set,
        cpus=_optional_string(resources_block.get("cpus"), "resources.cpus"),
        memory=_optional_string(resources_block.get("memory"), "resources.memory"),
        pids_limit=pids_limit,
        raw=payload,
    )


def _load_profile_payload(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if _yaml is not None:
        payload = _yaml.safe_load(raw) or {}
    else:
        payload = _simple_yaml_mapping(raw)
    if not isinstance(payload, dict):
        raise ValueError(f"Runner profile must be a mapping: {path}")
    return payload


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    stripped = value.strip()
    return stripped or None


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        items: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"{field_name} entries must be strings")
            stripped = item.strip()
            if stripped:
                items.append(stripped)
        return tuple(items)
    raise ValueError(f"{field_name} must be a string or list of strings")


def _simple_yaml_mapping(raw: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported profile YAML at line {line_number}: {raw_line}")
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip("\"'")
    return payload
