# nanoclaw (minimal OpenClaw-like core)

A minimal, research-oriented agent loop that keeps only core behavior:

- dynamic file-backed context assembly
- runtime metadata and optional workspace context injection
- tool-calling loop with an OpenClaw-like core subset (`read`, `write`, `edit`, `apply_patch`, `grep`, `find`, `ls`, `exec`)
- file-backed memory helpers (`memory_search`, `memory_get`, `memory_append`)
- skill discovery plus explicit/automatic skill activation
- strict official prompt file sync + checksum manifest verification
- versioned prompt snapshots for reproducible experiments
- declarative task YAMLs, asset-backed scenario setup, and per-run result capture

This project intentionally excludes non-core engineering concerns like cross-platform packaging, chat platform integrations, rich UI rendering, and retry frameworks.

## Supported Subset

`nanoclaw` references OpenClaw's runtime contract, but it is not trying to reproduce the full OpenClaw product.

Supported concepts:

- prompt assembly from synced official templates plus workspace files
- explicit runtime tool surface
- skill discovery and activation
- approval-gated shell execution
- file-backed memory/workspace state
- reproducible task runs and traces

Intentionally not supported:

- messaging channels and provider routing
- gateway/daemon lifecycle
- browser/canvas/node/device control
- full cron infrastructure
- full multi-session orchestration fabric

## Tool Taxonomy

- Runtime tools are defined by `nanoclaw/core_loop.py` and exposed to the model directly.
- Workspace files like `TOOLS.md` are guidance files only. They do not grant capabilities.
- Skills teach the model when and how to use tools, but are not tools themselves.

## Layout

- `nanoclaw/core_loop.py`: minimal ReAct-like loop
- `nanoclaw/skills.py`: discover skills, parse `SKILL.md`, and resolve active skills
- `nanoclaw/prompt_sync.py`: sync official prompt files from `openclaw/openclaw`, write `manifest.json`, and manage prompt versions
- `nanoclaw/task_loader.py`: load task YAML files and resolve runtime settings
- `nanoclaw/run_store.py`: materialize asset-backed run directories and persist traces/results
- `nanoclaw/cli.py`: commands for bootstrap/sync/verify/run
- `skills/`: optional repo-local skill folders
- `workspace/`: shared runtime files and synced prompt files
- `tasks/`: declarative task definitions
- `assets/`: scenario templates copied into a per-run workspace
- `results/`: generated task runs, traces, and before/after snapshots

## Install

```bash
uv run python -m pip install -e .
```

## Run Tests

```bash
uv run python -m unittest discover -s tests -p 'test_*.py'
```

## 1) Bootstrap workspace

```bash
uv run python main.py bootstrap
```

This creates:

- `workspace/MEMORY.md`
- `workspace/memory/`
- `workspace/memory/<today>.md`
- `workspace/active_task.md`
- `workspace/prompts/official/`

## 2) Sync official prompt files (byte-identical copy)

By default, `sync-prompts` pulls OpenClaw runtime workspace templates (not repo-root `AGENTS.md`):

- `docs/reference/templates/AGENTS.md`
- `docs/reference/templates/SOUL.md`
- `docs/reference/templates/TOOLS.md`
- `docs/reference/templates/IDENTITY.md`
- `docs/reference/templates/USER.md`
- `docs/reference/templates/HEARTBEAT.md`
- `docs/reference/templates/BOOTSTRAP.md`

Run:

```bash
uv run python main.py sync-prompts --ref main
```

Default behavior is cache-first: if local prompt files already match `manifest.json`, it does not pull remote again.

Use `--refresh` when you want to pull remote again:

```bash
uv run python main.py sync-prompts --refresh
```

When remote prompt content changes, nanoclaw stores a new snapshot under `workspace/prompts/official/versions/<timestamp_commit>/` and keeps previous snapshots. If commit changes but prompt files are byte-identical, it reuses the existing snapshot.

The active snapshot is copied under `workspace/prompts/official/` using the same relative paths (for example `docs/reference/templates/AGENTS.md`) plus `manifest.json`.

The manifest includes source repo/ref/commit, sha256 checksums, byte counts, generation timestamp, and snapshot version id.

Note: during runtime, nanoclaw strips YAML front matter from synced template markdown so loaded prompt content matches OpenClaw's template loader behavior.
Also note: synced prompt files are treated as prompt references. They are no longer merged into the active workspace project context by default; `BOOTSTRAP.md` is first-run-only and `HEARTBEAT.md` is heartbeat-mode-only.

