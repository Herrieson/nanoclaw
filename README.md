# nanoclaw (minimal OpenClaw-like core)

A minimal, research-oriented agent loop that keeps only core behavior:

- dynamic file-backed context assembly
- tool-calling loop (read/write, dangerous command gate, ask-human)
- strict official prompt file sync + checksum manifest verification
- versioned prompt snapshots for reproducible experiments
- declarative task YAMLs, asset-backed scenario setup, and per-run result capture

This project intentionally excludes non-core engineering concerns like cross-platform packaging, chat platform integrations, rich UI rendering, and retry frameworks.

## Layout

- `nanoclaw/core_loop.py`: minimal ReAct-like loop
- `nanoclaw/prompt_sync.py`: sync official prompt files from `openclaw/openclaw`, write `manifest.json`, and manage prompt versions
- `nanoclaw/task_loader.py`: load task YAML files and resolve runtime settings
- `nanoclaw/run_store.py`: materialize asset-backed run directories and persist traces/results
- `nanoclaw/cli.py`: commands for bootstrap/sync/verify/run
- `workspace/`: shared runtime files and synced prompt files
- `tasks/`: declarative task definitions
- `assets/`: scenario templates copied into a per-run workspace
- `results/`: generated task runs, traces, and before/after snapshots

## Install

```bash
uv run python -m pip install -e .
```

## 1) Bootstrap workspace

```bash
uv run python main.py bootstrap
```

This creates:

- `workspace/MEMORY.md`
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

## 6) Run a task YAML against an asset

List tasks:

```bash
uv run python main.py list-tasks
```

Run one task:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/summarize_memory.yaml
```

A more realistic example in this repo is `tasks/incident_review.yaml`. It uses `task.task_file` to point at a longer prompt file and pulls its starting workspace from `assets/incident_review/`.

Task definition:

```yaml
id: incident_review
name: Incident Review
asset: incident_review

task:
  task_file: prompts/incident_review.md

runtime:
  model: gpt-4o
  max_steps: 18
  temperature: 0.1
```

Asset contents:

```text
assets/incident_review/
  MEMORY.md
  active_task.md
  reports/
    incident_report.md
    timeline.md
```

Run it:

```bash
export OPENAI_API_KEY="<your-key>"
uv run python main.py run-task --task tasks/incident_review.yaml
```

That run asks the agent to:

- read the incident notes and timeline
- write `deliverables/executive_summary.md`
- write `deliverables/customer_update.md`
- update `active_task.md` with the completed handoff

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

For the incident example, a successful run would leave files like these under `results/incident_review/<run-id>/workspace_after/`:

```text
deliverables/executive_summary.md
deliverables/customer_update.md
active_task.md
```

## Environment variables

- `OPENAI_API_KEY`: required when `NANOCLAW_BASE_URL` is not set
- `NANOCLAW_BASE_URL`: optional custom OpenAI-compatible endpoint
- `NANOCLAW_MODEL`: default `gpt-4o`
- `NANOCLAW_WORKSPACE_DIR`: default `workspace`
- `NANOCLAW_PROMPT_DIR`: default `workspace/prompts/official`
- `NANOCLAW_PROMPT_FILES`: default `docs/reference/templates/AGENTS.md,docs/reference/templates/SOUL.md,docs/reference/templates/TOOLS.md,docs/reference/templates/IDENTITY.md,docs/reference/templates/USER.md,docs/reference/templates/HEARTBEAT.md,docs/reference/templates/BOOTSTRAP.md`
- `NANOCLAW_MAX_STEPS`: default `15`
- `NANOCLAW_TEMPERATURE`: default `0.2`

## Standalone sync script

```bash
uv run python scripts/sync_openclaw_prompts.py --list-versions
uv run python scripts/sync_openclaw_prompts.py --switch-version <version-id>
uv run python scripts/sync_openclaw_prompts.py --refresh --ref main
```
