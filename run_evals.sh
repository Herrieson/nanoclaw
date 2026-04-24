#!/bin/bash

set -u

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

# 定义所有需要评估的模型名称数组，需与 run_tasks.sh 保持一致
MODELS=(
    # "minimaxminimaxm27"
    # "minimaxminimaxm21"
    # "deepseekv32"
    # "deepseekv3"
    "qwen3vlflash"
    "qwenplus"
)

# 遍历每个模型并执行命令
for MODEL in "${MODELS[@]}"; do
    DIR_NAME="$(slugify_model_name "${MODEL}")"
    RESULTS_DIR="results/skills/${DIR_NAME}"

    echo "=================================================="
    echo "🚀 开始评估模型: ${MODEL} ..."
    echo "📂 结果输入目录: ${RESULTS_DIR}"
    echo "=================================================="

    uv run python scripts/evaluate_generated_tasks.py \
        "${RESULTS_DIR}/data_round_01_skills_*/*" \
        --json-out "${RESULTS_DIR}/evaluation.json" \
        --csv-out "${RESULTS_DIR}/evaluation.csv" \
        --summary-out "${RESULTS_DIR}/evaluation_summary.json" \
        --enable-judge \
        --judge-model qwen3.5-27b \
        --judge-max-attempts 2 \
        --workers 32
        
    # 检查上一条命令是否执行成功
    if [ $? -eq 0 ]; then
        echo "✅ 模型 ${MODEL} 评估完成！"
    else
        echo "❌ 模型 ${MODEL} 评估出错，请检查日志。"
    fi
    echo ""
done

echo "🎉 所有模型的评估任务已全部执行完毕！"
