# nanoclaw Hermes runner image

This image extends the official Hermes Agent Docker image with the nanoclaw runner adapter.

Build:

```bash
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
```

Use it through:

```bash
uv run python main.py run-task \
  --task tasks/my_task.yaml \
  --runner-profile runner_profiles/hermes.yaml
```

The adapter entrypoint is `/opt/nanoclaw-adapter/run_task`. It reads the standard
nanoclaw Docker runner inputs from `/input`, runs Hermes inside `/workspace`, stores
Hermes state under `/state`, and writes `final_answer.md`, `trace.jsonl`,
`hermes_stdout.log`, `hermes_stderr.log`, and `runner_metadata.json` under `/output`.

By default the adapter runs:

```text
hermes -z <task prompt>
```

If `NANOCLAW_HERMES_TOOLSETS`, `NANOCLAW_HERMES_SKILLS`, or
`NANOCLAW_HERMES_MAX_TURNS` is set, it switches to:

```text
hermes chat --quiet -q <task prompt>
```