## 3) List and switch prompt versions

List local snapshots:

```bash
uv run python main.py sync-prompts --list-versions
```

Switch to a stored snapshot:

```bash
uv run python main.py sync-prompts --switch-version 20260325T080947Z_d41b92fff25a
```

## 4) Verify prompt integrity

```bash
uv run python main.py verify-prompts
```

If any active prompt file differs from the active manifest checksum, verification fails.

## 5) Run agent loop

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run --task "Read MEMORY.md and summarize it."
```

Or from a task file:

```bash
uv run python main.py run --task-file ./workspace/active_task.md
```

You can also inject a different runtime mode:

```bash
uv run python main.py run --run-mode heartbeat --task "Check HEARTBEAT.md and report only if needed."
```

Or continue an ad hoc local session:

```bash
uv run python main.py run --session demo --task "Summarize what we decided earlier."
```

Session history is stored locally under `workspace/sessions/<session-id>.jsonl` and trimmed deterministically by the configured message/character limits.

## 6) Run a task YAML against an asset

List tasks:

```bash
uv run python main.py list-tasks
```

Run one task:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/tutorial_workspace_brief.yaml
```

This repo now keeps a single tutorial example: `tasks/tutorial_workspace_brief.yaml`. It shows how a task can combine:

- top-level `prompts` for one or more prompt sources
- top-level `environment` for asset-backed workspace setup
- asset-backed workspace files under `assets/tutorial_workspace_brief/`
- environment-level workspace context injection
- a task-scoped skill pool where the agent can use the relevant subset
- memory lookup plus durable memory updates
- a concrete markdown deliverable written into the run workspace

Task definition:

```yaml
id: tutorial_workspace_brief
name: Tutorial Workspace Brief

prompts:
  - prompts/tutorial_workspace_brief.md

environment:
  asset: tutorial_workspace_brief
  workspace_context_files:
    - TEAM_STYLE.md
    - PROJECT_OVERVIEW.md

skills:
  available:
    - tutorial-brief-writer
    - memory-preference-checker

runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  max_steps: 16
  temperature: 0.1
```

Asset contents:

```text
assets/tutorial_workspace_brief/
  MEMORY.md
  active_task.md
  TEAM_STYLE.md
  PROJECT_OVERVIEW.md
  docs/
    briefing_notes.md
    open_questions.md
  inbox/
    user_request.md
  deliverables/
    README.md
  memory/
    2026-04-09.md
```

Run it:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/tutorial_workspace_brief.yaml
```

The run output will include:

- `results/tutorial_workspace_brief/<run-id>/workspace_before/`
- `results/tutorial_workspace_brief/<run-id>/workspace_after/`
- `results/tutorial_workspace_brief/<run-id>/final_answer.md`
- `results/tutorial_workspace_brief/<run-id>/trace.jsonl`

Task runtime fields can also declare experiment semantics such as:

- `runtime.mode`
- `runtime.session`
- `runtime.memory_policy`
- `runtime.workspace_context_files`

## 6.1) Write Your Own Task

There is also a standalone task-writing guide at `nanoclaw/doc/task_tutorial.md`.

A task in `nanoclaw` is usually made of three parts:

- a YAML file under `tasks/`
- one or more prompt files under `tasks/prompts/`
- an asset directory under `assets/<asset-name>/`

Recommended layout:

```text
tasks/
  my_task.yaml
  prompts/
    my_task.md

assets/
  my_task_asset/
    MEMORY.md
    active_task.md
    TEAM_STYLE.md
    docs/
      notes.md
```

Minimal recommended task:

```yaml
id: my_task
name: My Task
description: Short explanation of what this task is testing.

prompts:
  - prompts/my_task.md

environment:
  asset: my_task_asset
  workspace_context_files:
    - TEAM_STYLE.md

skills:
  available:
    - tutorial-brief-writer
    - memory-preference-checker

runtime:
  model: gpt-4o
  mode: interactive
  memory_policy: default
  max_steps: 12
  temperature: 0.1
