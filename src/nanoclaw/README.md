# nanoclaw

Nanoclaw is a research-oriented agent benchmark runner. It provides:

- a minimal OpenClaw-like agent loop for built-in Nanoclaw runs
- declarative workplace task loading
- asset-backed task workspaces
- skill discovery and task-scoped skill injection
- multi-turn task execution with trace capture
- Docker adapters for external agent frameworks
- workplace evaluation, chart rendering, and Excel export

The project is designed for benchmark orchestration and reproducible agent
evaluation, not as a full OpenClaw replacement.

## Repository Scope

This GitHub repository contains source code, runner adapters, scripts, tests,
and prompt snapshots.

The benchmark dataset is hosted separately on Hugging Face:

- ClawBenchPro: <https://huggingface.co/datasets/ErenJaegerYeager/ClawBenchPro>

Generated benchmark files are runtime or release artifacts and should stay out
of the source repository:

- `tasks/`
- `assets/`
- `results/`
- `.staging/`
- `published_datasets/`
- `ClawBenchPro/`

Use the Hugging Face dataset package when you want to run the benchmark tasks.

## Layout

- `nanoclaw/`: core runtime, task loading, batch runner, Docker runner, and evaluation code
- `scripts/`: dataset packaging, evaluation, charting, and export utilities
- `docker/`: external runner images and adapters
- `runner_profiles/`: Docker runner profiles
- `skills/`: small repo-local example skills used by tests and task fixtures
- `workspace/prompts/official/`: synced OpenClaw prompt template snapshots
- `tests/`: unit tests
- `run_evals.sh`: evaluation helper

## Install

Install editable dependencies with `uv`:

```bash
uv run python -m pip install -e .
```

Run the unit tests:

```bash
uv run python -m unittest discover -s tests -p 'test_*.py'
```

Bootstrap local workspace files:

```bash
uv run python main.py bootstrap
```

Verify the synced prompt snapshot:

```bash
uv run python main.py verify-prompts
```

## Model Environment

For the built-in Nanoclaw runner, set either a direct OpenAI key or an
OpenAI-compatible endpoint:

```bash
export OPENAI_API_KEY="<your-key>"
export NANOCLAW_MODEL="gpt-4o"
```

For OpenAI-compatible gateways:

```bash
export OPENAI_API_KEY="<your-key-or-provider-key>"
export NANOCLAW_BASE_URL="https://your-endpoint/v1"
export NANOCLAW_MODEL="qwen3.5-flash"
```

Common environment variables:

- `OPENAI_API_KEY`: default API key used by Nanoclaw and several adapters
- `NANOCLAW_BASE_URL`: optional OpenAI-compatible base URL
- `NANOCLAW_MODEL`: default model name
- `NANOCLAW_TEMPERATURE`: default `0.2`
- `NANOCLAW_MAX_STEPS`: default `15`
- `NANOCLAW_WORKSPACE_DIR`: default `workspace`
- `NANOCLAW_SKILL_DIRS`: optional comma-separated extra skill roots

## Prepare ClawBenchPro

Download the benchmark package from Hugging Face:

```bash
uv run hf download \
  ErenJaegerYeager/ClawBenchPro \
  --repo-type dataset \
  --local-dir ClawBenchPro
```

Copy tasks, task-local skills, and suite manifests into the local Nanoclaw
workspace:

