# nanoclaw OpenClaw runner image

This image extends the official OpenClaw image with the nanoclaw runner adapter.

Build:

```bash
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
```

Use it through:

```bash
uv run python main.py run-task \
  --task tasks/my_task.yaml \
  --runner-profile runner_profiles/openclaw.yaml
```

The adapter entrypoint is `/opt/nanoclaw-adapter/run_task`. It reads:

- `/input/task.md`
- `/input/resolved_task.json`
- `/input/prior_messages.json`
- `/input/runner_request.json`

It writes:

- `/output/final_answer.md`
- `/output/trace.jsonl`
- `/output/openclaw_stdout.log`
- `/output/openclaw_stderr.log`
- `/output/runner_metadata.json`

By default it stores OpenClaw home/config/cache under `/state`, which lets
nanoclaw reuse state across turns while still removing each container after it
exits.
