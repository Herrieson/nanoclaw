# Persona Aligned Mix 200

200-task workplace suite spanning base, multi_turn, hard, and skills groups.

## Layout

- `tasks/`: task YAML files and task-local directories.
- `tasks/prompts/`: prompt files referenced by the YAML bundles.
- `assets/`: frozen initial workspaces generated from the task builders.
- `skills/`: global task-local skills referenced by the task YAML files.
- `eval_manifests/`: group-wise manifests and task id lists.
- `provenance/`: original staging manifests copied for traceability.
- `manifest.json`: machine-readable package summary.
- `checksums.sha256`: file inventory for integrity checks.

## Counts

- Tasks: 200
- base: 50
- multi_turn: 50
- hard: 50
- skills: 50

This directory is self-contained and does not depend on `.staging`.
