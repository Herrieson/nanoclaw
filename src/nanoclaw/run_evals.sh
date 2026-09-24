#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

RESULTS_ROOT="${RESULTS_ROOT:-results/round_01_aligned_mix_800}"
STAGING_ROOT="${STAGING_ROOT:-.staging/round_01_aligned_mix_800}"
SELECTION_MANIFEST="${SELECTION_MANIFEST:-${STAGING_ROOT}/selection_manifest.jsonl}"
IMPORT_MANIFEST="${IMPORT_MANIFEST:-${STAGING_ROOT}/import_manifest.jsonl}"
GROUP_MANIFEST_ROOT="${GROUP_MANIFEST_ROOT:-${STAGING_ROOT}/eval_manifests}"
OUTPUT_ROOT="${OUTPUT_ROOT:-results/round_01_aligned_mix_800_new_verifier_workplace_only}"
INTERMEDIATE_ROOT="${INTERMEDIATE_ROOT:-${OUTPUT_ROOT}/_group_reports}"
CHART_OUTPUT="${CHART_OUTPUT:-${OUTPUT_ROOT}/model_comparison.svg}"
COMPONENTS="${COMPONENTS:-workplace}"
EVAL_WORKERS="${EVAL_WORKERS:-16}"
SELECT_RUN_PER_TASK="${SELECT_RUN_PER_TASK:-latest-completed}"
ALLOW_ISSUES="${ALLOW_ISSUES:-1}"
ENABLE_JUDGE="${ENABLE_JUDGE:-0}"

EVAL_GROUPS=(
    "multi_turn_aligned"
    "skills_aligned"
    "hard_aligned"
    "base"
)

declare -A VERIFIER_JSONLS
VERIFIER_JSONLS[multi_turn_aligned]="doc/todo/gemini3_2000_score_new_verifier_multi_turn_1.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_2.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_3.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_4.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_5.jsonl"
VERIFIER_JSONLS[skills_aligned]="doc/todo/gemini3_2000_skills_score_new_verifier_1.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_2.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_3.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_4.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_5.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_6.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_7.jsonl"
VERIFIER_JSONLS[hard_aligned]="doc/todo/gemini3_2000_score_new_verifier_hard_1.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_2.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_3.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_4.jsonl"
VERIFIER_JSONLS[base]="doc/todo/gemini3_2000_score_new_verifier_1.jsonl doc/todo/gemini3_2000_score_new_verifier_2.jsonl doc/todo/gemini3_2000_score_new_verifier_3.jsonl"

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

