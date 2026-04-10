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

        self.assertIn("--- BEGIN RUNTIME TOOLS ---", prompt)
        self.assertIn("--- BEGIN RUNTIME METADATA ---", prompt)
        self.assertIn("--- BEGIN MEMORY POLICY ---", prompt)
        self.assertIn("--- BEGIN WORKSPACE CONTEXT ---", prompt)
        self.assertIn("Run mode: interactive", prompt)
        self.assertIn("memory_policy", agent.last_runtime_metadata)

    def test_final_response_classification(self) -> None:
        agent = MinimalClaw(self.settings)

        self.assertEqual(agent._classify_final_response("HEARTBEAT_OK"), "heartbeat_ack")
        self.assertEqual(agent._classify_final_response(" SILENT_REPLY\n"), "silent_reply")
        self.assertEqual(agent._classify_final_response("hello"), "final_answer")

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

        self.assertIn("--- BEGIN SKILL CATALOG ---", prompt)
        self.assertIn(".skills/tutorial-brief-writer/SKILL.md", prompt)
        self.assertIn("You do not need to use every available skill.", prompt)


if __name__ == "__main__":
    unittest.main()
