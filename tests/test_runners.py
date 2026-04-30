from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nanoclaw.config import Settings
from nanoclaw.runners import DockerRunner, RunnerProfile, RunnerRequest, load_runner_profile


class RunnerProfileTest(unittest.TestCase):
    def test_loads_docker_runner_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile_path = Path(tmp) / "openclaw.yaml"
            profile_path.write_text(
                "\n".join(
                    [
                        "id: openclaw",
                        "type: docker",
                        "image: nanoclaw-runner-openclaw:test",
                        "command:",
                        "  - /adapter/run_task",
                        "timeout_seconds: 120",
                        "network: bridge",
                        "env:",
                        "  pass:",
                        "    - OPENAI_API_KEY",
                        "  set:",
                        "    FRAMEWORK: openclaw",
                        "resources:",
                        "  cpus: '2'",
                        "  memory: 4g",
                        "  pids_limit: 256",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            profile = load_runner_profile(profile_path)

        self.assertEqual(profile.profile_id, "openclaw")
        self.assertEqual(profile.runner_type, "docker")
        self.assertEqual(profile.image, "nanoclaw-runner-openclaw:test")
        self.assertEqual(profile.command, ("/adapter/run_task",))
        self.assertEqual(profile.timeout_seconds, 120)
        self.assertEqual(profile.network, "bridge")
        self.assertEqual(profile.env_pass, ("OPENAI_API_KEY",))
        self.assertEqual(profile.env_set, {"FRAMEWORK": "openclaw"})
        self.assertEqual(profile.cpus, "2")
        self.assertEqual(profile.memory, "4g")
        self.assertEqual(profile.pids_limit, 256)


class DockerRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.workspace = self.root / "workspace"
        self.run_dir = self.root / "run"
        self.workspace.mkdir()
        self.run_dir.mkdir()
        self.settings = Settings(
            model="gpt-4o",
            api_key="test",
            base_url="http://example.invalid",
            workspace_dir=self.workspace,
            prompt_dir=self.workspace / "prompts" / "official",
            prompt_files=("docs/reference/templates/AGENTS.md",),
            workspace_context_files=("TEAM_STYLE.md",),
            extra_skill_dirs=(),
            run_mode="interactive",
            memory_policy="default",
            approval_mode="reject",
            session_max_messages=10,
            session_max_chars=1000,
            max_steps=12,
            temperature=0.2,
        )
        (self.workspace / "TEAM_STYLE.md").write_text("Be precise.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_docker_runner_contract_with_fake_docker(self) -> None:
        profile = RunnerProfile(
            profile_id="fake-openclaw",
            runner_type="docker",
            image="nanoclaw-runner-openclaw:test",
            command=("/adapter/run_task",),
            network="bridge",
            timeout_seconds=30,
            env_pass=("OPENAI_API_KEY",),
            env_set={"FRAMEWORK": "openclaw"},
            cpus="2",
            memory="4g",
            pids_limit=128,
        )
        commands: list[list[str]] = []
        output_dir = self.run_dir / "runner_output"

        def fake_docker(
            command: list[str],
            timeout: float | None,
        ) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            action = command[1]
            if action == "create":
                return subprocess.CompletedProcess(command, 0, "container-123\n", "")
            if action == "start":
                return subprocess.CompletedProcess(command, 0, "container-123\n", "")
            if action == "wait":
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "final_answer.md").write_text("Done.\n", encoding="utf-8")
                (output_dir / "trace.jsonl").write_text(
                    json.dumps({"type": "assistant_message", "content": "Done."}) + "\n",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, "0\n", "")
            if action == "logs":
                return subprocess.CompletedProcess(command, 0, "stdout\n", "stderr\n")
            if action == "inspect":
                return subprocess.CompletedProcess(command, 0, '[{"Id": "container-123"}]\n', "")
            if action == "rm":
                return subprocess.CompletedProcess(command, 0, "", "")
            raise AssertionError(f"unexpected docker command: {command}")

        request = RunnerRequest(
            task_id="data_01",
            run_id="20260101T000000Z",
            prompt="Write the answer.",
            resolved_task={"id": "data_01"},
            settings=self.settings,
            workspace_dir=self.workspace,
            run_dir=self.run_dir,
            input_dir=self.run_dir / "runner_input",
            output_dir=output_dir,
            state_dir=self.run_dir / "runner_state",
            trace_path=self.run_dir / "trace.jsonl",
            approval_log_path=self.run_dir / "approval_log.jsonl",
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret"}, clear=False):
            result = DockerRunner(profile, command_runner=fake_docker).run(request)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.final_answer, "Done.\n")
        self.assertEqual(result.workspace_context_files, ("TEAM_STYLE.md",))
        self.assertEqual(result.runner_metadata["container_id"], "container-123")
        self.assertEqual(result.runner_metadata["exit_code"], 0)
        self.assertEqual(result.runner_metadata["image"], "nanoclaw-runner-openclaw:test")
        self.assertTrue((request.input_dir / "task.md").exists())
        self.assertTrue((request.input_dir / "resolved_task.json").exists())
        self.assertEqual(
            json.loads((request.trace_path).read_text(encoding="utf-8").strip())["type"],
            "assistant_message",
        )
        self.assertEqual((self.run_dir / "container_stdout.log").read_text(encoding="utf-8"), "stdout\n")
        self.assertEqual((self.run_dir / "container_stderr.log").read_text(encoding="utf-8"), "stderr\n")

        create_command = commands[0]
        self.assertIn("--network", create_command)
        self.assertIn("bridge", create_command)
        self.assertIn("--cpus", create_command)
        self.assertIn("2", create_command)
        self.assertIn("--memory", create_command)
        self.assertIn("4g", create_command)
        self.assertIn("--pids-limit", create_command)
        self.assertIn("128", create_command)
        self.assertIn("-e", create_command)
        self.assertIn("OPENAI_API_KEY", create_command)
        self.assertIn("FRAMEWORK=openclaw", create_command)
        self.assertIn("nanoclaw-runner-openclaw:test", create_command)
        self.assertIn("/adapter/run_task", create_command)


if __name__ == "__main__":
    unittest.main()
