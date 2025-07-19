.PHONY: help install install-dev test lint format format-check clean setup pre-commit-install pre-commit-run lock-check run

export PYTHONPATH := .

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install core dependencies
	uv sync

install-dev: ## Install core + dev dependencies
	uv sync --extra dev

setup: install-dev pre-commit-install ## Full dev setup

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

lint: ## Run Ruff linter
	uv run ruff check .

format: ## Format code with Ruff
	uv run ruff format .

format-check: ## Check formatting (CI)
	uv run ruff format --check .

test: ## Run Pytest
	uv run pytest

clean: ## Remove caches & pyc files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

lock-check: ## Ensure uv.lock is up-to-date
	uv sync --locked --extra dev

run: ## Run the main application
	uv run python main.py
