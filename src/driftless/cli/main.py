"""driftless — root CLI application.

Commands: init, status, verify, review, finish
Subcommand groups: work, change
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from driftless import __version__
from driftless.cli import change as change_cli
from driftless.cli import work as work_cli
from driftless.cli.utils import resolve_work
from driftless.git.adapter import GitAdapter
from driftless.logging import setup_logging
from driftless.openspec.adapter import OpenSpecAdapter, OpenSpecNotFound
from driftless.output import renderer
from driftless.work import service as work_service
from driftless.work.models import WorkStatus

app = typer.Typer(
    name="driftless",
    help="AI-native SDLC outer-loop CLI for coding agents.",
    no_args_is_help=True,
    add_completion=False,
)

# Register subcommand groups
app.add_typer(work_cli.app, name="work")
app.add_typer(change_cli.app, name="change")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"driftless {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-V",
            help="Enable verbose debug logging to stderr.",
        ),
    ] = False,
) -> None:
    """Driftless — AI-native SDLC workflow CLI.

    Used by coding agents (Claude Code, etc.) to manage engineering work
    across the outer-loop lifecycle: Work → OpenSpec → Git → Verify → Done.
    """
    setup_logging(verbose=verbose)


@app.command("init")
def cmd_init(
    tools: Annotated[
        str,
        typer.Option(
            "--tools",
            help="AI tools to configure in OpenSpec (e.g. 'claude,cursor').",
        ),
    ] = "claude",
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing CLAUDE.md skill file."),
    ] = False,
) -> None:
    """Initialize Driftless and OpenSpec in the current repository."""
    cwd = Path.cwd()

    # 1. Verify git repository
    git = GitAdapter(cwd)
    if not git.is_repo():
        renderer.error_with_hint(
            "Not inside a git repository.",
            "Initialize git first:\n  git init\n\nThen retry:\n  driftless init",
        )
        return

    renderer.success(f"Git repository detected: {git.root()}")
    renderer.info(f"Branch: {git.branch()}")

    # 2. Detect OpenSpec
    openspec = OpenSpecAdapter(cwd)
    available, version = openspec.detect()
    if not available:
        renderer.error_with_hint("OpenSpec not found.", OpenSpecNotFound.INSTALL_HINT)
        return

    renderer.success(f"OpenSpec detected: {version}")

    # 3. Initialize OpenSpec if needed
    if openspec.is_initialized():
        renderer.info("OpenSpec already initialized (openspec/ directory exists).")
    else:
        renderer.info(f"Initializing OpenSpec with tools: {tools} ...")
        try:
            openspec.init(tools=tools)
            renderer.success("OpenSpec initialized.")
        except Exception as e:
            renderer.error_with_hint(
                f"OpenSpec initialization failed: {e}",
                "Try running manually:\n  npx @fission-ai/openspec init",
            )
            return

    # 4. Create .driftless/ directory structure and config
    driftless_dir = cwd / ".driftless"
    driftless_dir.mkdir(exist_ok=True)
    (driftless_dir / "work").mkdir(exist_ok=True)

    config = {
        "version": __version__,
        "initialized_at": datetime.now(tz=UTC).isoformat(),
        "openspec_tools": tools,
        "git_root": str(git.root()),
    }
    (driftless_dir / "config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    renderer.success(f"Driftless state directory created: {driftless_dir}")

    # 5. Write agent skills (CLAUDE.md & AGENTS.md universal skill standard)
    from driftless.agents.manager import install_agent_skills

    installed_skills = install_agent_skills(cwd, tools=tools, force=force)
    for skill_path in installed_skills:
        renderer.success(f"Agent skill written: {skill_path.name}")

    renderer.print_human(
        [
            "",
            "[bold green]Driftless initialized.[/bold green]",
            "",
            "Next steps:",
            '  driftless work create "<description>"',
            "  driftless status",
            "",
        ]
    )


@app.command("status")
def cmd_status(
    work_id: Annotated[
        str | None,
        typer.Option("--work", "-w", help="Work ID. Defaults to active work."),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Show current Driftless + OpenSpec + Git status."""
    cwd = Path.cwd()
    git = GitAdapter(cwd)
    openspec = OpenSpecAdapter(cwd)

    work = resolve_work(work_id=work_id, required=False)
    git_state = git.status_summary()

    openspec_state: dict = {"status": "—"}
    if work and work.openspec_change:
        opsx_available, _ = openspec.detect()
        if opsx_available and openspec.is_initialized():
            openspec_state = openspec.status(work.openspec_change)
            openspec_state.setdefault("status", "ready")
        else:
            openspec_state = {"status": "not-initialized"}

    def _next_message(w) -> str:
        if not w:
            return "create work with: driftless work create '<description>'"
        status_map = {
            WorkStatus.CREATED: "run 'driftless change create <name>' to start OpenSpec inner loop",
            WorkStatus.SPECIFYING: "author proposal.md in openspec/changes/<name>/",
            WorkStatus.PLANNING: "author design.md and tasks.md",
            WorkStatus.IMPLEMENTING: "implement the work, then run 'driftless verify'",
            WorkStatus.VERIFYING: "run 'driftless verify' — if pass, run 'driftless review'",
            WorkStatus.REVIEW: "run 'driftless review' then 'driftless finish' when approved",
            WorkStatus.DELIVERY: "run 'driftless finish' to complete",
            WorkStatus.DONE: "work is complete",
        }
        return status_map.get(w.status, "check driftless status")

    status_data = {
        "work": work.model_dump(mode="json") if work else {},
        "git": git_state,
        "openspec": openspec_state,
        "message": _next_message(work),
    }

    if json_output:
        renderer.print_json(status_data)
    else:
        renderer.print_status_human(status_data)


