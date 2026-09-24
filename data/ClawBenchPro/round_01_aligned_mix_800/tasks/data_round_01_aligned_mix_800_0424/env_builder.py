from __future__ import annotations

import os
import runpy
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    asset_dir = repo_root / "assets" / "data_round_01_aligned_mix_800_0424"
    asset_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(asset_dir)
    runpy.run_path(str(Path(__file__).with_name("_env_builder_impl.py")), run_name="__main__")


if __name__ == "__main__":
    main()
