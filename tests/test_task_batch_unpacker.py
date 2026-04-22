from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from nanoclaw.task_batch_unpacker import unpack_jsonl_records
from nanoclaw.task_importer import import_staged_tasks


class TaskBatchUnpackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.unpack_root = Path(self.temp_dir.name) / "unpacked"
        self.jsonl_path = Path(self.temp_dir.name) / "batch.jsonl"
        (self.repo_root / "tasks" / "prompts").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "assets").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _build_payload(self, task_id: str, *, total_score: float | None = None) -> dict[str, object]:
        code_block = "\n".join(
            [
                "```yaml",
                f"tasks/{task_id}.yaml",
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
                "```",
                "```markdown",
                f"tasks/prompts/{task_id}.md",
                "Use docs/input.txt",
                "```",
                "```python",
                f"tasks/{task_id}/env_builder.py",
                f"from pathlib import Path\nPath('assets/{task_id}').mkdir(parents=True, exist_ok=True)",
                "```",
            ]
        )
        payload: dict[str, object] = {"raw_output": code_block}
        if total_score is not None:
            payload["qa_result"] = {"total_score": total_score}
        return payload

    def test_unpack_jsonl_records_preserves_duplicate_task_ids_across_records(self) -> None:
        payload = self._build_payload("data_01")
        self.jsonl_path.write_text(
            json.dumps(payload, ensure_ascii=False) + "\n" + json.dumps(payload, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        unpacked = unpack_jsonl_records(self.jsonl_path, output_root=self.unpack_root)
        self.assertEqual(len(unpacked), 2)
        self.assertTrue((self.unpack_root / "record_0001" / "tasks" / "data_01.yaml").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "tasks" / "data_01.yaml").exists())

        imported = import_staged_tasks(
            self.unpack_root,
            repo_root=self.repo_root,
            round_id="round_batch",
            max_tasks=100,
        )
        self.assertEqual(
            [item.imported_task_id for item in imported],
            ["data_round_batch_0001", "data_round_batch_0002"],
        )

    def test_unpack_jsonl_records_can_select_top_scores_first(self) -> None:
        payloads = [
            self._build_payload("data_low", total_score=10),
            self._build_payload("data_high", total_score=40),
            self._build_payload("data_mid", total_score=20),
        ]
        self.jsonl_path.write_text(
            "".join(json.dumps(payload, ensure_ascii=False) + "\n" for payload in payloads),
            encoding="utf-8",
        )

        unpacked = unpack_jsonl_records(
            self.jsonl_path,
            output_root=self.unpack_root,
            max_records=2,
            sort_by_total_score=True,
        )

        self.assertEqual(len(unpacked), 2)
        self.assertTrue((self.unpack_root / "record_0001" / "tasks" / "data_high.yaml").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "tasks" / "data_mid.yaml").exists())
        self.assertFalse((self.unpack_root / "record_0003").exists())


if __name__ == "__main__":
    unittest.main()
