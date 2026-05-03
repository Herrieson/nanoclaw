#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

RESULTS_ROOT="${RESULTS_ROOT:-results/nanoclaw_workplace_suite}"
EVAL_ROOT="${EVAL_ROOT:-results/nanoclaw_workplace_suite_eval}"
RUNNER_PROFILE="${RUNNER_PROFILE:-}"
RUNNER_NAME="${RUNNER_NAME:-built-in nanoclaw}"
WORKERS="${WORKERS:-1}"
EVAL_WORKERS="${EVAL_WORKERS:-16}"
APPROVAL_MODE="${APPROVAL_MODE:-reject}"
RESUME="${RESUME:-1}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-1}"
RUN_TASKS="${RUN_TASKS:-1}"
RUN_EVALS="${RUN_EVALS:-1}"
RENDER_CHARTS="${RENDER_CHARTS:-1}"
ALLOW_ISSUES="${ALLOW_ISSUES:-1}"
ENABLE_JUDGE="${ENABLE_JUDGE:-0}"
COMPONENTS="${COMPONENTS:-workplace}"
SELECT_RUN_PER_TASK="${SELECT_RUN_PER_TASK:-latest-completed}"

DEFAULT_DATASETS=(
    "round_01_aligned_mix_subset_100"
    "persona_aligned_mix_subset_100"
)

DEFAULT_MODELS=(
    "qwen3.5-flash"
)

if [ -n "${DATASETS_OVERRIDE:-}" ]; then
    read -r -a DATASETS <<< "${DATASETS_OVERRIDE}"
else
    DATASETS=("${DEFAULT_DATASETS[@]}")
fi

if [ -n "${MODELS_OVERRIDE:-}" ]; then
    read -r -a MODELS <<< "${MODELS_OVERRIDE}"
else
    MODELS=("${DEFAULT_MODELS[@]}")
fi

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

dataset_task_glob() {
    case "$1" in
        round_01_aligned_mix_800)
            echo "tasks/data_round_01_aligned_mix_800_*.yaml"
            ;;
        round_01_aligned_mix_subset_100)
            echo "tasks/data_round_01_aligned_mix_800_*.yaml"
            ;;
        persona_aligned_mix_200)
            echo "tasks/data_persona_aligned_*_50_*.yaml"
            ;;
        persona_aligned_mix_subset_100)
            echo "tasks/data_persona_aligned_*_50_*.yaml"
            ;;
        *)
            echo "[ERROR] Unknown dataset: $1" >&2
            return 1
            ;;
    esac
}

dataset_staging_root() {
    case "$1" in
        round_01_aligned_mix_800)
            echo ".staging/round_01_aligned_mix_800"
            ;;
        round_01_aligned_mix_subset_100)
            echo ".staging/round_01_aligned_mix_subset_100"
            ;;
        persona_aligned_mix_200)
            echo ".staging/persona_aligned_mix_200"
            ;;
        persona_aligned_mix_subset_100)
            echo ".staging/persona_aligned_mix_subset_100"
            ;;
        *)
            echo "[ERROR] Unknown dataset: $1" >&2
            return 1
            ;;
    esac
}

dataset_groups() {
    case "$1" in
        round_01_aligned_mix_800|round_01_aligned_mix_subset_100)
            echo "multi_turn_aligned skills_aligned hard_aligned base"
            ;;
        persona_aligned_mix_200|persona_aligned_mix_subset_100)
            echo "base multi_turn hard skills"
            ;;
        *)
            echo "[ERROR] Unknown dataset: $1" >&2
            return 1
            ;;
    esac
}

dataset_title() {
    case "$1" in
        round_01_aligned_mix_800)
            echo "Round 01 Aligned Mix 800"
            ;;
        round_01_aligned_mix_subset_100)
            echo "Round 01 Aligned Mix Subset 100"
            ;;
        persona_aligned_mix_200)
            echo "Persona Aligned Mix 200"
            ;;
        persona_aligned_mix_subset_100)
            echo "Persona Aligned Mix Subset 100"
            ;;
        *)
            echo "$1"
            ;;
    esac
}

