"""CLI helper utilities."""

from __future__ import annotations

from pathlib import Path

from driftless.output import renderer
from driftless.work import service as work_service
from driftless.work.models import Work


def resolve_work(
    work_id: str | None = None,
    required: bool = True,
    repo_root: Path | None = None,
) -> Work | None:
    """Resolve Work by ID or default to active work.

    If required is True and no work is found, prints a failure hint and exits (exit code 1).
    """
    if work_id:
        try:
            return work_service.load_work(work_id, repo_root=repo_root)
        except FileNotFoundError:
            renderer.error_with_hint(
                f"Work '{work_id}' not found.",
                "Run 'driftless work list' to see available works.",
            )
            return None

    work = work_service.active_work(repo_root=repo_root)
    if not work and required:
        renderer.error_with_hint(
            "No active work found.",
            'Create work first:\n  driftless work create "<description>"',
        )
        return None
    return work
