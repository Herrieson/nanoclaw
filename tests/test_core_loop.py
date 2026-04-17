from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nanoclaw.config import Settings
from nanoclaw.core_loop import MinimalClaw
from nanoclaw.skills import SkillDefinition


class CoreLoopTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.prompts = self.workspace / "prompts" / "official"
        (self.prompts / "docs/reference/templates").mkdir(parents=True)
        (self.prompts / "docs/reference/templates/AGENTS.md").write_text(
            "# Agents\nUse tools carefully.\n",
            encoding="utf-8",
        )
        (self.prompts / "docs/reference/templates/HEARTBEAT.md").write_text(
            "# Heartbeat\nReply with HEARTBEAT_OK when idle.\n",
            encoding="utf-8",
        )
        (self.prompts / "docs/reference/templates/BOOTSTRAP.md").write_text(
            "# Bootstrap\nIntroduce the workspace on first run.\n",
            encoding="utf-8",
        )
        (self.workspace / "SOUL.md").write_text("# SOUL\nBe concise.\n", encoding="utf-8")
        (self.workspace / "USER.md").write_text("# USER\nName: Tester\n", encoding="utf-8")

        self.settings = Settings(
            model="gpt-4o",
            api_key="test",
            base_url="http://example.invalid",
            workspace_dir=self.workspace,
            prompt_dir=self.prompts,
            prompt_files=("docs/reference/templates/AGENTS.md",),
            workspace_context_files=("SOUL.md", "USER.md"),
            extra_skill_dirs=(),
            run_mode="interactive",
            memory_policy="strict",
            approval_mode="interactive",
            session_max_messages=10,
            session_max_chars=1000,
            max_steps=2,
            temperature=0.0,
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_build_system_prompt_includes_runtime_and_workspace_context(self) -> None:
        agent = MinimalClaw(self.settings)
        agent.bootstrap_workspace()

        prompt = agent.build_system_prompt()

        self.assertIn("## Tooling", prompt)
        self.assertIn("## Memory Recall", prompt)
        self.assertIn("## Workspace", prompt)
        self.assertIn("## Current Date & Time", prompt)
        self.assertIn("## Runtime", prompt)
        self.assertIn("## Prompt References", prompt)
        self.assertIn("# Project Context", prompt)
        self.assertIn("run_mode=interactive", prompt)
        self.assertIn(
            "Use memory_append only when the user or task explicitly asks you to remember or record something into memory files.",
            prompt,
        )
        self.assertIn(
            "Treat them as reference guidance, not as the active workspace project context.",
            prompt,
        )
        self.assertNotIn("## Heartbeat", prompt)
        self.assertIn("memory_policy", agent.last_runtime_metadata)

    def test_final_response_classification(self) -> None:
        agent = MinimalClaw(self.settings)

        self.assertEqual(agent._classify_final_response("HEARTBEAT_OK"), "heartbeat_ack")
        self.assertEqual(agent._classify_final_response(" SILENT_REPLY\n"), "silent_reply")
        self.assertEqual(agent._classify_final_response("hello"), "final_answer")

    def test_mock_noop_model_returns_without_api_call(self) -> None:
        mock_settings = Settings(
            model="mock-noop",
            api_key=None,
            base_url=None,
            workspace_dir=self.settings.workspace_dir,
            prompt_dir=self.settings.prompt_dir,
            prompt_files=self.settings.prompt_files,
            workspace_context_files=self.settings.workspace_context_files,
            extra_skill_dirs=self.settings.extra_skill_dirs,
            run_mode=self.settings.run_mode,
            memory_policy=self.settings.memory_policy,
            approval_mode=self.settings.approval_mode,
            session_max_messages=self.settings.session_max_messages,
            session_max_chars=self.settings.session_max_chars,
            max_steps=self.settings.max_steps,
            temperature=self.settings.temperature,
        )
        agent = MinimalClaw(mock_settings)
        agent.bootstrap_workspace()

        final_text = agent.run("Do nothing.", echo=False)

        self.assertEqual(final_text, "MOCK_NOOP_FINAL_ANSWER")
        self.assertIsNotNone(agent.last_run_report)
        self.assertEqual(agent.last_run_report.status, "completed")
        self.assertEqual(agent.last_run_report.steps_used, 0)

    def test_build_system_prompt_includes_skill_catalog_locations(self) -> None:
        skill_path = self.workspace / ".skills" / "tutorial-brief-writer" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("Use this skill for tutorial briefs.\n", encoding="utf-8")
        skill = SkillDefinition(
            slug="tutorial-brief-writer",
            name="tutorial-brief-writer",
            description="Produce concise tutorial-style workspace briefs.",
            aliases=(),
            requires=(),
            homepage=None,
            instructions="Use this skill for tutorial briefs.",
            source_path=skill_path,
            root_dir=skill_path.parent,
            checksum="abc",
        )

        agent = MinimalClaw(self.settings, available_skills=(skill,))
        prompt = agent.build_system_prompt()

        self.assertIn("## Skills (mandatory)", prompt)
        self.assertIn("<available_skills>", prompt)
        self.assertIn("<name>tutorial-brief-writer</name>", prompt)
        self.assertIn(".skills/tutorial-brief-writer/SKILL.md", prompt)
        self.assertIn("If exactly one skill clearly applies", prompt)

    def test_build_system_prompt_does_not_preinject_activated_skill_instructions(self) -> None:
        skill_path = self.workspace / ".skills" / "tutorial-brief-writer" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("Use this skill for tutorial briefs.\n", encoding="utf-8")
        skill = SkillDefinition(
            slug="tutorial-brief-writer",
            name="tutorial-brief-writer",
            description="Produce concise tutorial-style workspace briefs.",
            aliases=(),
            requires=(),
            homepage=None,
            instructions="Use this skill for tutorial briefs.",
            source_path=skill_path,
            root_dir=skill_path.parent,
            checksum="abc",
        )

        agent = MinimalClaw(
            self.settings,
            available_skills=(skill,),
            activated_skills=(skill,),
        )
        prompt = agent.build_system_prompt()

        self.assertNotIn("## Pre-Activated Skills", prompt)
        self.assertNotIn("The following skill instructions were injected up front", prompt)

    def test_bootstrap_prompt_is_first_run_only(self) -> None:
        bootstrap_settings = Settings(
            model=self.settings.model,
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            workspace_dir=self.settings.workspace_dir,
            prompt_dir=self.settings.prompt_dir,
            prompt_files=(
                "docs/reference/templates/AGENTS.md",
                "docs/reference/templates/BOOTSTRAP.md",
            ),
            workspace_context_files=self.settings.workspace_context_files,
            extra_skill_dirs=self.settings.extra_skill_dirs,
            run_mode=self.settings.run_mode,
            memory_policy=self.settings.memory_policy,
            approval_mode=self.settings.approval_mode,
            session_max_messages=self.settings.session_max_messages,
            session_max_chars=self.settings.session_max_chars,
            max_steps=self.settings.max_steps,
            temperature=self.settings.temperature,
        )

        first_agent = MinimalClaw(bootstrap_settings)
        first_agent.bootstrap_workspace()
        first_prompt = first_agent.build_system_prompt()
        self.assertIn("## Bootstrap", first_prompt)
        self.assertIn("Introduce the workspace on first run.", first_prompt)

        second_agent = MinimalClaw(bootstrap_settings)
        second_agent.bootstrap_workspace()
        second_prompt = second_agent.build_system_prompt()
        self.assertNotIn("## Bootstrap", second_prompt)
        self.assertNotIn("Introduce the workspace on first run.", second_prompt)

    def test_heartbeat_prompt_only_appears_in_heartbeat_mode(self) -> None:
        heartbeat_settings = Settings(
            model=self.settings.model,
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            workspace_dir=self.settings.workspace_dir,
            prompt_dir=self.settings.prompt_dir,
            prompt_files=(
                "docs/reference/templates/AGENTS.md",
                "docs/reference/templates/HEARTBEAT.md",
            ),
            workspace_context_files=self.settings.workspace_context_files,
            extra_skill_dirs=self.settings.extra_skill_dirs,
            run_mode="heartbeat",
            memory_policy=self.settings.memory_policy,
            approval_mode=self.settings.approval_mode,
            session_max_messages=self.settings.session_max_messages,
            session_max_chars=self.settings.session_max_chars,
            max_steps=self.settings.max_steps,
            temperature=self.settings.temperature,
        )

        agent = MinimalClaw(heartbeat_settings)
        agent.bootstrap_workspace()
        prompt = agent.build_system_prompt()

        self.assertIn("## Heartbeat", prompt)
        self.assertIn("Reply with HEARTBEAT_OK when idle.", prompt)


if __name__ == "__main__":
    unittest.main()
