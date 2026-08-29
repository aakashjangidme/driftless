"""Git adapter — thin wrapper around git CLI subprocess calls."""

from __future__ import annotations

import subprocess
from pathlib import Path

from driftless.logging import get_logger

logger = get_logger("git")


class GitError(Exception):
    """Raised when a git command fails."""


class GitAdapter:
    """Adapter for reading Git repository state via subprocess."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self._cwd = repo_root or Path.cwd()

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and return the result."""
        cmd = ["git", "--no-pager", *args]
        logger.debug("Running command: %s (cwd=%s)", cmd, self._cwd)
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=self._cwd,
            capture_output=True,
            text=True,
            check=check,
        )
        logger.debug("Command exit code: %d", result.returncode)
        return result

    def is_repo(self) -> bool:
        """Return True if the current directory is inside a git repository."""
        result = self._run(
            ["rev-parse", "--is-inside-work-tree"],
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def root(self) -> Path:
        """Return the root directory of the git repository.

        Raises GitError if not in a git repo.
        """
        result = self._run(["rev-parse", "--show-toplevel"])
        return Path(result.stdout.strip())

    def branch(self) -> str:
        """Return the current branch name.

        Returns branch name, or initial branch if before the first commit.
        """
        result = self._run(["rev-parse", "--abbrev-ref", "HEAD"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        sym_result = self._run(["symbolic-ref", "--short", "HEAD"], check=False)
        if sym_result.returncode == 0:
            return sym_result.stdout.strip()
        return "main"

    def commit(self) -> str:
        """Return the current HEAD commit SHA (short form).

        Returns 'none' if repository has no commits yet.
        """
        result = self._run(["rev-parse", "--short", "HEAD"], check=False)
        if result.returncode != 0:
            return "none"
        return result.stdout.strip()

    def is_clean(self) -> bool:
        """Return True if the working tree has no uncommitted changes."""
        result = self._run(["status", "--porcelain"])
        return result.stdout.strip() == ""

    def status_summary(self) -> dict:
        """Return a dict summarising current git state."""
        if not self.is_repo():
            return {"available": False}
        return {
            "available": True,
            "branch": self.branch(),
            "commit": self.commit(),
            "clean": self.is_clean(),
        }
