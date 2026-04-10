from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nanoclaw.memory import (
    append_memory,
    bootstrap_memory_files,
    get_memory_slice,
    search_memory,
    today_memory_filename,
)


class MemoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir(parents=True)
        bootstrap_memory_files(self.workspace)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_bootstrap_creates_daily_memory_file(self) -> None:
        daily_path = self.workspace / today_memory_filename()
        self.assertTrue(daily_path.exists())

    def test_search_and_get_memory(self) -> None:
        append_memory(self.workspace, "MEMORY.md", "- prefers dark mode\n")
        append_memory(self.workspace, "memory/notes.md", "Remember dark mode later.\n")

        payload = json.loads(search_memory(self.workspace, "dark mode"))
        paths = {item["path"] for item in payload["matches"]}
        self.assertIn("MEMORY.md", paths)
        self.assertIn("memory/notes.md", paths)

        snippet = get_memory_slice(self.workspace, "MEMORY.md", 1, 5)
        self.assertIn("prefers dark mode", snippet)

    def test_search_handles_semanticish_query_variants(self) -> None:
        append_memory(
            self.workspace,
            "MEMORY.md",
            "- Sam prefers dark mode in editor themes.\n",
        )
        append_memory(
            self.workspace,
            "memory/notes.md",
            "- Sam asked us not to switch the team wiki back to light mode.\n",
        )

        payload = json.loads(search_memory(self.workspace, "Sam display theme preference"))
        self.assertGreaterEqual(len(payload["matches"]), 1)
        self.assertEqual(payload["matches"][0]["path"], "MEMORY.md")
        self.assertIn("dark mode", payload["matches"][0]["text"])


if __name__ == "__main__":
    unittest.main()
