.PHONY: install-hooks lint test format typecheck pre-commit

install-hooks:
	uv sync --group dev
	pre-commit install
	@echo "Pre-commit hooks installed. Hooks will run on every commit."

lint:
	uv run ruff check src/driftless

format:
	uv run ruff format src/driftless

typecheck:
	uv run mypy src/driftless --ignore-missing-imports

test:
	uv run pytest tests/

pre-commit:
	pre-commit run --all-files

all: lint format typecheck test
