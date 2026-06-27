# Devpost "Project details" — CascadeCare Network Command (Track 1)

> **How to use this file:** each `## FIELD:` section below maps 1:1 to a box on the Devpost
> *Project details* form. Copy each block into the matching field. Items marked `[HUMAN]` still
> need you (a screenshot, a Labs-access confirm); `[VERIFY]` must be confirmed live before submit.
>
> **Honesty rules (keep intact):** no claim of runtime `qem:` Data Fabric fan-out (spawn inputs are
> literal provider slugs — proven 2026-06-10); the timeline is simulated; external parties are
> deterministic API-workflow mocks. Say only what runs.

---

## FIELD: Project title

```
CascadeCare Network Command — the living case layer for healthcare financial shockwaves
```

## FIELD: Elevator pitch / tagline (≤ 200 chars)

```
A UiPath Maestro Case command center that runs a multi-hospital cyber-payment crisis as one living, three-level case — 12 AI agents, 5 goal reversals, human gates, live on Automation Cloud.
```

---

## FIELD: Project Story — "About the project"

> Paste everything in this fenced region into the **Story** box (it supports Markdown).
> Devpost renders the headings; keep them.

<!-- ⬇️ BEGIN STORY — paste from here ⬇️ -->

## Inspiration

When a U.S. healthcare clearinghouse goes dark, hospitals stop getting paid within days — and
patient care is the next thing to break. The mid-2020s clearinghouse cyberattacks exposed the real
failure mode: the payment intermediary at the center has to answer the same regulator subpoena six
conflicting ways at once. Every affected hospital, payer, and regulator opens its own disconnected
workstream, and **nobody owns the whole picture.**

We realized a crisis like this isn't a workflow — it's a **case that keeps rewriting its own goal**,
and that UiPath **Maestro Case** is built to run exactly that. There was a second pull, too:
healthcare is UiPath's #1 vertical for 2026. At **ViVE 2026**, UiPath launched agentic healthcare
solutions — Medical Records Summarization, Claim Denial Prevention, Prior Authorization — each doing
one job, for one provider, in isolation. The missing piece was the **orchestrator that coordinates
those agents across a multi-stakeholder crisis.** That's CascadeCare.

## What it does

CascadeCare Network Command runs an entire multi-hospital cyber-payment crisis as **one evolving
Maestro Case**. **ClearFlow Health Network** (a fictional payment intermediary) serves six hospital
systems and four payers. When anomalous claim-flow drops hit several providers at once, the case has
to determine — under regulator, payer, and insurer pressure — whether ClearFlow is the **breach
vector, a bystander, or a co-victim**, while honoring conflicting BAA obligations to every customer.

- **Three levels of native case nesting** — master crisis → **6 stakeholder parent cases** → **6
  obligation grandchild cases**, wired with the native `case-management` task.
- **Five master-level goal reversals** reshape the response across a simulated 90-day timeline — the
  case **re-routes itself**, no human driving it stage to stage.
- **12 AI agents** plug into stages as `type:"agent"` tasks; **every LLM call routes through the
  UiPath LLM Gateway + Trust Layer** (PHI/PII guardrails).
- **Two human-in-the-loop gates** in Action Center — and the human's decision is **consumed
  downstream**, reshaping the litigation posture, not just logged.
- **Hero moment — Reversal 3 (Day 30):** a state DOI subpoena lands and the master case fans out
  **six stakeholder cases simultaneously** on the canvas, each spawning its grandchild — **13 live
  case instances, three levels deep, in one beat.**

| # | Day | The goal rewrites itself |
|---|-----|--------------------------|
| 1 | 1  | "Assist isolated customers" → "Is ClearFlow the vector?" — the Multi-Customer Pattern Detector correlates all 6 providers and finds one signature |
| 2 | 5  | ClearFlow cleared; vendor **Nimbus** identified — the Vector Hypothesis Agent flips the posture to visible bystander |
| 3 | 30 | **State DOI subpoena collision** — the master spawns 6 stakeholder cases at once (visible fan), each spawning an obligation grandchild: **13 live cases, 3 levels** |
| 4 | 45 | Payer demands collide with BAAs — the Fiduciary Conflict Detector fires a **tri-party human gate** in Action Center |
| 5 | 90 | Litigation cascade — bystander becomes co-defendant; the Negligent Monitoring Risk Agent reshuffles privilege and re-opens *only* the cross-provider correlation |

**Why it matters to UiPath's healthcare vertical:** the ViVE-2026 solutions do the work; **CascadeCare
is the Maestro Case layer that orchestrates them under fire.** Each stakeholder case can invoke the
medical-records, claim-denial, and prior-auth workflows for its provider. And the per-decision audit
trail + SLA-timeliness record it produces are the kind of **survey-grade evidence** accreditors (The
Joint Commission, NCQA, ACHC — HIPAA throughout) look for after a disruption. *CascadeCare produces
that evidence; it does not implement any accreditation standard.*

