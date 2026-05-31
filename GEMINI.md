# GEMINI.md — CascadeCare Network Command

> Gemini CLI reads this file for project instructions.
> All universal rules live in AGENTS.md. Read it first.

## Read this first

The canonical project rules — naming conventions, IP safety, TDD requirement,
file conventions, SPEC GATE, memory system, autopilot protocol, and all stop
conditions — are in `AGENTS.md`. This file supplements them with Gemini-specific notes.

## Architecture (one line)

Pure-UiPath at runtime. Python is build-time + Coded Agent scaffolding only.
See `specs/003-uipath-native/plan.md` for the full current plan.

## Gemini-specific behaviour

- **Yolo mode** (`gemini --yolo`) is Autopilot. The same three halt conditions
  apply: failed acceptance test, SPEC GATE awaiting approval, session-summary
  request after slice completion. Everything else runs silently.
- Hooks (Claude Code `settings.json`) are not active in Gemini CLI sessions.
  The AGENTS.md rules apply by instruction instead — treat them as binding.
- `knowledge/` is immutable. The guard is instruction-level here (no hook).
  Refuse any edit to files in `knowledge/` regardless.

## Session start / end

```bash
# Start of every session:
python .agent-os/scripts/resume.py   # or:  make resume

# End of every session:
make save-session TASK=<slice> SUMMARY="..." DECISIONS="..." BLOCKERS="..." NEXT="..."
```

## Spec-kit workflow per slice

Slices are already defined in `specs/003-uipath-native/tasks.md`.
Skip `/speckit.specify`. For each slice:

```
/speckit.plan      paste the slice from tasks.md + tech constraints
/speckit.analyze   catch inconsistencies before coding
/speckit.tasks     break into subtasks; each must be individually testable
/speckit.implement Spec Gate fires per function — show SPEC block, wait for approval
```

## Additional context

For technologies, project structure, and shell commands:
`specs/003-uipath-native/plan.md`, `specs/003-uipath-native/data-model.md`,
`specs/003-uipath-native/tasks.md`
