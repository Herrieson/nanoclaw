from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "docker" / "openclaw-runner" / "adapter" / "run_task.mjs"


@unittest.skipUnless(shutil.which("node"), "node is required to test the OpenClaw adapter")
class OpenClawAdapterTest(unittest.TestCase):
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

        (self.input_dir / "task.md").write_text("Do the thing.\n", encoding="utf-8")
        (self.input_dir / "resolved_task.json").write_text(
            json.dumps({"id": "task_1"}) + "\n",
            encoding="utf-8",
        )
        (self.input_dir / "runner_request.json").write_text(
            json.dumps(
                {
                    "task_id": "task_1",
                    "run_id": "run_1",
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

    def test_runs_openclaw_and_writes_runner_contract_outputs(self) -> None:
        self._write_fake_openclaw(
            """
            printf '%s\\n' "$PWD" > "$FAKE_OPENCLAW_CWD_FILE"
            printf '%s\\n' "$HOME" > "$FAKE_OPENCLAW_HOME_FILE"
            for arg in "$@"; do printf '%s\\n' "$arg"; done > "$FAKE_OPENCLAW_ARGS_FILE"
            printf '%s\\n' 'startup log'
            printf '%s\\n' '{"type":"assistant_message","content":"Adapter final answer."}'
            """
        )

        result = self._run_adapter()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "Adapter final answer.\n",
        )
        self.assertIn(
            "startup log",
            (self.output / "openclaw_stdout.log").read_text(encoding="utf-8"),
        )
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["framework"], "openclaw")
        self.assertEqual(metadata["session_id"], "nanoclaw-task_1-run_1")
        self.assertEqual(metadata["final_answer_strategy"], "jsonl_stdout")

        args = (self.root / "openclaw_args.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(args[:3], ["agent", "--local", "--message"])
        self.assertEqual(args[3], "Do the thing.")
        self.assertIn("--json", args)
        self.assertIn("--session-id", args)
        self.assertIn("nanoclaw-task_1-run_1", args)
        self.assertIn("--model", args)
        self.assertIn("gpt-4o", args)
        self.assertEqual(
            (self.root / "openclaw_cwd.txt").read_text(encoding="utf-8").strip(),
            str(self.workspace),
        )
        self.assertEqual(
            (self.root / "openclaw_home.txt").read_text(encoding="utf-8").strip(),
            str(self.state / "home"),
        )

        trace_events = [
            json.loads(line)
            for line in (self.output / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(trace_events[0]["type"], "adapter_started")
        self.assertEqual(trace_events[-1]["type"], "openclaw_finished")
        self.assertEqual(trace_events[-1]["exit_code"], 0)

    def test_nonzero_openclaw_exit_still_records_logs_and_answer(self) -> None:
        self._write_fake_openclaw(
            """
            printf '%s\\n' 'OpenClaw failed on purpose.' >&2
            exit 7
            """
        )

        result = self._run_adapter()

        self.assertEqual(result.returncode, 7)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "OpenClaw failed on purpose.\n",
        )
        self.assertIn(
            "OpenClaw failed on purpose.",
            (self.output / "openclaw_stderr.log").read_text(encoding="utf-8"),
        )
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["exit_code"], 7)
        self.assertEqual(metadata["final_answer_strategy"], "stderr_fallback")

    def test_seeds_openclaw_home_template_before_running(self) -> None:
        template = self.root / "openclaw_home_template"
        sentinel = template / ".openclaw" / "plugin-runtime-deps" / "runtime" / "sentinel.txt"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text("prewarmed\n", encoding="utf-8")
        self._write_fake_openclaw(
            """
            test -f "$HOME/.openclaw/plugin-runtime-deps/runtime/sentinel.txt"
            test "${OPENCLAW_PLUGIN_STAGE_DIR:-}" = "$NANOCLAW_OPENCLAW_HOME_TEMPLATE/.openclaw/plugin-runtime-deps"
            printf '%s\\n' 'Seeded runtime deps.'
            """
        )

        result = self._run_adapter(
            {"NANOCLAW_OPENCLAW_HOME_TEMPLATE": str(template)}
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.state / "home" / ".openclaw" / "plugin-runtime-deps" / "runtime" / "sentinel.txt").read_text(encoding="utf-8"),
            "prewarmed\n",
        )
        self.assertTrue((self.state / "home" / ".openclaw" / "plugin-runtime-deps").is_symlink())
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "Seeded runtime deps.\n",
        )

    def test_sets_noninteractive_pnpm_environment(self) -> None:
        self._write_fake_openclaw(
            """
            test "${CI:-}" = "true"
            test "${NPM_CONFIG_CONFIRM_MODULES_PURGE:-}" = "false"
            test "${PNPM_CONFIG_CONFIRM_MODULES_PURGE:-}" = "false"
            test "${npm_config_confirm_modules_purge:-}" = "false"
            test "${npm_config_confirmModulesPurge:-}" = "false"
            printf '%s\\n' 'Noninteractive pnpm env ok.'
            """
        )

        result = self._run_adapter()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.output / "final_answer.md").read_text(encoding="utf-8"),
            "Noninteractive pnpm env ok.\n",
        )

    def test_writes_direct_custom_config_without_onboarding(self) -> None:
        self._write_fake_openclaw(
            """
            test "$1" != "onboard"
            printf '%s\\n' 'Direct config ok.'
            """
        )

        result = self._run_adapter(
            {
                "NANOCLAW_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "OPENAI_API_KEY": "test-key",
            },
            auto_onboard=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        config_path = self.state / "home" / ".openclaw" / "openclaw.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        provider = config["models"]["providers"]["custom-dashscope-aliyuncs-com"]
        self.assertEqual(provider["baseUrl"], "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.assertEqual(provider["api"], "openai-completions")
        self.assertEqual(
            provider["apiKey"],
            {"source": "env", "provider": "default", "id": "CUSTOM_API_KEY"},
        )
        self.assertEqual(provider["models"][0]["id"], "gpt-4o")
        self.assertEqual(
            config["agents"]["defaults"]["model"]["primary"],
            "custom-dashscope-aliyuncs-com/gpt-4o",
        )
        self.assertTrue((self.state / "home" / ".openclaw" / "agents" / "main" / "sessions").is_dir())
        metadata = json.loads((self.output / "runner_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["onboarding"]["reason"], "direct_config_written")

        trace_events = [
            json.loads(line)
            for line in (self.output / "trace.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertIn("openclaw_config_written", [event["type"] for event in trace_events])

    def _run_adapter(
        self,
        extra_env: dict[str, str] | None = None,
        *,
        auto_onboard: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        env = {
            **os.environ,
            "PATH": f"{self.fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_OPENCLAW_ARGS_FILE": str(self.root / "openclaw_args.txt"),
            "FAKE_OPENCLAW_CWD_FILE": str(self.root / "openclaw_cwd.txt"),
            "FAKE_OPENCLAW_HOME_FILE": str(self.root / "openclaw_home.txt"),
        }
        if not auto_onboard:
            env["NANOCLAW_OPENCLAW_AUTO_ONBOARD"] = "0"
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [
                "node",
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

    def _write_fake_openclaw(self, body: str) -> None:
        openclaw = self.fake_bin / "openclaw"
        openclaw.write_text(
            "#!/usr/bin/env sh\nset -eu\n" + body.strip() + "\n",
            encoding="utf-8",
        )
        openclaw.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
