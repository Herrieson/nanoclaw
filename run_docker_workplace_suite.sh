#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

RESULTS_ROOT="${RESULTS_ROOT:-results/docker_workplace_suite}"
EVAL_ROOT="${EVAL_ROOT:-results/docker_workplace_suite_eval}"
RUN_TASKS="${RUN_TASKS:-1}"
RUN_EVALS="${RUN_EVALS:-1}"
RENDER_CHARTS="${RENDER_CHARTS:-1}"

DEFAULT_RUNNERS=(
    "openclaw"
    "hermes"
    "codex"
)

DEFAULT_DATASETS=(
    "round_01_aligned_mix_800"
    "persona_aligned_mix_200"
)

DEFAULT_MODELS=(
    "qwen3.5-flash"
)

if [ -n "${RUNNERS_OVERRIDE:-}" ]; then
    read -r -a RUNNERS <<< "${RUNNERS_OVERRIDE}"
else
    RUNNERS=("${DEFAULT_RUNNERS[@]}")
fi

if [ -n "${DATASETS_OVERRIDE:-}" ]; then
    read -r -a DATASETS_FOR_CHART <<< "${DATASETS_OVERRIDE}"
else
    DATASETS_FOR_CHART=("${DEFAULT_DATASETS[@]}")
fi

if [ -n "${MODELS_OVERRIDE:-}" ]; then
    read -r -a MODELS_FOR_CHART <<< "${MODELS_OVERRIDE}"
else
    MODELS_FOR_CHART=("${DEFAULT_MODELS[@]}")
fi

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

runner_profile_path() {
    case "$1" in
        openclaw)
            echo "runner_profiles/openclaw.yaml"
            ;;
        hermes)
            echo "runner_profiles/hermes.yaml"
            ;;
        codex)
            echo "runner_profiles/codex.yaml"
            ;;
        *)
            echo "[ERROR] Unknown runner: $1" >&2
            return 1
            ;;
    esac
}

render_combined_chart() {
    local SUMMARY_COPY_ROOT="${EVAL_ROOT}/_suite_chart_summaries"
    local SUMMARY_PATHS=()
    local RUNNER_NAME
    local DATASET
    local MODEL
    local MODEL_SLUG
    local SOURCE_SUMMARY
    local DEST_DIR
    local STATUS

    rm -rf "${SUMMARY_COPY_ROOT:?}"
    mkdir -p "${SUMMARY_COPY_ROOT}"

    for RUNNER_NAME in "${RUNNERS[@]}"; do
        for DATASET in "${DATASETS_FOR_CHART[@]}"; do
            for MODEL in "${MODELS_FOR_CHART[@]}"; do
                MODEL_SLUG="$(slugify_model_name "${MODEL}")"
                SOURCE_SUMMARY="${EVAL_ROOT}/${RUNNER_NAME}/${DATASET}/merged/${MODEL_SLUG}/evaluation_summary.json"
                if [ ! -f "${SOURCE_SUMMARY}" ]; then
                    continue
                fi
                DEST_DIR="${SUMMARY_COPY_ROOT}/${RUNNER_NAME}__${DATASET}__${MODEL_SLUG}"
                mkdir -p "${DEST_DIR}"
                cp "${SOURCE_SUMMARY}" "${DEST_DIR}/evaluation_summary.json"
                SUMMARY_PATHS+=( "${DEST_DIR}/evaluation_summary.json" )
            done
        done
    done

    if [ ${#SUMMARY_PATHS[@]} -eq 0 ]; then
        echo "[WARN] No summaries found for combined Docker chart."
        return 1
    fi

    uv run python scripts/visualize_evaluation_summary.py \
        "${SUMMARY_PATHS[@]}" \
        --output "${EVAL_ROOT}/docker_runner_dataset_model_comparison.svg" \
        --title "Docker Workplace Evaluation: Runner x Dataset x Model" \
        --sort-by average_objective_score
    STATUS=$?
    if [ ${STATUS} -eq 0 ]; then
        echo "[OK] Combined Docker chart written to ${EVAL_ROOT}/docker_runner_dataset_model_comparison.svg"
        return 0
    fi

    echo "[ERROR] Combined Docker chart rendering failed with exit code ${STATUS}."
    return 1
}

if [ ${#RUNNERS[@]} -eq 0 ]; then
    echo "[ERROR] No runners configured. Set RUNNERS_OVERRIDE or edit DEFAULT_RUNNERS."
    exit 1
fi

echo "=================================================="
echo "[INFO] Docker workplace suite"
echo "[INFO] Runners: ${RUNNERS[*]}"
echo "[INFO] Results root: ${RESULTS_ROOT}"
echo "[INFO] Eval root: ${EVAL_ROOT}"
echo "[INFO] Run tasks: ${RUN_TASKS}"
echo "[INFO] Run evals: ${RUN_EVALS}"
echo "[INFO] Render charts: ${RENDER_CHARTS}"
echo "=================================================="

EXIT_CODE=0

for RUNNER_NAME in "${RUNNERS[@]}"; do
    PROFILE_PATH="$(runner_profile_path "${RUNNER_NAME}")" || {
        EXIT_CODE=1
        continue
    }

    if [ ! -f "${PROFILE_PATH}" ]; then
        echo "[ERROR] Missing runner profile for ${RUNNER_NAME}: ${PROFILE_PATH}"
        EXIT_CODE=1
        continue
    fi

    echo "=================================================="
    echo "[INFO] Running Docker runner: ${RUNNER_NAME}"
    echo "[INFO] Profile: ${PROFILE_PATH}"
    echo "=================================================="

    RUNNER_PROFILE="${PROFILE_PATH}" \
    RUNNER_NAME="${RUNNER_NAME}" \
    RESULTS_ROOT="${RESULTS_ROOT}/${RUNNER_NAME}" \
    EVAL_ROOT="${EVAL_ROOT}/${RUNNER_NAME}" \
    RUN_TASKS="${RUN_TASKS}" \
    RUN_EVALS="${RUN_EVALS}" \
    RENDER_CHARTS="${RENDER_CHARTS}" \
    bash run_nanoclaw_workplace_suite.sh
    STATUS=$?

    if [ ${STATUS} -ne 0 ]; then
        echo "[ERROR] Docker runner ${RUNNER_NAME} completed with exit code ${STATUS}."
        EXIT_CODE=1
    fi
done

if [ "${RENDER_CHARTS}" != "0" ] && [ "${RUN_EVALS}" != "0" ]; then
    render_combined_chart || EXIT_CODE=1
fi

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[OK] Docker workplace suite completed."
else
    echo "[ERROR] Docker workplace suite completed with issues. Check the logs above."
fi

exit ${EXIT_CODE}
