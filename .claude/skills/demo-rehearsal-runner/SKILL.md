---
name: demo-rehearsal-runner
description: "Activate when rehearsing or testing the demo runner. Guides dry-running the 3-minute demo end-to-end against the local stack."
---

# Demo Rehearsal Runner

## Purpose

Guide dry-running the 3-minute demo end-to-end, including expected state transitions per reversal.

## When to Activate

- Rehearsing the demo
- Testing the demo runner
- Validating reversal acceptance criteria
- Building Slice 017 (demo runner)

## Demo Timeline

Total runtime: ~3 minutes (180 seconds)

| Timestamp | Event | Expected State Change |
|---|---|---|
| 0:00 | Show baseline dashboard | Normal metrics, no active cases |
| 0:15 | Day 0: Northstar anomaly | Master case opens, 3 child cases, network risk score jumps |
| 0:25 | Day 0: Alpha anomaly | Second child case opens |
| 0:35 | Day 1: Beta anomaly → Reversal 1 | Pattern Detector fires, master goal shifts, correlation visualization |
| 0:50 | Day 3: PHI signal (child event) | BAA Exposure child case opens, evidence added |
| 1:00 | Day 5: Reversal 2 | ClearFlow cleared, Nimbus identified, posture decision |
| 1:15 | Day 14: Liquidity stress (child event) | Payment Continuity escalates, cash-at-risk counter updates |
| 1:30 | Day 30: Reversal 3 | Subpoena → BAA Reasoner → 6 grandchild cases → three-level nesting visible |
| 1:50 | Day 45: Reversal 4 | Apex demands data, fiduciary conflict, tri-party HITL gate |
| 2:10 | Day 90: Reversal 5 | Litigation cascade, co-defendant posture, privilege reshuffle |
| 2:30 | Show executive brief | Current state summary, evidence pack, decision history |
| 2:50 | Closing | Demo closing line |

## Validation Checklist Per Reversal

For each reversal, verify:
- [ ] Master goal changed (check goalHistory)
- [ ] Correct child cases opened/reopened
- [ ] Evidence added with correct privilege scope
- [ ] HITL decision appeared (if applicable)
- [ ] Agent recommendation displayed
- [ ] Timeline event rendered
- [ ] Network risk score updated
- [ ] Cash-at-risk counter updated (if applicable)

## Acceptance Criteria Cross-Reference

Map each reversal to its acceptance criteria in REQUIREMENTS.md and Build Brief.
