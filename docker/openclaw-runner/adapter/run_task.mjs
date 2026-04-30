#!/usr/bin/env node
import { createWriteStream } from "node:fs";
import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";

const ADAPTER_NAME = "nanoclaw-openclaw-adapter";
const CAPTURE_LIMIT_BYTES = 2_000_000;

async function main() {
  const options = parseArgs(process.argv.slice(2));
  await ensureDir(options.output);
  await ensureDir(options.state);
  await ensureDir(options.workspace);

  const tracePath = path.join(options.output, "trace.jsonl");
  const startedAt = Date.now();
  const taskText = await fs.readFile(options.task, "utf8");
  const inputDir = path.dirname(options.task);
  const runnerRequest = await readJsonIfExists(
    path.join(inputDir, "runner_request.json"),
    {},
  );
  const priorMessages = await readJsonIfExists(
    path.join(inputDir, "prior_messages.json"),
    [],
  );
  const resolvedTask = await readJsonIfExists(options.resolvedTask, {});

  const env = await buildOpenClawEnv(options, runnerRequest);
  const message = buildMessage(taskText, priorMessages, env);
  const sessionId = resolveSessionId(runnerRequest, resolvedTask, env);
  const command = env.NANOCLAW_OPENCLAW_CLI || "openclaw";
  const args = buildOpenClawArgs(message, sessionId, env);

  await appendTrace(tracePath, {
    type: "adapter_started",
    adapter: ADAPTER_NAME,
    task_id: runnerRequest.task_id ?? resolvedTask.id ?? null,
    run_id: runnerRequest.run_id ?? null,
    turn: runnerRequest.turn ?? null,
    session_id: sessionId,
  });

  const onboarding = await maybeOnboardOpenClaw({
    command,
    env,
    workspace: options.workspace,
    outputDir: options.output,
    tracePath,
  });

  const stdoutPath = path.join(options.output, "openclaw_stdout.log");
  const stderrPath = path.join(options.output, "openclaw_stderr.log");

  await appendTrace(tracePath, {
    type: "openclaw_started",
    command: redactCommandForTrace(command, args),
    cwd: options.workspace,
  });

  const result = await runCommand(command, args, {
    cwd: options.workspace,
    env,
    stdoutPath,
    stderrPath,
  });

  const extraction = extractFinalAnswer(result.stdout, result.stderr);
  const finalAnswer = ensureTrailingNewline(extraction.content);
  await fs.writeFile(path.join(options.output, "final_answer.md"), finalAnswer, "utf8");

  const metadata = {
    adapter: ADAPTER_NAME,
    framework: "openclaw",
    command: redactCommandForTrace(command, args),
    cwd: options.workspace,
    session_id: sessionId,
    exit_code: result.exitCode,
    signal: result.signal,
    error: result.error,
    final_answer_strategy: extraction.strategy,
    final_answer_bytes: Buffer.byteLength(finalAnswer, "utf8"),
    stdout_file: path.basename(stdoutPath),
    stderr_file: path.basename(stderrPath),
    onboarding,
    duration_ms: Date.now() - startedAt,
  };
  await fs.writeFile(
    path.join(options.output, "runner_metadata.json"),
    JSON.stringify(metadata, null, 2) + "\n",
    "utf8",
  );

  await appendTrace(tracePath, {
    type: "openclaw_finished",
    exit_code: result.exitCode,
    signal: result.signal,
    error: result.error,
    final_answer_strategy: extraction.strategy,
    duration_ms: Date.now() - startedAt,
  });

  process.exitCode = normalizeExitCode(result.exitCode, result.signal);
}

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      printUsageAndExit();
    }
    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }
    const key = arg.slice(2);
    const value = argv[index + 1];
    if (value === undefined || value.startsWith("--")) {
      throw new Error(`Missing value for ${arg}`);
    }
    index += 1;
    if (key === "resolved-task") {
      options.resolvedTask = value;
    } else if (["task", "workspace", "output", "state"].includes(key)) {
      options[key] = value;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  for (const key of ["task", "resolvedTask", "workspace", "output", "state"]) {
    if (!options[key]) {
      throw new Error(`Missing required argument: --${toKebabCase(key)}`);
    }
  }

  return {
    task: path.resolve(options.task),
    resolvedTask: path.resolve(options.resolvedTask),
    workspace: path.resolve(options.workspace),
    output: path.resolve(options.output),
    state: path.resolve(options.state),
  };
}