dataset_group_verifiers() {
    local DATASET="$1"
    local GROUP_NAME="$2"

    case "${DATASET}:${GROUP_NAME}" in
        round_01_aligned_mix_800:multi_turn_aligned|round_01_aligned_mix_subset_100:multi_turn_aligned)
            echo "doc/todo/gemini3_2000_score_new_verifier_multi_turn_1.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_2.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_3.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_4.jsonl doc/todo/gemini3_2000_score_new_verifier_multi_turn_5.jsonl"
            ;;
        round_01_aligned_mix_800:skills_aligned|round_01_aligned_mix_subset_100:skills_aligned)
            echo "doc/todo/gemini3_2000_skills_score_new_verifier_1.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_2.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_3.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_4.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_5.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_6.jsonl doc/todo/gemini3_2000_skills_score_new_verifier_7.jsonl"
            ;;
        round_01_aligned_mix_800:hard_aligned|round_01_aligned_mix_subset_100:hard_aligned)
            echo "doc/todo/gemini3_2000_score_new_verifier_hard_1.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_2.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_3.jsonl doc/todo/gemini3_2000_score_new_verifier_hard_4.jsonl"
            ;;
        round_01_aligned_mix_800:base|round_01_aligned_mix_subset_100:base)
            echo "doc/todo/gemini3_2000_score_new_verifier_1.jsonl doc/todo/gemini3_2000_score_new_verifier_2.jsonl doc/todo/gemini3_2000_score_new_verifier_3.jsonl"
            ;;
        persona_aligned_mix_200:base|persona_aligned_mix_subset_100:base)
            echo "doc/todo/persona/base.jsonl"
            ;;
        persona_aligned_mix_200:multi_turn|persona_aligned_mix_subset_100:multi_turn)
            echo "doc/todo/persona/multi_turn.jsonl"
            ;;
        persona_aligned_mix_200:hard|persona_aligned_mix_subset_100:hard)
            echo "doc/todo/persona/hard.jsonl"
            ;;
        persona_aligned_mix_200:skills|persona_aligned_mix_subset_100:skills)
            echo "doc/todo/persona/skills.jsonl"
            ;;
        *)
            echo "[ERROR] No verifier mapping for ${DATASET}/${GROUP_NAME}" >&2
            return 1
            ;;
    esac
}

