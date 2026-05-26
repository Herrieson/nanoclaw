from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.workplace_trace_evaluator import extract_file_blocks


DEFAULT_CLAWBENCHPRO_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "ClawBenchPro"
DEFAULT_YUNWU_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "dataset_for_benchmark" / "yunwu"
DEFAULT_LEGACY_TODO_ROOT = REPO_ROOT.parent / "nanoclaw_datasets" / "nanoclaw" / "doc" / "todo"

DATASETS = ("round_01_aligned_mix_800", "persona_aligned_mix_200")
RAW_OUTPUT_KEYS = ("dual_verified_raw_output", "raw_output", "enhanced_raw_output")
RAW_OUTPUT_PRIORITY = {key: index for index, key in enumerate(RAW_OUTPUT_KEYS)}

GROUP_SOURCE_HINTS = {
    ("round_01_aligned_mix_800", "base"): (
        "gemini3_2000_score_new_verifier_1.jsonl",
        "gemini3_2000_score_new_verifier_2.jsonl",
        "gemini3_2000_score_new_verifier_3.jsonl",
        "all_outputs_for_copy_0427_new_verifier/",
    ),
    ("round_01_aligned_mix_800", "hard_aligned"): (
        "gemini3_2000_score_new_verifier_hard_",
        "all_outputs_for_copy_0427_废土版_new_verifier/",
        "all_outputs_for_copy_0427_new_verifier/",
    ),
    ("round_01_aligned_mix_800", "multi_turn_aligned"): (
        "gemini3_2000_score_new_verifier_multi_turn_",
        # Workplace state is the same target surface as the base task when
        # multi-turn only changes prompt/session structure.
        "all_outputs_for_copy_0427_new_verifier/",
    ),
    ("round_01_aligned_mix_800", "skills_aligned"): (
        "gemini3_2000_skills_score_new_verifier_",
        "enhanced_tasks_with_skills_0427_new_verifier/",
        "all_outputs_for_copy_0427_new_verifier/",
    ),
    ("persona_aligned_mix_200", "base"): ("专业人士版/基础数据.jsonl",),
    ("persona_aligned_mix_200", "multi_turn"): (
        "专业人士版/multi_turn.jsonl",
        "专业人士版/基础数据.jsonl",
    ),
    ("persona_aligned_mix_200", "hard"): ("专业人士版/废土版.jsonl",),
    ("persona_aligned_mix_200", "skills"): ("专业人士版/带skill版.jsonl",),
}


@dataclass(frozen=True, slots=True)
class TaskRef:
    dataset: str
    group: str
    source_task_id: str
    imported_task_id: str
    task_dir: str


@dataclass(frozen=True, slots=True)
class VerifierCandidate:
    source_task_id: str
    source_path: Path
    display_path: str
    raw_output_key: str
    line_number: int
    block_path: str
    script_text: str


@dataclass(frozen=True, slots=True)
class MaterializedVerifier:
    task: TaskRef
    candidate: VerifierCandidate


def main() -> int:
    args = build_parser().parse_args()
    clawbenchpro_root = args.clawbenchpro_root.expanduser().resolve()
    source_roots = resolve_source_roots(args.source_root)
    datasets = tuple(args.datasets or DATASETS)

    task_refs = load_task_refs(clawbenchpro_root, datasets)
    candidates = index_workplace_verifiers(source_roots)
    materialized, missing = select_materialized_verifiers(task_refs, candidates)

    print_summary(materialized, missing, source_roots)
    if missing and not args.allow_missing:
        return 1

    if not args.write:
        print("Dry run only. Re-run with --write to materialize files.")
        return 0

    if not args.task_files and not args.verifier_jsonl:
        raise SystemExit("Nothing to write: both --no-task-files and --no-verifier-jsonl were set.")

    if args.task_files:
        write_task_local_verifiers(clawbenchpro_root, materialized)
    if args.verifier_jsonl:
        write_group_verifier_jsonl(clawbenchpro_root, materialized)
    if args.refresh_metadata:
        refresh_dataset_manifests(clawbenchpro_root, datasets)
        refresh_root_manifest(clawbenchpro_root, datasets)
        write_checksums(clawbenchpro_root, datasets)

    print(f"Wrote {len(materialized)} workplace verifier(s) under {clawbenchpro_root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize ClawBenchPro verify_workplace.py files from raw verifier JSONL sources. "
            "Defaults to dry-run coverage reporting."
        )
    )
    parser.add_argument(
        "--clawbenchpro-root",
        type=Path,
        default=DEFAULT_CLAWBENCHPRO_ROOT,
        help=f"ClawBenchPro root. Default: {DEFAULT_CLAWBENCHPRO_ROOT}",
    )
    parser.add_argument(
        "--source-root",
        action="append",
        type=Path,
        default=None,
        help=(
            "Raw verifier source directory or JSONL file. Can be repeated. "
            "Defaults to yunwu plus legacy doc/todo when present."
        ),
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        choices=DATASETS,
        default=None,
        help="Datasets to materialize. Defaults to all ClawBenchPro datasets.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write files. Without this flag the script only reports coverage.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not fail when some task verifiers are missing.",
    )
    parser.add_argument(
        "--no-task-files",
        dest="task_files",
        action="store_false",
        help="Do not write task-local tasks/<task_id>/verify_workplace.py files.",
    )
    parser.add_argument(
        "--no-verifier-jsonl",
        dest="verifier_jsonl",
        action="store_false",
        help="Do not write dataset-local verifiers/<group>.jsonl files.",
    )
    parser.add_argument(
        "--no-refresh-metadata",
        dest="refresh_metadata",
        action="store_false",
        help="Do not refresh manifest.json and checksums.sha256 files after writing.",
    )
    parser.set_defaults(task_files=True, verifier_jsonl=True, refresh_metadata=True)
    return parser


