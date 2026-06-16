# Demo Guide — Criterion-3 Exceptions + the 6-Way Fan-Out

The two highest-scoring moments to film, with exact commands and what to put on screen.
For the full end-to-end run, see [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md) (Path A). This guide
covers only the two "money" segments and is **honest about what works today vs. what needs a tiny
addition**.

```bash
export FK=de7b7c18-d743-4c8c-b555-9bd3b96fe524        # Shared/CascadeCare-v110 folder key
MASTER=AC365BA5-C807-4DFC-A009-00F3EA61E497           # clearflow-master-crisis process key
```

> **Authoritative status surface:** the **Maestro → Case Instances** view, NOT the Orchestrator
> Jobs view. Completed Maestro case instances never flip their backing job to Successful (it shows
> "Running" forever) — judging from Jobs would look broken. Always show case status from Case
> Instances or `uip maestro case instance list --folder-key $FK`.

---

## SEGMENT 1 — The 6-way fan-out (hero shot, ~t+150s)

**What it is:** at the **Regulatory Response** stage (`Stage_JM1SVs`) the master caseplan holds
**6 `case-management` spawn tasks** (Northstar + Providers Alpha–Epsilon), each of which spawns its
own obligation-grandchild → **6 children + 6 grandchildren = 13 instances across 3 levels**, live on
the canvas. This is genuinely rare; most submissions are single-process or 2-level.

**How to trigger:** fully automatic. Start the master and let it walk:
```bash
uip or jobs start $MASTER --folder-key $FK --output json
```
The master auto-walks Initial Response → Multi-Customer Investigation → Vector Isolation →
**Regulatory Response (fan-out here)** → Fiduciary Review → Litigation Defense → Closed. No manual
step triggers the fan-out.

**What to put on screen (the money shot):**
- **Primary:** the **Maestro Case Instances** list (the heatmap), split-screen with the
  **master case canvas** open on the Regulatory Response stage. Film the 6 child instances landing
  at **1× speed** (do not speed up — the simultaneity is the point). Hold it ~8–10 seconds.
- **Secondary (narrative):** the Coded Web App dashboard at
  `https://hackathon26_042.staging.uipath.host/clearflow-network-command` — the Energy-Flow cascade
  view. Good for the exec framing, but the Case Instances view is the *proof*.

**Watch it from the CLI while filming** (counts instances by nesting level):
```bash
uip maestro case instance list --folder-key $FK --output json | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d),'instances')"
```

**Narration:** *"One subpoena. Six providers, each with a different BAA. Watch Maestro Case fan out
six child cases simultaneously — and each one spawns its own obligation grandchild. Three levels of
live case nesting, no custom orchestration code."*

---

## SEGMENT 2 — Exception handling (Criterion 3, your #1 edge)

Criterion 3 explicitly scores exception/failure/edge-case handling, and it's the most
under-demonstrated criterion in hackathons. You have **three** showable stories, ranked here by how
clean they are to film. Do **A** for sure; **C** is the "meaningful human oversight" beat; **B** is
advanced/optional.

### 2A — In-agent graceful degradation (CLEANEST — recommended)

**The point:** when the LLM Gateway fails, the forensic agent does **not** crash — it catches the
error, surfaces `error_type`/`error_message`, and **still returns the correct route** (routing is
deterministic; only the advisory narration needed the LLM). "Fail safe, not fail over."

**Where it surfaces:** the forensic task `tFSEXam01` (Vector Isolation) writes `error_type` and
`error_message` as **case instance variables**, readable live:
```bash
uip maestro case instance variables <instanceId> --folder-key $FK
```

**How to demo it deterministically (off-tenant, ~30s):** run the agent locally where the Gateway
call fails, on a non-escalate input (`nimbus_indicators > 0` so enrichment actually runs):
```bash
cd agents/forensic-self-exam-agent-langgraph
uv run uipath run agent '{"nimbus_indicators": 3, "clearflow_indicators": 0}'
# → route_to="baa-boundary", clearflow_vector_status="cleared",
#   rationale="", error_type=<the failure class>, error_message=<detail>
```
Then show the test that proves the contract, green:
```bash
uv run pytest tests/agents/test_forensic_langgraph.py -k error_surfacing -v
```

**Narration:** *"I'll knock out the LLM Gateway. A naive agent crashes and faults the case. Ours
catches it, records exactly what failed — error type and message — and still routes correctly. The
case keeps moving; the failure is on the record, not swallowed."*

> ⚠️ **Honest gap + the 3-line fix.** There is **no failure-injection switch today**. The local run
> above relies on the Gateway call failing in your local env (auth/SDK), which is slightly
> non-deterministic. For a *deterministic, explainable* on-camera failure, add a tiny env guard to
> `enrich_node` — `if os.getenv("FORENSIC_FORCE_ENRICH_ERROR"): raise RuntimeError("Simulated LLM Gateway 520")`
> — ~3 lines + a test, so you can say *"I set this flag to simulate a Gateway 520"* and it fails the
> same way every take. **Ask and I'll build it (TDD).** It also lets the degradation be shown in-case,
> not just locally.

