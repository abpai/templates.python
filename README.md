# Python Boilerplate with OpenAI Agents

This template is a **lean starting point** for Python projects that use:

* ✅ Ruff – formatting & linting
* 🧪 Pytest – testing
* ⚙️ Pydantic Settings – typed environment configuration
* 📦 uv – fast dependency management / locking

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
    *This creates a `.venv` directory in your project.*

2.  **Install Dependencies:**
    ```bash
    # Installs core + dev dependencies into your active venv
    make setup
    ```

3.  **Run the Quick-Start Agent Demo:**
    ```bash
    # This will use your activated environment
    make run
    ```

4.  **Run Quality Checks:**
    ```bash
    make format-check && make lint && make test
    ```

`main.py` is a minimal script that spins up an assistant. Modify it to explore the SDK.

---

## Make Commands

| Command            | Description                          |
| ------------------ | ------------------------------------ |
| `make install`     | Install core dependencies            |
| `make install-dev` | Install core + dev dependencies      |
| `make format`      | Format code with Ruff                |
| `make format-check`| Check formatting (CI mode)           |
| `make lint`        | Run Ruff linter                      |
| `make test`        | Run Pytest                           |
| `make clean`       | Remove *.pyc & cache directories     |
| `make lock-check`  | Assert `uv.lock` is in sync          |

---

## Environment Variables

`utils/settings.py` reads variables from a `.env` file or the environment.

| Variable          | Default       | Description                          |
| ----------------- | ------------- | ------------------------------------ |
| `OPENAI_API_KEY`  | (required)    | Your OpenAI API key.                 |
| `LOG_LEVEL`       | `INFO`        | `DEBUG`, `INFO`, `WARNING`, `ERROR`  |
| `LOG_FORMAT`      | `console`     | `console` (colored) or `json`.       |
| `DEFAULT_MODEL`   | `gpt-4o-mini` | Default model for agents.            |

See `.env.example` for a template.

---

## Folder Layout

Only what you need, nothing more:

```
├── main.py                   # Minimal OpenAI Agents example
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

## License

MIT