function printUsageAndExit() {
  process.stdout.write(
    [
      "Usage: run_task --task /input/task.md --resolved-task /input/resolved_task.json \\",
      "  --workspace /workspace --output /output --state /state",
      "",
    ].join("\n"),
  );
  process.exit(0);
}

function toKebabCase(value) {
  return value.replace(/[A-Z]/g, (match) => `-${match.toLowerCase()}`);
}

async function buildOpenClawEnv(options, runnerRequest) {
  const env = { ...process.env };
  if (!env.NANOCLAW_MODEL && runnerRequest.model) {
    env.NANOCLAW_MODEL = String(runnerRequest.model);
  }
  if (env.NANOCLAW_BASE_URL && !env.OPENAI_BASE_URL) {
    env.OPENAI_BASE_URL = env.NANOCLAW_BASE_URL;
  }
  if (env.NANOCLAW_BASE_URL && !env.CUSTOM_API_KEY && env.OPENAI_API_KEY) {
    env.CUSTOM_API_KEY = env.OPENAI_API_KEY;
  }

  if (env.NANOCLAW_OPENCLAW_ISOLATED_HOME !== "0") {
    const homeDir = env.NANOCLAW_OPENCLAW_HOME || path.join(options.state, "home");
    const xdgDir = path.join(options.state, "xdg");
    env.HOME = homeDir;
    env.XDG_CONFIG_HOME = env.XDG_CONFIG_HOME || path.join(xdgDir, "config");
    env.XDG_STATE_HOME = env.XDG_STATE_HOME || path.join(xdgDir, "state");
    env.XDG_CACHE_HOME = env.XDG_CACHE_HOME || path.join(xdgDir, "cache");
    await ensureDir(homeDir);
    await ensureDir(env.XDG_CONFIG_HOME);
    await ensureDir(env.XDG_STATE_HOME);
    await ensureDir(env.XDG_CACHE_HOME);
  }

  return env;
}

function buildMessage(taskText, priorMessages, env) {
  if (
    env.NANOCLAW_OPENCLAW_INCLUDE_PRIOR_MESSAGES !== "1"
    || !Array.isArray(priorMessages)
    || priorMessages.length === 0
  ) {
    return taskText;
  }

  const history = priorMessages
    .filter((message) => message && typeof message === "object")
    .map((message) => {
      const role = String(message.role ?? "message").toUpperCase();
      const content = String(message.content ?? "");
      return `[${role}]\n${content}`;
    })
    .filter((message) => message.trim().length > 0)
    .join("\n\n");

  if (!history) {
    return taskText;
  }

  return `${history}\n\n[USER]\n${taskText}`;
}

function resolveSessionId(runnerRequest, resolvedTask, env) {
  const raw =
    env.NANOCLAW_OPENCLAW_SESSION_ID
    || [
      "nanoclaw",
      runnerRequest.task_id ?? resolvedTask.id ?? "task",
      runnerRequest.run_id ?? "run",
    ].join("-");
  return String(raw).replace(/[^a-zA-Z0-9_.:-]+/g, "-").slice(0, 180);
}

function buildOpenClawArgs(message, sessionId, env) {
  const args = ["agent", "--local", "--message", message, "--json"];

  if (env.NANOCLAW_OPENCLAW_AGENT) {
    args.push("--agent", env.NANOCLAW_OPENCLAW_AGENT);
  } else {
    args.push("--session-id", sessionId);
  }

  if (env.NANOCLAW_MODEL) {
    args.push("--model", env.NANOCLAW_MODEL);
  }
  if (env.NANOCLAW_OPENCLAW_THINKING) {
    args.push("--thinking", env.NANOCLAW_OPENCLAW_THINKING);
  }
  if (env.NANOCLAW_OPENCLAW_VERBOSE) {
    const verboseValue = env.NANOCLAW_OPENCLAW_VERBOSE === "1"
      ? "on"
      : env.NANOCLAW_OPENCLAW_VERBOSE === "0"
        ? "off"
        : env.NANOCLAW_OPENCLAW_VERBOSE;
    args.push("--verbose", verboseValue);
  }
  if (env.NANOCLAW_OPENCLAW_TIMEOUT) {
    args.push("--timeout", env.NANOCLAW_OPENCLAW_TIMEOUT);
  }

  return args;
}

