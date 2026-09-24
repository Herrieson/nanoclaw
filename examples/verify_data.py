"""Verify every tracked benchmark file against its dataset checksum manifest."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "ClawBenchPro"


def verify(manifest: Path) -> tuple[int, int]:
    checked = failed = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, relative = line.split(maxsplit=1)
        path = manifest.parent / relative
        if not path.is_file():
            print(f"MISSING {path}")
            failed += 1
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checked += 1
        if actual != digest:
            print(f"FAIL {path}: expected {digest}, got {actual}")
            failed += 1
    return checked, failed


def main() -> int:
    # The upstream root inventory includes its publishing repository metadata.
    # The subset inventories are the portable release manifests.
    manifests = sorted(ROOT.glob("*/checksums.sha256"))
    total = failures = 0
    for manifest in manifests:
        checked, failed = verify(manifest)
        print(f"{manifest.relative_to(ROOT)}: checked={checked} failed={failed}")
        total += checked
        failures += failed
    print(f"total_checked={total} total_failed={failures}")
    return int(failures != 0)


if __name__ == "__main__":
    raise SystemExit(main())
