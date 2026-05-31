---
description: TDD agent — implement using strict red → green → refactor cycles
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(pytest *), Bash(ruff *), Bash(mypy *), Bash(make *)
argument-hint: [feature, behavior, or bug to implement]
model: sonnet
context: fork
agent: general-purpose
---

# TDD

Implement using strict red → green → refactor. One test per cycle. One behavior per test.

## Target

$ARGUMENTS

## Cycle

### 1. RED
Write ONE failing test describing the expected behavior. Run it in isolation:

```bash
pytest tests/test_<module>.py::<TestClass>::<test_name> -x --tb=short
```

Confirm it fails with the expected **assertion** error — not import/syntax errors. If it fails on import, create a minimal stub so the test fails on assertion.

### 2. GREEN
Write the simplest code that passes. No future-proofing. No extra branches "while you're there." Run the single test, then the full suite:

```bash
pytest -x --tb=short
```

### 3. REFACTOR
All green? Clean up: extract, rename, deduplicate. Then:

```bash
ruff check --fix . && ruff format .
mypy --strict src/
pytest -x --tb=short
```

Repeat red → green → refactor until all acceptance criteria have passing tests.

## Rules

- **Naming**: `test_<action>_<condition>_<expected>` — e.g. `test_classify_returns_password_intent_when_reset_keyword_present`.
- **One test per cycle.** Do not write a batch of tests upfront.
- **Bug fix flow**: write a reproducing test first (must fail), then fix.
- **Never** add broad `except Exception`, `pass` in except, mocked returns in production code, or stubs that return hardcoded success. These are banned by `scripts/check-no-fake-success.sh`.
- **Never** skip or xfail a test to reach green faster.
- Touch only files relevant to the current behavior.

## Done criteria

- All acceptance criteria have passing tests.
- `make verify` is green.
- Coverage check run with `pytest --cov=src --cov-report=term-missing`; gaps are either filled or explicitly justified in the completion summary.

## Completion summary

Report: the behavior implemented, number of red → green cycles, final coverage delta, and `make verify` result.
