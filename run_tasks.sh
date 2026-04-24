#!/bin/bash

# 定义需要运行的模型数组
MODELS=(
    "qwen3-32b"
    "qwen2.5-14b-instruct-1m"
    "deepseek-v3"
)

# 遍历每个模型并执行命令
for MODEL in "${MODELS[@]}"; do
    # 动态生成目录名称：移除模型名称中的连字符(-)和点号(.)
    # 例如：qwen2.5-14b-instruct-1m -> qwen2514binstruct1m
    DIR_NAME="${MODEL//[-.]/}"
    RESULTS_DIR="results/${DIR_NAME}"

    echo "=================================================="
    echo "🚀 开始运行模型: ${MODEL} ..."
    echo "📂 结果输出目录: ${RESULTS_DIR}"
    echo "=================================================="

    uv run python scripts/run_generated_tasks.py \
        --model "${MODEL}" \
        --approval-mode approve-all \
        --workers 16 \
        --run-builder-validation \
        --strict \
        --quarantine-invalid \
        --results-dir "${RESULTS_DIR}" \
        --evaluate \
        --enable-judge \
        --judge-model qwen3.5-27b \
        --judge-max-attempts 2 \
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