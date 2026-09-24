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

    def _build_inline_header_payload(self, task_id: str) -> dict[str, object]:
        code_block = "\n".join(
            [
                f"```yaml tasks/{task_id}.yaml",
                f"id: {task_id}",
                "name: Inline Header Example",
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
                f"```markdown tasks/prompts/{task_id}.md",
                "Use docs/input.txt",
                "```",
                f"```python skills/{task_id}/inline_tool.py",
                "print('inline')",
                "```",
            ]
        )
        return {"raw_output": code_block}

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

    def test_unpack_jsonl_records_sorts_by_enhancement_total_qa_score(self) -> None:
        payloads = []
        for task_id, score in [("data_low", 27), ("data_high", 30), ("data_mid", 29)]:
            payload = self._build_payload(task_id)
            payload["enhanced_raw_output"] = payload.pop("raw_output")
            payload["enhancement_qa_result"] = {"total_qa_score": score}
            payloads.append(payload)
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

    def test_unpack_jsonl_records_supports_dual_verified_raw_output(self) -> None:
        payload = self._build_payload("data_01")
        payload["dual_verified_raw_output"] = payload.pop("raw_output")
        self.jsonl_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")

        unpacked = unpack_jsonl_records(self.jsonl_path, output_root=self.unpack_root)

        self.assertEqual(len(unpacked), 1)
        self.assertTrue((self.unpack_root / "record_0001" / "tasks" / "data_01.yaml").exists())

    def test_unpack_jsonl_records_normalizes_bare_prompt_paths(self) -> None:
        payload = {
            "raw_output": "\n".join(
                [
                    "```yaml",
                    "tasks/data_01.yaml",
                    "id: data_01",
                    "prompt: prompts/data_01.md",
                    "asset: data_01",
                    "```",
                    "```markdown",
                    "prompts/data_01.md",
                    "Prompt body",
                    "```",
                ]
            )
        }
        self.jsonl_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")

        unpacked = unpack_jsonl_records(self.jsonl_path, output_root=self.unpack_root)

        self.assertEqual(len(unpacked), 1)
        self.assertTrue(
            (self.unpack_root / "record_0001" / "tasks" / "prompts" / "data_01.md").exists()
        )

    def test_unpack_jsonl_records_supports_enhanced_skill_records_and_manifest_order(self) -> None:
        first = self._build_payload("data_01", total_score=10)
        first["task_id"] = "data_01"
        first["original_scores"] = first.pop("qa_result")
        first["enhanced_raw_output"] = first.pop("raw_output") + "\n" + "\n".join(
            [
                "```markdown",
                "skills/data_01/pdf_reader.md",
                "# PDF Reader",
                "Reads PDFs for data_01.",
                "```",
                "```python",
                "# skills/data_01/pdf_reader.py",
                "print('data_01')",
                "```",
            ]
        )
        second = self._build_payload("data_02", total_score=40)
        second["task_id"] = "data_02"
        second["original_scores"] = second.pop("qa_result")
        second["enhanced_raw_output"] = second.pop("raw_output")
        self.jsonl_path.write_text(
            json.dumps(first, ensure_ascii=False) + "\n" + json.dumps(second, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        unpacked = unpack_jsonl_records(
            [self.jsonl_path],
            output_root=self.unpack_root,
            max_records=2,
            order_task_ids=["data_02", "data_01"],
        )

        self.assertEqual([item.record_id for item in unpacked], ["record_0001", "record_0002"])
        self.assertTrue((self.unpack_root / "record_0001" / "tasks" / "data_02.yaml").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "tasks" / "data_01.yaml").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "skills" / "data_01" / "pdf_reader.md").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "skills" / "data_01" / "pdf_reader.py").exists())

    def test_unpack_jsonl_records_supports_inline_fence_paths_and_manifest_order(self) -> None:
        first = self._build_inline_header_payload("data_01")
        second = self._build_inline_header_payload("data_02")
        self.jsonl_path.write_text(
            json.dumps(first, ensure_ascii=False) + "\n" + json.dumps(second, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        unpacked = unpack_jsonl_records(
            [self.jsonl_path],
            output_root=self.unpack_root,
            max_records=2,
            order_task_ids=["data_02", "data_01"],
        )

        self.assertEqual([item.record_id for item in unpacked], ["record_0001", "record_0002"])
        data_02_yaml = self.unpack_root / "record_0001" / "tasks" / "data_02.yaml"
        self.assertTrue(data_02_yaml.exists())
        self.assertTrue(data_02_yaml.read_text(encoding="utf-8").startswith("id: data_02\n"))
        self.assertTrue((self.unpack_root / "record_0001" / "skills" / "data_02" / "inline_tool.py").exists())
        self.assertTrue((self.unpack_root / "record_0002" / "tasks" / "data_01.yaml").exists())

    def test_unpack_jsonl_records_supports_path_before_fence_for_manifest_order(self) -> None:
        payload = {
            "raw_output": "\n".join(
                [
                    "### 1. `tasks/data_01.yaml`",
                    "```yaml",
                    "id: data_01",
                    "name: Path Before Fence Example",
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
                    "`skills/data_01/path_before_tool.py`",
                    "```python",
                    "print('path before fence')",
                    "```",
                ]
            )
        }
        self.jsonl_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")

        unpacked = unpack_jsonl_records(
            [self.jsonl_path],
            output_root=self.unpack_root,
            max_records=1,
            order_task_ids=["data_01"],
        )

        self.assertEqual(len(unpacked), 1)
        data_01_yaml = self.unpack_root / "record_0001" / "tasks" / "data_01.yaml"
        self.assertTrue(data_01_yaml.exists())
        self.assertTrue(data_01_yaml.read_text(encoding="utf-8").startswith("id: data_01\n"))
        self.assertTrue((self.unpack_root / "record_0001" / "skills" / "data_01" / "path_before_tool.py").exists())


if __name__ == "__main__":
    unittest.main()
