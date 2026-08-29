# AGENTS.md — Driftless Development Guidelines

Agents working on this repository follow the conventions below. When in doubt, check `pyproject.toml` for ruff rules and `tests/` for expected behavior.

---

## Project Overview

**Driftless** — AI-native SDLC outer-loop CLI for coding agents. Manages work lifecycle, OpenSpec integration, and Git-aware state across `CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE`.

**Key APIs**: `driftless work create`, `driftless status`, `driftless verify`, `driftless review`, `driftless finish`

**Primary files**:
- `src/driftless/work/models.py` — WorkType, WorkStatus, ALLOWED_TRANSITIONS, Work model
- `src/driftless/cli/main.py` — CLI entry point with `init`, `status`, `verify`, `review`, `finish` commands
- `src/driftless/state/store.py` — Persist/load work state to `.driftless/work/<id>/state.json`
- `src/driftless/git/adapter.py` — Git subprocess wrapper (GitAdapter)
- `src/driftless/output/renderer.py` — Human-readable + JSON output (rich.Console)
- `src/driftless/cli/utils.py` — Work resolution helpers

---

## Code Idioms (Required)

All files must start with:

```python
from __future__ import annotations
```

Extensive type hints using `Annotated`, `Optional`, `list`, `dict`. `pathlib.Path` for file operations. `str, Enum` patterns for `WorkType`/`WorkStatus`. Pydantic `BaseModel` with `ConfigDict(use_enum_values=False)`. `model_dump(mode="json")` / `model_dump_json()` serialization.

