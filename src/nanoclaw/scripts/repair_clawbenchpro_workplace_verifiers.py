from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.materialize_clawbenchpro_workplace_verifiers import (  # noqa: E402
    refresh_dataset_manifests,
    refresh_root_manifest,
    write_checksums,
)


DEFAULT_CLAWBENCHPRO_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "ClawBenchPro"
DATASETS = ("round_01_aligned_mix_800", "persona_aligned_mix_200")
OUTPUT_MARKERS = ("workplace_score", "verify_result", "state.json", "total_score")


@dataclass(frozen=True, slots=True)
class TaskVerifier:
    dataset: str
    group: str
    source_task_id: str
    imported_task_id: str
    task_dir: str
    path: Path
    text: str
    reasons: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.reasons


def main() -> int:
    args = build_parser().parse_args()
    root = args.clawbenchpro_root.expanduser().resolve()
    datasets = tuple(args.datasets or DATASETS)

    tasks = load_task_verifiers(root, datasets)
    valid_by_source = index_valid_donors(tasks, allow_cross_group_copy=args.allow_cross_group_copy)
    repairs = plan_repairs(
        tasks,
        valid_by_source,
        allow_cross_group_copy=args.allow_cross_group_copy,
    )

    print_summary(tasks, repairs)
    if not repairs:
        return 0
    if not args.write:
        print("Dry run only. Re-run with --write to repair verifier files.")
        return 0

    apply_repairs(root, repairs)
    if args.refresh_metadata:
        for dataset in datasets:
            write_repair_manifest(root / dataset, repairs)
        refresh_dataset_manifests(root, datasets)
        refresh_root_manifest(root, datasets)
        write_checksums(root, datasets)

    print(f"Repaired {len(repairs)} verifier(s) under {root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Repair ClawBenchPro task-local and JSONL workplace verifiers. "
            "Invalid verifiers are restored from same-source valid donors when possible; "
            "otherwise a conservative zero-score fallback is written."
        )
    )
    parser.add_argument(
        "--clawbenchpro-root",
        type=Path,
        default=DEFAULT_CLAWBENCHPRO_ROOT,
        help=f"ClawBenchPro root. Default: {DEFAULT_CLAWBENCHPRO_ROOT}",
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        choices=DATASETS,
        default=None,
        help="Datasets to repair. Defaults to all ClawBenchPro datasets.",
    )
    parser.add_argument("--write", action="store_true", help="Write repaired files.")
    parser.add_argument(
        "--allow-cross-group-copy",
        action="store_true",
        help=(
            "Allow copying a verifier from the same source_task_id in another group. "
            "This is disabled by default because group variants can have different "
            "prompts, environments, and scoring semantics."
        ),
    )
    parser.add_argument(
        "--no-refresh-metadata",
        dest="refresh_metadata",
        action="store_false",
        help="Do not refresh manifests and checksums after writing.",
    )
    parser.set_defaults(refresh_metadata=True)
    return parser


def load_task_verifiers(root: Path, datasets: tuple[str, ...]) -> list[TaskVerifier]:
    tasks: list[TaskVerifier] = []
    for dataset in datasets:
        manifest_path = root / dataset / "import_manifest.jsonl"
        for row in read_jsonl(manifest_path):
            task_dir = str(row["task_dir"])
            path = root / dataset / task_dir / "verify_workplace.py"
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            tasks.append(
                TaskVerifier(
                    dataset=dataset,
                    group=str(row["group"]),
                    source_task_id=str(row["source_task_id"]),
                    imported_task_id=str(row["imported_task_id"]),
                    task_dir=task_dir,
                    path=path,
                    text=text,
                    reasons=validate_verifier(text, path),
                )
            )
    return tasks


def validate_verifier(text: str, path: Path) -> tuple[str, ...]:
    reasons: list[str] = []
    if not text.strip():
        reasons.append("empty")
    if not any(marker in text for marker in OUTPUT_MARKERS):
        reasons.append("missing_score_output_marker")
    try:
        compile(text, str(path), "exec")
    except SyntaxError as exc:
        reasons.append(f"syntax_error:{exc.msg}:line_{exc.lineno}")
    return tuple(reasons)


def index_valid_donors(
    tasks: list[TaskVerifier],
    *,
    allow_cross_group_copy: bool,
) -> dict[tuple[str, ...], list[TaskVerifier]]:
    donors: dict[tuple[str, ...], list[TaskVerifier]] = {}
    for task in tasks:
        if task.is_valid:
            key = donor_key(task, allow_cross_group_copy=allow_cross_group_copy)
            donors.setdefault(key, []).append(task)
    for donor_list in donors.values():
        donor_list.sort(key=lambda item: (item.group, item.imported_task_id))
    return donors


def donor_key(task: TaskVerifier, *, allow_cross_group_copy: bool) -> tuple[str, ...]:
    if allow_cross_group_copy:
        return (task.dataset, task.source_task_id)
    return (task.dataset, task.group, task.source_task_id)


