from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .config import DEFAULT_PROMPT_FILES, Settings
from .core_loop import MinimalClaw
from .prompt_sync import (
    list_prompt_versions,
    switch_prompt_version,
    sync_official_prompts,
    verify_manifest,
)


def _parse_csv_files(raw: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _load_task(task: str | None, task_file: str | None) -> str:
    if task:
        return task
    if task_file:
        return Path(task_file).read_text(encoding="utf-8")
    raise ValueError("Provide --task or --task-file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="nanoclaw minimal agent loop")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("bootstrap", help="Create minimal workspace files")

    sync_parser = sub.add_parser(
        "sync-prompts", help="Copy official prompt files from openclaw repo"
    )
    sync_parser.add_argument(
        "--repo-url",
        default="https://github.com/openclaw/openclaw.git",
        help="Source repository URL",
    )
    sync_parser.add_argument("--ref", default="main", help="Git ref/branch/tag")
    sync_parser.add_argument(
        "--files",
        default=",".join(DEFAULT_PROMPT_FILES),
        help="Comma separated file list, relative to repository root",
    )
    sync_parser.add_argument(
        "--output-dir",
        default=None,
        help="Output prompt directory (default: from Settings)",
    )
    sync_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force pull from remote and create/activate a new snapshot if content changed",
    )
    sync_parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List local prompt snapshots and show active one",
    )
    sync_parser.add_argument(
        "--switch-version",
        default=None,
        help="Activate an existing local prompt snapshot by version id",
    )

    verify_parser = sub.add_parser(
        "verify-prompts", help="Verify copied prompt files with manifest"
    )
    verify_parser.add_argument(
        "--manifest",
        default=None,
        help="Manifest path (default: <prompt_dir>/manifest.json)",
    )
    verify_parser.add_argument(
        "--base-dir",
        default=None,
        help="Base directory for prompt files (default: prompt_dir)",
    )

    run_parser = sub.add_parser("run", help="Run the minimal agent loop")
    run_parser.add_argument("--task", default=None, help="Task string")
    run_parser.add_argument("--task-file", default=None, help="Load task text from file")
    run_parser.add_argument(
        "--max-steps", type=int, default=None, help="Override max tool steps"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "bootstrap":
        agent = MinimalClaw(settings)
        agent.bootstrap_workspace()
        print(f"Workspace ready: {settings.workspace_dir}")
        print(f"Prompt dir: {settings.prompt_dir}")
        return

    if args.command == "sync-prompts":
        output_dir = Path(args.output_dir) if args.output_dir else settings.prompt_dir

        if args.list_versions and args.switch_version:
            raise ValueError("--list-versions cannot be combined with --switch-version")
        if args.switch_version and args.refresh:
            raise ValueError("--switch-version cannot be combined with --refresh")

        if args.list_versions:
            versions = list_prompt_versions(output_dir)
            if not versions:
                print("No saved prompt versions")
                return
            for version in versions:
                marker = "*" if version.active else " "
                files_text = ", ".join(version.files) if version.files else "-"
                print(
                    f"{marker} {version.version_id} "
                    f"commit={version.source_commit} "
                    f"generated_at={version.generated_at_utc} "
                    f"files={files_text}"
                )
            return

        if args.switch_version:
            result = switch_prompt_version(
                output_dir=output_dir,
                version_id=args.switch_version,
            )
            print(f"Switched to version: {result.version_id}")
            print(f"Source commit: {result.source_commit}")
            print(f"Manifest: {result.manifest_path}")
            for file in result.copied_files:
                print(f"- {file}")
            return

        files = _parse_csv_files(args.files)
        if not files:
            raise ValueError("No files provided for --files")

        result = sync_official_prompts(
            output_dir=output_dir,
            files=files,
            repo_url=args.repo_url,
            ref=args.ref,
            force_refresh=args.refresh,
        )
        if result.used_cache and not result.pulled:
            print(f"Using cached prompt version: {result.version_id}")
        elif result.used_cache and result.pulled:
            print(f"No prompt changes. Reusing version: {result.version_id}")
        else:
            print(f"Created prompt version: {result.version_id}")
        print(f"Synced commit: {result.source_commit}")
        print(f"Manifest: {result.manifest_path}")
        for file in result.copied_files:
            print(f"- {file}")
        return

    if args.command == "verify-prompts":
        base_dir = Path(args.base_dir) if args.base_dir else settings.prompt_dir
        manifest = Path(args.manifest) if args.manifest else base_dir / "manifest.json"
        ok, errors = verify_manifest(manifest_path=manifest, base_dir=base_dir)
        if ok:
            print("Prompt manifest verification passed")
            return
        print("Prompt manifest verification failed")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    if args.command == "run":
        task = _load_task(args.task, args.task_file)
        if args.max_steps is not None:
            settings = replace(settings, max_steps=args.max_steps)

        agent = MinimalClaw(settings)
        agent.bootstrap_workspace()
        agent.run(task, echo=True)
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
