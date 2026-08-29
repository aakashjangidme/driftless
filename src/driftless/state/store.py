"""State store — reads and writes Work state to .driftless/work/<id>/state.json."""

from __future__ import annotations

from pathlib import Path

from driftless.work.models import Work

_DRIFTLESS_DIR = ".driftless"
_WORK_DIR = "work"


def _driftless_root(repo_root: Path | None = None) -> Path:
    """Return the .driftless directory path, rooted at repo_root or cwd."""
    base = repo_root or Path.cwd()
    return base / _DRIFTLESS_DIR


def work_dir(work_id: str, repo_root: Path | None = None) -> Path:
    """Return the directory path for a specific Work."""
    return _driftless_root(repo_root) / _WORK_DIR / work_id


def state_path(work_id: str, repo_root: Path | None = None) -> Path:
    """Return the state.json path for a specific Work."""
    return work_dir(work_id, repo_root) / "state.json"


def save(work: Work, repo_root: Path | None = None) -> None:
    """Persist Work state to .driftless/work/<id>/state.json."""
    path = state_path(work.id, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        work.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load(work_id: str, repo_root: Path | None = None) -> Work:
    """Load Work state from disk.

    Raises FileNotFoundError if the work does not exist.
    """
    path = state_path(work_id, repo_root)
    if not path.exists():
        raise FileNotFoundError(
            f"Work '{work_id}' not found at {path}. "
            "Run 'driftless work list' to see available work."
        )
    raw = path.read_text(encoding="utf-8")
    return Work.model_validate_json(raw)


def list_ids(repo_root: Path | None = None) -> list[str]:
    """Return sorted list of all work IDs found in .driftless/work/."""
    work_base = _driftless_root(repo_root) / _WORK_DIR
    if not work_base.exists():
        return []
    ids = [
        d.name
        for d in sorted(work_base.iterdir())
        if d.is_dir() and (d / "state.json").exists()
    ]
    return ids


def driftless_initialized(repo_root: Path | None = None) -> bool:
    """Return True if .driftless directory exists."""
    return _driftless_root(repo_root).exists()