```bash
mkdir -p tasks skills .staging/round_01_aligned_mix_800 .staging/persona_aligned_mix_200

cp -a ClawBenchPro/round_01_aligned_mix_800/tasks/. tasks/
cp -a ClawBenchPro/persona_aligned_mix_200/tasks/. tasks/

cp -a ClawBenchPro/round_01_aligned_mix_800/skills/. skills/
cp -a ClawBenchPro/persona_aligned_mix_200/skills/. skills/

cp -a ClawBenchPro/round_01_aligned_mix_800/selection_manifest.jsonl \
  .staging/round_01_aligned_mix_800/selection_manifest.jsonl
cp -a ClawBenchPro/round_01_aligned_mix_800/import_manifest.jsonl \
  .staging/round_01_aligned_mix_800/import_manifest.jsonl

cp -a ClawBenchPro/persona_aligned_mix_200/selection_manifest.jsonl \
  .staging/persona_aligned_mix_200/selection_manifest.jsonl
cp -a ClawBenchPro/persona_aligned_mix_200/import_manifest.jsonl \
  .staging/persona_aligned_mix_200/import_manifest.jsonl
```

ClawBenchPro is published in compact builder form. Prebuilt `assets/` are not
included. Each task carries a local `env_builder.py`; Nanoclaw's batch runner
uses those builders automatically before each task run.

To materialize assets inside the downloaded dataset package for inspection:

```bash
uv run python ClawBenchPro/materialize_assets.py \
  --dataset round_01_aligned_mix_800 \
  --workers 8
```

## ClawBenchPro Subset Workflow

Run and evaluate a local subset package such as
`../nanoclaw_datasets/ClawBenchPro_subsets/smoke_40`:

```bash
uv run python scripts/run_clawbenchpro_subset.py \
  ../nanoclaw_datasets/ClawBenchPro_subsets/smoke_40 \
  --runners nanoclaw openclaw hermes codex \
  --models qwen3.5-flash \
  --workers 2 \
  --eval-workers 8
```

Create or rebuild deterministic subsets:

```bash
uv run python scripts/build_clawbenchpro_subsets.py --write --overwrite

uv run python scripts/build_clawbenchpro_subsets.py \
  --custom-name smoke_80 \
  --round-per-group 10 \
  --persona-per-group 10 \
  --write
```

View result summaries:

```bash
uv run python scripts/summarize_clawbenchpro_results.py results/clawbenchpro_eval
```

## Smoke Test

Run one task with the built-in Nanoclaw runner:

```bash
uv run python scripts/run_generated_tasks.py \
  tasks/data_round_01_aligned_mix_800_0001.yaml \
  --model qwen3.5-flash \
  --approval-mode reject \
  --workers 1 \
  --results-dir results/smoke_nanoclaw/qwen35flash \
  --resume \
  --skip-validation \
  --skip-normalize \
  --skip-auto-fix
```

Run one task with a Docker runner:

```bash
uv run python scripts/run_generated_tasks.py \
  tasks/data_round_01_aligned_mix_800_0001.yaml \
  --model qwen3.5-flash \
  --approval-mode reject \
  --workers 1 \
  --results-dir results/smoke_codex/qwen35flash \
  --runner-profile runner_profiles/codex.yaml \
  --resume \
  --skip-validation \
  --skip-normalize \
  --skip-auto-fix
```

## Docker Runners

Nanoclaw can orchestrate external agent frameworks in Docker. The source repo
currently includes three adapters:

| Framework | Local image | Runner profile |
| --- | --- | --- |
| OpenClaw | `nanoclaw-runner-openclaw:latest` | `runner_profiles/openclaw.yaml` |
| Hermes Agent | `nanoclaw-runner-hermes:latest` | `runner_profiles/hermes.yaml` |
| Codex | `nanoclaw-runner-codex:latest` | `runner_profiles/codex.yaml` |

Build the images:

```bash
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
docker build -t nanoclaw-runner-codex:latest docker/codex-runner
```

Run benchmark tasks directly with `scripts/run_generated_tasks.py`. Omit
`--runner-profile` for the built-in Nanoclaw runner, or pass one of the Docker
profiles:

```bash
uv run python scripts/run_generated_tasks.py <task-yaml-globs...> \
  --model qwen3.5-flash \
  --approval-mode reject \
  --workers 2 \
  --results-dir results/clawbenchpro_smoke_40/openclaw/qwen35flash \
  --runner-profile runner_profiles/openclaw.yaml \
  --resume \
  --skip-validation \
  --skip-normalize \
  --skip-auto-fix
```

