# Contributing to Driftless

All contributions go through GitHub PRs. Here's the full workflow.

## Prerequisites

- Python 3.12+
- `uv` package manager

## Setup

```bash
uv sync --group dev
```

### Install pre-commit hooks

```bash
make install-hooks
```

This installs git pre-commit hooks that run `ruff`, `mypy`, and YAML/TOML
validators on every commit. To run them manually:

```bash
make pre-commit
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

3. **Run checks** — pre-commit hooks run automatically on commit. To run manually:
   ```bash
   make pre-commit        # all hooks
   make lint              # ruff check only
   make typecheck         # mypy only
   make test             # pytest only
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
