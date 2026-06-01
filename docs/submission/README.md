# AgentHack 2026 — Submission Package Checklist

Slice 017 status. The **offline-completable** artifacts are DONE and machine-verified; the
**human-capture** artifacts below require a live tenant + recording and are carried forward.
Honest status only — no fabricated links.

## Required Devpost artifacts (4)

| # | Artifact | Status | Owner | Notes |
|---|----------|--------|-------|-------|
| 1 | Public GitHub repo (MIT) + README | ✅ DONE | — | [`README.md`](../../README.md) names every UiPath component; [`LICENSE`](../../LICENSE) MIT; gate `tests/unit/docs/test_readme_completeness.py` |
| 2 | Devpost project page | ⬜ PENDING (human) | — | Title, Track 1, business problem, architecture, screenshots. Source copy: README inventory + [`docs/architecture.md`](../architecture.md) |
| 3 | Demo video ≤5 min on YouTube/Vimeo | ⬜ PENDING (human) | — | Must show the solution running **live** on UiPath Automation Cloud (not slides); name each agent. Shot-list: [`docs/demo/run-playbook.md`](../demo/run-playbook.md). Hero (Reversal 3 fan-spawn) ~2:30 |
| 4 | Solution running live on Automation Cloud | ⬜ PENDING (tenant) | — | Open blockers: API workflow re-add (Error 2005), Maestro folder context, BPMN 1654 — see [`DEVIATIONS.md`](../../DEVIATIONS.md) |

## Bonus + supplementary

| Item | Status | Notes |
|------|--------|-------|
| Coding-agent bonus evidence | ✅ DONE | [`CODING_AGENTS.md`](../../CODING_AGENTS.md) + [`CLAUDE_CODE_USAGE.md`](../../CLAUDE_CODE_USAGE.md) + [`docs/coding-agents/`](../coding-agents/) |
| 1-min coding-agent reel | ⬜ PENDING (human) | Capture during the live demo session |
| Live-session screenshots / transcripts | ⬜ PENDING (human) | Channels scaffolded in [`docs/coding-agents/screenshots/`](../coding-agents/screenshots/) + [`docs/prompt-logs/`](../prompt-logs/) |
| Presentation deck | ⬜ PENDING (human) | Use the AgentHack-provided template |

## Release tag rule

Do **not** apply the `agenthack-2026-submission` git tag until artifact #4 (live demo recorded on
Automation Cloud) exists. The tag asserts a recorded live demo; tagging from an offline session
would be dishonest. Tag at the same commit as the final video upload.

## Deadlines (per `agenthack-2026-intel`)

- Submission: **June 29, 2026, 11:45 PM PDT** (early submission better — judging starts June 3).
- UiPath Labs access for judges: apply by June 5.
