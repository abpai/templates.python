# AI Agent Code Guidelines

This document provides coding guidelines for AI agents working on this Python project.

## Environment and Dependencies

- **Tooling**: Use `uv` for all package management
- **Python Version**: 3.13+
- **Package Manager**: uv (fast, modern dependency management)
- **Type Checker**: ty (Astral's fast type checker, alpha stage) - `make typecheck`
  - Note: ty is in early development and may have bugs/missing features

## Code Style

**Format**: 2-space indentation, single quotes, 88-character lines, `snake_case` variables/functions, `PascalCase` classes, boolean flags prefixed with `is_/has_/should_`. Pre-commit hooks ensure code quality on commit.

**Docstrings**:

- Use simple one-line docstrings for most functions - be concise and descriptive
- Type hints replace Args/Returns documentation - don't duplicate what's in the signature
- No Examples section - type hints + function name should be self-explanatory
- Exception: Top-level user-facing APIs may include brief usage notes if necessary
- Rationale: Modern Python with PEP 484 type hints makes verbose docstrings redundant

**Comments**:

- Avoid narrating the code; prefer clear names and small functions
- Comments should explain *why* (tradeoffs, invariants, pitfalls), not *what*
- Delete commented-out code instead of keeping it around

**Naming**:

- Prefer domain-specific, intention-revealing names over generic ones (`process`, `handle`, `manager`, `util`)
- Keep public API names stable and unsurprising; avoid cleverness

## Architecture Principles

**Classes for state and lifecycle**, pure functions for transformations. Use classes when managing resources, coordinating operations, or defining interfaces.

**Protocols over inheritance**: Define interfaces with `typing.Protocol` for flexible, duck-typed implementations.

**Immutable configs**: Frozen dataclasses with `__post_init__` validation and factory classmethods (`from_uri()`, `from_dict()`).

**Factory functions**: Standalone functions (`get_backend()`, `resolve_config()`) that map configurations to implementations.

**Resource management**:

- Reference counting for expensive resources (connections, clients) with acquire/release semantics
- Context managers (`__enter__`/`__exit__`) for automatic cleanup
- Track ownership with boolean flags to avoid closing borrowed resources

**Streaming over bulk**: Use `Iterator[T]` to yield chunks for large datasets. Implement retry logic within generators for resilience.

**Separation by lifecycle**: Split read and write operations into distinct classes, even when working with the same backend (e.g., `SessionStoreReader`, `SessionStoreWriter`).

**Domain exceptions**: Create specific exception types rather than generic `RuntimeError`.

**Performance**: Use `@dataclass(slots=True)` for frequently-instantiated objects and `TypeVar` for type-safe generic protocols.

**Resilience**: Exponential backoff for network operations, graceful empty returns over exceptions, debug logging for key metrics. Keep error handling targeted (catch specific exceptions, add context, re-raise/convert).

## Best Practices

- RORO pattern: service functions receive/return single Pydantic objects
- Single responsibility: break 150+ line functions into focused 15-25 line methods
- Early returns, no magic values, explicit dependencies
- DRY principle: extract utility functions to eliminate duplication
- Pipeline pattern: chain transformations with clear inputs/outputs
- No excessive error handling or low-value comments

## Code Quality Bar (What to Avoid)

When generating code, optimize for reviewability and long-term maintainability.

- **Unnecessary comments**: If a comment just restates the code, remove it and improve naming/structure instead
- **Long docstrings**: Keep most docstrings to a single line; only expand when a public API truly needs usage notes
- **Overly defensive code**: Don’t add “just in case” checks everywhere; validate at boundaries and trust validated data internally
- **Broad `try/except`**: Avoid wrapping whole functions; don’t swallow exceptions; catch specific errors only to recover or add context
- **Deep nesting**: Prefer guard clauses and extraction to keep indentation shallow (avoid multi-level `if/for/try`)
- **Bad abstractions**: Don’t create classes/protocols/layers without clear value; avoid one-method wrappers and “framework-building”
- **Vague naming**: Avoid generic verbs (`do`, `process`, `handle`) and generic buckets (`utils`, `helpers`) for core logic
- **Weak typing / schemas**: Avoid `Any` and unstructured `dict[str, Any]` in core code; prefer Pydantic models (or narrow typed objects) with explicit fields and validation
- **Noisy error handling**: Prefer a small number of well-placed domain exceptions over many `RuntimeError`/`ValueError` catch-alls

## Pydantic Commitment

- All interface models use Pydantic `BaseModel` (not dataclasses)
- Validation, `.model_dump()`, JSON serialization built-in
- Reserve `@dataclass(slots=True)` only for inner performance-critical helpers (graph traversal caches, etc.)
