---
license: mit
language:
- zh
- en
task_categories:
- text-generation
- question-answering
pretty_name: ClawBenchPro
tags:
- agent-benchmark
- workplace
- tool-use
- multi-turn
- skills
- nanoclaw
size_categories:
- 1K<n<10K
configs:
- config_name: default
  default: true
  data_files:
  - split: test
    path: dataset_index.csv
- config_name: round_01_aligned_mix_800
  data_files:
  - split: test
    path: round_01_aligned_mix_800/dataset_index.csv
- config_name: persona_aligned_mix_200
  data_files:
  - split: test
    path: persona_aligned_mix_200/dataset_index.csv
---

# ClawBenchPro

ClawBenchPro is a compact, builder-based workplace-agent benchmark package exported from Nanoclaw.
It contains task YAML files, prompts, task-local environment builders, skills, evaluation manifests,
provenance metadata, and checksums.

## Included Splits

| Dataset | Tasks | Groups |
|---|---:|---|
| `round_01_aligned_mix_800` | 800 | `base`, `hard_aligned`, `multi_turn_aligned`, `skills_aligned` |
| `persona_aligned_mix_200` | 200 | `base`, `hard`, `multi_turn`, `skills` |

## Directory Layout

```text
ClawBenchPro/
├── README.md
├── LICENSE
├── dataset_index.jsonl
├── manifest.json
├── checksums.sha256
├── round_01_aligned_mix_800/
└── persona_aligned_mix_200/
```

Each dataset directory contains:

- `tasks/`: task YAML files, prompts, and task-local `env_builder.py` builders.
- `skills/`: packaged skills referenced by task YAML files.
- `eval_manifests/`: group-level manifests and task id lists.
- `provenance/`: sanitized construction metadata.
- `manifest.json`: dataset-level metadata.
- `checksums.sha256`: dataset-level file checksums.

Prebuilt `assets/` directories are intentionally not included to keep the Hugging Face repository
compact. Each task includes an `env_builder.py` that can materialize `assets/<task_id>/` on demand.

## Usage

After downloading the dataset, point Nanoclaw or compatible runners at the YAML tasks under:

```text
round_01_aligned_mix_800/tasks/*.yaml
persona_aligned_mix_200/tasks/*.yaml
```

Group manifests are available under `eval_manifests/` for category-level analysis.

To materialize one task environment manually:

```bash
cd round_01_aligned_mix_800
python tasks/data_round_01_aligned_mix_800_0001/env_builder.py
```

This creates:

```text
round_01_aligned_mix_800/assets/data_round_01_aligned_mix_800_0001/
```

Nanoclaw's batch runner can also invoke these builders automatically before each task run.

To materialize assets in batches from the repository root:

```bash
python materialize_assets.py --dataset round_01_aligned_mix_800 --workers 8
python materialize_assets.py --dataset persona_aligned_mix_200 --workers 8
```

## Dataset Index

`dataset_index.jsonl` provides one row per task with:

```text
dataset, task_id, category, task_file, asset_dir, prompt_files, skill_count
```

The full task definitions remain in the YAML files.

## Responsible AI (RAI) Considerations

This section summarizes the Responsible AI information also encoded in the Croissant metadata under
`croissant/openreview_croissant.json`.

### Synthetic Data Generation

ClawBenchPro is designed as a synthetic workplace-agent benchmark. Tasks were generated, staged,
imported into Nanoclaw task YAML format, validated with task-local `env_builder.py` builders, grouped
into aligned benchmark subsets, and exported in compact builder-only form for hosting. The benchmark
includes fictional workplace scenarios, synthetic personas, synthetic internal services, synthetic
records, task-local skills, and generated workspace fixtures. The package is not intended to contain
real user records or operational credentials.

### Sandbox Fixtures and Real-World Safety

Some tasks intentionally contain strings that look like API keys, internal URLs, secrets, policy-sensitive
phrases, corrupted files, or broken logs. These are sandbox benchmark fixtures used to test whether agents
can reason about noisy workplace environments. They are not real credentials, do not connect to production
systems, and are meant to be executed in local or containerized workspaces. Prebuilt `assets/` are not
published; environments are materialized locally from `env_builder.py` when needed.

### Environment Validation Limitations

Environment builders were checked for the ability to materialize task workspaces, but this does not prove
that every possible runner, model, operating system, dependency version, or execution policy will behave
identically. The benchmark measures performance in controlled Nanoclaw-compatible environments and should
not be interpreted as a complete certification of real-world workplace automation reliability.

### Biases and Scope Limitations

The dataset is selected to stress agentic workflows such as state tracking, tool use, multi-turn reasoning,
file manipulation, and skill invocation. This creates selection bias toward tasks that can be packaged as
local workspaces. The benchmark may underrepresent low-resource languages, non-technical occupations,
accessibility-specific workflows, embodied tasks, and domains requiring direct human interaction.

### Intended and Non-Recommended Uses

Intended uses include comparative evaluation of language-agent runners, category-level benchmark analysis,
reproducibility studies, and diagnosis of tool-use or multi-turn failure modes. The dataset is not validated
for model fine-tuning, safety certification, demographic fairness auditing, hiring decisions, medical,
legal, financial, or other safety-critical deployment decisions.

### Social Impact

ClawBenchPro may help make agent evaluation more reproducible and transparent by providing local synthetic
workspaces, explicit task categories, and machine-readable metadata. Potential risks include overgeneralizing
benchmark scores, optimizing narrowly to synthetic tasks, or presenting benchmark performance as evidence of
real-world reliability. We mitigate these risks by documenting limitations, keeping tasks sandboxed, and
publishing Croissant metadata with RAI fields.

## License

This package is released under the MIT License. See `LICENSE`.

## Notes

- The package is intended as a benchmark artifact rather than a tabular training dataset.
- Some tasks intentionally contain synthetic keys, internal URLs, noisy logs, broken files, or
  policy-sensitive strings as part of the benchmark environment. These are benchmark fixtures,
  not operational credentials.
- Build-time local absolute paths have been removed from the Hugging Face-ready package.
