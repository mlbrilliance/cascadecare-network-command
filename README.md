# CascadeCare Network Command

**The living case layer for healthcare financial shockwaves.**

A UiPath **Maestro Case** demonstration built for **UiPath AgentHack 2026 — Track 1**. Everything
runs on UiPath Automation Cloud; Python exists only as build-time tooling.

## What This Is

When a provider goes dark, the payment network feels it first. CascadeCare Network Command shows
how **ClearFlow Health Network** — a fictional US healthcare payment intermediary — manages a
multi-customer cyber cascade as **one evolving Maestro Case**. A master crisis case spawns
per-stakeholder parent cases, which in turn spawn per-obligation grandchild cases — **three levels
of native case nesting** — while five master-level goal reversals reshape the response across a
90-day simulated timeline.

The hero moment: **Reversal 3** (a state DOI subpoena) fans out **six grandchild cases
simultaneously** on the Maestro Case canvas.

> **Status (2026-06-12):** Every UiPath artifact below is authored, validated against its UiPath
> contract (V20 / CNCF Serverless 1.0.0 / Agent Builder), and **running live on UiPath Automation
> Cloud** — `clearflow-solution` 1.0.23 deployed to `Shared/CascadeCare-v110`, with a full
> cascade run proven end-to-end (master + 6 child + 6 grandchild cases all Completed). Live run
> procedure: [`docs/DEMO-RUNBOOK.md`](docs/DEMO-RUNBOOK.md). Historical deviations:
> [`DEVIATIONS.md`](DEVIATIONS.md).

## Why This Matters — Healthcare Is UiPath's 2026 Vertical

Healthcare is UiPath's **#1 vertical push for 2026**. At **ViVE 2026**, UiPath launched its
agentic healthcare solutions — **Medical Records Summarization**, **Claim Denial Prevention**,
and **Prior Authorization**. Those agents do the work; **CascadeCare is the Maestro Case layer
that orchestrates them under fire.** When a payment-network crisis hits, CascadeCare coordinates
the medical-records, claim-denial, and prior-auth agents across a multi-stakeholder cascade
instead of leaving them to run in isolation — the **vertical bridge** built in slice **S024**.
That makes CascadeCare immediately **adoptable by the health vertical**: it is the crisis
orchestrator for the agents UiPath already ships.

The scenario is dead-on the threat that vertical exists to survive. CascadeCare's fictional
**ClearFlow Health Network** cascade is modeled on the real class of U.S. healthcare
clearinghouse / payment-network cyberattacks of the mid-2020s — incidents that left vast numbers
of providers unable to get paid and drove billions of dollars in downstream cost, among the most
consequential healthcare cyber events on record. CascadeCare demonstrates how an AI-driven
Maestro Case would manage exactly that, end to end.

## Demo: Five Reversals

| # | Name | Day | Master goal shift |
|---|---|-----|-------------------|
| 1 | Multi-customer correlation | 1 | "Assist isolated customers" → "Determine if ClearFlow is the vector" |
| 2 | ClearFlow cleared, Nimbus identified | 5 | "Am I the cause?" → "Visible bystander with a posture decision" |
| 3 | State DOI subpoena collision | 30 | Three-level nesting goes live — **6 grandchild cases spawn** |
| 4 | Payer demands vs. BAAs | 45 | Fiduciary Conflict Detector fires; tri-party HITL gate |
| 5 | Litigation cascade | 90 | Bystander → co-defendant; privilege reshuffles |

## UiPath Component Inventory

Every runtime asset is a UiPath artifact. **27 core artifacts** plus the Data Fabric, Context
Grounding, and Trust Layer surfaces below.

### Maestro Case — three-level nesting (3 case definitions, V20)

| Case definition | Level | Role |
|-----------------|-------|------|
| `clearflow-master-crisis` | Master | The crisis spine; drives the five reversals and spawns stakeholder parents |
| `clearflow-stakeholder-parent` | Parent | One per provider / payer / vendor stakeholder; spawns obligation grandchildren |
| `clearflow-obligation-grandchild` | Grandchild | Per-BAA / per-regulator / per-investigation obligation |

Wired with the native `case-management` task type — no Postgres mirror, no level-flag superset.

**Canonical case surfaces** — the Maestro Case patterns Devpost judges are trained to recognize, built into the caseplans:

- **SLA + escalation → Maestro Notification**, at case and stage level across all three nesting levels — on-track / at-risk / breached, firing notification actions on breach and at-risk.
- **Agent-driven progression** — the master advances itself: the Forensic Self-Exam agent's output drives the Vector Isolation → Regulatory Response exit when ClearFlow's vector status clears (`=js:vars.var_clearflow_vector_status === 'cleared'`).
- **Targeted re-entry** — at Reversal 5 (ClearFlow → co-defendant), the master re-opens the Multi-Customer Investigation stage via an interrupting entry condition (`=js:vars.var_reversal_number >= 5`) and a `return-to-origin` exit, re-running **only** the cross-provider correlation while the settled anomaly classification is skipped (`shouldRunOnlyOnce`).
- **Agent Evaluations** — eval sets for all seven agents (low-code under `agents/<name>/evals/`, coded under `agents/<name>/evaluations/`).

Per-agent Agent Memory is a deploy-time toggle, not fabricated offline config; cross-timeline state is carried by the master's root variables + Data Fabric (see `docs/adr/0004-agent-memory-is-deploy-time-not-fabricated-config.md`).

### Agent Builder agents (6, low-code, Claude BYO-LLM)

| Agent | Role |
|-------|------|
| `vector-hypothesis-agent` | Determines the attack vector (ClearFlow vs. Nimbus) |
| `baa-boundary-reasoner` | Analyzes BAA terms (+ Context Grounding on `BAA-corpus`); finds cross-BAA conflicts |
| `fiduciary-conflict-detector` | Multi-party obligation conflicts; builds the HITL form payload (Reversal 4) |
| `negligent-monitoring-risk-agent` | Co-defendant exposure analysis (Reversal 5) |
| `assess-claim-disruption` | Quantifies per-stakeholder claim disruption and liquidity impact (parent Impact Assessment) |
| `classify-obligation` | Classifies the raised obligation (subpoena / breach-notification / BAA-disclosure / audit) for the grandchild intake |

### Coded Agents (4, Python SDK)

| Agent | Role |
|-------|------|
| `claim-flow-anomaly-detector` | Classifies an anomaly score on claim telemetry |
| `multi-customer-pattern-detector` | Cross-provider correlation; emits the cascade signal |
| `forensic-self-exam-agent` | Coordinates the other agents; routing |
| `case-job-janitor` | Ops utility on an hourly time trigger: sweeps zombie "Running" Orchestrator job rows left behind by completed case instances (the platform never flips them to Successful) |

### Integration Service API Workflows (19, `Type:"Api"`)

**Source-system mocks (14)** — `counsel-hawthorne`, `insurer-aurora-specialty`, `payer-apex`,
`payer-lakeshore`, `payer-summitblue`, `payer-union-prairie`, `provider-alpha`, `provider-beta`,
`provider-delta`, `provider-epsilon`, `provider-gamma`, `provider-northstar`, `regulator-tn-doi`,
`vendor-nimbus`.

**Case utilities (2)** — `register-stakeholder` (parent-case onboarding: registers the stakeholder
and pulls its BAA) and `generate-audit-record` (writes a per-action audit record).

**UiPath Healthcare Agentic Solutions (3)** — the *vertical bridge*: CascadeCare orchestrates
UiPath's own ViVE-2026 Healthcare Solutions as case-invoked tasks inside the stakeholder-parent's
Impact Assessment stage — `solution-medical-records-summarization` (Medical Records Summarization),
`solution-claim-denial-prevention` (Claim Denial Prevention & Resolution), and
`solution-prior-auth-continuity` (Prior Authorization).

### Maestro BPMN (2) and Maestro Flow (1)

| Artifact | Type | Role |
|----------|------|------|
| `clearflow-ideal-incident-response` | Maestro BPMN | The ideal-response playbook (hybrid BPMN + Case) |
| `case-closed-notification` | Maestro BPMN | Sends the case-closure notification when a case completes |
| `clearflow-demo-driver` | Maestro Flow | The Demo Driver that paces the 90-day timeline to wall-clock |

### UiPath Apps (1)

| App | Role |
|-----|------|
| `clearflow-network-command` | Narrative dashboard: cascade tree, reversal timeline, agent activity, HITL overrides |

### Data Fabric entities (9)

`Provider`, `Payer`, `Vendor`, `Regulator`, `Insurer`, `Counsel`, `BAA`, `ClaimTelemetry`,
`RegulatorTemplate` — schemas specified in
[`specs/003-uipath-native/data-model.md`](specs/003-uipath-native/data-model.md).

### Context Grounding indexes (2, live + retrieval-verified)

