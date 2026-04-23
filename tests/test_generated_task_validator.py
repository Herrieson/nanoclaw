from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from nanoclaw.generated_task_validator import (
    autofix_prompt_repo_asset_paths,
    autofix_verify_rules_runtime_paths,
    collect_task_artifacts,
    quarantine_invalid_task,
    validate_generated_task,
)


class GeneratedTaskValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        (self.repo_root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "assets").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_task(self, task_id: str, *, prompt_body: str = "Use `docs/input.txt`.\n") -> Path:
        prompt_path = self.repo_root / "tasks" / "prompts" / f"{task_id}.md"
        prompt_path.write_text(prompt_body, encoding="utf-8")
        task_path = self.repo_root / "tasks" / f"{task_id}.yaml"
        task_path.write_text(
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
        return task_path

    def test_reports_missing_asset_and_builder(self) -> None:
        task_path = self._write_task("data_480")
        result = validate_generated_task(task_path, repo_root=self.repo_root)
        self.assertEqual([issue.code for issue in result.issues], ["missing_asset_and_builder"])

    def test_reports_empty_builder(self) -> None:
        task_path = self._write_task("data_119")
        builder_path = self.repo_root / "tasks" / "data_119" / "env_builder.py"
        builder_path.parent.mkdir(parents=True, exist_ok=True)
        builder_path.write_text("\n", encoding="utf-8")

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        self.assertEqual([issue.code for issue in result.issues], ["empty_builder"])

    def test_reports_prompt_repo_asset_reference_warning(self) -> None:
        task_path = self._write_task(
            "data_01",
            prompt_body="Read `assets/data_01/raw_exports/transactions.txt`.\n",
        )
        asset_dir = self.repo_root / "assets" / "data_01"
        asset_dir.mkdir(parents=True, exist_ok=True)

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        self.assertEqual([issue.code for issue in result.issues], ["prompt_uses_repo_asset_path"])

    def test_autofix_prompt_repo_asset_reference_rewrites_to_runtime_relative_path(self) -> None:
        task_path = self._write_task(
            "data_01",
            prompt_body=(
                "Read `assets/data_01/raw_exports/transactions.txt`.\n"
                "Save the summary to `assets/data_01/report.md`.\n"
                "Start in `assets/data_01/`.\n"
            ),
        )
        asset_dir = self.repo_root / "assets" / "data_01"
        asset_dir.mkdir(parents=True, exist_ok=True)

        autofix_result = autofix_prompt_repo_asset_paths(task_path, repo_root=self.repo_root)
        self.assertEqual(
            [path.relative_to(self.repo_root).as_posix() for path in autofix_result.changed_files],
            ["tasks/prompts/data_01.md"],
        )

        prompt_text = (self.repo_root / "tasks" / "prompts" / "data_01.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`raw_exports/transactions.txt`", prompt_text)
        self.assertIn("`report.md`", prompt_text)
        self.assertIn("`./`", prompt_text)

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        self.assertEqual(result.issues, ())

    def test_autofix_verify_rules_rewrites_legacy_runtime_paths(self) -> None:
        task_path = self._write_task("data_34")
        verify_path = self.repo_root / "tasks" / "data_34" / "verify_rules.py"
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(
            "\n".join(
                [
                    "target = '/workspace/itinerary.md'",
                    "legacy = 'assets/data_34/verify_result.json'",
                    "source_tree = 'tasks/data_34/verify_result.json'",
                    "joined = os.path.join('assets', 'data_34')",
                    "base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/data_34'))",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (self.repo_root / "assets" / "data_34").mkdir(parents=True, exist_ok=True)

        autofix_result = autofix_verify_rules_runtime_paths(task_path, repo_root=self.repo_root)
        self.assertEqual(
            [path.relative_to(self.repo_root).as_posix() for path in autofix_result.changed_files],
            ["tasks/data_34/verify_rules.py"],
        )
        updated = verify_path.read_text(encoding="utf-8")
        self.assertIn("target = 'itinerary.md'", updated)
        self.assertIn("legacy = 'verify_result.json'", updated)
        self.assertIn("source_tree = 'verify_result.json'", updated)
        self.assertIn('joined = "."', updated)
        self.assertIn('base_dir = "."', updated)

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        self.assertEqual(result.issues, ())

    def test_run_builder_detects_wrong_output_directory(self) -> None:
        task_path = self._write_task("data_316")
        builder_path = self.repo_root / "tasks" / "data_316" / "env_builder.py"
        builder_path.parent.mkdir(parents=True, exist_ok=True)
        builder_path.write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    "wrong = Path('../assets/data_316').resolve()",
                    "wrong.mkdir(parents=True, exist_ok=True)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = validate_generated_task(
            task_path,
            repo_root=self.repo_root,
            run_builder=True,
        )
        self.assertIn("builder_missing_asset_dir", [issue.code for issue in result.issues])

    def test_run_builder_uses_isolated_assets_root_for_wrapped_builder(self) -> None:
        task_path = self._write_task("data_317")
        builder_dir = self.repo_root / "tasks" / "data_317"
        builder_dir.mkdir(parents=True, exist_ok=True)
        builder_path = builder_dir / "env_builder.py"
        impl_path = builder_dir / "_env_builder_impl.py"
        builder_path.write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    "repo_root = Path(__file__).resolve().parents[2]",
                    "asset_dir = repo_root / 'assets' / 'data_317'",
                    "asset_dir.mkdir(parents=True, exist_ok=True)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        impl_path.write_text(
            "\n".join(
                [
                    "from pathlib import Path",
                    "Path('docs').mkdir(parents=True, exist_ok=True)",
                    "Path('docs/input.txt').write_text('ok\\n', encoding='utf-8')",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        isolated_assets_root = self.repo_root / "results" / "demo_model" / ".batch_env" / "assets"
        result = validate_generated_task(
            task_path,
            repo_root=self.repo_root,
            run_builder=True,
            keep_assets=True,
            assets_root=isolated_assets_root,
        )

        self.assertEqual(result.issues, ())
        self.assertTrue((isolated_assets_root / "data_317" / "docs" / "input.txt").exists())
        self.assertFalse((self.repo_root / "assets" / "data_317").exists())

    def test_collect_task_artifacts_includes_prompt_task_and_asset(self) -> None:
        task_path = self._write_task("data_200")
        asset_dir = self.repo_root / "assets" / "data_200"
        asset_dir.mkdir(parents=True, exist_ok=True)
        task_dir = self.repo_root / "tasks" / "data_200"
        task_dir.mkdir(parents=True, exist_ok=True)

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        artifacts = collect_task_artifacts(result, repo_root=self.repo_root)
        self.assertEqual(
            {path.relative_to(self.repo_root).as_posix() for path in artifacts},
            {
                "tasks/data_200.yaml",
                "tasks/prompts/data_200.md",
                "tasks/data_200",
                "assets/data_200",
            },
        )

    def test_quarantine_invalid_task_moves_related_files(self) -> None:
        task_path = self._write_task("data_119")
        builder_path = self.repo_root / "tasks" / "data_119" / "env_builder.py"
        builder_path.parent.mkdir(parents=True, exist_ok=True)
        builder_path.write_text("\n", encoding="utf-8")
        asset_dir = self.repo_root / "assets" / "data_119"
        asset_dir.mkdir(parents=True, exist_ok=True)
        quarantine_root = self.repo_root / ".invalid_generated"

        result = validate_generated_task(task_path, repo_root=self.repo_root)
        moved = quarantine_invalid_task(
            result,
            repo_root=self.repo_root,
            quarantine_root=quarantine_root,
        )

        self.assertFalse(task_path.exists())
        self.assertFalse(builder_path.parent.exists())
        self.assertFalse(asset_dir.exists())
        self.assertTrue((quarantine_root / "tasks" / "data_119.yaml").exists())
        self.assertTrue((quarantine_root / "tasks" / "data_119" / "env_builder.py").exists())
        self.assertTrue((quarantine_root / "tasks" / "prompts" / "data_119.md").exists())
        self.assertTrue((quarantine_root / "assets" / "data_119").exists())
        self.assertEqual(len(moved), 4)


if __name__ == "__main__":
    unittest.main()
