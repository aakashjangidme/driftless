"""Logging configuration for driftless CLI."""

from __future__ import annotations

import logging
import os
from pathlib import Path

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(verbose: bool = False, repo_root: Path | None = None) -> None:
    """Configure Driftless logging.

    Logs DEBUG/INFO messages to .driftless/state.log if .driftless directory exists,
    and optionally to stderr if verbose is True or DRIFTLESS_DEBUG env var is set.
    """
    root_logger = logging.getLogger("driftless")
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # 1. File Logger (.driftless/state.log)
    base = repo_root or Path.cwd()
    driftless_dir = base / ".driftless"
    if driftless_dir.exists():
        log_file = driftless_dir / "driftless.log"
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.debug("Failed to set up file logger: %s", e)

    # 2. Console Logger (stderr) if verbose or DRIFTLESS_DEBUG set
    if verbose or os.environ.get("DRIFTLESS_DEBUG"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'driftless' hierarchy."""
    return logging.getLogger(f"driftless.{name}")
