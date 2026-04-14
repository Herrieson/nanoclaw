from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from nanoclaw.config import Settings
from nanoclaw.task_loader import load_task_definition


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_IDS = ["data_52", "data_53"]


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegeneratedSamplesTest(unittest.TestCase):
    def test_docs_explain_user_surface_prompt_vs_implicit_constraints(self) -> None:
        guide = (REPO_ROOT / "doc" / "task_data_guide.md").read_text(encoding="utf-8")
        skills_doc = (REPO_ROOT / "doc" / "task.txt").read_text(encoding="utf-8")
        no_skills_doc = (REPO_ROOT / "doc" / "task_no_skills.txt").read_text(encoding="utf-8")

        self.assertIn("用户表层任务", guide)
        self.assertIn("隐式约束", guide)
        self.assertIn("真实用户", skills_doc)
        self.assertIn("不要把评测要求直接写成用户口吻", skills_doc)
        self.assertIn("真实用户", no_skills_doc)
        self.assertIn("不要把规则校验要求直接写成用户请求", no_skills_doc)

    def test_new_samples_exist_and_prompts_are_natural(self) -> None:
        settings = Settings.from_env()
        for task_id in TASK_IDS:
            task_path = REPO_ROOT / "tasks" / f"{task_id}.yaml"
            prompt_path = REPO_ROOT / "tasks" / "prompts" / f"{task_id}.md"
            task = load_task_definition(task_path, settings)
            self.assertEqual(task.task_id, task_id)
            prompt = prompt_path.read_text(encoding="utf-8")
            self.assertNotIn("accepted_sources", prompt)
            self.assertNotIn("rejected_sources", prompt)
            self.assertNotIn("rejection_reasons", prompt)
            self.assertIn("deliverables", prompt)

    def test_new_samples_build_assets_and_verifiers_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            for task_id in TASK_IDS:
                env_builder = _load_module(REPO_ROOT / "tasks" / task_id / "env_builder.py", f"env_{task_id}")
                asset_root = tmp_root / "assets" / task_id
                env_builder.build_asset(asset_root)
                self.assertTrue((asset_root / "README.txt").exists())
                self.assertTrue((asset_root / "deliverables").exists())

                verify_name = "verify_rules.py" if task_id == "data_53" else "verify.py"
                verifier = _load_module(REPO_ROOT / "tasks" / task_id / verify_name, f"verify_{task_id}")
                self.assertTrue(hasattr(verifier, "score_result"))


if __name__ == "__main__":
    unittest.main()