def plan_repairs(
    tasks: list[TaskVerifier],
    valid_by_source: dict[tuple[str, ...], list[TaskVerifier]],
    *,
    allow_cross_group_copy: bool,
) -> list[dict[str, Any]]:
    repairs: list[dict[str, Any]] = []
    for task in tasks:
        if task.is_valid:
            continue
        donors = valid_by_source.get(donor_key(task, allow_cross_group_copy=allow_cross_group_copy), [])
        donor = donors[0] if donors else None
        if donor is not None:
            text = donor.text.replace(donor.imported_task_id, task.imported_task_id)
            action = (
                "copy_same_source_cross_group_valid_verifier"
                if donor.group != task.group
                else "copy_same_group_valid_verifier"
            )
            donor_id = donor.imported_task_id
        else:
            text = fallback_verifier(task)
            action = "write_conservative_zero_score_fallback"
            donor_id = None
        repairs.append(
            {
                "dataset": task.dataset,
                "group": task.group,
                "source_task_id": task.source_task_id,
                "imported_task_id": task.imported_task_id,
                "task_dir": task.task_dir,
                "path": task.path,
                "original_sha256": sha256_text(task.text),
                "original_reasons": list(task.reasons),
                "repair_action": action,
                "donor_imported_task_id": donor_id,
                "repaired_text": ensure_trailing_newline(text),
            }
        )
    return repairs


def fallback_verifier(task: TaskVerifier) -> str:
    reasons = "; ".join(task.reasons)
    reason = (
        "Original ClawBenchPro verify_workplace.py could not be recovered from "
        f"a same-source valid donor. Validation reasons: {reasons}."
    )
    return f'''from __future__ import annotations

import json
import os
import sys


def main() -> None:
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = {{
        "total_score": 0,
        "details": [
            {{
                "item": "verifier_repair_fallback",
                "score": 0,
                "max_score": 100,
                "passed": False,
                "reason": {reason!r},
            }}
        ],
        "repair_metadata": {{
            "dataset": {task.dataset!r},
            "group": {task.group!r},
            "source_task_id": {task.source_task_id!r},
            "imported_task_id": {task.imported_task_id!r},
            "repair_action": "write_conservative_zero_score_fallback",
        }},
    }}
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
'''


def apply_repairs(root: Path, repairs: list[dict[str, Any]]) -> None:
    by_dataset_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for repair in repairs:
        path = repair["path"]
        text = repair["repaired_text"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        by_dataset_group.setdefault((repair["dataset"], repair["group"]), []).append(repair)

    for (dataset, group), group_repairs in by_dataset_group.items():
        update_verifier_jsonl(
            root / dataset / "verifiers" / f"{group}.jsonl",
            group_repairs,
        )


def update_verifier_jsonl(path: Path, repairs: list[dict[str, Any]]) -> None:
    by_task_id = {repair["imported_task_id"]: repair for repair in repairs}
    rows = read_jsonl(path)
    updated_rows = []
    for row in rows:
        task_id = str(row.get("imported_task_id"))
        repair = by_task_id.get(task_id)
        if repair is not None:
            text = repair["repaired_text"].rstrip()
            row = dict(row)
            row["raw_output"] = (
                "```python\n"
                f"# scripts/{repair['source_task_id']}/verify_workplace.py\n"
                f"{text}\n"
                "```\n"
            )
            row["verifier_repair"] = {
                "action": repair["repair_action"],
                "original_sha256": repair["original_sha256"],
                "original_reasons": repair["original_reasons"],
                "donor_imported_task_id": repair["donor_imported_task_id"],
            }
        updated_rows.append(row)
    write_jsonl(updated_rows, path)


def write_repair_manifest(dataset_root: Path, repairs: list[dict[str, Any]]) -> None:
    rows = [
        {
            "dataset": repair["dataset"],
            "group": repair["group"],
            "source_task_id": repair["source_task_id"],
            "imported_task_id": repair["imported_task_id"],
            "task_dir": repair["task_dir"],
            "original_sha256": repair["original_sha256"],
            "original_reasons": repair["original_reasons"],
            "repair_action": repair["repair_action"],
            "donor_imported_task_id": repair["donor_imported_task_id"],
            "repaired_sha256": sha256_text(repair["repaired_text"]),
        }
        for repair in repairs
        if repair["dataset"] == dataset_root.name
    ]
    if not rows:
        return
    output_path = dataset_root / "provenance" / "verifier_repair_manifest.jsonl"
    write_jsonl(rows, output_path)


def print_summary(tasks: list[TaskVerifier], repairs: list[dict[str, Any]]) -> None:
    invalid = [task for task in tasks if not task.is_valid]
    print(f"Task-local verifier files: {len(tasks)}")
    print(f"Invalid verifier files: {len(invalid)}")
    print(f"Planned repairs: {len(repairs)}")
    actions: dict[str, int] = {}
    for repair in repairs:
        action = str(repair["repair_action"])
        actions[action] = actions.get(action, 0) + 1
    for action in sorted(actions):
        print(f"  {action}: {actions[action]}")
    if invalid:
        reason_counts: dict[str, int] = {}
        for task in invalid:
            for reason in task.reasons:
                key = reason.split(":", 1)[0]
                reason_counts[key] = reason_counts.get(key, 0) + 1
        print("Invalid reasons:")
        for reason in sorted(reason_counts):
            print(f"  {reason}: {reason_counts[reason]}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
