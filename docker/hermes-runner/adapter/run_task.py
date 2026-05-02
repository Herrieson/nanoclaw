#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


ADAPTER_NAME = "nanoclaw-hermes-adapter"


def main(argv: list[str] | None = None) -> int:
    options = parse_args(argv)
    options.output.mkdir(parents=True, exist_ok=True)
    options.state.mkdir(parents=True, exist_ok=True)
    options.workspace.mkdir(parents=True, exist_ok=True)

    trace_path = options.output / "trace.jsonl"
    started_at = time.monotonic()
    task_text = options.task.read_text(encoding="utf-8")
    input_dir = options.task.parent
    runner_request = read_json(input_dir / "runner_request.json", {})
    prior_messages = read_json(input_dir / "prior_messages.json", [])
    resolved_task = read_json(options.resolved_task, {})

    env = build_hermes_env(options, runner_request)
    message = build_message(task_text, prior_messages, env)
    command = env.get("NANOCLAW_HERMES_CLI", "hermes")
    args = build_hermes_args(message, env)
    stdout_path = options.output / "hermes_stdout.log"
    stderr_path = options.output / "hermes_stderr.log"

    append_trace(
        trace_path,
        {
            "type": "adapter_started",
            "adapter": ADAPTER_NAME,
            "task_id": runner_request.get("task_id") or resolved_task.get("id"),
            "run_id": runner_request.get("run_id"),
            "turn": runner_request.get("turn"),
            "mode": hermes_mode(env),
        },
    )
    append_trace(
        trace_path,
        {
            "type": "hermes_started",
            "command": redact_command(command, args),
            "cwd": str(options.workspace),
            "hermes_home": env.get("HERMES_HOME"),
        },
    )

    result = run_command(
        command,
        args,
        cwd=options.workspace,
        env=env,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
    extraction = extract_final_answer(result.stdout, result.stderr)
    final_answer = ensure_trailing_newline(extraction["content"])
    (options.output / "final_answer.md").write_text(final_answer, encoding="utf-8")
    state_cleanup = cleanup_hermes_state(env, options.state)

    metadata = {
        "adapter": ADAPTER_NAME,
        "framework": "hermes-agent",
        "command": redact_command(command, args),
        "cwd": str(options.workspace),
        "hermes_home": env.get("HERMES_HOME"),
        "mode": hermes_mode(env),
        "exit_code": result.returncode,
        "final_answer_strategy": extraction["strategy"],
        "final_answer_bytes": len(final_answer.encode("utf-8")),
        "stdout_file": stdout_path.name,
        "stderr_file": stderr_path.name,
        "state_cleanup": state_cleanup,
        "duration_ms": int((time.monotonic() - started_at) * 1000),
    }
    (options.output / "runner_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    append_trace(
        trace_path,
        {
            "type": "hermes_finished",
            "exit_code": result.returncode,
            "final_answer_strategy": extraction["strategy"],
            "state_cleanup": state_cleanup,
            "duration_ms": metadata["duration_ms"],
        },
    )
    return result.returncode


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a nanoclaw task with Hermes Agent.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--resolved-task", required=True, type=Path, dest="resolved_task")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    return parser.parse_args(argv)


def build_hermes_env(options: argparse.Namespace, runner_request: dict[str, Any]) -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("HERMES_HOME", str(options.state))
    env.setdefault("HOME", str(Path(env["HERMES_HOME"]) / "home"))
    env.setdefault("XDG_CONFIG_HOME", str(Path(env["HERMES_HOME"]) / "xdg" / "config"))
    env.setdefault("XDG_STATE_HOME", str(Path(env["HERMES_HOME"]) / "xdg" / "state"))
    env.setdefault("XDG_CACHE_HOME", str(Path(env["HERMES_HOME"]) / "xdg" / "cache"))

    if not env.get("NANOCLAW_MODEL") and runner_request.get("model"):
        env["NANOCLAW_MODEL"] = str(runner_request["model"])
    if env.get("NANOCLAW_MODEL") and not env.get("HERMES_INFERENCE_MODEL"):
        env["HERMES_INFERENCE_MODEL"] = env["NANOCLAW_MODEL"]
    if env.get("NANOCLAW_HERMES_MODEL") and not env.get("HERMES_INFERENCE_MODEL"):
        env["HERMES_INFERENCE_MODEL"] = env["NANOCLAW_HERMES_MODEL"]
    if env.get("NANOCLAW_HERMES_PROVIDER") and not env.get("HERMES_INFERENCE_PROVIDER"):
        env["HERMES_INFERENCE_PROVIDER"] = env["NANOCLAW_HERMES_PROVIDER"]
    if env.get("NANOCLAW_BASE_URL") and not env.get("OPENAI_BASE_URL"):
        env["OPENAI_BASE_URL"] = env["NANOCLAW_BASE_URL"]
    if env.get("NANOCLAW_BASE_URL") and not env.get("CUSTOM_BASE_URL"):
        env["CUSTOM_BASE_URL"] = env["NANOCLAW_BASE_URL"]
    elif env.get("OPENAI_BASE_URL") and not env.get("CUSTOM_BASE_URL"):
        env["CUSTOM_BASE_URL"] = env["OPENAI_BASE_URL"]
    if env.get("CUSTOM_BASE_URL") and not env.get("HERMES_INFERENCE_PROVIDER"):
        env["HERMES_INFERENCE_PROVIDER"] = "custom"

    for directory in [
        Path(env["HERMES_HOME"]),
        Path(env["HOME"]),
        Path(env["XDG_CONFIG_HOME"]),
        Path(env["XDG_STATE_HOME"]),
        Path(env["XDG_CACHE_HOME"]),
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    return env


def build_message(task_text: str, prior_messages: Any, env: dict[str, str]) -> str:
    if env.get("NANOCLAW_HERMES_INCLUDE_PRIOR_MESSAGES", "1") == "0":
        return task_text
    if not isinstance(prior_messages, list) or not prior_messages:
        return task_text

    history_parts: list[str] = []
    for message in prior_messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "message").upper()
        content = str(message.get("content") or "")
        if content.strip():
            history_parts.append(f"[{role}]\n{content}")

    if not history_parts:
        return task_text
    return "\n\n".join(history_parts + [f"[USER]\n{task_text}"])


def hermes_mode(env: dict[str, str]) -> str:
    explicit = env.get("NANOCLAW_HERMES_MODE", "").strip().lower()
    if explicit in {"chat", "oneshot"}:
        return explicit
    chat_only_vars = [
        "NANOCLAW_HERMES_TOOLSETS",
        "NANOCLAW_HERMES_SKILLS",
        "NANOCLAW_HERMES_MAX_TURNS",
        "NANOCLAW_HERMES_SOURCE",
        "NANOCLAW_HERMES_RESUME",
        "NANOCLAW_HERMES_CONTINUE",
    ]
    return "chat" if any(env.get(name) for name in chat_only_vars) else "oneshot"


def build_hermes_args(message: str, env: dict[str, str]) -> list[str]:
    mode = hermes_mode(env)
    args: list[str] = []

    if env.get("NANOCLAW_HERMES_RESUME"):
        args.extend(["--resume", env["NANOCLAW_HERMES_RESUME"]])
    if env.get("NANOCLAW_HERMES_CONTINUE"):
        args.extend(["--continue", env["NANOCLAW_HERMES_CONTINUE"]])
    if env.get("NANOCLAW_HERMES_YOLO") == "1":
        args.append("--yolo")
    if env.get("NANOCLAW_HERMES_IGNORE_USER_CONFIG") == "1":
        args.append("--ignore-user-config")
    if env.get("NANOCLAW_HERMES_IGNORE_RULES") == "1":
        args.append("--ignore-rules")

    provider = env.get("NANOCLAW_HERMES_PROVIDER") or env.get("HERMES_INFERENCE_PROVIDER")
    model = (
        env.get("NANOCLAW_HERMES_MODEL")
        or env.get("NANOCLAW_MODEL")
        or env.get("HERMES_INFERENCE_MODEL")
    )

    if mode == "chat":
        args.extend(["chat", "--quiet", "-q", message])
        if env.get("NANOCLAW_HERMES_SOURCE"):
            args.extend(["--source", env["NANOCLAW_HERMES_SOURCE"]])
        if env.get("NANOCLAW_HERMES_TOOLSETS"):
            args.extend(["--toolsets", env["NANOCLAW_HERMES_TOOLSETS"]])
        if env.get("NANOCLAW_HERMES_SKILLS"):
            args.extend(["--skills", env["NANOCLAW_HERMES_SKILLS"]])
        if env.get("NANOCLAW_HERMES_MAX_TURNS"):
            args.extend(["--max-turns", env["NANOCLAW_HERMES_MAX_TURNS"]])
    else:
        args.extend(["-z", message])

    if provider:
        args.extend(["--provider", provider])
    if model:
        args.extend(["--model", model])
    return args


def run_command(
    command: str,
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            [command, *args],
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


def cleanup_hermes_state(env: dict[str, str], state_dir: Path) -> dict[str, Any]:
    skills_dir = Path(env.get("HERMES_HOME") or state_dir) / "skills"
    payload: dict[str, Any] = {
        "skills_dir": str(skills_dir),
        "removed_skills": False,
    }
    if env.get("NANOCLAW_HERMES_KEEP_STATE_SKILLS") == "1":
        payload["skipped_reason"] = "disabled_by_env"
        return payload

    if not skills_dir.exists():
        payload["skipped_reason"] = "missing"
        return payload

    try:
        resolved_skills_dir = skills_dir.resolve(strict=False)
        resolved_state_dir = state_dir.resolve(strict=False)
        if not resolved_skills_dir.is_relative_to(resolved_state_dir):
            payload["skipped_reason"] = "outside_state_dir"
            return payload
    except OSError as exc:
        payload["skipped_reason"] = "path_resolution_failed"
        payload["error"] = str(exc)
        return payload

    try:
        shutil.rmtree(skills_dir)
    except OSError as exc:
        payload["skipped_reason"] = "remove_failed"
        payload["error"] = str(exc)
        return payload

    payload["removed_skills"] = True
    return payload


def extract_final_answer(stdout: str, stderr: str) -> dict[str, str]:
    stdout_clean = strip_ansi(stdout).strip()
    stderr_clean = strip_ansi(stderr).strip()
    if stdout_clean:
        return {"content": stdout_clean, "strategy": "stdout"}
    if stderr_clean:
        return {"content": stderr_clean, "strategy": "stderr_fallback"}
    return {"content": "", "strategy": "empty"}


def strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", value)


def redact_command(command: str, args: list[str]) -> list[str]:
    redacted = [command]
    redact_next = False
    for arg in args:
        if redact_next:
            redacted.append("<task prompt>")
            redact_next = False
            continue
        redacted.append(arg)
        if arg in {"-z", "-q", "--query"}:
            redact_next = True
    return redacted


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def append_trace(path: Path, payload: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def ensure_trailing_newline(value: str) -> str:
    return value if value.endswith("\n") else f"{value}\n"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        output_dir = None
        if "--output" in sys.argv:
            index = sys.argv.index("--output")
            if index + 1 < len(sys.argv):
                output_dir = Path(sys.argv[index + 1])
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            message = f"{type(exc).__name__}: {exc}"
            (output_dir / "final_answer.md").write_text(message + "\n", encoding="utf-8")
            append_trace(
                output_dir / "trace.jsonl",
                {
                    "type": "adapter_failed",
                    "adapter": ADAPTER_NAME,
                    "error": message,
                },
            )
        raise
