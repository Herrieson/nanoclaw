#!/bin/bash

# 定义所有需要评估的模型名称数组
MODELS=(
    "qwen36p"
    "qwen3527b"
    "gpt54"
    "gpt52"
    "gpt4o"
    "mock-noop"
)

# 遍历每个模型并执行命令
for MODEL in "${MODELS[@]}"; do
    echo "=================================================="
    echo "🚀 开始评估模型: ${MODEL} ..."
    echo "=================================================="

    uv run python scripts/evaluate_generated_tasks.py \
        "results/${MODEL}/data_*/*" \
        --json-out "results/${MODEL}/evaluation.json" \
        --csv-out "results/${MODEL}/evaluation.csv" \
        --summary-out "results/${MODEL}/evaluation_summary.json" \
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