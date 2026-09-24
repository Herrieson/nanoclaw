<div align="center">
<h1>ClawBenchPro</h1>
<h3>Benchmarking How Well Agent Harnesses Work</h3>

[![English README](https://img.shields.io/badge/README-English-ef9a9a?style=for-the-badge)](README.md)
[![Dataset](https://img.shields.io/badge/Dataset-1%2C000_Tasks-4d8cd8?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/datasets/ErenJaegerYeager/ClawBenchPro)
[![Harnesses](https://img.shields.io/badge/Harnesses-4_Frameworks-63cad3?style=for-the-badge)](src/nanoclaw/runner_profiles/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
</div>

---

## 1. 📖 项目概览

**ClawBenchPro** 用于评估 agent harness 如何帮助语言模型完成专业工作场景中的任务。本仓库统一公开 **1,000 条评测任务**、**NanoClaw 执行与评测代码**，以及 **OpenClaw、Hermes-Agent、Codex** 的适配器。

对应手稿《ClawBenchPro: Benchmarking How Well Agent Harnesses Work》描述了覆盖 **43 个专业领域**的基准，包含基础任务、多轮交互、复杂环境和技能增强四类场景。

```text
任务 YAML + 提示词 → 环境构建器 → Agent 框架执行
                                      ↓
评测报告 ← 工作区验证器 ← 最终工作区状态
```

评测以智能体实际生成的工作区为依据：环境构建器准备初始文件，指定框架执行交互，工作区验证器检查最终状态。多框架评测入口默认采用仅工作区评分。

**Hugging Face 数据集：** [ErenJaegerYeager/ClawBenchPro](https://huggingface.co/datasets/ErenJaegerYeager/ClawBenchPro)。

---

## 2. 📁 项目结构

```text
ClawBenchPro/
├── README.md                         # English
├── README_zh.md                      # 中文
├── LICENSE
├── data/ClawBenchPro/
│   ├── round_01_aligned_mix_800/      # 800 tasks
│   ├── persona_aligned_mix_200/       # 200 tasks
│   ├── dataset_index.csv
│   └── materialize_assets.py
├── examples/
│   ├── smoke_test.py
│   └── verify_data.py
├── docs/
│   ├── data-format.md
│   └── research-notes.md
└── src/nanoclaw/
    ├── nanoclaw/                     # Runtime, task loading, evaluation
    ├── scripts/                      # Batch execution and reporting
    ├── runner_profiles/              # OpenClaw / Hermes / Codex
    ├── docker/                       # External harness adapters
    └── tests/                        # Runner regression tests
```

---

## 3. 🧩 主要内容

### 3.1 评测数据集

| 数据包 | 基础 | 多轮 | 复杂环境 | 技能 | 合计 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `round_01_aligned_mix_800` | 200 | 200 | 200 | 200 | 800 |
| `persona_aligned_mix_200` | 50 | 50 | 50 | 50 | 200 |
| **合计** | **250** | **250** | **250** | **250** | **1,000** |

每个数据包包含任务 YAML、Markdown 提示词、工作区构建器、可选技能、verifier JSONL、评测清单和来源记录。800 条任务数据包使用 `multi_turn_aligned`、`hard_aligned`、`skills_aligned` 作为组名；persona 数据包使用 `multi_turn`、`hard`、`skills`。

初始工作区以紧凑的构建器形式发布，在执行时生成。详细结构见[数据格式说明](docs/data-format.md)和[数据卡](data/ClawBenchPro/README.md)。

### 3.2 执行与评测流程

| 组件 | 作用 | 代码位置 |
| --- | --- | --- |
| 任务加载器 | 解析任务配置与提示词 | [task_loader.py](src/nanoclaw/nanoclaw/task_loader.py) |
| 批量执行器 | 准备工作区并执行任务 | [batch_runner.py](src/nanoclaw/nanoclaw/batch_runner.py) |
| NanoClaw 循环 | 组织模型推理与工具交互 | [core_loop.py](src/nanoclaw/nanoclaw/core_loop.py) |
| Docker 适配器 | 接入其他智能体框架 | [docker/](src/nanoclaw/docker/) |
| 工作区评测 | 使用任务验证器对运行结果判分 | [评测脚本](src/nanoclaw/scripts/evaluate_workplace_trace_tasks.py) |
| 实验入口 | 运行框架与模型组合并汇总评测 | [数据包运行脚本](src/nanoclaw/scripts/run_clawbenchpro_subset.py) |

### 3.3 支持的框架

| 框架 | 执行方式 | 配置与说明 |
| --- | --- | --- |
| NanoClaw | 内置 Python runner | [运行文档](src/nanoclaw/README.md) |
| OpenClaw | Docker 适配器 | [配置](src/nanoclaw/runner_profiles/openclaw.yaml) · [适配器说明](src/nanoclaw/docker/openclaw-runner/README.md) |
| Hermes-Agent | Docker 适配器 | [配置](src/nanoclaw/runner_profiles/hermes.yaml) |
| Codex | Docker 适配器 | [配置](src/nanoclaw/runner_profiles/codex.yaml) · [适配器说明](src/nanoclaw/docker/codex-runner/README.md) |

模型与服务端点的兼容性由所选框架决定。跨框架实验前，需要按对应 profile 配置模型服务及环境变量。

---

## 4. 🚀 复现评测

### 4.1 下载与安装

需要 **Python 3.12.10 或更新版本**、**uv**、**Git LFS**；运行外部框架还需要 Docker。下面的克隆地址在仓库更名后仍可通过 GitHub 重定向使用。

```bash
# Git LFS is required for the benchmark JSONL files.
git lfs install
git clone git@github.com:Herrieson/nanoclaw.git ClawBenchPro
cd ClawBenchPro
git lfs pull
python3 examples/verify_data.py

cd src/nanoclaw
uv sync
uv run python -m unittest discover -s tests -p 'test_*.py'
```

### 4.2 查看并运行单个任务

`--list-only` 只显示选中的任务，不调用模型；`--run` 会实际执行任务，需要模型凭据。请使用与 runner 相同的 `uv` 环境：

```bash
# Run from ClawBenchPro/src/nanoclaw.
uv run python ../../examples/smoke_test.py --list-only

export OPENAI_API_KEY="<your-api-key>"
export NANOCLAW_MODEL="<your-model>"
# Optional: OpenAI-compatible endpoint
# export NANOCLAW_BASE_URL="https://your-endpoint/v1"

uv run python ../../examples/smoke_test.py --run
```

示例默认选择 `round_01_aligned_mix_800` 中的第一条任务。可通过 `--dataset persona_aligned_mix_200` 切换数据包，或通过 `--task <task-id>` 指定任务。结果写入仓库根目录的 `results/smoke/`。此示例只执行任务；执行并评分请使用下面的数据包工作流。

### 4.3 跨框架对比

构建需要使用的适配器镜像，然后运行评测矩阵：

```bash
# Run from ClawBenchPro/src/nanoclaw.
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
docker build -t nanoclaw-runner-codex:latest docker/codex-runner

uv run python scripts/run_clawbenchpro_subset.py \
  ../../data/ClawBenchPro \
  --datasets persona_aligned_mix_200 \
  --runners nanoclaw openclaw hermes codex \
  --models "$NANOCLAW_MODEL" \
  --workers 2 --eval-workers 4 \
  --components workplace
```

以上命令对 **4 个框架分别运行完整的 200 条任务**，不是单任务 smoke test。仅测试内置框架时使用 `--runners nanoclaw`；选择 `round_01_aligned_mix_800` 可运行另一个数据包，省略 `--datasets` 则运行两个数据包。添加 `--no-run-tasks` 可只对已有运行结果评分。

### 4.4 查看结果

```bash
# Run from ClawBenchPro/src/nanoclaw.
uv run python scripts/summarize_clawbenchpro_results.py results/clawbenchpro_eval
```

数据包运行结果位于 `src/nanoclaw/results/clawbenchpro_runs/`；评测 JSON、CSV 和汇总位于 `src/nanoclaw/results/clawbenchpro_eval/`，按数据包、框架和模型组织。生成的结果默认不纳入 Git。

---

## 5. 🔎 数据完整性与研究范围

`examples/verify_data.py` 校验两个子集的可移植 checksum 清单。整理时，发布文件通过了 **7,756 项校验**。这代表文件完整性，不等同于验证了所有任务语义或复现了模型表现。

本仓库提供评测数据和框架适配器，暂未附带论文实验的运行结果或复现排行榜。相关材料对应关系见[研究说明](docs/research-notes.md)。

---

## 6. 📄 许可证与致谢

代码与数据保留原有 **MIT** 许可证及版权声明：[仓库许可证](LICENSE)、[执行器许可证](src/nanoclaw/LICENSE)、[数据集许可证](data/ClawBenchPro/LICENSE)。外部框架遵循各自许可证。感谢 NanoClaw 运行时及适配器所使用的 OpenClaw、Hermes-Agent 和 Codex 生态。