## Evaluation Outputs

Evaluate completed workplace runs with `scripts/evaluate_workplace_trace_tasks.py`.
The evaluator writes detailed JSON, CSV, an aggregate summary, and a
self-contained `*_records.jsonl` file with prompts, trace events, verifier code,
and verifier result for each run.

Per model and dataset, write evaluation files under a chosen eval root such as:

```text
<eval-root>/<runner>/<model-slug>/
```

Important files:

- `evaluation.json`: per-task evaluation rows
- `*_records.jsonl`: self-contained per-run records
- `evaluation_summary.json`: aggregate metrics for one model and dataset
- `charts/*.svg`: dataset and category charts

For final benchmark reporting, use `average_objective_score` as the main score.
`perfect_score_rate` is the share of evaluated tasks that reached a perfect
objective score.

## Runner Adapter Contract

Each Docker image adds `/opt/nanoclaw-adapter/run_task`. Nanoclaw mounts the task
workspace and normalized input files, then expects normalized outputs:

```text
/workspace/                 writable task workspace
/input/task.md              current task prompt
/input/resolved_task.json   resolved task metadata
/input/prior_messages.json  prior turn/session messages
/input/runner_request.json  runtime metadata
/output/final_answer.md     final answer
/output/trace.jsonl         normalized runner trace events
/output/*_stdout.log        raw framework stdout
/output/*_stderr.log        raw framework stderr
/output/runner_metadata.json adapter/framework metadata
/state/                     writable runner state reused across turns
```

Nanoclaw records Docker stdout/stderr, inspect metadata, runner events,
`workspace_before/`, `workspace_after/`, `final_answer.md`, `trace.jsonl`, and
summary metadata in the run directory.

## Prompt Sync

Nanoclaw stores versioned prompt snapshots under `workspace/prompts/official/`.

Sync current OpenClaw template prompts:

```bash
uv run python main.py sync-prompts --refresh --ref main
```

List local prompt snapshots:

```bash
uv run python main.py sync-prompts --list-versions
```

Switch to a stored snapshot:

```bash
uv run python main.py sync-prompts --switch-version <version-id>
```

## Task Authoring

The public benchmark tasks are distributed through ClawBenchPro. For local
experiments, a Nanoclaw task usually has:

- one YAML file under `tasks/`
- one or more prompt files under `tasks/prompts/`
- either a prebuilt asset directory under `assets/<task-id>/` or a task-local
  `tasks/<task-id>/env_builder.py`

Minimal task shape:

```yaml
id: my_task
name: My Task
prompts:
  - prompts/my_task.md
environment:
  asset: my_task
skills:
  available:
    - tutorial-brief-writer
runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  approval_mode: auto-approve
  max_steps: 50
  temperature: 0.1
```

More details are in `nanoclaw/doc/task_tutorial.md`.

## Dataset Packaging Maintainers

These scripts are for rebuilding the hosted dataset package from local staging
artifacts:

```bash
uv run python scripts/build_published_workplace_datasets.py --force
uv run python scripts/build_clawbenchpro_hf_dataset.py --force
```

The generated `published_datasets/` and `ClawBenchPro/` directories are release
artifacts. They should be uploaded to the dataset host, not committed to this
source repository.

## Repository Hygiene

Do not commit generated benchmark artifacts or local runtime state:

- `results/`
- `.staging/`
- `tasks/`
- `assets/`
- `published_datasets/`
- `ClawBenchPro/`
- `.env`
- `.openclaw/`
- `workspace/sessions/`
- `workspace/memory/`
- `workspace/.agents/`

The source repository should stay small enough to clone quickly. Full benchmark
tasks, manifests, Croissant metadata, and dataset cards belong in the Hugging
Face dataset repository.
