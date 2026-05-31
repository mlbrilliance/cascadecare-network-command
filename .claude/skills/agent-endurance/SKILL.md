---
name: agent-endurance
description: Structure long-running Claude Code sessions on this Python project so the agent iterates for hours instead of stopping after one pass. Use when the user mentions "long-running session", "multi-hour run", "agent keeps stopping", "agent finishes too early", "headless run", "tmux session", "milestones", "make verify", "fake success", "prevent shortcuts", or asks how to set up hooks, a verification gate, or an operating contract for an autonomous coding agent.
---

# Agent Endurance

Structure long-running Claude Code sessions so they iterate for hours instead of stopping after one pass.

## When to use this skill

- Setting up a new multi-hour or overnight run on this repo.
- Diagnosing why an agent finishes too early or claims completion without evidence.
- Adding hooks, milestones, or a verification gate to an existing session.

## Why agents stop early

Agents default to "produce a plausible completion." Without enforcement they will attempt a one-shot implementation, claim success without verification, swallow errors via broad `try/except` or mocked returns, and stop at the first "good enough" output.

The fix is never "ask harder." It is changing the environment.

## Setup checklist

### Step 1: Decompose into milestones

Break the project into 5–20 small milestones. Each has its own definition of done. Store them in `MILESTONES.md` at the repo root. Example already checked in — update statuses as work progresses (`pending → CURRENT → done / blocked`).

### Step 2: Single verification command

`make verify` is the gate. It runs `pytest -x --tb=short`, `ruff check .`, `ruff format --check .`, and `mypy --strict src/`. The agent runs it after every meaningful edit. Do not skip it.

### Step 3: Operating-contract prompt

The user-facing prompt reads like a contract: scope lock, verification mandate, anti-fake-success rules, failure protocol, evidence requirement, and explicit process order (Read → plan → execute one subtask → verify → repeat).

Full template: `references/prompt-template.md`.

### Step 4: Hooks

Hooks are deterministic — they run even if the model forgets or tries to skip verification. Configure in `.claude/settings.json`:

- **PostToolUse** on `Write|Edit|MultiEdit` → auto-format.
- **Stop** → `make verify`; exit 2 blocks the stop.
- **Stop** → `scripts/check-no-fake-success.sh`; exit 2 blocks the stop.

Full configs: `references/hooks-config.md`.

### Step 5: Prevent fake-success

Most common failure mode. Run `scripts/check-no-fake-success.sh` from a Stop hook. It fails on:

- `except Exception` in `src/**/*.py`
- Empty `except:` blocks with `pass`
- Stub returns (`return True  # stub`, `return None  # stub`)
- Unreferenced `# TODO` / `# FIXME`

Also require that every new function has at least one test exercising real behavior, and ban mocked network calls in production code.

### Step 6: Multi-hour runs

For sessions >1 hour, use persistent infrastructure:

- `claude -p` in a tmux/screen session on a VPS.
- CI runners with the agent in the loop.
- Headless mode with `--output-format stream-json` for log inspection.

### Step 7: Subagents

Use the `Task` tool only for clearly separable concerns. More subagents ≠ better — they multiply context drift. Default to a single agent with hooks.

## Example

User says: "Run this project overnight until M3 is done."

Actions:
1. Confirm `MILESTONES.md` marks M1, M2 as done and M3 as `CURRENT`.
2. Fill in `references/prompt-template.md` with milestone M3 details.
3. Verify `.claude/settings.json` has the Stop hook on `make verify` and `check-no-fake-success.sh`.
4. Launch `claude -p "$(cat prompt.txt)"` inside tmux.
5. Next morning, check `MILESTONES.md` and the session log for the completion summary.

Result: agent iterates on M3 only, cannot stop until `make verify` is green, and cannot introduce the banned shortcuts.

## Troubleshooting

### Agent finishes too quickly

**Cause:** Missing one of the four gates.
**Fix:** Check in order — (1) milestones exist and are scoped, (2) `make verify` target exists and runs, (3) anti-fake-success script is wired to a Stop hook, (4) prompt requires an evidence-bearing completion summary.

### Stop hook never fires

**Cause:** Agent invokes a different stop path, or hook config is malformed.
**Fix:** Run `claude --debug` and confirm the Stop hook is registered. Validate `.claude/settings.json` is valid JSON.

### `make verify` passes but code is clearly broken

**Cause:** Tests are mocked or skipped; checks cover too little.
**Fix:** Audit `tests/` for `@pytest.mark.skip`, `mock.patch` of production functions, and coverage gaps. Add the anti-pattern to `scripts/check-no-fake-success.sh`.

### Quick diagnostic

If the agent keeps finishing too quickly, tighten these four in order — same model will iterate much longer:

1. No milestones → task too broad.
2. No `make verify` → no verification gate.
3. No anti-fake-success rules → agent takes shortcuts.
4. No evidence requirement → agent claims done without proof.
