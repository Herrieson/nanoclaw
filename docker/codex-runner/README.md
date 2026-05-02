# nanoclaw Codex runner image

This image installs the OpenAI Codex CLI and adds the nanoclaw Docker runner
adapter.

Build:

```bash
docker build -t nanoclaw-runner-codex:latest docker/codex-runner
```

Use it through:

```bash
uv run python main.py run-task \
  --task tasks/my_task.yaml \
  --runner-profile runner_profiles/codex.yaml
```

The adapter entrypoint is `/opt/nanoclaw-adapter/run_task`. It reads:

- `/input/task.md`
- `/input/resolved_task.json`
- `/input/prior_messages.json`
- `/input/runner_request.json`

It writes:

- `/output/final_answer.md`
- `/output/trace.jsonl`
- `/output/codex_stdout.jsonl`
- `/output/codex_stderr.log`
- `/output/runner_metadata.json`

By default the adapter runs Codex in non-interactive mode:

```text
codex exec --json --skip-git-repo-check --sandbox workspace-write \
  --output-last-message /output/final_answer.md -C /workspace -
```

The task prompt is passed on stdin. `HOME`, `CODEX_HOME`, and XDG state/cache
locations are isolated under `/state`.

Useful environment variables:

- `NANOCLAW_MODEL` or `NANOCLAW_CODEX_MODEL`: model override.
- `NANOCLAW_BASE_URL` or `NANOCLAW_CODEX_BASE_URL`: custom OpenAI-compatible API base URL.
- `NANOCLAW_CODEX_MODEL_PROVIDER`: provider id for the generated Codex config.
- `NANOCLAW_CODEX_WIRE_API`: optional provider `wire_api` value. Defaults to `chat` for custom base URLs.
- `NANOCLAW_CODEX_SANDBOX`: sandbox mode. Defaults to `workspace-write`.
- `NANOCLAW_CODEX_APPROVAL_POLICY`: approval policy. Defaults to `never`.
- `NANOCLAW_CODEX_NETWORK_ACCESS`: set `0` to disable network access for workspace-write sandboxed commands.
