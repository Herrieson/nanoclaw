from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_GROUPS = (
    ("multi_turn_aligned", ".staging/round_01_multi_turn_aligned"),
    ("skills_aligned", ".staging/round_01_skills_aligned_500"),
    ("hard_aligned", ".staging/round_01_hard_aligned"),
    ("base", ".staging/round_01"),
)


@dataclass(frozen=True, slots=True)
class StagedRecord:
    source_task_id: str
    record_root: Path
    task_path: Path


@dataclass(frozen=True, slots=True)
class GroupConfig:
    name: str
    root: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build one staging root from several source staging roots, selecting the same "
            "source_task_id values from every group."
        )
    )
    parser.add_argument(
        "--output-root",
        default=".staging/round_01_aligned_mix_800",
        help="Destination staging root to create.",
    )
    parser.add_argument(
        "--count-per-group",
        type=int,
        default=200,
        help="Number of aligned source_task_id values to copy from each group.",
    )
    parser.add_argument(
        "--group",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help=(
            "Source staging group. Repeatable. Defaults to the round_01 multi_turn, "
            "skills, hard, and base staging roots."
        ),
    )
    parser.add_argument(
        "--order-manifest",
        default=".staging/round_01/import_manifest.jsonl",
        help=(
            "Manifest whose source_task_id order is used for aligned sampling. "
            "Falls back to the first group's record order when omitted."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output root.",
    )
    return parser


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _parse_group(raw_value: str) -> GroupConfig:
    name, separator, path_value = raw_value.partition("=")
    if not separator or not name.strip() or not path_value.strip():
        raise ValueError(f"Invalid --group value: {raw_value!r}. Expected NAME=PATH.")
    return GroupConfig(name=name.strip(), root=_resolve_path(path_value.strip()))


def _default_groups() -> list[GroupConfig]:
    return [
        GroupConfig(name=name, root=_resolve_path(path_value))
        for name, path_value in DEFAULT_GROUPS
    ]


def _discover_records(root: Path) -> dict[str, StagedRecord]:
    if not root.exists():
        raise FileNotFoundError(f"Staging root does not exist: {root}")

    by_source_task_id: dict[str, StagedRecord] = {}
    duplicate_task_ids: list[str] = []
    for task_path in sorted(root.glob("record_*/tasks/*.yaml")):
        if not task_path.is_file():
            continue
        if not task_path.read_text(encoding="utf-8").strip():
            continue
        source_task_id = task_path.stem
        if source_task_id in by_source_task_id:
            duplicate_task_ids.append(source_task_id)
            continue
        by_source_task_id[source_task_id] = StagedRecord(
            source_task_id=source_task_id,
            record_root=task_path.parent.parent,
            task_path=task_path,
        )

    if duplicate_task_ids:
        preview = ", ".join(sorted(set(duplicate_task_ids))[:10])
        raise ValueError(f"Duplicate source_task_id values in {root}: {preview}")
    if not by_source_task_id:
        raise ValueError(f"No staged task YAML files found in {root}")
    return by_source_task_id


def _load_ordered_task_ids(manifest_path: Path | None) -> list[str]:
    if manifest_path is None:
        return []
    if not manifest_path.exists():
        raise FileNotFoundError(f"Order manifest does not exist: {manifest_path}")

    ordered: list[str] = []
    seen: set[str] = set()
    with manifest_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw_line = line.strip()
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            source_task_id = payload.get("source_task_id")
            if not isinstance(source_task_id, str) or not source_task_id.strip():
                continue
            source_task_id = source_task_id.strip()
            if source_task_id in seen:
                continue
            ordered.append(source_task_id)
            seen.add(source_task_id)
    return ordered


def _select_aligned_task_ids(
    indexes: dict[str, dict[str, StagedRecord]],
    *,
    ordered_task_ids: list[str],
    count_per_group: int,
) -> list[str]:
    common_task_ids = set.intersection(*(set(records) for records in indexes.values()))
    if ordered_task_ids:
        candidates = [task_id for task_id in ordered_task_ids if task_id in common_task_ids]
    else:
        first_group_records = next(iter(indexes.values()))
        candidates = [
            task_id
            for task_id in sorted(first_group_records)
            if task_id in common_task_ids
        ]

    if len(candidates) < count_per_group:
        raise ValueError(
            f"Only {len(candidates)} aligned source_task_id values are available; "
            f"{count_per_group} requested."
        )
    return candidates[:count_per_group]


def _prepare_output_root(output_root: Path, *, force: bool) -> None:
    if output_root.exists():
        if not force:
            raise FileExistsError(f"Output root already exists: {output_root}")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=False)