async function maybeOnboardOpenClaw({ command, env, workspace, outputDir, tracePath }) {
  if (env.NANOCLAW_OPENCLAW_AUTO_ONBOARD === "0") {
    await appendTrace(tracePath, { type: "openclaw_onboard_skipped", reason: "disabled" });
    return { attempted: false, reason: "disabled" };
  }

  const configPath = path.join(env.HOME || "", ".openclaw", "openclaw.json");
  if (!env.HOME || await fileExists(configPath)) {
    const reason = env.HOME ? "config_exists" : "home_unset";
    await appendTrace(tracePath, { type: "openclaw_onboard_skipped", reason });
    return { attempted: false, reason };
  }

  const onboardArgs = buildOnboardArgs(env, workspace);
  if (!onboardArgs) {
    await appendTrace(tracePath, {
      type: "openclaw_onboard_skipped",
      reason: "no_supported_provider_env",
    });
    return { attempted: false, reason: "no_supported_provider_env" };
  }

  const stdoutPath = path.join(outputDir, "openclaw_onboard_stdout.log");
  const stderrPath = path.join(outputDir, "openclaw_onboard_stderr.log");

  await appendTrace(tracePath, {
    type: "openclaw_onboard_started",
    command: redactCommandForTrace(command, onboardArgs),
  });

  const result = await runCommand(command, onboardArgs, {
    cwd: env.HOME,
    env,
    stdoutPath,
    stderrPath,
  });

  await appendTrace(tracePath, {
    type: "openclaw_onboard_finished",
    exit_code: result.exitCode,
    signal: result.signal,
    error: result.error,
  });

  return {
    attempted: true,
    exit_code: result.exitCode,
    signal: result.signal,
    error: result.error,
    stdout_file: path.basename(stdoutPath),
    stderr_file: path.basename(stderrPath),
  };
}

function buildOnboardArgs(env, workspace) {
  const baseArgs = [
    "onboard",
    "--non-interactive",
    "--mode",
    "local",
    "--workspace",
    workspace,
    "--secret-input-mode",
    "ref",
    "--accept-risk",
    "--no-install-daemon",
    "--skip-daemon",
    "--skip-channels",
    "--skip-health",
    "--skip-search",
    "--skip-skills",
    "--skip-ui",
  ];

  if (env.NANOCLAW_BASE_URL && env.NANOCLAW_MODEL && env.CUSTOM_API_KEY) {
    return [
      ...baseArgs,
      "--auth-choice",
      "custom-api-key",
      "--custom-base-url",
      env.NANOCLAW_BASE_URL,
      "--custom-model-id",
      env.NANOCLAW_MODEL,
      "--custom-compatibility",
      env.NANOCLAW_OPENCLAW_CUSTOM_COMPATIBILITY || "openai",
    ];
  }

  if (env.OPENAI_API_KEY) {
    return [...baseArgs, "--auth-choice", "openai-api-key"];
  }

  return null;
}

async function runCommand(command, args, { cwd, env, stdoutPath, stderrPath }) {
  await ensureDir(path.dirname(stdoutPath));
  await ensureDir(path.dirname(stderrPath));

  return new Promise((resolve) => {
    const stdout = makeStreamCollector(stdoutPath);
    const stderr = makeStreamCollector(stderrPath);
    let spawnError = null;

    let child;
    try {
      child = spawn(command, args, {
        cwd,
        env,
        stdio: ["ignore", "pipe", "pipe"],
      });
    } catch (error) {
      spawnError = error;
      Promise.all([stdout.close(), stderr.close()]).then(() => {
        resolve({
          exitCode: 127,
          signal: null,
          error: error.message,
          stdout: "",
          stderr: error.message,
        });
      });
      return;
    }

    child.stdout.on("data", (chunk) => stdout.write(chunk));
    child.stderr.on("data", (chunk) => stderr.write(chunk));
    child.on("error", (error) => {
      spawnError = error;
    });
    child.on("close", (exitCode, signal) => {
      Promise.all([stdout.close(), stderr.close()]).then(() => {
        resolve({
          exitCode: spawnError ? 127 : exitCode,
          signal,
          error: spawnError ? spawnError.message : null,
          stdout: stdout.text,
          stderr: stderr.text,
        });
      });
    });
  });
}

