# run_docker_workplace_suite.sh

这个脚本用于用 Docker runner 运行并评估：

- `round_01_aligned_mix_800`
- `persona_aligned_mix_200`

默认会依次跑这三个镜像 runner：

- `openclaw` -> `runner_profiles/openclaw.yaml`
- `hermes` -> `runner_profiles/hermes.yaml`
- `codex` -> `runner_profiles/codex.yaml`

评估只跑 workplace，并在结束后生成柱状图。

## 先构建镜像

```bash
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
docker build -t nanoclaw-runner-codex:latest docker/codex-runner
```

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
RUNNERS_OVERRIDE='openclaw hermes codex' \
MODELS_OVERRIDE='qwen3.5-flash qwen3.5-plus deepseek-v3.2' \
WORKERS=8 \
EVAL_WORKERS=16 \
bash run_docker_workplace_suite.sh
```

## 只跑某个镜像

```bash
RUNNERS_OVERRIDE='hermes' \
MODELS_OVERRIDE='qwen3.5-flash' \
WORKERS=8 \
EVAL_WORKERS=16 \
bash run_docker_workplace_suite.sh
```

## 只重新评估和画图

```bash
RUN_TASKS=0 \
RUN_EVALS=1 \
RENDER_CHARTS=1 \
RUNNERS_OVERRIDE='openclaw hermes codex' \
MODELS_OVERRIDE='qwen3.5-flash qwen3.5-plus deepseek-v3.2' \
EVAL_WORKERS=16 \
bash run_docker_workplace_suite.sh
```

## 输出位置

任务结果：

```text
results/docker_workplace_suite/<runner>/<dataset>/<model>/
```

评估结果和图：

```text
results/docker_workplace_suite_eval/<runner>/<dataset>/
results/docker_workplace_suite_eval/docker_runner_dataset_model_comparison.svg
```

例如：

```text
results/docker_workplace_suite/openclaw/persona_aligned_mix_200/qwen35flash/
results/docker_workplace_suite_eval/openclaw/persona_aligned_mix_200/merged/qwen35flash/evaluation_summary.json
```
