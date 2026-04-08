from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
except ModuleNotFoundError:
    _yaml = None


_TOKEN_PATTERN = re.compile(r"[a-z0-9]{4,}")
_NORMALIZE_PATTERN = re.compile(r"[^a-z0-9]+")
_STOPWORDS = frozenset(
    {
        "about",
        "after",
        "agent",
        "analysis",
        "brief",
        "create",
        "draft",
        "follow",
        "from",
        "have",
        "into",
        "keep",
        "make",
        "need",
        "notes",
        "plain",
        "prepare",
        "review",
        "task",
        "that",
        "their",
        "them",
        "then",
        "this",
        "with",
        "work",
        "write",
    }
)


@dataclass(frozen=True, slots=True)
class SkillDefinition:
    slug: str
    name: str
    description: str
    instructions: str
    source_path: Path
    root_dir: Path
    checksum: str


@dataclass(frozen=True, slots=True)
class SkillLoadError:
    source_path: Path
    error: str


@dataclass(frozen=True, slots=True)
class SkillCatalog:
    roots: tuple[Path, ...]
    skills: tuple[SkillDefinition, ...]
    errors: tuple[SkillLoadError, ...]


def discover_skills(
    workspace_dir: Path,
    extra_dirs: tuple[Path, ...] = (),
) -> SkillCatalog:
    roots = _skill_roots(workspace_dir, extra_dirs)
    discovered: list[SkillDefinition] = []
    errors: list[SkillLoadError] = []
    seen_slugs: set[str] = set()

    for root in roots:
        if not root.exists() or not root.is_dir():
            continue

        for skill_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists() or not skill_file.is_file():
                continue

            try:
                skill = _load_skill(skill_file, root)
            except Exception as exc:
                errors.append(
                    SkillLoadError(source_path=skill_file, error=f"{type(exc).__name__}: {exc}")
                )
                continue

            if skill.slug in seen_slugs:
                continue

            seen_slugs.add(skill.slug)
            discovered.append(skill)

    return SkillCatalog(
        roots=roots,
        skills=tuple(discovered),
        errors=tuple(errors),
    )


def resolve_requested_skills(
    skills: tuple[SkillDefinition, ...],
    requested_names: tuple[str, ...],
) -> tuple[SkillDefinition, ...]:
    if not requested_names:
        return ()

    resolved: list[SkillDefinition] = []
    seen: set[str] = set()

    for requested in requested_names:
        skill = _find_skill(skills, requested)
        if skill is None:
            available = ", ".join(sorted(skill.slug for skill in skills)) or "(none)"
            raise ValueError(
                f"Unknown skill '{requested}'. Available skills: {available}"
            )
        if skill.slug in seen:
            continue
        seen.add(skill.slug)
        resolved.append(skill)

    return tuple(resolved)


def auto_select_skills(
    skills: tuple[SkillDefinition, ...],
    task_text: str,
) -> tuple[SkillDefinition, ...]:
    normalized_task = _normalize_text(task_text)
    task_tokens = set(_TOKEN_PATTERN.findall(normalized_task))
    selected: list[SkillDefinition] = []

    for skill in skills:
        aliases = {
            _normalize_text(skill.slug),
            _normalize_text(skill.name),
        }
        if any(alias and alias in normalized_task for alias in aliases):
            selected.append(skill)
            continue

        skill_tokens = {
            token
            for token in _TOKEN_PATTERN.findall(
                _normalize_text(f"{skill.name} {skill.description}")
            )
            if token not in _STOPWORDS
        }
        if len(skill_tokens & task_tokens) >= 2:
            selected.append(skill)

    return tuple(selected)


def serialize_skill(skill: SkillDefinition) -> dict[str, str]:
    return {
        "slug": skill.slug,
        "name": skill.name,
        "description": skill.description,
        "source_path": str(skill.source_path),
        "checksum": skill.checksum,
    }


def _skill_roots(workspace_dir: Path, extra_dirs: tuple[Path, ...]) -> tuple[Path, ...]:
    ordered = [
        workspace_dir.expanduser().resolve() / ".agents" / "skills",
        Path("skills").expanduser().resolve(),
        *(path.expanduser().resolve() for path in extra_dirs),
    ]
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in ordered:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)
    return tuple(deduped)


def _load_skill(path: Path, root_dir: Path) -> SkillDefinition:
    raw = path.read_text(encoding="utf-8")
    metadata, instructions = _split_frontmatter(raw)
    slug = path.parent.name

    name_raw = metadata.get("name", slug)
    description_raw = metadata.get("description")
    if not isinstance(name_raw, str) or not name_raw.strip():
        raise ValueError("Skill frontmatter must define a non-empty 'name'")
    if not isinstance(description_raw, str) or not description_raw.strip():
        raise ValueError("Skill frontmatter must define a non-empty 'description'")

    body = instructions.strip()
    if not body:
        raise ValueError("Skill instructions are empty")

    return SkillDefinition(
        slug=slug,
        name=name_raw.strip(),
        description=description_raw.strip(),
        instructions=body,
        source_path=path.resolve(),
        root_dir=root_dir.resolve(),
        checksum=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        raise ValueError("Skill file must start with YAML frontmatter")

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Skill file must start with YAML frontmatter")

    for index in range(1, len(lines)):
        if lines[index].strip() != "---":
            continue
        frontmatter = "\n".join(lines[1:index])
        body = "\n".join(lines[index + 1 :])
        return _load_frontmatter_mapping(frontmatter), body

    raise ValueError("Skill frontmatter is missing a closing '---' line")


def _load_frontmatter_mapping(content: str) -> dict[str, Any]:
    if _yaml is not None:
        payload = _yaml.safe_load(content)
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise ValueError("Skill frontmatter must be a mapping")
        return payload

    payload: dict[str, Any] = {}
    for index, raw_line in enumerate(content.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(
                f"Unsupported frontmatter line {index}: {raw_line}"
            )
        key, raw_value = stripped.split(":", 1)
        payload[key.strip()] = _parse_scalar(raw_value.strip())
    return payload


def _parse_scalar(raw: str) -> Any:
    if not raw:
        return ""
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1]
    if len(raw) >= 2 and raw[0] == raw[-1] == "'":
        return raw[1:-1]
    return raw


def _normalize_text(value: str) -> str:
    normalized = _NORMALIZE_PATTERN.sub(" ", value.lower()).strip()
    return re.sub(r"\s+", " ", normalized)


def _find_skill(
    skills: tuple[SkillDefinition, ...],
    requested_name: str,
) -> SkillDefinition | None:
    wanted = _normalize_text(requested_name)
    if not wanted:
        return None

    for skill in skills:
        identifiers = {
            _normalize_text(skill.slug),
            _normalize_text(skill.name),
        }
        if wanted in identifiers:
            return skill

    return None
