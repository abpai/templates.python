# Python Boilerplate

This template is a **lean starting point** for Python projects that use:

- ✅ Ruff – formatting & linting
- 🧪 Pytest – testing
- ⚙️ Pydantic Settings – typed environment configuration
- 📦 uv – fast dependency management / locking
- 📝 structlog – structured logging

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

`src/main.py` is a minimal script with structured logging. Modify it to build your application.

---

## Make Commands

| Command            | Description                             |
| ------------------ | --------------------------------------- |
| `make install`     | Install core dependencies               |
| `make install-dev` | Install core + dev dependencies         |
| `make setup`       | Install dependencies + pre-commit hooks |
| `make format`      | Format code with Ruff                   |
| `make lint`        | Run Ruff linter                         |
| `make typecheck`   | Run Pyright type checker                |
| `make test`        | Run Pytest                              |
| `make clean`       | Remove \*.pyc & cache directories       |
| `make lock-check`  | Assert `uv.lock` is in sync             |

---

## Environment Variables

`utils/settings.py` reads variables from a `.env` file or the environment.

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
│   └── main.py               # Main application entry point
├── utils/
│   └── settings.py           # Pydantic Settings helper
├── tests/
│   └── test_basic.py         # Single sanity-check test
├── Makefile                  # Workflow commands
├── pyproject.toml            # Project + dependency config
├── uv.lock                   # Locked dependency versions
└── .github/workflows/        # CI (lint + test)
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

## License

MIT