build_group_manifests() {
    local DATASET="$1"
    local STAGING_ROOT
    local SELECTION_MANIFEST
    local IMPORT_MANIFEST
    local GROUP_MANIFEST_ROOT
    local GROUPS_RAW

    STAGING_ROOT="$(dataset_staging_root "${DATASET}")" || return 1
    SELECTION_MANIFEST="${STAGING_ROOT}/selection_manifest.jsonl"
    IMPORT_MANIFEST="${STAGING_ROOT}/import_manifest.jsonl"
    GROUP_MANIFEST_ROOT="${STAGING_ROOT}/eval_manifests"
    GROUPS_RAW="$(dataset_groups "${DATASET}")" || return 1
    read -r -a GROUPS <<< "${GROUPS_RAW}"

    uv run python - "${SELECTION_MANIFEST}" "${IMPORT_MANIFEST}" "${GROUP_MANIFEST_ROOT}" "${GROUPS[@]}" <<'PY'
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
if not group_order:
    raise SystemExit("No evaluation groups were configured.")

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
    group = selection.get("group") or imported.get("group")
    if source_task_id != imported_source_task_id:
        raise SystemExit(
            f"Manifest source_task_id mismatch at line {line_number}: "
            f"{source_task_id!r} != {imported_source_task_id!r}"
        )
    if not isinstance(group, str) or not group:
        raise SystemExit(f"Missing group in manifests at line {line_number}")
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

run_dataset_tasks() {
    local DATASET="$1"
    local TASK_GLOB
    local STAGING_ROOT
    local TASK_IDS_FILE
    local DATASET_RESULTS_ROOT

    TASK_GLOB="$(dataset_task_glob "${DATASET}")" || return 1
    STAGING_ROOT="$(dataset_staging_root "${DATASET}")" || return 1
    TASK_IDS_FILE="${STAGING_ROOT}/task_ids"
    DATASET_RESULTS_ROOT="${RESULTS_ROOT}/${DATASET}"

    local TASK_FILES=()
    if [ -f "${TASK_IDS_FILE}" ]; then
        local TASK_IDS=()
        local TASK_ID
        mapfile -t TASK_IDS < "${TASK_IDS_FILE}"
        for TASK_ID in "${TASK_IDS[@]}"; do
            [ -n "${TASK_ID}" ] || continue
            TASK_FILES+=( "tasks/${TASK_ID}.yaml" )
        done
    else
        shopt -s nullglob
        TASK_FILES=( ${TASK_GLOB} )
        shopt -u nullglob
    fi

    if [ ${#TASK_FILES[@]} -eq 0 ]; then
        echo "[ERROR] ${DATASET}: no tasks matched ${TASK_GLOB}"
        return 1
    fi

    echo "=================================================="
    echo "[INFO] Running dataset with built-in nanoclaw: ${DATASET}"
    echo "[INFO] Task glob: ${TASK_GLOB}"
    if [ -f "${TASK_IDS_FILE}" ]; then
        echo "[INFO] Task ids file: ${TASK_IDS_FILE}"
    fi
    echo "[INFO] Matched tasks: ${#TASK_FILES[@]}"
    echo "[INFO] Results root: ${DATASET_RESULTS_ROOT}"
    echo "[INFO] Runner: ${RUNNER_NAME}"
    if [ -n "${RUNNER_PROFILE}" ]; then
        echo "[INFO] Runner profile: ${RUNNER_PROFILE}"
    fi
    echo "[INFO] Workers per model: ${WORKERS}"
    echo "[INFO] Approval mode: ${APPROVAL_MODE}"
    echo "=================================================="

    local STATUS
    local MODEL
    local MODEL_SLUG
    local RESULTS_DIR
    local RUN_ARGS
    local DATASET_EXIT_CODE=0

    for MODEL in "${MODELS[@]}"; do
        MODEL_SLUG="$(slugify_model_name "${MODEL}")"
        RESULTS_DIR="${DATASET_RESULTS_ROOT}/${MODEL_SLUG}"

        echo "=================================================="
        echo "[INFO] ${DATASET}: running model ${MODEL}"
        echo "[INFO] Results dir: ${RESULTS_DIR}"
        echo "[INFO] Runner: ${RUNNER_NAME}"
        echo "=================================================="

        RUN_ARGS=(
            scripts/run_generated_tasks.py
            "${TASK_FILES[@]}"
            --model "${MODEL}"
            --approval-mode "${APPROVAL_MODE}"
            --workers "${WORKERS}"
            --results-dir "${RESULTS_DIR}"
        )

        if [ -n "${RUNNER_PROFILE}" ]; then
            RUN_ARGS+=(--runner-profile "${RUNNER_PROFILE}")
        fi

        if [ "${RESUME}" != "0" ]; then
            RUN_ARGS+=(--resume)
        fi

        if [ "${SKIP_PREFLIGHT}" != "0" ]; then
            RUN_ARGS+=(--skip-validation --skip-normalize --skip-auto-fix)
        else
            RUN_ARGS+=(--run-builder-validation --strict --quarantine-invalid)
        fi

        uv run python "${RUN_ARGS[@]}"
        STATUS=$?
        if [ ${STATUS} -eq 0 ]; then
            echo "[OK] ${DATASET}/${MODEL} run finished."
        else
            echo "[ERROR] ${DATASET}/${MODEL} run failed with exit code ${STATUS}; continuing."
            DATASET_EXIT_CODE=1
        fi
        echo ""
    done

    return ${DATASET_EXIT_CODE}
}

merge_model_reports() {
    local INTERMEDIATE_ROOT="$1"
    local OUTPUT_ROOT="$2"
    shift 2

    uv run python - "${INTERMEDIATE_ROOT}" "${OUTPUT_ROOT}" "$@" <<'PY'
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
    "evaluation_group",
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

evaluate_dataset() {
    local DATASET="$1"
    local STAGING_ROOT
    local GROUP_MANIFEST_ROOT
    local DATASET_RESULTS_ROOT
    local DATASET_EVAL_ROOT
    local INTERMEDIATE_ROOT
    local MERGED_ROOT
    local GROUPS_RAW
    local DATASET_EXIT_CODE=0

    STAGING_ROOT="$(dataset_staging_root "${DATASET}")" || return 1
    GROUP_MANIFEST_ROOT="${STAGING_ROOT}/eval_manifests"
    DATASET_RESULTS_ROOT="${RESULTS_ROOT}/${DATASET}"
    DATASET_EVAL_ROOT="${EVAL_ROOT}/${DATASET}"
    INTERMEDIATE_ROOT="${DATASET_EVAL_ROOT}/_group_reports"
    MERGED_ROOT="${DATASET_EVAL_ROOT}/merged"
    GROUPS_RAW="$(dataset_groups "${DATASET}")" || return 1
    read -r -a GROUPS <<< "${GROUPS_RAW}"

    if [ ! -d "${DATASET_RESULTS_ROOT}" ]; then
        echo "[ERROR] ${DATASET}: results root does not exist: ${DATASET_RESULTS_ROOT}"
        return 1
    fi

    echo "=================================================="
    echo "[INFO] Evaluating dataset: ${DATASET}"
    echo "[INFO] Results root: ${DATASET_RESULTS_ROOT}"
    echo "[INFO] Eval root: ${DATASET_EVAL_ROOT}"
    echo "[INFO] Components: ${COMPONENTS}"
    echo "[INFO] Eval workers: ${EVAL_WORKERS}"
    echo "=================================================="

    build_group_manifests "${DATASET}" || return 1

    local MODEL
    local MODEL_SLUG
    local GROUP_NAME
    local TASK_ID_FILE
    local GROUP_MANIFEST
    local TASK_IDS
    local TASK_ID
    local MATCHES
    local RUN_DIRS
    local GROUP_VERIFIERS_RAW
    local GROUP_VERIFIERS
    local GROUP_OUTPUT_DIR
    local EVAL_ARGS
    local STATUS

    for MODEL in "${MODELS[@]}"; do
        MODEL_SLUG="$(slugify_model_name "${MODEL}")"
        if [ ! -d "${DATASET_RESULTS_ROOT}/${MODEL_SLUG}" ]; then
            echo "[WARN] ${DATASET}: skipping missing model results dir ${DATASET_RESULTS_ROOT}/${MODEL_SLUG}"
            DATASET_EXIT_CODE=1
            continue
        fi

        for GROUP_NAME in "${GROUPS[@]}"; do
            TASK_ID_FILE="${GROUP_MANIFEST_ROOT}/${GROUP_NAME}.task_ids"
            GROUP_MANIFEST="${GROUP_MANIFEST_ROOT}/${GROUP_NAME}.jsonl"
            if [ ! -f "${TASK_ID_FILE}" ] || [ ! -f "${GROUP_MANIFEST}" ]; then
                echo "[ERROR] ${DATASET}/${GROUP_NAME}: missing group manifest files."
                DATASET_EXIT_CODE=1
                continue
            fi

            mapfile -t TASK_IDS < "${TASK_ID_FILE}"
            RUN_DIRS=()
            shopt -s nullglob
            for TASK_ID in "${TASK_IDS[@]}"; do
                [ -n "${TASK_ID}" ] || continue
                MATCHES=( "${DATASET_RESULTS_ROOT}/${MODEL_SLUG}/${TASK_ID}"/* )
                RUN_DIRS+=( "${MATCHES[@]}" )
            done
            shopt -u nullglob

            if [ ${#RUN_DIRS[@]} -eq 0 ]; then
                echo "[WARN] ${DATASET}/${MODEL_SLUG}/${GROUP_NAME}: no run dirs matched; skipping."
                DATASET_EXIT_CODE=1
                continue
            fi

            GROUP_VERIFIERS_RAW="$(dataset_group_verifiers "${DATASET}" "${GROUP_NAME}")" || {
                DATASET_EXIT_CODE=1
                continue
            }
            read -r -a GROUP_VERIFIERS <<< "${GROUP_VERIFIERS_RAW}"
            GROUP_OUTPUT_DIR="${INTERMEDIATE_ROOT}/${GROUP_NAME}/${MODEL_SLUG}"

            echo "=================================================="
            echo "[INFO] Evaluating ${DATASET}/${MODEL_SLUG}/${GROUP_NAME}"
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
                echo "[ERROR] Evaluation failed for ${DATASET}/${MODEL_SLUG}/${GROUP_NAME} with exit code ${STATUS}."
                DATASET_EXIT_CODE=1
            fi
        done
    done

    echo "=================================================="
    echo "[INFO] Merging per-group reports for ${DATASET}"
    echo "=================================================="
    merge_model_reports "${INTERMEDIATE_ROOT}" "${MERGED_ROOT}" "${GROUPS[@]}" || return 1

    return ${DATASET_EXIT_CODE}
}

render_dataset_charts() {
    local DATASET="$1"
    local DATASET_EVAL_ROOT="${EVAL_ROOT}/${DATASET}"
    local MERGED_ROOT="${DATASET_EVAL_ROOT}/merged"
    local CHART_ROOT="${DATASET_EVAL_ROOT}/charts"
    local TITLE
    local GROUPS_RAW
    local GROUPS
    local SUMMARY_PATHS
    local GROUP_NAME
    local STATUS
    local CHART_EXIT_CODE=0

    TITLE="$(dataset_title "${DATASET}")"
    GROUPS_RAW="$(dataset_groups "${DATASET}")" || return 1
    read -r -a GROUPS <<< "${GROUPS_RAW}"
    mkdir -p "${CHART_ROOT}"

    shopt -s nullglob
    SUMMARY_PATHS=( "${MERGED_ROOT}"/*/evaluation_summary.json )
    shopt -u nullglob

    if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
        echo "[WARN] ${DATASET}: no merged summaries found; skipping dataset chart."
        CHART_EXIT_CODE=1
    else
        uv run python scripts/visualize_evaluation_summary.py \
            "${SUMMARY_PATHS[@]}" \
            --output "${CHART_ROOT}/model_comparison.svg" \
            --title "${TITLE} Workplace Evaluation" \
            --sort-by average_objective_score
        STATUS=$?
        if [ ${STATUS} -eq 0 ]; then
            echo "[OK] Chart written to ${CHART_ROOT}/model_comparison.svg"
        else
            echo "[ERROR] Chart rendering failed for ${DATASET} with exit code ${STATUS}."
            CHART_EXIT_CODE=1
        fi
    fi

    for GROUP_NAME in "${GROUPS[@]}"; do
        shopt -s nullglob
        SUMMARY_PATHS=( "${DATASET_EVAL_ROOT}/_group_reports/${GROUP_NAME}"/*/evaluation_summary.json )
        shopt -u nullglob

        if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
            echo "[WARN] ${DATASET}/${GROUP_NAME}: no group summaries found; skipping group chart."
            CHART_EXIT_CODE=1
            continue
        fi

        uv run python scripts/visualize_evaluation_summary.py \
            "${SUMMARY_PATHS[@]}" \
            --output "${CHART_ROOT}/${GROUP_NAME}_model_comparison.svg" \
            --title "${TITLE} ${GROUP_NAME} Workplace Evaluation" \
            --sort-by average_objective_score
        STATUS=$?
        if [ ${STATUS} -eq 0 ]; then
            echo "[OK] Chart written to ${CHART_ROOT}/${GROUP_NAME}_model_comparison.svg"
        else
            echo "[ERROR] Group chart rendering failed for ${DATASET}/${GROUP_NAME} with exit code ${STATUS}."
            CHART_EXIT_CODE=1
        fi
    done

    return ${CHART_EXIT_CODE}
}

render_suite_chart() {
    local SUMMARY_COPY_ROOT="${EVAL_ROOT}/_suite_chart_summaries"
    local SUMMARY_PATHS=()
    local DATASET
    local MODEL
    local MODEL_SLUG
    local SOURCE_SUMMARY
    local DEST_DIR
    local STATUS

    rm -rf "${SUMMARY_COPY_ROOT:?}"
    mkdir -p "${SUMMARY_COPY_ROOT}"

    for DATASET in "${DATASETS[@]}"; do
        for MODEL in "${MODELS[@]}"; do
            MODEL_SLUG="$(slugify_model_name "${MODEL}")"
            SOURCE_SUMMARY="${EVAL_ROOT}/${DATASET}/merged/${MODEL_SLUG}/evaluation_summary.json"
            if [ ! -f "${SOURCE_SUMMARY}" ]; then
                continue
            fi
            DEST_DIR="${SUMMARY_COPY_ROOT}/${DATASET}__${MODEL_SLUG}"
            mkdir -p "${DEST_DIR}"
            cp "${SOURCE_SUMMARY}" "${DEST_DIR}/evaluation_summary.json"
            SUMMARY_PATHS+=( "${DEST_DIR}/evaluation_summary.json" )
        done
    done

    if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
        echo "[WARN] No summaries found for suite chart."
        return 1
    fi

    uv run python scripts/visualize_evaluation_summary.py \
        "${SUMMARY_PATHS[@]}" \
        --output "${EVAL_ROOT}/suite_model_dataset_comparison.svg" \
        --title "Nanoclaw Workplace Evaluation: Dataset x Model" \
        --sort-by average_objective_score
    STATUS=$?
    if [ ${STATUS} -eq 0 ]; then
        echo "[OK] Suite chart written to ${EVAL_ROOT}/suite_model_dataset_comparison.svg"
        return 0
    fi

    echo "[ERROR] Suite chart rendering failed with exit code ${STATUS}."
    return 1
}

if [ ${#DATASETS[@]} -eq 0 ]; then
    echo "[ERROR] No datasets configured. Set DATASETS_OVERRIDE or edit DEFAULT_DATASETS."
    exit 1
fi

if [ ${#MODELS[@]} -eq 0 ]; then
    echo "[ERROR] No models configured. Set MODELS_OVERRIDE or edit DEFAULT_MODELS."
    exit 1
fi

echo "=================================================="
echo "[INFO] Nanoclaw workplace suite"
echo "[INFO] Runner: ${RUNNER_NAME}"
if [ -n "${RUNNER_PROFILE}" ]; then
    echo "[INFO] Runner profile: ${RUNNER_PROFILE}"
else
    echo "[INFO] Runner profile: <builtin>"
fi
echo "[INFO] Datasets: ${DATASETS[*]}"
echo "[INFO] Models: ${MODELS[*]}"
echo "[INFO] Results root: ${RESULTS_ROOT}"
echo "[INFO] Eval root: ${EVAL_ROOT}"
echo "[INFO] Components: ${COMPONENTS}"
echo "[INFO] Run tasks: ${RUN_TASKS}"
echo "[INFO] Run evals: ${RUN_EVALS}"
echo "[INFO] Render charts: ${RENDER_CHARTS}"
echo "=================================================="

EXIT_CODE=0

for DATASET in "${DATASETS[@]}"; do
    dataset_task_glob "${DATASET}" >/dev/null || {
        EXIT_CODE=1
        continue
    }
    dataset_staging_root "${DATASET}" >/dev/null || {
        EXIT_CODE=1
        continue
    }

    if [ "${RUN_TASKS}" != "0" ]; then
        run_dataset_tasks "${DATASET}" || EXIT_CODE=1
    fi

    if [ "${RUN_EVALS}" != "0" ]; then
        evaluate_dataset "${DATASET}" || EXIT_CODE=1
    fi

    if [ "${RENDER_CHARTS}" != "0" ] && [ "${RUN_EVALS}" != "0" ]; then
        render_dataset_charts "${DATASET}" || EXIT_CODE=1
    fi
done

if [ "${RENDER_CHARTS}" != "0" ] && [ "${RUN_EVALS}" != "0" ]; then
    render_suite_chart || EXIT_CODE=1
fi

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[OK] Nanoclaw workplace suite completed."
else
    echo "[ERROR] Nanoclaw workplace suite completed with issues. Check the logs above."
fi

exit ${EXIT_CODE}
