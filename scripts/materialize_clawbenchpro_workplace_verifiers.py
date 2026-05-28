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
OUTPUT_MARKERS = ("workplace_score", "verify_result", "state.json", "total_score")

# These hints are intentionally group-exact. Do not add base/hard/skills fallback
# paths here unless --allow-cross-group-copy style behavior is explicitly needed.
GROUP_SOURCE_HINTS = {
    ("round_01_aligned_mix_800", "base"): (
        "all_outputs_for_copy_0427_new_verifier/",
        "gemini3_2000_score_new_verifier_",
    ),
    ("round_01_aligned_mix_800", "hard_aligned"): (
        "all_outputs_for_copy_0427_废土版_new_verifier/",
        "gemini3_2000_score_new_verifier_hard_",
    ),
    ("round_01_aligned_mix_800", "multi_turn_aligned"): (
        "all_outputs_multi_turn_0428_new_verifier/",
        "gemini3_2000_score_new_verifier_multi_turn_",
    ),
    ("round_01_aligned_mix_800", "skills_aligned"): (
        "enhanced_tasks_with_skills_0427_new_verifier/",
        "gemini3_2000_skills_score_new_verifier_",
    ),
    ("persona_aligned_mix_200", "base"): ("专业人士版/基础数据.jsonl",),
    ("persona_aligned_mix_200", "hard"): ("专业人士版/废土版.jsonl",),
    ("persona_aligned_mix_200", "multi_turn"): ("专业人士版/multi_turn.jsonl",),
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
    workplace_block_path: str | None
    workplace_script: str | None
    trace_prompt: str | None
    turn_scripts: dict[int, str]
    turn_trace_prompts: dict[int, str]
    workplace_reasons: tuple[str, ...]
    turn_reasons: tuple[str, ...]

    @property
    def has_valid_workplace(self) -> bool:
        return self.workplace_script is not None and not self.workplace_reasons

    @property
    def has_valid_turns(self) -> bool:
        return bool(self.turn_scripts) and not self.turn_reasons


@dataclass(frozen=True, slots=True)
class MaterializedVerifier:
    task: TaskRef
    action: str
    candidate: VerifierCandidate | None
    reasons: tuple[str, ...]


def main() -> int:
    args = build_parser().parse_args()
    clawbenchpro_root = args.clawbenchpro_root.expanduser().resolve()
    source_roots = resolve_source_roots(args.source_root)
    datasets = tuple(args.datasets or DATASETS)

    task_refs = load_task_refs(clawbenchpro_root, datasets)
    candidates = index_verifier_candidates(source_roots)
    materialized, missing = select_materialized_verifiers(
        task_refs,
        candidates,
        fallback_invalid=not args.no_fallback_invalid,
    )

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
    write_provenance_manifests(clawbenchpro_root, datasets, materialized)
    if args.refresh_metadata:
        refresh_dataset_manifests(clawbenchpro_root, datasets)
        refresh_root_manifest(clawbenchpro_root, datasets)
        write_checksums(clawbenchpro_root, datasets)

    print(f"Wrote {len(materialized)} verifier record(s) under {clawbenchpro_root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize ClawBenchPro verifier records from raw JSONL sources. "
            "Default policy is group-exact: base/hard/multi_turn/skills do not copy "
            "verifiers from each other. Multi-turn tasks use original per-turn verifier scripts."
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
    parser.add_argument("--write", action="store_true", help="Write files.")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not fail when --no-fallback-invalid leaves some task verifiers missing.",
    )
    parser.add_argument(
        "--no-fallback-invalid",
        action="store_true",
        help="Do not write conservative zero-score fallback records for missing/invalid raw verifiers.",
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


def index_verifier_candidates(source_roots: list[Path]) -> dict[str, list[VerifierCandidate]]:
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
                            candidate = candidate_from_raw_output(
                                source_root=source_root,
                                jsonl_path=jsonl_path,
                                line_number=line_number,
                                raw_output_key=raw_output_key,
                                raw_output=raw_output,
                                payload=payload,
                            )
                            if candidate is None:
                                continue
                            candidates.setdefault(candidate.source_task_id, []).append(candidate)
            except UnicodeDecodeError:
                continue
    for candidate_list in candidates.values():
        candidate_list.sort(key=lambda candidate: (candidate.display_path, candidate.line_number))
    return candidates


def candidate_from_raw_output(
    *,
    source_root: Path,
    jsonl_path: Path,
    line_number: int,
    raw_output_key: str,
    raw_output: str,
    payload: dict[str, Any],
) -> VerifierCandidate | None:
    blocks = extract_file_blocks(raw_output)
    source_task_id = source_task_id_from_blocks(blocks) or payload_source_task_id(payload)
    if source_task_id is None:
        return None

    workplace_block_path, workplace_script = first_workplace_block(blocks, source_task_id=source_task_id)
    trace_prompt = first_trace_prompt(blocks, source_task_id=source_task_id)
    turn_scripts = extract_turn_scripts(blocks, source_task_id=source_task_id)
    turn_trace_prompts = extract_turn_trace_prompts(blocks, source_task_id=source_task_id)

    if workplace_script is None and not turn_scripts:
        return None

    workplace_reasons = (
        validate_python_verifier(workplace_script, label=workplace_block_path or "verify_workplace.py")
        if workplace_script is not None
        else ("missing_workplace_script",)
    )
    turn_reasons = validate_turn_verifiers(turn_scripts)

    return VerifierCandidate(
        source_task_id=source_task_id,
        source_path=jsonl_path,
        display_path=display_path(jsonl_path, source_root),
        raw_output_key=raw_output_key,
        line_number=line_number,
        workplace_block_path=workplace_block_path,
        workplace_script=(
            ensure_trailing_newline(
                apply_known_workplace_repairs(
                    workplace_script,
                    source_task_id=source_task_id,
                    block_path=workplace_block_path,
                )
            )
            if workplace_script is not None
            else None
        ),
        trace_prompt=ensure_trailing_newline(trace_prompt) if trace_prompt is not None else None,
        turn_scripts={turn: ensure_trailing_newline(text) for turn, text in turn_scripts.items()},
        turn_trace_prompts={turn: ensure_trailing_newline(text) for turn, text in turn_trace_prompts.items()},
        workplace_reasons=workplace_reasons,
        turn_reasons=turn_reasons,
    )


def apply_known_workplace_repairs(
    script_text: str,
    *,
    source_task_id: str,
    block_path: str | None,
) -> str:
    if source_task_id == "data_16" and block_path and block_path.endswith("verify_workplace.py"):
        # The raw verifier used os.path.exists() before opening fix_list/target.json.
        # If an agent creates a directory at that path, evaluation should assign
        # zero/partial credit instead of crashing with IsADirectoryError.
        return script_text.replace(
            "if os.path.exists(target_file):\n"
            "        score += 15\n"
            "        details.append({\"item\": \"检查目标文件是否存在\", \"score\": 15, \"max_score\": 15, \"passed\": True, \"reason\": \"文件 fix_list/target.json 存在\"})\n"
            "    else:\n"
            "        details.append({\"item\": \"检查目标文件是否存在\", \"score\": 0, \"max_score\": 15, \"passed\": False, \"reason\": \"文件 fix_list/target.json 不存在\"})",
            "if os.path.isfile(target_file):\n"
            "        score += 15\n"
            "        details.append({\"item\": \"检查目标文件是否存在\", \"score\": 15, \"max_score\": 15, \"passed\": True, \"reason\": \"文件 fix_list/target.json 存在且是普通文件\"})\n"
            "    else:\n"
            "        reason = \"文件 fix_list/target.json 不存在\" if not os.path.exists(target_file) else \"fix_list/target.json 是目录或非普通文件\"\n"
            "        details.append({\"item\": \"检查目标文件是否存在\", \"score\": 0, \"max_score\": 15, \"passed\": False, \"reason\": reason})",
        )
    return script_text


def source_task_id_from_blocks(blocks: dict[str, str]) -> str | None:
    for block_path in blocks:
        task_id = source_task_id_from_path(block_path)
        if task_id is not None:
            return task_id
    return None


def source_task_id_from_path(block_path: str) -> str | None:
    for part in block_path.split("/"):
        if re.fullmatch(r"data_\d+", part):
            return part
    return None


def payload_source_task_id(payload: dict[str, Any]) -> str | None:
    task_id = payload.get("task_id")
    if isinstance(task_id, str) and re.fullmatch(r"data_\d+", task_id.strip()):
        return task_id.strip()
    return None


def first_workplace_block(
    blocks: dict[str, str],
    *,
    source_task_id: str,
) -> tuple[str | None, str | None]:
    preferred = (
        f"scripts/{source_task_id}/verify_workplace.py",
        f"tasks/{source_task_id}/verify_workplace.py",
        f"tasks/{source_task_id}/verify_rules.py",
    )
    for block_path in preferred:
        script = blocks.get(block_path)
        if script is not None:
            return block_path, script
    for block_path, script in blocks.items():
        if block_path.endswith("/verify_workplace.py") or block_path.endswith("/verify_rules.py"):
            return block_path, script
    return None, None


def first_trace_prompt(blocks: dict[str, str], *, source_task_id: str) -> str | None:
    for block_path in (
        f"scripts/{source_task_id}/verify_trace.md",
        f"tasks/{source_task_id}/verify_trace.md",
        f"tasks/{source_task_id}/verify_prompt.md",
    ):
        value = blocks.get(block_path)
        if value is not None:
            return value
    return None


def extract_turn_scripts(blocks: dict[str, str], *, source_task_id: str) -> dict[int, str]:
    scripts: dict[int, str] = {}
    for block_path, script in blocks.items():
        match = re.fullmatch(
            rf"scripts/{re.escape(source_task_id)}/verify_turn_(\d+)\.py",
            block_path,
        )
        if match:
            scripts[int(match.group(1))] = script
    return dict(sorted(scripts.items()))


def extract_turn_trace_prompts(blocks: dict[str, str], *, source_task_id: str) -> dict[int, str]:
    prompts: dict[int, str] = {}
    for block_path, prompt in blocks.items():
        match = re.fullmatch(
            rf"scripts/{re.escape(source_task_id)}/verify_trace_turn_(\d+)\.md",
            block_path,
        )
        if match:
            prompts[int(match.group(1))] = prompt
    return dict(sorted(prompts.items()))


def validate_python_verifier(text: str, *, label: str) -> tuple[str, ...]:
    reasons: list[str] = []
    if not text.strip():
        reasons.append("empty")
    if not any(marker in text for marker in OUTPUT_MARKERS):
        reasons.append("missing_score_output_marker")
    try:
        compile(text, label, "exec")
    except SyntaxError as exc:
        reasons.append(f"syntax_error:{exc.msg}:line_{exc.lineno}")
    return tuple(reasons)


def validate_turn_verifiers(turn_scripts: dict[int, str]) -> tuple[str, ...]:
    if not turn_scripts:
        return ("missing_turn_verifiers",)
    reasons: list[str] = []
    for turn, script in sorted(turn_scripts.items()):
        for reason in validate_python_verifier(script, label=f"verify_turn_{turn}.py"):
            reasons.append(f"turn_{turn}:{reason}")
    return tuple(reasons)


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
    *,
    fallback_invalid: bool,
) -> tuple[list[MaterializedVerifier], list[TaskRef]]:
    materialized: list[MaterializedVerifier] = []
    missing: list[TaskRef] = []
    for ref in refs:
        selected = select_candidate(ref, candidates.get(ref.source_task_id, []))
        if selected is not None:
            materialized.append(selected)
            continue
        if not fallback_invalid:
            missing.append(ref)
            continue
        same_group_candidates = same_group_candidates_for_ref(ref, candidates.get(ref.source_task_id, []))
        fallback_candidate = same_group_candidates[0] if same_group_candidates else None
        reasons = fallback_reasons(ref, fallback_candidate)
        materialized.append(
            MaterializedVerifier(
                task=ref,
                action=fallback_action(reasons),
                candidate=fallback_candidate,
                reasons=reasons,
            )
        )
    return materialized, missing


def select_candidate(ref: TaskRef, candidates: list[VerifierCandidate]) -> MaterializedVerifier | None:
    exact_candidates = same_group_candidates_for_ref(ref, candidates)
    if is_multi_turn_group(ref.group):
        for candidate in exact_candidates:
            if candidate.has_valid_turns:
                return MaterializedVerifier(
                    task=ref,
                    action="same_group_raw_turn_verifiers",
                    candidate=candidate,
                    reasons=(),
                )
        return None

    for candidate in exact_candidates:
        if candidate.has_valid_workplace:
            return MaterializedVerifier(
                task=ref,
                action="same_group_raw_workplace",
                candidate=candidate,
                reasons=(),
            )
    return None


def same_group_candidates_for_ref(
    ref: TaskRef,
    candidates: list[VerifierCandidate],
) -> list[VerifierCandidate]:
    hints = GROUP_SOURCE_HINTS.get((ref.dataset, ref.group), ())
    if not hints:
        return []
    exact = [
        candidate
        for candidate in candidates
        if any(hint in candidate.display_path for hint in hints)
    ]
    return sorted(exact, key=lambda candidate: candidate_rank(ref, candidate))


def candidate_rank(ref: TaskRef, candidate: VerifierCandidate) -> tuple[int, int, int, str, int]:
    hints = GROUP_SOURCE_HINTS.get((ref.dataset, ref.group), ())
    hint_index = next(
        (index for index, hint in enumerate(hints) if hint in candidate.display_path),
        len(hints),
    )
    block_path_priority = 0 if (candidate.workplace_block_path or "").startswith("scripts/") else 1
    return (
        hint_index,
        RAW_OUTPUT_PRIORITY.get(candidate.raw_output_key, len(RAW_OUTPUT_PRIORITY)),
        block_path_priority,
        candidate.display_path,
        candidate.line_number,
    )


def is_multi_turn_group(group: str) -> bool:
    return "multi_turn" in group


def fallback_reasons(ref: TaskRef, candidate: VerifierCandidate | None) -> tuple[str, ...]:
    if candidate is None:
        return ("raw_record_missing",)
    if is_multi_turn_group(ref.group):
        return candidate.turn_reasons or ("raw_turn_verifier_invalid",)
    return candidate.workplace_reasons or ("raw_workplace_verifier_invalid",)


def fallback_action(reasons: tuple[str, ...]) -> str:
    if any("syntax_error" in reason for reason in reasons):
        return "conservative_fallback_raw_syntax_bad"
    if any("empty" in reason for reason in reasons):
        return "conservative_fallback_raw_empty"
    if any("missing" in reason for reason in reasons):
        return "conservative_fallback_raw_missing"
    return "conservative_fallback_raw_invalid"


def write_task_local_verifiers(root: Path, materialized: list[MaterializedVerifier]) -> None:
    for item in materialized:
        task = item.task
        if item.action == "same_group_raw_workplace" and item.candidate is not None:
            assert item.candidate.workplace_script is not None
            text = replace_task_id_references(
                item.candidate.workplace_script,
                source_task_id=task.source_task_id,
                imported_task_id=task.imported_task_id,
            )
        else:
            text = task_local_fallback_verifier(item)
        output_path = root / task.dataset / task.task_dir / "verify_workplace.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ensure_trailing_newline(text), encoding="utf-8")


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
            rows.append(
                {
                    "dataset": task.dataset,
                    "group": task.group,
                    "source_task_id": task.source_task_id,
                    "imported_task_id": task.imported_task_id,
                    "raw_output": verifier_raw_output(item),
                    "verifier_materialization": materialization_metadata(item),
                }
            )
        output_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )


