from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import re


CODE_BLOCK_PATTERN = re.compile(r"```(?P<header>[^\n`]*)\n(?P<body>.*?)```", re.DOTALL)
ALLOWED_PATH_PREFIXES = ("tasks/", "skills/", "scripts/", "prompts/")


@dataclass(frozen=True, slots=True)
class UnpackedRecord:
    record_id: str
    record_root: Path
    files_written: int


@dataclass(frozen=True, slots=True)
class _CandidateRecord:
    source_index: int
    raw_output: str
    total_score: float | None
    task_id: str | None


def unpack_jsonl_records(
    jsonl_path: Path | Sequence[Path],
    *,
    output_root: Path,
    max_records: int | None = None,
    sort_by_total_score: bool = False,
    order_task_ids: Sequence[str] | None = None,
) -> list[UnpackedRecord]:
    jsonl_paths = _resolve_jsonl_paths(jsonl_path)

    resolved_output = output_root.expanduser().resolve()
    resolved_output.mkdir(parents=True, exist_ok=True)

    candidates = _load_candidates(
        jsonl_paths,
        max_records=max_records,
        sort_by_total_score=sort_by_total_score,
        order_task_ids=order_task_ids,
    )
    unpacked: list[UnpackedRecord] = []
    for accepted, candidate in enumerate(candidates, start=1):
        matches = _iter_code_blocks(candidate.raw_output, fallback_task_id=candidate.task_id)
        record_id = f"record_{accepted:04d}"
        record_root = resolved_output / record_id
        files_written = 0
        for relative_path, content in matches:
            target_path = record_root / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content.strip() + "\n", encoding="utf-8")
            files_written += 1
        unpacked.append(
            UnpackedRecord(
                record_id=record_id,
                record_root=record_root,
                files_written=files_written,
            )
        )
    return unpacked


def _resolve_jsonl_paths(jsonl_path: Path | Sequence[Path]) -> list[Path]:
    if isinstance(jsonl_path, Path):
        raw_paths = [jsonl_path]
    else:
        raw_paths = list(jsonl_path)
    if not raw_paths:
        raise ValueError("At least one JSONL file must be provided.")

    resolved_paths: list[Path] = []
    for path in raw_paths:
        resolved = path.expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"JSONL file not found: {resolved}")
        resolved_paths.append(resolved)
    return resolved_paths


def _load_candidates(
    jsonl_paths: Sequence[Path],
    *,
    max_records: int | None,
    sort_by_total_score: bool,
    order_task_ids: Sequence[str] | None,
) -> list[_CandidateRecord]:
    candidates: list[_CandidateRecord] = []
    global_index = 0
    for jsonl_path in jsonl_paths:
        with jsonl_path.open("r", encoding="utf-8") as handle:
            for line_num, line in enumerate(handle, start=1):
                raw_line = line.strip()
                if not raw_line:
                    continue
                payload = json.loads(raw_line)
                raw_output = _extract_raw_output(payload)
                if raw_output is None:
                    continue
                task_id = _extract_task_id(payload)
                writable_blocks = _iter_code_blocks(raw_output, fallback_task_id=task_id)
                if not writable_blocks or not _has_nonempty_task_yaml(writable_blocks):
                    continue
                global_index += 1
                candidates.append(
                    _CandidateRecord(
                        source_index=global_index,
                        raw_output=raw_output,
                        total_score=_extract_total_score(payload),
                        task_id=task_id,
                    )
                )
                if (
                    max_records is not None
                    and not sort_by_total_score
                    and order_task_ids is None
                    and len(candidates) >= max_records
                ):
                    return candidates

    if order_task_ids is not None:
        candidates = _order_candidates_by_task_ids(candidates, order_task_ids)
        if max_records is not None:
            candidates = candidates[:max_records]
        return candidates

    if sort_by_total_score:
        candidates.sort(
            key=lambda item: (
                -(item.total_score if item.total_score is not None else float("-inf")),
                item.source_index,
            )
        )
        if max_records is not None:
            candidates = candidates[:max_records]
    return candidates


def _extract_raw_output(payload: dict[str, object]) -> str | None:
    for key in ("raw_output", "enhanced_raw_output", "dual_verified_raw_output"):
        raw_output = payload.get(key)
        if isinstance(raw_output, str) and raw_output.strip():
            return raw_output
    return None


def _extract_total_score(payload: dict[str, object]) -> float | None:
    for key in ("qa_result", "original_scores", "enhancement_qa_result"):
        score_block = payload.get(key)
        if not isinstance(score_block, dict):
            continue
        total_score = score_block.get("total_qa_score") or score_block.get("total_score")
        if isinstance(total_score, (int, float)):
            return float(total_score)
    return None


def _extract_task_id(payload: dict[str, object]) -> str | None:
    task_id = payload.get("task_id")
    if isinstance(task_id, str) and re.fullmatch(r"data_\d+", task_id.strip()):
        return task_id.strip()
    return None