### 2B — Operator fault + recover (advanced / optional)

**The point:** a faulted case is recoverable by an operator, with a full audit trail.

**Reality check (be honest in the demo):** the only way to *induce* a fault today is to **delete a
HITL gate task** in Action Center (→ incident `ErrorCode 160009`, IncidentType "User") — which
collides with the HITL story in 2C, so do it on a **throwaway run**, not your main demo instance.
The recovery verbs are confirmed live:
```bash
uip maestro case instance incidents <instanceId> --folder-key $FK   # shows the 160009 incident
uip maestro case instance retry    <instanceId> --folder-key $FK   # recovers the faulted instance
uip maestro case instance get      <instanceId> --folder-key $FK   # confirm it resumed
```
**On screen:** the **Action History** of the case instance in the Case Instance Management console —
it records the incident and the retry as a timestamped audit trail (strong auditability evidence).

**Recommendation:** if time is tight, *mention* this layer with the CLI + incidents output rather
than staging a live fault. The in-agent story (2A) already proves graceful failure handling cleanly.

### 2C — Meaningful human oversight (Approve vs Deny) — CORRECTED

**Important correction:** the Deny branch does **not** rework/rewind a stage (earlier guidance was
wrong). Both Approve and Deny complete the gate and advance the case identically. What makes the
human's choice *meaningful* is that it is **recorded as an auditable ruling** (reviewerId + rationale
+ timestamp) **and consumed downstream**: `reviewerDecision="approved"|"denied"` is read by the
Reversal-5 agents to frame ClearFlow as a *cooperative* vs *contesting* party.

**How to reach it:** automatic — the master pauses at **Fiduciary Review** (`Stage_LKuLeU`), task
`tvlKcFYnW`. The AppTask renders in **Action Center → Tasks** (folder `CascadeCare-v110`, app
`CascadeCare`) with the Fiduciary Conflict Detector's pre-filled conflict analysis.

**Choose Deny (app):** click **Deny**, fill ReviewerId / ReviewerContext (rationale). Then show it
recorded + consumed:
```bash
uip maestro case instance variables <instanceId> --folder-key $FK   # reviewerDecision="denied", reviewerId, reviewTimestamp
```
**CLI alternative** (works — `demo_autocomplete.py` proves it; assign first):
```bash
uip tasks assign   <taskId> --user you@org.com
uip tasks complete <taskId> --type AppTask --folder-id <fid> --action Deny \
  --data '{"ReviewerId":"...","ReviewerDecision":"Deny","ReviewerContext":"BAA + insurer freeze override the payer demand"}'
```

**To show BOTH Approve and Deny:** there is one fiduciary task per run, so **run the master twice**
(`demo_autocomplete.py` keeps `DEMO_KEEP_FIDUCIARY=2` — one Approve, one Deny — and
`DEMO_KEEP_OBLIGATION=2` — one File, one Withdraw — for live action; run `--dry-run` first).

**Narration:** *"The agent surfaces a three-way conflict — payer demand vs. provider BAAs vs. insurer
freeze — but it does not decide. A human rules. I'll Deny: ClearFlow refuses the payer, citing BAA
obligations. That decision is stamped with who decided, why, and when — and the litigation-defense
agents downstream now frame ClearFlow as a contesting party. Human-in-the-loop that actually changes
the response, with a compliance-grade audit trail."*

---

## Suggested 90-second Criterion-3 cut (order)

1. **2A** in-agent graceful degradation (~30s) — break the Gateway, agent surfaces error + routes anyway.
2. **2C** Deny at the fiduciary gate (~40s) — human rules, decision recorded + consumed downstream.
3. **2B** one line on operator `instance retry` + the incident audit trail (~15s) — "and if a case
   does fault, an operator recovers it with a full audit history."

This lets a time-boxed judge score Criterion 3 at the top of the band in under two minutes — while
most submissions never show a single failure.

---

## Honest gaps (so nothing in the video is a surprise)
- **No failure-injection tooling** for 2A today → add the `FORENSIC_FORCE_ENRICH_ERROR` env guard
  (offered above) for a deterministic take; otherwise prove locally via the SDK-absent run + the test.
- **2B fault path is destructive** (delete a gate) → use a throwaway run, or just narrate the CLI.
- **`docs/DEMO-RUNBOOK.md` A4 is stale** — it says there's no CLI for the gates; `uip tasks complete
  --type AppTask` works (see `scripts/demo_autocomplete.py`). One-line doc fix pending.
- **`docs/demo/run-playbook.md` is superseded** — follow `DEMO-RUNBOOK.md`.
