# CascadeCare — Presentation Script & Talking Points

A scene-by-scene guide for the live demo and the judge Q&A. Every answer here maps to a live
artifact on the tenant.

---

## Opening Hook (30 seconds)

> "On February 21, 2024, a cyberattack hit the largest healthcare clearinghouse in the United
> States. Within 24 hours, providers across the country couldn't submit claims. Within a week,
> billions of dollars in payments were frozen. It took months to fully recover — and the manual
> coordination was chaos.
>
> CascadeCare shows how that response looks when Maestro Case is running it."

---

## Scene 1 — The Crisis Starts (Reversal 1)

**What you show:** Master crisis case starts, first agent stage runs.

**What you say:**
> "A provider goes dark. ClearFlow's claim-flow anomaly detector — a coded Python agent running
> on an Orchestrator time trigger every 15 minutes — sees claim volume drop 94%. It scores
> severity 'critical'. The multi-customer pattern detector confirms the same fingerprint across
> three providers. That's a cascade signal, not an isolated outage.
>
> The ClearFlowIdealIncidentResponse BPMN catches that event at its Incident Intake node, runs
> triage, and the is_cascade gateway routes to spawning this master crisis case. No human kicked
> this off. It took seconds from detection to case creation."

**If asked "how does it detect in real time?"** → See Judge Q&A section below.

---

## Scene 2 — The Hero Moment (Reversal 3, ~2:30 in video)

**What you show:** Six grandchild obligation cases fan out simultaneously on the canvas.

**What you say:**
> "Day 30. Tennessee DOI issues a subpoena — Reversal 3. Watch the canvas.
>
> One state regulatory action fans out six obligation grandchild cases simultaneously — one per
> provider stakeholder affected by the subpoena. Three levels of native Maestro Case nesting,
> live. This is the architecture that lets ClearFlow manage 37 simultaneous legal and compliance
> obligations as structured cases with SLAs, agents, and human gates — not a spreadsheet."

---

## Scene 3 — The HITL Gate (Reversal 4)

**What you show:** Action Center task for Tri-Party Fiduciary Conflict Review.

**What you say:**
> "Reversal 4. Apex Health Plan invokes an operational-visibility clause and demands direct access
> to provider claim data — threatening to withhold remittances in 72 hours.
>
> The Fiduciary Conflict Detector agent identifies the three-way collision: Apex's contract demand
> vs. provider BAA confidentiality terms vs. the Aurora Specialty insurer freeze directive.
> Complying with Apex violates at least two BAAs. The agent surfaces this to a human reviewer
> here, in Action Center, with the full conflict analysis pre-populated.
>
> This is AI doing the legal triage. The human makes the call. The case records it and moves on."

---

## Scene 4 — Vertical Bridge

**What you show:** Impact Assessment stage in stakeholder-parent, UiPath Healthcare Solutions running.

**What you say:**
> "At ViVE 2026, UiPath shipped Medical Records Summarization, Claim Denial Prevention, and Prior
> Authorization as standalone agentic solutions. CascadeCare is the Maestro Case layer that
> orchestrates them under fire.
>
> When a provider stakeholder enters Impact Assessment, CascadeCare invokes all three as
> case-coordinated tasks — not in isolation. The medical records agent, the claim denial agent,
> and the prior auth agent all run inside the same stakeholder case, with their outputs feeding
> the case's obligation classification. That's the vertical bridge."

---

## Judge Q&A

### "How does it detect a real crisis? You kicked this off manually."

> "Manual start is for demo pacing. In production, the `ClearFlowIdealIncidentResponse` BPMN is
> the entry point, and its start event binds to an Integration Service webhook — a SIEM alert,
> an EDI monitoring platform, or a claim-queue watchdog.
>
> The detection pipeline is fully built:
>
> 1. **claim-flow-anomaly-detector** (coded agent, Orchestrator time trigger, every 15 min) —
>    watches claim volume telemetry for each provider. When claim_drop_pct exceeds threshold and
>    anomaly_score hits critical, it fires.
>
> 2. **multi-customer-pattern-detector** (coded agent) — correlates across all providers. Same
>    failure fingerprint on 3+ providers = cascade signal. This prevents a single-provider outage
>    from triggering a full crisis response.
>
> 3. **BPMN routing** — the is_cascade? gateway decides: isolated incident (standard playbook)
>    or cascade (spawn master crisis case). Both paths are live.
>
> Swapping the 14 mock API workflow endpoints for live EDI connector feeds is the only
> production-readiness delta. The orchestration logic doesn't change."

### "What's the time-to-detect?"

> "15-minute polling cycle on claim telemetry, configurable down to real-time via webhook. For
> reference, the real incident class this models went undetected at scale for days and took hours
> for first-responder organizations to manually activate. CascadeCare spawns the master case
> within seconds of cascade confirmation."

### "Why three levels of case nesting? Couldn't you do this with a flat case?"

> "Each level has a different owner, SLA, and lifecycle. The master crisis is owned by ClearFlow
> leadership — it drives strategy across the 90-day timeline. Stakeholder parents are owned by
> the relationship manager for each provider or payer — they track impact and obligations per
> partner. Grandchild cases are owned by legal or compliance per obligation — each has its own
> BAA reference, jurisdiction, and filing deadline.
>
> Flattening this would mean one case with 37 obligations all at the same level, no SLA
> differentiation, and no clean way to assign ownership. The nesting IS the architecture that
> makes it manageable."

### "Is this HIPAA-compliant? PHI is flowing through agents."

> "Every LLM call flows through the UiPath LLM Gateway → Trust Layer from the first agent
> invocation. There are two active policies: a PHI/PII detection pool that blocks or redacts
> patient identifiers, SSNs, and NPI-format claim numbers before they reach the model, and a
> content filtering pool for healthcare-sensitive output. PHI never leaves the UiPath governance
> boundary. That's not a demo constraint — it's enforced at the infrastructure layer."

### "Why UiPath for this? Couldn't you build this in LangGraph or a custom orchestrator?"

> "You could. But you'd be rebuilding what Maestro Case already gives you natively: SLA
> escalation, HITL gates, three-level case nesting, agent invocation, Data Fabric, Context
> Grounding, Trust Layer PHI guardrails, Action Center, and the Orchestrator job runtime — all
> integrated, all governed, none requiring custom code to wire together.
>
> With LangGraph you write the orchestrator. With Maestro Case you describe the process and
> UiPath runs it. For a crisis that spans 90 days, 37 obligations, 6 stakeholders, and 2 human
> approval gates — that's the right level of abstraction."

### "What happens after the demo ends? Is this production-ready?"

> "The architecture is production-ready as specified. What the demo uses:
> - 14 mock API workflows fronting fictional external systems → swap for live IS connectors
> - Simulated claim telemetry in Data Fabric → swap for live EDI feed
> - Manual demo driver pacing → swap for Orchestrator time trigger on anomaly detector
>
> The orchestration layer — case nesting, agent routing, HITL gates, SLA escalation, Trust Layer
> — runs identically in production. ClearFlow Health Network is fictional. The crisis class is not."

---

## Closing (20 seconds)

> "Healthcare is UiPath's number one vertical push for 2026. The agents UiPath shipped at ViVE —
> Medical Records, Claim Denial, Prior Auth — do the work. CascadeCare is the Maestro Case layer
> that coordinates them when the network is on fire.
>
> When a provider goes dark, the payment network feels it first. Now there's a system that feels
> it too — and acts."
