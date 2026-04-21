from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from nanoclaw.evaluator import evaluate_run, summarize_evaluations


class EvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        (self.repo_root / "tasks").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "results").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_run(self, task_id: str, *, status: str = "completed") -> Path:
        task_dir = self.repo_root / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        run_dir = self.repo_root / "results" / task_id / "20260101T000000Z"
        (run_dir / "workspace_after").mkdir(parents=True, exist_ok=True)
        summary = {
            "task_id": task_id,
            "run_id": "20260101T000000Z",
            "status": status,
            "result_type": "final_answer" if status == "completed" else "failure",
        }
        (run_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        return run_dir

    def test_evaluate_run_supports_repo_asset_style_verify_script(self) -> None:
        run_dir = self._create_run("data_03")
        target = run_dir / "workspace_after" / "trip_prep" / "shopping_list.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {
                    "total_cost": 26.5,
                    "items": {
                        "sausages": 7,
                        "tortillas": 10,
                        "beef": 2,
                        "salsa": 1,
                    },
                }
            ),
            encoding="utf-8",
        )
        verify_script = self.repo_root / "tasks" / "data_03" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "import os",
                    "target = 'assets/data_03/trip_prep/shopping_list.json'",
                    "result = {'file_exists': os.path.exists(target), 'total_cost_correct': False, 'items_correct': False}",
                    "if result['file_exists']:",
                    "    data = json.load(open(target))",
                    "    result['total_cost_correct'] = data.get('total_cost') == 26.5",
                    "    result['items_correct'] = data.get('items', {}).get('beef') == 2",
                    "with open('verify_result.json', 'w') as f:",
                    "    json.dump(result, f)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 100.0)
        self.assertEqual(result.objective_score_source, "boolean_ratio")

    def test_evaluate_run_supports_absolute_workspace_verify_script(self) -> None:
        run_dir = self._create_run("data_34")
        target = run_dir / "workspace_after" / "itinerary.md"
        target.write_text("ok\n", encoding="utf-8")
        verify_script = self.repo_root / "tasks" / "data_34" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "import os",
                    "target = '/workspace/itinerary.md'",
                    "result = {'success': os.path.exists(target)}",
                    "with open('/workspace/verify_result.json', 'w') as f:",
                    "    json.dump(result, f)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 100.0)
        self.assertEqual(result.objective_score_source, "success")

    def test_evaluate_run_supports_stdout_only_verify_script(self) -> None:
        run_dir = self._create_run("data_400")
        target = run_dir / "workspace_after" / "urgent_patrols.json"
        target.write_text("[]\n", encoding="utf-8")
        verify_script = self.repo_root / "tasks" / "data_400" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "print(json.dumps({'score': 80, 'success': True}))",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 80.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_normalizes_fractional_verify_scores_to_percent(self) -> None:
        run_dir = self._create_run("data_401")
        verify_script = self.repo_root / "tasks" / "data_401" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "print(json.dumps({'score': 1.0}))",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 100.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_normalizes_partial_fractional_verify_scores_to_percent(self) -> None:
        run_dir = self._create_run("data_402")
        verify_script = self.repo_root / "tasks" / "data_402" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "print(json.dumps({'score': 0.5}))",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 50.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_supports_pretty_printed_stdout_json(self) -> None:
        run_dir = self._create_run("data_262")
        target = run_dir / "workspace_after" / "assets" / "data_262"
        target.mkdir(parents=True, exist_ok=True)
        (target / "final_schedule.json").write_text("{}\n", encoding="utf-8")
        verify_script = self.repo_root / "tasks" / "data_262" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "print(json.dumps({'file_exists': True, 'json_valid': True, 'correct_data': False}, indent=2))",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 66.67)
        self.assertEqual(result.objective_score_source, "boolean_ratio")

    def test_evaluate_run_supports_verify_output_written_under_tasks_dir(self) -> None:
        run_dir = self._create_run("data_422")
        target = run_dir / "workspace_after" / "assets" / "data_422"
        target.mkdir(parents=True, exist_ok=True)
        (target / "report.txt").write_text("ok\n", encoding="utf-8")
        verify_script = self.repo_root / "tasks" / "data_422" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "with open('tasks/data_422/verify_result.json', 'w') as f:",
                    "    json.dump({'score': 55}, f)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 55.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_supports_verify_script_using___file___based_assets_path(self) -> None:
        run_dir = self._create_run("data_450")
        target = run_dir / "workspace_after" / "eco_summary.txt"
        target.write_text("BIN-004 345.6\n", encoding="utf-8")
        verify_script = self.repo_root / "tasks" / "data_450" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "import os",
                    "base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/data_450'))",
                    "with open(os.path.join(base_dir, 'verify_result.json'), 'w') as f:",
                    "    json.dump({'score': 90}, f)",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 90.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_supports_verify_function_returning_dict(self) -> None:
        run_dir = self._create_run("data_465")
        target = run_dir / "workspace_after" / "final_report.json"
        target.write_text(
            json.dumps(
                {
                    "total_spend": 148000,
                    "most_expensive_item": "Ritmo de la Tierra",
                    "projected_increase": 23000,
                }
            ),
            encoding="utf-8",
        )
        verify_script = self.repo_root / "tasks" / "data_465" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "def verify():",
                    "    data = json.load(open('final_report.json'))",
                    "    return {'score': 100 if data.get('total_spend') == 148000 else 0}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 100.0)
        self.assertEqual(result.objective_score_source, "verify_score")

    def test_evaluate_run_skips_failed_runs(self) -> None:
        run_dir = self._create_run("data_500", status="failed")
        verify_script = self.repo_root / "tasks" / "data_500" / "verify_rules.py"
        verify_script.write_text("raise RuntimeError('should not run')\n", encoding="utf-8")

        result = evaluate_run(run_dir, repo_root=self.repo_root)
        self.assertEqual(result.evaluation_status, "skipped_run_not_completed")
        self.assertIsNone(result.objective_score)
        self.assertEqual(result.run_status, "failed")

    def test_summarize_evaluations_computes_benchmark_score(self) -> None:
        run_dir_ok = self._create_run("data_501")
        verify_script = self.repo_root / "tasks" / "data_501" / "verify_rules.py"
        verify_script.write_text(
            "\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('verify_result.json').write_text(json.dumps({'score': 80}), encoding='utf-8')",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        run_dir_failed = self._create_run("data_502", status="failed")

        result_ok = evaluate_run(run_dir_ok, repo_root=self.repo_root)
        result_failed = evaluate_run(run_dir_failed, repo_root=self.repo_root)
        summary = summarize_evaluations([result_ok, result_failed])

        self.assertEqual(summary.total_runs, 2)
        self.assertEqual(summary.completed_runs, 1)
        self.assertEqual(summary.skipped_incomplete_runs, 1)
        self.assertEqual(summary.evaluated_runs, 1)
        self.assertEqual(summary.scored_runs, 1)
        self.assertEqual(summary.perfect_score_runs, 0)
        self.assertEqual(summary.perfect_score_rate, 0.0)
        self.assertEqual(summary.run_success_rate, 50.0)
        self.assertEqual(summary.average_objective_score, 80.0)
        self.assertEqual(summary.benchmark_score, 40.0)

    def test_summarize_evaluations_tracks_perfect_score_rate(self) -> None:
        run_dir_a = self._create_run("data_503")
        verify_script_a = self.repo_root / "tasks" / "data_503" / "verify_rules.py"
        verify_script_a.write_text(
            "\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('verify_result.json').write_text(json.dumps({'score': 100}), encoding='utf-8')",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        run_dir_b = self._create_run("data_504")
        verify_script_b = self.repo_root / "tasks" / "data_504" / "verify_rules.py"
        verify_script_b.write_text(
            "\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('verify_result.json').write_text(json.dumps({'score': 40}), encoding='utf-8')",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result_a = evaluate_run(run_dir_a, repo_root=self.repo_root)
        result_b = evaluate_run(run_dir_b, repo_root=self.repo_root)
        summary = summarize_evaluations([result_a, result_b])

        self.assertEqual(summary.perfect_score_runs, 1)
        self.assertEqual(summary.perfect_score_rate, 50.0)


if __name__ == "__main__":
    unittest.main()
