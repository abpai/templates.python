# Python Boilerplate

![CI](https://github.com/abpai/templates.python/actions/workflows/ci.yml/badge.svg)
![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This template is a **lean starting point** for Python projects that use:

- ✅ Ruff – formatting & linting
- 🧪 Pytest – testing
- ⚙️ Pydantic Settings – typed environment configuration
- 📦 uv – fast dependency management / locking
- 📝 structlog – structured logging
- 🔍 ty – fast type checking (Rust-powered)

---

## Quick Start

1.  **Create & Activate Virtual Environment:**

    ```bash
    # Create the virtual environment using uv
    uv venv
    # Activate it (on macOS/Linux)
    source .venv/bin/activate
    # On Windows, use: .venv\Scripts\activate
    ```

    _This creates a `.venv` directory in your project._

2.  **Install Dependencies:**

    ```bash
    # Installs core + dev dependencies into your active venv
    make setup
    ```

3.  **Run the Application:**

    ```bash
    # This will use your activated environment
    make run
    ```

4.  **Run Quality Checks:**
    ```bash
    make format && make lint && make test
    ```

`src/templates_python/main.py` is a minimal entry point with structured logging. Modify it to build your application.

---

## Make Commands

| Command            | Description                             |
| ------------------ | --------------------------------------- |
| `make install`     | Install core dependencies               |
| `make install-dev` | Install core + dev dependencies         |
| `make setup`       | Install dependencies + pre-commit hooks |
| `make format`      | Format code with Ruff                   |
| `make lint`        | Run Ruff linter                         |
| `make typecheck`   | Run ty type checker                     |
| `make test`        | Run Pytest                              |
| `make clean`       | Remove \*.pyc & cache directories       |
| `make lock-check`  | Assert `uv.lock` is in sync             |

---

## Environment Variables

`src/templates_python/utils/settings.py` reads variables from a `.env` file or the environment.

| Variable     | Default   | Description                         |
| ------------ | --------- | ----------------------------------- |
| `LOG_LEVEL`  | `INFO`    | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `console` | `console` (colored) or `json`.      |

See `.env.example` for a template.

---

## Folder Layout

Only what you need, nothing more:

```
├── src/
│   └── templates_python/
│       ├── main.py           # Main application entry point
│       └── utils/
│           └── settings.py   # Pydantic Settings helper
├── tests/
│   └── test_settings.py      # Settings validation tests
├── Makefile                  # Workflow commands
├── pyproject.toml            # Project + dependency config
├── uv.lock                   # Locked dependency versions
└── .github/workflows/        # CI (lint + typecheck + test)
```

---

## Optional: ML Dependencies

This template includes an optional ML dependency group for data science and machine learning projects:

```bash
# Install with ML dependencies
uv sync --extra ml
```

Includes: PyTorch, scikit-learn, MLflow, matplotlib, numpy, pandas, and seaborn.

---

## Type Checking with ty

This template uses [ty](https://github.com/astral-sh/ty), Astral's fast type checker written in Rust.

**Note:** ty is in alpha and under active development. While production use is not yet recommended, it's suitable for experimentation and early adoption.

```bash
# Run ty type checker
make typecheck
```

Configuration is in `pyproject.toml` under `[tool.ty]`.

---

## Code Style

This project uses **2-space indentation** and **single quotes** (configured in Ruff). While Python conventionally uses 4-space indentation, 2-space is a deliberate choice for more compact code. The formatter enforces this automatically.

Key style settings:
- Indent: 2 spaces
- Quotes: Single (`'`)
- Line length: 88 characters

---

## First Things To Edit

When copying this template into a new project, update:

- `[project] name`, `description`, `authors`, and `version` in `pyproject.toml`
- The import package name under `src/` (rename `templates_python/` to your project slug)
- The CLI entry in `[project.scripts]`

---

## License

MIT
