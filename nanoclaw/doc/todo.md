# Nanoclaw Retrofit TODO

## Purpose

`nanoclaw` should primarily reference `openclaw-prompts-and-skills/OPENCLAW_SYSTEM_PROMPT_STUDY.md`, but only as a guide to OpenClaw's runtime contract.

The goal is not to reproduce OpenClaw as a product.

The goal is to make `nanoclaw` a better **experimental** agent core for:

- prompt assembly experiments
- tool protocol experiments
- skill loading experiments
- memory and recall experiments
- session/runtime semantics experiments

## Project Boundary

Keep:

- CLI-first workflows
- file-backed state
- small local modules
- reproducible task runs
- explicit policies

Do not add:

- messaging platform integrations
- gateway/daemon infrastructure
- browser/canvas/device control
- product-facing automation layers
- full sub-agent orchestration fabric

## Main Principle

When reading `OPENCLAW_SYSTEM_PROMPT_STUDY.md`, split features into three groups.

Implement directly:

- dynamic system prompt assembly
- explicit runtime tool list
- workspace context injection
- selective skill loading
- memory recall policy
- gated command execution
- run/session persistence
- heartbeat/silent-reply semantics

Simulate minimally:

- heartbeat mode
- session continuity
- system event mode
- runtime metadata injection

Do not implement:

- `message`
- `gateway`
- `browser`
- `canvas`
- `nodes`
- full `cron`
- full `sessions_*` orchestration

## Tooling Direction

The OpenClaw study makes an important distinction:

- the actual tool surface comes from the runtime system prompt
- `TOOLS.md` is only workspace guidance
- skills teach tool usage, but are not tools themselves

`nanoclaw` should follow that same separation.

### Target Tool Subset

Adopt OpenClaw-style names and semantics where it helps prompt compatibility.

Implement in `nanoclaw`:

- `read`
- `write`
- `edit`
- `apply_patch`
- `grep`
- `find`
- `ls`
- `exec`

Consider later, only if experiments need them:

- `process`
- `web_search`
- `web_fetch`
- `image`

Explicitly out of scope:

