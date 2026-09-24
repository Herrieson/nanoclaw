"""Inspect or run one ClawBenchPro task through the bundled NanoClaw runner."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "src" / "nanoclaw"
DATA = ROOT / "data" / "ClawBenchPro"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="round_01_aligned_mix_800")
    parser.add_argument("--task", default=None, help="Task YAML filename or task id")
    parser.add_argument("--model", default=os.getenv("NANOCLAW_MODEL", "gpt-4o-mini"))
    parser.add_argument("--run", action="store_true", help="Execute the task")
    parser.add_argument("--list-only", action="store_true", help="Only print the selected task")
    args = parser.parse_args()
    dataset = DATA / args.dataset
    task_dir = dataset / "tasks"
    if not task_dir.is_dir():
        parser.error(f"dataset not found: {dataset}")
    tasks = sorted(task_dir.glob("*.yaml"))
    if args.task:
        wanted = args.task if args.task.endswith(".yaml") else args.task + ".yaml"
        tasks = [p for p in tasks if p.name == wanted or p.stem == args.task]
    if not tasks:
        parser.error("no matching task YAML found")
    task = tasks[0]
    print(f"dataset={args.dataset}\ntask={task.relative_to(ROOT)}")
    if not args.run or args.list_only:
        return 0
    command = [sys.executable, "scripts/run_generated_tasks.py", str(task),
               "--model", args.model, "--workers", "1", "--approval-mode", "reject",
               "--results-dir", str(ROOT / "results" / "smoke")]
    return subprocess.run(command, cwd=RUNNER).returncode


if __name__ == "__main__":
    raise SystemExit(main())

