.DEFAULT_GOAL := help
.PHONY: help install install-dev setup pre-commit-install pre-commit-run lint lint-fix format format-check typecheck test check clean lock-check run build

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies only
	uv sync --locked --no-dev

install-dev: ## Install core and development dependencies
	uv sync --locked

setup: install-dev pre-commit-install ## Set up development tools and Git hooks

pre-commit-install: ## Install pre-commit hooks
	uv run --locked pre-commit install

pre-commit-run: ## Run pre-commit hooks on all tracked files
	uv run --locked pre-commit run --all-files

lint: ## Check lint rules without changing files
	uv run --locked ruff check .

lint-fix: ## Apply safe lint fixes
	uv run --locked ruff check . --fix

format: ## Format Python code
	uv run --locked ruff format .

format-check: ## Check formatting without changing files
	uv run --locked ruff format --check .

typecheck: ## Run ty type checking
	uv run --locked ty check

test: ## Run tests with branch coverage
	uv run --locked pytest

check: lock-check lint format-check typecheck quality quality-test test ## Run all local quality checks

clean: ## Remove generated caches without traversing environments or Git
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml

lock-check: ## Check lockfile freshness without installing packages
	uv lock --check

run: ## Run with production dependencies
	uv run --locked --no-dev templates-python

build: ## Build a source archive and wheel
	uv build

.PHONY: quality quality-advisory quality-test
quality: ## Block new or worsening complexity and unsafe type suppressions
	uv run --locked --project tools/quality python tools/quality/check.py

quality-advisory: ## Report annotation, API-size, exception, and performance advice
	uv run --locked --project tools/quality python tools/quality/check.py --advisory

quality-test: ## Test the quality policy without ML dependencies or credentials
	uv run --locked --project tools/quality python -m unittest discover -s tools/quality -p 'test_*.py'
