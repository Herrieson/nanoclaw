from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ClawBenchProScriptTests(unittest.TestCase):
    def test_data_1878_turn_1_repair_ignores_directories(self) -> None:
        module = load_script_module(
            "materialize_clawbenchpro_workplace_verifiers",
            "scripts/materialize_clawbenchpro_workplace_verifiers.py",
        )
        original = (
            '    memo_files = [f for f in os.listdir(workspace) if "memo" in f.lower() '
            'or "archive" in f.lower() or "logic" in f.lower() or "report" in f.lower()]\n'
            "    if memo_files:\n"
        )

        repaired = module.apply_known_turn_repairs(
            original,
            source_task_id="data_1878",
            turn=1,
        )

        self.assertIn("os.path.isfile(os.path.join(workspace, f))", repaired)
        self.assertIn("if memo_files:", repaired)

    def test_subset_builder_excludes_context_limit_outlier(self) -> None:
        module = load_script_module(
            "build_clawbenchpro_subsets",
            "scripts/build_clawbenchpro_subsets.py",
        )

        self.assertIn(
            "data_persona_aligned_hard_50_0022",
            module.EXCLUDED_IMPORTED_TASK_IDS,
        )


if __name__ == "__main__":
    unittest.main()
