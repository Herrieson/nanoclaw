from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_PROMPT_FILES = ("CLAUDE.md", "AGENTS.md")


def _split_csv(raw: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = raw.strip()
    if not value:
        return default
    items = [item.strip() for item in value.split(",")]
    filtered = [item for item in items if item]
    return tuple(filtered) if filtered else default


@dataclass(frozen=True, slots=True)
class Settings:
    model: str
    api_key: str | None
    base_url: str | None
    workspace_dir: Path
    prompt_dir: Path
    prompt_files: tuple[str, ...]
    max_steps: int
    temperature: float

    @classmethod
    def from_env(cls) -> "Settings":
        workspace_dir = Path(
            os.getenv("NANOCLAW_WORKSPACE_DIR", "workspace")
        ).expanduser()
        prompt_dir_env = os.getenv("NANOCLAW_PROMPT_DIR")
        prompt_dir = (
            Path(prompt_dir_env).expanduser()
            if prompt_dir_env
            else workspace_dir / "prompts" / "official"
        )
        prompt_files = _split_csv(
            os.getenv("NANOCLAW_PROMPT_FILES", ",".join(DEFAULT_PROMPT_FILES)),
            DEFAULT_PROMPT_FILES,
        )

        return cls(
            model=os.getenv("NANOCLAW_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("NANOCLAW_BASE_URL"),
            workspace_dir=workspace_dir,
            prompt_dir=prompt_dir,
            prompt_files=prompt_files,
            max_steps=int(os.getenv("NANOCLAW_MAX_STEPS", "15")),
            temperature=float(os.getenv("NANOCLAW_TEMPERATURE", "0.2")),
        )