**Ruff configuration** (in `pyproject.toml`):

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "S", "UP", "PERF", "ASYNC"]
ignore = ["T2", "E501"]
```

**Prohibited** (will cause ruff failure unless justified):

- `BLE001` bare `Exception` catches — use specific exception types
- `RUF059` unpacked vars never used — prefix with `_` or remove
- `UP042` `str,Enum` — switch to `enum.StrEnum` (Python 3.12+)
- `S101` `assert` as guard — use `if` guard + `raise ValueError` instead
- `S603` subprocess with untrusted input — these are internal git/OpenSpec calls, justified
- `S110` `try`-`except`-`pass` — only for non-critical failures (logging setup, git continue-on-failure)

---

## Daily Workflow

### 1. Start a new work item

```bash
driftless work create "Add OAuth login"
# or with type: driftless work create "Fix null ptr" --type bug
```

### 2. Make changes

- Edit source files in `src/driftless/`
- Follow existing idioms (see "Code Idioms" section)
- Run `ruff check src/driftless` — fix all auto-fixable issues
- Run `python -m pytest tests/ --tb=short` — all 143 tests must pass

### 3. Verify state

```bash
driftless status      # Check current work + git + OpenSpec state
driftless verify      # Must pass before review
```

### 4. Advance lifecycle

```bash
driftless review      # Move work to REVIEW stage
driftless finish      # Complete work (DONE), archive OpenSpec change
```

### 5. Run the full test suite

```bash
python -m pytest tests/ --tb=no -q
# Expected: 143 passed, 0 failed
```

If tests fail, debug using the `diagnosing-bugs` skill pattern — reproduce, isolate, fix.

---

## Adding New Features

### 1. Identify the domain layer

- **CLI** → `src/driftless/cli/` — `main.py`, `change.py`, `work.py`, `utils.py`
- **Work service** → `src/driftless/work/service.py` — `create_work`, `list_works`, `transition`, `link_openspec_change`
- **State store** → `src/driftless/state/store.py` — `save`, `load`, `list_ids`, `state_path`
- **Git adapter** → `src/driftless/git/adapter.py` — `is_repo`, `root`, `branch`, `is_clean`, `status_summary`
- **Output renderer** → `src/driftless/output/renderer.py` — all `print_*_human`, `error_with_hint`, `success`, `warn`, `info`
- **Models** → `src/driftless/work/models.py` — `WorkType`, `WorkStatus`, `ALLOWED_TRANSITIONS`, `Work`

### 2. Follow the pattern

- Add new command in `src/driftless/cli/main.py` → register with `app.command(...)` → add sub-typer
- Add model fields in `src/driftless/work/models.py` — use `WorkType`/`WorkStatus` enums
- Add state store methods in `src/driftless/state/store.py` — `work_dir`, `state_path`, `save`, `load`, `list_ids`
- Add git methods in `src/driftless/git/adapter.py` — keep it thin, just subprocess wrapping
- Add renderer methods in `src/driftless/output/renderer.py` — `success`, `warn`, `info`, `error_with_hint`, `print_*_human`
- Update `ALLOWED_TRANSITIONS` in `src/driftless/work/models.py` if adding new states

### 3. Run ruff + tests before committing

```bash
ruff check src/driftless  # 9 errors max (all justified)
python -m pytest tests/ --tb=no -q  # 143 passed
```

---

## Git Workflow

- **Branch**: `main` — only merge via PR with `driftless finish` completed
- **Commit messages**: Conventional Commits style (optional but recommended)
- **Never** modify `.driftless/work/*/state.json` directly — use `driftless` commands
- **Always** run `driftless verify` before `driftless review` or `driftless finish`
- **Never** bypass `driftless verify` — it checks: workflow consistency, OpenSpec validation, git clean

---

## Common Patterns

### Transitioning work status

```python
from driftless.work.service import transition
from driftless.work.models import WorkStatus

work = ...  # load existing work
work = transition(work, WorkStatus.IMPLEMENTING)  # returns new Work
store.save(work, repo_root)  # persist
```

### Linking OpenSpec change

```python
from driftless.work.service import link_openspec_change
from driftless.state import store

work = ...  # existing work
work = link_openspec_change(work, "add-oauth-login", repo_root)
store.save(work, repo_root)
```

### Loading / saving work

```python
from driftless.state.store import load, save, list_ids

works = list_ids(repo_root)  # ["W-0001", "W-0002", ...]
work = load("W-0001", repo_root)  # returns Work model
save(work, repo_root)  # persists to .driftless/work/W-0001/state.json
```

### CLI output patterns

```python
from driftless.output.renderer import success, warn, info, error_with_hint

success("Work created")
warn("Deprecated feature in use")
info("Run 'driftless status' for status")
error_with_hint("Not a git repo", "Initialize git first: git init")
```

---

## Project Conventions

| Convention | Detail |
|---|---|
| **File header** | `from __future__ import annotations` + imports + docstring |
| **Enums** | `class X(StrEnum)` (Python 3.12+), values are `str` |
| **Pydantic** | `model_config = ConfigDict(use_enum_values=False)` |
| **Serialization** | `model_dump(mode="json")` / `model_dump_json()` |
| **Path operations** | `pathlib.Path` throughout, no `os.path` |
| **CLI flags** | `Annotated[..., typer.Option(--flag, "-f", help="...")]` |
| **Terminal output** | `rich.Console` for colored output; `err_console` for errors |
| **Error handling** | `error_with_hint(message, hint)` exits with code 1 |
| **Success/warn/info** | `success(msg)`, `warn(msg)`, `info(msg)` — use these, not `print()` |
| **Logging** | `driftless.logging.get_logger("name")` for DEBUG/INFO to `.driftless/driftless.log` |
| **Git adapter** | `GitAdapter(cwd)` — thin wrapper, `_run(args, check=True)` |
| **State store** | `driftless.state.store` — state storage |
| **Allowed transitions** | `ALLOWED_TRANSITIONS` dict in `src/driftless/work/models.py` |
| **Ruff errors** | 9 justified: S101 (4), S603 (2), S110 (3), BLE001 (8, pending fix) |
| **Test expectations** | 143 tests, all must pass before commit |

---

## Need Help?

- Check `pyproject.toml` for ruff rule details
- Run `python -m pytest tests/ --tb=short` to see test failures
- Look at `src/driftless/work/models.py` for the domain model
- Review `src/driftless/cli/main.py` for CLI command patterns
- Check `src/driftless/output/renderer.py` for output patterns
- See `src/driftless/state/store.py` for state persistence
- Consult `CLAUDE.md` (generated at `driftless init`) for external agent guidance

---

*This file was generated on 2026-08-29 for the Driftless repository. It defines the development conventions that all agents working on this codebase must follow. When conventions change, update this file and update `pyproject.toml` ruff rules in tandem.*

*Related*: `CLAUDE.md` (generated at `driftless init`) teaches external Claude Code agents how to use the SDLC workflow.