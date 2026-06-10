# CascadeCare — Deferred Fixes (polish, time-permitting)

Things that work well enough for the demo but should be cleaned up before final submission.
Ordered by priority. None of these block the core demo (full 3-level walk + master HITL gate
+ Slack close-out all work live).

---

## ~~P1 — Grandchild HITL app auto-submits~~ — RESOLVED 2026-06-10

**Was:** the grandchild "Prepare & File Obligation Response" gate completed immediately
because the Autopilot-generated app `Regulatory/Contractual Obligation Response`
(id `de1f291b-ff90-47b7-87b3-d7a08db1792b`) had no human-required outcome.

**Fix shipped:** the app's Action Schema now has blocking **File / Withdraw** outcomes
(SubmitAction rules on each button), republished into `Shared/CascadeCare-v110`; deployment
**1.0.21** (from canonical) re-bound the gate to `de1f291b`. Verified live: grandchild
instance `bc4cbace`, gate `t9BUmAX8k` → **InProgress** (element-executions show the
paused-on-AppTask pattern: task + CancelTaskBoundaryEvent both InProgress). The reviewer's
clicked outcome lands in the auto `Action` output; the 4 mapped outputs (ReviewerId,
ResponseDisposition, ResponseNarrative, FiledTimestamp) carry the case data.

**TRACKING note also closed:** 1.0.21 eliminated the deployed-vs-repo drift — live and
canonical both bind `de1f291b`, and it pauses.

---

## P3 — Canvas "already installed by active deployment" publish warnings

Publishing the solution **from the Studio Web canvas** is blocked by warnings that the
low-code agents / grandchild app are "already installed by an active deployment of this
solution." This is why canvas publish fails — but it does **not** affect the CLI
pack→publish→deploy path (that's how every version 1.0.13–1.0.20 shipped). Clean-up would
mean reconciling the solution resource references so the canvas can publish too. Low priority
(CLI deploy is the working path).

---

## COSMETIC — 6 spawns yield 12 children

Each of the master's 6 "Spawn Stakeholder Parent" tasks creates **2** child instances (12
total) due to platform **450007 "Duplicate message subscription"** double-delivering the
spawn message. Each spawn task completes once; the platform creates the duplicate. No clean
case-definition knob. Harmless for the fan visual; note it if a judge asks.

---

## Reference — what's confirmed working (do NOT touch)

- Full 3-level walk: master → 6 stakeholder children → obligation grandchild (commit
  `a74b0f5`, 1.0.19+). Spawn fix = `tfmtATbvb` entry re-pointed to `current-stage-entered`.
- Master Reversal-4 HITL gate (`tvlKcFYnW` → `CascadeCare`) pauses + Action Center + Slack
  close-out → master Completed.
- ViVE vertical-bridge workflows fire once per child (medical-records / claim-denial /
  prior-auth).
- Deploy recipe + auth + monitoring: see `docs/DEMO-RUNBOOK.md`.