def resolve_source_roots(raw_roots: list[Path] | None) -> list[Path]:
    if raw_roots:
        roots = [path.expanduser().resolve() for path in raw_roots]
    else:
        roots = [
            path.resolve()
            for path in (DEFAULT_YUNWU_ROOT, DEFAULT_LEGACY_TODO_ROOT)
            if path.exists()
        ]
    if not roots:
        raise SystemExit("No verifier source roots were found. Pass --source-root explicitly.")
    return roots


def load_task_refs(clawbenchpro_root: Path, datasets: tuple[str, ...]) -> list[TaskRef]:
    refs: list[TaskRef] = []
    for dataset in datasets:
        manifest_path = clawbenchpro_root / dataset / "import_manifest.jsonl"
        if not manifest_path.is_file():
            raise SystemExit(f"Missing import manifest: {manifest_path}")
        with manifest_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                try:
                    refs.append(
                        TaskRef(
                            dataset=dataset,
                            group=str(payload["group"]),
                            source_task_id=str(payload["source_task_id"]),
                            imported_task_id=str(payload["imported_task_id"]),
                            task_dir=str(payload["task_dir"]),
                        )
                    )
                except KeyError as exc:
                    raise ValueError(f"{manifest_path}:{line_number} missing key {exc}") from exc
    return refs


def index_workplace_verifiers(source_roots: list[Path]) -> dict[str, list[VerifierCandidate]]:
    candidates: dict[str, list[VerifierCandidate]] = {}
    for source_root in source_roots:
        jsonl_paths = [source_root] if source_root.is_file() else sorted(source_root.rglob("*.jsonl"))
        for jsonl_path in jsonl_paths:
            try:
                with jsonl_path.open("r", encoding="utf-8") as handle:
                    for line_number, raw_line in enumerate(handle, start=1):
                        line = raw_line.strip()
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        for raw_output_key in RAW_OUTPUT_KEYS:
                            raw_output = payload.get(raw_output_key)
                            if not isinstance(raw_output, str) or not raw_output.strip():
                                continue
                            for block_path, script_text in extract_file_blocks(raw_output).items():
                                if not block_path.endswith("verify_workplace.py"):
                                    continue
                                source_task_id = source_task_id_from_path(block_path)
                                if source_task_id is None:
                                    continue
                                candidate = VerifierCandidate(
                                    source_task_id=source_task_id,
                                    source_path=jsonl_path,
                                    display_path=display_path(jsonl_path, source_root),
                                    raw_output_key=raw_output_key,
                                    line_number=line_number,
                                    block_path=block_path,
                                    script_text=ensure_trailing_newline(script_text),
                                )
                                candidates.setdefault(source_task_id, []).append(candidate)
            except UnicodeDecodeError:
                continue
    return candidates


def source_task_id_from_path(block_path: str) -> str | None:
    for part in block_path.split("/"):
        if re.fullmatch(r"data_\d+", part):
            return part
    return None


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def select_materialized_verifiers(
    refs: list[TaskRef],
    candidates: dict[str, list[VerifierCandidate]],
) -> tuple[list[MaterializedVerifier], list[TaskRef]]:
    materialized: list[MaterializedVerifier] = []
    missing: list[TaskRef] = []
    for ref in refs:
        candidate = select_candidate(ref, candidates.get(ref.source_task_id, []))
        if candidate is None:
            missing.append(ref)
            continue
        materialized.append(MaterializedVerifier(task=ref, candidate=candidate))
    return materialized, missing


def select_candidate(ref: TaskRef, candidates: list[VerifierCandidate]) -> VerifierCandidate | None:
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate_rank(ref, candidate))


def candidate_rank(ref: TaskRef, candidate: VerifierCandidate) -> tuple[int, int, int, str, int]:
    hints = GROUP_SOURCE_HINTS.get((ref.dataset, ref.group), ())
    hint_index = next(
        (index for index, hint in enumerate(hints) if hint in candidate.display_path),
        len(hints),
    )
    block_path_priority = 0 if candidate.block_path.startswith("scripts/") else 1
    return (
        hint_index,
        RAW_OUTPUT_PRIORITY.get(candidate.raw_output_key, len(RAW_OUTPUT_PRIORITY)),
        block_path_priority,
        candidate.display_path,
        candidate.line_number,
    )


