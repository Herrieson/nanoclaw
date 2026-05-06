from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "published_datasets" / "nanoclaw_workplace_suite"
DEFAULT_OUTPUT = REPO_ROOT / "ClawBenchPro"

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".task_ids",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {
    ".cache",
    "__pycache__",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
}

DATASETS = (
    {
        "name": "round_01_aligned_mix_800",
        "title": "Round 01 Aligned Mix 800",
        "task_count": 800,
        "groups": (
            ("base", 200),
            ("hard_aligned", 200),
            ("multi_turn_aligned", 200),
            ("skills_aligned", 200),
        ),
    },
    {
        "name": "persona_aligned_mix_200",
        "title": "Persona Aligned Mix 200",
        "task_count": 200,
        "groups": (
            ("base", 50),
            ("hard", 50),
            ("multi_turn", 50),
            ("skills", 50),
        ),
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Hugging Face-ready ClawBenchPro dataset directory."
    )
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE),
        help="Source standalone dataset package.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output Hugging Face dataset directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace output directory if it already exists.",
    )
    parser.add_argument(
        "--include-assets",
        action="store_true",
        help="Include prebuilt assets/. By default ClawBenchPro is published in compact builder-only form.",
    )
    parser.add_argument(
        "--dataset-url",
        default="https://huggingface.co/datasets/ErenJaegerYeager/ClawBenchPro",
        help="Canonical hosted dataset URL used in Croissant metadata.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    if not source.is_dir():
        raise SystemExit(f"Source dataset package does not exist: {source}")
    if output.exists():
        if not args.force:
            raise SystemExit(f"Output already exists, pass --force to replace it: {output}")
        shutil.rmtree(output)

    output.mkdir(parents=True)
    copy_package(source, output, include_assets=args.include_assets)
    sanitize_text_files(output)
    write_dataset_card(output)
    write_license(output)
    write_gitattributes(output)
    write_gitignore(output)
    write_hfignore(output)
    write_materialize_script(output)
    write_dataset_index(output)
    write_croissant_files(output, dataset_url=args.dataset_url.rstrip("/"))
    write_package_manifest(output)
    write_checksums(output)
    print(f"Wrote Hugging Face-ready dataset package to {output}")
    return 0


def copy_package(source: Path, output: Path, *, include_assets: bool) -> None:
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        if should_skip(rel, include_assets=include_assets):
            continue
        dest = output / rel
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)


def should_skip(rel: Path, *, include_assets: bool) -> bool:
    if any(part in SKIP_DIRS for part in rel.parts):
        return True
    if not include_assets and "assets" in rel.parts:
        return True
    if rel.suffix in SKIP_SUFFIXES:
        return True
    return False


