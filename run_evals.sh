#!/bin/bash

set -u

RESULTS_ROOT="results/multi_turn_100"
RUN_GLOB="${RESULTS_ROOT}/*/data_round_01_multi_turn_100_*/*"
MANIFEST=".staging/round_01_multi_turn_100/import_manifest.jsonl"
OUTPUT_ROOT="results/multi_turn_100_new_verifier_workplace_only"

VERIFIER_JSONLS=(
    "doc/todo/gemini3_2000_score_new_verifier_multi_turn_1.jsonl"
    "doc/todo/gemini3_2000_score_new_verifier_multi_turn_2.jsonl"
    "doc/todo/gemini3_2000_score_new_verifier_multi_turn_3.jsonl"
    "doc/todo/gemini3_2000_score_new_verifier_multi_turn_4.jsonl"
    "doc/todo/gemini3_2000_score_new_verifier_multi_turn_5.jsonl"
)

echo "=================================================="
echo "🚀 开始评估 multi-turn-100 任务"
echo "📂 结果输入: ${RUN_GLOB}"
echo "🧾 Manifest: ${MANIFEST}"
echo "📂 评估输出: ${OUTPUT_ROOT}"
echo "=================================================="

uv run python scripts/evaluate_workplace_trace_tasks.py \
    "${RUN_GLOB}" \
    --verifier-jsonl "${VERIFIER_JSONLS[@]}" \
    --manifest "${MANIFEST}" \
    --components workplace \
    --workers 16 \
    --select-run-per-task latest-completed \
    --output-root "${OUTPUT_ROOT}" \
    --allow-issues

if [ $? -eq 0 ]; then
    echo "✅ multi-turn-100 新 verifier workplace 评估完成！"
else
    echo "❌ multi-turn-100 新 verifier workplace 评估出错，请检查日志。"
fi
