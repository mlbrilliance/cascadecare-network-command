# AgentHack 2026 — Submission Package Checklist

Status as of 2026-06-12 (slice 023 closed). The build artifacts are DONE — including the
**live deployment** (artifact #4) — and the remaining **human-capture** artifacts
(video, Devpost page, deck) are carried forward. Honest status only — no fabricated links.

## Required Devpost artifacts (4)

| # | Artifact | Status | Owner | Notes |
|---|----------|--------|-------|-------|
| 1 | Public GitHub repo (MIT) + README | ✅ DONE | — | [`README.md`](../../README.md) names every UiPath component; [`LICENSE`](../../LICENSE) MIT; gate `tests/unit/docs/test_readme_completeness.py` |
| 2 | Devpost project page | ⬜ PENDING (human) | — | Paste-ready copy drafted: [`DEVPOST.md`](DEVPOST.md) (fill `[HUMAN]` links/screenshots; clear `[VERIFY]` items live first) |
| 3 | Demo video ≤5 min on YouTube/Vimeo | ⬜ PENDING (human) | — | Must show the solution running **live** (not slides); name each agent. Full shot-list + narration: [`VIDEO-SCRIPT.md`](VIDEO-SCRIPT.md); run procedure: [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md). Hero (Reversal 3 fan-spawn) ~2:30 |
| 4 | Solution running live on Automation Cloud | ✅ DONE (live) | — | `clearflow-solution` 1.0.23 deployed to `Shared/CascadeCare-v110`; full cascade live-proven 2026-06-12 (master + 6 children + 6 grandchildren all Completed). The former blockers (Error 2005, Maestro folder context, BPMN 1654) were resolved in slices 015–023 — see [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md) |

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

- Submission: **June 29, 2026, 11:45 PM EDT** (early submission better — judging is rolling, started June 3).
- UiPath Labs access for judges: apply by June 5.
