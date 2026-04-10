from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SESSIONS_DIRNAME = "sessions"


def validate_session_id(session_id: str) -> str:
    normalized = session_id.strip()
    if not normalized:
        raise ValueError("Session id cannot be empty")
    if not SESSION_ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Session id must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}"
        )
    return normalized


def load_session_messages(
    workspace_dir: Path,
    session_id: str,
    *,
    max_messages: int,
    max_chars: int,
) -> tuple[dict[str, str], ...]:
    path = session_path(workspace_dir, session_id)
    if not path.exists():
        return ()

    loaded: list[dict[str, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if not isinstance(payload, dict):
            continue
        role = payload.get("role")
        content = payload.get("content")
        if role not in {"user", "assistant"}:
            continue
        if not isinstance(content, str) or not content:
            continue
        loaded.append({"role": role, "content": content})

    return tuple(_trim_messages(loaded, max_messages=max_messages, max_chars=max_chars))


def append_session_message(
    workspace_dir: Path,
    session_id: str,
    *,
    role: str,
    content: str,
    result_type: str | None = None,
) -> None:
    normalized_session_id = validate_session_id(session_id)
    if role not in {"user", "assistant"}:
        raise ValueError(f"Unsupported session role: {role}")
    if not content:
        return

    path = session_path(workspace_dir, normalized_session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "role": role,
        "content": content,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if result_type is not None:
        payload["result_type"] = result_type

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def session_path(workspace_dir: Path, session_id: str) -> Path:
    normalized = validate_session_id(session_id)
    return workspace_dir / SESSIONS_DIRNAME / f"{normalized}.jsonl"


def _trim_messages(
    messages: list[dict[str, str]],
    *,
    max_messages: int,
    max_chars: int,
) -> list[dict[str, str]]:
    trimmed = list(messages)
    if max_messages > 0 and len(trimmed) > max_messages:
        trimmed = trimmed[-max_messages:]

    if max_chars <= 0:
        return trimmed

    total = 0
    collected: list[dict[str, str]] = []
    for message in reversed(trimmed):
        message_len = len(message["content"])
        if collected and total + message_len > max_chars:
            break
        collected.append(message)
        total += message_len

    return list(reversed(collected))
