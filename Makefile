.PHONY: help install install-dev setup pre-commit-install pre-commit-run lint format typecheck test clean lock-check run

export PYTHONPATH := .
VENV_DIR = .venv

help:
	@echo 'Available commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:
	uv sync

install-dev:
	uv sync --extra dev

setup:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo 'Creating virtual environment in $(VENV_DIR)...'; \
		uv venv; \
	fi
	@echo 'Installing dependencies...'
	@uv sync --extra dev
	@echo 'Installing pre-commit hooks...'
	@uv run pre-commit install
	@echo '\n✅ Setup complete. To activate the environment, run:\nsource .venv/bin/activate'

pre-commit-install:
	uv run pre-commit install

pre-commit-run:
	uv run pre-commit run --all-files

lint:
	uv run ruff check . --fix

format:
	uv run ruff format .

typecheck:
		uv run pyright

test: ## Run Pytest
	uv run pytest

clean: ## Remove caches & pyc files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "pycache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage

lock-check: ## Ensure uv.lock is up-to-date
	uv sync --locked --extra dev

run: ## Run the main application
	uv run python src/main.py
