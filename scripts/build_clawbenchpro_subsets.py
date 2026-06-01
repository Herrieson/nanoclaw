from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.workplace_trace_evaluator import extract_file_blocks


DEFAULT_SOURCE_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "ClawBenchPro"
DEFAULT_OUTPUT_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "ClawBenchPro_subsets"
DEFAULT_SEED = "clawbenchpro-subsets-v1"
OUTPUT_MARKERS = ("workplace_score", "verify_result", "state.json", "total_score")
EXCLUDED_IMPORTED_TASK_IDS = frozenset(
    {
        # This hard task asks agents to inspect a multi-megabyte scene JSON. Some
        # runners reasonably try to read it directly, which can exceed provider
        # input limits before the task reaches verification. Keep smoke/pilot
        # subsets focused on benchmark behavior rather than context-limit traps.
        "data_persona_aligned_hard_50_0022",
    }
)

DATASET_GROUPS = {
    "round_01_aligned_mix_800": (
        "base",
        "hard_aligned",
        "multi_turn_aligned",
        "skills_aligned",
    ),
    "persona_aligned_mix_200": (
        "base",
        "hard",
        "multi_turn",
        "skills",
    ),
}

SUBSET_SPECS = {
    "smoke_40": {
        "round_01_aligned_mix_800": {
            "base": 5,
            "hard_aligned": 5,
            "multi_turn_aligned": 5,
            "skills_aligned": 5,
        },
        "persona_aligned_mix_200": {
            "base": 5,
            "hard": 5,
            "multi_turn": 5,
            "skills": 5,
        },
    },
    "pilot_200": {
        "round_01_aligned_mix_800": {
            "base": 40,
            "hard_aligned": 40,
            "multi_turn_aligned": 40,
            "skills_aligned": 40,
        },
        "persona_aligned_mix_200": {
            "base": 10,
            "hard": 10,
            "multi_turn": 10,
            "skills": 10,
        },
    },
}

ROOT_COPY_FILES = (
    ".gitattributes",
    ".gitignore",
    ".hfignore",
    "LICENSE",
    "materialize_assets.py",
)
DATASET_COPY_FILES = ("README.md",)


@dataclass(frozen=True, slots=True)
class SelectedDataset:
    name: str
    rows: list[dict[str, Any]]
    rows_by_group: dict[str, list[dict[str, Any]]]
    excluded_imported_task_ids: list[str]

    @property
    def task_ids(self) -> set[str]:
        return {str(row["imported_task_id"]) for row in self.rows}

    @property
    def task_paths(self) -> set[str]:
        return {str(row["task_path"]) for row in self.rows}

    @property
    def group_counts(self) -> dict[str, int]:
        return {group: len(rows) for group, rows in self.rows_by_group.items()}


@dataclass(frozen=True, slots=True)
class BuiltDataset:
    name: str
    title: str
    task_count: int
    group_counts: dict[str, int]
    files: int
    bytes: int
    excluded_imported_task_ids: list[str]


