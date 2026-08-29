"""Agent skill manager — generates instruction files for supported coding agents."""

from __future__ import annotations

from pathlib import Path

from driftless.agents.agents_md import write_agents_skill
from driftless.agents.claude import write_claude_skill
from driftless.logging import get_logger

logger = get_logger("agents")


def install_agent_skills(
    project_root: Path,
    tools: str = "claude",
    force: bool = False,
) -> list[Path]:
    """Install agent skill files based on configured tools.

    Always installs CLAUDE.md and AGENTS.md (as the universal standard) unless tools=='none'.
    """
    if tools.strip().lower() == "none":
        logger.info("Skipping agent skill generation (tools=none)")
        return []

    installed: list[Path] = []

    # 1. Install CLAUDE.md for Claude Code
    try:
        claude_path = write_claude_skill(project_root, force=force)
        installed.append(claude_path)
        logger.debug("Installed CLAUDE.md skill at %s", claude_path)
    except Exception as e:
        logger.error("Failed to write CLAUDE.md skill: %s", e)

    # 2. Install AGENTS.md (Universal standard for Cursor, OpenCode, Devin, Antigravity, RooCode, etc.)
    try:
        agents_path = write_agents_skill(project_root, force=force)
        installed.append(agents_path)
        logger.debug("Installed AGENTS.md skill at %s", agents_path)
    except Exception as e:
        logger.error("Failed to write AGENTS.md skill: %s", e)

    return installed
