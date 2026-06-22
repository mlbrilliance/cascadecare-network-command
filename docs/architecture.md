# CascadeCare Network Command — Technical Architecture

## Architecture in One Sentence

**UiPath Maestro Case IS the runtime.** Three nested `caseplan.json` files (master → stakeholder-parent → obligation-grandchild) wired via the native `case-management` task type manage the entire crisis lifecycle. Every agent, workflow, HITL gate, and data store is a UiPath asset.

---

## System Layers

> **Status (2026-06):** every layer below is **built and live** on UiPath Automation Cloud
> (`clearflow-solution` 1.0.35, full cascade proven end-to-end). The polished current architecture
> diagram is [`docs/images/architecture.svg`](images/architecture.svg) (embedded in the README); the
> ASCII views here are the engineering reference. Any remaining "(planned — Slice NNN)" markers below
> are historical build annotations, not current gaps.

```
+------------------------------------------------------------------+
|                    DEMO DRIVER LAYER                              |
|  Maestro Flow: clearflow-demo-driver                             |
|  7 scheduled steps → API Workflow calls at compressed intervals  |
+------------------------------------------------------------------+
|                    ORCHESTRATION LAYER                            |
|  Maestro Case (3-level: master / stakeholder-parent /            |
|    obligation-grandchild, native case-management task type)      |
|  Maestro BPMN: clearflow-ideal-incident-response                 |
|    (happy path → gateway → Maestro Case spawn at R1)             |
+------------------------------------------------------------------+
|                    INTELLIGENCE LAYER                             |
|  UiPath Agent Builder × 6  (Claude BYO-LLM via LLM Gateway)    |
|  UiPath Coded Agents × 6  (Python SDK, UiPath first-party LLM)  |
|  UiPath Trust Layer  (PHI/PII detection on every LLM call)       |
+------------------------------------------------------------------+
|                    DATA LAYER                                     |
|  UiPath Data Fabric  (Provider, Payer, Vendor, Regulator,        |
|    Insurer, Counsel, BAA, ClaimTelemetry, RegulatorTemplate)     |
|  UiPath Context Grounding  (BAA corpus + ClaimTelemetry corpus)  |
+------------------------------------------------------------------+
|                    MOCK EXTERNAL SYSTEMS                          |
|  Integration Service API Workflows × 19                          |
|  (one per: Northstar, Alpha-Epsilon, Apex, SummitBlue,           |
|   Union Prairie, Lakeshore, Nimbus, TN DOI, Aurora, Hawthorne)   |
+------------------------------------------------------------------+
|                    HUMAN-IN-THE-LOOP LAYER                        |
|  UiPath Action Center  (HITL approval gates)                     |
|  UiPath Apps: clearflow-network-command  (narrative dashboard)   |
+------------------------------------------------------------------+
```

---

## Maestro Case: Three-Level Nesting

```
clearflow-master-crisis (master case) — 7 stages:
  Initial Response → Multi-Customer Investigation → Vector Isolation →
  Regulatory Response → Fiduciary Review → Litigation Defense → Closed
       └─ at Regulatory Response: 6× [case-management task] → clearflow-stakeholder-parent (one per provider)
            stages: Stakeholder Onboarding → Impact Assessment → Obligation Determination → Stakeholder Resolved
                 └─ [case-management task] → clearflow-obligation-grandchild (×6)
                      stages: Obligation Intake → Obligation Response → Obligation Discharged
```

### Case Definitions

| File | Role | Status |
|---|---|---|
| `maestro_case/clearflow-master-crisis/content/caseplan.json` | Master crisis case — governs the full 90-day cascade | Active (V20.0.0) |
| `maestro_case/clearflow-stakeholder-parent/content/caseplan.json` | Stakeholder parent case — one instance per provider/payer/vendor | Slice 010 |
| `maestro_case/clearflow-obligation-grandchild/content/caseplan.json` | Obligation grandchild — per-BAA, per-regulator sub-cases | Slice 010 |

The three caseplan.json files are wired via the native V20 `case-management` task type. No external orchestrator, no relational mirror.

### Canvas Engineering for Reversal 3 (Hero Moment) (planned — Slice 010)

The master case's "Regulatory Response" stage will contain six `case-management` task tiles (`width: 304, height: 128`) positioned in a horizontal fan at calculated `{x, y}` offsets (engineered in Slice 010). When the TN DOI subpoena event fires, all six stakeholder-parent cases spawn simultaneously. The camera holds on this canvas for 8–10 seconds — the three-level hierarchy lands in a single frame.

---

## Maestro BPMN (planned — Slice 011)

