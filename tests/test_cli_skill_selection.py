from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nanoclaw.cli import _select_skills
from nanoclaw.config import Settings


class CliSkillSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.skills_dir = self.root / "skills"
        for slug in ("alpha-skill", "beta-skill"):
            skill_dir = self.skills_dir / slug
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"""---
name: {slug}
description: Test skill {slug}
---
Use this skill for {slug}.
""",
                encoding="utf-8",
            )
        self.settings = Settings(
            model="gpt-4o",
            api_key="test",
            base_url="http://example.invalid",
            workspace_dir=self.workspace,
            prompt_dir=self.workspace / "prompts" / "official",
            prompt_files=("docs/reference/templates/AGENTS.md",),
            workspace_context_files=("SOUL.md",),
            extra_skill_dirs=(),
            run_mode="interactive",
            memory_policy="default",
            approval_mode="interactive",
            session_max_messages=10,
            session_max_chars=1000,
            max_steps=12,
            temperature=0.2,
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_missing_available_uses_discovered_skills(self) -> None:
        with patch("os.getcwd", return_value=str(self.root)), patch.object(Path, "cwd", return_value=self.root):
            _, available_skills, _ = _select_skills(
                task_text="Use local tools",
                settings=self.settings,
                workspace_dir=self.workspace,
                available_skill_names=None,
                requested_skill_names=(),
                auto_skills=False,
            )
        self.assertEqual({skill.slug for skill in available_skills}, {"alpha-skill", "beta-skill"})

    def test_explicit_empty_available_disables_all_skills(self) -> None:
        with patch("os.getcwd", return_value=str(self.root)), patch.object(Path, "cwd", return_value=self.root):
            _, available_skills, _ = _select_skills(
                task_text="Use local tools",
                settings=self.settings,
                workspace_dir=self.workspace,
                available_skill_names=(),
                requested_skill_names=(),
                auto_skills=False,
            )
        self.assertEqual(available_skills, ())

    def test_nonempty_available_whitelists_skills(self) -> None:
        with patch("os.getcwd", return_value=str(self.root)), patch.object(Path, "cwd", return_value=self.root):
            _, available_skills, _ = _select_skills(
                task_text="Use local tools",
                settings=self.settings,
                workspace_dir=self.workspace,
                available_skill_names=("beta-skill",),
                requested_skill_names=(),
                auto_skills=False,
            )
        self.assertEqual(tuple(skill.slug for skill in available_skills), ("beta-skill",))


if __name__ == "__main__":
    unittest.main()
