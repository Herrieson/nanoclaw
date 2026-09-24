#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections.abc import Iterable
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


ADAPTER_NAME = "nanoclaw-codex-adapter"
CAPTURE_LIMIT_BYTES = 2_000_000


def main(argv: list[str] | None = None) -> int:
    options = parse_args(argv)
    options.output.mkdir(parents=True, exist_ok=True)
    options.state.mkdir(parents=True, exist_ok=True)
    options.workspace.mkdir(parents=True, exist_ok=True)

    trace_path = options.output / "trace.jsonl"
    stdout_path = options.output / "codex_stdout.jsonl"
    stderr_path = options.output / "codex_stderr.log"
    final_answer_path = options.output / "final_answer.md"
    started_at = time.monotonic()

    task_text = options.task.read_text(encoding="utf-8")
    input_dir = options.task.parent
    runner_request = read_json(input_dir / "runner_request.json", {})
    prior_messages = read_json(input_dir / "prior_messages.json", [])
    resolved_task = read_json(options.resolved_task, {})

    env = build_codex_env(options, runner_request)
    config_path = write_codex_config(options, env, runner_request)
    materialize_agents_file(options.workspace)
    message = build_message(task_text, prior_messages, options.workspace, env)
    command = env.get("NANOCLAW_CODEX_CLI", "codex")
    args = build_codex_args(
        output_last_message=final_answer_path,
        workspace=options.workspace,
        env=env,
    )

    append_trace(
        trace_path,
        {
            "type": "adapter_started",
            "adapter": ADAPTER_NAME,
            "task_id": runner_request.get("task_id") or resolved_task.get("id"),
            "run_id": runner_request.get("run_id"),
            "turn": runner_request.get("turn"),
            "codex_home": env.get("CODEX_HOME"),
            "config_path": str(config_path),
        },
    )
    append_trace(
        trace_path,
        {
            "type": "codex_started",
            "command": redact_command(command, args),
            "cwd": str(options.workspace),
        },
    )

    result = run_command(
        command,
        args,
        cwd=options.workspace,
        env=env,
        stdin=message,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
    copy_codex_events_to_trace(stdout_path, trace_path)

    extraction = extract_final_answer(
        final_answer_path=final_answer_path,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    final_answer = ensure_trailing_newline(extraction["content"])
    final_answer_path.write_text(final_answer, encoding="utf-8")

    metadata = {
        "adapter": ADAPTER_NAME,
        "framework": "openai-codex",
        "command": redact_command(command, args),
        "cwd": str(options.workspace),
        "codex_home": env.get("CODEX_HOME"),
        "config_path": str(config_path),
        "exit_code": result.returncode,
        "final_answer_strategy": extraction["strategy"],
        "final_answer_bytes": len(final_answer.encode("utf-8")),
        "stdout_file": stdout_path.name,
        "stderr_file": stderr_path.name,
        "duration_ms": int((time.monotonic() - started_at) * 1000),
    }
    (options.output / "runner_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    append_trace(
        trace_path,
        {
            "type": "codex_finished",
            "exit_code": result.returncode,
            "final_answer_strategy": extraction["strategy"],
            "duration_ms": metadata["duration_ms"],
        },
    )
    return result.returncode


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a nanoclaw task with OpenAI Codex CLI.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--resolved-task", required=True, type=Path, dest="resolved_task")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    return parser.parse_args(argv)


def build_codex_env(options: argparse.Namespace, runner_request: dict[str, Any]) -> dict[str, str]:
    env = dict(os.environ)
    state_home = options.state / "home"
    codex_home = state_home / ".codex"
    env["HOME"] = str(state_home)
    env["CODEX_HOME"] = env.get("CODEX_HOME") or str(codex_home)
    env["XDG_CONFIG_HOME"] = env.get("XDG_CONFIG_HOME") or str(options.state / "xdg" / "config")
    env["XDG_STATE_HOME"] = env.get("XDG_STATE_HOME") or str(options.state / "xdg" / "state")
    env["XDG_CACHE_HOME"] = env.get("XDG_CACHE_HOME") or str(options.state / "xdg" / "cache")
    env["CI"] = env.get("CI") or "true"
    env["NO_COLOR"] = env.get("NO_COLOR") or "1"

    if not env.get("NANOCLAW_MODEL") and runner_request.get("model"):
        env["NANOCLAW_MODEL"] = str(runner_request["model"])
    if env.get("NANOCLAW_CODEX_MODEL") and not env.get("NANOCLAW_MODEL"):
        env["NANOCLAW_MODEL"] = env["NANOCLAW_CODEX_MODEL"]
    if env.get("NANOCLAW_BASE_URL") and not env.get("OPENAI_BASE_URL"):
        env["OPENAI_BASE_URL"] = env["NANOCLAW_BASE_URL"]
    if env.get("NANOCLAW_CODEX_BASE_URL") and not env.get("OPENAI_BASE_URL"):
        env["OPENAI_BASE_URL"] = env["NANOCLAW_CODEX_BASE_URL"]

    for directory in [
        state_home,
        Path(env["CODEX_HOME"]),
        Path(env["XDG_CONFIG_HOME"]),
        Path(env["XDG_STATE_HOME"]),
        Path(env["XDG_CACHE_HOME"]),
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    return env


def write_codex_config(
    options: argparse.Namespace,
    env: dict[str, str],
    runner_request: dict[str, Any],
) -> Path:
    codex_home = Path(env["CODEX_HOME"])
    codex_home.mkdir(parents=True, exist_ok=True)
    config_path = codex_home / "config.toml"

    model = resolve_model(env, runner_request)
    base_url = env.get("NANOCLAW_CODEX_BASE_URL") or env.get("NANOCLAW_BASE_URL") or env.get("OPENAI_BASE_URL")
    provider = env.get("NANOCLAW_CODEX_MODEL_PROVIDER") or ("nanoclaw" if base_url else "")
    approval_policy = env.get("NANOCLAW_CODEX_APPROVAL_POLICY") or "never"
    sandbox_mode = env.get("NANOCLAW_CODEX_SANDBOX") or "workspace-write"
    network_access = env.get("NANOCLAW_CODEX_NETWORK_ACCESS", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }

    lines: list[str] = [
        f"model = {toml_string(model)}",
        f"approval_policy = {toml_string(approval_policy)}",
        f"sandbox_mode = {toml_string(sandbox_mode)}",
        "",
        "[sandbox_workspace_write]",
        f"network_access = {toml_bool(network_access)}",
        "writable_roots = [\"/workspace\", \"/tmp\"]",
        "",
        f"[projects.{toml_string(str(options.workspace))}]",
        'trust_level = "trusted"',
    ]

    if provider:
        lines.insert(1, f"model_provider = {toml_string(provider)}")
        env_key = env.get("NANOCLAW_CODEX_API_KEY_ENV") or "OPENAI_API_KEY"
        lines.extend(
            [
                "",
                f"[model_providers.{provider}]",
                'name = "Nanoclaw OpenAI Compatible"',
                f"base_url = {toml_string(base_url or 'https://api.openai.com/v1')}",
                f"env_key = {toml_string(env_key)}",
                "requires_openai_auth = false",
            ]
        )
        wire_api = env.get("NANOCLAW_CODEX_WIRE_API", "").strip() or "chat"
        if wire_api:
            lines.append(f"wire_api = {toml_string(wire_api)}")

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config_path


def resolve_model(env: dict[str, str], runner_request: dict[str, Any]) -> str:
    return (
        env.get("NANOCLAW_CODEX_MODEL")
        or env.get("NANOCLAW_MODEL")
        or str(runner_request.get("model") or "")
        or "gpt-5-codex"
    )


def build_codex_args(
    *,
    output_last_message: Path,
    workspace: Path,
    env: dict[str, str],
) -> list[str]:
    args = [
        "exec",
        "--json",
        "--color",
        "never",
        "--skip-git-repo-check",
        "-c",
        f"approval_policy={toml_string(env.get('NANOCLAW_CODEX_APPROVAL_POLICY') or 'never')}",
        "-c",
        f"sandbox_mode={toml_string(env.get('NANOCLAW_CODEX_SANDBOX') or 'workspace-write')}",
        "--output-last-message",
        str(output_last_message),
        "-C",
        str(workspace),
    ]

    if env.get("NANOCLAW_CODEX_EPHEMERAL", "1") != "0":
        args.append("--ephemeral")
    if env.get("NANOCLAW_CODEX_IGNORE_RULES") == "1":
        args.append("--ignore-rules")
    if env.get("NANOCLAW_CODEX_IGNORE_USER_CONFIG") == "1":
        args.append("--ignore-user-config")

    model = resolve_model(env, {})
    if model:
        args.extend(["--model", model])

    if env.get("NANOCLAW_CODEX_YOLO") == "1":
        args.append("--dangerously-bypass-approvals-and-sandbox")
    elif env.get("NANOCLAW_CODEX_FULL_AUTO") == "1":
        args.append("--full-auto")
    else:
        args.extend(["--sandbox", env.get("NANOCLAW_CODEX_SANDBOX") or "workspace-write"])

    profile = env.get("NANOCLAW_CODEX_PROFILE")
    if profile:
        args.extend(["--profile", profile])

    args.append("-")
    return args


def build_message(task_text: str, prior_messages: Any, workspace: Path, env: dict[str, str]) -> str:
    parts: list[str] = []
    if env.get("NANOCLAW_CODEX_INCLUDE_PRIOR_MESSAGES", "1") != "0":
        parts.extend(format_prior_messages(prior_messages))
    skill_instructions = build_skill_instructions(workspace)
    if skill_instructions:
        parts.append(skill_instructions)
    parts.append(f"[USER]\n{task_text}" if parts else task_text)
    return "\n\n".join(part for part in parts if part.strip())


def format_prior_messages(prior_messages: Any) -> list[str]:
    if not isinstance(prior_messages, list):
        return []
    parts: list[str] = []
    for message in prior_messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "message").upper()
        content = str(message.get("content") or "")
        if content.strip():
            parts.append(f"[{role}]\n{content}")
    return parts


def build_skill_instructions(workspace: Path) -> str:
    skill_root = workspace / ".skills"
    if not skill_root.exists() or not skill_root.is_dir():
        return ""
    skills: list[str] = []
    for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir()):
        skill_doc = skill_dir / "SKILL.md"
        if skill_doc.exists():
            skills.append(f"- {skill_dir.name}: .skills/{skill_dir.name}/SKILL.md")
    if not skills:
        return ""
    return "\n".join(
        [
            "[SYSTEM]",
            "Available task-local skills are installed under `/workspace/.skills`.",
            "Before using a skill, read its SKILL.md and follow it. Use only skills relevant to the task.",
            "Available skills:",
            *skills,
        ]
    )


def materialize_agents_file(workspace: Path) -> None:
    agents_path = workspace / "AGENTS.md"
    if agents_path.exists():
        return
    skill_root = workspace / ".skills"
    lines = [
        "# Nanoclaw Runner Instructions",
        "",
        "Work only inside this task workspace unless the user explicitly asks otherwise.",
        "Create or edit the files requested by the task prompt.",
    ]
    if skill_root.exists() and any(skill_root.iterdir()):
        lines.extend(
            [
                "",
                "Task-local skills are available in `.skills/`.",
                "Read the relevant `SKILL.md` before using a skill.",
            ]
        )
    agents_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_command(
    command: str,
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    stdin: str,
    stdout_path: Path,
    stderr_path: Path,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            [command, *args],
            input=stdin,
            check=False,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            errors="replace",
        )
    except FileNotFoundError as exc:
        result = subprocess.CompletedProcess(
            [command, *args],
            returncode=127,
            stdout="",
            stderr=str(exc),
        )

    stdout_path.write_text(result.stdout or "", encoding="utf-8")
    stderr_path.write_text(result.stderr or "", encoding="utf-8")
    return result


def extract_final_answer(*, final_answer_path: Path, stdout: str, stderr: str) -> dict[str, str]:
    if final_answer_path.exists():
        content = final_answer_path.read_text(encoding="utf-8", errors="replace")
        if content.strip():
            return {"strategy": "output_last_message", "content": content}

    jsonl_content = extract_final_answer_from_jsonl(stdout)
    if jsonl_content:
        return {"strategy": "stdout_jsonl", "content": jsonl_content}

    text = stdout.strip() or stderr.strip()
    if text:
        return {"strategy": "stdout_stderr_fallback", "content": text}
    return {"strategy": "empty", "content": ""}


def extract_final_answer_from_jsonl(stdout: str) -> str:
    candidates: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        candidates.extend(find_text_values(payload))
    return candidates[-1] if candidates else ""


def find_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return []
    if isinstance(value, list):
        found: list[str] = []
        for item in value:
            found.extend(find_text_values(item))
        return found
    if not isinstance(value, dict):
        return []

    found = []
    event_type = str(value.get("type") or "").lower()
    role = str(value.get("role") or "").lower()
    if role == "assistant" or "assistant" in event_type or "message" in event_type:
        for key in ("text", "content", "message"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                found.append(raw)

    for nested in value.values():
        found.extend(find_text_values(nested))
    return found


def copy_codex_events_to_trace(stdout_path: Path, trace_path: Path) -> None:
    if not stdout_path.exists():
        return
    for raw_line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            append_trace(trace_path, {"type": "codex_stdout_text", "content": truncate(line)})
            continue
        append_trace(trace_path, {"type": "codex_event", "event": payload})


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def append_trace(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def redact_command(command: str, args: Iterable[str]) -> list[str]:
    redacted = [command, *args]
    output = []
    skip_next = False
    for item in redacted:
        if skip_next:
            output.append("<redacted>")
            skip_next = False
            continue
        output.append(item)
        if item in {"--api-key", "--key", "--token"}:
            skip_next = True
    return output


def truncate(value: str, limit: int = CAPTURE_LIMIT_BYTES) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= limit:
        return value
    return encoded[:limit].decode("utf-8", errors="replace") + "\n[truncated]"


def toml_string(value: str) -> str:
    return json.dumps(str(value))


def toml_bool(value: bool) -> str:
    return "true" if value else "false"


def ensure_trailing_newline(value: str) -> str:
    return value if value.endswith("\n") else value + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
