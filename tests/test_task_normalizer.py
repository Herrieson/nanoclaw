from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import yaml

from nanoclaw.config import Settings
from nanoclaw.task_loader import load_task_definition
from nanoclaw.task_normalizer import normalize_task_file


class TaskNormalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_normalize_adds_prompts_and_strips_assets_prefix(self) -> None:
        task_path = self.root / "tasks" / "data_01.yaml"
        prompt_path = self.root / "tasks" / "prompts" / "data_01.md"
        prompt_path.write_text("Write `deliverables/report.md`.\n", encoding="utf-8")
        task_path.write_text(
            "\n".join(
                [
                    "id: data_01",
                    "name: Sample Task",
                    "description: Example task",
                    "environment:",
                    "  asset: assets/data_01",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = normalize_task_file(task_path, create_backup=False)
        self.assertTrue(result.changed)

        normalized_text = task_path.read_text(encoding="utf-8")
        payload = yaml.safe_load(normalized_text)
        self.assertEqual(payload["prompts"], ["prompts/data_01.md"])
        self.assertEqual(payload["environment"]["asset"], "data_01")
        self.assertEqual(payload["skills"], {"available": None})
        self.assertEqual(payload["runtime"]["model"], "gpt-4o")
        self.assertEqual(payload["runtime"]["approval_mode"], "reject")
        self.assertEqual(payload["runtime"]["max_steps"], 30)
        self.assertEqual(payload["runtime"]["temperature"], 0.2)
        self.assertNotIn("x_legacy", payload)
        self.assertIn("skills:\n  available:\n", normalized_text)

        task = load_task_definition(task_path, Settings.from_env())
        self.assertEqual(task.task_id, "data_01")
        self.assertEqual(task.asset, "data_01")
        self.assertIn("deliverables/report.md", task.prompt)

    def test_normalize_environment_assets_list_to_asset_name(self) -> None:
        task_path = self.root / "tasks" / "data_87.yaml"
        prompt_path = self.root / "tasks" / "prompts" / "data_87.md"
        prompt_path.write_text("Read `docs/input.json`.\n", encoding="utf-8")
        task_path.write_text(
            "\n".join(
                [
                    "id: data_87",
                    "name: Legacy Asset Layout",
                    "environment:",
                    "  image: python:3.9-slim",
                    "  assets:",
                    "    - source: assets/data_87/",
                    "      destination: /workspace/",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        normalize_task_file(task_path, create_backup=False)

        normalized_text = task_path.read_text(encoding="utf-8")
        payload = yaml.safe_load(normalized_text)
        self.assertEqual(payload["environment"]["asset"], "data_87")
        self.assertEqual(payload["prompts"], ["prompts/data_87.md"])
        self.assertEqual(payload["skills"], {"available": None})
        self.assertEqual(payload["runtime"]["mode"], "interactive")
        self.assertEqual(payload["runtime"]["memory_policy"], "default")
        self.assertEqual(payload["runtime"]["approval_mode"], "reject")
        self.assertNotIn("x_legacy", payload)
        self.assertIn("skills:\n  available:\n", normalized_text)

        task = load_task_definition(task_path, Settings.from_env())
        self.assertEqual(task.asset, "data_87")
        self.assertIn("docs/input.json", task.prompt)


if __name__ == "__main__":
    unittest.main()
