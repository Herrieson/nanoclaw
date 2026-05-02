from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "docker" / "codex-runner" / "adapter" / "run_task.py"


def load_adapter_module():
    spec = importlib.util.spec_from_file_location("nanoclaw_codex_adapter", ADAPTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CodexAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.input_dir = self.root / "input"
        self.workspace = self.root / "workspace"
        self.output = self.root / "output"
        self.state = self.root / "state"
        self.input_dir.mkdir()
        self.workspace.mkdir()
        self.output.mkdir()
        self.state.mkdir()
        (self.input_dir / "task.md").write_text("Create report.txt.\n", encoding="utf-8")
        (self.input_dir / "resolved_task.json").write_text(
            json.dumps({"id": "data_test"}) + "\n",
            encoding="utf-8",
        )
        (self.input_dir / "runner_request.json").write_text(
            json.dumps(
                {
                    "task_id": "data_test",
                    "run_id": "20260101T000000Z",
                    "model": "qwen3.5-flash",
                    "turn": None,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.input_dir / "prior_messages.json").write_text(
            json.dumps([{"role": "assistant", "content": "previous answer"}]) + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _argv(self) -> list[str]:
        return [
            "--task",
            str(self.input_dir / "task.md"),
            "--resolved-task",
            str(self.input_dir / "resolved_task.json"),
            "--workspace",
            str(self.workspace),
            "--output",
            str(self.output),
            "--state",
            str(self.state),
        ]

    def test_main_runs_codex_exec_and_writes_outputs(self) -> None:
        adapter = load_adapter_module()
        captured: dict[str, object] = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            captured["stdin"] = kwargs.get("input")
            final_path = self.output / "final_answer.md"
            final_path.write_text("done\n", encoding="utf-8")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({"type": "message", "role": "assistant", "content": "done"}) + "\n",
                stderr="",
            )

        with mock.patch.dict(
            adapter.os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "NANOCLAW_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "NANOCLAW_CODEX_WIRE_API": "responses",
            },
            clear=True,
        ), mock.patch.object(adapter.subprocess, "run", side_effect=fake_run):
            status = adapter.main(self._argv())

        self.assertEqual(status, 0)
        command = captured["command"]
        self.assertEqual(command[0:2], ["codex", "exec"])
        self.assertIn("--json", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn('sandbox_mode="workspace-write"', command)
        self.assertIn("--sandbox", command)
        self.assertIn("workspace-write", command)
        self.assertIn("--output-last-message", command)
        self.assertEqual(command[-1], "-")
        self.assertIn("previous answer", str(captured["stdin"]))
        self.assertEqual((self.output / "final_answer.md").read_text(encoding="utf-8"), "done\n")
        self.assertTrue((self.output / "codex_stdout.jsonl").exists())
        self.assertTrue((self.output / "codex_stderr.log").exists())
        self.assertTrue((self.output / "runner_metadata.json").exists())
        self.assertTrue((self.workspace / "AGENTS.md").exists())

        config = (self.state / "home" / ".codex" / "config.toml").read_text(encoding="utf-8")
        self.assertIn('model = "qwen3.5-flash"', config)
        self.assertIn('model_provider = "nanoclaw"', config)
        self.assertIn('base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"', config)
        self.assertIn('wire_api = "responses"', config)

        trace = (self.output / "trace.jsonl").read_text(encoding="utf-8")
        self.assertIn("codex_started", trace)
        self.assertIn("codex_event", trace)
        self.assertIn("codex_finished", trace)

    def test_main_falls_back_to_stdout_when_last_message_file_missing(self) -> None:
        adapter = load_adapter_module()

        def fake_run(command, **kwargs):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps(
                    {
                        "type": "assistant_message",
                        "message": {"role": "assistant", "content": "stdout final"},
                    }
                )
                + "\n",
                stderr="",
            )

        with mock.patch.dict(adapter.os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True), mock.patch.object(
            adapter.subprocess,
            "run",
            side_effect=fake_run,
        ):
            status = adapter.main(self._argv())

        self.assertEqual(status, 0)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "stdout final\n",
        )
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["final_answer_strategy"], "stdout_jsonl")

    def test_custom_provider_defaults_to_chat_wire_api(self) -> None:
        adapter = load_adapter_module()

        def fake_run(command, **kwargs):
            (self.output / "final_answer.md").write_text("done\n", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with mock.patch.dict(
            adapter.os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "NANOCLAW_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
            clear=True,
        ), mock.patch.object(adapter.subprocess, "run", side_effect=fake_run):
            status = adapter.main(self._argv())

        self.assertEqual(status, 0)
        config = (self.state / "home" / ".codex" / "config.toml").read_text(encoding="utf-8")
        self.assertIn('wire_api = "chat"', config)


if __name__ == "__main__":
    unittest.main()