```

Field guide:

- `id`: unique task id. This becomes the result group directory under `results/<id>/`.
- `name`: human-readable label for summaries and logs.
- `description`: optional note describing the scenario or what you want to evaluate.
- `prompts`: the task instruction sources. Use a single file, a list of files, or a `files` plus `inline` mapping when you want to compose the final task text from multiple parts.
- `environment.asset`: which asset directory should be copied into the run workspace before execution.
- `environment.workspace_context_files`: workspace files to inject directly into the system prompt when present.
- `skills.available`: the task-scoped skill pool. The agent can use the relevant subset; it does not need to use every listed skill.
- `skills.include`: optional forced pre-activation list. Use this only when you want a skill injected up front.
- `skills.auto`: optional boolean. When `true`, nanoclaw will auto-pick the best matching skill from the available pool.
- `runtime.model`: model used for this task run.
- `runtime.mode`: run mode injected into runtime metadata, such as `interactive` or `heartbeat`.
- `runtime.session`: optional local session id if you want continuity across repeated task runs.
- `runtime.memory_policy`: memory behavior hint. `default` is normal, `strict` pushes the agent to check memory before answering, and `off` removes memory-policy instructions from the system prompt.
- `runtime.workspace_context_files`: runtime-level override for injected workspace files. If set, it takes precedence over `environment.workspace_context_files`.
- `runtime.max_steps`: maximum tool-calling steps before the loop stops.
- `runtime.temperature`: sampling temperature for the model.

Prompt-writing advice:

- Put the concrete success criteria in the prompt file, not in the YAML metadata.
- Tell the agent exactly what files to read or write when the task is about file manipulation.
- If the task depends on remembered facts, say so explicitly in the prompt so the memory tools are relevant.
- Prefer short, testable instructions over broad open-ended requests.

Prompt file example:

```md
Read the workspace materials and prepare a short brief.

Requirements:

1. Read `MEMORY.md` and `docs/notes.md`.
2. Write `deliverables/brief.md`.
3. Use these sections:
   - Goal
   - Context
   - Next Step
4. Mention user preferences only if memory supports them.
```

Asset-writing advice:

- `MEMORY.md` should contain durable facts or preferences you want the agent to be able to recall.
- `active_task.md` is useful for scenario flavor, but the real task instruction should live in `prompts/...`.
- Add only the files the scenario actually needs. Small assets are easier to reason about and reproduce.
- Include an empty `deliverables/` directory when the task is supposed to generate files.

Skill usage in tasks:

- Put candidate skills in `skills.available`.
- At runtime, nanoclaw mirrors those skills into `.skills/<slug>/SKILL.md` inside the run workspace.
- The system prompt tells the agent to scan the skill catalog first, then `read` only the relevant `SKILL.md` files.
- This means one task can expose multiple skills while still expecting the agent to use only the ones that matter.

Running your task:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/my_task.yaml
```

After the run, inspect:

- `results/my_task/<run-id>/resolved_task.json` to see the fully resolved task payload
- `results/my_task/<run-id>/trace.jsonl` to see tool calls and loop events
- `results/my_task/<run-id>/workspace_after/` to inspect generated files

## 7) Discover and activate skills

List discovered skills:

```bash
uv run python main.py list-skills
```

Activate a skill for an ad hoc run:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run --task "Prepare a short tutorial brief for this workspace." --skill tutorial-brief-writer
```

Or ask nanoclaw to auto-select skills from the task text:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run --task "Prepare a short tutorial brief for this workspace." --auto-skills
```

`--auto-skills` now selects the single best matching skill by metadata, instead of loading every plausible skill.

Skill search roots are checked in this order:

- `<workspace>/.agents/skills`
- `./skills`
- `NANOCLAW_SKILL_DIRS` entries

Each skill lives in its own directory with a `SKILL.md` file that starts with YAML frontmatter:

```md
---
name: tutorial-brief-writer
description: Produce concise tutorial-style workspace briefs from memory and local markdown sources.
aliases:
  - tutorial-brief
  - workspace-brief
---
Use this skill when the task asks for a tutorial brief, workspace handoff, or compact project summary.
```

The tutorial run asks the agent to:

- read the tutorial workspace materials
- check memory before mentioning stable preferences
- write `deliverables/tutorial_brief.md`
- append a durable note to `MEMORY.md`

Each run creates a directory like:

```text
results/<task-id>/<run-id>/
  task.yaml
  resolved_task.json
  workspace/
  workspace_before/
  workspace_after/
  trace.jsonl
  approval_log.jsonl
  summary.json
  final_answer.md
```

The selected `assets/<asset-name>/` tree is copied into `results/.../workspace/` before execution, then `workspace_before/` and `workspace_after/` snapshots are written around the run.

