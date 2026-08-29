# Contributing to Driftless

All contributions go through GitHub PRs. Here's the full workflow.

## Prerequisites

- Python 3.12+
- `uv` package manager

## Setup

```bash
uv sync --group dev
```

## Workflow

1. **Fork & clone** the repo, then create a feature branch:
   ```bash
   git checkout -b feat/my-feature main
   ```

2. **Make changes** with signed commits:
   ```bash
   git commit -S -m "feat: add new feature"
   ```

3. **Run checks locally** before pushing:
   ```bash
   uv run ruff format --check src/driftless
   uv run ruff check src/driftless
   uv run mypy src/driftless --ignore-missing-imports
   uv run pytest tests/
   ```

4. **Push and open a PR**:
   ```bash
   git push -u origin feat/my-feature
   gh pr create --fill
   ```

## PR Requirements

- CI must pass (Lint & Type Check + Tests)
- At least 1 approving review
- Branches auto-delete on merge (squash-only)
- Keep PRs focused — one feature per PR
