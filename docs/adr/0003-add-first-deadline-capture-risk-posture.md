# ADR-0003: Add-first, deadline-capture, full-set-or-nothing risk posture

- **Status:** accepted
- **Date:** 2026-06-03

## Context
After the Academy course, the team chose to maximize the submission: add all four enhancement
bundles (SLA+escalation+Notification; agent-driven+Agent Memory; OOTB Case App+heatmap;
evals+targeted re-entry) plus the healthcare vertical bridge, build first, and capture the demo
video at the deadline (June 28–29) rather than early. The team explicitly set the bar at "full
feature set or nothing" — no reduced fallback submission. Three live-deploy blockers remain open
(Slice-019 carry-forwards T-a4/T-b3/T-c4, each requiring interactive `uip login`).

## Decision
Honor the maximal posture. To keep it from degrading into "finish nothing," impose ONE
non-negotiable guardrail that does not conflict with capturing late: **resolve the live-deploy
blockers early (Slice S020) and re-verify the full live path after every subsequent slice.**
Building late is acceptable; discovering a dead live path late is not.

## Rationale
"Full-set-or-nothing" + "capture at the deadline" + an unresolved blocker on June 28 = no
captured submission at all. Continuous live-path verification is cheap insurance that preserves
maximum build time while removing the single fatal failure mode.

## Alternatives considered
- Capture-first baseline then layer — lowest risk; rejected by the team (wanted maximum ceiling).
- No fixed guardrail — leaves the fatal "dead live path discovered late" failure mode open.

## Consequences
- S020 runs first and its live tasks (T-a4/T-b3/T-c4) are human-gated (interactive login) — the
  team executes them via `! uip login` + the Slice-019 runbook.
- Every slice ends with a live-path re-verification step.
- Future reviews should NOT re-litigate the scope cut; "nothing cut" is a recorded decision.
