from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "docker" / "hermes-runner" / "adapter" / "run_task.py"


class HermesAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.input_dir = self.root / "input"
        self.workspace = self.root / "workspace"
        self.output = self.root / "output"
        self.state = self.root / "state"
        self.fake_bin = self.root / "bin"
        for path in [
            self.input_dir,
            self.workspace,
            self.output,
            self.state,
            self.fake_bin,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        (self.input_dir / "task.md").write_text("Do the Hermes thing.\n", encoding="utf-8")
        (self.input_dir / "resolved_task.json").write_text(
            json.dumps({"id": "task_hermes"}) + "\n",
            encoding="utf-8",
        )
        (self.input_dir / "runner_request.json").write_text(
            json.dumps(
                {
                    "task_id": "task_hermes",
                    "run_id": "run_hermes",
                    "turn": None,
                    "model": "gpt-4o",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.input_dir / "prior_messages.json").write_text("[]\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_runs_hermes_oneshot_and_writes_runner_contract_outputs(self) -> None:
        self._write_fake_hermes(
            """
            printf '%s\\n' "$PWD" > "$FAKE_HERMES_CWD_FILE"
            printf '%s\\n' "$HERMES_HOME" > "$FAKE_HERMES_HOME_FILE"
            for arg in "$@"; do printf '%s\\n' "$arg"; done > "$FAKE_HERMES_ARGS_FILE"
            printf '%s\\n' 'Hermes final answer.'
            """
        )

        result = self._run_adapter()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "Hermes final answer.\n",
        )
        self.assertEqual(
            (self.output / "hermes_stdout.log").read_text(encoding="utf-8"),
            "Hermes final answer.\n",
        )
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["framework"], "hermes-agent")
        self.assertEqual(metadata["mode"], "oneshot")
        self.assertEqual(metadata["final_answer_strategy"], "stdout")

        args = (self.root / "hermes_args.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(args[:2], ["-z", "Do the Hermes thing."])
        self.assertIn("--model", args)
        self.assertIn("gpt-4o", args)
        self.assertEqual(
            (self.root / "hermes_cwd.txt").read_text(encoding="utf-8").strip(),
            str(self.workspace),
        )
        self.assertEqual(
            (self.root / "hermes_home.txt").read_text(encoding="utf-8").strip(),
            str(self.state),
        )

        trace_events = [
            json.loads(line)
            for line in (self.output / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(trace_events[0]["type"], "adapter_started")
        self.assertEqual(trace_events[-1]["type"], "hermes_finished")
        self.assertEqual(trace_events[-1]["exit_code"], 0)

    def test_toolsets_switch_to_chat_quiet_mode(self) -> None:
        self._write_fake_hermes(
            """
            for arg in "$@"; do printf '%s\\n' "$arg"; done > "$FAKE_HERMES_ARGS_FILE"
            printf '%s\\n' 'Chat mode answer.'
            """
        )

        result = self._run_adapter(
            {
                "NANOCLAW_HERMES_TOOLSETS": "shell,edit",
                "NANOCLAW_HERMES_PROVIDER": "openrouter",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        args = (self.root / "hermes_args.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(args[:4], ["chat", "--quiet", "-q", "Do the Hermes thing."])
        self.assertIn("--toolsets", args)
        self.assertIn("shell,edit", args)
        self.assertIn("--provider", args)
        self.assertIn("openrouter", args)
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["mode"], "chat")

    def test_nonzero_hermes_exit_still_records_logs_and_answer(self) -> None:
        self._write_fake_hermes(
            """
            printf '%s\\n' 'Hermes failed on purpose.' >&2
            exit 9
            """
        )

        result = self._run_adapter()

        self.assertEqual(result.returncode, 9)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "Hermes failed on purpose.\n",
        )
        self.assertIn(
            "Hermes failed on purpose.",
            (self.output / "hermes_stderr.log").read_text(encoding="utf-8"),
        )
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["exit_code"], 9)
        self.assertEqual(metadata["final_answer_strategy"], "stderr_fallback")

    def _run_adapter(
        self,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = {
            **os.environ,
            "PATH": f"{self.fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_HERMES_ARGS_FILE": str(self.root / "hermes_args.txt"),
            "FAKE_HERMES_CWD_FILE": str(self.root / "hermes_cwd.txt"),
            "FAKE_HERMES_HOME_FILE": str(self.root / "hermes_home.txt"),
        }
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [
                "python3",
                str(ADAPTER),
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
            ],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def _write_fake_hermes(self, body: str) -> None:
        hermes = self.fake_bin / "hermes"
        hermes.write_text(
            "#!/usr/bin/env sh\nset -eu\n" + body.strip() + "\n",
            encoding="utf-8",
        )
        hermes.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
