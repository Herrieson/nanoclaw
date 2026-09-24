from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSIONS_DIRNAME = "versions"


@dataclass(frozen=True, slots=True)
class SyncResult:
    source_commit: str
    manifest_path: Path
    copied_files: tuple[Path, ...]
    version_id: str
    used_cache: bool
    pulled: bool


@dataclass(frozen=True, slots=True)
class PromptVersion:
    version_id: str
    source_commit: str
    generated_at_utc: str
    manifest_path: Path
    files: tuple[str, ...]
    active: bool


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


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid JSON object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _manifest_contains_files(payload: dict[str, Any], files: tuple[str, ...]) -> bool:
    file_map = payload.get("files")
    if not isinstance(file_map, dict):
        return False
    return all(relative_file in file_map for relative_file in files)


def _iter_version_manifests(output_dir: Path, manifest_name: str) -> list[Path]:
    versions_dir = output_dir / VERSIONS_DIRNAME
    if not versions_dir.exists():
        return []
    return sorted(versions_dir.glob(f"*/{manifest_name}"), reverse=True)


def _new_version_id(output_dir: Path, commit: str) -> str:
    prefix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_commit = (commit or "unknown")[:12]
    base = f"{prefix}_{short_commit}"
    versions_dir = output_dir / VERSIONS_DIRNAME
    candidate = base
    suffix = 1
    while (versions_dir / candidate).exists():
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def _snapshot_manifest_path(
    output_dir: Path, version_id: str, manifest_name: str
) -> Path:
    return output_dir / VERSIONS_DIRNAME / version_id / manifest_name


def _ensure_manifest_version_id(
    output_dir: Path, manifest_payload: dict[str, Any], manifest_name: str
) -> str:
    existing = manifest_payload.get("version_id")
    if isinstance(existing, str) and existing:
        snapshot_manifest = _snapshot_manifest_path(output_dir, existing, manifest_name)
        if snapshot_manifest.exists():
            return existing

    commit = str(manifest_payload.get("source_commit", "unknown"))
    version_id = _new_version_id(output_dir, commit)
    snapshot_dir = output_dir / VERSIONS_DIRNAME / version_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    file_map = manifest_payload.get("files")
    if not isinstance(file_map, dict) or not file_map:
        raise ValueError("Manifest is missing file checksums")

    for relative_file in file_map:
        source = output_dir / relative_file
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(
                f"Missing local prompt file while materializing snapshot: {relative_file}"
            )
        destination = snapshot_dir / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    manifest_payload["version_id"] = version_id
    manifest_payload["snapshot_dir"] = f"{VERSIONS_DIRNAME}/{version_id}"
    snapshot_manifest = snapshot_dir / manifest_name
    _write_json(snapshot_manifest, manifest_payload)
    _write_json(output_dir / manifest_name, manifest_payload)
    return version_id


def _activate_snapshot(
    output_dir: Path, version_id: str, manifest_name: str
) -> tuple[Path, ...]:
    snapshot_manifest = _snapshot_manifest_path(output_dir, version_id, manifest_name)
    if not snapshot_manifest.exists():
        raise FileNotFoundError(f"Version not found: {version_id}")

    payload = _read_json(snapshot_manifest)
    file_map = payload.get("files")
    if not isinstance(file_map, dict) or not file_map:
        raise ValueError(f"Invalid snapshot manifest: {snapshot_manifest}")

    snapshot_dir = snapshot_manifest.parent
    copied: list[Path] = []

    for relative_file in file_map:
        source = snapshot_dir / relative_file
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(
                f"Snapshot file missing: {relative_file} in version {version_id}"
            )
        destination = output_dir / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        copied.append(destination)

    payload["version_id"] = version_id
    payload["snapshot_dir"] = f"{VERSIONS_DIRNAME}/{version_id}"
    _write_json(output_dir / manifest_name, payload)
    return tuple(copied)


def _find_matching_snapshot(
    output_dir: Path,
    manifest_name: str,
    source_repo: str,
    source_ref: str,
    checksums: dict[str, dict[str, str | int]],
) -> str | None:
    for snapshot_manifest in _iter_version_manifests(output_dir, manifest_name):
        payload = _read_json(snapshot_manifest)
        if payload.get("source_repo") != source_repo:
            continue
        if payload.get("source_ref") != source_ref:
            continue

        file_map = payload.get("files")
        if not isinstance(file_map, dict):
            continue

        matched = True
        for relative_file, meta in checksums.items():
            existing_meta = file_map.get(relative_file)
            if not isinstance(existing_meta, dict):
                matched = False
                break
            if str(existing_meta.get("sha256", "")) != str(meta.get("sha256", "")):
                matched = False
                break
            if str(existing_meta.get("bytes", "")) != str(meta.get("bytes", "")):
                matched = False
                break

        if matched:
            version_id = payload.get("version_id")
            if isinstance(version_id, str) and version_id:
                return version_id
            return snapshot_manifest.parent.name

    return None