function makeStreamCollector(filePath) {
  const stream = createWriteStream(filePath, { flags: "w" });
  let text = "";
  let capturedBytes = 0;

  return {
    get text() {
      return text;
    },
    write(chunk) {
      stream.write(chunk);
      if (capturedBytes >= CAPTURE_LIMIT_BYTES) {
        return;
      }
      const remaining = CAPTURE_LIMIT_BYTES - capturedBytes;
      const piece = chunk.length > remaining ? chunk.subarray(0, remaining) : chunk;
      text += piece.toString("utf8");
      capturedBytes += piece.length;
    },
    close() {
      return new Promise((resolve) => {
        stream.end(resolve);
      });
    },
  };
}

function extractFinalAnswer(stdout, stderr) {
  const whole = parseJson(stdout.trim());
  const wholeText = whole === null ? null : findTextCandidate(whole);
  if (wholeText) {
    return { content: wholeText, strategy: "json_stdout" };
  }

  const lines = stdout.split(/\r?\n/).filter((line) => line.trim().length > 0);
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const value = parseJson(lines[index].trim());
    if (value === null) {
      continue;
    }
    const text = findTextCandidate(value);
    if (text) {
      return { content: text, strategy: "jsonl_stdout" };
    }
  }

  const stdoutFallback = stdout.trim();
  if (stdoutFallback) {
    return { content: stdoutFallback, strategy: "stdout_fallback" };
  }

  const stderrFallback = stderr.trim();
  if (stderrFallback) {
    return { content: stderrFallback, strategy: "stderr_fallback" };
  }

  return { content: "", strategy: "empty" };
}

function findTextCandidate(value) {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed || null;
  }
  if (Array.isArray(value)) {
    const parts = value
      .map((item) => findTextCandidate(item))
      .filter((item) => item && item.trim().length > 0);
    return parts.length > 0 ? parts.join("\n") : null;
  }
  if (typeof value !== "object") {
    return null;
  }

  for (const key of [
    "final_answer",
    "finalAnswer",
    "answer",
    "reply",
    "response",
    "text",
    "content",
    "output",
    "message",
    "result",
    "summary",
  ]) {
    if (Object.hasOwn(value, key)) {
      const text = findTextCandidate(value[key]);
      if (text) {
        return text;
      }
    }
  }

  if (Array.isArray(value.choices)) {
    const text = findTextCandidate(value.choices);
    if (text) {
      return text;
    }
  }

  if (Array.isArray(value.messages)) {
    for (let index = value.messages.length - 1; index >= 0; index -= 1) {
      const message = value.messages[index];
      if (!message || typeof message !== "object") {
        continue;
      }
      if (!message.role || String(message.role).toLowerCase() === "assistant") {
        const text = findTextCandidate(message);
        if (text) {
          return text;
        }
      }
    }
  }

  for (const nestedValue of Object.values(value)) {
    const text = findTextCandidate(nestedValue);
    if (text) {
      return text;
    }
  }

  return null;
}

function parseJson(raw) {
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function redactCommandForTrace(command, args) {
  const redacted = [command];
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    redacted.push(arg);
    if (arg === "--message") {
      redacted.push("<task prompt>");
      index += 1;
    }
  }
  return redacted;
}

function normalizeExitCode(exitCode, signal) {
  if (Number.isInteger(exitCode)) {
    return exitCode;
  }
  if (signal) {
    return 128;
  }
  return 1;
}

function ensureTrailingNewline(value) {
  return value.endsWith("\n") ? value : `${value}\n`;
}

async function readJsonIfExists(filePath, fallback) {
  try {
    return JSON.parse(await fs.readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") {
      return fallback;
    }
    return fallback;
  }
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function ensureDir(dirPath) {
  await fs.mkdir(dirPath, { recursive: true });
}

async function appendTrace(tracePath, payload) {
  await fs.appendFile(
    tracePath,
    JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        ...payload,
      },
      null,
      0,
    ) + "\n",
    "utf8",
  );
}

main().catch(async (error) => {
  const outputFlagIndex = process.argv.indexOf("--output");
  if (outputFlagIndex >= 0 && process.argv[outputFlagIndex + 1]) {
    const outputDir = path.resolve(process.argv[outputFlagIndex + 1]);
    await ensureDir(outputDir);
    const message = `${error.name || "Error"}: ${error.message || String(error)}`;
    await fs.writeFile(path.join(outputDir, "final_answer.md"), `${message}\n`, "utf8");
    await appendTrace(path.join(outputDir, "trace.jsonl"), {
      type: "adapter_failed",
      adapter: ADAPTER_NAME,
      error: message,
    });
  }
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
