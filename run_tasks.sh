#!/bin/bash

set -u

TASK_GLOB="tasks/data_round_01_multi_turn_100_*.yaml"
RESULTS_ROOT="results/multi_turn_100"

slugify_model_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+//g'
}

shopt -s nullglob
TASK_FILES=(${TASK_GLOB})
shopt -u nullglob

if [ ${#TASK_FILES[@]} -eq 0 ]; then
    echo "❌ 未找到 multi-turn-100 任务: ${TASK_GLOB}"
    exit 1
fi

echo "🎯 本次仅运行 multi-turn-100 任务: ${TASK_GLOB} (${#TASK_FILES[@]} 个)"

# 定义需要运行的模型数组
MODELS=(
    "MiniMax-M2.1"
    "MiniMax-M2.5"
    "deepseek-v3.2"
    "deepseek-v3"
    # "qwen3-vl-flash"
    # "qwen-plus"
    # "qwen2.5-14b-instruct-1m"
    # "qwen3.5-flash"
    # "qwen3.5-plus"
    # "qwen3.5-27b"
)

# 遍历每个模型并执行命令
for MODEL in "${MODELS[@]}"; do
    # 动态生成目录名称：移除 /、-、. 等非字母数字字符，并统一小写
    # 例如：qwen2.5-14b-instruct-1m -> qwen2514binstruct1m
    #      MiniMax/MiniMax-M2.1 -> minimaxminimaxm21
    DIR_NAME="$(slugify_model_name "${MODEL}")"
    RESULTS_DIR="${RESULTS_ROOT}/${DIR_NAME}"

    echo "=================================================="
    echo "🚀 开始运行模型: ${MODEL} ..."
    echo "📂 结果输出目录: ${RESULTS_DIR}"
    echo "=================================================="

    uv run python scripts/run_generated_tasks.py \
        "${TASK_FILES[@]}" \
        --model "${MODEL}" \
        --approval-mode approve-all \
        --workers 1 \
        --run-builder-validation \
        --strict \
        --quarantine-invalid \
        --results-dir "${RESULTS_DIR}" \
        --resume

    # 检查上一条命令是否执行成功
    if [ $? -eq 0 ]; then
        echo "✅ 模型 ${MODEL} 任务执行成功！"
    else
        echo "❌ 模型 ${MODEL} 任务执行出错，请检查日志。"
        # 如果希望某个模型出错时直接终止整个脚本，取消下面这行注释：
        # exit 1
    fi
    echo ""
done

echo "🎉 所有模型的任务已全部执行完毕！"
