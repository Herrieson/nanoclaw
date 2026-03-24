from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SyncResult:
    source_commit: str
    manifest_path: Path
    copied_files: tuple[Path, ...]


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {process.stderr.strip() or process.stdout.strip()}"
        )
    return process.stdout.strip()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sync_official_prompts(
    output_dir: Path,
    files: tuple[str, ...],
    repo_url: str = "https://github.com/openclaw/openclaw.git",
    ref: str = "main",
    manifest_name: str = "manifest.json",
) -> SyncResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="nanoclaw-sync-") as tmp:
        repo_dir = Path(tmp) / "openclaw"
        _run_git(["clone", "--depth", "1", "--branch", ref, repo_url, str(repo_dir)])
        commit = _run_git(["rev-parse", "HEAD"], cwd=repo_dir)

        copied: list[Path] = []
        checksums: dict[str, dict[str, str | int]] = {}

        for relative_file in files:
            source = repo_dir / relative_file
            if not source.exists() or not source.is_file():
                raise FileNotFoundError(
                    f"Cannot find '{relative_file}' in {repo_url}@{ref}"
                )

            destination = output_dir / relative_file
            destination.parent.mkdir(parents=True, exist_ok=True)

            data = source.read_bytes()
            destination.write_bytes(data)
            copied.append(destination)
            checksums[relative_file] = {
                "sha256": _sha256(data),
                "bytes": len(data),
            }

    manifest_path = output_dir / manifest_name
    manifest = {
        "source_repo": repo_url,
        "source_ref": ref,
        "source_commit": commit,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": checksums,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return SyncResult(source_commit=commit, manifest_path=manifest_path, copied_files=tuple(copied))


def verify_manifest(manifest_path: Path, base_dir: Path) -> tuple[bool, list[str]]:
    if not manifest_path.exists():
        return False, [f"manifest not found: {manifest_path}"]

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    file_map = payload.get("files", {})
    errors: list[str] = []

    for relative_file, meta in file_map.items():
        file_path = base_dir / relative_file
        if not file_path.exists():
            errors.append(f"missing file: {relative_file}")
            continue

        current_hash = _sha256(file_path.read_bytes())
        expected_hash = str(meta.get("sha256", ""))
        if current_hash != expected_hash:
            errors.append(
                f"hash mismatch: {relative_file} (expected {expected_hash}, got {current_hash})"
            )

    return len(errors) == 0, errors
