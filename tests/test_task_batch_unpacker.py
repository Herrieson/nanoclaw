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

    def test_unpack_jsonl_records_preserves_duplicate_task_ids_across_records(self) -> None:
        code_block = "\n".join(
            [
                "```yaml",
                "tasks/data_01.yaml",
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
                "  max_steps: 30",
                "  temperature: 0.2",
                "```",
                "```markdown",
                "tasks/prompts/data_01.md",
                "Use docs/input.txt",
                "```",
                "```python",
                "tasks/data_01/env_builder.py",
                "from pathlib import Path",
                "Path('assets/data_01').mkdir(parents=True, exist_ok=True)",
                "```",
            ]
        )
        payload = {"raw_output": code_block}
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


if __name__ == "__main__":
    unittest.main()
