# Python quality policy

Run `make quality quality-test` from the repository root. CI and pre-commit run the same gate.
The separate, locked Python 3.13 tool environment needs no application imports,
ML environment, credentials, database or cloud service.

| Policy | Enforcement |
| --- | --- |
| Cyclomatic complexity | Ruff C901, maximum 10 |
| Cognitive complexity | Complexipy, maximum 15 |
| Chained casts / widening then casting back | anti-slop errors |
| Type suppressions | Specific checker code and meaningful SAFETY explanation |
| Blanket lint suppressions | Ruff PGH004 |
| Existing complexity | Per-function ceilings in `complexity-baseline.json` |
| Existing suppression debt | Exact fingerprints in `anti-slop-baseline.json` |

Unused lint suppressions remain covered by the existing application Ruff checks.
They need the full project rule set to distinguish used and unused ignores.

The gate measures complete function bodies, including changes under unchanged
`def` lines. Complexity ignores are disabled. Exceptional functions belong in
the reviewed baseline. Identities include path and lexical name; moves and renames
therefore need baseline review. Ordinary checks do not modify files.

The template starts with empty baselines. New violations fail immediately.
The gate itself and its tests also have no complexity allowances.

## Tools and isolation

Ruff 0.16.8, Complexipy 8.0.1 and anti-slop-py at commit
`86ea16d3abb2322e0496c5b6da8cd6d5704166cf` are pinned in this directory's `uv.lock`.
The audited upstream anti-slop source is an immutable Git dependency instead of
a copied source tree; its license remains with the installed source package.

anti-slop-py requires Python 3.12+, so the gate runs on Python 3.13. The quality tools
are separate from runtime dependencies. The existing application
Ruff and ty configuration remains separate.

## Advisory checks

`make quality-advisory` reports annotations, argument counts (5 total, 4
positional), statements (40), branches, returns, broad exceptions, simplification
and performance advice. Findings do not fail; tool/configuration errors do.
These thresholds are in `check.py`.

Typer callbacks, SDK adapters, fixtures and per-job/per-segment error boundaries
need context. The gate permits `isinstance`, `object`, mocks, dynamic attributes,
open dictionaries and names containing `shape`. Never remove input validation or
alter cleanup semantics merely to lower a score. Prefer typed domain contracts
where one exists, without adding wrappers just to satisfy lint.

## Baseline maintenance

Prefer fixing the finding. To record an intentional exception or move:

```bash
uv run --locked --project tools/quality python tools/quality/check.py --update-baseline
```

This explicit maintenance command must never run in CI. Review both JSON files.
Every new/increased allowance or suppression needs a reason in the PR. Reduce or
remove an allowance in the same change that improves a function. Checks permit
improvements and print how many allowances can be tightened; until updated, the
previous baseline ceiling remains the allowed maximum.

A moved function needs explicit matching of old and new entries during review.
Missing tools/baselines, syntax errors and incompatible baseline limits fail the
check. Policy tests exercise new/worse complexity, body edits, file/line changes,
suppression handling and valid boundary patterns.

## Scope

Blocking paths are in `[tool.quality]` in the application `pyproject.toml`. New
Python files in these paths are checked, including untracked files. Add new
top-level code directories explicitly. Notebook cells are excluded. Scope,
policy and baseline changes require review like code changes. Application tests
remain `make test`; static checks do not prove runtime or production parity.

References: [Ruff C901](https://docs.astral.sh/ruff/rules/complex-structure/),
[Complexipy](https://complexipy.com/usage-guide/), and
[the audited anti-slop source](https://github.com/TinyFrontier/anti-slop-py/tree/86ea16d3abb2322e0496c5b6da8cd6d5704166cf).