## How we built it

**Pure UiPath at runtime — the Maestro Case canvas IS the orchestrator** (not a Python harness).
Everything runs **live on UiPath Automation Cloud** (`clearflow-solution` **1.0.36**, folder
`Shared/CascadeCare-v110`); the full cascade is proven end-to-end — master + 6 children + 6
grandchildren all reach **Completed**. **13 UiPath product surfaces · 38 runtime artifacts.**

- **3 Maestro Cases (V20)** nested via the native `case-management` task.
- **6 Agent Builder agents** (Claude Sonnet 4.6 BYO-LLM through the LLM Gateway).
- **6 Coded Agents** (Python SDK) — **two are LangGraph `StateGraph` agents** via `uipath-langchain`:
  the **live forensic self-exam agent** (fires in-case at Vector Isolation) and the **in-case
  audit-ledger writer** (persists immutable, queryable `AuditRecord` rows to Data Fabric during the
  run — a survey-ready compliance ledger, idempotent on duplicate fire).
- **19 Integration Service API Workflows** (one mock front per external party + the 3 ViVE
  healthcare-solution bridges).
- **2 Maestro BPMN** + **1 Maestro Flow** (hybrid BPMN + Case pattern; demo driver).
- **1 UiPath App** dashboard (with a live **Compliance Ledger** reading the `AuditRecord` entity) +
  **2 Action Center HITL apps**.
- **9 Data Fabric entities** (4,320 telemetry rows) + **2 Context Grounding indexes** (live,
  retrieval-verified) generated from the same seed tables so structured data and retrieval never
  disagree.
- **Trust Layer** PHI/PII policy on every LLM call.

