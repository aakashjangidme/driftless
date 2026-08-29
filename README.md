![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg?logo=codecov)
![Tests](https://img.shields.io/badge/pass-143%20tests-brightgreen.svg?logo=github-actions)
![Release](https://img.shields.io/github/v/release/aakashjangidme/driftless?logo=github)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg?logo=python)
![GitHub stars](https://img.shields.io/github/stars/aakashjangidme/driftless?style=social&label=Stars)
![Built for AI agents](https://img.shields.io/badge/built%20for-Claude%20Code-orange?logo=claude)

# Driftless — AI-Native SDLC CLI for Coding Agents

**Driftless** is a local-first CLI that provides an **outer-loop SDLC workflow layer** around [OpenSpec](https://openspec.sh)'s **inner-loop specification workflow**. It is designed for **coding agents** like **Claude Code** and **Cursor** to manage engineering work across the full lifecycle: from idea to specification, planning, implementation, verification, review, delivery, and completion.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Full SDLC Lifecycle](#full-sdlc-lifecycle)
- [CLI Reference](#cli-reference)
- [Contributing](#contributing)
- [Test Status](#test-status)
- [License](#license)
- [Authors](#authors)

---

## Installation

### From GitHub (latest release)

```bash
uv tool install git+https://github.com/aakashjangidme/driftless.git
```

### From local directory

```bash
uv tool install .
```

To update or reinstall:

```bash
uv tool install --force .
```

### Editable install (development)

```bash
uv tool install --editable .
```

---

## Quick Start

```bash
driftless init
driftless work create "<description>"
driftless change create <name>
driftless verify
driftless review
driftless finish
```

---

## Features

- **Work lifecycle management** — `CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE`
- **OpenSpec integration** — bridges AI agents to OpenSpec's inner-loop specification workflow
- **Git-aware state** — persists work state to `.driftless/` with full Git branch tracking
- **Agent-ready** — designed for Claude Code, Cursor, and other coding agents
- **CI/CD enforced** — branch protection, squash-merge, required reviews, and status checks

---

## Full SDLC Lifecycle

```text
CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE
```

---

## CLI Reference

### `driftless --version`

Show the installed version and exit.

### `driftless --verbose`

Enable debug-level logging to stderr.

### `driftless init`

Initialize Driftless and OpenSpec in the current repository.

### `driftless work create "<description>"`

Create a new unit of engineering work.

### `driftless work list`

List all works.

### `driftless work show W-0001`

Show details of a specific work.

### `driftless change create <name>`

Create an OpenSpec change and link it to the active work.

### `driftless status`

Show current Forge + OpenSpec + Git status.

### `driftless verify`

Verify work readiness (Git clean, OpenSpec valid).

### `driftless review`

Transition active work to REVIEW stage.

### `driftless finish`

Complete work and archive OpenSpec change.

---

## Contributing

Contributions are welcome! All changes must go through a PR with CI passing.

1. Fork the repo and create a feature branch
2. Make your changes with signed commits
3. Open a PR targeting `main`
4. CI must pass (Lint & Type Check + Tests)
5. At least 1 approving review required

```bash
git checkout -b feat/my-feature main
# make changes...
git commit -S -m "feat: ..."
git push -u origin feat/my-feature
gh pr create --fill
```

---

## Test Status

All **143 tests** pass with **0 failures**.

---

## License

MIT

---

## Authors

[aakashjangidme](https://github.com/aakashjangidme)
