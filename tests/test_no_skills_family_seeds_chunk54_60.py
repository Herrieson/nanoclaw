from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from nanoclaw.config import Settings
from nanoclaw.task_loader import load_task_definition

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_IDS = ["data_54", "data_55", "data_56", "data_57", "data_58", "data_59", "data_60"]

def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class NoSkillsFamilySeedsChunkTest(unittest.TestCase):
    def test_task_yaml_loads_with_explicit_empty_skills(self) -> None:
        settings = Settings.from_env()
        for task_id in TASK_IDS:
            task_path = REPO_ROOT / 'tasks' / f'{task_id}.yaml'
            task = load_task_definition(task_path, settings)
            self.assertEqual(task.task_id, task_id)
            self.assertTrue(task.skills.available_explicit)
            self.assertEqual(task.skills.available, ())

    def test_prompts_stay_natural(self) -> None:
        for task_id in TASK_IDS:
            prompt = (REPO_ROOT / 'tasks' / 'prompts' / f'{task_id}.md').read_text(encoding='utf-8')
            self.assertNotIn('accepted_sources', prompt)
            self.assertNotIn('rejected_sources', prompt)
            self.assertNotIn('accepted source', prompt.lower())
            self.assertNotIn('rejected source', prompt.lower())
            self.assertIn('deliverables', prompt)

    def test_env_builders_and_verifiers_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            for task_id in TASK_IDS:
                env_builder = _load_module(REPO_ROOT / 'tasks' / task_id / 'env_builder.py', f'env_{task_id}')
                verifier = _load_module(REPO_ROOT / 'tasks' / task_id / 'verify_rules.py', f'verify_{task_id}')
                asset_root = tmp_root / 'assets' / task_id
                env_builder.build_asset(asset_root)
                self.assertTrue((asset_root / 'README.txt').exists())
                self.assertTrue((asset_root / 'deliverables' / 'README.md').exists())
                self.assertTrue((asset_root / 'notes' / 'triage_rules.md').exists())
                self.assertTrue(hasattr(verifier, 'score_result'))

if __name__ == '__main__':
    unittest.main()