def verifier_raw_output(item: MaterializedVerifier) -> str:
    task = item.task
    candidate = item.candidate
    if item.action == "same_group_raw_workplace" and candidate is not None:
        assert candidate.workplace_script is not None
        return python_block(
            f"scripts/{task.source_task_id}/verify_workplace.py",
            candidate.workplace_script,
        )
    if item.action == "same_group_raw_turn_verifiers" and candidate is not None:
        blocks: list[str] = []
        for turn, script in sorted(candidate.turn_scripts.items()):
            blocks.append(python_block(f"scripts/{task.source_task_id}/verify_turn_{turn}.py", script))
            trace_prompt = candidate.turn_trace_prompts.get(turn)
            if trace_prompt is not None:
                blocks.append(markdown_block(f"scripts/{task.source_task_id}/verify_trace_turn_{turn}.md", trace_prompt))
        return "\n".join(blocks).rstrip() + "\n"
    return python_block(
        f"scripts/{task.source_task_id}/verify_workplace.py",
        conservative_fallback_verifier(item),
    )


def python_block(relative_path: str, text: str) -> str:
    return f"```python\n# {relative_path}\n{text.rstrip()}\n```\n"


def markdown_block(relative_path: str, text: str) -> str:
    return f"```markdown\n# {relative_path}\n{text.rstrip()}\n```\n"