`maestro_bpmn/clearflow-ideal-incident-response/process.bpmn` (planned — Slice 011)

Models the textbook cyber-incident response playbook:

```
Intake → Triage → Contain → Notify → Close
              ↓
          Gateway: is_cascade?
              ↓ YES
          [Maestro Case spawn: clearflow-master-crisis]
```

Role in demo: cold-open cut (0–20s). Shows the expected happy path. When Reversal 1 fires, the gateway diverges into the master case. Story: "BPMN is the playbook. Maestro Case is what happens when reality breaks it."

---

## Agents (planned — Agent Builder agents Slice 008, Coded Agents Slice 009)

> **Current count: 6 Agent Builder + 6 Coded.** The tables below are the original design (4 + 3).
> The shipped system adds `assess-claim-disruption` + `classify-obligation` (Agent Builder) and
> `forensic-self-exam-agent-langgraph` (a **LangGraph `StateGraph`**, LIVE) + `case-job-janitor`
> + `audit-ledger-writer-langgraph` (a second **LangGraph `StateGraph`** coded Agent, wired into the
> master caseplan's **Closed stage** (task `tALWdgr01`) — it fires **in-case, live during the run**,
> receives `case_ref` from `metadata.caseId`, and writes immutable, idempotent `AuditRecord` ledger
> rows to Data Fabric — 6 rows per run, idempotent on duplicate fire) (Coded). The README "Agent
> inventory" table is the authoritative current list.

### Agent Builder (original design: 4 agents — UiPath Agent Builder, low-code LLM + tools)

| Agent | Trigger | LLM | Context source |
|---|---|---|---|
| Vector Hypothesis Agent | Multi-Customer Pattern Detector output | Claude BYO-LLM | Context Grounding: ClaimTelemetry corpus |
| BAA Boundary Reasoner | TN DOI subpoena event | Claude BYO-LLM | Context Grounding: BAA corpus |
| Fiduciary Conflict Detector | Competing payer + provider demands | Claude BYO-LLM | Data Fabric: BAA + payer policy entities |
| Negligent Monitoring Risk Agent | ClearFlow named co-defendant | Claude BYO-LLM | Context Grounding: full case evidence |

All system prompts: `agents/prompts/<agent-name>.md`

### Coded Agents (3 agents — Python SDK, published to Studio Web) (planned — Slice 009)

| Agent | Trigger | LLM | Logic |
|---|---|---|---|
| Claim Flow Anomaly Detector | Demo Driver t+10s | UiPath first-party | Telemetry threshold + z-score |
| Multi-Customer Pattern Detector | 2+ anomalies active | UiPath first-party | Cross-provider correlation, likelihood test |
| Forensic Self-Exam Agent | Master case "Classification" stage | UiPath first-party | Infrastructure review routing |

### LLM Routing

All LLM calls flow through the **UiPath LLM Gateway** → **Trust Layer** (PHI/PII detection + content filtering). Two pools:

- **UiPath first-party LLM** — Coded Agents (high-volume, classification + summarization)
- **Claude via BYO-LLM** — Agent Builder agents (heavy reasoning, registered via `uip llm-configuration byo-connections`)

---

## Integration Service API Workflows (~13 Mock External Systems) (planned — Slice 006)

Each workflow reads from Data Fabric, shapes a payload, and emits an event consumed by Maestro Triggers on the master case.

| Workflow | External system |
|---|---|
| `api_workflows/provider-northstar/` | Northstar Regional Health |
| `api_workflows/provider-alpha/` | Provider Alpha |
| `api_workflows/provider-beta/` | Provider Beta |
| `api_workflows/provider-gamma/` | Provider Gamma |
| `api_workflows/provider-delta/` | Provider Delta |
| `api_workflows/provider-epsilon/` | Provider Epsilon |
| `api_workflows/payer-apex/` | Apex Health Plan |
| `api_workflows/payer-summitblue/` | SummitBlue Medicare Advantage |
| `api_workflows/payer-union-prairie/` | Union Prairie Benefits |
| `api_workflows/payer-lakeshore/` | Lakeshore TPA Services |
| `api_workflows/vendor-nimbus/` | Nimbus Patient Engagement Platform |
| `api_workflows/regulator-tn-doi/` | TN Department of Insurance |
| `api_workflows/insurer-aurora/` | Aurora Specialty (cyber insurer) |

---

## Data Fabric Entities (Slice 019)

Seeded by `scripts/seed_data_fabric.sh` (Slice 019) using `uip df` and
`uip context-grounding` CLI commands. Run `bash scripts/seed_data_fabric.sh --emit-json`
to inspect the full seed offline; `UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply`
to apply to a tenant.

