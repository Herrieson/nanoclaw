from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nanoclaw.config import Settings
from nanoclaw.task_loader import load_task_definition


class TaskLoaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.settings = Settings(
            model="gpt-4o",
            api_key="test",
            base_url="http://example.invalid",
            workspace_dir=self.root / "workspace",
            prompt_dir=self.root / "workspace" / "prompts" / "official",
            prompt_files=("docs/reference/templates/AGENTS.md",),
            workspace_context_files=("SOUL.md",),
            extra_skill_dirs=(),
            run_mode="interactive",
            memory_policy="default",
            session_max_messages=10,
            session_max_chars=1000,
            max_steps=12,
            temperature=0.2,
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_loads_legacy_task_schema(self) -> None:
        task_path = self.root / "legacy.yaml"
        prompt_path = self.root / "prompt.md"
        prompt_path.write_text("Legacy task prompt.\n", encoding="utf-8")
        task_path.write_text(
            "\n".join(
                [
                    "id: legacy",
                    "asset: empty",
                    "task:",
                    "  task_file: prompt.md",
                    "skills:",
                    "  include:",
                    "    - tutorial-brief-writer",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        task = load_task_definition(task_path, self.settings)

        self.assertEqual(task.task_id, "legacy")
        self.assertEqual(task.asset, "empty")
        self.assertEqual(task.prompt.strip(), "Legacy task prompt.")
        self.assertEqual(task.prompt_sources, (str(prompt_path.resolve()),))
        self.assertEqual(task.skills.include, ("tutorial-brief-writer",))
        self.assertEqual(task.skills.available, ())

    def test_loads_prompt_environment_and_skill_pool_schema(self) -> None:
        prompt_a = self.root / "prompts" / "intro.md"
        prompt_b = self.root / "prompts" / "body.md"
        prompt_a.parent.mkdir(parents=True)
        prompt_a.write_text("Intro prompt.\n", encoding="utf-8")
        prompt_b.write_text("Body prompt.\n", encoding="utf-8")
        task_path = self.root / "modern.yaml"
        task_path.write_text(
            "\n".join(
                [
                    "id: modern",
                    "prompts:",
                    "  files:",
                    "    - prompts/intro.md",
                    "    - prompts/body.md",
                    "  inline:",
                    "    - Extra constraint.",
                    "environment:",
                    "  asset: tutorial_workspace_brief",
                    "  workspace_context_files:",
                    "    - TEAM_STYLE.md",
                    "skills:",
                    "  available:",
                    "    - tutorial-brief-writer",
                    "    - memory-preference-checker",
                    "runtime:",
                    "  memory_policy: strict",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        task = load_task_definition(task_path, self.settings)

        self.assertEqual(task.asset, "tutorial_workspace_brief")
        self.assertEqual(
            task.runtime.workspace_context_files,
            ("TEAM_STYLE.md",),
        )
        self.assertEqual(
            task.skills.available,
            ("tutorial-brief-writer", "memory-preference-checker"),
        )
        self.assertEqual(task.skills.include, ())
        self.assertIn("Intro prompt.", task.prompt)
        self.assertIn("Body prompt.", task.prompt)
        self.assertIn("Extra constraint.", task.prompt)
        self.assertEqual(len(task.prompt_sources), 3)


if __name__ == "__main__":
    unittest.main()
