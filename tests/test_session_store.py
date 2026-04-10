from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nanoclaw.session_store import (
    append_session_message,
    load_session_messages,
    session_path,
)


class SessionStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name) / "workspace"
        self.workspace.mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_load_session_messages_applies_message_limit(self) -> None:
        append_session_message(self.workspace, "demo", role="user", content="q1")
        append_session_message(
            self.workspace,
            "demo",
            role="assistant",
            content="a1",
            result_type="final_answer",
        )
        append_session_message(self.workspace, "demo", role="user", content="q2")

        loaded = load_session_messages(
            self.workspace,
            "demo",
            max_messages=2,
            max_chars=1000,
        )

        self.assertEqual(
            loaded,
            (
                {"role": "assistant", "content": "a1"},
                {"role": "user", "content": "q2"},
            ),
        )
        self.assertTrue(session_path(self.workspace, "demo").exists())


if __name__ == "__main__":
    unittest.main()
