from __future__ import annotations

import unittest

from nanoclaw.command_policy import CommandPolicy


class CommandPolicyTest(unittest.TestCase):
    def test_safe_readonly_command_does_not_require_approval(self) -> None:
        policy = CommandPolicy()

        decision = policy.decide("ls")

        self.assertTrue(decision.safe_readonly)
        self.assertFalse(decision.requires_approval)
        self.assertFalse(decision.human_approved)

    def test_approval_is_consumed_once(self) -> None:
        policy = CommandPolicy()

        first = policy.decide("touch demo.txt")
        self.assertTrue(first.requires_approval)

        normalized = policy.approve_once("touch demo.txt")
        second = policy.decide("touch demo.txt")
        self.assertEqual(second.normalized_command, normalized)
        self.assertTrue(second.human_approved)
        self.assertFalse(second.requires_approval)

        policy.consume_approval(normalized)
        third = policy.decide("touch demo.txt")
        self.assertTrue(third.requires_approval)


if __name__ == "__main__":
    unittest.main()
