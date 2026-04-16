from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nanoclaw.batch_runner import default_worker_count, resolve_task_specs, run_batch
from nanoclaw.evaluator import (
    evaluate_run,
    summarize_evaluations,
    write_evaluation_csv,
    write_evaluation_json,
    write_evaluation_summary_json,
)
from nanoclaw.generated_task_validator import (
    autofix_prompt_repo_asset_paths,
    autofix_verify_rules_runtime_paths,
    delete_invalid_task,
    quarantine_invalid_task,
    validate_generated_task,
    write_validation_report,
)
from nanoclaw.task_normalizer import normalize_task_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch-run generated nanoclaw tasks with optional model override."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["tasks/data_*.yaml"],
        help="Task file paths or glob patterns. Defaults to tasks/data_*.yaml.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override runtime.model for every task in this batch run.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=default_worker_count(),
        help="Number of concurrent task workers.",
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory used to store task run outputs.",
    )
    parser.add_argument(
        "--keep-assets",
        action="store_true",
        help="Keep assets/<task-id>/ after each run instead of deleting builder output.",
    )
    parser.add_argument(
        "--approval-mode",
        choices=("reject", "approve-all"),
        default=None,
        help="Override runtime.approval_mode for this batch. If omitted, use the task YAML value.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Do not validate generated tasks before running them.",
    )
    parser.add_argument(
        "--skip-normalize",
        action="store_true",
        help="Do not normalize task YAML files before preflight validation or execution.",
    )
    parser.add_argument(
        "--skip-auto-fix",
        action="store_true",
        help="Do not auto-fix safe prompt path issues before preflight validation or execution.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not save pre-normalization backups.",
    )
    parser.add_argument(
        "--backup-root",
        default=".task_normalizer_backups",
        help="Directory used for pre-normalization backups when backups are enabled.",
    )
    parser.add_argument(
        "--run-builder-validation",
        action="store_true",
        help="Execute env_builder.py during preflight validation before the real batch run.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat remaining warnings as invalid tasks during preflight validation.",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--quarantine-invalid",
        action="store_true",
        help="Move invalid tasks out of the active repo tree during preflight validation.",
    )
    action_group.add_argument(
        "--delete-invalid",
        action="store_true",
        help="Delete invalid tasks during preflight validation. Use with care.",
    )
    parser.add_argument(
        "--quarantine-root",
        default=".invalid_generated",
        help="Root directory used by --quarantine-invalid.",
    )
    parser.add_argument(
        "--validation-report",
        default=None,
        help="JSON path used to save preflight validation results. Defaults to <results-dir>/invalid_tasks.json when invalid tasks are found.",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate the run directories produced by this batch after execution completes.",
    )
    parser.add_argument(
        "--evaluation-json-out",
        default=None,
        help="JSON output path for detailed evaluation results. Defaults to <results-dir>/evaluation.json.",
    )
    parser.add_argument(
        "--evaluation-csv-out",
        default=None,
        help="CSV output path for summarized evaluation results. Defaults to <results-dir>/evaluation.csv.",
    )
    parser.add_argument(
        "--evaluation-summary-out",
        default=None,
        help="JSON output path for aggregate evaluation metrics. Defaults to <results-dir>/evaluation_summary.json.",
    )
    return parser


def expand_paths(patterns: list[str]) -> list[Path]:
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
            if resolved_path in seen:
                continue
            seen.add(resolved_path)
            resolved.append(resolved_path)
    return resolved