def materialization_metadata(item: MaterializedVerifier) -> dict[str, Any]:
    candidate = item.candidate
    metadata: dict[str, Any] = {
        "action": item.action,
        "reasons": list(item.reasons),
    }
    if candidate is not None:
        metadata.update(
            {
                "source_path": candidate.source_path.as_posix(),
                "source_line": candidate.line_number,
                "source_field": candidate.raw_output_key,
                "workplace_block_path": candidate.workplace_block_path,
                "turns": sorted(candidate.turn_scripts),
            }
        )
    return metadata


def task_local_fallback_verifier(item: MaterializedVerifier) -> str:
    if item.action == "same_group_raw_turn_verifiers":
        reason = (
            "This multi-turn task is evaluated from the original per-turn verifier "
            "scripts stored in verifiers/*.jsonl. The task-local verify_workplace.py "
            "is intentionally a non-authoritative zero-score fallback."
        )
    else:
        reason = fallback_reason_text(item)
    return conservative_fallback_verifier(item, reason=reason, task_local=True)


def conservative_fallback_verifier(
    item: MaterializedVerifier,
    *,
    reason: str | None = None,
    task_local: bool = False,
) -> str:
    task = item.task
    resolved_reason = reason or fallback_reason_text(item)
    action = "task_local_turn_verifier_placeholder" if task_local and item.action == "same_group_raw_turn_verifiers" else item.action
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
                "item": "verifier_materialization_fallback",
                "score": 0,
                "max_score": 100,
                "passed": False,
                "reason": {resolved_reason!r},
            }}
        ],
        "verifier_materialization": {{
            "dataset": {task.dataset!r},
            "group": {task.group!r},
            "source_task_id": {task.source_task_id!r},
            "imported_task_id": {task.imported_task_id!r},
            "action": {action!r},
        }},
    }}
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
'''


def fallback_reason_text(item: MaterializedVerifier) -> str:
    reasons = "; ".join(item.reasons) if item.reasons else "unknown"
    return (
        "Original same-group verifier could not be materialized as an executable "
        f"workplace verifier. Validation reasons: {reasons}."
    )


def write_provenance_manifests(
    root: Path,
    datasets: tuple[str, ...],
    materialized: list[MaterializedVerifier],
) -> None:
    by_dataset: dict[str, list[MaterializedVerifier]] = {dataset: [] for dataset in datasets}
    for item in materialized:
        by_dataset.setdefault(item.task.dataset, []).append(item)

    for dataset, items in by_dataset.items():
        dataset_root = root / dataset
        materialization_rows = [provenance_row(item) for item in items]
        write_jsonl(
            materialization_rows,
            dataset_root / "provenance" / "verifier_materialization_manifest.jsonl",
        )
        repair_rows = [
            row
            for row in materialization_rows
            if str(row.get("repair_action", "")).startswith("conservative_fallback")
        ]
        repair_path = dataset_root / "provenance" / "verifier_repair_manifest.jsonl"
        if repair_rows:
            write_jsonl(repair_rows, repair_path)
        elif repair_path.exists():
            repair_path.unlink()


def provenance_row(item: MaterializedVerifier) -> dict[str, Any]:
    task = item.task
    candidate = item.candidate
    text = raw_text_for_hash(item)
    row: dict[str, Any] = {
        "dataset": task.dataset,
        "group": task.group,
        "source_task_id": task.source_task_id,
        "imported_task_id": task.imported_task_id,
        "task_dir": task.task_dir,
        "repair_action": item.action,
        "reasons": list(item.reasons),
        "repaired_sha256": sha256_text(text),
    }
    if candidate is not None:
        row.update(
            {
                "verifier_source_path": candidate.source_path.as_posix(),
                "verifier_source_line": candidate.line_number,
                "verifier_source_field": candidate.raw_output_key,
                "verifier_block_path": candidate.workplace_block_path,
                "turns": sorted(candidate.turn_scripts),
            }
        )
    return row


def raw_text_for_hash(item: MaterializedVerifier) -> str:
    candidate = item.candidate
    if item.action == "same_group_raw_workplace" and candidate is not None:
        return candidate.workplace_script or ""
    if item.action == "same_group_raw_turn_verifiers" and candidate is not None:
        return "\n".join(script for _, script in sorted(candidate.turn_scripts.items()))
    return conservative_fallback_verifier(item)


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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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

    action_counts: dict[str, int] = {}
    group_counts: dict[tuple[str, str, str], int] = {}
    source_counts: dict[tuple[str, str, str], int] = {}
    for item in materialized:
        action_counts[item.action] = action_counts.get(item.action, 0) + 1
        group_key = (item.task.dataset, item.task.group, item.action)
        group_counts[group_key] = group_counts.get(group_key, 0) + 1
        if item.candidate is not None:
            source_key = (
                item.task.dataset,
                item.task.group,
                source_bucket(item.candidate.display_path),
            )
            source_counts[source_key] = source_counts.get(source_key, 0) + 1

    print(f"Materialized verifier records: {len(materialized)}")
    print(f"Missing verifier records: {len(missing)}")
    print("Actions:")
    for action in sorted(action_counts):
        print(f"  {action}: {action_counts[action]}")

    print("Actions by group:")
    for dataset, group, action in sorted(group_counts):
        print(f"  {dataset}/{group}: {action} -> {group_counts[(dataset, group, action)]}")

    print("Selected source buckets:")
    for dataset, group, bucket in sorted(source_counts):
        print(f"  {dataset}/{group}: {bucket} -> {source_counts[(dataset, group, bucket)]}")

    if missing:
        print("Missing examples:")
        for ref in missing[:20]:
            print(f"  {ref.dataset}/{ref.group}: {ref.source_task_id} -> {ref.imported_task_id}")


def source_bucket(display_path_value: str) -> str:
    parts = display_path_value.split("/")
    return parts[0] if len(parts) > 1 else display_path_value


if __name__ == "__main__":
    raise SystemExit(main())
