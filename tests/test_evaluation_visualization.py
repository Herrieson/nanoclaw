from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from nanoclaw.evaluation_visualization import (
    discover_summary_paths,
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


if __name__ == "__main__":
    unittest.main()
