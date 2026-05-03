# run_nanoclaw_workplace_suite.sh

这个脚本用于用 nanoclaw 自身框架运行并评估 200 条子集：

- `round_01_aligned_mix_subset_100`
- `persona_aligned_mix_subset_100`

默认不使用 Docker 镜像，只用内置 nanoclaw runner。评估只跑 workplace，并在结束后生成柱状图。

这两个子集合计 200 条。每个子集 100 条，四类各 25 条。

## 配置环境变量

```bash
export NANOCLAW_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_KEY="你的 API Key"

export NANOCLAW_EVAL_API_KEY="$OPENAI_API_KEY"
export NANOCLAW_EVAL_BASE_URL="$NANOCLAW_BASE_URL"

export MOCK_API_KEY="$OPENAI_API_KEY"
export MOCK_API_BASE="$NANOCLAW_BASE_URL"
export MOCK_MODEL_NAME="qwen3.5-flash"
```

## 运行

```bash
MODELS_OVERRIDE='qwen3.5-flash qwen3.5-plus deepseek-v3.2' \
WORKERS=8 \
EVAL_WORKERS=16 \
bash run_nanoclaw_workplace_suite.sh
```

如果要跑全量 1000 条，再显式指定：

```bash
DATASETS_OVERRIDE='round_01_aligned_mix_800 persona_aligned_mix_200' \
MODELS_OVERRIDE='qwen3.5-flash qwen3.5-plus deepseek-v3.2' \
WORKERS=8 \
EVAL_WORKERS=16 \
bash run_nanoclaw_workplace_suite.sh
```

## 只重新评估和画图

```bash
RUN_TASKS=0 \
RUN_EVALS=1 \
RENDER_CHARTS=1 \
MODELS_OVERRIDE='qwen3.5-flash qwen3.5-plus deepseek-v3.2' \
EVAL_WORKERS=16 \
bash run_nanoclaw_workplace_suite.sh
```

## 运行前先配置 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
uv sync
```

## 输出位置

任务结果：

```text
results/nanoclaw_workplace_suite/
```

评估结果和图：

```text
results/nanoclaw_workplace_suite_eval/
```
