from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from nanoclaw.evaluator import EvaluationJudgeConfig
from nanoclaw.workplace_trace_evaluator import (
    evaluate_workplace_trace_run,
    extract_file_blocks,
    load_verifier_bundle,
    summarize_workplace_trace_evaluations,
)


class WorkplaceTraceEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_manifest(self) -> Path:
        manifest_path = self.root / "import_manifest.jsonl"
        manifest_path.write_text(
            json.dumps(
                {
                    "source_task_id": "data_1",
                    "imported_task_id": "data_round_01_0001",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return manifest_path

    def _write_jsonl(self, *, workplace_script: str | None = None, trace_prompt: str | None = None) -> Path:
        workplace_block = ""
        if workplace_script is not None:
            workplace_block = f"""
```python
# scripts/data_1/verify_workplace.py
{workplace_script}
```
"""
        trace_block = ""
        if trace_prompt is not None:
            trace_block = f"""
```markdown
# scripts/data_1/verify_trace.md
{trace_prompt}
```
"""
        raw_output = f"""```yaml
tasks/data_1.yaml
id: data_1
```

```markdown
tasks/prompts/data_1.md
Prompt
```

```python
tasks/data_1/env_builder.py
print("ok")
```
{workplace_block}{trace_block}"""
        jsonl_path = self.root / "new_verifier.jsonl"
        jsonl_path.write_text(json.dumps({"raw_output": raw_output}) + "\n", encoding="utf-8")
        return jsonl_path

    def _create_run(
        self,
        *,
        status: str = "completed",
        error: str | None = None,
    ) -> Path:
        run_dir = self.root / "results" / "model_a" / "data_round_01_0001" / "20260101T000000Z"
        (run_dir / "workspace_after").mkdir(parents=True)
        (run_dir / "workspace_after" / "answer.txt").write_text("done\n", encoding="utf-8")
        (run_dir / "trace.jsonl").write_text('{"type":"tool_call","tool":"python"}\n', encoding="utf-8")
        (run_dir / "final_answer.md").write_text("complete\n", encoding="utf-8")
        (run_dir / "summary.json").write_text(
            json.dumps(
                {
                    "task_id": "data_round_01_0001",
                    "run_id": "20260101T000000Z",
                    "status": status,
                    "result_type": "final_answer" if status == "completed" else "failure",
                    "model": "model-a",
                    "error": error,
                }
            ),
            encoding="utf-8",
        )
        return run_dir

    def _judge_config(self) -> EvaluationJudgeConfig:
        return EvaluationJudgeConfig(
            enabled=True,
            model="judge-model",
            api_key="test-key",
            base_url=None,
            max_attempts=2,
            temperature=0.0,
        )

    def test_extract_file_blocks_keeps_inner_fences_and_script_paths(self) -> None:
        raw_output = """```yaml
tasks/data_1.yaml
id: data_1
```

```markdown
# scripts/data_1/verify_trace.md
Return:
```json
{"score": 100}
```
```
"""
        blocks = extract_file_blocks(raw_output)
        self.assertIn("tasks/data_1.yaml", blocks)
        self.assertIn("scripts/data_1/verify_trace.md", blocks)
        self.assertIn("```json", blocks["scripts/data_1/verify_trace.md"])

    def test_extract_file_blocks_strips_nested_wrapper_fence(self) -> None:
        raw_output = """```yaml
tasks/data_1.yaml
id: data_1
```

```python
# scripts/data_1/verify_workplace.py
```

```python
print("ok")
```
```
"""
        blocks = extract_file_blocks(raw_output)
        self.assertEqual(blocks["scripts/data_1/verify_workplace.py"], 'print("ok")\n')

    def test_extract_file_blocks_supports_single_line_header_paths(self) -> None:
        raw_output = """```yaml tasks/data_1.yaml
id: data_1
```

```python tasks/data_1/verify_rules.py
print("ok")
```
"""
        blocks = extract_file_blocks(raw_output)
        self.assertEqual(blocks["tasks/data_1.yaml"], "id: data_1\n")
        self.assertEqual(blocks["tasks/data_1/verify_rules.py"], 'print("ok")\n')

    def test_load_bundle_accepts_legacy_verify_rules_and_prompt_names(self) -> None:
        manifest_path = self._write_manifest()
        raw_output = """```yaml tasks/data_1.yaml
id: data_1
```

```python tasks/data_1/verify_rules.py
print("ok")
```

```markdown tasks/data_1/verify_prompt.md
Judge trace.
```
"""
        jsonl_path = self.root / "legacy_new_verifier.jsonl"
        jsonl_path.write_text(json.dumps({"raw_output": raw_output}) + "\n", encoding="utf-8")

        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        verifier = bundle.verifiers["data_round_01_0001"]

        self.assertEqual(verifier.workplace_script, 'print("ok")\n')
        self.assertEqual(verifier.trace_prompt, "Judge trace.\n")

    def test_load_bundle_accepts_dual_verified_raw_output(self) -> None:
        manifest_path = self._write_manifest()
        raw_output = """```yaml tasks/data_1.yaml
id: data_1
```

```python scripts/data_1/verify_workplace.py
print("ok")
```
"""
        jsonl_path = self.root / "dual_verified_new_verifier.jsonl"
        jsonl_path.write_text(
            json.dumps({"dual_verified_raw_output": raw_output}) + "\n",
            encoding="utf-8",
        )

        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)

        self.assertEqual(bundle.mapped_record_count, 1)
        self.assertEqual(bundle.verifiers["data_round_01_0001"].workplace_script, 'print("ok")\n')

    def test_workplace_only_evaluation_reads_workplace_score_json(self) -> None:
        manifest_path = self._write_manifest()
        jsonl_path = self._write_jsonl(
            workplace_script="\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('workplace_score.json').write_text(json.dumps({'total_score': 70}), encoding='utf-8')",
                ]
            )
        )
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        run_dir = self._create_run()

        result = evaluate_workplace_trace_run(
            run_dir,
            verifiers=bundle.verifiers,
            components="workplace",
            judge_config=EvaluationJudgeConfig.disabled(),
        )

        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.workplace_score, 70.0)
        self.assertEqual(result.objective_score, 70.0)
        self.assertEqual(result.objective_score_source, "workplace")

    def test_multi_turn_workplace_uses_turn_snapshots(self) -> None:
        manifest_path = self._write_manifest()

        def verifier_script(expected: str) -> str:
            return "\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    f"expected = {expected!r}",
                    "content = Path('answer.txt').read_text(encoding='utf-8').strip()",
                    "score = 100 if content == expected else 0",
                    "Path('workplace_score.json').write_text(json.dumps({'total_score': score}), encoding='utf-8')",
                ]
            )

        raw_output = f"""```yaml
tasks/data_1.yaml
id: data_1
```

```python
# scripts/data_1/verify_turn_1.py
{verifier_script("turn1")}
```

```python
# scripts/data_1/verify_turn_2.py
{verifier_script("turn2")}
```
"""
        jsonl_path = self.root / "multi_turn_new_verifier.jsonl"
        jsonl_path.write_text(json.dumps({"raw_output": raw_output}) + "\n", encoding="utf-8")
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        run_dir = self._create_run()
        (run_dir / "workspace_after" / "answer.txt").write_text("final\n", encoding="utf-8")
        (run_dir / "workspace_after_turn_1").mkdir()
        (run_dir / "workspace_after_turn_1" / "answer.txt").write_text("turn1\n", encoding="utf-8")
        (run_dir / "workspace_after_turn_2").mkdir()
        (run_dir / "workspace_after_turn_2" / "answer.txt").write_text("turn2\n", encoding="utf-8")
        summary_path = run_dir / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["multi_turn"] = True
        summary["turns"] = [
            {"turn": 1, "after_state_dir": "workspace_after_turn_1"},
            {"turn": 2, "after_state_dir": "workspace_after_turn_2"},
        ]
        summary_path.write_text(json.dumps(summary), encoding="utf-8")

        result = evaluate_workplace_trace_run(
            run_dir,
            verifiers=bundle.verifiers,
            components="workplace",
            judge_config=EvaluationJudgeConfig.disabled(),
        )

        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.workplace_score, 100.0)
        self.assertEqual(result.workplace_score_source, "multi_turn_workplace_average")
        self.assertEqual(
            [item["workspace_after_dir"] for item in result.workplace_data["turns"]],
            ["workspace_after_turn_1", "workspace_after_turn_2"],
        )

    def test_workplace_evaluates_failed_max_steps_runs(self) -> None:
        manifest_path = self._write_manifest()
        jsonl_path = self._write_jsonl(
            workplace_script="\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('workplace_score.json').write_text(json.dumps({'total_score': 55}), encoding='utf-8')",
                ]
            )
        )
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        run_dir = self._create_run(
            status="failed",
            error="Agent exceeded max steps (30) without final answer",
        )

        result = evaluate_workplace_trace_run(
            run_dir,
            verifiers=bundle.verifiers,
            components="workplace",
            judge_config=EvaluationJudgeConfig.disabled(),
        )

        self.assertEqual(result.run_status, "failed")
        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.objective_score, 55.0)

    def test_workplace_skips_failed_infra_runs(self) -> None:
        manifest_path = self._write_manifest()
        jsonl_path = self._write_jsonl(
            workplace_script="raise RuntimeError('should not run')"
        )
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        run_dir = self._create_run(
            status="failed",
            error="RateLimitError: Error code: 429 - quota exceeded",
        )

        result = evaluate_workplace_trace_run(
            run_dir,
            verifiers=bundle.verifiers,
            components="workplace",
            judge_config=EvaluationJudgeConfig.disabled(),
        )

        self.assertEqual(result.evaluation_status, "skipped_infra_failure")
        self.assertIsNone(result.objective_score)

    @mock.patch("nanoclaw.workplace_trace_evaluator.OpenAI")
    def test_full_evaluation_averages_workplace_and_trace_scores(self, openai_cls: mock.Mock) -> None:
        manifest_path = self._write_manifest()
        jsonl_path = self._write_jsonl(
            workplace_script="\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('workplace_score.json').write_text(json.dumps({'total_score': 80}), encoding='utf-8')",
                ]
            ),
            trace_prompt="Score trace behavior.",
        )
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        run_dir = self._create_run()
        response = mock.Mock()
        response.choices = [mock.Mock(message=mock.Mock(content='{"score": 60, "reasoning": "ok"}'))]
        client = mock.Mock()
        client.chat.completions.create.return_value = response
        openai_cls.return_value = client

        result = evaluate_workplace_trace_run(
            run_dir,
            verifiers=bundle.verifiers,
            components="full",
            judge_config=self._judge_config(),
        )

        self.assertEqual(result.evaluation_status, "evaluated")
        self.assertEqual(result.workplace_score, 80.0)
        self.assertEqual(result.trace_score, 60.0)
        self.assertEqual(result.objective_score, 70.0)
        self.assertEqual(result.objective_score_source, "workplace_trace_average")

    def test_summary_tracks_component_averages(self) -> None:
        manifest_path = self._write_manifest()
        jsonl_path = self._write_jsonl(
            workplace_script="\n".join(
                [
                    "import json",
                    "from pathlib import Path",
                    "Path('workplace_score.json').write_text(json.dumps({'total_score': 100}), encoding='utf-8')",
                ]
            )
        )
        bundle = load_verifier_bundle([jsonl_path], manifest_path=manifest_path)
        result = evaluate_workplace_trace_run(
            self._create_run(),
            verifiers=bundle.verifiers,
            components="workplace",
            judge_config=EvaluationJudgeConfig.disabled(),
        )
        summary = summarize_workplace_trace_evaluations([result])

        self.assertEqual(summary.scored_runs, 1)
        self.assertEqual(summary.perfect_score_rate, 100.0)
        self.assertEqual(summary.average_workplace_score, 100.0)
        self.assertEqual(summary.average_objective_score, 100.0)


if __name__ == "__main__":
    unittest.main()
