from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.task_batch_unpacker import unpack_jsonl_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely unpack JSONL task generations into per-record staging directories."
    )
    parser.add_argument("jsonl", nargs="+", help="Input JSONL path(s).")
    parser.add_argument("--output-root", required=True, help="Directory used to store unpacked records.")
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Optional cap on the number of accepted records to unpack.",
    )
    parser.add_argument(
        "--sort-by-total-score",
        action="store_true",
        help=(
            "Sort accepted JSONL records by qa_result/original_scores/enhancement_qa_result "
            "total_score or total_qa_score descending before applying --max-records."
        ),
    )
    parser.add_argument(
        "--order-from-manifest",
        default=None,
        help=(
            "Optional import_manifest.jsonl whose source_task_id order should be reused. "
            "Only records with matching task ids are unpacked."
        ),
    )
    return parser


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _load_manifest_task_order(path_value: str | None) -> list[str] | None:
    if path_value is None:
        return None
    path = _resolve_path(path_value)
    task_ids: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw_line = line.strip()
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            source_task_id = payload.get("source_task_id")
            if isinstance(source_task_id, str) and source_task_id.strip():
                task_ids.append(source_task_id.strip())
    return task_ids


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    unpacked = unpack_jsonl_records(
        [_resolve_path(item) for item in args.jsonl],
        output_root=_resolve_path(args.output_root),
        max_records=args.max_records,
        sort_by_total_score=args.sort_by_total_score,
        order_task_ids=_load_manifest_task_order(args.order_from_manifest),
    )
    print(f"Unpacked {len(unpacked)} record(s) into {_resolve_path(args.output_root)}")
    for item in unpacked[:10]:
        print(f"- {item.record_id}: {item.files_written} file(s)")
    if len(unpacked) > 10:
        print(f"... {len(unpacked) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
