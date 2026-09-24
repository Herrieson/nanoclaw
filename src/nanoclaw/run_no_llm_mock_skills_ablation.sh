#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

TASK_GLOB="${TASK_GLOB:-tasks/data_no_llm_mock_skills_*.yaml}"
RESULTS_ROOT="${RESULTS_ROOT:-results/no_llm_mock_skills_ablation}"
EVAL_ROOT="${EVAL_ROOT:-results/no_llm_mock_skills_ablation_eval}"
VERIFIER_JSONL="${VERIFIER_JSONL:-doc/todo/no_llm_mock_skills.jsonl}"
IMPORT_MANIFEST="${IMPORT_MANIFEST:-.staging/no_llm_mock_skills/import_manifest.jsonl}"
CHART_OUTPUT="${CHART_OUTPUT:-${EVAL_ROOT}/model_comparison.svg}"
COMPONENTS="${COMPONENTS:-workplace}"
WORKERS="${WORKERS:-1}"
EVAL_WORKERS="${EVAL_WORKERS:-16}"
APPROVAL_MODE="${APPROVAL_MODE:-reject}"
RESUME="${RESUME:-1}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-1}"
RUN_TASKS="${RUN_TASKS:-1}"
RUN_EVALS="${RUN_EVALS:-1}"
ALLOW_ISSUES="${ALLOW_ISSUES:-1}"
ENABLE_JUDGE="${ENABLE_JUDGE:-0}"
SELECT_RUN_PER_TASK="${SELECT_RUN_PER_TASK:-latest-completed}"

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

DEFAULT_MODELS=(
    "qwen3.5-flash"
)

if [ -n "${MODELS_OVERRIDE:-}" ]; then
    read -r -a MODELS <<< "${MODELS_OVERRIDE}"
else
    MODELS=("${DEFAULT_MODELS[@]}")
fi

shopt -s nullglob
TASK_FILES=( ${TASK_GLOB} )
shopt -u nullglob

