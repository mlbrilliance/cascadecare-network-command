# CascadeCare — The Architecture Diagram, Explained

A companion to [`docs/images/architecture.png`](../images/architecture.png). It tells you **what the
diagram is**, then **what it does** as a flow story (Day 1 → Day 90), then walks the picture panel by
panel in the real UiPath terminology — and ends with a say-it-out-loud script and a glossary. New
terms are defined inline and collected at the end.

---

## In one breath

> One **UiPath Maestro Case** orchestrates an entire healthcare-payment crisis end to end. The
> master case (`clearflow-master-crisis`) walks itself through seven stages over a simulated 90 days,
> calls **12 agents** as `type:"agent"` tasks inside those stages, **spawns** child and grandchild
> cases via the native `case-management` task as the crisis spreads, pauses at two **Action Center**
> human gates, and on closure writes an immutable **AuditRecord** ledger to **Data Fabric** — every
> LLM call governed by the **UiPath LLM Gateway + Trust Layer**, with no external orchestrator.

## What the diagram is

It's a schematic of a **running** UiPath solution, in two numbered sections: **① Orchestration** (the
Maestro Case at runtime — stages, agents, nesting, human gates, Trust Layer) and **② Data,
Integration & Surfaces** (the platform foundation it runs on), plus a **vertical bridge** to UiPath's
own healthcare agents and a footer. The architectural claim it makes: **the Maestro Case canvas *is*
the orchestrator** — there is no Python/LangGraph harness driving it from outside.

## The big idea

UiPath ships healthcare **agents** — Medical Records Summarization, Claim Denial Prevention, Prior
Authorization — but each runs **one job, one provider, in isolation**. A payment-network cyberattack
that freezes claims across **six hospital systems at once** doesn't need a better soloist; it needs a
**conductor** that decides which agent runs, for which provider, in what order, under which legal
constraint. CascadeCare is that conductor — and the conductor is a Maestro Case.

---

## The flow, as a story (Day 1 → Day 90)

Read the diagram left to right and this is the story it tells. The protagonist is **ClearFlow Health
Network** (a fictional payment intermediary) sitting between six hospitals and four payers.

1. **Day 1 — Initial Response.** A provider (Northstar Regional Health) goes dark and claim volume
   collapses. An **Integration Service API Workflow** emits the event; a **Maestro Trigger** routes it
   to the **Claim Flow Anomaly Detector** (Coded Agent · Python SDK), which flags the anomaly. The
   master case opens.

2. **Reversal 1 (Day 1) → Multi-Customer Investigation.** A second provider shows the same signature.
   The **Multi-Customer Pattern Detector** (Coded) correlates across providers — this is **network-
   wide, not isolated** — and the case advances to Multi-Customer Investigation.

3. **Reversal 2 (Day 5) → Vector Isolation.** The vendor (Nimbus) is implicated as the attack vector.
   The **Forensic Self-Exam Agent** (Coded · **LangGraph `StateGraph`**) examines ClearFlow's *own*
   infrastructure — is the intermediary itself compromised? — and returns `vector_status="cleared"`,
   which satisfies the stage exit (`=js:vars.var_clearflow_vector_status === 'cleared'`). The **Vector
   Hypothesis Agent** (Agent Builder) forms the breach hypothesis. The case clears Vector Isolation.

4. **Reversal 3 (Day 30) → Regulatory Response — the hero moment.** A state insurance regulator
   (TN DOI) issues a subpoena. Every provider now needs a **lawful, individualized** answer, so the
   master **fans out 6 `clearflow-stakeholder-parent` cases at once** via the native
   `case-management` task — one per provider. Inside each parent, the **BAA Boundary Reasoner** (Agent
   Builder, grounded on the live `BAA-corpus` via **Context Grounding**) decides what may lawfully be
   disclosed under *that* provider's Business Associate Agreement, and **Assess Claim Disruption**
   sizes the liquidity hit. Each parent then spawns a **`clearflow-obligation-grandchild`**, where
   **Classify Obligation** triages each legal obligation. **Thirteen instances** now run — 1 master +
   6 parents + 6 grandchildren — **three levels of native nesting.** *Six providers, six lawful
   answers, one subpoena.*

5. **Reversal 4 (Day 45) → Fiduciary Review — the human gate.** A payer (Apex) demands action that
   conflicts with a provider's BAA *and* ClearFlow's own duties. The **Fiduciary Conflict Detector**
   (Agent Builder) surfaces the three-way conflict and recommends "route to neutral review" — but a
   machine shouldn't settle a tri-party fiduciary conflict alone, so the case **stops at an Action
   Center HITL gate.** A human rules; the ruling is recorded with *who / why / when* and **read
   downstream** to set the litigation posture. *Both Approve and Deny advance — the decision is data,
   not a rewind.*

