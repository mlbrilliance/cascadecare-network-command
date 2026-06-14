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

## Scene 3 — The HITL Gates (Reversals 3 & 4)

**What you show:** Action Center — both the Tri-Party Fiduciary Conflict Review (master crisis)
and the Prepare & File Obligation Response tasks (grandchild × 6).

**What you say:**
> "Two types of human decision, running in parallel.
>
> At the top level — Reversal 4. Apex Health Plan invokes an operational-visibility clause and
> demands direct access to provider claim data, threatening to withhold remittances in 72 hours.
> The Fiduciary Conflict Detector agent identifies the three-way collision: Apex's contract demand
> vs. provider BAA confidentiality terms vs. the Aurora Specialty insurer freeze directive.
> Complying with Apex violates at least two BAAs. The agent surfaces this here, pre-populated,
> with its full conflict analysis.
>
> At the same time — Reversal 3 already fired. Six grandchild obligation cases are waiting for
> their own reviewers to prepare and file each individual DOI subpoena response.
>
> Two different decisions. Two different case levels. Both waiting for humans simultaneously.
> That's Maestro Case nesting working exactly as intended."

**Approve vs. Deny (Fiduciary gate) — what to say:**
> "If I Approve — ClearFlow cooperates with Apex under restricted disclosure terms. Contractual
> alignment with the payer, but disclosure risk if providers challenge the BAA breach.
>
> If I Deny — ClearFlow refuses, citing BAA obligations and the insurer freeze directive. Stronger
> HIPAA compliance posture, but Apex may escalate to remittance withholding.
>
> Either way, the case records my decision, my identity, and my timestamp. That's the audit trail
> that matters in a regulatory investigation."

**File vs. Withdraw (Obligation Response gate) — what to say:**
> "For each of the six obligation grandchildren — I can File the response to the DOI subpoena, or
> Withdraw. File means the obligation is resolved, audited, closed. Withdraw means ClearFlow
> chose not to respond — and the case records that as a compliance gap. In production, a withdrawal
> triggers the SLA breach escalation path: the relationship manager gets notified, the obligation
> is flagged for the next regulatory cycle.
>
> CascadeCare tracks not just what was done. It tracks what wasn't done — and why."

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

### "Why not just kick off the claim-flow-anomaly-detector directly, instead of the master crisis case?"

> "In production, you DO kick it off — it runs on an Orchestrator time trigger every 15 minutes,
> right now, on the tenant. When it fires at critical severity, the multi-customer-pattern-detector
> confirms the cascade, and the BPMN spawns the master crisis case. They are sequential steps in
> the same pipeline, not alternatives.
>
> The reason you can't replace the master case with just the anomaly detector: a Python function
> scores telemetry, returns a severity score, and exits. It holds no state. After it fires — who
> coordinates the 6 providers? Who tracks the 37 legal obligations over 90 days? Who manages the
> BAA compliance, the DOI subpoena, the payer fiduciary conflict, the insurer freeze directive,
> the SLA escalations, and the two human approval gates? That is Maestro Case.
>
> The anomaly detector is the smoke alarm. The BPMN is the 911 call. The master crisis case is
> the incident command structure. You need all three."

### "Why not just run the Medical Records / Claim Denial / Prior Auth agents directly?"

> "Those agents each handle one clinical job for one provider. Without CascadeCare coordinating
> them you'd run each of 3 agents for each of 6 providers — 18 manual invocations with no shared
> state, no SLA tracking, no legal layer, no human approval gates, and no case record.
>
> A payment-network crisis isn't one clinical job. It's a BAA compliance review, a state
> regulatory subpoena, a payer fiduciary conflict, an insurer reservation-of-rights directive,
> and a clinical continuity problem, all happening simultaneously across six providers. Each is a
> different agent, a different obligation, a different deadline, and potentially a different human
> reviewer.
>
> CascadeCare tells those agents when to run, for which provider, under which legal constraints,
> in what order. That's the vertical bridge — CascadeCare is the crisis orchestrator for the
> agents UiPath already ships."

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

### "Why did the master crisis keep advancing even though you hadn't approved the obligation responses yet?"

> "Because they're independent concerns on independent timelines — and that's correct.
>
> The master crisis advancing to R4 (Payer Fiduciary demand on Day 45) doesn't depend on whether
> individual obligation responses from R3 (DOI subpoena on Day 30) have been filed. In a real
> crisis, the incident command doesn't freeze while field teams file paperwork. New information
> keeps arriving; new reversals keep happening.
>
> Maestro Case models this correctly. Nested cases are independent. The HITL gate pauses only the
> specific case waiting for human input — not the entire case network. The master crisis paused
> at R4 waiting for the Fiduciary Review; the grandchildren paused at their Obligation Response
> gate simultaneously. Both waiting at the same time, independently. That's not a flaw. That's
> parallel case management.
>
> The demo compresses 90 days to minutes. In production, Day 30 events and Day 45 events are
> separated by two weeks of real-world work. The architecture is identical."

### "What does Approve vs. Deny actually change downstream?"

> "The `reviewerDecision` output variable from the Fiduciary gate is read by the R5 co-defendant
> stage. Approve frames ClearFlow as a cooperative party in the litigation — weaker BAA protection
> but lower adversarial friction with the payer. Deny frames ClearFlow as contesting the payer
> demand — stronger HIPAA/BAA compliance posture, higher adversarial risk.
>
> Either way, the case advances to R5. The decision isn't about skipping stages. It's about what
> posture the subsequent agent takes when ClearFlow is named a co-defendant. Same case, different
> legal framing based on what the human decided 15 days earlier."

### "What does File vs. Withdraw mean for each obligation response?"

> "File means the DOI subpoena response is formally submitted. The audit record shows
> `disposition=filed` with a timestamp — compliance confirmed, obligation closed, no escalation.
>
> Withdraw means ClearFlow chose not to respond to that specific obligation. The audit record
> shows `disposition=withdrawn`. The grandchild case still closes — there's no rework loop that
> forces a filing — but the compliance gap is permanent in the case record. In production, that
> withdrawal triggers the SLA breach escalation path: the relationship manager for that stakeholder
> gets notified, the obligation gets flagged for the next regulatory review cycle, and the master
> crisis summary reflects an unresolved obligation.
>
> For a demo with mixed File and Withdraw decisions: 'I filed the urgent ones and withdrew the
> low-priority responses to show that CascadeCare handles both outcomes. The system doesn't just
> track successful compliance — it tracks where compliance broke down and why.'"

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
