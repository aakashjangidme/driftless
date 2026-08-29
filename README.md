![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg?logo=codecov)
![Build](https://img.shields.io/badge/pass-143%20tests-brightgreen.svg?logo=github-actions)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)

# Driftless — AI-Native SDLC CLI

**Driftless** is a local-first CLI providing an **outer-loop SDLC workflow layer** around OpenSpec's **inner-loop specification workflow**. It is designed to be used by coding agents such as **Claude Code**.

---

## Installation via `uv tool`

Driftless is packaged as a standard Python CLI tool buildable via `uv`.

### 1. Global Installation from Local Directory

From the `driftless` project directory, run:

```bash
uv tool install .
```

To update or reinstall:

```bash
uv tool install --force .
```

### 2. Global Installation from Git Repository

Once published to a Git repository:

```bash
uv tool install git+https://github.com/your-org/driftless.git
```

### 3. uv tool install --editable .

```bash
uv tool install --editable .
```

### 4. Manual install via pip

```bash
pip install driftless-cli
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

## Full SDLC Lifecycle

```text
CREATED → SPECIFYING → PLANNING → IMPLEMENTING → VERIFYING → REVIEW → DELIVERY → DONE
```

---

## CLI Reference

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

## Test Status

All **143 tests** pass with **0 failures**.

---

## License

MIT

---

## Authors

[aakashjangidme](https://github.com/aakashjangidme)

