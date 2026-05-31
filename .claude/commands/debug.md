---
description: Debug agent — reproduce → isolate → hypothesize → fix, one hypothesis at a time
allowed-tools: Read, Grep, Glob, Edit, Bash(pytest *), Bash(make *), Bash(ruff *), Bash(mypy *)
argument-hint: [error message, test name, or traceback]
model: sonnet
context: fork
agent: general-purpose
---

# Debug

Diagnose this issue using the `debug-trace` methodology. Do not shotgun-debug.

## Target

$ARGUMENTS

## Process

1. **Reproduce** — run the failing test or trigger the error in isolation:
   `pytest tests/test_<module>.py::<test_name> -x --tb=long -vv`
   If no test exists, write one before debugging.
2. **Isolate** — read the full traceback. Find the innermost frame in *our* code. Inspect locals one line before the failure with `logger.debug(f"inputs: {locals()}")`.
3. **Hypothesize** — state ONE hypothesis. Verify with a minimal assertion or change. If wrong, discard and restate — do not stack hypotheses.
4. **Fix** — apply the fix, run the specific test, then `make verify`.
5. **Clean** — remove all temporary debug logging before finishing.

## Project-specific traps

Check these before guessing:

- OCR output encoding — `bytes` vs `str` mismatches from the ingestion layer.
- Pydantic validation errors — inspect `exc.errors()` and `model.model_dump()` to see which field failed.
- Async/sync mismatch in FastAPI endpoints — sync function calling an async dependency or vice versa.
- Fixture order in pytest — run with `--setup-show`.

## Constraints

- One hypothesis at a time.
- No broad `except Exception` or `pass` in except blocks — these are banned by `scripts/check-no-fake-success.sh`.
- Do not disable tests to make failures go away.
- Touch only the files needed for the diagnosis and fix.

## Completion summary

Report: root cause, the one-line explanation of *why* the bug existed, what changed, and `make verify` result.
