# General Rules

## 1. Environment and Dependencies
- **Tooling**: Use `uv` for all package management.

## 2. Code Style and Formatting
- **Indentation**: Strictly use 2 spaces for indentation.
- **Quotes**: Use single quotes (`'`) for all strings. Use double quotes (`"`) only when a string contains a single quote.
- **Naming Conventions**:
  - `snake_case` for all variables, functions, methods, files, and directories.
  - `PascalCase` for all class names (e.g., `Pydantic` models, custom exceptions).
- **Boolean Variables**: Name boolean variables with an auxiliary verb prefix (e.g., `is_active`, `has_permission`, `should_send_email`).

## 3. Programming Paradigm and Structure
- **Functional Approach**: Prefer pure, standalone functions. Avoid classes unless necessary.
- **Class Usage Exceptions**: Use classes only for:
  - Data structures (Pydantic models).
  - Framework requirements (e.g., Django models, FastAPI routers).
  - Custom exception types.
- **Modularity (DRY)**: Do not repeat code. Refactor any duplicated logic into reusable functions. Group related utility functions into separate modules (e.g., `utils/data_processing.py`).

## 4. API and Function Design
- **RORO Pattern**: All service-layer functions and API endpoint handlers must follow the "Receive an Object, Return an Object" pattern.
- **Data Contracts**: Use Pydantic models to define the "objects" for RORO. The input object should be a single Pydantic model, and the return value should be a single Pydantic model (or `None`).
