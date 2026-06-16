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

All running live on UiPath Automation Cloud (`clearflow-solution` 1.0.32, folder
`Shared/CascadeCare-v110`); full cascade proven end-to-end — master + 6 children +
6 grandchildren all reach **Completed**. **13 UiPath product surfaces, 37 runtime artifacts.**

- **3 Maestro Cases** (V20): `clearflow-master-crisis` → `clearflow-stakeholder-parent` →
  `clearflow-obligation-grandchild`, nested via the native `case-management` task
- **6 Agent Builder agents** (**Claude Sonnet 4.6** BYO-LLM through UiPath LLM Gateway):
  vector-hypothesis-agent, baa-boundary-reasoner, fiduciary-conflict-detector,
  negligent-monitoring-risk-agent, assess-claim-disruption, classify-obligation
- **5 Coded Agents** (Python SDK): claim-flow-anomaly-detector, multi-customer-pattern-detector,
  **forensic-self-exam-agent-langgraph** (a **LangGraph `StateGraph`** deployed via
  `uipath-langchain` — the live forensic agent, proving the agent layer is framework-agnostic
  under Maestro Case), forensic-self-exam-agent (original, superseded), and case-job-janitor
  (ops — sweeps platform job-state drift hourly)
- **19 Integration Service API Workflows** — one mock front per external party (6 providers,
  4 payers, regulator, insurer, counsel, vendor, audit) + the 3 ViVE healthcare-solution bridges
- **2 Maestro BPMN** (ideal-response playbook that spawns the master case; closure
  notification) + **1 Maestro Flow** (demo driver) — hybrid BPMN + Case pattern
- **1 UiPath App** (ClearFlow Network Command dashboard) + 2 Action Center HITL apps
  (master fiduciary gate; grandchild file/withdraw gate)
- **9 Data Fabric entities** (providers, payers, BAAs, claim telemetry — 4,320 telemetry rows)
- **OOTB Case App** configured for all three case types (caseSummary + stakeholder/obligation
  sections) `[VERIFY: 1.0.24 deployed + renders]`
- **2 Context Grounding indexes, live + retrieval-verified** — `BAA-corpus` (6 synthetic
  full-text BAAs grounding the BAA Boundary Reasoner) and `ClaimTelemetry-corpus`; corpora are
  generated from the same seed tables as the Data Fabric records, so retrieval and structured
  data never disagree
- **Trust Layer** PHI/PII policies on every LLM call (all agents route through LLM Gateway)

## Hero demo moment

Reversal 3 (Day 30): a Tennessee DOI subpoena arrives mid-crisis. On one canvas, the master
case fans out **six stakeholder parent cases simultaneously** — each seeded with its provider
identity — and each parent spawns its per-obligation grandchild. Thirteen coordinated case
instances, three levels deep, every one driven to Completed.

## Exception, failure & edge-case handling

Crisis software is judged by what it does when things break — and most demos only show the happy
path. CascadeCare handles failure in four complementary layers:

1. **In-agent graceful degradation.** When the LLM Gateway fails (520 / auth / offline), the
   LangGraph forensic agent catches it, surfaces `error_type` / `error_message` as case variables,
   and **still returns the correct route** — routing is deterministic, so the agent never faults and
   the case keeps moving. Authored test-first (a failing test proved the error was being swallowed
   before the fix landed).
2. **Structured coded-agent errors.** Coded Agents return `error_type` / `error_message` in their
   Output contract and never raise — a failure becomes data, not a crashed job.
3. **Case-native resilience.** Case + stage SLA rules fire escalation notifications (on-track /
   at-risk / breached) across all three nesting levels; a `return-to-origin` exit re-opens *only*
   the Multi-Customer Investigation stage at Reversal 5, re-running the cross-provider correlation
   while skipping settled work.
4. **Operator recovery + audit.** A faulted instance is recovered with `uip maestro case instance
   retry`; the Action History records the incident and the retry as a timestamped, compliance-grade
   audit trail.

**Edge cases handled by design:** negative/empty agent inputs are clamped and routed to escalate
rather than mis-routing; the no-signal path skips the LLM call entirely; spawn fan-out uses literal
stakeholder slugs (runtime `qem:` expressions fail `400300` in spawn inputs — a real platform edge
case we avoided); an unauthorized HITL action is recorded as a `User` incident rather than silently
lost.

**Meaningful human oversight:** at the Reversal-4 fiduciary gate the human's Approve/Deny is
recorded as an auditable ruling (who decided, why, when) **and consumed downstream** — the decision
reshapes ClearFlow's Reversal-5 litigation posture (cooperative vs. contesting). The human's choice
changes the response, not just the audit log.

## Built with coding agents (bonus)

**Claude Code** (Anthropic's CLI) authored 100% of this submission — **37 UiPath runtime
artifacts**, **680 offline test gates** (written test-first, before each artifact), and **9
externalized agent prompts** — driving the `uip` CLI and the official `uipath-*` authoring skills
under a test-gated spec-kit workflow. Diagnoses were empirical, not guessed (e.g. Orchestrator
Error 2005 root-caused by inspecting the offline-packed `package-descriptor.json`). The Criterion-3
exception handling above was authored test-first: a failing test proved the forensic agent was
silently swallowing an LLM-Gateway failure *before* the fix landed. One of the five Coded Agents is
a **LangGraph `StateGraph`** (via `uipath-langchain`) — a standalone specialist coded agent in its
own right.

Evidence: `CODING_AGENTS.md` (full 37-artifact authorship table), `CLAUDE_CODE_USAGE.md`,
`docs/coding-agents/` (per-type evidence pages + prompt logs + screenshots
`[HUMAN: capture during demo session]`).

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
- Executive dashboard (Coded Web App, live):
  `https://hackathon26_042.staging.uipath.host/clearflow-network-command`

## Screenshots to attach `[HUMAN]`

1. Master case canvas with all stages + reversal path
2. The Reversal-3 fan: 6 children spawning (Case Instances view)
3. Action Center fiduciary gate (tri-party HITL form)
4. OOTB Case App: timeline + SLA tiles + sections `[VERIFY: 1.0.32]`
5. Trust Layer / LLM Gateway policy view on an agent call
6. All-Completed cascade (master + 6 + 6) — the closure proof
7. Exception handling (Criterion 3): the forensic agent surfacing `error_type`/`error_message` on a Gateway failure (still routed), and/or the Action History showing an `instance retry` recovery
