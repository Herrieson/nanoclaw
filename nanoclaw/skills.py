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
    aliases: tuple[str, ...]
    requires: tuple[str, ...]
    homepage: str | None
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
    best_skill: SkillDefinition | None = None
    best_score = 0

    for skill in skills:
        score = _auto_skill_score(
            skill=skill,
            normalized_task=normalized_task,
            task_tokens=task_tokens,
        )
        if score <= 0:
            continue
        if score > best_score:
            best_skill = skill
            best_score = score
            continue
        if score == best_score and best_skill is not None:
            if skill.slug < best_skill.slug:
                best_skill = skill

    if best_skill is None:
        return ()
    return (best_skill,)


def serialize_skill(skill: SkillDefinition) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "slug": skill.slug,
        "name": skill.name,
        "description": skill.description,
        "source_path": str(skill.source_path),
        "checksum": skill.checksum,
    }
    if skill.aliases:
        payload["aliases"] = list(skill.aliases)
    if skill.requires:
        payload["requires"] = list(skill.requires)
    if skill.homepage:
        payload["homepage"] = skill.homepage
    return payload


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
    aliases = _string_tuple(metadata.get("aliases"), "aliases")
    requires = _string_tuple(metadata.get("requires"), "requires")
    homepage = _optional_string(metadata.get("homepage"), "homepage")
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
        aliases=aliases,
        requires=requires,
        homepage=homepage.strip() if homepage and homepage.strip() else None,
        instructions=body,
        source_path=path.resolve(),
        root_dir=root_dir.resolve(),
        checksum=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )


def _auto_skill_score(
    *,
    skill: SkillDefinition,
    normalized_task: str,
    task_tokens: set[str],
) -> int:
    score = 0
    aliases = {
        _normalize_text(skill.slug),
        _normalize_text(skill.name),
        *(_normalize_text(alias) for alias in skill.aliases),
    }
    for alias in aliases:
        if not alias:
            continue
        if alias == normalized_task:
            score += 100
            continue
        if alias in normalized_task:
            score += 20

    skill_tokens = {
        token
        for token in _TOKEN_PATTERN.findall(
            _normalize_text(f"{skill.name} {skill.description}")
        )
        if token not in _STOPWORDS
    }
    overlap = len(skill_tokens & task_tokens)
    if overlap >= 2:
        score += overlap

    return score


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
    lines = content.splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        index += 1
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(
                f"Unsupported frontmatter line {index}: {raw_line}"
            )
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value:
            payload[key] = _parse_scalar(value)
            continue

        collected: list[str] = []
        while index < len(lines):
            child_raw = lines[index]
            child_stripped = child_raw.strip()
            if not child_stripped or child_stripped.startswith("#"):
                index += 1
                continue
            if not child_raw.startswith((" ", "\t")):
                break
            if not child_stripped.startswith("- "):
                raise ValueError(
                    f"Unsupported frontmatter line {index + 1}: {child_raw}"
                )
            collected.append(_parse_scalar(child_stripped[2:].strip()))
            index += 1

        payload[key] = collected
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


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Skill frontmatter field '{field_name}' must be a string")
    return value


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if not isinstance(value, list):
        raise ValueError(
            f"Skill frontmatter field '{field_name}' must be a string or list of strings"
        )

    collected: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(
                f"Skill frontmatter field '{field_name}' must contain only strings"
            )
        stripped = item.strip()
        if stripped:
            collected.append(stripped)
    return tuple(collected)


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
            *(_normalize_text(alias) for alias in skill.aliases),
        }
        if wanted in identifiers:
            return skill

    return None
