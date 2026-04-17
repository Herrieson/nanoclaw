from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest

from nanoclaw.batch_runner import (
    BatchTaskSpec,
    cleanup_environment,
    find_latest_completed_run_dir,
    parse_run_dir,
    partition_task_specs_for_resume,
    prepare_environment,
    resolve_task_specs,
)


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

    def test_find_latest_completed_run_dir_prefers_latest_completed_run(self) -> None:
        task_results_dir = self.repo_root / "results" / "data_03"
        task_results_dir.mkdir(parents=True, exist_ok=True)

        def write_summary(run_id: str, status: str) -> Path:
            run_dir = task_results_dir / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "summary.json").write_text(
                json.dumps({"task_id": "data_03", "run_id": run_id, "status": status}),
                encoding="utf-8",
            )
            return run_dir

        write_summary("20260101T000000Z", "completed")
        write_summary("20260101T000000Z_2", "failed")
        latest_completed = write_summary("20260101T000000Z_10", "completed")

        resolved = find_latest_completed_run_dir(
            "data_03",
            results_dir=self.repo_root / "results",
        )
        self.assertEqual(resolved, latest_completed.resolve())

    def test_partition_task_specs_for_resume_skips_completed_tasks_only(self) -> None:
        task_a_results = self.repo_root / "results" / "data_10" / "20260101T000000Z"
        task_a_results.mkdir(parents=True, exist_ok=True)
        (task_a_results / "summary.json").write_text(
            json.dumps({"task_id": "data_10", "run_id": "20260101T000000Z", "status": "completed"}),
            encoding="utf-8",
        )
        task_b_results = self.repo_root / "results" / "data_11" / "20260101T000000Z"
        task_b_results.mkdir(parents=True, exist_ok=True)
        (task_b_results / "summary.json").write_text(
            json.dumps({"task_id": "data_11", "run_id": "20260101T000000Z", "status": "failed"}),
            encoding="utf-8",
        )

        specs = [
            BatchTaskSpec(
                task_path=self.repo_root / "tasks" / "data_10.yaml",
                task_id="data_10",
                asset_name="data_10",
                builder_path=None,
            ),
            BatchTaskSpec(
                task_path=self.repo_root / "tasks" / "data_11.yaml",
                task_id="data_11",
                asset_name="data_11",
                builder_path=None,
            ),
            BatchTaskSpec(
                task_path=self.repo_root / "tasks" / "data_12.yaml",
                task_id="data_12",
                asset_name="data_12",
                builder_path=None,
            ),
        ]

        pending_specs, reused_run_dirs = partition_task_specs_for_resume(
            specs,
            results_dir=self.repo_root / "results",
        )

        self.assertEqual([spec.task_id for spec in pending_specs], ["data_11", "data_12"])
        self.assertEqual(reused_run_dirs, {"data_10": task_a_results.resolve()})


if __name__ == "__main__":
    unittest.main()
