from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
        description="Normalize and validate generated data_*.yaml tasks before batch execution."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["tasks/data_*.yaml"],
        help="Task file paths or glob patterns. Defaults to tasks/data_*.yaml.",
    )
    parser.add_argument(
        "--skip-normalize",
        action="store_true",
        help="Do not normalize task YAML files before validation.",
    )
    parser.add_argument(
        "--skip-auto-fix",
        action="store_true",
        help="Do not auto-fix safe prompt path issues before validation.",
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
        "--run-builders",
        action="store_true",
        help="Execute env_builder.py during validation and verify the expected asset directory is produced.",
    )
    parser.add_argument(
        "--keep-assets",
        action="store_true",
        help="Keep assets generated during --run-builders instead of deleting them afterwards.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit non-zero when warnings are present.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as invalid dataset items and return non-zero when any warning remains.",
    )
    parser.add_argument(
        "--report-path",
        default=None,
        help="Optional JSON path used to save structured validation results.",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--quarantine-invalid",
        action="store_true",
        help="Move invalid tasks out of the active repo tree instead of leaving them in place.",
    )
    action_group.add_argument(
        "--delete-invalid",
        action="store_true",
        help="Delete invalid tasks and their assets after validation. Use with care.",
    )
    parser.add_argument(
        "--quarantine-root",
        default=".invalid_generated",
        help="Root directory used by --quarantine-invalid.",
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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    task_paths = expand_paths(args.paths)
    if not task_paths:
        parser.error("No task files matched the provided paths.")

    normalized_changed = 0
    if not args.skip_normalize:
        backup_root = Path(args.backup_root)
        if not backup_root.is_absolute():
            backup_root = (REPO_ROOT / backup_root).resolve()
        for task_path in task_paths:
            normalize_result = normalize_task_file(
                task_path,
                create_backup=not args.no_backup,
                backup_root=backup_root,
            )
            if normalize_result.changed:
                normalized_changed += 1
        print(
            f"Normalized {len(task_paths)} task files before validation; changed {normalized_changed}."
        )

    prompt_fixed = 0
    if not args.skip_auto_fix:
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
            f"Auto-fixed prompt path issues in {prompt_fixed} task(s) and verify_rules path issues in {verify_fixed} task(s) before validation."
        )

    error_count = 0
    warning_count = 0
    results = []
    invalid_results = []
    quarantine_root = (REPO_ROOT / args.quarantine_root).resolve()
    for task_path in task_paths:
        result = validate_generated_task(
            task_path,
            repo_root=REPO_ROOT,
            run_builder=args.run_builders,
            keep_assets=args.keep_assets,
        )
        results.append(result)
        if not result.issues:
            print(f"ok: {result.task_id}")
            continue

        print(f"{result.task_id}:")
        for issue in result.issues:
            print(f"  [{issue.severity}] {issue.code}: {issue.message}")
            if issue.severity == "error":
                error_count += 1
            elif issue.severity == "warning":
                warning_count += 1
        is_invalid = result.has_errors or (args.strict and result.has_warnings)
        if is_invalid:
            invalid_results.append(result)

    if args.quarantine_invalid:
        for result in invalid_results:
            moved = quarantine_invalid_task(
                result,
                repo_root=REPO_ROOT,
                quarantine_root=quarantine_root,
            )
            print(f"  action: quarantined {len(moved)} path(s) under {quarantine_root}")
    elif args.delete_invalid:
        for result in invalid_results:
            deleted = delete_invalid_task(result, repo_root=REPO_ROOT)
            print(f"  action: deleted {len(deleted)} path(s)")

    if args.report_path:
        report_path = Path(args.report_path)
        if not report_path.is_absolute():
            report_path = (REPO_ROOT / report_path).resolve()
        write_validation_report(results, output_path=report_path)
        print(f"Validation report written to {report_path}")

    print(
        f"Validated {len(task_paths)} tasks; errors={error_count} warnings={warning_count}."
    )
    if error_count:
        return 1
    if warning_count and (args.fail_on_warning or args.strict):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
