#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

TASK_GLOB="${TASK_GLOB:-tasks/data_round_01_aligned_mix_800_*.yaml}"
RESULTS_ROOT="${RESULTS_ROOT:-results/round_01_aligned_mix_800}"
RUNNER_PROFILE="${RUNNER_PROFILE:-runner_profiles/openclaw.yaml}"
WORKERS="${WORKERS:-1}"
APPROVAL_MODE="${APPROVAL_MODE:-reject}"
RESUME="${RESUME:-1}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-1}"

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

DEFAULT_MODELS=(
    # "MiniMax-M2.1"
    # "MiniMax-M2.5"
    # "deepseek-v3.2"
    # "deepseek-v3"
    # "qwen3-vl-flash"
    # "qwen-plus"
    # "qwen2.5-14b-instruct-1m"
    "qwen3.5-flash"
    # "qwen3.5-plus"
    # "qwen3.5-27b"
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

if [ ${#MODELS[@]} -eq 0 ]; then
    echo "[ERROR] No models configured. Set MODELS_OVERRIDE or edit DEFAULT_MODELS."
    exit 1
fi

echo "=================================================="
echo "[INFO] Dataset task glob: ${TASK_GLOB}"
echo "[INFO] Matched tasks: ${#TASK_FILES[@]}"
echo "[INFO] Results root: ${RESULTS_ROOT}"
echo "[INFO] Runner profile: ${RUNNER_PROFILE:-<builtin>}"
echo "[INFO] Workers per model: ${WORKERS}"
echo "[INFO] Approval mode: ${APPROVAL_MODE}"
echo "=================================================="

EXIT_CODE=0

for MODEL in "${MODELS[@]}"; do
    DIR_NAME="$(slugify_model_name "${MODEL}")"
    RESULTS_DIR="${RESULTS_ROOT}/${DIR_NAME}"

    echo "=================================================="
    echo "[INFO] Running model: ${MODEL}"
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
        echo "[OK] Model ${MODEL} finished."
    else
        echo "[ERROR] Model ${MODEL} failed with exit code ${STATUS}."
        EXIT_CODE=1
    fi
    echo ""
done

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[OK] All configured model runs finished."
else
    echo "[ERROR] One or more model runs failed. Check the logs above."
fi

exit ${EXIT_CODE}
