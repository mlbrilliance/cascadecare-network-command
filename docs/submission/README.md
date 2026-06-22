# AgentHack 2026 — Submission Package Checklist

Status as of 2026-06-22 (solution 1.0.35 live; dashboard v1.0.15 live). The build artifacts are
DONE — including the **live deployment** (artifact #4) — and the remaining **human-capture**
artifacts (video, Devpost page, deck) are carried forward. Honest status only — no fabricated links.

## Required Devpost artifacts (5)

| # | Artifact | Status | Owner | Notes |
|---|----------|--------|-------|-------|
| 1 | Public GitHub repo (MIT) + README | ✅ DONE | — | [`README.md`](../../README.md) names every UiPath component; [`LICENSE`](../../LICENSE) MIT; gate `tests/unit/docs/test_readme_completeness.py` |
| 2 | Devpost project page | ⬜ PENDING (human) | — | Paste-ready copy drafted: [`DEVPOST.md`](DEVPOST.md) (fill `[HUMAN]` links/screenshots; clear `[VERIFY]` items live first) |
| 3 | Demo video ≤5 min on YouTube/Vimeo | ⬜ PENDING (human) | — | Must show the solution running **live** (not slides); name each agent. Full shot-list + narration: [`VIDEO-SCRIPT.md`](VIDEO-SCRIPT.md); run procedure: [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md). Hero (Reversal 3 fan-spawn) ~2:30 |
| 4 | Solution running live on Automation Cloud | ✅ DONE (live) | — | `clearflow-solution` 1.0.35 deployed to `Shared/CascadeCare-v110`; full cascade live-proven (latest preserved runs 2026-06-22: `CFCS-67730745`, `CFCS-67767069` — master + 6 children + 6 grandchildren all Completed, incl. closure + in-case audit-ledger write). The former blockers (Error 2005, Maestro folder context, BPMN 1654) were resolved in slices 015–023 — see [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md) |
| 5 | Completed presentation deck | ⬜ PENDING (human) | — | **Mandatory** per Devpost rules; AgentHack template at <https://bit.ly/3R0MsHU>. Host on Drive/OneDrive/Dropbox with public ("access to all") permission. Content brief: [`DECK-BRIEF.md`](DECK-BRIEF.md) |

## Bonus + supplementary

| Item | Status | Notes |
|------|--------|-------|
| Coding-agent bonus evidence | ✅ DONE | [`CODING_AGENTS.md`](../../CODING_AGENTS.md) + [`CLAUDE_CODE_USAGE.md`](../../CLAUDE_CODE_USAGE.md) + [`docs/coding-agents/`](../coding-agents/) |
| 1-min coding-agent reel | ⬜ PENDING (human) | Capture during the live demo session |
| Live-session screenshots / transcripts | ⬜ PENDING (human) | Channels scaffolded in [`docs/coding-agents/screenshots/`](../coding-agents/screenshots/) + [`docs/prompt-logs/`](../prompt-logs/) |
| Product-feedback form | ⬜ OPTIONAL (human) | Earns **Best Product Feedback** ($1,500); form closes **Jul 2, 2026**. Draft: [`PRODUCT-FEEDBACK.md`](PRODUCT-FEEDBACK.md) |

## Release tag rule

Do **not** apply the `agenthack-2026-submission` git tag until artifact #4 (live demo recorded on
Automation Cloud) exists. The tag asserts a recorded live demo; tagging from an offline session
would be dishonest. Tag at the same commit as the final video upload.

## Deadlines (per `agenthack-2026-intel`)

- Submission: **June 29, 2026, 11:45 PM EDT** (early submission better — judging is rolling, started June 3).
- UiPath Labs access for judges: **resolved** — the `staging.uipath.com/hackathon26_042` tenant *is* the Labs environment, and the public MIT repo also satisfies judge access (optional courtesy email: andreea.tomescu@uipath.com).
- Product-feedback form closes **July 2, 2026, 11:45 PM EDT**; People's Choice voting **July 3–30, 2026**.
