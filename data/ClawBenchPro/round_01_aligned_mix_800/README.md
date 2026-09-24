# Round 01 Aligned Mix 800

800-task workplace suite spanning base, hard_aligned, multi_turn_aligned, and skills_aligned groups.

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

- Tasks: 800
- multi_turn_aligned: 200
- skills_aligned: 200
- hard_aligned: 200
- base: 200

This directory is self-contained and does not depend on `.staging`.
