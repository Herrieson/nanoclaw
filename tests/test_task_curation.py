from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from nanoclaw.task_curation import (
    build_dataset_manifest,
    curate_tasks,
    discover_evaluation_paths,
    load_task_attempts,
)


class TaskCurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        (self.repo_root / "results").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "tasks").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "assets").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_model_eval(
        self,
        model_name: str,
        task_id: str,
        *,
        run_status: str,
        evaluation_status: str,
        objective_score: float | None,
        probe_score: float | None = None,
        error: str | None = None,
    ) -> None:
        model_dir = self.repo_root / "results" / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        task_dir = model_dir / task_id / "20260101T000000Z"
        task_dir.mkdir(parents=True, exist_ok=True)
        summary_path = task_dir / "summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "run_id": "20260101T000000Z",
                    "status": run_status,
                    "error": error,
                }
            ),
            encoding="utf-8",
        )
        evaluation_path = model_dir / "evaluation.json"
        existing = []
        if evaluation_path.exists():
            existing = json.loads(evaluation_path.read_text(encoding="utf-8"))
        existing.append(
            {
                "task_id": task_id,
                "summary_path": str(summary_path),
                "run_status": run_status,
                "evaluation_status": evaluation_status,
                "objective_score": objective_score,
                "probe_score": objective_score if probe_score is None else probe_score,
            }
        )
        evaluation_path.write_text(json.dumps(existing), encoding="utf-8")
        (self.repo_root / "tasks" / f"{task_id}.yaml").write_text("id: x\n", encoding="utf-8")
        (self.repo_root / "assets" / task_id).mkdir(parents=True, exist_ok=True)

    def test_curate_tasks_assigns_all_labels(self) -> None:
        models = ("mock-noop", "real_a", "real_b", "real_c", "real_d")

        for model in models:
            self._write_model_eval(
                model,
                "data_bad_verifier",
                run_status="completed",
                evaluation_status="evaluated",
                objective_score=100.0,
            )
            self._write_model_eval(
                model,
                "data_easy",
                run_status="completed",
                evaluation_status="evaluated",
                objective_score=100.0 if model != "mock-noop" else 0.0,
            )

        for model, score in {
            "mock-noop": 0.0,
            "real_a": 100.0,
            "real_b": 40.0,
            "real_c": 55.0,
            "real_d": 20.0,
        }.items():
            self._write_model_eval(
                model,
                "data_keep",
                run_status="completed",
                evaluation_status="evaluated",
                objective_score=score,
            )

        for model, score in {
            "mock-noop": 0.0,
            "real_a": 20.0,
            "real_b": 10.0,
            "real_c": 0.0,
            "real_d": None,
        }.items():
            self._write_model_eval(
                model,
                "data_broken",
                run_status="failed" if score is None else "completed",
                evaluation_status="skipped_run_not_completed" if score is None else "evaluated",
                objective_score=score,
                error="Agent exceeded max steps (50) without final answer" if score is None else None,
            )

        for model, score in {
            "mock-noop": 0.0,
            "real_a": 35.0,
            "real_b": 45.0,
            "real_c": 50.0,
            "real_d": 59.0,
        }.items():
            self._write_model_eval(
                model,
                "data_ambiguous",
                run_status="completed",
                evaluation_status="evaluated",
                objective_score=score,
            )

        for model, status, score in (
            ("mock-noop", "evaluated", 0.0),
            ("real_a", "evaluated", 100.0),
            ("real_b", "verify_error", None),
            ("real_c", "evaluated", 80.0),
            ("real_d", "evaluated", 60.0),
        ):
            self._write_model_eval(
                model,
                "data_verifier_runtime_issue",
                run_status="completed",
                evaluation_status=status,
                objective_score=score,
            )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=4,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=100,
            sample_salt="test",
        )

        by_task = {record.task_id: record for record in records}
        self.assertEqual(by_task["data_bad_verifier"].label, "drop_bad_verifier")
        self.assertEqual(by_task["data_easy"].label, "easy_pool")
        self.assertTrue(by_task["data_easy"].easy_pool_selected)
        self.assertEqual(by_task["data_keep"].label, "keep")
        self.assertEqual(by_task["data_broken"].label, "drop_broken")
        self.assertEqual(by_task["data_ambiguous"].label, "drop_ambiguous")
        self.assertEqual(
            by_task["data_verifier_runtime_issue"].label,
            "drop_bad_verifier_runtime",
        )
        self.assertEqual(by_task["data_verifier_runtime_issue"].verifier_issue_count, 1)

        manifest = build_dataset_manifest(records, repo_root=self.repo_root)
        self.assertEqual(
            [item["task_id"] for item in manifest],
            ["data_easy", "data_keep"],
        )

    def test_curate_tasks_marks_pending_when_coverage_is_insufficient(self) -> None:
        self._write_model_eval(
            "mock-noop",
            "data_pending",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=0.0,
        )
        self._write_model_eval(
            "real_a",
            "data_pending",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=100.0,
        )
        self._write_model_eval(
            "real_b",
            "data_pending",
            run_status="failed",
            evaluation_status="skipped_run_not_completed",
            objective_score=None,
            error="Error code: 429 - rate limit reached",
        )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=2,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=30,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "pending")

    def test_verifier_runtime_issues_are_dropped_from_dataset(self) -> None:
        self._write_model_eval(
            "mock-noop",
            "data_drop_verifier_runtime",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=0.0,
        )
        self._write_model_eval(
            "real_a",
            "data_drop_verifier_runtime",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=100.0,
        )
        self._write_model_eval(
            "real_b",
            "data_drop_verifier_runtime",
            run_status="completed",
            evaluation_status="verify_error",
            objective_score=None,
        )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=2,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=100,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "drop_bad_verifier_runtime")
        manifest = build_dataset_manifest(records, repo_root=self.repo_root)
        self.assertEqual(manifest, [])

    def test_access_denied_is_treated_as_infra_failure(self) -> None:
        self._write_model_eval(
            "mock-noop",
            "data_access_denied",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=0.0,
        )
        self._write_model_eval(
            "real_a",
            "data_access_denied",
            run_status="failed",
            evaluation_status="skipped_run_not_completed",
            objective_score=None,
            error=(
                "Error code: 400 - {'error': {'message': 'Access denied, please make sure "
                "your account is in good standing. For details, see: "
                "https://help.aliyun.com/zh/model-studio/error-code#overdue-payment', "
                "'type': 'Arrearage', 'code': 'Arrearage'}}"
            ),
        )
        self._write_model_eval(
            "real_b",
            "data_access_denied",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=100.0,
        )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        attempts = attempts_by_task["data_access_denied"]
        denied_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_a")
        successful_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_b")
        self.assertTrue(denied_attempt.infra_failure)
        self.assertFalse(denied_attempt.valid_attempt)
        self.assertFalse(successful_attempt.infra_failure)
        self.assertTrue(successful_attempt.valid_attempt)

        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=2,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=30,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "pending")

    def test_content_filter_is_treated_as_infra_failure(self) -> None:
        self._write_model_eval(
            "mock-noop",
            "data_content_filter",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=0.0,
        )
        self._write_model_eval(
            "real_a",
            "data_content_filter",
            run_status="failed",
            evaluation_status="skipped_run_not_completed",
            objective_score=None,
            error=(
                "BadRequestError: Error code: 400 - {'error': {'message': "
                "\"The response was filtered due to the prompt triggering Azure OpenAI's "
                "content management policy.\", 'code': 'content_filter', "
                "'innererror': {'code': 'ResponsibleAIPolicyViolation', "
                "'content_filter_result': {'self_harm': {'filtered': True, "
                "'severity': 'medium'}}}}}"
            ),
        )
        self._write_model_eval(
            "real_b",
            "data_content_filter",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=100.0,
        )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        attempts = attempts_by_task["data_content_filter"]
        filtered_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_a")
        successful_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_b")
        self.assertTrue(filtered_attempt.infra_failure)
        self.assertFalse(filtered_attempt.valid_attempt)
        self.assertFalse(successful_attempt.infra_failure)
        self.assertTrue(successful_attempt.valid_attempt)

        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=2,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=30,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "pending")

    def test_invalid_function_arguments_is_treated_as_infra_failure(self) -> None:
        self._write_model_eval(
            "mock-noop",
            "data_invalid_function_arguments",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=0.0,
        )
        self._write_model_eval(
            "real_a",
            "data_invalid_function_arguments",
            run_status="failed",
            evaluation_status="skipped_run_not_completed",
            objective_score=None,
            error=(
                "Error code: 400 - {'error': {'message': "
                "'<400> InternalError.Algo.InvalidParameter: The \"function.arguments\" "
                "parameter of the code model must be in JSON format.', "
                "'type': 'invalid_request_error', 'code': 'invalid_parameter_error'}}"
            ),
        )
        self._write_model_eval(
            "real_b",
            "data_invalid_function_arguments",
            run_status="completed",
            evaluation_status="evaluated",
            objective_score=100.0,
        )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        attempts = attempts_by_task["data_invalid_function_arguments"]
        invalid_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_a")
        successful_attempt = next(attempt for attempt in attempts if attempt.model_name == "real_b")
        self.assertTrue(invalid_attempt.infra_failure)
        self.assertFalse(invalid_attempt.valid_attempt)
        self.assertFalse(successful_attempt.infra_failure)
        self.assertTrue(successful_attempt.valid_attempt)

        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=2,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=30,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "pending")

    def test_mock_bad_verifier_detection_uses_probe_score(self) -> None:
        for model, objective_score, probe_score in (
            ("mock-noop", 50.0, 100.0),
            ("real_a", 100.0, 100.0),
            ("real_b", 85.0, 85.0),
            ("real_c", 75.0, 75.0),
            ("real_d", 65.0, 65.0),
        ):
            self._write_model_eval(
                model,
                "data_probe_bad_verifier",
                run_status="completed",
                evaluation_status="evaluated",
                objective_score=objective_score,
                probe_score=probe_score,
            )

        evaluation_paths = discover_evaluation_paths(
            ["results/*/evaluation.json"],
            repo_root=self.repo_root,
        )
        attempts_by_task, _ = load_task_attempts(evaluation_paths)
        records = curate_tasks(
            attempts_by_task,
            mock_models={"mock-noop"},
            min_real_models=4,
            keep_threshold=60.0,
            broken_threshold=30.0,
            easy_pool_keep_percent=30,
            sample_salt="test",
        )

        self.assertEqual(records[0].label, "drop_bad_verifier")
        self.assertTrue(records[0].mock_solved)


if __name__ == "__main__":
    unittest.main()
