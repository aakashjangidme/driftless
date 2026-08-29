"""Output renderer — human-readable and JSON output for Driftless CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def print_json(data: Any) -> None:
    """Print data as JSON to stdout. Used for --json flag outputs."""
    print(json.dumps(data, indent=2, default=str))


def print_human(lines: list[str]) -> None:
    """Print human-readable lines to stdout."""
    for line in lines:
        console.print(line)


def print_work_human(work_data: dict) -> None:
    """Print a formatted Work summary."""
    wid = work_data.get("id", "?")
    title = work_data.get("title", "?")
    wtype = work_data.get("type", "?")
    status = work_data.get("status", "?")
    branch = work_data.get("branch") or "—"
    openspec = work_data.get("openspec_change") or "—"

    console.print()
    console.print(f"[bold cyan]Driftless · {wid}[/bold cyan]")
    console.print()
    console.print(f"[bold]{title}[/bold]")
    console.print(f"Type:    [dim]{wtype}[/dim]")
    console.print(f"Status:  [yellow]{status}[/yellow]")
    console.print()
    console.print(f"OpenSpec: [dim]{openspec}[/dim]")
    console.print(f"Branch:   [dim]{branch}[/dim]")
    console.print()


def print_status_human(status_data: dict) -> None:
    """Print a formatted driftless status output."""
    work = status_data.get("work", {})
    git = status_data.get("git", {})
    openspec_info = status_data.get("openspec", {})
    message = status_data.get("message", "")

    if not work:
        console.print("[dim]No active work found. Run:[/dim]")
        console.print("  driftless work create <description>")
        return

    wid = work.get("id", "?")
    title = work.get("title", "?")
    wtype = work.get("type", "?")
    wstatus = work.get("status", "?")
    openspec_change = work.get("openspec_change") or "—"

    branch = git.get("branch", "—")
    clean = git.get("clean")
    git_label = (
        f"{branch} ({'clean' if clean else 'dirty'})" if git.get("available") else "—"
    )

    opsx_status = openspec_info.get("status", "—")

    console.print()
    console.print(f"[bold cyan]Driftless · {wid}[/bold cyan]")
    console.print()
    console.print(f"[bold]{title}[/bold]")
    console.print(f"Type:    [dim]{wtype}[/dim]")
    console.print(f"Status:  [yellow]{wstatus}[/yellow]")
    console.print()
    console.print(f"OpenSpec: [dim]{openspec_change}[/dim]  ({opsx_status})")
    console.print(f"Git:      [dim]{git_label}[/dim]")
    console.print()
    if message:
        console.print(f"[dim]Next:[/dim] {message}")
        console.print()


def print_verify_human(verify_data: dict) -> None:
    """Print a formatted driftless verify output."""
    overall = verify_data.get("status", "unknown")
    work_id = verify_data.get("work", "?")
    openspec_info = verify_data.get("openspec", {})
    git = verify_data.get("git", {})
    next_stage = verify_data.get("next", "?")
    errors = verify_data.get("errors", [])

    status_color = "green" if overall == "pass" else "red"
    console.print()
    console.print(
        f"[bold]driftless verify[/bold]  [{status_color}]{overall.upper()}[/{status_color}]"
    )
    console.print()
    console.print(f"Work:      [cyan]{work_id}[/cyan]")

    opsx_ok = openspec_info.get("passed", openspec_info.get("status") == "pass")
    opsx_label = "[green]pass[/green]" if opsx_ok else "[red]fail[/red]"
    console.print(f"OpenSpec:  {opsx_label}")

    git_ok = git.get("clean", False)
    git_label = "[green]clean[/green]" if git_ok else "[yellow]dirty[/yellow]"
    console.print(f"Git:       {git_label}  ({git.get('branch', '—')})")
    console.print()
    if errors:
        console.print("[red]Errors:[/red]")
        for e in errors:
            console.print(f"  • {e}")
        console.print()
    console.print(f"[dim]Next:[/dim] {next_stage}")
    console.print()


def error_with_hint(message: str, hint: str = "") -> None:
    """Print an error message with an actionable hint and exit 1."""
    err_console.print(f"\n[bold red]Error:[/bold red] {message}")
    if hint:
        err_console.print(f"\n{hint}\n")
    sys.exit(1)


def warn(message: str) -> None:
    """Print a warning to stderr."""
    err_console.print(f"[yellow]Warning:[/yellow] {message}")


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def info(message: str) -> None:
    """Print an info line."""
    console.print(f"[dim]{message}[/dim]")
