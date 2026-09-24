from __future__ import annotations

import difflib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_MEMORY_FILE = "MEMORY.md"
DAILY_MEMORY_DIR = "memory"
MAX_MEMORY_MATCHES = 200
TOKEN_PATTERN = re.compile(r"[a-z0-9]{3,}")


@dataclass(frozen=True, slots=True)
class MemoryMatch:
    path: str
    line: int
    text: str
    score: int


def today_memory_filename(*, now: datetime | None = None) -> str:
    current = now or datetime.now().astimezone()
    return f"{DAILY_MEMORY_DIR}/{current.strftime('%Y-%m-%d')}.md"


def bootstrap_memory_files(workspace_dir: Path) -> None:
    memory_dir = workspace_dir / DAILY_MEMORY_DIR
    memory_dir.mkdir(parents=True, exist_ok=True)

    daily_path = workspace_dir / today_memory_filename()
    if not daily_path.exists():
        daily_path.write_text(
            "# Daily Memory\n\n- Capture raw notes, decisions, and follow-ups here.\n",
            encoding="utf-8",
        )


def resolve_memory_path(workspace_dir: Path, raw_path: str) -> Path:
    relative_path = raw_path.strip()
    if not relative_path:
        raise ValueError("Memory path cannot be empty")

    normalized = Path(relative_path).as_posix()
    if normalized != DEFAULT_MEMORY_FILE and not normalized.startswith(f"{DAILY_MEMORY_DIR}/"):
        raise ValueError(
            "Memory path must be MEMORY.md or a file under memory/"
        )

    candidate = (workspace_dir / normalized).resolve()
    workspace = workspace_dir.resolve()
    if candidate != workspace and workspace not in candidate.parents:
        raise ValueError(f"Memory path escapes workspace: {raw_path}")
    return candidate


def iter_memory_paths(workspace_dir: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    long_term = workspace_dir / DEFAULT_MEMORY_FILE
    if long_term.exists() and long_term.is_file():
        paths.append(long_term)

    daily_dir = workspace_dir / DAILY_MEMORY_DIR
    if daily_dir.exists() and daily_dir.is_dir():
        paths.extend(
            path
            for path in sorted(daily_dir.rglob("*.md"))
            if path.is_file()
        )

    return tuple(paths)


def search_memory(
    workspace_dir: Path,
    query: str,
    *,
    limit: int = MAX_MEMORY_MATCHES,
) -> str:
    needle = query.strip().lower()
    if not needle:
        raise ValueError("Memory search query cannot be empty")
    query_tokens = _tokenize(needle)

    matches: list[MemoryMatch] = []
    for path in iter_memory_paths(workspace_dir):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, line in enumerate(lines, start=1):
            score = _memory_match_score(query=needle, query_tokens=query_tokens, line=line)
            if score <= 0:
                continue
            matches.append(
                MemoryMatch(
                    path=_relative_workspace_path(workspace_dir, path),
                    line=line_number,
                    text=line,
                    score=score,
                )
            )

    matches.sort(key=lambda match: (-match.score, match.path, match.line))
    truncated = len(matches) > limit
    matches = matches[:limit]

    return json.dumps(
        {
            "query": query,
            "matches": [asdict(match) for match in matches],
            "truncated": truncated,
        },
        indent=2,
        ensure_ascii=False,
    )


def get_memory_slice(
    workspace_dir: Path,
    raw_path: str,
    start_line: int,
    end_line: int,
) -> str:
    path = resolve_memory_path(workspace_dir, raw_path)
    if start_line < 1 or end_line < start_line:
        raise ValueError("Invalid line range")
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return f"{Path(raw_path).as_posix()}: empty file"

    if start_line > len(lines):
        raise ValueError(
            f"Start line {start_line} is beyond end of file ({len(lines)} lines)"
        )

    actual_end = min(end_line, len(lines))
    selected = [
        f"{line_number}: {lines[line_number - 1]}"
        for line_number in range(start_line, actual_end + 1)
    ]
    return "\n".join(
        [
            f"{Path(raw_path).as_posix()}:{start_line}-{actual_end}",
            *selected,
        ]
    )


def append_memory(workspace_dir: Path, raw_path: str, content: str) -> str:
    path = resolve_memory_path(workspace_dir, raw_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    prefix = ""
    if existing and not existing.endswith("\n"):
        prefix = "\n"
    elif existing:
        prefix = ""

    path.write_text(existing + prefix + content, encoding="utf-8")
    return f"Success: Appended to {Path(raw_path).as_posix()}."


def _relative_workspace_path(workspace_dir: Path, path: Path) -> str:
    return str(path.relative_to(workspace_dir)).replace("\\", "/")


def _tokenize(value: str) -> tuple[str, ...]:
    return tuple(TOKEN_PATTERN.findall(value.lower()))


def _memory_match_score(*, query: str, query_tokens: tuple[str, ...], line: str) -> int:
    lowered_line = line.lower()
    if query in lowered_line:
        return 100

    line_tokens = _tokenize(lowered_line)
    if not query_tokens or not line_tokens:
        return 0

    matched_tokens = 0
    for query_token in query_tokens:
        if any(_tokens_match(query_token, line_token) for line_token in line_tokens):
            matched_tokens += 1

    minimum_matches = 2 if len(query_tokens) >= 2 else 1
    if matched_tokens < minimum_matches:
        return 0

    return matched_tokens


def _tokens_match(left: str, right: str) -> bool:
    if left == right:
        return True
    if len(left) >= 4 and len(right) >= 4:
        if left.startswith(right[:4]) or right.startswith(left[:4]):
            return True
    return difflib.SequenceMatcher(a=left, b=right).ratio() >= 0.75
