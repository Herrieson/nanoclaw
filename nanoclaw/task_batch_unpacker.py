from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


CODE_BLOCK_PATTERN = re.compile(r"```[a-zA-Z]*\n(tasks/[^\n]+)\n(.*?)```", re.DOTALL)


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


def unpack_jsonl_records(
    jsonl_path: Path,
    *,
    output_root: Path,
    max_records: int | None = None,
    sort_by_total_score: bool = False,
) -> list[UnpackedRecord]:
    resolved_jsonl = jsonl_path.expanduser().resolve()
    if not resolved_jsonl.exists():
        raise FileNotFoundError(f"JSONL file not found: {resolved_jsonl}")

    resolved_output = output_root.expanduser().resolve()
    resolved_output.mkdir(parents=True, exist_ok=True)

    candidates = _load_candidates(
        resolved_jsonl,
        max_records=max_records,
        sort_by_total_score=sort_by_total_score,
    )
    unpacked: list[UnpackedRecord] = []
    for accepted, candidate in enumerate(candidates, start=1):
        matches = CODE_BLOCK_PATTERN.findall(candidate.raw_output)
        record_id = f"record_{accepted:04d}"
        record_root = resolved_output / record_id
        files_written = 0
        for relative_path, content in matches:
            clean_relative = relative_path.strip()
            if not clean_relative.startswith("tasks/"):
                continue
            target_path = record_root / clean_relative
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


def _load_candidates(
    jsonl_path: Path,
    *,
    max_records: int | None,
    sort_by_total_score: bool,
) -> list[_CandidateRecord]:
    candidates: list[_CandidateRecord] = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            raw_output = payload.get("raw_output")
            if not isinstance(raw_output, str) or not raw_output.strip():
                continue
            if not CODE_BLOCK_PATTERN.findall(raw_output):
                continue
            candidates.append(
                _CandidateRecord(
                    source_index=line_num,
                    raw_output=raw_output,
                    total_score=_extract_total_score(payload),
                )
            )
            if max_records is not None and not sort_by_total_score and len(candidates) >= max_records:
                break

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


def _extract_total_score(payload: dict[str, object]) -> float | None:
    qa_result = payload.get("qa_result")
    if not isinstance(qa_result, dict):
        return None
    total_score = qa_result.get("total_score")
    if isinstance(total_score, (int, float)):
        return float(total_score)
    return None
