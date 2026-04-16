from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.task_normalizer import normalize_task_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize generated data_*.yaml files into the current nanoclaw task schema."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["tasks/data_*.yaml"],
        help="Task file paths or glob patterns to normalize. Defaults to tasks/data_*.yaml.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not save pre-normalization backups.",
    )
    parser.add_argument(
        "--backup-root",
        default=".task_normalizer_backups",
        help="Directory used for backups when backups are enabled.",
    )
    return parser


def expand_paths(patterns: list[str]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        matches = sorted(Path().glob(pattern))
        if not matches:
            candidate = Path(pattern)
            if candidate.exists():
                matches = [candidate]
        for path in matches:
            resolved_path = path.resolve()
            if resolved_path in seen:
                continue
            seen.add(resolved_path)
            resolved.append(resolved_path)
    return resolved


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    task_paths = expand_paths(args.paths)
    if not task_paths:
        parser.error("No task files matched the provided paths.")

    changed = 0
    for task_path in task_paths:
        result = normalize_task_file(
            task_path,
            create_backup=not args.no_backup,
            backup_root=Path(args.backup_root),
        )
        status = "updated" if result.changed else "unchanged"
        print(f"{status}: {task_path} -> asset={result.asset}")
        if result.backup_path is not None:
            print(f"  backup: {result.backup_path}")
        if result.changed:
            changed += 1

    print(f"Normalized {len(task_paths)} task files; changed {changed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
