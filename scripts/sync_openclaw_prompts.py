from __future__ import annotations

import argparse
from pathlib import Path

from nanoclaw.prompt_sync import sync_official_prompts


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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = tuple(item.strip() for item in args.files.split(",") if item.strip())
    if not files:
        raise ValueError("No files provided")

    result = sync_official_prompts(
        output_dir=Path(args.output_dir),
        files=files,
        repo_url=args.repo_url,
        ref=args.ref,
    )

    print(f"Synced commit: {result.source_commit}")
    print(f"Manifest: {result.manifest_path}")
    for file in result.copied_files:
        print(f"- {file}")


if __name__ == "__main__":
    main()
