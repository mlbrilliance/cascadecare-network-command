# CascadeCare — Deferred Fixes (polish, time-permitting)

Things that work well enough for the demo but should be cleaned up before final submission.
Ordered by priority. None of these block the core demo (full 3-level walk + master HITL gate
+ Slack close-out all work live).

---

## P1 — Grandchild HITL app auto-submits (no human pause)

**Symptom:** the grandchild "Prepare & File Obligation Response" gate completes immediately
instead of pausing for a reviewer.

**Root cause (A/B-proven, 2026-06-09):** the case wiring is correct — the gate `t9BUmAX8k`
(`clearflow-obligation-grandchild`, stage `Stage_F95sBP`) is a proper `Actions.HITL v2` task,
identical to the working master gate `tvlKcFYnW`, and its app binding resolves with no
`170015`. The problem is the **app itself**: `Regulatory/Contractual Obligation Response`
(id `de1f291b-ff90-47b7-87b3-d7a08db1792b`, Autopilot-generated) has **no human-required
outcome**, so the action returns at once. Proof: re-binding the same gate to the master's
`CascadeCare` app made it **pause** (`t9BUmAX8k` → InProgress, Action Center task created).

**Fix:**
1. In **Studio Web → Apps**, open `Regulatory/Contractual Obligation Response` and add a
   blocking action outcome — a submit/approve button the reviewer must click to complete the
   task (mirror how `CascadeCare` has Approve/Deny). Republish into `Shared/CascadeCare-v110`.
2. The canonical case already binds this gate to `de1f291b` (the CascadeCare re-bind was a
   test, reverted in the repo). So after the app is fixed: redeploy from canonical
   (runbook Path B) → spawn a child → verify the grandchild gate goes **InProgress** and
   renders an Action Center task.

---

## TRACKING — Deployed vs repo drift on the grandchild gate

**Right now:** live deployment **1.0.20** has the grandchild gate bound to **`CascadeCare`**
(a manual test binding — it pauses, but shows the master's fiduciary-review content, which is
the wrong narrative for an obligation gate). The **repo/committed** canonical binds it to the
correct app **`de1f291b`**.

**Implication:** a clean redeploy from canonical (runbook Path B) will revert the gate to
`de1f291b` — which auto-completes until **P1** is done. So do **P1 first**, then redeploy.
Until then, the live pause relies on the 1.0.20 CascadeCare binding that is *not* in git.

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