**Built by coding agents on UiPath** — the +2 bonus made literal. **Claude Code** (Anthropic's CLI)
was the **primary** coding agent and authored the bulk of the work — all 38 artifacts, **768 offline
test gates written test-first**, and 9 externalized agent prompts — driving the `uip` CLI and the
official `uipath-*` skills. **OpenAI Codex** assisted as a **secondary** coding agent (cross-review,
alternative generations, selected pieces). Two independent coding agents both working productively
against UiPath is the point this bonus rewards.

## Challenges we ran into

Five weeks on Maestro Case meant discovering a layer of **undocumented footguns**, and most of the
build was empirical diagnosis, not guesswork:

- **Cryptic, un-Googleable error codes** — `400300` (runtime `=datafabric.qem:` in spawn inputs
  faults), `160009` (deleting a HITL gate task *faults the case*) returned zero search hits.
- **Caseplan edits going silently inert** — the runtime executes the *compiled* `caseplan.json.bpmn`,
  which only the Studio Web canvas regenerates; a stale `.bpmn`, a canvas-dropped start event, or a
  stripped `=js:` expression makes edits do nothing.
- **Data Fabric insert traps** — underscore field names and a reserved `id` silently drop on insert;
  STRING fields cap at 200 chars.
- **Orchestrator Error 2005** — root-caused by packing an Api project offline and diffing the
  generated `package-descriptor.json` against the nupkg contents.
- **Spawn fan-out** — runtime `qem:` Data Fabric expressions aren't supported in `JobArguments`, so
  we fan out on literal stakeholder slugs (and filed product feedback).

We turned the hard-won knowledge into an open-source, **offline, credential-free** developer kit —
the **Maestro Case Kit** (`pipx install maestro-case-kit`, MIT): a `maestro-case` CLI, a
dependency-free MCP server, and agent skills, all over one shared tool registry. It includes an
`explain` knowledge oracle for those error codes, a static caseplan `lint`, a `check-spawn` guard for
the `qem:` trap, and a `check-cli` guard for a namespace bug we hit in UiPath's *own* skills repo
(since fixed upstream).

## Accomplishments that we're proud of

- **The full cascade runs live, end-to-end** — master auto-walks every agent stage, fans out 6 + 6,
  passes two human gates, and reaches Completed. Not slides.
- **Exception handling as a first-class feature** — four complementary layers, authored test-first.
- **An in-case LangGraph agent writing an immutable compliance ledger** to Data Fabric *during* the
  run — proving the agent layer is framework-agnostic under Maestro Case.
- **We shipped reusable open-source tooling** UiPath could dogfood — beyond the demo.
- **The whole thing was built by coding agents**, test-first, with a zero-tolerance IP-safety gate on
  every commit.

## What we learned

- **Maestro Case is a genuine orchestrator** — multi-level spawning, self-driving stage progression,
  and SLA escalation belong on the canvas, not in glue code.
- **The agent layer is framework-agnostic** — a LangGraph `StateGraph` deploys cleanly via
  `uipath-langchain` and runs in-case alongside low-code Agent Builder agents under one Trust Layer.
- **Crisis software is judged by failure paths** — the interesting engineering is what happens when
  the LLM Gateway drops, an input is empty, or a human acts out of turn.
- **TDD works even against an opaque platform** — an offline structure/contract test suite (768 gates)
  caught regressions a live tenant would have hidden.

## What's next

- **Swap the API-workflow mocks for the live ViVE healthcare solutions** — a connector change, not a
  redesign — so CascadeCare orchestrates UiPath's shipping agents directly.
- **Maestro Case Kit v2** — auth-requiring operators (gate actions, AppTask completion, reconcile).
- **Push our `qem:` spawn-fan-out product feedback** with UiPath toward a supported pattern.

## A note on honesty

The 90-day timeline is **simulated** (compressed to minutes by a demo driver); external parties are
**deterministic API-workflow mocks**; per-provider fan-out uses **literal provider slugs** because
runtime `qem:` Data Fabric expressions in spawn `JobArguments` aren't supported today. Everything
described above as "live" runs live on Automation Cloud.

<!-- ⬆️ END STORY — paste to here ⬆️ -->

---

## FIELD: Built with

> Devpost renders these as tags. Paste as a comma-separated list.

```
uipath, uipath-maestro, maestro-case, uipath-agent-builder, uipath-coded-agents, langgraph, uipath-langchain, python, typescript, fastapi, anthropic-claude, claude-sonnet-4.6, uipath-llm-gateway, ai-trust-layer, uipath-data-fabric, context-grounding, uipath-integration-service, uipath-action-center, uipath-apps, uipath-automation-cloud, uipath-studio-web, claude-code, openai-codex, pytest, mit-license
```

## FIELD: "Try it out" links

> One link per "add another link" row.

- **GitHub repo (MIT):** https://github.com/mlbrilliance/cascadecare-network-command
- **Live operator dashboard (Coded Web App):** https://hackathon26_042.staging.uipath.host/clearflow-network-command
- **Demo video (≤5 min, live run):** https://youtu.be/J2gMR2DrzAY
- **Live tenant for judges:** `staging.uipath.com/hackathon26_042/DefaultTenant`, folder `Shared/CascadeCare-v110` — UiPath Labs access `[HUMAN: confirm Labs request]`

## FIELD: Project Media — Image gallery

> JPG/PNG/GIF, ≤ 5 MB each, **3:2 ratio preferred**, up to 15. Upload in this order; the first image
> is the gallery cover. Ready-to-upload assets are in `docs/images/`.

1. `docs/images/thumbnail-submission.png` — **cover** (project hero card).
2. `docs/images/architecture.png` — architecture: 3 nested case levels, 12 agents, Trust Layer, foundation.
3. Master case canvas — all stages + the reversal path. `[HUMAN: screenshot]`
4. The Reversal-3 fan — 6 children spawning in the Case Instances view. `[HUMAN: screenshot]`
5. All-Completed cascade (master + 6 + 6) — the closure proof. `[HUMAN: screenshot]`
6. Action Center fiduciary gate — the tri-party HITL form. `[HUMAN: screenshot]`
7. OOTB Case App — timeline + SLA tiles + sections. `[VERIFY: 1.0.36 renders] [HUMAN: screenshot]`
8. Trust Layer / LLM Gateway policy view on an agent call. `[HUMAN: screenshot]`
9. Exception handling — the forensic agent surfacing `error_type`/`error_message` on a Gateway failure (still routed), or the Action History showing an `instance retry` recovery. `[HUMAN: screenshot]`
10. Live Compliance Ledger panel on the dashboard (the `AuditRecord` rows). `[HUMAN: screenshot]`

> Full shot list with captions + verification steps: [`SCREENSHOT-SHOTLIST.md`](SCREENSHOT-SHOTLIST.md).

## FIELD: Video demo link

> Embedded at the top of the project page.

```
https://youtu.be/J2gMR2DrzAY
```

---

## Supporting evidence (not a form field — for judges who dig in)

- **Coding-agent bonus:** [`CODING_AGENTS.md`](../../CODING_AGENTS.md) (full 38-artifact authorship
  table), [`CLAUDE_CODE_USAGE.md`](../../CLAUDE_CODE_USAGE.md), [`docs/coding-agents/`](../coding-agents/).
- **Open-source tooling:** [`tooling/maestro-case-kit/`](../../tooling/maestro-case-kit/) +
  [`CONTRIBUTE-BACK-PR.md`](CONTRIBUTE-BACK-PR.md).
- **Live-run procedure / deviations:** [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md),
  [`DEVIATIONS.md`](../../DEVIATIONS.md).
