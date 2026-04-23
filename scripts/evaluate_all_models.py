from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class ModelEvaluationTarget:
    model_name: str
    model_dir: Path

    @property
    def run_pattern(self) -> str:
        return f"{self.model_dir.relative_to(REPO_ROOT).as_posix()}/data_*/*"

    @property
    def json_out(self) -> Path:
        return self.model_dir / "evaluation.json"

    @property
    def csv_out(self) -> Path:
        return self.model_dir / "evaluation.csv"

    @property
    def summary_out(self) -> Path:
        return self.model_dir / "evaluation_summary.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate all model result directories under results/."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["results/*"],
        help="Model result directories or glob patterns. Defaults to results/*.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip model directories that already contain evaluation.json, evaluation.csv, and evaluation_summary.json.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop immediately if any per-model evaluation exits non-zero.",
    )
    parser.add_argument(
        "--enable-judge",
        action="store_true",
        help="Pass through to evaluate_generated_tasks.py.",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Pass through to evaluate_generated_tasks.py.",
    )
    parser.add_argument(
        "--judge-base-url",
        default=None,
        help="Pass through to evaluate_generated_tasks.py.",
    )
    parser.add_argument(
        "--judge-max-attempts",
        type=int,
        default=None,
        help="Pass through to evaluate_generated_tasks.py.",
    )
    return parser


def _expand_paths(patterns: list[str]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        matches = sorted(REPO_ROOT.glob(pattern))
        if not matches:
            candidate = (REPO_ROOT / pattern).resolve()
            if candidate.exists():
                matches = [candidate]
        for path in matches:
            resolved_path = path.resolve()
            if resolved_path in seen or not resolved_path.is_dir():
                continue
            seen.add(resolved_path)
            resolved.append(resolved_path)
    return resolved


def discover_model_targets(patterns: list[str]) -> list[ModelEvaluationTarget]:
    targets: list[ModelEvaluationTarget] = []
    for model_dir in _expand_paths(patterns):
        if model_dir.name.startswith(".") or model_dir.name == "curation":
            continue
        if not any(child.is_dir() and child.name.startswith("data_") for child in model_dir.iterdir()):
            continue
        targets.append(
            ModelEvaluationTarget(
                model_name=model_dir.name,
                model_dir=model_dir,
            )
        )
    return targets


def build_command(
    target: ModelEvaluationTarget,
    *,
    enable_judge: bool,
    judge_model: str | None,
    judge_base_url: str | None,
    judge_max_attempts: int | None,
) -> list[str]:
    command = [
        sys.executable,
        str((REPO_ROOT / "scripts" / "evaluate_generated_tasks.py").resolve()),
        target.run_pattern,
        "--json-out",
        str(target.json_out),
        "--csv-out",
        str(target.csv_out),
        "--summary-out",
        str(target.summary_out),
    ]
    if enable_judge:
        command.append("--enable-judge")
    if judge_model:
        command.extend(["--judge-model", judge_model])
    if judge_base_url:
        command.extend(["--judge-base-url", judge_base_url])
    if judge_max_attempts is not None:
        command.extend(["--judge-max-attempts", str(judge_max_attempts)])
    return command


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    targets = discover_model_targets(args.paths)
    if not targets:
        parser.error("No model result directories matched the provided paths.")

    failed_models: list[str] = []
    skipped_models = 0

    for index, target in enumerate(targets, start=1):
        if args.skip_existing and target.json_out.exists() and target.csv_out.exists() and target.summary_out.exists():
            skipped_models += 1
            print(f"[{index}/{len(targets)}] Skip {target.model_name}: existing evaluation outputs found.")
            continue

        print(f"[{index}/{len(targets)}] Evaluate {target.model_name}")
        process = subprocess.run(
            build_command(
                target,
                enable_judge=bool(args.enable_judge),
                judge_model=args.judge_model,
                judge_base_url=args.judge_base_url,
                judge_max_attempts=args.judge_max_attempts,
            ),
            cwd=REPO_ROOT,
            text=True,
        )
        if process.returncode != 0:
            failed_models.append(target.model_name)
            if args.stop_on_error:
                print("")
                print(f"Stopped after failure in {target.model_name}.")
                return process.returncode
        print("")

    print(
        f"Evaluated {len(targets) - skipped_models} model(s); "
        f"skipped {skipped_models}; failed {len(failed_models)}."
    )
    if failed_models:
        for model_name in failed_models:
            print(f"- {model_name}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