def main() -> int:
    args = build_parser().parse_args()
    source_root = args.source_root.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()
    subset_specs = dict(SUBSET_SPECS)
    if args.custom_name:
        subset_specs[args.custom_name] = build_custom_spec(args)
    subset_names = tuple(args.subsets or ([args.custom_name] if args.custom_name else SUBSET_SPECS))

    selections = {
        subset_name: select_subset(
            source_root,
            subset_name,
            seed=args.seed,
            subset_specs=subset_specs,
            require_valid_verifiers=not args.allow_invalid_verifiers,
        )
        for subset_name in subset_names
    }
    print_summary(selections)

    if not args.write:
        print("Dry run only. Re-run with --write to build subset directories.")
        return 0

    for subset_name, selected in selections.items():
        subset_root = output_root / subset_name
        if subset_root.exists():
            if not args.overwrite:
                raise SystemExit(f"Output already exists: {subset_root}. Use --overwrite to rebuild it.")
            shutil.rmtree(subset_root)
        build_subset_package(
            source_root=source_root,
            subset_root=subset_root,
            subset_name=subset_name,
            seed=args.seed,
            selected=selected,
        )
        print(f"Wrote {subset_name} to {subset_root}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic smoke/pilot subsets from a complete ClawBenchPro package."
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help=f"Complete ClawBenchPro root. Default: {DEFAULT_SOURCE_ROOT}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Directory that will contain subset packages. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--subsets",
        nargs="*",
        default=None,
        help="Subset names to build. Defaults to built-ins, or --custom-name when provided.",
    )
    parser.add_argument(
        "--custom-name",
        default=None,
        help="Build one custom subset with this name, e.g. smoke_80 or pilot_320.",
    )
    parser.add_argument(
        "--round-per-group",
        type=int,
        default=None,
        help="Default custom quota for each round_01_aligned_mix_800 group.",
    )
    parser.add_argument(
        "--persona-per-group",
        type=int,
        default=None,
        help="Default custom quota for each persona_aligned_mix_200 group.",
    )
    parser.add_argument(
        "--quota",
        action="append",
        default=[],
        help=(
            "Override one custom quota as dataset/group=count. "
            "Example: --quota round_01_aligned_mix_800/base=20"
        ),
    )
    parser.add_argument(
        "--seed",
        default=DEFAULT_SEED,
        help=f"Stable sampling seed. Default: {DEFAULT_SEED}",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write subset directories. Without this flag the script only reports selected counts.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete and rebuild existing subset directories.",
    )
    parser.add_argument(
        "--allow-invalid-verifiers",
        action="store_true",
        help=(
            "Allow tasks whose verifier JSONL records do not contain an executable "
            "same-group verifier. By default such tasks are skipped before sampling."
        ),
    )
    return parser


def build_custom_spec(args: argparse.Namespace) -> dict[str, dict[str, int]]:
    if not args.custom_name:
        raise ValueError("--custom-name is required for custom specs")
    if args.round_per_group is None and args.persona_per_group is None and not args.quota:
        raise SystemExit(
            "Custom subsets need --round-per-group/--persona-per-group or explicit --quota overrides."
        )

    spec: dict[str, dict[str, int]] = {}
    for dataset_name, groups in DATASET_GROUPS.items():
        default = args.round_per_group if dataset_name == "round_01_aligned_mix_800" else args.persona_per_group
        spec[dataset_name] = {group: int(default or 0) for group in groups}

    for raw_quota in args.quota:
        dataset_group, _, raw_count = raw_quota.partition("=")
        dataset_name, _, group_name = dataset_group.partition("/")
        if not dataset_name or not group_name or not raw_count:
            raise SystemExit(f"Invalid --quota value: {raw_quota!r}")
        if dataset_name not in DATASET_GROUPS or group_name not in DATASET_GROUPS[dataset_name]:
            raise SystemExit(f"Unknown dataset/group in --quota: {raw_quota!r}")
        count = int(raw_count)
        if count < 0:
            raise SystemExit(f"Quota must be non-negative: {raw_quota!r}")
        spec[dataset_name][group_name] = count

    missing = [
        f"{dataset}/{group}"
        for dataset, groups in spec.items()
        for group, count in groups.items()
        if count <= 0
    ]
    if missing:
        preview = ", ".join(missing[:8])
        raise SystemExit(f"Custom subset has non-positive quotas for: {preview}")
    return spec


