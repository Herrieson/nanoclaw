# ClawBenchPro Open Evaluation Kit

ClawBenchPro Open Evaluation Kit bundles the NanoClaw benchmark runner with the
reproducible ClawBenchPro workplace benchmark. It is intended for researchers
who want to inspect tasks, run a small smoke test, or compare agent harnesses
under the same workspace-based grading protocol.

The repository contains:

- `src/nanoclaw/`: the NanoClaw runner, evaluator, Docker adapters, scripts,
  and unit tests.
- `data/ClawBenchPro/`: the 1,000-task benchmark package downloaded from the
  Hugging Face release, including task YAML, prompts, generated workspace
  builders, skills, verifiers, manifests, and checksums.
- `examples/`: small, copy-pasteable commands for inspection and evaluation.
- `docs/`: data format and framework adapter notes.

## Quick start

Requirements: Python 3.12+, `uv`, and (only for external harnesses) Docker.

```bash
cd src/nanoclaw
uv run python -m pip install -e .
uv run python -m unittest discover -s tests -p 'test_*.py'
```

Run the built-in runner on one task without an API call:

```bash
cd ../..
python examples/smoke_test.py --list-only
```

To run an actual task, configure an OpenAI-compatible endpoint first:

```bash
export OPENAI_API_KEY="..."
export NANOCLAW_MODEL="gpt-4o-mini"
python examples/smoke_test.py --run
```

The smoke command uses `round_01_aligned_mix_800` by default and writes outputs
to `results/`, which is ignored by Git. Use `--dataset persona_aligned_mix_200`
to select the 200-task persona subset.

## Run and compare frameworks

NanoClaw is built in. OpenClaw, Hermes-Agent, and Codex are exposed through
Docker runner profiles. Build only the images you intend to use:

```bash
cd src/nanoclaw
docker build -t nanoclaw-runner-openclaw:latest docker/openclaw-runner
docker build -t nanoclaw-runner-hermes:latest docker/hermes-runner
docker build -t nanoclaw-runner-codex:latest docker/codex-runner
```

Run and evaluate a subset (the script discovers task manifests automatically):

```bash
uv run python scripts/run_clawbenchpro_subset.py \
  ../../data/ClawBenchPro \
  --datasets persona_aligned_mix_200 \
  --runners nanoclaw openclaw hermes codex \
  --models gpt-4o-mini \
  --workers 2 --eval-workers 4
```

For a first run, use `--datasets persona_aligned_mix_200` and one runner. The
800-task release can require substantial API budget and disk space.

## Data layout and integrity

Each dataset directory contains task YAML files, prompt files, task-local
workspace builders, optional skills, deterministic verifiers, evaluation
manifests, provenance records, and `checksums.sha256`. Verify the checked-in
payload from the repository root:

```bash
python examples/verify_data.py
```

The benchmark uses synthetic or transformed workplace scenarios. It is an
evaluation resource, not a source of production credentials or live services.
Task builders may create files that resemble operational data; run agents in an
isolated environment and review any external integrations before enabling them.

## Research context

The accompanying paper materials describe a workspace-grounded benchmark with
four task groups (base, multi-turn, hard/environment, and skills), broad
professional-domain coverage, and comparisons across NanoClaw, OpenClaw,
Hermes-Agent, and Codex. The PDFs and TeX sources used to prepare those
materials are kept outside this release directory; see `docs/research-notes.md`
for the claims and artifact mapping.

## License and attribution

The runner and benchmark package are released under the MIT License. See
`src/nanoclaw/LICENSE` and `data/ClawBenchPro/LICENSE`. Cite the ClawBenchPro
paper and the upstream NanoClaw project when using this repository in research.

