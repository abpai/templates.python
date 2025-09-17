# General Rules

## Environment and Dependencies
- **Tooling**: Use `uv` for all package management.

## Code Style

**Format**: 2-space indent, single quotes, `snake_case` vars/functions, `PascalCase` classes, `is_/has_/should_` booleans

**Architecture**:
- Pure functions preferred; classes for stateful operations (3+ shared params), data structures, framework requirements
- RORO pattern: service functions receive/return single Pydantic objects
- Single responsibility: break 150+ line functions into focused 15-25 line methods, early returns, no magic values, explicit dependencies
- DRY principle: extract utility functions to eliminate code duplication when applicable
- Pipeline pattern: chain transformations with clear inputs/outputs
- No excessive error handling or low-value comments

## Codex Commands

Conventions:
- Any user message that **starts with** `!` is a command.
- Be non-verbose. For commands, print a single status line (or a short block) on success/failure.
- Use UTC timestamps. Touch only files inside this repo.
- If a directory you need doesn’t exist, create it.

Commands:

- `!summarize [slug]`: Read `.codex/commands/summarize.md` for command instructions.
