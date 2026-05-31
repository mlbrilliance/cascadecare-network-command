# Project Configuration

> Project-specific settings the agent reads. Fill these in during bootstrap.
> AGENTS.md holds the universal rules; this file holds what changes per project.

## Language & Runtime
Python 3.12+ (build-time / Coded Agents only). UiPath at runtime.

## Package manager
uv

## Formatter / Linter command
uv run ruff check --fix && uv run ruff format

## Test command
uv run pytest

## Build command
uv run mypy src/

## Task runner
uv run (all dev commands via `uv run`; no Makefile)

## Spec-driven toolchain
Manual — agent performs plan → analyze → tasks → implement in sequence.
Spec Gate fires before every new function in agents/ or src/.

## Notes
- Pure-UiPath at runtime. Python is build-time / Coded Agent scaffolding only.
- knowledge/ is immutable. The PreToolUse hook blocks all writes there.
- TDD enforced: test file must exist before source file for agents/ and src/.
- All agent system prompts live in agents/prompts/*.md — never inline.
- .agent-os/memory/project_memory.db is the session-persistence store.
  Run `python .agent-os/scripts/resume.py` at session start.
  Run `python .agent-os/scripts/checkpoint.py` + `save_session.py` at task end.