If skills are activated, both `resolved_task.json` and `summary.json` record the requested/auto-selected skill metadata and checksums for that run.

For the tutorial example, a successful run would leave files like these under `results/tutorial_workspace_brief/<run-id>/workspace_after/`:

```text
deliverables/tutorial_brief.md
MEMORY.md
active_task.md
```

## 8) Run tasks with an external agent framework

`nanoclaw` can also act as a benchmark orchestrator for a real agent framework running
inside Docker. In this mode, `nanoclaw` still owns task loading, asset setup, run
directories, snapshots, summaries, and evaluation; the containerized framework owns
the actual agent loop.

The current external runners are:

| Framework | Base image | Local image | Runner profile |
| --- | --- | --- | --- |
| OpenClaw | `ghcr.io/openclaw/openclaw:latest` | `nanoclaw-runner-openclaw:latest` | `runner_profiles/openclaw.yaml` |
| Hermes Agent | `nousresearch/hermes-agent:latest` | `nanoclaw-runner-hermes:latest` | `runner_profiles/hermes.yaml` |

Build the runner images:

```bash
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
```

If Docker Hub returns `429 Too Many Requests` while building the Hermes image,
run `docker login` and retry the build. The OpenClaw image is hosted on GHCR; the
Hermes image is currently pulled from Docker Hub.

Run one task with a real framework:

```bash
OPENAI_API_KEY=... \
uv run python main.py run-task \
  --task tasks/my_task.yaml \
  --runner-profile runner_profiles/openclaw.yaml

OPENAI_API_KEY=... \
uv run python main.py run-task \
  --task tasks/my_task.yaml \
  --runner-profile runner_profiles/hermes.yaml
```

Batch runs use the same `--runner-profile` flag:

```bash
OPENAI_API_KEY=... \
uv run python scripts/run_generated_tasks.py \
  tasks/data_round_01_*.yaml \
  --runner-profile runner_profiles/openclaw.yaml \
  --results-dir results/openclaw_base

OPENAI_API_KEY=... \
uv run python scripts/run_generated_tasks.py \
  tasks/data_round_01_*.yaml \
  --runner-profile runner_profiles/hermes.yaml \
  --results-dir results/hermes_base
```

A Docker runner profile declares the image, adapter command, timeout, resource
limits, network mode, and environment variables that may be passed from the host.
The task YAML remains framework-agnostic; framework selection happens at runtime
through `--runner-profile`.

### Runner adapter contract

Each framework image only adds `/opt/nanoclaw-adapter/run_task` on top of the
official framework image. The adapter receives mounted nanoclaw inputs and writes
normalized outputs:

```text
/workspace/                 writable task workspace
/input/task.md              current prompt
/input/resolved_task.json   resolved task metadata
/input/prior_messages.json  prior turn/session messages
/input/runner_request.json  runtime metadata
/output/final_answer.md     required final answer
/output/trace.jsonl         normalized runner trace events
/output/*_stdout.log        raw framework stdout
/output/*_stderr.log        raw framework stderr
/output/runner_metadata.json adapter/framework metadata
/state/                     writable runner state, reused across turns
```

`nanoclaw` records Docker stdout/stderr, Docker inspect output, runner events,
`workspace_before/`, `workspace_after/`, `final_answer.md`, `trace.jsonl`, and
runner metadata in `summary.json`. The container is removed after the run by default.

Multi-turn runs do not keep containers alive. Instead, `nanoclaw` reuses `/state`
across turns, so framework config, sessions, and cache can persist while each turn
still starts from a clean container process.

### OpenClaw runner

The OpenClaw runner extends the official `ghcr.io/openclaw/openclaw:latest` image.
Its adapter calls:

```text
openclaw agent --local --message <task prompt> --json --session-id <run session> --model <model>
```

Common OpenClaw settings:

- `NANOCLAW_MODEL`: passed as OpenClaw `--model`; defaults to the task/runtime model
- `NANOCLAW_BASE_URL`: copied to `OPENAI_BASE_URL` for OpenAI-compatible endpoints
- `NANOCLAW_OPENCLAW_AGENT`: pass `--agent <id>` instead of `--session-id`
- `NANOCLAW_OPENCLAW_THINKING`: pass `--thinking <level>`
- `NANOCLAW_OPENCLAW_TIMEOUT`: pass OpenClaw `--timeout <seconds>`
- `NANOCLAW_OPENCLAW_VERBOSE`: pass OpenClaw `--verbose on|off`; `1` maps to `on`
- `NANOCLAW_OPENCLAW_INCLUDE_PRIOR_MESSAGES=1`: include prior turn messages in the prompt body
- `NANOCLAW_OPENCLAW_AUTO_ONBOARD=0`: skip adapter-managed non-interactive onboarding
- `NANOCLAW_OPENCLAW_ISOLATED_HOME=0`: use the image's existing OpenClaw home/config