6. **Reversal 5 (Day 90) → Litigation Defense + return-to-origin.** ClearFlow is named a
   co-defendant. The **Negligent Monitoring Risk** agent (Agent Builder) assesses exposure. Because
   new evidence reopens the question of who-knew-what, the case takes the **`return-to-origin` exit
   back to Multi-Customer Investigation** (interrupting entry `=js:vars.var_reversal_number >= 5`),
   re-running *only* the cross-provider correlation while settled work is skipped (`shouldRunOnlyOnce`).
   This is the dashed arc at the top of the diagram — the thing a linear process can't do.

7. **Closed.** Every obligation is discharged and every stakeholder resolved, so the master closes. On
   closure the **Audit Ledger Writer** (Coded · **LangGraph**) fires **in-case**, takes `case_ref`
   from `metadata.ExternalId` (the readable `CFCS-…` id), and writes **6 immutable, idempotent
   `AuditRecord` rows** to **Data Fabric** — the survey-grade compliance ledger, surfaced live on the
   Coded Web App's **Compliance Ledger** panel. **All 13 instances: Completed.**

Throughout, every LLM call passed through the **LLM Gateway + Trust Layer** (PHI/PII guardrails);
structured data came from **Data Fabric** + **Context Grounding**; external parties were **Integration
Service API Workflows**; and each stakeholder case could invoke UiPath's **ViVE healthcare agents** via
the vertical bridge.

---

## A guided tour of the picture (what each panel is)

### Section ① — Orchestration (the Maestro Case canvas)
- **The master pipeline** = `clearflow-master-crisis` and its **seven stages**: Initial Response →
  Multi-Customer Investigation → Vector Isolation → Regulatory Response → Fiduciary Review →
  Litigation Defense → Closed. Arrows are **stage exits**; the case advances itself via exit
  conditions, not clicks.
- **The R1–R5 pills** = the **five reversals** (the scripted goal changes above).
- **The dashed arc** = the **`return-to-origin` exit** that re-opens Multi-Customer Investigation at R5.
- **The agent chips under each stage** = agents wired as **`type:"agent"` tasks** (named per stage in
  the flow story above). Caption: **12 agents = 6 Agent Builder (Claude Sonnet 4.6 BYO-LLM) + 6 Coded
  (Python SDK), 2 LangGraph `StateGraph`s** (⚡) via `uipath-langchain`.
- **The nested cards** = the 3-level hierarchy via the native **`case-management` task**:
  `clearflow-stakeholder-parent` ×6 (stages: Stakeholder Onboarding → Impact Assessment → Obligation
  Determination → Resolved) and `clearflow-obligation-grandchild` ×6 (Obligation Intake → Response →
  Discharged). The **"13 live case instances"** callout is the fan-out total.
- **The two gold pills** = **Action Center HITL gates** (Fiduciary Review ruling; grandchild
  file/withdraw).
- **The amber bar** = **UiPath LLM Gateway + Trust Layer** — PHI/PII guardrails on every LLM call.
- **The green "Closed" stage** = closure + the **Audit Ledger Writer** writing the `AuditRecord` ledger;
  **"✓ all instances Completed."**

### Section ② — Data, Integration & Surfaces (the foundation)
- **Data Fabric** — 9 entities, 4,320 telemetry rows (structured source-of-truth seed).
- **Context Grounding** — 2 indexes; the live `BAA-corpus` grounds the BAA Boundary Reasoner.
- **Integration Service** — **19 API Workflows** (CNCF Serverless): external-party mocks + 3 ViVE bridges.
- **Maestro BPMN × 2** (ideal-response playbook + closure) · **Maestro Flow** (demo driver).
- **Action Center** (2 HITL gate apps) · **Coded Web App** (dashboard + live **Compliance Ledger**).
- Right-hand headline: **13 UiPath product surfaces · 38 runtime artifacts.**

### The Vertical bridge
Each `clearflow-stakeholder-parent` invokes the **UiPath ViVE-2026** solutions (Medical Records
Summarization · Claim Denial Prevention · Prior Authorization). In the demo these are API-workflow
mocks; swapping in the live solutions is a connector change.

### The footer
**"Built end-to-end with Claude Code"** (38 artifacts · 768 offline tests, test-first) + the legend.

---

## The legend (color key), in UiPath terms