def sync_official_prompts(
    output_dir: Path,
    files: tuple[str, ...],
    repo_url: str = "https://github.com/openclaw/openclaw.git",
    ref: str = "main",
    manifest_name: str = "manifest.json",
    force_refresh: bool = False,
) -> SyncResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / manifest_name

    if not force_refresh and manifest_path.exists():
        payload = _read_json(manifest_path)
        if _manifest_contains_files(payload, files):
            is_valid, _ = verify_manifest(manifest_path=manifest_path, base_dir=output_dir)
            if is_valid:
                version_id = _ensure_manifest_version_id(
                    output_dir=output_dir,
                    manifest_payload=payload,
                    manifest_name=manifest_name,
                )
                payload = _read_json(manifest_path)
                copied = tuple(output_dir / relative_file for relative_file in files)
                return SyncResult(
                    source_commit=str(payload.get("source_commit", "unknown")),
                    manifest_path=manifest_path,
                    copied_files=copied,
                    version_id=version_id,
                    used_cache=True,
                    pulled=False,
                )

    with tempfile.TemporaryDirectory(prefix="nanoclaw-sync-") as tmp:
        repo_dir = Path(tmp) / "openclaw"
        _run_git(["clone", "--depth", "1", "--branch", ref, repo_url, str(repo_dir)])
        commit = _run_git(["rev-parse", "HEAD"], cwd=repo_dir)

        checksums: dict[str, dict[str, str | int]] = {}
        staged_data: dict[str, bytes] = {}

        for relative_file in files:
            source = repo_dir / relative_file
            if not source.exists() or not source.is_file():
                raise FileNotFoundError(
                    f"Cannot find '{relative_file}' in {repo_url}@{ref}"
                )

            data = source.read_bytes()
            staged_data[relative_file] = data
            checksums[relative_file] = {
                "sha256": _sha256(data),
                "bytes": len(data),
            }

    matching_version = _find_matching_snapshot(
        output_dir=output_dir,
        manifest_name=manifest_name,
        source_repo=repo_url,
        source_ref=ref,
        checksums=checksums,
    )
    if matching_version:
        copied = _activate_snapshot(
            output_dir=output_dir,
            version_id=matching_version,
            manifest_name=manifest_name,
        )
        active_payload = _read_json(manifest_path)
        return SyncResult(
            source_commit=str(active_payload.get("source_commit", "unknown")),
            manifest_path=manifest_path,
            copied_files=copied,
            version_id=matching_version,
            used_cache=True,
            pulled=True,
        )

    version_id = _new_version_id(output_dir=output_dir, commit=commit)
    snapshot_dir = output_dir / VERSIONS_DIRNAME / version_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for relative_file, data in staged_data.items():
        destination = snapshot_dir / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    manifest = {
        "source_repo": repo_url,
        "source_ref": ref,
        "source_commit": commit,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "version_id": version_id,
        "snapshot_dir": f"{VERSIONS_DIRNAME}/{version_id}",
        "files": checksums,
    }
    _write_json(snapshot_dir / manifest_name, manifest)

    copied = _activate_snapshot(
        output_dir=output_dir,
        version_id=version_id,
        manifest_name=manifest_name,
    )
    return SyncResult(
        source_commit=commit,
        manifest_path=manifest_path,
        copied_files=copied,
        version_id=version_id,
        used_cache=False,
        pulled=True,
    )


def switch_prompt_version(
    output_dir: Path,
    version_id: str,
    manifest_name: str = "manifest.json",
) -> SyncResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = _activate_snapshot(
        output_dir=output_dir,
        version_id=version_id,
        manifest_name=manifest_name,
    )
    manifest_path = output_dir / manifest_name
    payload = _read_json(manifest_path)
    return SyncResult(
        source_commit=str(payload.get("source_commit", "unknown")),
        manifest_path=manifest_path,
        copied_files=copied,
        version_id=version_id,
        used_cache=True,
        pulled=False,
    )


def list_prompt_versions(
    output_dir: Path,
    manifest_name: str = "manifest.json",
) -> tuple[PromptVersion, ...]:
    active_manifest = output_dir / manifest_name
    active_version: str | None = None
    if active_manifest.exists():
        payload = _read_json(active_manifest)
        active_raw = payload.get("version_id")
        if isinstance(active_raw, str) and active_raw:
            active_version = active_raw

    versions: list[PromptVersion] = []
    for snapshot_manifest in _iter_version_manifests(output_dir, manifest_name):
        payload = _read_json(snapshot_manifest)
        version_raw = payload.get("version_id")
        version_id = (
            version_raw
            if isinstance(version_raw, str) and version_raw
            else snapshot_manifest.parent.name
        )
        file_map = payload.get("files")
        file_names = tuple(file_map.keys()) if isinstance(file_map, dict) else ()
        versions.append(
            PromptVersion(
                version_id=version_id,
                source_commit=str(payload.get("source_commit", "unknown")),
                generated_at_utc=str(payload.get("generated_at_utc", "")),
                manifest_path=snapshot_manifest,
                files=file_names,
                active=version_id == active_version,
            )
        )

    if versions:
        return tuple(versions)

    if active_manifest.exists():
        payload = _read_json(active_manifest)
        file_map = payload.get("files")
        file_names = tuple(file_map.keys()) if isinstance(file_map, dict) else ()
        return (
            PromptVersion(
                version_id="legacy-active",
                source_commit=str(payload.get("source_commit", "unknown")),
                generated_at_utc=str(payload.get("generated_at_utc", "")),
                manifest_path=active_manifest,
                files=file_names,
                active=True,
            ),
        )

    return ()


def verify_manifest(manifest_path: Path, base_dir: Path) -> tuple[bool, list[str]]:
    if not manifest_path.exists():
        return False, [f"manifest not found: {manifest_path}"]

    payload = _read_json(manifest_path)
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