if [ ${#TASK_FILES[@]} -eq 0 ]; then
    echo "[ERROR] No tasks matched: ${TASK_GLOB}"
    exit 1
fi

if [ ! -f "${VERIFIER_JSONL}" ]; then
    echo "[ERROR] Verifier JSONL does not exist: ${VERIFIER_JSONL}"
    exit 1
fi

if [ ! -f "${IMPORT_MANIFEST}" ]; then
    echo "[ERROR] Import manifest does not exist: ${IMPORT_MANIFEST}"
    exit 1
fi

if [ ${#MODELS[@]} -eq 0 ]; then
    echo "[ERROR] No models configured. Set MODELS_OVERRIDE or edit DEFAULT_MODELS."
    exit 1
fi

echo "=================================================="
echo "[INFO] No-LLM mock skills ablation"
echo "[INFO] Dataset task glob: ${TASK_GLOB}"
echo "[INFO] Matched tasks: ${#TASK_FILES[@]}"
echo "[INFO] Results root: ${RESULTS_ROOT}"
echo "[INFO] Eval root: ${EVAL_ROOT}"
echo "[INFO] Verifier JSONL: ${VERIFIER_JSONL}"
echo "[INFO] Import manifest: ${IMPORT_MANIFEST}"
echo "[INFO] Runner: built-in nanoclaw"
echo "[INFO] Workers per model: ${WORKERS}"
echo "[INFO] Eval workers: ${EVAL_WORKERS}"
echo "[INFO] Components: ${COMPONENTS}"
echo "[INFO] Approval mode: ${APPROVAL_MODE}"
echo "=================================================="

EXIT_CODE=0

for MODEL in "${MODELS[@]}"; do
    DIR_NAME="$(slugify_model_name "${MODEL}")"
    RESULTS_DIR="${RESULTS_ROOT}/${DIR_NAME}"
    MODEL_EVAL_DIR="${EVAL_ROOT}/${DIR_NAME}"

    if [ "${RUN_TASKS}" != "0" ]; then
        echo "=================================================="
        echo "[INFO] Running model with built-in nanoclaw: ${MODEL}"
        echo "[INFO] Results dir: ${RESULTS_DIR}"
        echo "=================================================="

        RUN_ARGS=(
            scripts/run_generated_tasks.py
            "${TASK_FILES[@]}"
            --model "${MODEL}"
            --approval-mode "${APPROVAL_MODE}"
            --workers "${WORKERS}"
            --results-dir "${RESULTS_DIR}"
        )

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
            echo "[OK] Model ${MODEL} run finished."
        else
            echo "[ERROR] Model ${MODEL} run finished with exit code ${STATUS}; continuing to evaluation of available runs."
            EXIT_CODE=1
        fi
        echo ""
    fi

    if [ "${RUN_EVALS}" != "0" ]; then
        shopt -s nullglob
        RUN_DIRS=( "${RESULTS_DIR}"/data_no_llm_mock_skills_*/* )
        shopt -u nullglob

        if [ ${#RUN_DIRS[@]} -eq 0 ]; then
            echo "[WARN] No run directories found for ${MODEL}: ${RESULTS_DIR}"
            EXIT_CODE=1
            continue
        fi

        echo "=================================================="
        echo "[INFO] Evaluating model: ${MODEL}"
        echo "[INFO] Matched run dirs: ${#RUN_DIRS[@]}"
        echo "[INFO] Eval dir: ${MODEL_EVAL_DIR}"
        echo "=================================================="

        EVAL_ARGS=(
            scripts/evaluate_workplace_trace_tasks.py
            "${RUN_DIRS[@]}"
            --verifier-jsonl "${VERIFIER_JSONL}"
            --manifest "${IMPORT_MANIFEST}"
            --components "${COMPONENTS}"
            --workers "${EVAL_WORKERS}"
            --select-run-per-task "${SELECT_RUN_PER_TASK}"
            --no-group-by-model
            --json-out "${MODEL_EVAL_DIR}/evaluation.json"
            --csv-out "${MODEL_EVAL_DIR}/evaluation.csv"
            --summary-out "${MODEL_EVAL_DIR}/evaluation_summary.json"
        )

        if [ "${ALLOW_ISSUES}" != "0" ]; then
            EVAL_ARGS+=(--allow-issues)
        fi
        if [ "${ENABLE_JUDGE}" != "0" ] || [ "${COMPONENTS}" != "workplace" ]; then
            EVAL_ARGS+=(--enable-judge)
        fi

        uv run python "${EVAL_ARGS[@]}"
        STATUS=$?
        if [ ${STATUS} -eq 0 ]; then
            echo "[OK] Model ${MODEL} evaluation finished."
        else
            echo "[ERROR] Model ${MODEL} evaluation failed with exit code ${STATUS}."
            EXIT_CODE=1
        fi
        echo ""
    fi
done

if [ "${RUN_EVALS}" != "0" ]; then
    shopt -s nullglob
    SUMMARY_PATHS=( "${EVAL_ROOT}"/*/evaluation_summary.json )
    shopt -u nullglob

    if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
        echo "[WARN] No evaluation_summary.json files found under ${EVAL_ROOT}; skipping chart."
        EXIT_CODE=1
    else
        echo "=================================================="
        echo "[INFO] Rendering model comparison chart"
        echo "=================================================="
        uv run python scripts/visualize_evaluation_summary.py \
            "${SUMMARY_PATHS[@]}" \
            --output "${CHART_OUTPUT}" \
            --title "No-LLM Mock Skills Ablation Workplace Evaluation" \
            --sort-by average_objective_score
        STATUS=$?
        if [ ${STATUS} -eq 0 ]; then
            echo "[OK] Chart written to ${CHART_OUTPUT}"
        else
            echo "[ERROR] Chart rendering failed with exit code ${STATUS}."
            EXIT_CODE=1
        fi
    fi
fi

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[OK] Run + evaluation completed."
else
    echo "[ERROR] Run + evaluation completed with issues. Check the logs above."
fi

exit ${EXIT_CODE}
