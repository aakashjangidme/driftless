"""driftless work — Work lifecycle subcommands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from driftless.cli.utils import resolve_work
from driftless.output import renderer
from driftless.work import service as work_service
from driftless.work.models import WorkType

app = typer.Typer(
    name="work",
    help="Manage engineering work (create, list, show).",
    no_args_is_help=True,
)


@app.command("create")
def work_create(
    description: Annotated[str, typer.Argument(help="Short description of the work.")],
    work_type: Annotated[
        WorkType,
        typer.Option("--type", "-t", help="Work type.", show_default=True),
    ] = WorkType.feature,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Create a new unit of engineering work."""
    try:
        work = work_service.create_work(title=description, work_type=work_type)
    except Exception as e:
        renderer.error_with_hint(
            f"Failed to create work: {e}",
            "Ensure you are inside a git repository and have run 'driftless init'.",
        )
        return

    data = work.model_dump(mode="json")

    if json_output:
        renderer.print_json(data)
    else:
        renderer.success(f"Created Work {work.id}")
        renderer.print_work_human(data)
        renderer.info(f"Persisted to .driftless/work/{work.id}/state.json")
        renderer.info(
            "Next: run 'driftless change create <name>' to start the OpenSpec inner loop."
        )


@app.command("list")
def work_list(
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """List all works."""
    works = work_service.list_works()

    if json_output:
        renderer.print_json([w.model_dump(mode="json") for w in works])
        return

    if not works:
        renderer.info("No work found. Run: driftless work create <description>")
        return

    console = Console()
    table = Table(title="Driftless Works", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Type", style="dim")
    table.add_column("Status", style="yellow")
    table.add_column("OpenSpec", style="dim")

    for work in works:
        table.add_row(
            work.id,
            work.title,
            work.type.value,
            work.status.value,
            work.openspec_change or "—",
        )

    console.print()
    console.print(table)
    console.print()


@app.command("show")
def work_show(
    work_id: Annotated[str, typer.Argument(help="Work ID (e.g. W-0001).")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output as JSON.")
    ] = False,
) -> None:
    """Show details of a specific work."""
    work = resolve_work(work_id=work_id, required=True)
    if not work:
        return

    data = work.model_dump(mode="json")
    if json_output:
        renderer.print_json(data)
    else:
        renderer.print_work_human(data)
