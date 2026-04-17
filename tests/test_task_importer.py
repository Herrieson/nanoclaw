from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nanoclaw.task_importer import import_staged_tasks


class TaskImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.staging_root = Path(self.temp_dir.name) / "staging"
        (self.repo_root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "assets").mkdir(parents=True, exist_ok=True)
        (self.staging_root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_staged_task(self, task_id: str) -> None:
        (self.staging_root / "tasks" / f"{task_id}.yaml").write_text(
            "\n".join(
                [
                    f"id: {task_id}",
                    "name: Example",
                    "prompts:",
                    f"  - prompts/{task_id}.md",
                    "environment:",
                    f"  asset: {task_id}",
                    "skills:",
                    "  available:",
                    "runtime:",
                    "  model: gpt-4o",
                    "  mode: interactive",
                    "  memory_policy: default",
                    "  approval_mode: reject",
                    "  max_steps: 30",
                    "  temperature: 0.2",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.staging_root / "tasks" / "prompts" / f"{task_id}.md").write_text(
            f"Use `assets/{task_id}/docs/input.txt`.\n",
            encoding="utf-8",
        )
        task_dir = self.staging_root / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "env_builder.py").write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    f"base = Path('assets/{task_id}/docs')",
                    "base.mkdir(parents=True, exist_ok=True)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (task_dir / "verify_rules.py").write_text(
            f"target = 'assets/{task_id}/report.txt'\n",
            encoding="utf-8",
        )

    def test_import_staged_tasks_rewrites_task_ids_and_prompt_paths(self) -> None:
        self._write_staged_task("data_01")

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        self.assertEqual(len(imported), 1)
        new_id = imported[0].imported_task_id
        self.assertEqual(new_id, "data_round_demo_0001")
        task_yaml = (self.repo_root / "tasks" / f"{new_id}.yaml").read_text(encoding="utf-8")
        prompt = (self.repo_root / "tasks" / "prompts" / f"{new_id}.md").read_text(encoding="utf-8")
        builder = (self.repo_root / "tasks" / new_id / "env_builder.py").read_text(encoding="utf-8")
        verify = (self.repo_root / "tasks" / new_id / "verify_rules.py").read_text(encoding="utf-8")

        self.assertIn(f"id: {new_id}", task_yaml)
        self.assertIn(f"asset: {new_id}", task_yaml)
        self.assertIn(f"prompts/{new_id}.md", task_yaml)
        self.assertIn("`docs/input.txt`", prompt)
        self.assertIn(new_id, builder)
        self.assertIn("target = 'report.txt'", verify)

    def test_import_staged_tasks_skips_existing_ids_when_allocating(self) -> None:
        self._write_staged_task("data_01")
        (self.repo_root / "tasks" / "data_round_demo_0001.yaml").write_text("id: x\n", encoding="utf-8")

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        self.assertEqual(imported[0].imported_task_id, "data_round_demo_0002")


if __name__ == "__main__":
    unittest.main()
