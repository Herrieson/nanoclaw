from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from nanoclaw.evaluation_visualization import (
    build_task_consensus_filter,
    discover_summary_paths,
    load_dataset_manifest_task_ids,
    load_model_metrics,
    render_grouped_bar_chart_svg,
    sort_model_metrics,
)


class EvaluationVisualizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        (self.repo_root / "results").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_summary(self, model_name: str, *, perfect: float, average: float) -> Path:
        model_dir = self.repo_root / "results" / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        summary_path = model_dir / "evaluation_summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "perfect_score_rate": perfect,
                    "average_objective_score": average,
                }
            ),
            encoding="utf-8",
        )
        return summary_path

    def _write_evaluation(
        self,
        model_name: str,
        *,
        rows: list[dict[str, object]],
    ) -> Path:
        model_dir = self.repo_root / "results" / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        evaluation_path = model_dir / "evaluation.json"
        evaluation_path.write_text(
            json.dumps(rows),
            encoding="utf-8",
        )
        return evaluation_path

    def _write_run_summary(self, model_name: str, task_id: str, *, error: str | None = None) -> Path:
        run_dir = self.repo_root / "results" / model_name / task_id / "20260101T000000Z"
        run_dir.mkdir(parents=True, exist_ok=True)
        summary_path = run_dir / "summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "error": error,
                }
            ),
            encoding="utf-8",
        )
        return summary_path

    def test_discovers_and_loads_model_metrics(self) -> None:
        self._write_summary("qwen36p", perfect=75.72, average=87.99)
        self._write_summary("gpt54", perfect=80.0, average=90.5)

        paths = discover_summary_paths(["results/*/evaluation_summary.json"], repo_root=self.repo_root)
        metrics = load_model_metrics(paths)

        self.assertEqual([item.model_name for item in metrics], ["gpt54", "qwen36p"])
        self.assertEqual(metrics[1].perfect_score_rate, 75.72)
        self.assertEqual(metrics[1].average_objective_score, 87.99)

    def test_renders_svg_and_supports_metric_sorting(self) -> None:
        first = self._write_summary("model_a", perfect=55.0, average=70.0)
        second = self._write_summary("model_b", perfect=75.0, average=65.0)

        metrics = load_model_metrics([first, second])
        sorted_metrics = sort_model_metrics(metrics, sort_by="perfect_score_rate")
        svg = render_grouped_bar_chart_svg(sorted_metrics, title="Comparison")

        self.assertEqual([item.model_name for item in sorted_metrics], ["model_b", "model_a"])
        self.assertIn("<svg", svg)
        self.assertIn("Comparison", svg)
        self.assertIn("model_a", svg)
        self.assertIn("model_b", svg)
        self.assertIn("perfect_score_rate", svg)
        self.assertIn("average_objective_score", svg)

    def test_loads_filtered_metrics_from_dataset_manifest(self) -> None:
        self._write_summary("model_a", perfect=99.0, average=99.0)
        self._write_summary("model_b", perfect=88.0, average=88.0)
        self._write_evaluation(
            "model_a",
            rows=[
                {"task_id": "data_keep", "evaluation_status": "evaluated", "objective_score": 100.0},
                {"task_id": "data_drop", "evaluation_status": "evaluated", "objective_score": 0.0},
            ],
        )
        self._write_evaluation(
            "model_b",
            rows=[
                {"task_id": "data_keep", "evaluation_status": "evaluated", "objective_score": 40.0},
                {"task_id": "data_drop", "evaluation_status": "evaluated", "objective_score": 100.0},
            ],
        )
        manifest_path = self.repo_root / "results" / "curation" / "dataset_manifest.jsonl"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps({"task_id": "data_keep"}) + "\n",
            encoding="utf-8",
        )

        task_filter = load_dataset_manifest_task_ids(manifest_path)
        paths = discover_summary_paths(["results/*/evaluation_summary.json"], repo_root=self.repo_root)
        metrics = sort_model_metrics(
            load_model_metrics(paths, task_filter=task_filter),
            sort_by="model",
        )

        self.assertEqual([item.model_name for item in metrics], ["model_a", "model_b"])
        self.assertEqual(metrics[0].perfect_score_rate, 100.0)
        self.assertEqual(metrics[0].average_objective_score, 100.0)
        self.assertEqual(metrics[1].perfect_score_rate, 0.0)
        self.assertEqual(metrics[1].average_objective_score, 40.0)
        svg = render_grouped_bar_chart_svg(
            metrics,
            title="Curated Comparison",
            subtitle="Curated task subset only.",
        )
        self.assertIn("Curated task subset only.", svg)

    def test_excludes_infra_failures_from_denominator_when_requested(self) -> None:
        self._write_summary("model_a", perfect=99.0, average=99.0)
        good_summary = self._write_run_summary("model_a", "data_good")
        infra_summary = self._write_run_summary(
            "model_a",
            "data_infra",
            error="Access denied, please make sure your account is in good standing.",
        )
        max_steps_summary = self._write_run_summary(
            "model_a",
            "data_max_steps",
            error="Agent exceeded max steps (50) without final answer",
        )
        self._write_evaluation(
            "model_a",
            rows=[
                {
                    "task_id": "data_good",
                    "summary_path": str(good_summary),
                    "run_status": "completed",
                    "evaluation_status": "evaluated",
                    "objective_score": 100.0,
                },
                {
                    "task_id": "data_infra",
                    "summary_path": str(infra_summary),
                    "run_status": "failed",
                    "evaluation_status": "skipped_run_not_completed",
                    "objective_score": None,
                },
                {
                    "task_id": "data_max_steps",
                    "summary_path": str(max_steps_summary),
                    "run_status": "failed",
                    "evaluation_status": "skipped_run_not_completed",
                    "objective_score": None,
                },
            ],
        )

        paths = discover_summary_paths(["results/*/evaluation_summary.json"], repo_root=self.repo_root)
        metrics_all = load_model_metrics(paths)
        metrics_excluding_infra = load_model_metrics(paths, exclude_infra_failures=True)

        self.assertEqual(metrics_all[0].perfect_score_rate, 99.0)
        self.assertEqual(metrics_excluding_infra[0].perfect_score_rate, 50.0)
        self.assertEqual(metrics_excluding_infra[0].average_objective_score, 100.0)

    def test_excludes_consensus_all_perfect_and_all_non_perfect_tasks(self) -> None:
        self._write_summary("model_a", perfect=99.0, average=99.0)
        self._write_summary("model_b", perfect=88.0, average=88.0)
        self._write_evaluation(
            "model_a",
            rows=[
                {"task_id": "all_perfect", "evaluation_status": "evaluated", "objective_score": 100.0},
                {"task_id": "all_non_perfect", "evaluation_status": "evaluated", "objective_score": 40.0},
                {"task_id": "mixed", "evaluation_status": "evaluated", "objective_score": 100.0},
            ],
        )
        self._write_evaluation(
            "model_b",
            rows=[
                {"task_id": "all_perfect", "evaluation_status": "evaluated", "objective_score": 100.0},
                {"task_id": "all_non_perfect", "evaluation_status": "evaluated", "objective_score": 20.0},
                {"task_id": "mixed", "evaluation_status": "evaluated", "objective_score": 50.0},
            ],
        )

        paths = discover_summary_paths(["results/*/evaluation_summary.json"], repo_root=self.repo_root)
        consensus_filter = build_task_consensus_filter(
            paths,
            exclude_all_perfect_percent=100,
            exclude_all_non_perfect_percent=100,
        )
        metrics = sort_model_metrics(
            load_model_metrics(paths, exclude_task_ids=consensus_filter.task_ids),
            sort_by="model",
        )

        self.assertEqual(consensus_filter.task_ids, {"all_perfect", "all_non_perfect"})
        self.assertEqual(metrics[0].perfect_score_rate, 100.0)
        self.assertEqual(metrics[0].average_objective_score, 100.0)
        self.assertEqual(metrics[1].perfect_score_rate, 0.0)
        self.assertEqual(metrics[1].average_objective_score, 50.0)


if __name__ == "__main__":
    unittest.main()
