# Devpost Page Copy — CascadeCare Network Command (Track 1)

Draft for the human submitter. Paste-ready sections below; items marked `[HUMAN]` need a real
link/screenshot; items marked `[VERIFY]` must be confirmed live before submitting.
Honesty rules: no claim of runtime `qem:` Data Fabric fan-out (spawn inputs are literal provider
slugs — proven 2026-06-10); do not claim Context Grounding is wired unless `[VERIFY]` passes.

---

## Title

**CascadeCare Network Command — the living case layer for healthcare financial shockwaves**

## Elevator pitch (Devpost tagline, ≤200 chars)

A UiPath Maestro Case command center that manages a multi-hospital cyber-payment crisis as one
living, three-level case — 10 AI agents, 5 goal reversals, human gates, all on Automation Cloud.

## The business problem

When a healthcare clearinghouse goes dark, providers stop getting paid within days. The
mid-2020s U.S. clearinghouse cyberattacks showed the failure mode: every affected hospital,
payer, regulator, and insurer opens its own disconnected workstream, and the intermediary at the
center answers the same subpoena six conflicting ways.

**ClearFlow Health Network** (fictional) is that intermediary: its pricing engine and payment
network serve six hospital systems and four payers. When anomalous claim-flow drops hit several
providers at once, ClearFlow must work out — under regulator, payer, and insurer pressure —
whether it is the breach vector, a bystander, or a co-victim, while honoring conflicting BAA
obligations to every customer.

CascadeCare manages that entire cascade as **one evolving Maestro Case**: a master crisis case
spawns per-stakeholder parent cases, which spawn per-obligation grandchild cases — **three
levels of native case nesting** — while **five master-level goal reversals** reshape the
response across a simulated 90-day timeline.

## Why this matters to UiPath's healthcare vertical

UiPath's ViVE-2026 healthcare agentic solutions (Medical Records Summarization, Claim Denial
Prevention, Prior Authorization) do the work; **CascadeCare is the Maestro Case layer that
orchestrates them under fire.** Each stakeholder parent case invokes all three solution
workflows for its provider — the crisis orchestrator for the agents UiPath already ships.

## What it does (the five reversals)

| # | Day | Goal shift |
|---|-----|-----------|
| 1 | 1 | "Assist isolated customers" → "Determine if ClearFlow is the vector" — Multi-Customer Pattern Detector correlates 6 providers |
| 2 | 5 | ClearFlow cleared; vendor **Nimbus** identified — Vector Hypothesis Agent flips the posture to visible bystander |
| 3 | 30 | **State DOI subpoena collision** — the master spawns 6 stakeholder parent cases simultaneously (visible fan on the canvas), each of which spawns an obligation grandchild: 13 live cases, 3 levels |
| 4 | 45 | Payer demands collide with BAAs — Fiduciary Conflict Detector fires a **tri-party human gate** in Action Center |
| 5 | 90 | Litigation cascade — bystander becomes co-defendant; Negligent Monitoring Risk Agent reshuffles privilege |

## How we built it (UiPath component inventory)

All running live on UiPath Automation Cloud (`clearflow-solution` 1.0.23+, folder
`Shared/CascadeCare-v110`); full cascade proven end-to-end — master + 6 children +
6 grandchildren all reach **Completed**.

- **3 Maestro Cases** (V20): `clearflow-master-crisis` → `clearflow-stakeholder-parent` →
  `clearflow-obligation-grandchild`, nested via the native `case-management` task
- **6 Agent Builder agents** (Claude BYO-LLM through UiPath LLM Gateway):
  vector-hypothesis-agent, baa-boundary-reasoner, fiduciary-conflict-detector,
  negligent-monitoring-risk-agent, assess-claim-disruption, classify-obligation
- **4 Coded Agents** (Python SDK): claim-flow-anomaly-detector,
  multi-customer-pattern-detector, forensic-self-exam-agent, case-job-janitor
  (an ops agent that sweeps platform job-state drift hourly)
- **19 Integration Service API Workflows** — one mock front per external party (6 providers,
  4 payers, regulator, insurer, counsel, vendor, audit) + the 3 ViVE healthcare-solution bridges
- **2 Maestro BPMN** (ideal-response playbook that spawns the master case; closure
  notification) + **1 Maestro Flow** (demo driver) — hybrid BPMN + Case pattern
- **1 UiPath App** (ClearFlow Network Command dashboard) + 2 Action Center HITL apps
  (master fiduciary gate; grandchild file/withdraw gate)
- **9 Data Fabric entities** (providers, payers, BAAs, claim telemetry — 4,320 telemetry rows)
- **OOTB Case App** configured for all three case types (caseSummary + stakeholder/obligation
  sections) `[VERIFY: 1.0.24 deployed + renders]`
- **Trust Layer** PHI/PII policies on every LLM call (all agents route through LLM Gateway)
- Context Grounding indexes (BAA corpus, claim telemetry) `[VERIFY: live before claiming]`

## Hero demo moment

Reversal 3 (Day 30): a Tennessee DOI subpoena arrives mid-crisis. On one canvas, the master
case fans out **six stakeholder parent cases simultaneously** — each seeded with its provider
identity — and each parent spawns its per-obligation grandchild. Thirteen coordinated case
instances, three levels deep, every one driven to Completed.

## Built with coding agents (bonus)

Claude Code built this end-to-end: caseplan authoring, agent scaffolding, deploy tooling,
live-debug loops. Evidence: `CODING_AGENTS.md`, `CLAUDE_CODE_USAGE.md`,
`docs/coding-agents/` (prompt logs + screenshots `[HUMAN: capture during demo session]`).

## Honest limitations

- The crisis timeline is simulated (90 days compressed to minutes by a demo driver).
- External parties (providers, payers, regulator) are deterministic API-workflow mocks.
- Per-provider spawn fan-out uses literal provider slugs in spawn inputs (runtime `qem:`
  Data Fabric expressions in JobArguments are not supported by the platform today — we filed
  product feedback).

## Links

- GitHub (MIT): `[HUMAN: repo URL]`
- Demo video (≤5 min, live run): `[HUMAN: YouTube/Vimeo URL]`
- Live tenant for judges: `staging.uipath.com/hackathon26_042/DefaultTenant`,
  folder `Shared/CascadeCare-v110` (UiPath Labs access `[HUMAN: confirm Labs request]`)

## Screenshots to attach `[HUMAN]`

1. Master case canvas with all stages + reversal path
2. The Reversal-3 fan: 6 children spawning (Case Instances view)
3. Action Center fiduciary gate (tri-party HITL form)
4. OOTB Case App: timeline + SLA tiles + sections `[VERIFY: 1.0.24]`
5. Trust Layer / LLM Gateway policy view on an agent call
6. All-Completed cascade (master + 6 + 6) — the closure proof
