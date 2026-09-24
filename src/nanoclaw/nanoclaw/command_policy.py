from __future__ import annotations

import shlex
from dataclasses import dataclass, field


DEFAULT_SAFE_READONLY_COMMANDS = frozenset({"pwd", "ls"})


@dataclass(frozen=True, slots=True)
class CommandDecision:
    normalized_command: str
    argv: tuple[str, ...]
    safe_readonly: bool
    human_approved: bool
    requires_approval: bool


@dataclass(slots=True)
class CommandPolicy:
    safe_readonly_commands: frozenset[str] = DEFAULT_SAFE_READONLY_COMMANDS
    _approved_commands: set[str] = field(default_factory=set)

    def normalize_command(self, command: str) -> tuple[str, tuple[str, ...]]:
        raw = command.strip()
        if not raw:
            raise ValueError("Empty command")

        try:
            argv = shlex.split(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid command syntax: {exc}") from exc

        if not argv:
            raise ValueError("Empty command")

        return shlex.join(argv), tuple(argv)

    def is_safe_readonly(self, argv: tuple[str, ...]) -> bool:
        name = argv[0]
        if name not in self.safe_readonly_commands:
            return False
        if name == "pwd":
            return len(argv) == 1
        return True

    def decide(self, command: str) -> CommandDecision:
        normalized_command, argv = self.normalize_command(command)
        safe_readonly = self.is_safe_readonly(argv)
        human_approved = normalized_command in self._approved_commands
        return CommandDecision(
            normalized_command=normalized_command,
            argv=argv,
            safe_readonly=safe_readonly,
            human_approved=human_approved,
            requires_approval=not safe_readonly and not human_approved,
        )

    def approve_once(self, command: str) -> str:
        normalized_command, _ = self.normalize_command(command)
        self._approved_commands.add(normalized_command)
        return normalized_command

    def consume_approval(self, normalized_command: str) -> None:
        self._approved_commands.remove(normalized_command)
