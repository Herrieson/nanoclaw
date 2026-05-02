from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import subprocess
import sys

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
        self._write_staged_task_with_prompt_path(task_id, prompt_path=f"prompts/{task_id}.md")

    def _write_staged_task_with_prompt_path(self, task_id: str, *, prompt_path: str) -> None:
        (self.staging_root / "tasks" / f"{task_id}.yaml").write_text(
            "\n".join(
                [
                    f"id: {task_id}",
                    "name: Example",
                    "prompts:",
                    f"  - {prompt_path}",
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

    def _write_cwd_builder_task(self, task_id: str) -> None:
        self._write_staged_task(task_id)
        task_dir = self.staging_root / "tasks" / task_id
        (task_dir / "env_builder.py").write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    f"# cwd is already assets/{task_id}/ during task execution",
                    "base = Path('docs')",
                    "base.mkdir(parents=True, exist_ok=True)",
                    "base.joinpath('input.txt').write_text('ok\\n', encoding='utf-8')",
                    "",
                ]
            ),
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

    def test_import_staged_tasks_accepts_tasks_prompts_style_paths(self) -> None:
        self._write_staged_task_with_prompt_path("data_02", prompt_path="tasks/prompts/data_02.md")

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        self.assertEqual(len(imported), 1)
        new_id = imported[0].imported_task_id
        task_yaml = (self.repo_root / "tasks" / f"{new_id}.yaml").read_text(encoding="utf-8")
        self.assertIn(f"prompts/{new_id}.md", task_yaml)
        self.assertNotIn("tasks/prompts/", task_yaml)

    def test_import_staged_tasks_normalizes_path_prompt_sources(self) -> None:
        (self.staging_root / "tasks" / "data_07.yaml").write_text(
            "\n".join(
                [
                    "name: Example",
                    "prompts:",
                    "  - path: prompts/data_07.md",
                    "environment:",
                    "  asset: data_07",
                    "runtime:",
                    "  model: gpt-4o",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.staging_root / "tasks" / "prompts" / "data_07.md").write_text(
            "Prompt body\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        task_yaml = (self.repo_root / "tasks" / f"{imported[0].imported_task_id}.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"prompts/{imported[0].imported_task_id}.md", task_yaml)
        self.assertNotIn("path:", task_yaml)

    def test_import_staged_tasks_converts_task_local_skills(self) -> None:
        self._write_staged_task("data_06")
        skill_dir = self.staging_root / "skills" / "data_06"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "pdf_reader.md").write_text(
            "# PDF Reader\n\nReads private PDFs for data_06.\n",
            encoding="utf-8",
        )
        (skill_dir / "pdf_reader.py").write_text(
            "TASK_ID = 'data_06'\n",
            encoding="utf-8",
        )
        (skill_dir / "orphan_tool.py").write_text(
            "TASK_ID = 'data_06'\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        new_id = imported[0].imported_task_id
        slug = f"{new_id}-pdf-reader".replace("_", "-")
        task_yaml = (self.repo_root / "tasks" / f"{new_id}.yaml").read_text(encoding="utf-8")
        skill_root = self.repo_root / "skills" / slug

        self.assertIn(slug, task_yaml)
        self.assertTrue((skill_root / "SKILL.md").exists())
        self.assertTrue((skill_root / "pdf_reader.py").exists())
        self.assertIn("description:", (skill_root / "SKILL.md").read_text(encoding="utf-8"))
        script = (skill_root / "pdf_reader.py").read_text(encoding="utf-8")
        self.assertIn(new_id, script)
        self.assertNotIn("data_06", script)

        orphan_slug = f"{new_id}-orphan-tool".replace("_", "-")
        orphan_root = self.repo_root / "skills" / orphan_slug
        self.assertIn(orphan_slug, task_yaml)
        self.assertTrue((orphan_root / "SKILL.md").exists())
        self.assertTrue((orphan_root / "orphan_tool.py").exists())

    def test_import_staged_tasks_normalizes_mapping_prompt_sources(self) -> None:
        (self.staging_root / "tasks" / "data_03.yaml").write_text(
            "\n".join(
                [
                    "name: Example",
                    "prompts:",
                    "  user: tasks/prompts/data_03.md",
                    "environment:",
                    "  asset: data_03",
                    "runtime:",
                    "  model: gpt-4o",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.staging_root / "tasks" / "prompts" / "data_03.md").write_text(
            "Prompt body\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        task_yaml = (self.repo_root / "tasks" / f"{imported[0].imported_task_id}.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"prompts/{imported[0].imported_task_id}.md", task_yaml)
        self.assertNotIn("tasks/prompts/", task_yaml)

    def test_import_staged_tasks_normalizes_main_prompt_sources(self) -> None:
        (self.staging_root / "tasks" / "data_08.yaml").write_text(
            "\n".join(
                [
                    "name: Example",
                    "prompts:",
                    "  main: prompts/data_08.md",
                    "environment:",
                    "  asset: data_08",
                    "runtime:",
                    "  model: gpt-4o",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.staging_root / "tasks" / "prompts" / "data_08.md").write_text(
            "Prompt body\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        task_yaml = (self.repo_root / "tasks" / f"{imported[0].imported_task_id}.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"prompts/{imported[0].imported_task_id}.md", task_yaml)
        self.assertNotIn("main:", task_yaml)

    def test_import_staged_tasks_normalizes_bare_task_id_prompt_sources(self) -> None:
        (self.staging_root / "tasks" / "data_04.yaml").write_text(
            "\n".join(
                [
                    "name: Example",
                    "prompts:",
                    "  - data_04",
                    "environment:",
                    "  asset: data_04",
                    "runtime:",
                    "  model: gpt-4o",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.staging_root / "tasks" / "prompts" / "data_04.md").write_text(
            "Prompt body\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        task_yaml = (self.repo_root / "tasks" / f"{imported[0].imported_task_id}.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"prompts/{imported[0].imported_task_id}.md", task_yaml)
        self.assertNotIn("- data_04", task_yaml)

    def test_import_staged_tasks_resumes_after_existing_round_items(self) -> None:
        self._write_staged_task("data_01")
        self._write_staged_task("data_02")
        self._write_staged_task("data_03")
        (self.repo_root / "tasks" / "data_round_demo_0001.yaml").write_text("id: x\n", encoding="utf-8")
        (self.repo_root / "tasks" / "data_round_demo_0002.yaml").write_text("id: y\n", encoding="utf-8")

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0].source_task_id, "data_03")
        self.assertEqual(imported[0].imported_task_id, "data_round_demo_0003")

    def test_import_staged_tasks_wraps_cwd_relative_builder(self) -> None:
        self._write_cwd_builder_task("data_05")

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        new_id = imported[0].imported_task_id
        builder_path = self.repo_root / "tasks" / new_id / "env_builder.py"
        impl_path = self.repo_root / "tasks" / new_id / "_env_builder_impl.py"

        self.assertTrue(impl_path.exists())
        self.assertIn(f'assets" / "{new_id}"', builder_path.read_text(encoding="utf-8"))

        subprocess.run(
            [sys.executable, str(builder_path)],
            cwd=self.repo_root,
            check=True,
        )

        self.assertTrue((self.repo_root / "assets" / new_id / "docs" / "input.txt").exists())

    def test_import_staged_tasks_skips_existing_ids_when_allocating(self) -> None:
        self._write_staged_task("data_01")
        (self.repo_root / "tasks" / "prompts" / "data_round_demo_0001.md").write_text(
            "occupied\n",
            encoding="utf-8",
        )

        imported = import_staged_tasks(
            self.staging_root,
            repo_root=self.repo_root,
            round_id="round_demo",
            max_tasks=100,
        )

        self.assertEqual(imported[0].imported_task_id, "data_round_demo_0002")


if __name__ == "__main__":
    unittest.main()
