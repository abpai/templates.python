# Python Template

![CI](https://github.com/abpai/templates.python/actions/workflows/ci.yml/badge.svg)
![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A small application template with a `src` layout, uv dependency locking,
Ruff formatting and linting, ty type checking, pytest branch coverage,
validated environment settings, and structured logging.

Python 3.13 is the default; CI also tests Python 3.14. Code uses two-space
indentation, single quotes, and an 88-character line length.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
these commands from your copy of this repository:

```bash
uv sync --locked
uv run --locked pre-commit install
uv run --locked templates-python
```

uv creates `.venv` and selects Python automatically. Activating the environment
is optional. On macOS/Linux, `make setup` performs the first two steps.
Git hooks require a Git checkout; if you downloaded an archive, initialize Git
or skip hook installation.

```bash
make check                         # Lockfile, lint, formatting, types, quality policy, tests
LOG_FORMAT=json make run           # JSON logging to stderr
uv run --locked python -m templates_python
```

Without Make (including Windows), run:

```bash
uv lock --check
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check
uv run --locked --project tools/quality python tools/quality/check.py
uv run --locked --project tools/quality python -m unittest discover -s tools/quality
uv run --locked pytest
```

## Commands

| Command | Purpose |
| --- | --- |
| `make setup` | Install development dependencies and Git hooks |
| `make install` | Sync production dependencies only |
| `make install-dev` | Sync core and development dependencies |
| `make run` | Run the application with production dependencies |
| `make check` | Run all local quality checks without editing source files |
| `make lint` / `make lint-fix` | Check lint rules / apply safe fixes |
| `make format-check` / `make format` | Check formatting / format code |
| `make typecheck` | Check source and tests with ty |
| `make test` | Run tests with branch coverage and an 80% minimum |
| `make lock-check` | Check the lockfile without installing dependencies |
| `make pre-commit-run` | Run all Git hooks; formatting hooks can edit files |
| `make build` | Build a wheel and source archive in `dist/` |
| `make clean` | Remove generated caches without traversing `.venv` or `.git` |

`uv sync` includes the development dependency group by default. Use `--no-dev`
for a production environment. A later `uv run` without `--no-dev` makes the
development tools available again. Routine commands use `--locked`, so dependency
metadata changes require an explicit lockfile update.

## Configuration

Copy `.env.example` to `.env` if you need local overrides. Environment variables
take precedence over `.env`; defaults apply when neither supplies a value.
Unrelated `.env` keys are ignored, and invalid logging values fail validation.

| Variable | Default | Accepted values |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (case-insensitive) |
| `LOG_FORMAT` | `console` | `console`, `json` |

`AppSettings` is immutable. `get_settings()` caches one instance for the process;
call `get_settings.cache_clear()` when deliberately reloading configuration.
Tests isolate environment variables, `.env` files, logging, and the settings cache.

`configure_logging(settings)` takes an explicit settings object and configures
root logging at application startup. Call it from an application's entry point;
importing the package does not change logging. Both structlog and standard-library
loggers emit timestamps, levels, logger names, and bound context. JSON logs include
exception tracebacks; console colors are disabled when output is redirected.

```python
import structlog

from templates_python.utils.logging import configure_logging
from templates_python.utils.settings import AppSettings

configure_logging(AppSettings(log_format='json'))
structlog.contextvars.bind_contextvars(request_id='request-123')
structlog.get_logger(__name__).info('Work completed', item_count=5)
structlog.contextvars.clear_contextvars()
```

## Optional notebook and ML tools

Notebook tools are separate from everyday development dependencies:

```bash
uv sync --locked --group notebook
uv run --locked --group notebook python -m ipykernel install --user --name my-project
```

The `ml` extra retains PyTorch, scikit-learn, MLflow, matplotlib, NumPy, pandas,
and seaborn:

```bash
uv sync --locked --extra ml
uv run --locked --extra ml python your_script.py
```

Keep the extra/group flags on later `uv run` commands when those tools are needed.
The ML stack is optional and is not covered by core CI; validate it against your
platform and GPU requirements before adopting it.

## Quality checks and upgrades

Git hooks run file checks, the project's locked Ruff version, ty, and lockfile
validation. The full test suite runs via `make check` and CI. Annotation lint rules
require typed function signatures; ty checks their use.

CI uses locked dependency installs, pinned Actions, read-only repository
permissions, and cancellation of superseded runs. It checks Python 3.13 and 3.14,
builds both distribution formats, and runs the installed wheel's CLI and module
entry points outside the source checkout. Dependabot proposes monthly Actions
updates.

To change dependencies intentionally:

```bash
uv add some-package
uv add --dev some-tool
uv lock --upgrade-package some-package
make check
make build
```

Review and commit `pyproject.toml` and `uv.lock` together. Use `uv lock --upgrade`
only when you intend to update the entire graph, including optional ML packages.
CI pins uv 0.11.2, the version used to validate this setup; review that pin when
upgrading uv. See [uv's dependency group documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies)
and [its CI guide](https://docs.astral.sh/uv/guides/integration/github/).

## Customize a copy

1. Update project name, description, version, authors, and license in `pyproject.toml`.
2. Rename `src/templates_python/` and update imports in source and tests.
3. Update `[project.scripts]`, the Hatch wheel package path, and both coverage settings.
4. Update CLI/module names in the Makefile, CI package smoke checks, tests, and README.
5. Replace the CI badge URL and review `AGENTS.md` for your team's conventions.
6. Run `uv lock`, `make check`, and `make build` after renaming.

The application starts in `src/templates_python/main.py`. Settings and logging
live separately under `src/templates_python/utils/`. Extend the functional core
with domain code as needed; this template does not impose a web framework,
database, or deployment target.

## Python quality policy

Run `make quality quality-test` for the blocking complexity and type-suppression
gates. Run `make quality-advisory` for annotation, API-size and design guidance.
See [tools/quality/README.md](tools/quality/README.md) for scope, pinned tools,
reviewed baselines and exceptions.

## Migration from earlier copies

- Replace `uv sync --extra dev` with `uv sync`; development tools now use a
  dependency group rather than a published extra.
- Add `--group notebook` when using Jupyter tools.
- Import `configure_logging` from `templates_python.utils.logging` and pass an
  `AppSettings` instance instead of a level string.
- `make lint` only checks; use `make lint-fix` to change code.
- Invalid logging settings now fail at startup instead of silently falling back.

## License

MIT. See [LICENSE](LICENSE).