def resolve_output_path(path_value: str | None, *, default_path: Path) -> Path:
    if not path_value:
        return default_path.resolve()
    path = Path(path_value)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    task_paths = expand_paths(args.paths)
    if not task_paths:
        parser.error("No task files matched the provided paths.")
    results_dir = (REPO_ROOT / args.results_dir).resolve()

    if not args.skip_normalize:
        backup_root = Path(args.backup_root)
        if not backup_root.is_absolute():
            backup_root = (REPO_ROOT / backup_root).resolve()
        normalized_changed = 0
        for task_path in task_paths:
            normalize_result = normalize_task_file(
                task_path,
                create_backup=not args.no_backup,
                backup_root=backup_root,
            )
            if normalize_result.changed:
                normalized_changed += 1
        print(
            f"Preflight normalization: {len(task_paths)} task file(s), changed {normalized_changed}."
        )

    if not args.skip_auto_fix:
        prompt_fixed = 0
        for task_path in task_paths:
            autofix_result = autofix_prompt_repo_asset_paths(task_path, repo_root=REPO_ROOT)
            if autofix_result.changed_files:
                prompt_fixed += 1
        verify_fixed = 0
        for task_path in task_paths:
            autofix_result = autofix_verify_rules_runtime_paths(task_path, repo_root=REPO_ROOT)
            if autofix_result.changed_files:
                verify_fixed += 1
        print(
            f"Preflight auto-fix: prompt paths updated in {prompt_fixed} task(s), verify_rules paths updated in {verify_fixed} task(s)."
        )

    valid_task_paths = task_paths
    invalid_results = []
    validation_results = []
    if not args.skip_validation:
        valid_task_paths = []
        for task_path in task_paths:
            result = validate_generated_task(
                task_path,
                repo_root=REPO_ROOT,
                run_builder=args.run_builder_validation,
                keep_assets=args.keep_assets,
            )
            validation_results.append(result)
            if result.has_errors or (args.strict and result.has_warnings):
                invalid_results.append(result)
            else:
                valid_task_paths.append(task_path)

        if invalid_results:
            report_path = (
                Path(args.validation_report).resolve()
                if args.validation_report and Path(args.validation_report).is_absolute()
                else (
                    (REPO_ROOT / args.validation_report).resolve()
                    if args.validation_report
                    else (results_dir / "invalid_tasks.json").resolve()
                )
            )
            write_validation_report(validation_results, output_path=report_path)
            print(f"Validation report written to {report_path}")

            if args.quarantine_invalid:
                quarantine_root = (REPO_ROOT / args.quarantine_root).resolve()
                for result in invalid_results:
                    moved = quarantine_invalid_task(
                        result,
                        repo_root=REPO_ROOT,
                        quarantine_root=quarantine_root,
                    )
                    print(
                        f"Quarantined invalid task {result.task_id}: {len(moved)} path(s) moved to {quarantine_root}"
                    )
            elif args.delete_invalid:
                for result in invalid_results:
                    deleted = delete_invalid_task(result, repo_root=REPO_ROOT)
                    print(f"Deleted invalid task {result.task_id}: {len(deleted)} path(s)")

            print(
                f"Skipped {len(invalid_results)} invalid task(s) during preflight validation."
            )

    if not valid_task_paths:
        print("No valid task files remained after preflight validation.")
        return 1

    specs = resolve_task_specs(
        [str(path.relative_to(REPO_ROOT)) for path in valid_task_paths],
        repo_root=REPO_ROOT,
    )
    if not specs:
        parser.error("No valid task files matched the provided paths.")

    results = run_batch(
        specs,
        repo_root=REPO_ROOT,
        results_dir=results_dir,
        model=args.model,
        workers=max(1, args.workers),
        cleanup_assets=not args.keep_assets,
        approval_mode=args.approval_mode,
    )

    failed = [result for result in results if not result.success]
    print(f"Completed {len(results)} task runs: {len(results) - len(failed)} succeeded, {len(failed)} failed.")

    evaluation_failed = False
    if args.evaluate:
        run_dirs = [result.run_dir for result in results if result.run_dir is not None]
        if run_dirs:
            evaluation_results = [evaluate_run(run_dir, repo_root=REPO_ROOT) for run_dir in run_dirs]
            evaluation_summary = summarize_evaluations(evaluation_results)
            evaluation_json_out = resolve_output_path(
                args.evaluation_json_out,
                default_path=results_dir / "evaluation.json",
            )
            evaluation_csv_out = resolve_output_path(
                args.evaluation_csv_out,
                default_path=results_dir / "evaluation.csv",
            )
            evaluation_summary_out = resolve_output_path(
                args.evaluation_summary_out,
                default_path=results_dir / "evaluation_summary.json",
            )
            write_evaluation_json(evaluation_results, output_path=evaluation_json_out)
            write_evaluation_csv(evaluation_results, output_path=evaluation_csv_out)
            write_evaluation_summary_json(
                evaluation_summary,
                output_path=evaluation_summary_out,
            )
            print(
                f"Evaluation summary: {evaluation_summary.completed_runs}/{evaluation_summary.total_runs} completed run(s), "
                f"{evaluation_summary.evaluated_runs} verified, {evaluation_summary.scored_runs} scored."
            )
            print(
                f"Perfect-score rate: {evaluation_summary.perfect_score_rate:.2f}% "
                f"({evaluation_summary.perfect_score_runs}/{evaluation_summary.total_runs})."
            )
            if evaluation_summary.benchmark_score is not None:
                print(
                    f"Benchmark score: {evaluation_summary.benchmark_score:.2f}/100 "
                    f"(run success rate {evaluation_summary.run_success_rate:.2f}%, "
                    f"mean objective score {evaluation_summary.average_objective_score:.2f})."
                )
            else:
                print(
                    f"Benchmark score: unavailable "
                    f"(run success rate {evaluation_summary.run_success_rate:.2f}%, no objective scores produced)."
                )
            print(f"Evaluation JSON: {evaluation_json_out}")
            print(f"Evaluation CSV: {evaluation_csv_out}")
            print(f"Evaluation summary JSON: {evaluation_summary_out}")
            evaluation_issues = [
                result
                for result in evaluation_results
                if result.evaluation_status not in {"evaluated", "skipped_run_not_completed"}
            ]
            if evaluation_issues:
                evaluation_failed = True
                print("\nEvaluation issues:")
                for result in evaluation_issues[:20]:
                    print(f"- {result.task_id}/{result.run_id}: {result.evaluation_status}")
                    if result.error:
                        print(f"  error={result.error}")
        else:
            print("Skipped evaluation because this batch did not produce any run directories.")

    if failed:
        print("\nFailures:")
        for result in failed:
            print(f"- {result.spec.task_id}: {result.error or 'unknown error'}")
            if result.run_dir is not None:
                print(f"  run_dir={result.run_dir}")
            if result.stderr.strip():
                print(f"  stderr={result.stderr.strip().splitlines()[-1]}")
            elif result.stdout.strip():
                print(f"  stdout={result.stdout.strip().splitlines()[-1]}")
        return 1

    if evaluation_failed:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
