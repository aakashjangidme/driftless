"""OpenSpec adapter — thin wrapper around npx @fission-ai/openspec CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from driftless.logging import get_logger

logger = get_logger("openspec")

OPENSPEC_CMD = ["npx", "--yes", "@fission-ai/openspec"]


class OpenSpecError(Exception):
    """Raised when an OpenSpec command fails."""


class OpenSpecNotFound(OpenSpecError):
    """Raised when OpenSpec is not available."""

    INSTALL_HINT = (
        "Driftless requires OpenSpec for change management.\n\n"
        "Install it:\n"
        "  npm install -g @fission-ai/openspec@latest\n\n"
        "Then retry your command."
    )


class OpenSpecAdapter:
    """Adapter for the @fission-ai/openspec CLI.

    All subprocess calls use structured list args — never string interpolation.
    """

    def __init__(self, cwd: Path | None = None) -> None:
        self._cwd = cwd or Path.cwd()

    def _run(
        self,
        args: list[str],
        check: bool = True,
        input: str | None = None,
    ) -> subprocess.CompletedProcess:
        """Run an openspec command and return the result."""
        cmd = [*OPENSPEC_CMD, *args]
        logger.debug("Running OpenSpec command: %s (cwd=%s)", cmd, self._cwd)
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=self._cwd,
            capture_output=True,
            text=True,
            check=False,
            input=input,
        )
        logger.debug("OpenSpec command exit code: %d", result.returncode)
        if check and result.returncode != 0:
            logger.error("OpenSpec command failed: %s (stderr: %s)", cmd, result.stderr)
            raise OpenSpecError(
                f"OpenSpec command failed: {' '.join(args)}\n"
                f"Exit code: {result.returncode}\n"
                f"Output: {result.stderr or result.stdout}"
            )
        return result

    def detect(self) -> tuple[bool, str]:
        """Return (available, version) for OpenSpec.

        Calls `openspec --version` to detect availability.
        """
        result = self._run(["--version"], check=False)
        if result.returncode != 0:
            return False, ""
        return True, result.stdout.strip()

    def is_initialized(self) -> bool:
        """Return True if OpenSpec has been initialized in the project."""
        openspec_dir = self._cwd / "openspec"
        return openspec_dir.exists()

    def init(self, tools: str = "claude") -> None:
        """Initialize OpenSpec in the current project non-interactively.

        Args:
            tools: comma-separated list of AI tools to configure (e.g. 'claude').
        """
        self._run(
            ["init", "--tools", tools, "--no-animation", "--no-color"],
            check=True,
        )

    def create_change(self, name: str, description: str = "") -> dict:
        """Create a new OpenSpec change and return the result dict.

        Uses: openspec new change <name> --description <text> --json
        """
        args = ["new", "change", name]
        if description:
            args += ["--description", description]
        args += ["--json", "--no-color"]
        result = self._run(args)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Some versions may output non-JSON on success; treat as ok
            return {"name": name, "raw": result.stdout.strip()}

    def status(self, change_name: str | None = None) -> dict:
        """Get artifact completion status for a change.

        Uses: openspec status [--change <name>] --json
        """
        args = ["status"]
        if change_name:
            args += ["--change", change_name]
        args += ["--json", "--no-color"]
        result = self._run(args, check=False)
        if result.returncode != 0:
            return {"error": result.stderr or result.stdout, "available": False}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip(), "available": True}

    def validate(self, change_name: str | None = None) -> dict:
        """Validate OpenSpec changes.

        Uses: openspec validate [<change>] --json
        """
        args = ["validate"]
        if change_name:
            args.append(change_name)
        args += ["--json", "--no-color"]
        result = self._run(args, check=False)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            data = {"raw": result.stdout.strip()}
        data["exit_code"] = result.returncode
        data["passed"] = result.returncode == 0
        return data

    def archive(self, change_name: str) -> None:
        """Archive a completed OpenSpec change.

        Uses: openspec archive <change-name>
        """
        self._run(["archive", change_name, "--no-color"])

    def change_show(self, change_name: str) -> dict:
        """Show a change in JSON format.

        Uses: openspec change show <name> --json
        """
        args = ["change", "show", change_name, "--json", "--no-color"]
        result = self._run(args, check=False)
        if result.returncode != 0:
            return {"error": result.stderr or result.stdout, "found": False}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip(), "found": True}

    def list_changes(self) -> dict:
        """List all active changes.

        Uses: openspec list --json
        """
        result = self._run(["list", "--json", "--no-color"], check=False)
        if result.returncode != 0:
            return {"error": result.stderr or result.stdout, "changes": []}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout.strip()}
