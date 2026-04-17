from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.task_importer import (
    default_round_id,
    import_staged_tasks,
    write_import_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import staged generated tasks into the repo with unique task identifiers."
    )
    parser.add_argument(
        "staging_root",
        help="Directory that contains a tasks/ subtree produced by unzip.py.",
    )
    parser.add_argument(
        "--round-id",
        default=None,
        help="Logical round identifier used when allocating unique task ids.",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=100,
        help="Maximum number of staged tasks to import.",
    )
    parser.add_argument(
        "--manifest-out",
        default=None,
        help="Optional JSONL manifest path for imported task mappings.",
    )
    return parser


def _resolve_output(path_value: str | None, *, default_path: Path) -> Path:
    if not path_value:
        return default_path.resolve()
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    staging_root = Path(args.staging_root).expanduser().resolve()
    round_id = args.round_id or default_round_id()
    imported = import_staged_tasks(
        staging_root,
        repo_root=REPO_ROOT,
        round_id=round_id,
        max_tasks=args.max_tasks,
    )
    if not imported:
        parser.error("No staged task YAML files were found to import.")

    manifest_out = _resolve_output(
        args.manifest_out,
        default_path=staging_root / "import_manifest.jsonl",
    )
    write_import_manifest(imported, output_path=manifest_out)

    print(f"Imported {len(imported)} task(s) from {staging_root}")
    print(f"Manifest: {manifest_out}")
    for item in imported[:10]:
        print(f"- {item.source_task_id} -> {item.imported_task_id}")
    if len(imported) > 10:
        print(f"... {len(imported) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
