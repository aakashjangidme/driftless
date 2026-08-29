"""Work service — high-level operations on Work objects."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from driftless.git.adapter import GitAdapter
from driftless.state import store
from driftless.work.models import Work, WorkStatus, WorkType

logger = logging.getLogger(__name__)


def _next_id(repo_root: Path | None = None) -> str:
    """Generate the next sequential Work ID (W-0001, W-0002, ...)."""
    ids = store.list_ids(repo_root)
    if not ids:
        return "W-0001"
    # Extract numeric parts and find max
    nums = []
    for wid in ids:
        m = re.match(r"W-(\d+)$", wid)
        if m:
            nums.append(int(m.group(1)))
    next_num = (max(nums) + 1) if nums else 1
    return f"W-{next_num:04d}"


def create_work(
    title: str,
    work_type: WorkType = WorkType.feature,
    repo_root: Path | None = None,
) -> Work:
    """Create a new Work, persist it, and return it."""
    git = GitAdapter(repo_root)
    work_id = _next_id(repo_root)

    branch: str | None = None
    repository: str | None = None
    if git.is_repo():
        try:
            branch = git.branch()
        except Exception as e:
            logger.debug("Could not determine git branch: %s", e)
        try:
            repository = str(git.root())
        except Exception as e:
            logger.debug("Could not determine git root: %s", e)

    work = Work(
        id=work_id,
        title=title,
        type=work_type,
        status=WorkStatus.CREATED,
        branch=branch,
        repository=repository,
    )
    store.save(work, repo_root)
    return work


def list_works(repo_root: Path | None = None) -> list[Work]:
    """Return all works, sorted by ID."""
    ids = store.list_ids(repo_root)
    works = []
    for wid in ids:
        try:
            works.append(store.load(wid, repo_root))
        except (FileNotFoundError, ValueError):
            pass
    return works


def load_work(work_id: str, repo_root: Path | None = None) -> Work:
    """Load a specific Work by ID."""
    return store.load(work_id, repo_root)


def active_work(repo_root: Path | None = None) -> Work | None:
    """Return the most recently updated non-DONE Work, or None."""
    works = list_works(repo_root)
    active = [w for w in works if w.is_active()]
    if not active:
        return None
    # Most recently updated
    return max(active, key=lambda w: w.updated_at)


def transition(
    work: Work,
    new_status: WorkStatus,
    repo_root: Path | None = None,
) -> Work:
    """Transition Work to new_status, persist, and return updated Work."""
    updated = work.transition_to(new_status)
    store.save(updated, repo_root)
    return updated


def link_openspec_change(
    work: Work,
    change_name: str,
    repo_root: Path | None = None,
) -> Work:
    """Link an OpenSpec change to the Work and persist."""
    updated = work.model_copy(update={"openspec_change": change_name})
    store.save(updated, repo_root)
    return updated
