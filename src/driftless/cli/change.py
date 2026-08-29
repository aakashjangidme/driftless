"""driftless change — OpenSpec change management subcommands."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console

from driftless.cli.utils import resolve_work
from driftless.openspec.adapter import OpenSpecAdapter, OpenSpecNotFound
from driftless.output import renderer
from driftless.work import service as work_service
from driftless.work.models import WorkStatus

app = typer.Typer(
    name="change",
    help="Manage OpenSpec change proposals.",
    no_args_is_help=True,
)


def _get_openspec() -> OpenSpecAdapter:
    """Return an OpenSpecAdapter, erroring clearly if OpenSpec is unavailable."""
    adapter = OpenSpecAdapter()
    available, _version = adapter.detect()
    if not available:
        renderer.error_with_hint(
            "OpenSpec not found.",
            OpenSpecNotFound.INSTALL_HINT,
        )
    return adapter


@app.command("create")
def change_create(
    name: Annotated[
        str, typer.Argument(help="Change name (slug, e.g. add-oauth-login).")
    ],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Description of the change."),
    ] = "",
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Create an OpenSpec change and link it to the active work."""
    adapter = _get_openspec()
    work = resolve_work(required=True)
    if work is None:
        raise ValueError("work is required")

    if not adapter.is_initialized():
        renderer.error_with_hint(
            "OpenSpec not initialized in this project.",
            "Run 'driftless init' to initialize both Driftless and OpenSpec.",
        )
        return

    try:
        result = adapter.create_change(name, description)
    except Exception as e:
        renderer.error_with_hint(
            f"Failed to create OpenSpec change: {e}",
            "Ensure OpenSpec is initialized: run 'driftless init'.",
        )
        return

    # Link the change to the Work and advance status
    updated = work_service.link_openspec_change(work, name)

    # Advance to SPECIFYING if still CREATED
    if updated.status == WorkStatus.CREATED:
        try:
            updated = work_service.transition(updated, WorkStatus.SPECIFYING)
        except ValueError:
            pass

    data = {
        "work_id": updated.id,
        "openspec_change": name,
        "work_status": updated.status.value,
        "openspec": result,
    }

    if json_output:
        renderer.print_json(data)
    else:
        renderer.success(f"Created OpenSpec change '{name}'")
        renderer.success(
            f"Linked to Work {updated.id} (status: {updated.status.value})"
        )
        renderer.info(f"OpenSpec change files: openspec/changes/{name}/")
        renderer.info(
            "Next: use Claude Code to author proposal.md, design.md, tasks.md"
        )


@app.command("status")
def change_status(
    change_name: Annotated[
        str | None,
        typer.Option(
            "--change", "-c", help="Change name. Defaults to active work's change."
        ),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Show artifact completion status for a change."""
    adapter = _get_openspec()

    if not change_name:
        work = work_service.active_work()
        if work and work.openspec_change:
            change_name = work.openspec_change
        else:
            renderer.error_with_hint(
                "No change name provided and no linked change in active work.",
                "Provide --change <name> or link a change: driftless change create <name>",
            )
            return

    result = adapter.status(change_name)

    if json_output:
        renderer.print_json(result)
    else:
        renderer.print_human(
            [
                "",
                f"[bold cyan]OpenSpec Change: {change_name}[/bold cyan]",
                "",
            ]
        )
        Console().print_json(json.dumps(result, indent=2, default=str))
        renderer.print_human([""])


@app.command("validate")
def change_validate(
    change_name: Annotated[
        str | None,
        typer.Option(
            "--change", "-c", help="Change name. Defaults to active work's change."
        ),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Validate an OpenSpec change."""
    adapter = _get_openspec()

    if not change_name:
        work = work_service.active_work()
        if work and work.openspec_change:
            change_name = work.openspec_change

    result = adapter.validate(change_name)
    passed = result.get("passed", False)

    if json_output:
        renderer.print_json(result)
    else:
        status_label = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        renderer.print_human(["", f"OpenSpec validate: {status_label}", ""])
        if not passed:
            errors = result.get("errors", [])
            for err in errors:
                renderer.print_human([f"  • {err}"])
            renderer.print_human([""])
