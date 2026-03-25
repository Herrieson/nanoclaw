from __future__ import annotations

import argparse
from pathlib import Path

from nanoclaw.prompt_sync import (
    list_prompt_versions,
    switch_prompt_version,
    sync_official_prompts,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync official prompt files from openclaw/openclaw"
    )
    parser.add_argument(
        "--repo-url",
        default="https://github.com/openclaw/openclaw.git",
        help="Source repository URL",
    )
    parser.add_argument("--ref", default="main", help="Git branch/tag/commit")
    parser.add_argument(
        "--files",
        default="CLAUDE.md,AGENTS.md",
        help="Comma separated root-relative file paths",
    )
    parser.add_argument(
        "--output-dir",
        default="workspace/prompts/official",
        help="Destination folder",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force pull from remote and create a new snapshot if changed",
    )
    parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List local prompt snapshots and show active one",
    )
    parser.add_argument(
        "--switch-version",
        default=None,
        help="Activate an existing local snapshot by version id",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

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

    files = tuple(item.strip() for item in args.files.split(",") if item.strip())
    if not files:
        raise ValueError("No files provided")

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


if __name__ == "__main__":
    main()