`BAA-corpus` (synthetic BAA full text → BAA Boundary Reasoner's grounding context) and
`ClaimTelemetry-corpus` (per-provider 30-day claim-flow narratives). Both indexes are **live on
the tenant and ingestion-verified** (semantic search returns the right BAA for cross-provider
conflict questions). Source documents are committed under
[`data/context-grounding/`](data/context-grounding/) and generated deterministically from the
seed tables by [`scripts/gen_cg_corpus.py`](scripts/gen_cg_corpus.py), so retrieval answers
always agree with the structured Data Fabric records.

### Trust Layer policies (2 pools)

Every LLM call flows through the **UiPath LLM Gateway → Trust Layer**: a **PHI/PII** detection
pool (blocks/redacts patient identifiers, SSNs, NPI-format claim numbers) and a
**content filtering** pool (healthcare-sensitive output guardrails). Demo narrative: *PHI never
leaves the UiPath governance boundary.*

## Repo Map

```
cascade_command/
  maestro_case/         # 3 caseplan.json definitions + clearflow-solution/ (.uipx packaging)
  maestro_bpmn/         # clearflow-ideal-incident-response.bpmn + case-closed-notification.bpmn
  maestro_flow/         # clearflow-demo-driver.flow (Demo Driver)
  agents/               # 6 Agent Builder (agent.json) + 4 Coded Agents (agent.py)
    prompts/            # 9 agent system prompts (Markdown — never inlined in Python)
  api_workflows/        # 19 Integration Service API Workflows
  apps/                 # clearflow-network-command UiPath App
  src/cascadecare/      # build-time Python wrappers (auth, maestro_client) — dev only
  tests/                # 470+ offline structure/contract gates
  specs/                # active spec: specs/003-uipath-native/
  scripts/              # pack-solution.sh, gen_api_entry_points.py (build-time)
  knowledge/            # immutable source-of-truth documents
  docs/                 # architecture, usage, changelog, coding-agent evidence, demo run-playbook
```

## Prerequisites

- **UiPath Automation Cloud** tenant with Maestro, Agent Builder, Integration Service, Data Fabric,
  Context Grounding, Trust Layer, Action Center, and Apps enabled.
- **Anthropic (Claude) BYO-LLM** registered in the UiPath LLM Gateway for the four low-code agents.
- **Python 3.12+ (LTS)** and [`uv`](https://docs.astral.sh/uv/) for the build-time tooling. (Python 3.13 available but 3.12 LTS recommended)
- The UiPath **`uip` CLI v1.1.0+** (installed via `uipath>=2.10.79` in project dependencies).

## Quickstart (build-time)

```bash
# Install the build tooling (no runtime Python service exists)
uv sync --extra dev

# Run the offline gate suite (470+ structure/contract tests)
uv run pytest

# Authenticate against the UiPath tenant
uv run python -m cascadecare.uipath.auth

# Pack the solution (.uipx) for Studio Web / Orchestrator publish
bash scripts/pack-solution.sh
```

> Data Fabric entity seeding is **specified** in
> [`data-model.md`](specs/003-uipath-native/data-model.md) but not yet scripted; seed records are
> authored directly in the tenant. Live publish and the end-to-end demo run are documented in
> [`docs/demo/run-playbook.md`](docs/demo/run-playbook.md).

## Built with Coding Agents

This entire repository — every UiPath artifact, test, spec, and build script — was authored by
**Claude Code** (Anthropic's CLI) driving the `uip` CLI and the official `uipath-*` authoring
skills, under a test-gated spec-kit workflow. The AgentHack coding-agent bonus evidence
((a) which tool, (b) how it contributed, (c) verifiable evidence) is consolidated in:

- [`CODING_AGENTS.md`](CODING_AGENTS.md) — canonical authorship table for all 27 artifacts.
- [`CLAUDE_CODE_USAGE.md`](CLAUDE_CODE_USAGE.md) — the Devpost bonus write-up.
- [`docs/coding-agents/`](docs/coding-agents/) — per-artifact-type evidence pages + prompt logs.

## Documentation

- [Architecture](docs/architecture.md)
- [Usage & Demo Storyboard](docs/usage-examples.md)
- [Demo Run Playbook](docs/demo/run-playbook.md)
- [Active Specification](specs/003-uipath-native/plan.md)
- [Deviations Log](DEVIATIONS.md)

## Demo Video

_Carried forward to final submission capture — a ≤5-minute video showing the solution running live
on UiPath Automation Cloud, hero moment (Reversal 3 subpoena fan-spawn) at ~2:30._

## IP Safety Notice

All company names, patient data, claim numbers, and regulatory citations are **fictional**. No real
healthcare organizations, patients, or legal proceedings are referenced. The `/audit-ip-safety`
command enforces a forbidden-token denylist before every commit.

## License

Licensed under the [MIT License](LICENSE).