| Color | Element |
|---|---|
| **Orange** | Maestro Case stage (a stage in a `caseplan.json`) |
| **Violet** | Agent Builder agent (low-code, Claude Sonnet 4.6 BYO-LLM) |
| **Cyan** | Coded Agent (Python SDK); ⚡ = LangGraph `StateGraph` via `uipath-langchain` |
| **Green** | Platform service (a first-party UiPath capability) |
| **Gold** | Human gate (Action Center HITL task — the case waits) |

## The numbers, and what each one means

| Number | Meaning |
|---|---|
| **3 case levels** | Native `case-management` nesting: master → stakeholder-parent → obligation-grandchild. |
| **5 reversals** | Five scripted goal changes (R1–R5), incl. a `return-to-origin` re-entry. |
| **12 agents** | 6 Agent Builder + 6 Coded; 2 are LangGraph `StateGraph`s. |
| **13 live instances** | 1 master + 6 parents + 6 grandchildren at fan-out. |
| **2 HITL gates** | Action Center tasks: the fiduciary ruling + the obligation file/withdraw. |
| **13 product surfaces** | 13 distinct UiPath products composed together. |
| **38 artifacts** | 38 runtime artifacts in the `clearflow-solution` `.uipx`. |
| **768 tests** | Offline structure/contract tests, authored test-first (TDD). |

---

## Say it out loud (a ~60-second script)

> "This is one UiPath Maestro Case — `clearflow-master-crisis` — orchestrating a healthcare-payment
> crisis end to end, and the Maestro Case canvas *is* the orchestrator; there's no external harness.
> The master walks itself through seven stages, and these R1-to-R5 pills are five reversals that
> change the goal. On Day 1 the Claim Flow Anomaly Detector flags a provider going dark; the
> Multi-Customer Pattern Detector correlates it across the network; the Forensic Self-Exam agent — a
> LangGraph agent — clears ClearFlow's own infrastructure.
>
> Then the hero moment: at Reversal 3 a regulator subpoena makes the master spawn six
> stakeholder-parent cases at once via the native case-management task, each spawning an obligation
> grandchild — thirteen live instances, three levels deep — and the BAA Boundary Reasoner grounds
> each provider's lawful answer in its own agreement via Context Grounding. At Reversal 4 the case
> stops at an Action Center human gate for a tri-party fiduciary ruling that's read downstream. At
> Reversal 5 it takes a return-to-origin exit back to re-investigate.
>
> Every LLM call goes through the LLM Gateway and Trust Layer. When the case closes, the Audit Ledger
> Writer — the second LangGraph agent — writes six immutable AuditRecord rows to Data Fabric, shown
> live on the Compliance Ledger. Thirteen UiPath surfaces, thirty-eight artifacts, all built with
> Claude Code."

---

## Glossary (the jargon used above)

- **Maestro Case** — UiPath's long-running case-management runtime; here, three `caseplan.json` files
  (V20) wired by the native `case-management` task. The case canvas is the orchestrator.
- **`type:"agent"` task** — a Maestro Case stage task that invokes an agent; how agents plug into stages.
- **`case-management` task** — the native task type that lets one case spawn another → the 3-level
  nesting and the Reversal-3 fan-out, with no external spawner.
- **Agent Builder agent** — a low-code UiPath agent (Claude Sonnet 4.6 via BYO-LLM through the LLM Gateway).
- **Coded Agent** — a Python-SDK agent; two of ours are **LangGraph `StateGraph`** agents deployed via
  **`uipath-langchain`**.
- **LLM Gateway + Trust Layer** — the single path every LLM call takes; the Trust Layer applies
  PHI/PII guardrails uniformly.
- **Data Fabric** — UiPath's structured-data store; also where the `AuditRecord` ledger entity lives.
- **Context Grounding** — retrieval over indexed corpora (e.g. `BAA-corpus`) so agents cite source text.
- **Action Center / HITL gate** — where a human-in-the-loop task pauses the case for an approval/ruling.
- **Integration Service API Workflow** — a CNCF-Serverless workflow standing in for an external party
  (or bridging a ViVE solution).
- **Reversal** — a scripted event (R1–R5) that changes the master goal and re-routes the case.
- **`return-to-origin` exit** — a Maestro Case exit type that re-enters an earlier stage (used at R5).
- **AuditRecord** — the immutable Data Fabric entity the Audit Ledger Writer populates at Closed.
- **BAA** — Business Associate Agreement; the health-data contract the BAA Boundary Reasoner grounds in.
- **ViVE-2026 solutions** — UiPath's healthcare agents (Medical Records Summarization, Claim Denial
  Prevention, Prior Authorization) each stakeholder case invokes via the vertical bridge.

---

*Source of truth for the narrative: [`STORY.md`](STORY.md). The diagram is a schematic — not
live-tenant footage.*