def select_subset(
    source_root: Path,
    subset_name: str,
    *,
    seed: str,
    subset_specs: dict[str, dict[str, dict[str, int]]],
    require_valid_verifiers: bool,
) -> dict[str, SelectedDataset]:
    if subset_name not in subset_specs:
        known = ", ".join(sorted(subset_specs))
        raise SystemExit(f"Unknown subset {subset_name!r}. Known subsets: {known}")
    spec = subset_specs[subset_name]
    selected: dict[str, SelectedDataset] = {}
    for dataset_name, group_quotas in spec.items():
        rows = read_jsonl(source_root / dataset_name / "import_manifest.jsonl")
        source_task_ids = {
            str(row.get("imported_task_id"))
            for row in rows
            if row.get("imported_task_id") is not None
        }
        excluded_imported_task_ids = sorted(source_task_ids & EXCLUDED_IMPORTED_TASK_IDS)
        valid_task_ids = (
            valid_verifier_task_ids(source_root / dataset_name)
            if require_valid_verifiers
            else None
        )
        indexed_rows = list(enumerate(rows))
        rows_by_group: dict[str, list[dict[str, Any]]] = {}
        for group_name in DATASET_GROUPS[dataset_name]:
            group_rows = [
                (index, row)
                for index, row in indexed_rows
                if str(row.get("group")) == group_name
                and str(row.get("imported_task_id")) not in EXCLUDED_IMPORTED_TASK_IDS
                and (
                    valid_task_ids is None
                    or str(row.get("imported_task_id")) in valid_task_ids
                )
            ]
            quota = group_quotas[group_name]
            if len(group_rows) < quota:
                raise ValueError(
                    f"{dataset_name}/{group_name} only has {len(group_rows)} eligible row(s), need {quota}"
                )
            picked = sorted(
                group_rows,
                key=lambda item: stable_sample_key(
                    seed,
                    dataset_name=dataset_name,
                    group_name=group_name,
                    row=item[1],
                ),
            )[:quota]
            rows_by_group[group_name] = [row for _, row in sorted(picked, key=lambda item: item[0])]

        selected[dataset_name] = SelectedDataset(
            name=dataset_name,
            rows=[row for group_name in DATASET_GROUPS[dataset_name] for row in rows_by_group[group_name]],
            rows_by_group=rows_by_group,
            excluded_imported_task_ids=excluded_imported_task_ids,
        )
    return selected


def valid_verifier_task_ids(dataset_root: Path) -> set[str]:
    valid: set[str] = set()
    verifier_root = dataset_root / "verifiers"
    if verifier_root.is_dir():
        for verifier_jsonl in sorted(verifier_root.glob("*.jsonl")):
            for row in read_jsonl(verifier_jsonl):
                task_id = row.get("imported_task_id")
                if not isinstance(task_id, str) or not task_id:
                    continue
                if verifier_row_is_fallback(row):
                    continue
                if verifier_row_is_executable(row):
                    valid.add(task_id)
    if valid:
        return valid

    # Backward-compatible fallback for older packages that only have task-local
    # verify_workplace.py files and no verifier JSONL metadata.
    for row in read_jsonl(dataset_root / "import_manifest.jsonl"):
        task_id = str(row["imported_task_id"])
        task_dir = str(row["task_dir"])
        verifier_path = dataset_root / task_dir / "verify_workplace.py"
        if verifier_path_is_executable(verifier_path):
            valid.add(task_id)
    return valid


def verifier_row_is_fallback(row: dict[str, Any]) -> bool:
    materialization = row.get("verifier_materialization")
    if isinstance(materialization, dict):
        action = materialization.get("action")
        if isinstance(action, str) and action.startswith("conservative_fallback"):
            return True
    repair = row.get("verifier_repair")
    if isinstance(repair, dict):
        action = repair.get("action")
        if isinstance(action, str) and action.startswith("write_conservative_zero_score_fallback"):
            return True
    return False


