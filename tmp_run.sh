#!/bin/bash

echo "正在启动第一阶段：Qwen 系列模型..."
RUNNER_PROFILE= \
RUNNER_NAME='nanoclaw' \
RESULTS_ROOT=results/nanoclaw_workplace_suite \
RUN_TASKS=1 \
RUN_EVALS=0 \
RENDER_CHARTS=0 \
RESUME=1 \
DATASETS_OVERRIDE='round_01_aligned_mix_subset_100 persona_aligned_mix_subset_100' \
MODELS_OVERRIDE='qwen3.5-27b qwen3.5-flash qwen3.5-plus qwen3.6-plus' \
WORKERS=16 \
bash run_nanoclaw_workplace_suite.sh

echo "第一阶段完成，正在启动第二阶段：DeepSeek/GLM/MiniMax 系列..."

RUNNER_PROFILE= \
RUNNER_NAME='nanoclaw' \
RESULTS_ROOT=results/nanoclaw_workplace_suite \
RUN_TASKS=1 \
RUN_EVALS=0 \
RENDER_CHARTS=0 \
RESUME=1 \
DATASETS_OVERRIDE='round_01_aligned_mix_subset_100 persona_aligned_mix_subset_100' \
MODELS_OVERRIDE='deepseek-v3.2 deepseek-v4-flash deepseek-v4-pro glm-4.7 glm-5.1 MiniMax-M2.1 MiniMax-M2.5' \
WORKERS=4 \
bash run_nanoclaw_workplace_suite.sh

echo "全部任务已执行完毕。"