def _extract_writable_blocks(raw_output: str) -> list[tuple[str, str]]:
    return list(_iter_code_blocks(raw_output))


def _iter_code_blocks(raw_output: str, *, fallback_task_id: str | None = None) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    seen_paths: set[str] = set()
    pending_path: str | None = None
    for match in CODE_BLOCK_PATTERN.finditer(raw_output):
        header = match.group("header")
        body = match.group("body")
        header_path = _clean_relative_path(header)
        if header_path is not None:
            if body.strip():
                if header_path not in seen_paths:
                    blocks.append((header_path, body))
                    seen_paths.add(header_path)
                pending_path = None
            else:
                pending_path = header_path
            continue

        if pending_path is not None and body.strip() and _clean_relative_path(body.strip()) is None:
            if pending_path not in seen_paths:
                blocks.append((pending_path, body))
                seen_paths.add(pending_path)
            pending_path = None
            continue

        if pending_path is not None and not body.strip():
            continue

        header_path = _clean_relative_path(header)
        if header_path is not None:
            if header_path not in seen_paths and body.strip():
                blocks.append((header_path, body))
                seen_paths.add(header_path)
            continue

        first_line, separator, remainder = body.partition("\n")
        body_path = _clean_relative_path(first_line) if separator else None
        if body_path is not None and separator:
            if remainder.strip():
                if body_path not in seen_paths:
                    blocks.append((body_path, remainder))
                    seen_paths.add(body_path)
                pending_path = None
            else:
                pending_path = body_path
            continue

        if pending_path is not None and body.strip() and _clean_relative_path(body.strip()) is None:
            if pending_path not in seen_paths:
                blocks.append((pending_path, body))
                seen_paths.add(pending_path)
            pending_path = None
            continue

        if pending_path is not None and not body.strip():
            continue

        if body_path is not None and separator:
            if body_path not in seen_paths and remainder.strip():
                blocks.append((body_path, remainder))
                seen_paths.add(body_path)
            continue

        preceding_path = _clean_relative_path(_previous_nonempty_line(raw_output, match.start()))
        if preceding_path is not None:
            if preceding_path not in seen_paths and body.strip():
                blocks.append((preceding_path, body))
                seen_paths.add(preceding_path)
            continue

        if fallback_task_id is not None and _looks_like_unlabeled_task_yaml(header, body):
            fallback_path = f"tasks/{fallback_task_id}.yaml"
            if fallback_path not in seen_paths:
                blocks.append((fallback_path, body))
                seen_paths.add(fallback_path)
    return blocks


def _previous_nonempty_line(raw_output: str, end: int) -> str:
    prefix = raw_output[:end].rstrip()
    if not prefix:
        return ""
    return prefix.rsplit("\n", maxsplit=1)[-1]


def _looks_like_unlabeled_task_yaml(header: str, body: str) -> bool:
    language = header.strip().split(maxsplit=1)[0].lower() if header.strip() else ""
    if language not in {"yaml", "yml"}:
        return False
    return bool(re.search(r"(?m)^(name|description|runtime|sessions|prompts?|asset):", body))


def _has_nonempty_task_yaml(blocks: Sequence[tuple[str, str]]) -> bool:
    for relative_path, content in blocks:
        if re.fullmatch(r"tasks/[^/]+\.ya?ml", relative_path) and content.strip():
            return True
    return False


def _clean_relative_path(raw_path: str) -> str | None:
    cleaned = raw_path.strip().lstrip("#").strip().strip("`")
    if not cleaned:
        return None
    for prefix in ALLOWED_PATH_PREFIXES:
        marker = cleaned.find(prefix)
        if marker >= 0:
            cleaned = cleaned[marker:]
            cleaned = cleaned.split(maxsplit=1)[0]
            cleaned = cleaned.strip().strip("`").rstrip(":")
            break
    else:
        return None
    if not cleaned.startswith(ALLOWED_PATH_PREFIXES):
        return None
    if ".." in Path(cleaned).parts:
        return None
    if cleaned.startswith("prompts/"):
        return f"tasks/{cleaned}"
    return cleaned


def _order_candidates_by_task_ids(
    candidates: Sequence[_CandidateRecord],
    order_task_ids: Sequence[str],
) -> list[_CandidateRecord]:
    by_task_id: dict[str, _CandidateRecord] = {}
    for candidate in candidates:
        task_id = _candidate_task_id(candidate.raw_output) or candidate.task_id
        if task_id is None or task_id in by_task_id:
            continue
        by_task_id[task_id] = candidate
    return [by_task_id[task_id] for task_id in order_task_ids if task_id in by_task_id]


def _candidate_task_id(raw_output: str) -> str | None:
    for clean_path, _ in _extract_writable_blocks(raw_output):
        match = re.fullmatch(r"tasks/([^/]+)\.ya?ml", clean_path)
        if match:
            return match.group(1)
    return None
