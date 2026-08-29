"""Universal AGENTS.md skill generator.

Generates an AGENTS.md file in the project root that teaches universal coding agents
(Cursor, OpenCode, Devin, Antigravity, RooCode, Factory, etc.) how and when to use Driftless.
"""

from __future__ import annotations

from pathlib import Path

AGENTS_MD_CONTENT = """\
# Driftless — AI-Native SDLC Workflow (Universal Agent Instructions)

This repository uses **Driftless** for outer-loop SDLC workflow management.

Driftless is a local CLI tool that you run. **Never** launch Driftless to orchestrate yourself — you invoke Driftless CLI.

---

## Agent / Driftless Operational Architecture

```text
       Coding Agent (Cursor / OpenCode / Devin / RooCode / etc.)
                                 │
                                 │ invokes CLI
                                 ↓
Driftless
                                 │
                         ┌───────┴───────┐
                         ↓               ↓
                    Outer Loop       OpenSpec
                  (Work Domain)     (Inner Loop)
                         │               │
                         └───────┬───────┘
                                 ↓
                                Git
```

- **Driftless owns**: Work lifecycle, workflow state, artifact conventions, OpenSpec integration, Git-aware state, verification.
- **You own**: reasoning, repository exploration, specification authoring, implementation, testing.

---

## Work Lifecycle & Commands

A **Work** is Driftless's primary outer-loop domain object. Work persists in `.driftless/work/<id>/state.json`.

Work lifecycle stages:
```text
CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE
```

### When to Use Driftless
- Starting a feature, bug fix, refactor, or migration: `driftless work create "<description>"`
- Checking active state: `driftless status --json`
- Creating an OpenSpec change: `driftless change create <name>`
- Verifying readiness before review: `driftless verify --json`
- Advancing lifecycle: `driftless review --json` -> `driftless finish --json`

---

## Machine-Readable CLI Execution

Always append `--json` to Driftless commands for machine-readable JSON outputs:

```bash
driftless work create "Add OAuth login" --type feature --json
driftless work list --json
driftless work show W-0001 --json
driftless change create add-oauth-login --json
driftless status --json
driftless verify --json
driftless review --json
driftless finish --json
```

---

## Verification Policy

Always run `driftless verify --json` before running `driftless review` or `driftless finish`.
- `"status": "pass"` -> Work is clean and ready for review.
- `"status": "fail"` -> Check `"errors"` array and fix highlighted issues before proceeding.
"""


def write_agents_skill(project_root: Path, force: bool = False) -> Path:
    """Write or append the AGENTS.md Driftless skill to project_root.

    Args:
        project_root: Root directory of the project.
        force: If True, overwrite existing AGENTS.md.

    Returns:
        Path to the written file.
    """
    target = project_root / "AGENTS.md"
    if target.exists() and not force:
        existing = target.read_text(encoding="utf-8")
        driftless_marker = "# Driftless — AI-Native SDLC Workflow"
        if driftless_marker in existing:
            return target
        target.write_text(
            existing.rstrip() + "\n\n---\n\n" + AGENTS_MD_CONTENT,
            encoding="utf-8",
        )
    else:
        target.write_text(AGENTS_MD_CONTENT, encoding="utf-8")
    return target