build_group_manifests() {
    # The aligned mix intentionally reuses each source_task_id across four task variants.
    # The verifier loader maps source_task_id -> imported_task_id, so eval needs one
    # manifest per variant group instead of the combined 800-row import manifest.
    uv run python - "${SELECTION_MANIFEST}" "${IMPORT_MANIFEST}" "${GROUP_MANIFEST_ROOT}" "${EVAL_GROUPS[@]}" <<'PY'
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys

selection_path = Path(sys.argv[1])
import_path = Path(sys.argv[2])
output_root = Path(sys.argv[3])
group_order = sys.argv[4:]

if not selection_path.exists():
    raise SystemExit(f"Missing selection manifest: {selection_path}")
if not import_path.exists():
    raise SystemExit(f"Missing import manifest: {import_path}")

selection_rows = [
    json.loads(line)
    for line in selection_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
import_rows = [
    json.loads(line)
    for line in import_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

if len(selection_rows) != len(import_rows):
    raise SystemExit(
        f"Selection/import manifest length mismatch: {len(selection_rows)} != {len(import_rows)}"
    )

rows_by_group: dict[str, list[dict[str, object]]] = defaultdict(list)
task_ids_by_group: dict[str, list[str]] = defaultdict(list)
for line_number, (selection, imported) in enumerate(zip(selection_rows, import_rows), start=1):
    source_task_id = selection.get("source_task_id")
    imported_source_task_id = imported.get("source_task_id")
    imported_task_id = imported.get("imported_task_id")
    group = selection.get("group")
    if source_task_id != imported_source_task_id:
        raise SystemExit(
            f"Manifest source_task_id mismatch at line {line_number}: "
            f"{source_task_id!r} != {imported_source_task_id!r}"
        )
    if not isinstance(group, str) or not group:
        raise SystemExit(f"Missing group in selection manifest at line {line_number}")
    if not isinstance(imported_task_id, str) or not imported_task_id:
        raise SystemExit(f"Missing imported_task_id in import manifest at line {line_number}")
    row = dict(imported)
    row["group"] = group
    row["aligned_index"] = selection.get("aligned_index")
    row["selection_record"] = selection.get("destination_record")
    rows_by_group[group].append(row)
    task_ids_by_group[group].append(imported_task_id)

output_root.mkdir(parents=True, exist_ok=True)
for group in group_order:
    rows = rows_by_group.get(group, [])
    if not rows:
        raise SystemExit(f"No manifest rows found for group: {group}")
    seen_source_ids: set[str] = set()
    duplicate_source_ids: set[str] = set()
    for row in rows:
        source_task_id = str(row.get("source_task_id"))
        if source_task_id in seen_source_ids:
            duplicate_source_ids.add(source_task_id)
        seen_source_ids.add(source_task_id)
    if duplicate_source_ids:
        preview = ", ".join(sorted(duplicate_source_ids)[:10])
        raise SystemExit(f"Duplicate source_task_id values in group {group}: {preview}")

    manifest_path = output_root / f"{group}.jsonl"
    task_ids_path = output_root / f"{group}.task_ids"
    manifest_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    task_ids_path.write_text("\n".join(task_ids_by_group[group]) + "\n", encoding="utf-8")
    print(f"{group}: {len(rows)} task(s), manifest={manifest_path}")
PY
}

discover_model_slugs() {
    MODEL_SLUGS=()
    if [ -n "${MODELS_OVERRIDE:-}" ]; then
        read -r -a REQUESTED_MODELS <<< "${MODELS_OVERRIDE}"
        for MODEL in "${REQUESTED_MODELS[@]}"; do
            MODEL_SLUGS+=("$(slugify_model_name "${MODEL}")")
        done
        return
    fi

    shopt -s nullglob
    for MODEL_DIR in "${RESULTS_ROOT}"/*; do
        if [ -d "${MODEL_DIR}" ]; then
            MODEL_SLUGS+=("$(basename "${MODEL_DIR}")")
        fi
    done
    shopt -u nullglob
}

merge_model_reports() {
    uv run python - "${INTERMEDIATE_ROOT}" "${OUTPUT_ROOT}" "${EVAL_GROUPS[@]}" <<'PY'
from __future__ import annotations

from collections import defaultdict
import csv
import json
from pathlib import Path
import sys
from typing import Any

intermediate_root = Path(sys.argv[1])
output_root = Path(sys.argv[2])
group_names = sys.argv[3:]

fieldnames = [
    "task_id",
    "source_task_id",
    "run_id",
    "run_dir",
    "run_status",
    "run_result_type",
    "model",
    "evaluation_status",
    "workplace_status",
    "workplace_score",
    "workplace_score_source",
    "workplace_exit_code",
    "workplace_error",
    "trace_status",
    "trace_score",
    "trace_model",
    "trace_attempts",
    "trace_error",
    "objective_score",
    "objective_score_source",
    "error",
]


def numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def average(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def csv_row(row: dict[str, Any]) -> dict[str, str]:
    output: dict[str, str] = {}
    for field in fieldnames:
        value = row.get(field)
        output[field] = "" if value is None else str(value)
    return output


model_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
for group in group_names:
    group_root = intermediate_root / group
    if not group_root.exists():
        continue
    for model_dir in sorted(path for path in group_root.iterdir() if path.is_dir()):
        evaluation_path = model_dir / "evaluation.json"
        if not evaluation_path.exists():
            continue
        payload = json.loads(evaluation_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise SystemExit(f"{evaluation_path} is not a JSON array")
        for item in payload:
            if not isinstance(item, dict):
                continue
            item = dict(item)
            item["evaluation_group"] = group
            model_rows[model_dir.name].append(item)

if not model_rows:
    raise SystemExit("No group evaluation reports were found to merge.")

output_root.mkdir(parents=True, exist_ok=True)
for model_name in sorted(model_rows):
    rows = sorted(
        model_rows[model_name],
        key=lambda item: (
            str(item.get("task_id") or ""),
            str(item.get("run_id") or ""),
            str(item.get("evaluation_group") or ""),
        ),
    )
    total_runs = len(rows)
    completed_runs = sum(1 for row in rows if row.get("run_status") == "completed")
    skipped_incomplete_runs = sum(
        1 for row in rows if row.get("evaluation_status") == "skipped_run_not_completed"
    )
    skipped_infra_failure_runs = sum(
        1 for row in rows if row.get("evaluation_status") == "skipped_infra_failure"
    )
    evaluated_runs = sum(1 for row in rows if row.get("evaluation_status") == "evaluated")
    workplace_scores = [
        value
        for value in (numeric(row.get("workplace_score")) for row in rows)
        if value is not None
    ]
    trace_scores = [
        value
        for value in (numeric(row.get("trace_score")) for row in rows)
        if value is not None
    ]
    objective_scores = [
        value
        for row in rows
        if row.get("evaluation_status") == "evaluated"
        for value in [numeric(row.get("objective_score"))]
        if value is not None
    ]
    scored_runs = len(objective_scores)
    perfect_score_runs = sum(1 for score in objective_scores if score == 100.0)
    evaluation_issue_runs = sum(
        1
        for row in rows
        if row.get("evaluation_status")
        not in {"evaluated", "skipped_run_not_completed", "skipped_infra_failure"}
    )
    run_success_rate = round((completed_runs / total_runs) * 100, 2) if total_runs else 0.0
    perfect_score_rate = round((perfect_score_runs / total_runs) * 100, 2) if total_runs else 0.0
    average_objective_score = average(objective_scores)
    summary = {
        "total_runs": total_runs,
        "completed_runs": completed_runs,
        "skipped_incomplete_runs": skipped_incomplete_runs,
        "skipped_infra_failure_runs": skipped_infra_failure_runs,
        "evaluated_runs": evaluated_runs,
        "scored_runs": scored_runs,
        "perfect_score_runs": perfect_score_runs,
        "perfect_score_rate": perfect_score_rate,
        "evaluation_issue_runs": evaluation_issue_runs,
        "run_success_rate": run_success_rate,
        "workplace_scored_runs": len(workplace_scores),
        "trace_scored_runs": len(trace_scores),
        "average_workplace_score": average(workplace_scores),
        "average_trace_score": average(trace_scores),
        "average_objective_score": average_objective_score if average_objective_score is not None else 0.0,
        "benchmark_score": (
            round((run_success_rate / 100.0) * average_objective_score, 2)
            if average_objective_score is not None
            else 0.0
        ),
    }

    model_output_root = output_root / model_name
    model_output_root.mkdir(parents=True, exist_ok=True)
    (model_output_root / "evaluation.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (model_output_root / "evaluation.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(csv_row(row))
    (model_output_root / "evaluation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{model_name}: merged {total_runs} run(s), "
        f"perfect={perfect_score_rate:.2f}%, avg={summary['average_objective_score']:.2f}"
    )
PY
}

if [ ! -d "${RESULTS_ROOT}" ]; then
    echo "[ERROR] Results root does not exist: ${RESULTS_ROOT}"
    exit 1
fi

echo "=================================================="
echo "[INFO] Evaluating aligned mix results"
echo "[INFO] Results root: ${RESULTS_ROOT}"
echo "[INFO] Selection manifest: ${SELECTION_MANIFEST}"
echo "[INFO] Import manifest: ${IMPORT_MANIFEST}"
echo "[INFO] Group manifests: ${GROUP_MANIFEST_ROOT}"
echo "[INFO] Output root: ${OUTPUT_ROOT}"
echo "[INFO] Chart output: ${CHART_OUTPUT}"
echo "[INFO] Components: ${COMPONENTS}"
echo "=================================================="

build_group_manifests || exit 1
discover_model_slugs

if [ ${#MODEL_SLUGS[@]} -eq 0 ]; then
    echo "[ERROR] No model result directories found under ${RESULTS_ROOT}."
    exit 1
fi

EXIT_CODE=0

for MODEL_SLUG in "${MODEL_SLUGS[@]}"; do
    if [ ! -d "${RESULTS_ROOT}/${MODEL_SLUG}" ]; then
        echo "[WARN] Skipping missing model results dir: ${RESULTS_ROOT}/${MODEL_SLUG}"
        continue
    fi

    for GROUP_NAME in "${EVAL_GROUPS[@]}"; do
        TASK_ID_FILE="${GROUP_MANIFEST_ROOT}/${GROUP_NAME}.task_ids"
        GROUP_MANIFEST="${GROUP_MANIFEST_ROOT}/${GROUP_NAME}.jsonl"
        mapfile -t TASK_IDS < "${TASK_ID_FILE}"

        RUN_DIRS=()
        shopt -s nullglob
        for TASK_ID in "${TASK_IDS[@]}"; do
            MATCHES=( "${RESULTS_ROOT}/${MODEL_SLUG}/${TASK_ID}"/* )
            RUN_DIRS+=( "${MATCHES[@]}" )
        done
        shopt -u nullglob

        if [ ${#RUN_DIRS[@]} -eq 0 ]; then
            echo "[WARN] ${MODEL_SLUG}/${GROUP_NAME}: no run dirs matched; skipping."
            continue
        fi

        read -r -a GROUP_VERIFIERS <<< "${VERIFIER_JSONLS[${GROUP_NAME}]}"
        GROUP_OUTPUT_DIR="${INTERMEDIATE_ROOT}/${GROUP_NAME}/${MODEL_SLUG}"

        echo "=================================================="
        echo "[INFO] Evaluating ${MODEL_SLUG}/${GROUP_NAME}"
        echo "[INFO] Matched run dirs: ${#RUN_DIRS[@]}"
        echo "[INFO] Output dir: ${GROUP_OUTPUT_DIR}"
        echo "=================================================="

        EVAL_ARGS=(
            scripts/evaluate_workplace_trace_tasks.py
            "${RUN_DIRS[@]}"
            --verifier-jsonl "${GROUP_VERIFIERS[@]}"
            --manifest "${GROUP_MANIFEST}"
            --components "${COMPONENTS}"
            --workers "${EVAL_WORKERS}"
            --select-run-per-task "${SELECT_RUN_PER_TASK}"
            --no-group-by-model
            --json-out "${GROUP_OUTPUT_DIR}/evaluation.json"
            --csv-out "${GROUP_OUTPUT_DIR}/evaluation.csv"
            --summary-out "${GROUP_OUTPUT_DIR}/evaluation_summary.json"
        )

        if [ "${ALLOW_ISSUES}" != "0" ]; then
            EVAL_ARGS+=(--allow-issues)
        fi
        if [ "${ENABLE_JUDGE}" != "0" ] || [ "${COMPONENTS}" != "workplace" ]; then
            EVAL_ARGS+=(--enable-judge)
        fi

        uv run python "${EVAL_ARGS[@]}"
        STATUS=$?
        if [ ${STATUS} -ne 0 ]; then
            echo "[ERROR] Evaluation failed for ${MODEL_SLUG}/${GROUP_NAME} with exit code ${STATUS}."
            EXIT_CODE=1
        fi
    done
done

echo "=================================================="
echo "[INFO] Merging per-group reports by model"
echo "=================================================="
merge_model_reports || exit 1

shopt -s nullglob
SUMMARY_PATHS=( "${OUTPUT_ROOT}"/*/evaluation_summary.json )
shopt -u nullglob

if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
    echo "[ERROR] No merged evaluation_summary.json files found under ${OUTPUT_ROOT}."
    exit 1
fi

echo "=================================================="
echo "[INFO] Rendering model comparison chart"
echo "=================================================="
uv run python scripts/visualize_evaluation_summary.py \
    "${SUMMARY_PATHS[@]}" \
    --output "${CHART_OUTPUT}" \
    --title "Round 01 Aligned Mix 800 Workplace Evaluation" \
    --sort-by average_objective_score
STATUS=$?
if [ ${STATUS} -ne 0 ]; then
    echo "[ERROR] Chart rendering failed with exit code ${STATUS}."
    EXIT_CODE=1
else
    echo "[OK] Chart written to ${CHART_OUTPUT}"
fi

exit ${EXIT_CODE}
