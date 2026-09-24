from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nanoclaw.skills import (
    SkillDefinition,
    auto_select_skills,
    discover_skills,
    resolve_requested_skills,
    serialize_skill,
)


class SkillsTest(unittest.TestCase):
    def test_auto_select_picks_single_best_skill(self) -> None:
        workspace = Path(tempfile.mkdtemp())
        skills = (
            SkillDefinition(
                slug="memory-preference-checker",
                name="Memory Preference Checker",
                description="Verify remembered preferences and prior decisions before answering",
                aliases=("memory-check",),
                requires=("memory",),
                homepage="https://example.com/memory",
                instructions="x",
                source_path=workspace / "a",
                root_dir=workspace,
                checksum="1",
            ),
            SkillDefinition(
                slug="weather",
                name="weather",
                description="Get weather forecasts using wttr.in",
                aliases=(),
                requires=(),
                homepage=None,
                instructions="y",
                source_path=workspace / "b",
                root_dir=workspace,
                checksum="2",
            ),
        )

        selected = auto_select_skills(
            skills,
            "Check memory before answering questions about user preferences.",
        )

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].slug, "memory-preference-checker")

    def test_skill_metadata_aliases_and_serialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            skill_dir = workspace / ".agents" / "skills" / "memory-preference-checker"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: Memory Preference Checker
description: Verify remembered preferences and prior decisions before answering
aliases:
  - memory-check
  - preference-check
requires:
  - memory
  - preferences
homepage: https://example.com/memory
---
Use this skill when the task depends on remembered preferences.
""",
                encoding="utf-8",
            )

            catalog = discover_skills(workspace)
            skill = next(
                skill
                for skill in catalog.skills
                if skill.slug == "memory-preference-checker"
            )
            self.assertEqual(skill.aliases, ("memory-check", "preference-check"))
            self.assertEqual(skill.requires, ("memory", "preferences"))
            self.assertEqual(skill.homepage, "https://example.com/memory")

            resolved = resolve_requested_skills(catalog.skills, ("memory-check",))
            self.assertEqual(resolved[0].slug, "memory-preference-checker")

            payload = serialize_skill(skill)
            self.assertEqual(payload["aliases"], ["memory-check", "preference-check"])
            self.assertEqual(payload["requires"], ["memory", "preferences"])
            self.assertEqual(payload["homepage"], "https://example.com/memory")


if __name__ == "__main__":
    unittest.main()
