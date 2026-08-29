"""Claude Code agent skill generator.

Generates a CLAUDE.md file in the project root that teaches Claude Code
how and when to use Driftless for the outer-loop SDLC workflow.
"""

from __future__ import annotations

from pathlib import Path

CLAUDE_MD_CONTENT = """\
# Driftless — AI-Native SDLC Workflow

This repository uses **Driftless** for outer-loop SDLC workflow management.

Driftless is a CLI you run. **Never** launch Driftless to orchestrate you — you invoke Driftless.

---

## What Driftless Is

Driftless provides a persistent, version-controlled outer-loop workflow around OpenSpec's inner-loop specification workflow.

```
  You (Claude Code)
       │
       │ invoke
       ↓
     Driftless CLI
       │
  ┌────┴─────┐
  ↓          ↓
Outer     OpenSpec
Loop     (Inner Loop)
  │          │
  └────┬─────┘
       ↓
      Git
```

Driftless owns: Work lifecycle, workflow state, artifact conventions, OpenSpec integration, Git-aware state, verification.

You own: reasoning, repository exploration, specification authoring, implementation, testing.

---

## What Work Is

A **Work** is Driftless's primary domain object. It represents one unit of engineering effort.

Work persists in `.driftless/work/<id>/state.json`.

Work lifecycle:
```
CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE
```

Work types: `feature`, `bug`, `refactor`, `migration`, `incident`, `maintenance`

---

## When to Use Driftless

| Situation | Action |
|-----------|--------|
| Starting new engineering work | `driftless work create "<description>"` |
| Checking current state | `driftless status` |
| Creating an OpenSpec change | `driftless change create <name>` |
| Checking OpenSpec + Git state | `driftless verify` |
| Moving work to review | `driftless review` |
| Completing work | `driftless finish` |

For a **simple typo or 1-line fix**, you may skip Driftless — it is for meaningful engineering work.

For a **feature, bug, refactor, migration, or incident**, always use Driftless to create Work first.

---

## Core Commands

### Initialize Driftless in a repository
```bash
driftless init
```
Run once per repository. Detects Git, initializes OpenSpec, writes this file.

### Create Work
```bash
driftless work create "Add OAuth login"
driftless work create "Fix null pointer in user service" --type bug
driftless work create "Migrate to PostgreSQL" --type migration
```

### List and inspect Work
```bash
driftless work list
driftless work list --json
driftless work show W-0001
driftless work show W-0001 --json
```

### Check overall status
```bash
driftless status
driftless status --json
driftless status --work W-0001
```

### OpenSpec change management
```bash
driftless change create add-oauth-login
driftless change create add-oauth-login --description "Add OAuth 2.0 login flow"
driftless change status
driftless change status --change add-oauth-login
driftless change validate
```

### Verify readiness to advance
```bash
driftless verify
driftless verify --json
```

Returns: `pass` or `fail` with reasons. If pass, Work can move to REVIEW.

### Advance lifecycle
```bash
driftless review       # Move to REVIEW stage
driftless finish       # Complete work (DONE), archive OpenSpec change
```

---

## OpenSpec Integration

Driftless wraps OpenSpec's inner loop. OpenSpec manages specifications inside `openspec/`.

When you create a Driftless change (`driftless change create <name>`), Driftless calls:
```
openspec new change <name>
```

OpenSpec creates:
```
openspec/changes/<name>/
  proposal.md
  design.md
  tasks.md
  specs/
```

You (Claude Code) write the content of these files.

Driftless validates them with:
```bash
driftless change validate
```

---

## Machine-Readable Output

All important commands support `--json` for reliable parsing:

```bash
driftless status --json
driftless verify --json
driftless work list --json
driftless work show W-0001 --json
driftless change status --json
```

Use `--json` when you need to parse Driftless output programmatically.

---

## Verification Before Advancing

Always run `driftless verify` before calling `driftless review` or `driftless finish`.

`driftless verify` checks:
1. Driftless workflow state is consistent
2. OpenSpec change validates (if linked)
3. Git working tree is clean

A `"status": "pass"` means the Work is ready for the next stage.

---

## Error Handling

Driftless errors explain what failed, why, and how to fix it. Parse stderr for error messages.

---

## Do NOT Do

- Do not launch Claude Code from Driftless — you invoke Driftless, not the other way around
- Do not modify `.driftless/work/*/state.json` directly — use `driftless` commands
- Do not bypass `driftless verify` before finishing work
"""


def write_claude_skill(project_root: Path, force: bool = False) -> Path:
    """Write the CLAUDE.md Driftless skill to project_root.

    Args:
        project_root: Root directory of the project.
        force: If True, overwrite existing CLAUDE.md.

    Returns:
        Path to the written file.
    """
    target = project_root / "CLAUDE.md"
    if target.exists() and not force:
        # Append Driftless section if CLAUDE.md already exists
        existing = target.read_text(encoding="utf-8")
        driftless_marker = "# Driftless — AI-Native SDLC Workflow"
        if driftless_marker in existing:
            return target  # Already has Driftless skill
        # Append
        target.write_text(
            existing.rstrip() + "\n\n---\n\n" + CLAUDE_MD_CONTENT,
            encoding="utf-8",
        )
    else:
        target.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
    return target
