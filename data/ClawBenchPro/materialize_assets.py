#!/usr/bin/env python3
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