| Entity | Contents |
|---|---|
| `Provider` | 6 records (Northstar + Alpha–Epsilon): org profile, CPN volume, BAA reference |
| `Payer` | 4 records (Apex, SummitBlue, Union Prairie, Lakeshore): contract terms, visibility rights |
| `Vendor` | Nimbus: SaaS profile, customer list, panic-state toggle |
| `Regulator` | TN DOI (additional regulators are future polish): jurisdiction, notification rules |
| `Insurer` | Aurora Specialty: coverage limits, sub-limit triggers, dispute flags |
| `Counsel` | Hawthorne Mercer LLP: engagement scope, privilege flags |
| `BAA` | 6 records (one per provider): heterogeneous terms, disclosure conditions, NDA clauses |
| `ClaimTelemetry` | Synthetic time-series: 90-day claim volume by provider, anomaly markers |
| `RegulatorTemplate` | Jurisdiction-specific notification templates |

### Context Grounding Indexes

| Index | Source entities | Used by |
|---|---|---|
| `BAA-corpus` | BAA entities (full text) | BAA Boundary Reasoner |
| `ClaimTelemetry-corpus` | ClaimTelemetry time-series | Vector Hypothesis Agent, Pattern Detector |

---

## Trust Layer

Policy applied uniformly on every LLM Gateway call (both first-party and BYO-LLM):

- **PHI/PII detection**: blocks or redacts any output containing patient identifiers, SSNs, claim numbers matching real NPI formats
- **Content filtering**: healthcare-sensitive output guardrails
- **Audit log**: every LLM call logged with input hash + policy outcome

Demo narrative: "PHI never leaves the UiPath governance boundary."

---

## Demo Driver: Event → Case Cascade Chain (planned — Maestro Flow Slice 012/013)

```
Maestro Flow: clearflow-demo-driver
  └─ Step 1 (t+10s)   → API Workflow: provider-northstar  → Maestro Trigger → Claim Anomaly Detector
  └─ Step 2 (t+25s)   → API Workflow: provider-alpha      → Maestro Trigger → Pattern Detector
  └─ Step 3 (t+45s)   → API Workflow: vendor-nimbus       → Maestro Trigger → Vector Hypothesis Agent
  └─ Step 4 (t+75s)   → API Workflow: regulator-tn-doi    → Maestro Trigger → BAA Boundary Reasoner
                                                                             → 6 grandchild cases (HERO)
  └─ Step 5 (t+120s)  → API Workflow: payer-apex          → Maestro Trigger → Fiduciary Conflict Detector
  └─ Step 6 (t+165s)  → API Workflow: insurer-aurora      → Maestro Trigger → Action Center HITL task
  └─ Step 7 (t+210s)  → API Workflow: regulator-tn-doi    → Maestro Trigger → Negligent Monitoring Risk Agent
```

Maestro Triggers on the master case filter incoming events and route them to the appropriate agent task or case-management spawn.

---

## HITL Gate (Reversal 4)

At t+165s (simulated Day 45), the Action Center receives a "TRI-PARTY APPROVAL" task:

- **Title**: Resolve Tri-Party Fiduciary Conflict — Apex / Northstar / ClearFlow
- **Priority**: Critical
- **Options**: Continue all controls | Pause crisis IDR objections | Settle high-value disputes | Route to neutral review
- **Agent recommendation**: Route to neutral review (from Fiduciary Conflict Detector)
- **Required approvers**: ClearFlow GC, COO, CISO

---

## Solution Packaging

```
maestro_case/clearflow-solution/
  clearflow-solution.uipx         # Solution descriptor (JSON)
  resources/                      # Shared resource files
  clearflow-master-crisis/        # Built by pack-solution.sh (copy from canonical)
  clearflow-stakeholder-parent/   # (planned — Slice 010) Built by pack-solution.sh
  clearflow-obligation-grandchild/ # (planned — Slice 010) Built by pack-solution.sh
```

**pack-solution.sh** is the ONLY way to update the solution package. It copies canonical `maestro_case/<name>/content/` files into the package before every `uip solution upload`. Never hand-edit the solution package.

---

## Build-Time Python Utilities (dev only, not in demo runtime)

| Module | Purpose |
|---|---|
| `src/cascadecare/uipath/auth.py` | OAuth2 client credentials helper for the `uip` CLI during development |
| `src/cascadecare/uipath/maestro_client.py` | Thin wrapper around `uip maestro case` CLI for build-time verification |

These modules are NOT invoked at demo runtime. The demo runs entirely within UiPath Automation Cloud.