def verifier_row_is_executable(row: dict[str, Any]) -> bool:
    raw_output = row.get("raw_output")
    if not isinstance(raw_output, str) or not raw_output.strip():
        return False
    blocks = extract_file_blocks(raw_output)
    workplace_scripts = [
        text
        for path, text in blocks.items()
        if path.endswith("/verify_workplace.py") or path.endswith("/verify_rules.py")
    ]
    if workplace_scripts:
        return any(python_verifier_is_executable(text) for text in workplace_scripts)

    turn_scripts = [
        text
        for path, text in blocks.items()
        if re.fullmatch(r"scripts/data_\d+/verify_turn_\d+\.py", path)
    ]
    return bool(turn_scripts) and all(python_verifier_is_executable(text) for text in turn_scripts)


def verifier_path_is_executable(path: Path) -> bool:
    if not path.is_file():
        return False
    return python_verifier_is_executable(path.read_text(encoding="utf-8"), label=str(path))


def python_verifier_is_executable(text: str, label: str = "<verifier>") -> bool:
    if not text.strip():
        return False
    if not any(marker in text for marker in OUTPUT_MARKERS):
        return False
    try:
        compile(text, label, "exec")
    except SyntaxError:
        return False
    return True


def stable_sample_key(
    seed: str,
    *,
    dataset_name: str,
    group_name: str,
    row: dict[str, Any],
) -> str:
    task_id = str(row["imported_task_id"])
    source_task_id = str(row["source_task_id"])
    payload = f"{seed}\0{dataset_name}\0{group_name}\0{task_id}\0{source_task_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_subset_package(
    *,
    source_root: Path,
    subset_root: Path,
    subset_name: str,
    seed: str,
    selected: dict[str, SelectedDataset],
) -> None:
    subset_root.mkdir(parents=True, exist_ok=False)
    for filename in ROOT_COPY_FILES:
        copy_file_if_exists(source_root / filename, subset_root / filename)
    write_subset_readme(
        source_root / "README.md",
        subset_root / "README.md",
        subset_name=subset_name,
        selected=selected,
    )

    built_datasets: list[BuiltDataset] = []
    for dataset_name in DATASET_GROUPS:
        built_datasets.append(
            build_dataset_subset(
                source_root=source_root,
                subset_root=subset_root,
                subset_name=subset_name,
                seed=seed,
                selected_dataset=selected[dataset_name],
            )
        )

    write_root_dataset_index(source_root=source_root, subset_root=subset_root, selected=selected)
    write_root_manifest(
        source_root=source_root,
        subset_root=subset_root,
        subset_name=subset_name,
        seed=seed,
        built_datasets=built_datasets,
    )
    write_checksums(subset_root / "round_01_aligned_mix_800", subset_root / "round_01_aligned_mix_800" / "checksums.sha256")
    write_checksums(subset_root / "persona_aligned_mix_200", subset_root / "persona_aligned_mix_200" / "checksums.sha256")
    write_checksums(subset_root, subset_root / "checksums.sha256")


def build_dataset_subset(
    *,
    source_root: Path,
    subset_root: Path,
    subset_name: str,
    seed: str,
    selected_dataset: SelectedDataset,
) -> BuiltDataset:
    dataset_name = selected_dataset.name
    source_dataset_root = source_root / dataset_name
    target_dataset_root = subset_root / dataset_name
    target_dataset_root.mkdir(parents=True)
    for filename in DATASET_COPY_FILES:
        copy_file_if_exists(source_dataset_root / filename, target_dataset_root / filename)

    for row in selected_dataset.rows:
        copy_task_files(source_dataset_root, target_dataset_root, row)

    write_jsonl(selected_dataset.rows, target_dataset_root / "import_manifest.jsonl")
    write_filtered_selection_manifest(source_dataset_root, target_dataset_root, selected_dataset)
    write_filtered_repair_manifest(source_dataset_root, target_dataset_root, selected_dataset)
    write_filtered_materialization_manifest(source_dataset_root, target_dataset_root, selected_dataset)
    write_eval_manifests(source_dataset_root, target_dataset_root, selected_dataset)
    write_verifier_jsonls(source_dataset_root, target_dataset_root, selected_dataset)
    write_dataset_index_files(source_root, subset_root, selected_dataset)
    write_dataset_manifest(
        source_dataset_root=source_dataset_root,
        target_dataset_root=target_dataset_root,
        subset_name=subset_name,
        seed=seed,
        selected_dataset=selected_dataset,
    )

    files, bytes_total = count_files(target_dataset_root)
    manifest_path = target_dataset_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"] = {
        "count": files,
        "bytes": bytes_total,
        "checksums": "checksums.sha256",
    }
    write_json(manifest_path, manifest)

    return BuiltDataset(
        name=dataset_name,
        title=str(manifest.get("title", dataset_name)),
        task_count=len(selected_dataset.rows),
        group_counts=selected_dataset.group_counts,
        files=files,
        bytes=bytes_total,
        excluded_imported_task_ids=selected_dataset.excluded_imported_task_ids,
    )