By default the adapter isolates OpenClaw home/config/cache under `/state`. When
`OPENAI_API_KEY` is available and OpenClaw has not yet been configured in `/state`,
the adapter attempts a non-interactive local OpenClaw onboarding step before the
task run. For a custom OpenAI-compatible endpoint, pass `NANOCLAW_BASE_URL`,
`NANOCLAW_MODEL`, and `OPENAI_API_KEY` or `CUSTOM_API_KEY`.

### Hermes runner

The Hermes runner extends the official `nousresearch/hermes-agent:latest` image.
Its adapter defaults to Hermes one-shot mode:

```text
hermes -z <task prompt>
```

This mode returns only the final response on stdout. If `NANOCLAW_HERMES_TOOLSETS`,
`NANOCLAW_HERMES_SKILLS`, `NANOCLAW_HERMES_MAX_TURNS`, `NANOCLAW_HERMES_SOURCE`,
`NANOCLAW_HERMES_RESUME`, or `NANOCLAW_HERMES_CONTINUE` is set, the adapter switches
to chat mode:

```text
hermes chat --quiet -q <task prompt>
```

Common Hermes settings:

- `NANOCLAW_MODEL`: copied to `HERMES_INFERENCE_MODEL` and passed as `--model`
- `NANOCLAW_BASE_URL`: copied to `OPENAI_BASE_URL` for OpenAI-compatible endpoints
- `NANOCLAW_HERMES_PROVIDER`: copied to `HERMES_INFERENCE_PROVIDER` and passed as `--provider`
- `NANOCLAW_HERMES_MODEL`: override the Hermes model independently of `NANOCLAW_MODEL`
- `NANOCLAW_HERMES_MODE=chat|oneshot`: force the adapter mode
- `NANOCLAW_HERMES_TOOLSETS`: pass Hermes `--toolsets`
- `NANOCLAW_HERMES_SKILLS`: pass Hermes `--skills`
- `NANOCLAW_HERMES_MAX_TURNS`: pass Hermes `--max-turns`
- `NANOCLAW_HERMES_YOLO=1`: pass Hermes `--yolo`
- `NANOCLAW_HERMES_IGNORE_USER_CONFIG=1`: pass Hermes `--ignore-user-config`
- `NANOCLAW_HERMES_IGNORE_RULES=1`: pass Hermes `--ignore-rules`
- `NANOCLAW_HERMES_INCLUDE_PRIOR_MESSAGES=0`: do not include prior turn messages in the prompt body

Hermes state is stored under `/state` by setting `HERMES_HOME=/state`.

## Environment variables

- `OPENAI_API_KEY`: required when `NANOCLAW_BASE_URL` is not set
- `NANOCLAW_BASE_URL`: optional custom OpenAI-compatible endpoint
- `NANOCLAW_MODEL`: default `gpt-4o`
- `NANOCLAW_WORKSPACE_DIR`: default `workspace`
- `NANOCLAW_PROMPT_DIR`: default `workspace/prompts/official`
- `NANOCLAW_PROMPT_FILES`: default `docs/reference/templates/AGENTS.md,docs/reference/templates/SOUL.md,docs/reference/templates/TOOLS.md,docs/reference/templates/IDENTITY.md,docs/reference/templates/USER.md,docs/reference/templates/HEARTBEAT.md,docs/reference/templates/BOOTSTRAP.md`; injected as prompt references, with `BOOTSTRAP.md` only on first-run bootstrap and `HEARTBEAT.md` only in heartbeat mode
- `NANOCLAW_SKILL_DIRS`: optional extra comma-separated skill directories
- `NANOCLAW_MAX_STEPS`: default `15`
- `NANOCLAW_TEMPERATURE`: default `0.2`

## Standalone sync script

```bash
uv run python scripts/sync_openclaw_prompts.py --list-versions
uv run python scripts/sync_openclaw_prompts.py --switch-version <version-id>
uv run python scripts/sync_openclaw_prompts.py --refresh --ref main
```
