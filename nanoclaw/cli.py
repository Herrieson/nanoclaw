from __future__ import annotations

import argparse
import shutil
from dataclasses import replace
from pathlib import Path

from .config import DEFAULT_PROMPT_FILES, Settings
from .core_loop import MinimalClaw
from .prompt_sync import (
    list_prompt_versions,
    switch_prompt_version,
    sync_official_prompts,
    verify_manifest,
)
from .run_store import (
    RunRecorder,
    create_task_run,
    snapshot_workspace,
    utc_now_iso,
    write_final_answer,
    write_summary,
)
from .session_store import append_session_message, load_session_messages
from .skills import (
    SkillDefinition,
    auto_select_skills,
    discover_skills,
    resolve_requested_skills,
    serialize_skill,
)
from .task_loader import list_task_files, load_task_definition


def _parse_csv_files(raw: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _load_task(task: str | None, task_file: str | None) -> str:
    if task:
        return task
    if task_file:
        return Path(task_file).read_text(encoding="utf-8")
    raise ValueError("Provide --task or --task-file")


def _unique_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        stripped = value.strip()
        if not stripped or stripped in seen:
            continue
        seen.add(stripped)
        unique.append(stripped)
    return tuple(unique)


def _select_skills(
    *,
    task_text: str,
    settings: Settings,
    workspace_dir: Path | None = None,
    available_skill_names: tuple[str, ...] = (),
    requested_skill_names: tuple[str, ...],
    auto_skills: bool,
):
    catalog = discover_skills(
        workspace_dir or settings.workspace_dir,
        settings.extra_skill_dirs,
    )
    available_skills = catalog.skills
    if available_skill_names:
        available_skills = resolve_requested_skills(catalog.skills, available_skill_names)

    selected = list(resolve_requested_skills(available_skills, requested_skill_names))
    selected_slugs = {skill.slug for skill in selected}

    if auto_skills:
        for skill in auto_select_skills(available_skills, task_text):
            if skill.slug in selected_slugs:
                continue
            selected.append(skill)
            selected_slugs.add(skill.slug)

    return catalog, available_skills, tuple(selected)


def _materialize_skill_pool(
    workspace_dir: Path,
    available_skills: tuple[SkillDefinition, ...],
) -> None:
    skill_root = workspace_dir / ".skills"
    if skill_root.exists():
        shutil.rmtree(skill_root)
    if not available_skills:
        return

    skill_root.mkdir(parents=True, exist_ok=True)
    for skill in available_skills:
        source_dir = skill.source_path.parent
        destination_dir = skill_root / skill.slug
        shutil.copytree(source_dir, destination_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="nanoclaw minimal agent loop")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("bootstrap", help="Create minimal workspace files")

    sync_parser = sub.add_parser(
        "sync-prompts", help="Copy official prompt files from openclaw repo"
    )
    sync_parser.add_argument(
        "--repo-url",
        default="https://github.com/openclaw/openclaw.git",
        help="Source repository URL",
    )
    sync_parser.add_argument("--ref", default="main", help="Git ref/branch/tag")
    sync_parser.add_argument(
        "--files",
        default=",".join(DEFAULT_PROMPT_FILES),
        help="Comma separated file list, relative to repository root",
    )
    sync_parser.add_argument(
        "--output-dir",
        default=None,
        help="Output prompt directory (default: from Settings)",
    )
    sync_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force pull from remote and create/activate a new snapshot if content changed",
    )
    sync_parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List local prompt snapshots and show active one",
    )
    sync_parser.add_argument(
        "--switch-version",
        default=None,
        help="Activate an existing local prompt snapshot by version id",
    )

    verify_parser = sub.add_parser(
        "verify-prompts", help="Verify copied prompt files with manifest"
    )
    verify_parser.add_argument(
        "--manifest",
        default=None,
        help="Manifest path (default: <prompt_dir>/manifest.json)",
    )
    verify_parser.add_argument(
        "--base-dir",
        default=None,
        help="Base directory for prompt files (default: prompt_dir)",
    )

    run_parser = sub.add_parser("run", help="Run the minimal agent loop")
    run_parser.add_argument("--task", default=None, help="Task string")
    run_parser.add_argument("--task-file", default=None, help="Load task text from file")
    run_parser.add_argument(
        "--max-steps", type=int, default=None, help="Override max tool steps"
    )
    run_parser.add_argument(
        "--run-mode",
        default=None,
        help="Runtime mode to inject into the system prompt (default: from env/settings)",
    )
    run_parser.add_argument(
        "--session",
        default=None,
        help="Optional local session id for ad hoc conversation continuity",
    )
    run_parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Activate a skill by slug or name (repeatable)",
    )
    run_parser.add_argument(
        "--auto-skills",
        action="store_true",
        help="Auto-select skills by matching the task text to skill metadata",
    )

    list_tasks_parser = sub.add_parser("list-tasks", help="List task YAML files")
    list_tasks_parser.add_argument(
        "--tasks-dir",
        default="tasks",
        help="Directory containing task YAML files",
    )

    sub.add_parser("list-skills", help="List discovered skills")

    run_task_parser = sub.add_parser(
        "run-task", help="Run a task YAML against an asset-backed workspace"
    )
    run_task_parser.add_argument(
        "--task",
        required=True,
        help="Path to the task YAML file",
    )
    run_task_parser.add_argument(
        "--assets-dir",
        default="assets",
        help="Directory containing asset subdirectories",
    )
    run_task_parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory used to store run outputs",
    )
    run_task_parser.add_argument(
        "--run-mode",
        default=None,
        help="Override runtime mode for this task run",
    )
    run_task_parser.add_argument(
        "--session",
        default=None,
        help="Override local session id for this task run",
    )
    run_task_parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Activate an additional skill by slug or name (repeatable)",
    )
    run_task_parser.add_argument(
        "--auto-skills",
        action="store_true",
        help="Auto-select skills by matching the resolved task prompt to skill metadata",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "bootstrap":
        agent = MinimalClaw(settings)
        agent.bootstrap_workspace()
        print(f"Workspace ready: {settings.workspace_dir}")
        print(f"Prompt dir: {settings.prompt_dir}")
        return

    if args.command == "sync-prompts":
        output_dir = Path(args.output_dir) if args.output_dir else settings.prompt_dir

        if args.list_versions and args.switch_version:
            raise ValueError("--list-versions cannot be combined with --switch-version")
        if args.switch_version and args.refresh:
            raise ValueError("--switch-version cannot be combined with --refresh")

        if args.list_versions:
            versions = list_prompt_versions(output_dir)
            if not versions:
                print("No saved prompt versions")
                return
            for version in versions:
                marker = "*" if version.active else " "
                files_text = ", ".join(version.files) if version.files else "-"
                print(
                    f"{marker} {version.version_id} "
                    f"commit={version.source_commit} "
                    f"generated_at={version.generated_at_utc} "
                    f"files={files_text}"
                )
            return

        if args.switch_version:
            result = switch_prompt_version(
                output_dir=output_dir,
                version_id=args.switch_version,
            )
            print(f"Switched to version: {result.version_id}")
            print(f"Source commit: {result.source_commit}")
            print(f"Manifest: {result.manifest_path}")
            for file in result.copied_files:
                print(f"- {file}")
            return

        files = _parse_csv_files(args.files)
        if not files:
            raise ValueError("No files provided for --files")

        result = sync_official_prompts(
            output_dir=output_dir,
            files=files,
            repo_url=args.repo_url,
            ref=args.ref,
            force_refresh=args.refresh,
        )
        if result.used_cache and not result.pulled:
            print(f"Using cached prompt version: {result.version_id}")
        elif result.used_cache and result.pulled:
            print(f"No prompt changes. Reusing version: {result.version_id}")
        else:
            print(f"Created prompt version: {result.version_id}")
        print(f"Synced commit: {result.source_commit}")
        print(f"Manifest: {result.manifest_path}")
        for file in result.copied_files:
            print(f"- {file}")
        return

    if args.command == "verify-prompts":
        base_dir = Path(args.base_dir) if args.base_dir else settings.prompt_dir
        manifest = Path(args.manifest) if args.manifest else base_dir / "manifest.json"
        ok, errors = verify_manifest(manifest_path=manifest, base_dir=base_dir)
        if ok:
            print("Prompt manifest verification passed")
            return
        print("Prompt manifest verification failed")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(1)

    if args.command == "run":
        task = _load_task(args.task, args.task_file)
        if args.max_steps is not None or args.run_mode is not None:
            settings = replace(
                settings,
                max_steps=(
                    args.max_steps if args.max_steps is not None else settings.max_steps
                ),
                run_mode=args.run_mode or settings.run_mode,
            )

        requested_skills = _unique_strings(tuple(args.skill))
        catalog, available_skills, activated_skills = _select_skills(
            task_text=task,
            settings=settings,
            requested_skill_names=requested_skills,
            auto_skills=bool(args.auto_skills),
        )

        agent = MinimalClaw(
            settings,
            available_skills=available_skills,
            activated_skills=activated_skills,
        )
        agent.bootstrap_workspace()
        prior_messages = ()
        if args.session:
            prior_messages = load_session_messages(
                settings.workspace_dir,
                args.session,
                max_messages=settings.session_max_messages,
                max_chars=settings.session_max_chars,
            )
        if catalog.errors:
            print("Skill discovery warnings:")
            for error in catalog.errors:
                print(f"- {error.source_path}: {error.error}")
        if activated_skills:
            print("Activated skills:")
            for skill in activated_skills:
                print(f"- {skill.slug} ({skill.source_path})")
        final_text = agent.run(task, echo=True, prior_messages=prior_messages)
        report = agent.last_run_report
        if (
            args.session
            and report
            and report.status == "completed"
            and report.result_type == "final_answer"
        ):
            append_session_message(
                settings.workspace_dir,
                args.session,
                role="user",
                content=task,
            )
            if final_text:
                append_session_message(
                    settings.workspace_dir,
                    args.session,
                    role="assistant",
                    content=final_text,
                    result_type=report.result_type,
                )
        return

    if args.command == "list-tasks":
        task_files = list_task_files(Path(args.tasks_dir))
        if not task_files:
            print(f"No task files found in: {Path(args.tasks_dir)}")
            return

        for task_path in task_files:
            try:
                task = load_task_definition(task_path, settings)
                print(
                    f"{task.task_id} "
                    f"asset={task.asset} "
                    f"source={task.source_path}"
                )
            except Exception as exc:
                print(f"! invalid task: {task_path} ({exc})")
        return

    if args.command == "list-skills":
        catalog = discover_skills(settings.workspace_dir, settings.extra_skill_dirs)
        if not catalog.skills:
            print("No skills found")
        else:
            for skill in catalog.skills:
                print(f"{skill.slug} source={skill.source_path}")
                print(f"  name={skill.name}")
                print(f"  description={skill.description}")
        if catalog.errors:
            print("Skill discovery warnings:")
            for error in catalog.errors:
                print(f"- {error.source_path}: {error.error}")
        return

    if args.command == "run-task":
        task = load_task_definition(Path(args.task), settings)
        task_assets_root = Path(args.assets_dir).expanduser().resolve()
        results_root = Path(args.results_dir).expanduser().resolve()
        skill_workspace_dir = task_assets_root / task.asset
        requested_skills = _unique_strings(task.skills.include + tuple(args.skill))
        auto_skills = task.skills.auto or bool(args.auto_skills)
        catalog, available_skills, activated_skills = _select_skills(
            task_text=task.prompt,
            settings=settings,
            workspace_dir=skill_workspace_dir,
            available_skill_names=task.skills.available,
            requested_skill_names=requested_skills,
            auto_skills=auto_skills,
        )
        resolved_payload = task.resolved_payload(
            activated_skills=tuple(serialize_skill(skill) for skill in activated_skills)
        )
        layout = create_task_run(
            task,
            assets_root=task_assets_root,
            results_root=results_root,
            resolved_payload=resolved_payload,
        )
        run_mode = args.run_mode or task.runtime.mode
        task_session = args.session or task.runtime.session
        task_settings = replace(
            settings,
            workspace_dir=layout.workspace_dir,
            model=task.runtime.model,
            workspace_context_files=task.runtime.workspace_context_files,
            run_mode=run_mode,
            memory_policy=task.runtime.memory_policy,
            max_steps=task.runtime.max_steps,
            temperature=task.runtime.temperature,
        )

        agent = MinimalClaw(
            task_settings,
            available_skills=available_skills,
            activated_skills=activated_skills,
        )
        _materialize_skill_pool(layout.workspace_dir, available_skills)
        agent.bootstrap_workspace()
        snapshot_workspace(layout.workspace_dir, layout.before_dir)

        recorder = RunRecorder(layout)
        started_at = utc_now_iso()
        run_error: Exception | None = None
        prior_messages = ()
        session_root = results_root / task.task_id
        if task_session:
            prior_messages = load_session_messages(
                session_root,
                task_session,
                max_messages=settings.session_max_messages,
                max_chars=settings.session_max_chars,
            )

        try:
            final_text = agent.run(
                task.prompt,
                echo=True,
                event_handler=recorder.record_event,
                prior_messages=prior_messages,
            )
            write_final_answer(layout.final_answer_path, final_text)
        except Exception as exc:
            run_error = exc
            failure_text = f"{type(exc).__name__}: {exc}"
            write_final_answer(layout.final_answer_path, failure_text)
        finally:
            snapshot_workspace(layout.workspace_dir, layout.after_dir)
            finished_at = utc_now_iso()
            report = agent.last_run_report
            if (
                task_session
                and report
                and report.status == "completed"
                and report.result_type == "final_answer"
            ):
                append_session_message(
                    session_root,
                    task_session,
                    role="user",
                    content=task.prompt,
                )
                if report.final_answer:
                    append_session_message(
                        session_root,
                        task_session,
                        role="assistant",
                        content=report.final_answer,
                        result_type=report.result_type,
                    )
            summary = {
                "task_id": task.task_id,
                "task_name": task.name,
                "description": task.description,
                "asset": task.asset,
                "asset_dir": str(layout.asset_dir),
                "task_file": str(task.source_path),
                "run_id": layout.run_id,
                "result_dir": str(layout.run_dir),
                "status": report.status if report else "failed",
                "result_type": report.result_type if report else "failure",
                "error": report.error if report else None,
                "model": task_settings.model,
                "max_steps": task_settings.max_steps,
                "temperature": task_settings.temperature,
                "run_mode": task_settings.run_mode,
                "memory_policy": task_settings.memory_policy,
                "session": task_session,
                "workspace_context_files": list(agent.last_workspace_context_files),
                "runtime_metadata": agent.last_runtime_metadata,
                "skills": {
                    "available": [
                        serialize_skill(skill) for skill in available_skills
                    ],
                    "requested": list(requested_skills),
                    "auto": auto_skills,
                    "activated": [
                        serialize_skill(skill) for skill in activated_skills
                    ],
                },
                "steps_used": report.steps_used if report else 0,
                "started_at": started_at,
                "finished_at": finished_at,
                "final_answer_file": layout.final_answer_path.name,
                "trace_file": layout.trace_path.name,
                "before_state_dir": layout.before_dir.name,
                "after_state_dir": layout.after_dir.name,
            }
            write_summary(layout.summary_path, summary)

        print(f"Run dir: {layout.run_dir}")
        print(f"Trace: {layout.trace_path}")
        print(f"Summary: {layout.summary_path}")
        print(f"Final answer: {layout.final_answer_path}")
        if catalog.errors:
            print("Skill discovery warnings:")
            for error in catalog.errors:
                print(f"- {error.source_path}: {error.error}")
        if activated_skills:
            print("Activated skills:")
            for skill in activated_skills:
                print(f"- {skill.slug} ({skill.source_path})")
        if run_error is not None:
            raise SystemExit(f"Task run failed: {run_error}")
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