def _copy_aligned_records(
    groups: list[GroupConfig],
    indexes: dict[str, dict[str, StagedRecord]],
    selected_task_ids: list[str],
    *,
    output_root: Path,
) -> list[dict[str, object]]:
    manifest_rows: list[dict[str, object]] = []
    destination_index = 1
    for group in groups:
        for aligned_index, source_task_id in enumerate(selected_task_ids, start=1):
            source_record = indexes[group.name][source_task_id]
            destination_record = f"record_{destination_index:04d}"
            destination_root = output_root / destination_record
            shutil.copytree(source_record.record_root, destination_root)

            manifest_rows.append(
                {
                    "destination_record": destination_record,
                    "aligned_index": aligned_index,
                    "group": group.name,
                    "source_root": str(group.root),
                    "source_record": source_record.record_root.name,
                    "source_task_id": source_task_id,
                    "source_task_path": str(source_record.task_path),
                }
            )
            destination_index += 1
    return manifest_rows


def _write_jsonl(rows: list[dict[str, object]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_summary(
    *,
    output_root: Path,
    groups: list[GroupConfig],
    indexes: dict[str, dict[str, StagedRecord]],
    selected_task_ids: list[str],
    manifest_rows: list[dict[str, object]],
    order_manifest: Path | None,
) -> None:
    common_count = len(set.intersection(*(set(records) for records in indexes.values())))
    summary = {
        "output_root": str(output_root),
        "order_manifest": str(order_manifest) if order_manifest is not None else None,
        "count_per_group": len(selected_task_ids),
        "total_records": len(manifest_rows),
        "common_source_task_ids": common_count,
        "groups": [
            {
                "name": group.name,
                "root": str(group.root),
                "available_records": len(indexes[group.name]),
            }
            for group in groups
        ],
        "selected_source_task_ids": selected_task_ids,
    }
    (output_root / "selection_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.count_per_group <= 0:
        parser.error("--count-per-group must be positive.")

    try:
        groups = [_parse_group(item) for item in args.group] if args.group else _default_groups()
    except ValueError as exc:
        parser.error(str(exc))

    group_names = [group.name for group in groups]
    if len(set(group_names)) != len(group_names):
        parser.error("Group names must be unique.")

    output_root = _resolve_path(args.output_root)
    order_manifest = _resolve_path(args.order_manifest) if args.order_manifest else None

    try:
        indexes = {
            group.name: _discover_records(group.root)
            for group in groups
        }
        selected_task_ids = _select_aligned_task_ids(
            indexes,
            ordered_task_ids=_load_ordered_task_ids(order_manifest),
            count_per_group=args.count_per_group,
        )
        _prepare_output_root(output_root, force=args.force)
        manifest_rows = _copy_aligned_records(
            groups,
            indexes,
            selected_task_ids,
            output_root=output_root,
        )
        _write_jsonl(manifest_rows, output_root / "selection_manifest.jsonl")
        _write_summary(
            output_root=output_root,
            groups=groups,
            indexes=indexes,
            selected_task_ids=selected_task_ids,
            manifest_rows=manifest_rows,
            order_manifest=order_manifest,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Created {len(manifest_rows)} staged record(s) at {output_root}")
    print(f"Aligned source_task_id count: {len(selected_task_ids)}")
    print(f"Manifest: {output_root / 'selection_manifest.jsonl'}")
    for group in groups:
        print(f"- {group.name}: {len(selected_task_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
