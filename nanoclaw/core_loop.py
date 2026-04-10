from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from openai import OpenAI

from .command_policy import CommandPolicy
from .config import Settings
from .memory import (
    append_memory,
    bootstrap_memory_files,
    get_memory_slice,
    search_memory,
)
from .skills import SkillDefinition


MAX_COMMAND_OUTPUT_CHARS = 4000
MAX_SEARCH_MATCHES = 200
HEARTBEAT_CONTEXT_FILE = "HEARTBEAT.md"
HEARTBEAT_ACK = "HEARTBEAT_OK"
SILENT_REPLY = "SILENT_REPLY"
EventHandler = Callable[[dict[str, Any]], None]


def _strip_front_matter(content: str) -> str:
    if not content.startswith("---"):
        return content

    end_index = content.find("\n---", 3)
    if end_index == -1:
        return content

    trimmed = content[end_index + len("\n---") :]
    return trimmed.lstrip()


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Read a text file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path like MEMORY.md",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Create or replace a text file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit",
            "description": "Make a precise in-file text replacement in a workspace file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                    "replace_all": {
                        "type": "boolean",
                        "description": "Replace all matches instead of exactly one.",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": "Apply one or more exact text replacements across workspace files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "old_text": {"type": "string"},
                                "new_text": {"type": "string"},
                                "replace_all": {"type": "boolean"},
                            },
                            "required": ["path", "old_text", "new_text"],
                        },
                    }
                },
                "required": ["changes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search workspace file contents with a regular expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "glob": {
                        "type": "string",
                        "description": "Optional glob like '**/*.md'. Defaults to all files.",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_search",
            "description": "Search MEMORY.md and memory/*.md for relevant prior context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_get",
            "description": "Read a narrow line range from MEMORY.md or memory/*.md.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                },
                "required": ["path", "start_line", "end_line"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_append",
            "description": "Append a note to MEMORY.md or a file under memory/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find",
            "description": "Find workspace files by glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern like '**/*.md'. Defaults to '**/*'.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ls",
            "description": "List directory contents from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path. Defaults to '.'.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "When true, list contents recursively.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exec",
            "description": "Run a shell command in the workspace. Safe read-only commands run directly; other commands require prior human approval.",
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


@dataclass(frozen=True, slots=True)
class RunReport:
    status: str
    result_type: str
    steps_used: int
    final_answer: str | None
    error: str | None


class MinimalClaw:
    def __init__(
        self,
        settings: Settings,
        *,
        available_skills: tuple[SkillDefinition, ...] = (),
        activated_skills: tuple[SkillDefinition, ...] = (),
    ) -> None:
        self.settings = settings
        self.settings.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.settings.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.client: OpenAI | None = None
        self.command_policy = CommandPolicy()
        self._event_handler: EventHandler | None = None
        self.last_run_report: RunReport | None = None
        self.available_skills = available_skills
        self.activated_skills = activated_skills
        self.last_workspace_context_files: tuple[str, ...] = ()
        self.last_runtime_metadata: dict[str, Any] = {}

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
        daily_memory_dir = self.settings.workspace_dir / "memory"

        if not memory_path.exists():
            memory_path.write_text("# Memory\nNo entries yet.\n", encoding="utf-8")
        if not active_task_path.exists():
            active_task_path.write_text("# Active Task\n", encoding="utf-8")
        daily_memory_dir.mkdir(parents=True, exist_ok=True)
        bootstrap_memory_files(self.settings.workspace_dir)

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
        raw = path.read_text(encoding="utf-8")
        return _strip_front_matter(raw)

    def _resolve_tool_path(self, raw_path: str | None, *, default: str = ".") -> Path:
        candidate = (raw_path or default).strip() or default
        return self._resolve_workspace_path(candidate)

    def _runtime_metadata(self) -> dict[str, str]:
        now = datetime.now().astimezone()
        return {
            "date_time": now.isoformat(),
            "timezone": str(now.tzinfo or "UTC"),
            "workspace_dir": str(self.settings.workspace_dir.resolve()),
            "model": self.settings.model,
            "run_mode": self.settings.run_mode,
            "memory_policy": self.settings.memory_policy,
        }

    def _workspace_context_paths(self) -> tuple[tuple[str, Path], ...]:
        selected: list[tuple[str, Path]] = []
        seen: set[str] = set()
        candidate_files = list(self.settings.workspace_context_files)
        if self.settings.run_mode == "heartbeat":
            candidate_files.append(HEARTBEAT_CONTEXT_FILE)

        for relative_name in candidate_files:
            normalized = relative_name.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            path = self._resolve_workspace_path(normalized)
            if path.exists() and path.is_file():
                selected.append((normalized, path))

        return tuple(selected)

    def _tool_prompt_lines(self) -> list[str]:
        lines = [
            "--- BEGIN RUNTIME TOOLS ---",
            "Tool availability is defined by the runtime, not by TOOLS.md.",
            "Call tools exactly by the names listed below.",
            "",
        ]
        for tool in TOOLS:
            function = tool["function"]
            lines.append(f"- {function['name']}: {function['description']}")
        lines.append("--- END RUNTIME TOOLS ---")
        lines.append("")
        return lines

    def _workspace_files_prompt_lines(self) -> list[str]:
        context_paths = self._workspace_context_paths()
        self.last_workspace_context_files = tuple(name for name, _ in context_paths)
        if not context_paths:
            return []

        lines = [
            "--- BEGIN WORKSPACE CONTEXT ---",
            "The following workspace files were loaded for this run when present.",
            "",
        ]
        for relative_name, path in context_paths:
            lines.append(f"--- BEGIN {relative_name} ---")
            lines.append(path.read_text(encoding="utf-8"))
            lines.append(f"--- END {relative_name} ---")
            lines.append("")
        lines.append("--- END WORKSPACE CONTEXT ---")
        lines.append("")
        return lines

    def _runtime_prompt_lines(self) -> list[str]:
        metadata = self._runtime_metadata()
        self.last_runtime_metadata = dict(metadata)
        return [
            "--- BEGIN RUNTIME METADATA ---",
            f"Current date/time: {metadata['date_time']}",
            f"Timezone: {metadata['timezone']}",
            f"Workspace directory: {metadata['workspace_dir']}",
            f"Model: {metadata['model']}",
            f"Run mode: {metadata['run_mode']}",
            "--- END RUNTIME METADATA ---",
            "",
        ]

    def _memory_policy_prompt_lines(self) -> list[str]:
        if self.settings.memory_policy == "off":
            return []

        recall_instruction = (
            "Before answering questions about prior work, decisions, dates, preferences, people, or todos, first use memory_search on MEMORY.md and memory/*.md."
        )
        if self.settings.memory_policy == "strict":
            recall_instruction = (
                "Always use memory_search on MEMORY.md and memory/*.md before answering questions about prior work, decisions, dates, preferences, people, or todos."
            )

        return [
            "--- BEGIN MEMORY POLICY ---",
            recall_instruction,
            "Use memory_get to fetch only the relevant line ranges before relying on remembered details.",
            "If memory search is inconclusive, say that you checked memory and were inconclusive.",
            "Use memory_append when the task explicitly asks you to remember something or when you need to persist a notable note into memory files.",
            "--- END MEMORY POLICY ---",
            "",
        ]

    def build_system_prompt(self) -> str:
        chunks = [
            "You are a self-hosted AI assistant. Follow the rules in the provided context exactly.",
            "",
        ]

        chunks.extend(self._tool_prompt_lines())
        chunks.extend(self._runtime_prompt_lines())
        chunks.extend(self._memory_policy_prompt_lines())

        for name in self.settings.prompt_files:
            content = self._read_prompt_file(name)
            chunks.append(f"--- BEGIN {name} ---")
            chunks.append(content)
            chunks.append(f"--- END {name} ---")
            chunks.append("")

        chunks.extend(self._workspace_files_prompt_lines())

        if self.available_skills:
            chunks.append("--- BEGIN SKILL CATALOG ---")
            chunks.append(
                "Before replying, scan the available skill descriptions below."
            )
            chunks.append(
                "Treat this catalog as task-scoped guidance. When a listed skill is relevant, read only the specific SKILL.md files you need with the read tool."
            )
            chunks.append(
                "Use the smallest helpful subset of skills for the task. You do not need to use every available skill."
            )
            if self.activated_skills:
                chunks.append(
                    "Some skills may also be pre-activated below for compatibility or explicit user choice."
                )
            chunks.append("")
            for skill in self.available_skills:
                chunks.append(
                    f"- {skill.slug}: {skill.description} | location=.skills/{skill.slug}/SKILL.md"
                )
            chunks.append("--- END SKILL CATALOG ---")
            chunks.append("")

        for skill in self.activated_skills:
            chunks.append(f"--- BEGIN SKILL {skill.slug} ---")
            chunks.append(f"Name: {skill.name}")
            chunks.append(f"Description: {skill.description}")
            chunks.append("")
            chunks.append(skill.instructions)
            chunks.append(f"--- END SKILL {skill.slug} ---")
            chunks.append("")

        return "\n".join(chunks)

    def _emit_event(self, event_type: str, **payload: Any) -> None:
        if self._event_handler is None:
            return

        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        self._event_handler(event)

    def _set_run_report(
        self,
        *,
        status: str,
        result_type: str,
        steps_used: int,
        final_answer: str | None,
        error: str | None,
    ) -> RunReport:
        report = RunReport(
            status=status,
            result_type=result_type,
            steps_used=steps_used,
            final_answer=final_answer,
            error=error,
        )
        self.last_run_report = report
        return report

    def _decode_tool_args(self, arguments_json: str) -> Any:
        try:
            return json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError:
            return arguments_json

    def _run_workspace_command(self, argv: tuple[str, ...]) -> str:
        try:
            process = subprocess.run(
                list(argv),
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

    def _read_workspace_file(self, raw_path: str) -> str:
        path = self._resolve_workspace_path(raw_path)
        return path.read_text(encoding="utf-8")

    def _write_workspace_file(self, raw_path: str, content: str) -> str:
        path = self._resolve_workspace_path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return "Success: File written."

    def _edit_workspace_file(
        self,
        raw_path: str,
        old_text: str,
        new_text: str,
        *,
        replace_all: bool = False,
    ) -> str:
        path = self._resolve_workspace_path(raw_path)
        content = path.read_text(encoding="utf-8")

        occurrences = content.count(old_text)
        if occurrences == 0:
            return "Error: target text not found."
        if not replace_all and occurrences != 1:
            return (
                "Error: target text matched multiple locations. "
                "Pass replace_all=true or provide more specific old_text."
            )

        updated = (
            content.replace(old_text, new_text)
            if replace_all
            else content.replace(old_text, new_text, 1)
        )
        path.write_text(updated, encoding="utf-8")
        changed = occurrences if replace_all else 1
        return f"Success: Applied {changed} edit(s)."

    def _apply_workspace_patch(self, changes: list[dict[str, Any]]) -> str:
        if not changes:
            return "Error: no changes provided."

        results: list[str] = []
        for index, change in enumerate(changes, start=1):
            try:
                result = self._edit_workspace_file(
                    str(change["path"]),
                    str(change["old_text"]),
                    str(change["new_text"]),
                    replace_all=bool(change.get("replace_all", False)),
                )
            except KeyError as exc:
                return f"Error: missing field {exc} in change #{index}"
            if result.startswith("Error:"):
                return f"{result} (change #{index})"
            results.append(f"change #{index}: {result}")

        return "Success: Patch applied.\n" + "\n".join(results)

    def _iter_workspace_files(self, pattern: str | None = None) -> tuple[Path, ...]:
        glob_pattern = (pattern or "**/*").strip() or "**/*"
        files = [
            path
            for path in self.settings.workspace_dir.glob(glob_pattern)
            if path.is_file()
        ]
        return tuple(sorted(files))

    def _relative_workspace_path(self, path: Path) -> str:
        return str(path.relative_to(self.settings.workspace_dir)).replace("\\", "/")

    def _find_workspace_files(self, pattern: str | None = None) -> str:
        files = [
            self._relative_workspace_path(path)
            for path in self._iter_workspace_files(pattern)
        ]
        return json.dumps({"files": files}, indent=2, ensure_ascii=False)

    def _list_workspace_dir(
        self,
        raw_path: str | None = None,
        *,
        recursive: bool = False,
    ) -> str:
        path = self._resolve_tool_path(raw_path, default=".")
        if not path.exists():
            return "Error: path not found."
        if path.is_file():
            return json.dumps(
                {
                    "path": self._relative_workspace_path(path),
                    "entries": [
                        {
                            "path": self._relative_workspace_path(path),
                            "type": "file",
                        }
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )

        entries = path.rglob("*") if recursive else path.iterdir()
        payload = []
        for entry in sorted(entries):
            payload.append(
                {
                    "path": self._relative_workspace_path(entry),
                    "type": "dir" if entry.is_dir() else "file",
                }
            )

        relative_path = "."
        if path != self.settings.workspace_dir:
            relative_path = self._relative_workspace_path(path)
        return json.dumps(
            {"path": relative_path, "entries": payload},
            indent=2,
            ensure_ascii=False,
        )

    def _grep_workspace(self, pattern: str, glob_pattern: str | None = None) -> str:
        regex = re.compile(pattern)
        matches: list[dict[str, Any]] = []

        for path in self._iter_workspace_files(glob_pattern):
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            for line_number, line in enumerate(lines, start=1):
                if not regex.search(line):
                    continue
                matches.append(
                    {
                        "path": self._relative_workspace_path(path),
                        "line": line_number,
                        "text": line,
                    }
                )
                if len(matches) >= MAX_SEARCH_MATCHES:
                    return json.dumps(
                        {
                            "matches": matches,
                            "truncated": True,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )

        return json.dumps(
            {
                "matches": matches,
                "truncated": False,
            },
            indent=2,
            ensure_ascii=False,
        )

    def _execute_workspace_command(self, command: str) -> str:
        decision = self.command_policy.decide(command)
        if decision.safe_readonly:
            self._emit_event(
                "command_execution",
                command=decision.normalized_command,
                safe_readonly=True,
                human_approved=False,
            )
            return self._run_workspace_command(decision.argv)

        if decision.requires_approval:
            self._emit_event("command_blocked", command=decision.normalized_command)
            print(
                f"\n[ALERT] Non-safe command blocked (needs approval): {decision.normalized_command}"
            )
            return (
                "Error: Permission denied. Call ask_human_for_confirmation "
                "with the same command before execution."
            )

        self.command_policy.consume_approval(decision.normalized_command)
        self._emit_event(
            "command_execution",
            command=decision.normalized_command,
            safe_readonly=False,
            human_approved=True,
        )
        print(f"\n[ALERT] Executing approved command: {decision.normalized_command}")
        return self._run_workspace_command(decision.argv)

    def _classify_final_response(self, text: str) -> str:
        normalized = text.strip()
        if normalized == HEARTBEAT_ACK:
            return "heartbeat_ack"
        if normalized == SILENT_REPLY:
            return "silent_reply"
        return "final_answer"

    def execute_tool(self, tool_name: str, arguments_json: str) -> str:
        try:
            args = json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError as exc:
            return f"Error: invalid JSON arguments: {exc}"

        try:
            if tool_name in {"read", "read_file"}:
                raw_path = str(args.get("path") or args["filename"])
                return self._read_workspace_file(raw_path)

            if tool_name in {"write", "write_file"}:
                raw_path = str(args.get("path") or args["filename"])
                return self._write_workspace_file(raw_path, str(args["content"]))

            if tool_name == "edit":
                return self._edit_workspace_file(
                    str(args["path"]),
                    str(args["old_text"]),
                    str(args["new_text"]),
                    replace_all=bool(args.get("replace_all", False)),
                )

            if tool_name == "apply_patch":
                changes = args.get("changes", [])
                if not isinstance(changes, list):
                    return "Error: 'changes' must be a list."
                return self._apply_workspace_patch(changes)

            if tool_name == "memory_search":
                return search_memory(self.settings.workspace_dir, str(args["query"]))

            if tool_name == "memory_get":
                return get_memory_slice(
                    self.settings.workspace_dir,
                    str(args["path"]),
                    int(args["start_line"]),
                    int(args["end_line"]),
                )

            if tool_name == "memory_append":
                return append_memory(
                    self.settings.workspace_dir,
                    str(args["path"]),
                    str(args["content"]),
                )

            if tool_name == "find":
                pattern = args.get("pattern")
                return self._find_workspace_files(
                    None if pattern is None else str(pattern)
                )

            if tool_name == "ls":
                return self._list_workspace_dir(
                    None if args.get("path") is None else str(args.get("path")),
                    recursive=bool(args.get("recursive", False)),
                )

            if tool_name == "grep":
                return self._grep_workspace(
                    str(args["pattern"]),
                    None if args.get("glob") is None else str(args.get("glob")),
                )

            if tool_name in {"exec", "execute_dangerous_command"}:
                return self._execute_workspace_command(str(args.get("command", "")))

            if tool_name == "ask_human_for_confirmation":
                reason = str(args.get("reason", "No reason provided."))
                command = str(args.get("command", ""))
                normalized_command, _ = self.command_policy.normalize_command(command)

                self._emit_event(
                    "approval_requested",
                    reason=reason,
                    command=normalized_command,
                )
                print(f"\n[Agent asks human] {reason}")
                print(f"Command for one-time approval: {normalized_command}")
                human_response = input("Your response (Approve/Reject/Modify): ").strip()
                lowered = human_response.lower()

                self._emit_event(
                    "approval_response",
                    command=normalized_command,
                    response=human_response,
                )
                if lowered.startswith("approve"):
                    self.command_policy.approve_once(command)
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

    def run(
        self,
        user_task: str,
        *,
        echo: bool = True,
        event_handler: EventHandler | None = None,
        prior_messages: tuple[dict[str, str], ...] = (),
    ) -> str:
        system_prompt = self.build_system_prompt()
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(prior_messages)
        messages.append({"role": "user", "content": user_task})
        steps_used = 0
        finished = False
        self._event_handler = event_handler
        self.last_run_report = None
        self._emit_event(
            "run_started",
            model=self.settings.model,
            max_steps=self.settings.max_steps,
            temperature=self.settings.temperature,
            run_mode=self.settings.run_mode,
            activated_skills=[skill.slug for skill in self.activated_skills],
            workspace_context_files=list(self.last_workspace_context_files),
            runtime_metadata=self.last_runtime_metadata,
            prior_message_count=len(prior_messages),
        )
        self._emit_event("user_task", content=user_task)

        if echo:
            print(f"User Task: {user_task}")

        try:
            client = self._get_client()
            for step in range(1, self.settings.max_steps + 1):
                steps_used = step
                if echo:
                    print(f"\n--- API Call {step} ---")

                self._emit_event("api_call_started", step=step)
                response = client.chat.completions.create(
                    model=self.settings.model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=self.settings.temperature,
                )

                message = response.choices[0].message
                dumped_message = message.model_dump(exclude_none=True)
                messages.append(dumped_message)
                self._emit_event("assistant_message", step=step, message=dumped_message)

                if not message.tool_calls:
                    final_text = message.content or ""
                    result_type = self._classify_final_response(final_text)
                    self._set_run_report(
                        status="completed",
                        result_type=result_type,
                        steps_used=step,
                        final_answer=final_text,
                        error=None,
                    )
                    self._emit_event(
                        "final_answer",
                        step=step,
                        content=final_text,
                        result_type=result_type,
                    )
                    self._emit_event(
                        "run_finished",
                        status="completed",
                        result_type=result_type,
                        steps_used=step,
                    )
                    finished = True
                    if echo:
                        print(f"\n[Final Answer]: {final_text}")
                    return final_text

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments or "{}"

                    self._emit_event(
                        "tool_call",
                        step=step,
                        tool=tool_name,
                        arguments=self._decode_tool_args(tool_args),
                    )

                    if echo:
                        print(f"[Tool Execution] -> {tool_name}({tool_args})")

                    result = self.execute_tool(tool_name, tool_args)
                    self._emit_event(
                        "tool_result",
                        step=step,
                        tool=tool_name,
                        content=result,
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

            error = (
                f"Agent exceeded max steps ({self.settings.max_steps}) without final answer"
            )
            self._set_run_report(
                status="failed",
                result_type="failure",
                steps_used=steps_used,
                final_answer=None,
                error=error,
            )
            self._emit_event("run_failed", error=error, steps_used=steps_used)
            self._emit_event(
                "run_finished",
                status="failed",
                result_type="failure",
                steps_used=steps_used,
                error=error,
            )
            finished = True
            raise RuntimeError(error)
        except Exception as exc:
            if not finished:
                error = f"{type(exc).__name__}: {exc}"
                self._set_run_report(
                    status="failed",
                    result_type="failure",
                    steps_used=steps_used,
                    final_answer=None,
                    error=error,
                )
                self._emit_event("run_failed", error=error, steps_used=steps_used)
                self._emit_event(
                    "run_finished",
                    status="failed",
                    result_type="failure",
                    steps_used=steps_used,
                    error=error,
                )
            raise
        finally:
            self._event_handler = None
