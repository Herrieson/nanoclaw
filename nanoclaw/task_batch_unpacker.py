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


def unpack_jsonl_records(
    jsonl_path: Path,
    *,
    output_root: Path,
    max_records: int | None = None,
) -> list[UnpackedRecord]:
    resolved_jsonl = jsonl_path.expanduser().resolve()
    if not resolved_jsonl.exists():
        raise FileNotFoundError(f"JSONL file not found: {resolved_jsonl}")

    resolved_output = output_root.expanduser().resolve()
    resolved_output.mkdir(parents=True, exist_ok=True)

    unpacked: list[UnpackedRecord] = []
    accepted = 0
    with resolved_jsonl.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, start=1):
            if max_records is not None and accepted >= max_records:
                break
            raw_line = line.strip()
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            raw_output = payload.get("raw_output")
            if not isinstance(raw_output, str) or not raw_output.strip():
                continue

            matches = CODE_BLOCK_PATTERN.findall(raw_output)
            if not matches:
                continue

            accepted += 1
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
