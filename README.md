# nanoclaw (minimal OpenClaw-like core)

A minimal, research-oriented agent loop that keeps only core behavior:

- dynamic file-backed context assembly
- tool-calling loop (read/write, dangerous command gate, ask-human)
- strict official prompt file sync + checksum manifest verification
- versioned prompt snapshots for reproducible experiments

This project intentionally excludes non-core engineering concerns like cross-platform packaging, chat platform integrations, rich UI rendering, and retry frameworks.

## Layout

- `nanoclaw/core_loop.py`: minimal ReAct-like loop
- `nanoclaw/prompt_sync.py`: sync official prompt files from `openclaw/openclaw`, write `manifest.json`, and manage prompt versions
- `nanoclaw/cli.py`: commands for bootstrap/sync/verify/run
- `workspace/`: runtime files and synced prompt files

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

```bash
uv run python main.py sync-prompts \
  --repo-url https://github.com/openclaw/openclaw.git \
  --ref main \
  --files CLAUDE.md,AGENTS.md
```

Default behavior is cache-first: if local prompt files already match `manifest.json`, it does not pull remote again.

Use `--refresh` when you want to pull remote again:

```bash
uv run python main.py sync-prompts --refresh
```

When remote prompt content changes, nanoclaw stores a new snapshot under `workspace/prompts/official/versions/<timestamp_commit>/` and keeps previous snapshots. If commit changes but prompt files are byte-identical, it reuses the existing snapshot.

The active snapshot is copied to:

- `workspace/prompts/official/CLAUDE.md`
- `workspace/prompts/official/AGENTS.md`
- `workspace/prompts/official/manifest.json`

The manifest includes source repo/ref/commit, sha256 checksums, byte counts, generation timestamp, and snapshot version id.

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

## Environment variables

- `OPENAI_API_KEY`: required when `NANOCLAW_BASE_URL` is not set
- `NANOCLAW_BASE_URL`: optional custom OpenAI-compatible endpoint
- `NANOCLAW_MODEL`: default `gpt-4o`
- `NANOCLAW_WORKSPACE_DIR`: default `workspace`
- `NANOCLAW_PROMPT_DIR`: default `workspace/prompts/official`
- `NANOCLAW_PROMPT_FILES`: default `CLAUDE.md,AGENTS.md`
- `NANOCLAW_MAX_STEPS`: default `15`
- `NANOCLAW_TEMPERATURE`: default `0.2`

## Standalone sync script

```bash
uv run python scripts/sync_openclaw_prompts.py --list-versions
uv run python scripts/sync_openclaw_prompts.py --switch-version <version-id>
uv run python scripts/sync_openclaw_prompts.py --refresh --ref main --files CLAUDE.md,AGENTS.md
```
