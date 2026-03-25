from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

from openai import OpenAI

from .config import Settings


SAFE_READONLY_COMMANDS = frozenset({"pwd", "ls"})
MAX_COMMAND_OUTPUT_CHARS = 4000


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a markdown file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Relative file path like MEMORY.md",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or replace a markdown file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_dangerous_command",
            "description": "Execute a shell command in workspace. Safe read-only commands run directly; other commands require prior human approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_human_for_confirmation",
            "description": "Ask the human to approve exactly one command execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                    "command": {
                        "type": "string",
                        "description": "The exact command to approve for one-time execution.",
                    },
                },
                "required": ["reason", "command"],
            },
        },
    },
]


class MinimalClaw:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.settings.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.client: OpenAI | None = None
        self._approved_commands: set[str] = set()

    def _get_client(self) -> OpenAI:
        if self.client is not None:
            return self.client

        api_key = self.settings.api_key or "EMPTY"
        if not self.settings.base_url and api_key == "EMPTY":
            raise ValueError(
                "OPENAI_API_KEY is required when NANOCLAW_BASE_URL is not set"
            )

        self.client = OpenAI(api_key=api_key, base_url=self.settings.base_url)
        return self.client

    def bootstrap_workspace(self) -> None:
        memory_path = self.settings.workspace_dir / "MEMORY.md"
        active_task_path = self.settings.workspace_dir / "active_task.md"

        if not memory_path.exists():
            memory_path.write_text("# Memory\nNo entries yet.\n", encoding="utf-8")
        if not active_task_path.exists():
            active_task_path.write_text("# Active Task\n", encoding="utf-8")

    def _resolve_workspace_path(self, relative_path: str) -> Path:
        candidate = (self.settings.workspace_dir / relative_path).resolve()
        workspace = self.settings.workspace_dir.resolve()
        if candidate != workspace and workspace not in candidate.parents:
            raise ValueError(f"Path escapes workspace: {relative_path}")
        return candidate

    def _read_prompt_file(self, relative_path: str) -> str:
        path = (self.settings.prompt_dir / relative_path).resolve()
        prompt_root = self.settings.prompt_dir.resolve()
        if path != prompt_root and prompt_root not in path.parents:
            raise ValueError(f"Prompt path escapes prompt dir: {relative_path}")
        if not path.exists():
            raise FileNotFoundError(
                f"Missing official prompt file: {path}. Run sync first."
            )
        return path.read_text(encoding="utf-8")

    def build_system_prompt(self) -> str:
        chunks = [
            "You are a self-hosted AI assistant. Follow the rules in the provided context exactly.",
            "",
        ]

        for name in self.settings.prompt_files:
            content = self._read_prompt_file(name)
            chunks.append(f"--- BEGIN {name} ---")
            chunks.append(content)
            chunks.append(f"--- END {name} ---")
            chunks.append("")

        return "\n".join(chunks)

    def _normalize_command(self, command: str) -> tuple[str, list[str]]:
        raw = command.strip()
        if not raw:
            raise ValueError("Empty command")

        try:
            argv = shlex.split(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid command syntax: {exc}") from exc

        if not argv:
            raise ValueError("Empty command")

        return shlex.join(argv), argv

    def _is_safe_readonly_command(self, argv: list[str]) -> bool:
        name = argv[0]
        if name not in SAFE_READONLY_COMMANDS:
            return False
        if name == "pwd":
            return len(argv) == 1
        return True

    def _run_workspace_command(self, argv: list[str]) -> str:
        try:
            process = subprocess.run(
                argv,
                cwd=str(self.settings.workspace_dir),
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except FileNotFoundError:
            return f"Error: command not found: {argv[0]}"
        except subprocess.TimeoutExpired:
            return "Error: command timed out (20s)"
        except Exception as exc:
            return f"Error: failed to run command: {exc}"

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        chunks: list[str] = []
        if stdout:
            chunks.append(stdout)
        if stderr:
            chunks.append(f"[stderr]\n{stderr}")

        output = "\n\n".join(chunks) if chunks else "(no output)"
        if len(output) > MAX_COMMAND_OUTPUT_CHARS:
            output = output[:MAX_COMMAND_OUTPUT_CHARS] + "\n...(truncated)"

        if process.returncode != 0:
            return f"Error: command exited with code {process.returncode}\n{output}"
        return output

    def execute_tool(self, tool_name: str, arguments_json: str) -> str:
        try:
            args = json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON arguments: {exc}"

        try:
            if tool_name == "read_file":
                path = self._resolve_workspace_path(str(args["filename"]))
                return path.read_text(encoding="utf-8")

            if tool_name == "write_file":
                path = self._resolve_workspace_path(str(args["filename"]))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(args["content"]), encoding="utf-8")
                return "Success: File written."

            if tool_name == "execute_dangerous_command":
                command = str(args.get("command", ""))
                normalized_command, argv = self._normalize_command(command)

                if self._is_safe_readonly_command(argv):
                    return self._run_workspace_command(argv)

                if normalized_command not in self._approved_commands:
                    print(
                        f"\n[ALERT] Non-safe command blocked (needs approval): {normalized_command}"
                    )
                    return (
                        "Error: Permission denied. Call ask_human_for_confirmation "
                        "with the same command before execution."
                    )

                self._approved_commands.remove(normalized_command)
                print(f"\n[ALERT] Executing approved command: {normalized_command}")
                return self._run_workspace_command(argv)

            if tool_name == "ask_human_for_confirmation":
                reason = str(args.get("reason", "No reason provided."))
                command = str(args.get("command", ""))
                normalized_command, _ = self._normalize_command(command)

                print(f"\n[Agent asks human] {reason}")
                print(f"Command for one-time approval: {normalized_command}")
                human_response = input("Your response (Approve/Reject/Modify): ").strip()
                lowered = human_response.lower()

                if lowered.startswith("approve"):
                    self._approved_commands.add(normalized_command)
                    return (
                        f"Human response: {human_response}. "
                        f"Approved once: {normalized_command}"
                    )

                return f"Human response: {human_response}"

            return f"Error: Unknown tool '{tool_name}'."

        except KeyError as exc:
            return f"Error: missing field {exc}"
        except ValueError as exc:
            return f"Error: {exc}"
        except FileNotFoundError:
            return "Error: File not found."
        except Exception as exc:
            return f"Error: {exc}"

    def run(self, user_task: str, *, echo: bool = True) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": user_task},
        ]

        if echo:
            print(f"User Task: {user_task}")

        client = self._get_client()

        for step in range(1, self.settings.max_steps + 1):
            if echo:
                print(f"\n--- API Call {step} ---")

            response = client.chat.completions.create(
                model=self.settings.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=self.settings.temperature,
            )

            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                final_text = message.content or ""
                if echo:
                    print(f"\n[Final Answer]: {final_text}")
                return final_text

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments or "{}"

                if echo:
                    print(f"[Tool Execution] -> {tool_name}({tool_args})")

                result = self.execute_tool(tool_name, tool_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

        raise RuntimeError(
            f"Agent exceeded max steps ({self.settings.max_steps}) without final answer"
        )
