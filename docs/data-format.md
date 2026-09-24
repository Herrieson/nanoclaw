# Data format

Each task is a YAML document under `<subset>/tasks/`.

- `id` and `name` identify the task.
- `prompts` or `prompt` points to one or more Markdown prompts.
- `environment.asset` selects the task workspace builder.
- `skills.available` lists task-local skill packages when skill augmentation is
  enabled.
- `sessions` describes multi-turn prompt order when present.
- `runtime` controls model, approval mode, temperature, and step budget.

The sibling task directory contains `env_builder.py` and source assets. Builders
are executed by NanoClaw before a run; prebuilt runtime assets are not required.
Verifier JSONL files and evaluation manifests provide deterministic task
selection and grading metadata. Use the checksums at the subset root to detect
accidental edits or incomplete copies.

