from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from nanoclaw.batch_runner import cleanup_environment, parse_run_dir, prepare_environment, resolve_task_specs


class BatchRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        (self.repo_root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_resolve_task_specs_reads_normalized_task(self) -> None:
        task_path = self.repo_root / "tasks" / "data_01.yaml"
        prompt_path = self.repo_root / "tasks" / "prompts" / "data_01.md"
        prompt_path.write_text("Write a report.\n", encoding="utf-8")
        task_path.write_text(
            "\n".join(
                [
                    "id: data_01",
                    "name: Example",
                    "prompts:",
                    "  - prompts/data_01.md",
                    "environment:",
                    "  asset: data_01",
                    "skills:",
                    "  available:",
                    "runtime:",
                    "  model: gpt-4o",
                    "  mode: interactive",
                    "  memory_policy: default",
                    "  approval_mode: reject",
                    "  max_steps: 50",
                    "  temperature: 0.2",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        spec = resolve_task_specs(["tasks/data_01.yaml"], repo_root=self.repo_root)[0]
        self.assertEqual(spec.task_id, "data_01")
        self.assertEqual(spec.asset_name, "data_01")
        self.assertIsNone(spec.builder_path)

    def test_prepare_and_cleanup_environment_from_builder(self) -> None:
        task_id = "data_02"
        task_path = self.repo_root / "tasks" / f"{task_id}.yaml"
        prompt_path = self.repo_root / "tasks" / "prompts" / f"{task_id}.md"
        builder_path = self.repo_root / "tasks" / task_id / "env_builder.py"
        prompt_path.write_text("Read docs/input.txt.\n", encoding="utf-8")
        builder_path.parent.mkdir(parents=True, exist_ok=True)
        builder_path.write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    "base = Path('assets/data_02/docs')",
                    "base.mkdir(parents=True, exist_ok=True)",
                    "base.joinpath('input.txt').write_text('ok\\n', encoding='utf-8')",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        task_path.write_text(
            "\n".join(
                [
                    "id: data_02",
                    "name: Example",
                    "prompts:",
                    "  - prompts/data_02.md",
                    "environment:",
                    "  asset: data_02",
                    "skills:",
                    "  available:",
                    "runtime:",
                    "  model: gpt-4o",
                    "  mode: interactive",
                    "  memory_policy: default",
                    "  approval_mode: reject",
                    "  max_steps: 50",
                    "  temperature: 0.2",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        spec = resolve_task_specs(["tasks/data_02.yaml"], repo_root=self.repo_root)[0]
        asset_dir = prepare_environment(spec, repo_root=self.repo_root)
        self.assertTrue(asset_dir.exists())
        self.assertTrue((asset_dir / "docs" / "input.txt").exists())

        cleanup_environment(spec, repo_root=self.repo_root)
        self.assertFalse(asset_dir.exists())

    def test_parse_run_dir(self) -> None:
        stdout = "Trace: foo\nRun dir: /tmp/example-run\nSummary: summary.json\n"
        self.assertEqual(parse_run_dir(stdout), Path("/tmp/example-run").resolve())


if __name__ == "__main__":
    unittest.main()