def write_task_local_verifiers(root: Path, materialized: list[MaterializedVerifier]) -> None:
    for item in materialized:
        task = item.task
        text = replace_task_id_references(
            item.candidate.script_text,
            source_task_id=task.source_task_id,
            imported_task_id=task.imported_task_id,
        )
        output_path = root / task.dataset / task.task_dir / "verify_workplace.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


def write_group_verifier_jsonl(root: Path, materialized: list[MaterializedVerifier]) -> None:
    grouped: dict[tuple[str, str], list[MaterializedVerifier]] = {}
    for item in materialized:
        grouped.setdefault((item.task.dataset, item.task.group), []).append(item)

    for (dataset, group), items in grouped.items():
        output_path = root / dataset / "verifiers" / f"{group}.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for item in sorted(items, key=lambda value: value.task.imported_task_id):
            task = item.task
            candidate = item.candidate
            raw_output = (
                "```python\n"
                f"# scripts/{task.source_task_id}/verify_workplace.py\n"
                f"{candidate.script_text.rstrip()}\n"
                "```\n"
            )
            rows.append(
                {
                    "dataset": task.dataset,
                    "group": task.group,
                    "source_task_id": task.source_task_id,
                    "imported_task_id": task.imported_task_id,
                    "verifier_source_path": candidate.source_path.as_posix(),
                    "verifier_source_line": candidate.line_number,
                    "verifier_source_field": candidate.raw_output_key,
                    "verifier_block_path": candidate.block_path,
                    "raw_output": raw_output,
                }
            )
        output_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )


def replace_task_id_references(text: str, *, source_task_id: str, imported_task_id: str) -> str:
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(source_task_id)}(?![A-Za-z0-9_])"
    )
    return pattern.sub(imported_task_id, text)


def refresh_dataset_manifests(root: Path, datasets: tuple[str, ...]) -> None:
    for dataset in datasets:
        dataset_root = root / dataset
        manifest_path = dataset_root / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files, bytes_total = count_files(dataset_root)
        manifest["files"] = {
            "count": files,
            "bytes": bytes_total,
            "checksums": "checksums.sha256",
        }
        groups = manifest.get("group_order") or list(manifest.get("group_counts", {}).keys())
        manifest["verifiers"] = {
            group: f"verifiers/{group}.jsonl"
            for group in groups
            if (dataset_root / "verifiers" / f"{group}.jsonl").is_file()
        }
        write_json(manifest_path, manifest)


def refresh_root_manifest(root: Path, datasets: tuple[str, ...]) -> None:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_name = {item.get("name"): item for item in manifest.get("datasets", []) if isinstance(item, dict)}
    for dataset in datasets:
        dataset_root = root / dataset
        entry = by_name.get(dataset)
        if entry is None or not dataset_root.is_dir():
            continue
        files, bytes_total = count_files(dataset_root)
        entry["files"] = files
        entry["bytes"] = bytes_total
        entry["checksums"] = f"{dataset}/checksums.sha256"
        entry["verifiers"] = f"{dataset}/verifiers"
    write_json(manifest_path, manifest)


def write_checksums(root: Path, datasets: tuple[str, ...]) -> None:
    for dataset in datasets:
        dataset_root = root / dataset
        if dataset_root.is_dir():
            write_checksums_for_root(dataset_root, dataset_root / "checksums.sha256")
    write_checksums_for_root(root, root / "checksums.sha256")


def write_checksums_for_root(root: Path, output_path: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output_path:
            continue
        rows.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    output_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_files(root: Path) -> tuple[int, int]:
    file_count = 0
    byte_count = 0
    for path in root.rglob("*"):
        if path.is_file():
            file_count += 1
            byte_count += path.stat().st_size
    return file_count, byte_count


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_summary(
    materialized: list[MaterializedVerifier],
    missing: list[TaskRef],
    source_roots: list[Path],
) -> None:
    print("Source roots:")
    for root in source_roots:
        print(f"  - {root}")

    totals: dict[tuple[str, str], int] = {}
    selected: dict[tuple[str, str, str], int] = {}
    for item in materialized:
        key = (item.task.dataset, item.task.group)
        totals[key] = totals.get(key, 0) + 1
        selected_key = (*key, source_bucket(item.candidate.display_path))
        selected[selected_key] = selected.get(selected_key, 0) + 1

    print(f"Covered workplace verifiers: {len(materialized)}")
    print(f"Missing workplace verifiers: {len(missing)}")
    for key in sorted(totals):
        print(f"  {key[0]}/{key[1]}: {totals[key]}")

    print("Selected source buckets:")
    for key in sorted(selected):
        dataset, group, bucket = key
        print(f"  {dataset}/{group}: {bucket} -> {selected[key]}")

    if missing:
        print("Missing examples:")
        for ref in missing[:20]:
            print(f"  {ref.dataset}/{ref.group}: {ref.source_task_id} -> {ref.imported_task_id}")


def source_bucket(display_path_value: str) -> str:
    parts = display_path_value.split("/")
    return parts[0] if len(parts) > 1 else display_path_value


if __name__ == "__main__":
    raise SystemExit(main())