def sanitize_text_files(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        sanitized = sanitize_text(text)
        if sanitized != text:
            path.write_text(sanitized, encoding="utf-8")


def sanitize_text(text: str) -> str:
    replacements = {
        "/home/hyx/workplace/nanoclaw/": "",
        "/home/hyx/workplace/nanoclaw": ".",
        "home/hyx/workplace/nanoclaw/": "",
        "home/hyx/workplace/nanoclaw": ".",
        "DESKTOP-2O26RJD": "<local-machine>",
    }
    for needle, replacement in replacements.items():
        text = text.replace(needle, replacement)
    return text


def write_dataset_card(root: Path) -> None:
    readme = """---
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
"""
    root.joinpath("README.md").write_text(readme, encoding="utf-8")


def write_license(root: Path) -> None:
    source_license = REPO_ROOT / "LICENSE"
    if source_license.exists():
        shutil.copy2(source_license, root / "LICENSE")
        return
    root.joinpath("LICENSE").write_text(
        "MIT License\n\nCopyright (c) 2026 Herrieson\n",
        encoding="utf-8",
    )


def write_gitattributes(root: Path) -> None:
    root.joinpath(".gitattributes").write_text(
        "\n".join(
            [
                "*.7z filter=lfs diff=lfs merge=lfs -text",
                "*.bin filter=lfs diff=lfs merge=lfs -text",
                "*.csv filter=lfs diff=lfs merge=lfs -text",
                "*.gz filter=lfs diff=lfs merge=lfs -text",
                "*.jsonl filter=lfs diff=lfs merge=lfs -text",
                "*.npy filter=lfs diff=lfs merge=lfs -text",
                "*.npz filter=lfs diff=lfs merge=lfs -text",
                "*.parquet filter=lfs diff=lfs merge=lfs -text",
                "*.pdf filter=lfs diff=lfs merge=lfs -text",
                "*.pkl filter=lfs diff=lfs merge=lfs -text",
                "*.png filter=lfs diff=lfs merge=lfs -text",
                "*.tar filter=lfs diff=lfs merge=lfs -text",
                "*.tgz filter=lfs diff=lfs merge=lfs -text",
                "*.zip filter=lfs diff=lfs merge=lfs -text",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_gitignore(root: Path) -> None:
    root.joinpath(".gitignore").write_text(
        "\n".join(
            [
                ".cache/",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                "round_01_aligned_mix_800/assets/",
                "persona_aligned_mix_200/assets/",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_hfignore(root: Path) -> None:
    root.joinpath(".hfignore").write_text(
        "\n".join(
            [
                ".cache/",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                "round_01_aligned_mix_800/assets/",
                "persona_aligned_mix_200/assets/",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_materialize_script(root: Path) -> None:
    root.joinpath("materialize_assets.py").write_text(
        '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys


DATASETS = ("round_01_aligned_mix_800", "persona_aligned_mix_200")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize ClawBenchPro task assets from env_builder.py files.")
    parser.add_argument("--dataset", choices=DATASETS, help="Only materialize one dataset.")
    parser.add_argument("--task-id", action="append", default=[], help="Only materialize a specific task id. May be repeated.")
    parser.add_argument("--task-ids-file", help="Text file containing one task id per line.")
    parser.add_argument("--workers", type=int, default=1, help="Number of builder processes to run concurrently.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    selected_datasets = (args.dataset,) if args.dataset else DATASETS
    task_ids = set(args.task_id)
    if args.task_ids_file:
        task_ids.update(
            line.strip()
            for line in Path(args.task_ids_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    builders: list[Path] = []
    for dataset in selected_datasets:
        tasks_root = root / dataset / "tasks"
        for builder in sorted(tasks_root.glob("*/env_builder.py")):
            if task_ids and builder.parent.name not in task_ids:
                continue
            builders.append(builder)

    if not builders:
        print("No env_builder.py files matched.", file=sys.stderr)
        return 1

    failures: list[tuple[Path, int]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(run_builder, builder): builder for builder in builders}
        completed = 0
        for future in as_completed(futures):
            builder = futures[future]
            completed += 1
            returncode = future.result()
            if returncode:
                failures.append((builder, returncode))
                print(f"[FAIL] {completed}/{len(builders)} {builder} exited {returncode}", file=sys.stderr)
            else:
                print(f"[OK] {completed}/{len(builders)} {builder.parent.name}")

    if failures:
        print(f"{len(failures)} builder(s) failed.", file=sys.stderr)
        return 1
    print(f"Materialized assets for {len(builders)} task(s).")
    return 0


def run_builder(builder: Path) -> int:
    proc = subprocess.run([sys.executable, str(builder)], cwd=str(builder.parents[2]))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
''',
        encoding="utf-8",
    )


def write_dataset_index(root: Path) -> None:
    rows_by_dataset: dict[str, list[dict[str, Any]]] = {}
    for dataset in DATASETS:
        dataset_name = dataset["name"]
        dataset_root = root / dataset_name
        if not dataset_root.is_dir():
            continue
        dataset_rows: list[dict[str, Any]] = []
        task_dir = dataset_root / "tasks"
        for task_file in sorted(task_dir.glob("*.yaml")):
            task_id = task_file.stem
            task_text = task_file.read_text(encoding="utf-8")
            category = infer_category(dataset_name, task_id)
            prompt_files = [
                f"{dataset_name}/tasks/{prompt_path}"
                for prompt_path in infer_prompt_files(task_text)
            ]
            asset_dir = f"{dataset_name}/{infer_asset_dir(task_text, task_id)}"
            skill_count = count_task_skills(task_text)
            dataset_rows.append(
                {
                    "dataset": dataset_name,
                    "task_id": task_id,
                    "category": category,
                    "task_file": str(task_file.relative_to(root)),
                    "asset_dir": asset_dir,
                    "prompt_files": prompt_files,
                    "skill_count": skill_count,
                }
            )
        rows_by_dataset[dataset_name] = dataset_rows

    rows = [row for dataset in DATASETS for row in rows_by_dataset.get(dataset["name"], [])]

    with root.joinpath("dataset_index.jsonl").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    with root.joinpath("dataset_index.csv").open("w", encoding="utf-8", newline="") as fh:
        fieldnames = [
            "dataset",
            "task_id",
            "category",
            "task_file",
            "asset_dir",
            "prompt_files",
            "skill_count",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["prompt_files"] = "|".join(row["prompt_files"])
            writer.writerow(csv_row)

    for dataset_name, dataset_rows in rows_by_dataset.items():
        dataset_root = root / dataset_name
        with dataset_root.joinpath("dataset_index.jsonl").open("w", encoding="utf-8") as fh:
            for row in dataset_rows:
                fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        with dataset_root.joinpath("dataset_index.csv").open(
            "w",
            encoding="utf-8",
            newline="",
        ) as fh:
            fieldnames = [
                "dataset",
                "task_id",
                "category",
                "task_file",
                "asset_dir",
                "prompt_files",
                "skill_count",
            ]
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset_rows:
                csv_row = dict(row)
                csv_row["prompt_files"] = "|".join(row["prompt_files"])
                writer.writerow(csv_row)


def infer_category(dataset_name: str, task_id: str) -> str:
    if dataset_name == "persona_aligned_mix_200":
        match = re.match(r"data_persona_aligned_(base|hard|multi_turn|skills)_50_", task_id)
        return match.group(1) if match else "unknown"
    if dataset_name == "round_01_aligned_mix_800":
        match = re.search(r"_(\d{4})$", task_id)
        if not match:
            return "unknown"
        idx = int(match.group(1))
        if 1 <= idx <= 200:
            return "base"
        if 201 <= idx <= 400:
            return "skills_aligned"
        if 401 <= idx <= 600:
            return "hard_aligned"
        if 601 <= idx <= 800:
            return "multi_turn_aligned"
    return "unknown"


def infer_prompt_files(task_text: str) -> list[str]:
    prompts: list[str] = []
    in_prompts = False
    for line in task_text.splitlines():
        stripped = line.strip()
        if stripped == "prompts:":
            in_prompts = True
            continue
        if in_prompts:
            if stripped.startswith("- "):
                prompts.append(stripped[2:].strip())
                continue
            if stripped and not line.startswith(" "):
                break
    return prompts


def infer_asset_dir(task_text: str, task_id: str) -> str:
    match = re.search(r"^\s*asset:\s*(\S+)\s*$", task_text, flags=re.MULTILINE)
    asset = match.group(1) if match else task_id
    return f"assets/{asset}"


def count_task_skills(task_text: str) -> int:
    match = re.search(r"^\s*available:\s*$", task_text, flags=re.MULTILINE)
    if not match:
        return 0
    count = 0
    started = False
    for line in task_text[match.end() :].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            count += 1
            started = True
            continue
        if started and not line.startswith(" "):
            break
        if stripped.startswith("runtime:"):
            break
    return count


def write_package_manifest(root: Path) -> None:
    dataset_summaries = []
    for dataset in DATASETS:
        dataset_root = root / dataset["name"]
        if not dataset_root.exists():
            continue
        files, bytes_total = count_files(dataset_root)
        summary = {
            "name": dataset["name"],
            "title": dataset["title"],
            "root": dataset["name"],
            "task_count": dataset["task_count"],
            "group_counts": {group: count for group, count in dataset["groups"]},
            "files": files,
            "bytes": bytes_total,
            "checksums": f"{dataset['name']}/checksums.sha256",
        }
        dataset_summaries.append(summary)

    manifest = {
        "package_name": "ClawBenchPro",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_package": "published_datasets/nanoclaw_workplace_suite",
        "format": "huggingface_dataset_repository",
        "license": "MIT",
        "datasets": dataset_summaries,
    }
    root.joinpath("manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_croissant_files(root: Path, *, dataset_url: str) -> None:
    croissant_root = root / "croissant"
    croissant_root.mkdir(parents=True, exist_ok=True)
    collection = build_croissant_metadata(
        name="ClawBenchPro",
        description=(
            "A compact, builder-based workplace-agent benchmark collection containing "
            "round_01_aligned_mix_800 and persona_aligned_mix_200."
        ),
        url=dataset_url,
        dataset_root=".",
        index_path="dataset_index.csv",
        task_count=1000,
        groups={
            "round_01_aligned_mix_800": 800,
            "persona_aligned_mix_200": 200,
        },
        file_sets=[
            ("round_01_tasks", "round_01_aligned_mix_800/tasks/**/*", "text/*"),
            ("round_01_skills", "round_01_aligned_mix_800/skills/**/*", "text/*"),
            ("round_01_eval_manifests", "round_01_aligned_mix_800/eval_manifests/*", "text/*"),
            ("persona_tasks", "persona_aligned_mix_200/tasks/**/*", "text/*"),
            ("persona_skills", "persona_aligned_mix_200/skills/**/*", "text/*"),
            ("persona_eval_manifests", "persona_aligned_mix_200/eval_manifests/*", "text/*"),
        ],
    )
    write_json(croissant_root / "clawbenchpro_collection_croissant.json", collection)

    for dataset in DATASETS:
        dataset_name = dataset["name"]
        dataset_meta = build_croissant_metadata(
            name=dataset_name,
            description=f"{dataset['title']} from the ClawBenchPro benchmark collection.",
            url=f"{dataset_url}/tree/main/{dataset_name}",
            dataset_root=dataset_name,
            index_path=f"{dataset_name}/dataset_index.csv",
            task_count=int(dataset["task_count"]),
            groups={group: count for group, count in dataset["groups"]},
            file_sets=[
                (f"{dataset_name}_tasks", f"{dataset_name}/tasks/**/*", "text/*"),
                (f"{dataset_name}_skills", f"{dataset_name}/skills/**/*", "text/*"),
                (
                    f"{dataset_name}_eval_manifests",
                    f"{dataset_name}/eval_manifests/*",
                    "text/*",
                ),
                (f"{dataset_name}_provenance", f"{dataset_name}/provenance/*", "text/*"),
            ],
        )
        write_json(croissant_root / f"{dataset_name}_croissant.json", dataset_meta)


def build_croissant_metadata(
    *,
    name: str,
    description: str,
    url: str,
    dataset_root: str,
    index_path: str,
    task_count: int,
    groups: dict[str, int],
    file_sets: list[tuple[str, str, str]],
) -> dict[str, Any]:
    raw_base_url = "https://huggingface.co/datasets/ErenJaegerYeager/ClawBenchPro/resolve/main"
    if "/tree/" in url:
        canonical_base = url.split("/tree/", 1)[0]
    else:
        canonical_base = url
    raw_base_url = f"{canonical_base}/resolve/main"

    distribution: list[dict[str, Any]] = [
        {
            "@type": "cr:FileObject",
            "@id": "dataset_index_csv",
            "name": "dataset_index.csv",
            "contentUrl": f"{raw_base_url}/{index_path}",
            "encodingFormat": "text/csv",
            "sha256": sha256_file(root_path_for_croissant(index_path)),
        },
    ]
    for file_set_id, includes, encoding_format in file_sets:
        distribution.append(
            {
                "@type": "cr:FileSet",
                "@id": file_set_id,
                "name": file_set_id,
                "containedIn": {"@id": "huggingface_repository"},
                "includes": includes,
                "encodingFormat": encoding_format,
            }
        )

    metadata: dict[str, Any] = {
        "@context": {
            "@language": "en",
            "@vocab": "https://schema.org/",
            "sc": "https://schema.org/",
            "cr": "http://mlcommons.org/croissant/",
            "citeAs": "cr:citeAs",
            "rai": "http://mlcommons.org/croissant/RAI/",
            "prov": "http://www.w3.org/ns/prov#",
            "dct": "http://purl.org/dc/terms/",
            "conformsTo": "dct:conformsTo",
            "dataType": {
                "@id": "cr:dataType",
                "@type": "@vocab",
            },
            "distribution": "sc:distribution",
            "recordSet": "cr:recordSet",
            "field": "cr:field",
            "source": "cr:source",
            "extract": "cr:extract",
            "column": "cr:column",
            "fileObject": "cr:fileObject",
            "fileSet": "cr:fileSet",
            "includes": "cr:includes",
            "containedIn": "cr:containedIn",
            "dataLimitations": "rai:dataLimitations",
            "dataBiases": "rai:dataBiases",
            "personalSensitiveInformation": "rai:personalSensitiveInformation",
            "dataUseCases": "rai:dataUseCases",
            "dataSocialImpact": "rai:dataSocialImpact",
            "equivalentProperty": "cr:equivalentProperty",
            "examples": {
                "@id": "cr:examples",
                "@type": "@json",
            },
            "hasSyntheticData": "rai:hasSyntheticData",
            "samplingRate": "cr:samplingRate",
            "wasDerivedFrom": "prov:wasDerivedFrom",
            "wasGeneratedBy": "prov:wasGeneratedBy",
        },
        "@type": "sc:Dataset",
        "name": name,
        "description": description,
        "url": url,
        "license": "https://spdx.org/licenses/MIT.html",
        "conformsTo": [
            "http://mlcommons.org/croissant/1.1",
            "http://mlcommons.org/croissant/RAI/1.0",
        ],
        "version": "1.0.0",
        "datePublished": "2026-05-06",
        "creator": {
            "@type": "sc:Organization",
            "name": "Nanoclaw contributors",
        },
        "keywords": [
            "agent benchmark",
            "workplace tasks",
            "tool use",
            "multi-turn",
            "skills",
            "synthetic data",
        ],
        "distribution": [
            {
                "@type": "cr:FileObject",
                "@id": "huggingface_repository",
                "name": "ClawBenchPro Hugging Face repository",
                "contentUrl": url,
                "encodingFormat": "git+https",
                "sha256": sha256_file(REPO_ROOT / "ClawBenchPro" / "manifest.json"),
            },
            *distribution,
        ],
        "citeAs": (
            "ClawBenchPro: A compact, builder-based workplace-agent benchmark collection. "
            f"{url}"
        ),
        "recordSet": [
            {
                "@type": "cr:RecordSet",
                "@id": "task_index",
                "name": "Task index",
                "description": (
                    f"One row per task in {name}. This index points to task YAML files, "
                    "prompt files, task-local builders, generated asset locations, and skill counts."
                ),
                "field": [
                    croissant_column("dataset", "sc:Text"),
                    croissant_column("task_id", "sc:Text"),
                    croissant_column("category", "sc:Text"),
                    croissant_column("task_file", "sc:Text"),
                    croissant_column("asset_dir", "sc:Text"),
                    croissant_column("prompt_files", "sc:Text"),
                    croissant_column("skill_count", "sc:Integer"),
                ],
            }
        ],
        "rai:dataLimitations": (
            "ClawBenchPro is intended for evaluating workplace-style agent behavior in controlled "
            "synthetic tasks. It is not representative of all languages, geographies, industries, "
            "accessibility needs, safety-critical domains, or real production workplaces. It should "
            "not be used as the sole basis for deployment, hiring, medical, legal, financial, or "
            "safety-critical decisions."
        ),
        "rai:dataBiases": (
            "The tasks were selected and generated to stress agentic workflows, tool use, state "
            "tracking, and benchmark coverage. This introduces selection bias toward tasks that are "
            "easy to package as local workspaces and may underrepresent low-resource languages, "
            "non-technical occupations, and domains requiring embodied or social interaction."
        ),
        "rai:personalSensitiveInformation": (
            "The dataset is designed as synthetic benchmark data and is not intended to contain "
            "real personal data. Some tasks may include fictional personas, synthetic internal URLs, "
            "synthetic keys, policy-sensitive text, or domain-specific records as benchmark fixtures."
        ),
        "rai:dataUseCases": (
            "Validated use cases include comparative evaluation of language-agent runners on "
            "workplace-style tasks, category-level benchmark analysis, and reproducibility studies. "
            "The dataset is not validated for model fine-tuning, safety certification, demographic "
            "fairness auditing, or real-world job-performance measurement."
        ),
        "rai:dataSocialImpact": (
            "Potential positive impacts include more reproducible agent evaluation and better "
            "measurement of multi-turn, tool-using systems. Risks include overgeneralizing benchmark "
            "scores, optimizing narrowly to synthetic tasks, or exposing agents to policy-sensitive "
            "fixtures without appropriate safeguards. The package documents task categories and uses "
            "local synthetic environments to reduce dependence on external services."
        ),
        "rai:hasSyntheticData": True,
        "prov:wasDerivedFrom": [
            {
                "@id": "nanoclaw_generation_pipeline",
                "name": "Nanoclaw task generation and import pipeline",
            }
        ],
        "prov:wasGeneratedBy": [
            {
                "@type": "prov:Activity",
                "name": "ClawBenchPro packaging",
                "description": (
                    "Tasks were generated, staged, imported into Nanoclaw task YAML format, "
                    "validated with env_builder.py builders, grouped into two aligned benchmark "
                    "datasets, sanitized for local path leakage, and exported in compact builder-only "
                    "form for hosting."
                ),
                "prov:used": [
                    "scripts/unpack_task_batch.py",
                    "scripts/import_staged_tasks.py",
                    "scripts/build_published_workplace_datasets.py",
                    "scripts/build_clawbenchpro_hf_dataset.py",
                ],
            }
        ],
        "additionalProperty": [
            {
                "@type": "sc:PropertyValue",
                "name": "task_count",
                "value": task_count,
            },
            {
                "@type": "sc:PropertyValue",
                "name": "dataset_root",
                "value": dataset_root,
            },
            {
                "@type": "sc:PropertyValue",
                "name": "group_counts",
                "value": json.dumps(groups, ensure_ascii=False, sort_keys=True),
            },
        ],
    }
    return metadata


def croissant_column(column: str, data_type: str) -> dict[str, Any]:
    return {
        "@type": "cr:Field",
        "@id": column,
        "name": column,
        "dataType": data_type,
        "source": {
            "fileObject": {"@id": "dataset_index_csv"},
            "extract": {"column": column},
        },
    }


def checksum_for_relative_path(relative_path: str) -> str | None:
    path = root_path_for_croissant(relative_path)
    return sha256_file(path) if path.exists() else None


def root_path_for_croissant(relative_path: str) -> Path:
    return REPO_ROOT / "ClawBenchPro" / relative_path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    def strip_none(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: strip_none(v) for k, v in value.items() if v is not None}
        if isinstance(value, list):
            return [strip_none(item) for item in value]
        return value

    path.write_text(
        json.dumps(strip_none(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_checksums(root: Path) -> None:
    for dataset in DATASETS:
        dataset_root = root / dataset["name"]
        if dataset_root.is_dir():
            write_checksums_for_root(dataset_root, dataset_root / "checksums.sha256")
    write_checksums_for_root(root, root / "checksums.sha256")


def write_checksums_for_root(root: Path, output_path: Path) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path == output_path:
            continue
        digest = sha256_file(path)
        rows.append(f"{digest}  {path.relative_to(root).as_posix()}")
    output_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_files(root: Path) -> tuple[int, int]:
    file_count = 0
    byte_count = 0
    for path in root.rglob("*"):
        if path.is_file():
            file_count += 1
            byte_count += path.stat().st_size
    return file_count, byte_count


if __name__ == "__main__":
    raise SystemExit(main())
