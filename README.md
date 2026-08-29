![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg?logo=codecov)
![Build](https://img.shields.io/badge/pass-143%20tests-brightgreen.svg?logo=github-actions)
![PyPI](https://img.shields.io/pypi/v/driftless-cli?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)

# Driftless — AI-Native SDLC CLI

**Driftless** is a local-first CLI providing an **outer-loop SDLC workflow layer** around OpenSpec's **inner-loop specification workflow**. It is designed to be used by coding agents such as **Claude Code**.

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

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Full SDLC Lifecycle](#full-sdlc-lifecycle)
- [CLI Reference](#cli-reference)
- [Test Status](#test-status)
- [License](#license)
- [Authors](#authors)

---

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

## Test Status

All **143 tests** pass with **0 failures**.

---

## License

MIT

---

## Authors

[aakashjangidme](https://github.com/aakashjangidme)