@app.command("verify")
def cmd_verify(
    work_id: Annotated[
        str | None,
        typer.Option("--work", "-w", help="Work ID. Defaults to active work."),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Verify work readiness (Git clean, OpenSpec valid)."""
    cwd = Path.cwd()
    git = GitAdapter(cwd)
    openspec = OpenSpecAdapter(cwd)
    errors: list[str] = []
    warnings: list[str] = []

    work = resolve_work(work_id=work_id, required=True)
    if work is None:
        raise ValueError("work is required")

    # 1. Git check
    git_state = git.status_summary()
    if not git_state.get("available"):
        errors.append("Not inside a git repository.")
    elif not git_state.get("clean"):
        warnings.append(
            "Git working tree is dirty (uncommitted changes). Consider committing before review."
        )

    # 2. OpenSpec check
    openspec_result: dict = {"status": "skip", "passed": True}
    if work.openspec_change:
        opsx_available, _ = openspec.detect()
        if opsx_available and openspec.is_initialized():
            openspec_result = openspec.validate(work.openspec_change)
            if not openspec_result.get("passed"):
                errors.append(
                    f"OpenSpec validation failed for change '{work.openspec_change}'."
                )
        else:
            warnings.append("OpenSpec not initialized. Skipping OpenSpec validation.")
            openspec_result = {"status": "skipped", "passed": True}
    else:
        warnings.append(
            "No OpenSpec change linked to this work. Run 'driftless change create <name>' to add one."
        )
        openspec_result = {"status": "no-change-linked", "passed": True}

    # 3. Workflow state check
    if work.status == WorkStatus.DONE:
        errors.append(f"Work {work.id} is already DONE.")

    overall = "pass" if not errors else "fail"

    next_stage_map = {
        WorkStatus.CREATED: WorkStatus.SPECIFYING.value,
        WorkStatus.SPECIFYING: WorkStatus.PLANNING.value,
        WorkStatus.PLANNING: WorkStatus.IMPLEMENTING.value,
        WorkStatus.IMPLEMENTING: WorkStatus.VERIFYING.value,
        WorkStatus.VERIFYING: WorkStatus.REVIEW.value,
        WorkStatus.REVIEW: WorkStatus.DELIVERY.value,
        WorkStatus.DELIVERY: WorkStatus.DONE.value,
        WorkStatus.DONE: "DONE",
    }
    next_stage = next_stage_map.get(work.status, "unknown")
    if overall == "pass" and work.status == WorkStatus.IMPLEMENTING:
        next_stage = "REVIEW (run: driftless review)"

    verify_data = {
        "status": overall,
        "work": work.id,
        "work_status": work.status.value,
        "openspec": openspec_result,
        "git": git_state,
        "errors": errors,
        "warnings": warnings,
        "next": next_stage,
    }

    if json_output:
        renderer.print_json(verify_data)
    else:
        renderer.print_verify_human(verify_data)

    if overall == "fail":
        raise typer.Exit(code=1)


@app.command("review")
def cmd_review(
    work_id: Annotated[
        str | None,
        typer.Option("--work", "-w", help="Work ID. Defaults to active work."),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Transition active work to REVIEW stage."""
    work = resolve_work(work_id=work_id, required=True)
    if work is None:
        raise ValueError("work is required")

    try:
        updated = work_service.transition(work, WorkStatus.REVIEW)
    except ValueError as e:
        renderer.error_with_hint(
            str(e),
            f"Current status: {work.status.value}. Run 'driftless verify' before advancing.",
        )
        return

    data = updated.model_dump(mode="json")
    if json_output:
        renderer.print_json(data)
    else:
        renderer.success(f"Work {updated.id} moved to REVIEW")
        renderer.info("Next: run 'driftless finish' when the review is approved.")


@app.command("finish")
def cmd_finish(
    work_id: Annotated[
        str | None,
        typer.Option("--work", "-w", help="Work ID. Defaults to active work."),
    ] = None,
    archive: Annotated[
        bool,
        typer.Option(
            "--archive/--no-archive", help="Archive the linked OpenSpec change."
        ),
    ] = True,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Complete work and archive OpenSpec change."""
    cwd = Path.cwd()
    openspec = OpenSpecAdapter(cwd)

    work = resolve_work(work_id=work_id, required=True)
    if work is None:
        raise ValueError("work is required")

    openspec_archived = False
    if archive and work.openspec_change:
        opsx_available, _ = openspec.detect()
        if opsx_available and openspec.is_initialized():
            try:
                openspec.archive(work.openspec_change)
                openspec_archived = True
                if not json_output:
                    renderer.success(
                        f"OpenSpec change '{work.openspec_change}' archived."
                    )
            except Exception as e:
                if not json_output:
                    renderer.warn(
                        f"Could not archive OpenSpec change: {e}. Continuing."
                    )

    try:
        if work.status == WorkStatus.REVIEW:
            work = work_service.transition(work, WorkStatus.DELIVERY)
        if work.status == WorkStatus.DELIVERY or work.status != WorkStatus.DONE:
            work = work_service.transition(work, WorkStatus.DONE)
    except ValueError as e:
        renderer.error_with_hint(
            str(e), "Use 'driftless review' first, then 'driftless finish'."
        )
        return

    data = {
        "work": work.model_dump(mode="json"),
        "openspec_archived": openspec_archived,
    }

    if json_output:
        renderer.print_json(data)
    else:
        renderer.success(f"Work {work.id} is DONE. 🎉")
        renderer.info(f"'{work.title}'")
        renderer.print_human([""])