def copy_task_files(source_dataset_root: Path, target_dataset_root: Path, row: dict[str, Any]) -> None:
    copy_file(source_dataset_root / row["task_path"], target_dataset_root / row["task_path"])
    for prompt_path in row.get("prompt_paths") or []:
        if is_real_relative_path(prompt_path):
            copy_file(source_dataset_root / prompt_path, target_dataset_root / prompt_path)

    task_dir = row.get("task_dir")
    if isinstance(task_dir, str) and task_dir:
        copy_tree_if_exists(source_dataset_root / task_dir, target_dataset_root / task_dir)

    asset_dir = row.get("asset_dir")
    if isinstance(asset_dir, str) and asset_dir:
        copy_tree_if_exists(source_dataset_root / asset_dir, target_dataset_root / asset_dir)

    for skill_dir in row.get("skill_dirs") or []:
        if isinstance(skill_dir, str) and skill_dir:
            copy_tree_if_exists(source_dataset_root / skill_dir, target_dataset_root / skill_dir)


def write_filtered_selection_manifest(
    source_dataset_root: Path,
    target_dataset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    rows = [
        row
        for row in read_jsonl(source_dataset_root / "selection_manifest.jsonl")
        if str(row.get("task_path")) in selected_dataset.task_paths
    ]
    write_jsonl(rows, target_dataset_root / "selection_manifest.jsonl")


def write_filtered_repair_manifest(
    source_dataset_root: Path,
    target_dataset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    source_path = source_dataset_root / "provenance" / "verifier_repair_manifest.jsonl"
    if not source_path.is_file():
        return
    selected_task_ids = selected_dataset.task_ids
    rows = [
        row
        for row in read_jsonl(source_path)
        if str(row.get("imported_task_id")) in selected_task_ids
    ]
    if rows:
        write_jsonl(rows, target_dataset_root / "provenance" / "verifier_repair_manifest.jsonl")


def write_filtered_materialization_manifest(
    source_dataset_root: Path,
    target_dataset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    source_path = source_dataset_root / "provenance" / "verifier_materialization_manifest.jsonl"
    if not source_path.is_file():
        return
    selected_task_ids = selected_dataset.task_ids
    rows = [
        row
        for row in read_jsonl(source_path)
        if str(row.get("imported_task_id")) in selected_task_ids
    ]
    if rows:
        write_jsonl(rows, target_dataset_root / "provenance" / "verifier_materialization_manifest.jsonl")


def write_eval_manifests(
    source_dataset_root: Path,
    target_dataset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    eval_root = target_dataset_root / "eval_manifests"
    eval_root.mkdir(parents=True, exist_ok=True)
    for group_name, rows in selected_dataset.rows_by_group.items():
        selected_task_ids = {str(row["imported_task_id"]) for row in rows}
        source_jsonl = source_dataset_root / "eval_manifests" / f"{group_name}.jsonl"
        eval_rows = [
            row
            for row in read_jsonl(source_jsonl)
            if str(row.get("imported_task_id")) in selected_task_ids
        ]
        write_jsonl(eval_rows, eval_root / f"{group_name}.jsonl")
        (eval_root / f"{group_name}.task_ids").write_text(
            "".join(f"{row['imported_task_id']}\n" for row in rows),
            encoding="utf-8",
        )


def write_verifier_jsonls(
    source_dataset_root: Path,
    target_dataset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    verifier_root = target_dataset_root / "verifiers"
    verifier_root.mkdir(parents=True, exist_ok=True)
    for group_name, rows in selected_dataset.rows_by_group.items():
        selected_task_ids = {str(row["imported_task_id"]) for row in rows}
        source_jsonl = source_dataset_root / "verifiers" / f"{group_name}.jsonl"
        verifier_rows = [
            row
            for row in read_jsonl(source_jsonl)
            if str(row.get("imported_task_id")) in selected_task_ids
        ]
        write_jsonl(verifier_rows, verifier_root / f"{group_name}.jsonl")


def write_dataset_index_files(
    source_root: Path,
    subset_root: Path,
    selected_dataset: SelectedDataset,
) -> None:
    dataset_name = selected_dataset.name
    selected_task_ids = selected_dataset.task_ids
    source_dataset_root = source_root / dataset_name
    target_dataset_root = subset_root / dataset_name

    jsonl_rows = [
        row
        for row in read_jsonl(source_dataset_root / "dataset_index.jsonl")
        if str(row.get("task_id")) in selected_task_ids
    ]
    write_jsonl(jsonl_rows, target_dataset_root / "dataset_index.jsonl")

    csv_rows = read_csv(source_dataset_root / "dataset_index.csv")
    write_csv(
        [row for row in csv_rows if str(row.get("task_id")) in selected_task_ids],
        target_dataset_root / "dataset_index.csv",
        fieldnames=csv_rows[0].keys() if csv_rows else (),
    )


def write_root_dataset_index(
    *,
    source_root: Path,
    subset_root: Path,
    selected: dict[str, SelectedDataset],
) -> None:
    selected_task_ids = set().union(*(dataset.task_ids for dataset in selected.values()))

    jsonl_rows = [
        row
        for row in read_jsonl(source_root / "dataset_index.jsonl")
        if str(row.get("task_id")) in selected_task_ids
    ]
    write_jsonl(jsonl_rows, subset_root / "dataset_index.jsonl")

    csv_rows = read_csv(source_root / "dataset_index.csv")
    write_csv(
        [row for row in csv_rows if str(row.get("task_id")) in selected_task_ids],
        subset_root / "dataset_index.csv",
        fieldnames=csv_rows[0].keys() if csv_rows else (),
    )


def write_dataset_manifest(
    *,
    source_dataset_root: Path,
    target_dataset_root: Path,
    subset_name: str,
    seed: str,
    selected_dataset: SelectedDataset,
) -> None:
    manifest = json.loads((source_dataset_root / "manifest.json").read_text(encoding="utf-8"))
    original_group_counts = manifest.get("group_counts")
    manifest["title"] = f"{manifest.get('title', selected_dataset.name)} ({subset_name})"
    manifest["description"] = (
        f"Deterministic {subset_name} subset of {selected_dataset.name} from ClawBenchPro."
    )
    manifest["task_count"] = len(selected_dataset.rows)
    manifest["group_counts"] = selected_dataset.group_counts
    manifest["subset"] = {
        "name": subset_name,
        "source_dataset": selected_dataset.name,
        "source_task_count": sum(original_group_counts.values())
        if isinstance(original_group_counts, dict)
        else None,
        "seed": seed,
        "strategy": (
            "stable sha256 sample per dataset/group after excluding tasks whose "
            "verifier JSONL record does not contain an executable same-group "
            "verifier and known context-limit outliers; smaller subsets are "
            "prefixes of larger quotas"
        ),
        "excluded_imported_task_ids": selected_dataset.excluded_imported_task_ids,
    }
    manifest["verifiers"] = {
        group_name: f"verifiers/{group_name}.jsonl"
        for group_name in selected_dataset.rows_by_group
    }
    manifest["eval_manifests"] = {
        group_name: {
            "jsonl": f"eval_manifests/{group_name}.jsonl",
            "task_ids": f"eval_manifests/{group_name}.task_ids",
        }
        for group_name in selected_dataset.rows_by_group
    }
    write_json(target_dataset_root / "manifest.json", manifest)


def write_root_manifest(
    *,
    source_root: Path,
    subset_root: Path,
    subset_name: str,
    seed: str,
    built_datasets: list[BuiltDataset],
) -> None:
    manifest = json.loads((source_root / "manifest.json").read_text(encoding="utf-8"))
    manifest["package_name"] = f"ClawBenchPro_{subset_name}"
    manifest["source_package"] = "ClawBenchPro"
    manifest["subset"] = {
        "name": subset_name,
        "seed": seed,
        "strategy": (
            "stable sha256 sample per dataset/group after excluding tasks whose "
            "verifier JSONL record does not contain an executable same-group "
            "verifier and known context-limit outliers; smaller subsets are "
            "prefixes of larger quotas"
        ),
        "excluded_imported_task_ids": sorted(
            {
                task_id
                for dataset in built_datasets
                for task_id in dataset.excluded_imported_task_ids
            }
        ),
        "task_count": sum(dataset.task_count for dataset in built_datasets),
    }
    manifest["datasets"] = [
        {
            "name": dataset.name,
            "title": dataset.title,
            "root": dataset.name,
            "task_count": dataset.task_count,
            "group_counts": dataset.group_counts,
            "files": dataset.files,
            "bytes": dataset.bytes,
            "checksums": f"{dataset.name}/checksums.sha256",
            "verifiers": f"{dataset.name}/verifiers",
        }
        for dataset in built_datasets
    ]
    write_json(subset_root / "manifest.json", manifest)


def write_subset_readme(
    source_readme: Path,
    target_readme: Path,
    *,
    subset_name: str,
    selected: dict[str, SelectedDataset],
) -> None:
    total = sum(len(dataset.rows) for dataset in selected.values())
    lines = [
        f"# ClawBenchPro {subset_name}",
        "",
        f"This package is a deterministic {total}-task subset of ClawBenchPro.",
        "",
        "## Subset Counts",
        "",
    ]
    for dataset_name, dataset in selected.items():
        lines.append(f"- `{dataset_name}`: {len(dataset.rows)}")
        for group_name, rows in dataset.rows_by_group.items():
            lines.append(f"  - `{group_name}`: {len(rows)}")
    lines.extend(["", "## Source README", ""])
    if source_readme.is_file():
        lines.append(source_readme.read_text(encoding="utf-8"))
    target_readme.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_checksums(root: Path, output_path: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output_path:
            continue
        rows.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    output_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def print_summary(selections: dict[str, dict[str, SelectedDataset]]) -> None:
    for subset_name, selected in selections.items():
        print(f"{subset_name}: {sum(len(dataset.rows) for dataset in selected.values())}")
        for dataset_name, dataset in selected.items():
            print(f"  {dataset_name}: {len(dataset.rows)}")
            for group_name, rows in dataset.rows_by_group.items():
                print(f"    {group_name}: {len(rows)}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(rows: list[dict[str, str]], path: Path, *, fieldnames: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def is_real_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    return not value.startswith("<")


def copy_file_if_exists(source: Path, target: Path) -> None:
    if source.is_file():
        copy_file(source, target)


def copy_tree_if_exists(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)


def count_files(root: Path) -> tuple[int, int]:
    files = 0
    bytes_total = 0
    for path in root.rglob("*"):
        if path.is_file():
            files += 1
            bytes_total += path.stat().st_size
    return files, bytes_total


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