- `browser`
- `canvas`
- `nodes`
- `cron`
- `message`
- `gateway`
- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`
- `session_status`

### Tool Compatibility Notes

- Rename `read_file` toward `read`.
- Rename `write_file` toward `write`.
- Replace "dangerous command" naming with `exec` plus policy gating.
- Add real `edit` and `apply_patch` semantics instead of relying on full-file overwrite.
- Prefer built-in `grep` / `find` / `ls` tools over shelling out.

## Phase 0: Freeze Scope

### [ ] 1. Document the supported OpenClaw-inspired subset

- Add a short section to `README.md`:
  - what `nanoclaw` borrows from OpenClaw
  - what it intentionally does not implement
- State clearly that `nanoclaw` is an experiment core, not a messaging runtime.

### [ ] 2. Document tool taxonomy

- Clarify in `README.md`:
  - runtime tools
  - workspace context files such as `TOOLS.md`
  - skills and `SKILL.md`
- State explicitly that `TOOLS.md` does not grant capabilities.

## Phase 1: Prompt Assembly

### [ ] 3. Add optional workspace context injection

Inject existing workspace files if present:

- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `AGENTS.md`
- `TOOLS.md`

Rules:

- load only files that exist
- keep injection order stable
- record injected files in run outputs

Touchpoints:

- `nanoclaw/config.py`
- `nanoclaw/core_loop.py`
- `nanoclaw/run_store.py`

### [ ] 4. Add runtime metadata injection

Inject a compact runtime block:

- current date/time
- timezone
- workspace path
- model name
- run mode

Do not inject product/channel routing details.

Touchpoints:

- `nanoclaw/config.py`
- `nanoclaw/core_loop.py`

## Phase 2: Tool Protocol

### [ ] 5. Align tool names with the OpenClaw-style subset

Move toward:

- `read`
- `write`
- `edit`
- `apply_patch`
- `grep`
- `find`
- `ls`
- `exec`

Keep compatibility shims only if migration cost is low.

Touchpoints:

- `nanoclaw/core_loop.py`

### [ ] 6. Add built-in workspace inspection tools

Implement native tools for:

- reading file contents
- directory listing
- glob/file discovery
- text search

Goal:

- reduce reliance on shell commands for routine exploration
- make experiments cleaner and safer

Touchpoints:

- `nanoclaw/core_loop.py`

### [ ] 7. Add precise editing tools

Implement:

- `edit`
- `apply_patch`

Rules:

- workspace-only writes
- deterministic behavior
- clear error messages

Touchpoints:

- `nanoclaw/core_loop.py`
- new `nanoclaw/file_edit.py`

### [ ] 8. Refactor command approval into an `exec` policy layer

Replace the current naming split with:

- `exec` as the tool
- a separate policy layer for readonly allowlists and human approval

Keep:

- one-time approval by exact normalized command

Touchpoints:

- `nanoclaw/core_loop.py`
- new `nanoclaw/command_policy.py`
- `nanoclaw/run_store.py`

## Phase 3: Memory And Skills

### [ ] 9. Add a first-class memory layout

Standardize:

- `memory/YYYY-MM-DD.md` for short-term notes
- `MEMORY.md` for curated long-term memory

Extend bootstrap and example assets accordingly.

Touchpoints:

- `nanoclaw/core_loop.py`
- `README.md`
- `assets/`

### [ ] 10. Add dedicated memory tools

Implement minimal file-backed memory tools:

- `memory_search`
- `memory_get`
- `memory_append`

Do not add embeddings or vector storage.

Touchpoints:

- `nanoclaw/core_loop.py`
- new `nanoclaw/memory.py`

### [ ] 11. Add explicit memory recall policy to the system prompt

Require memory lookup before answering about:

- previous work
- decisions
- dates
- preferences
- todos
- people/context from prior sessions

If memory is inconclusive, the answer should say so.

Touchpoints:

- `nanoclaw/core_loop.py`

### [ ] 12. Make skill loading more selective

For auto-skill loading:

- scan metadata first
- choose the single best match
- load one skill body by default

Keep explicit multi-skill activation available via CLI or task config.

Touchpoints:

- `nanoclaw/skills.py`
- `nanoclaw/cli.py`

### [ ] 13. Support richer optional skill metadata

Add support for optional fields such as:

- `aliases`
- `requires`
- `homepage`

Ignore unknown metadata.

Touchpoints:

- `nanoclaw/skills.py`

## Phase 4: Runtime Semantics

### [ ] 14. Introduce run modes

Add a small run mode enum:

- `interactive`
- `heartbeat`
- `system_event`

Use mode to control prompt assembly and runtime semantics.

Touchpoints:

- `nanoclaw/config.py`
- `nanoclaw/core_loop.py`
- `nanoclaw/cli.py`
- `nanoclaw/task_loader.py`

### [ ] 15. Add special final-response handling

Classify final outputs as:

- normal final answer
- heartbeat acknowledgement
- silent reply
- failure

Persist the classification in run summaries.

Touchpoints:

- `nanoclaw/core_loop.py`
- `nanoclaw/run_store.py`

### [ ] 16. Add lightweight session persistence

For ad hoc CLI runs, add optional local sessions:

- `--session <id>`
- local JSONL history
- deterministic trimming rules

Keep `run-task` isolated by default.

Touchpoints:

- `nanoclaw/cli.py`
- `nanoclaw/core_loop.py`
- new `nanoclaw/session_store.py`
- `nanoclaw/config.py`

### [ ] 17. Extend task YAML only where experiment fidelity needs it

Optional runtime fields:

- `runtime.mode`
- `runtime.session`
- `runtime.memory_policy`
- `runtime.workspace_context_files`

Keep schema flat and optional.

Touchpoints:

- `nanoclaw/task_loader.py`
- `nanoclaw/cli.py`

## Phase 5: Validation

### [ ] 18. Add tests for the retrofit behaviors

Cover:

- prompt context injection
- tool naming/protocol behavior
- memory search/get/append
- single-skill auto-selection
- heartbeat suppression
- session persistence and trimming
- command policy behavior

Suggested modules:

- `tests/test_core_loop.py`
- `tests/test_memory.py`
- `tests/test_skills.py`
- `tests/test_session_store.py`

### [ ] 19. Add example tasks/assets for the new semantics

Add at least:

- one memory-recall task
- one heartbeat/no-op task

Touchpoints:

- `tasks/`
- `assets/`
- `README.md`

## Recommended Order

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5

## Reject Or Defer If

A change requires:

- a long-running daemon
- channel routing or provider adapters
- infrastructure outside the local workspace
- large browser/device integration surfaces
- a second orchestration layer unrelated to experiments
- significant complexity with little gain in prompt/tool/memory research value
