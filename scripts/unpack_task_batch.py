from __future__ import annotations

import argparse
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
    parser.add_argument("jsonl", help="Input JSONL path.")
    parser.add_argument("--output-root", required=True, help="Directory used to store unpacked records.")
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Optional cap on the number of accepted records to unpack.",
    )
    return parser


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    unpacked = unpack_jsonl_records(
        _resolve_path(args.jsonl),
        output_root=_resolve_path(args.output_root),
        max_records=args.max_records,
    )
    print(f"Unpacked {len(unpacked)} record(s) into {_resolve_path(args.output_root)}")
    for item in unpacked[:10]:
        print(f"- {item.record_id}: {item.files_written} file(s)")
    if len(unpacked) > 10:
        print(f"... {len(unpacked) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
