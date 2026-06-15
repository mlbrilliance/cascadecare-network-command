# Findings: Can Platform Units power `forensic-self-exam-agent-langgraph` as a Maestro Case `type:'agent'` task?

**Prepared for:** CascadeCare Network Command (AgentHack 2026, Track 1)
**Tenant:** UiPath Cloud `hackathon26_042` / DefaultTenant · Folder `Shared/CascadeCare-v110`
**Date:** 2026-06-14
**Method:** 4-agent parallel research (tavily / exa / ref / context7) → synthesis. Full raw agent reports + evidence in the workflow transcript.

---

## 1. Verdict

**YES — conditional.** Platform Units (PU) are the correct and sufficient consumable to power this agent, and the swap is architecturally supported. The hackathon tenant's **10K PU** pool (valid May 19 – Aug 11 2026) is the single budget drawn for both the coded-agent execution and its LLM Gateway call; **Heals (500) and ScreenPlay Runs (500) are never touched** by this agent.

- **Overall confidence: HIGH** that PU is the right budget and 10K is more than enough (all four research agents converge with primary UiPath licensing docs).
- **Confidence MEDIUM-HIGH** on the exact per-run PU figure: the metering *shape* depends on whether the `enrich` node's UiPath LLM Gateway call is billed as a **UiPath-hosted model** (~0.2 PU/call) or **BYOM/BYO-subscription** (flat 0.2 PU/execution, LLM call not separately metered). Both paths are cheap.

**Single most important caveat:** The blocker for the demo is **NOT the budget — it is the I/O contract swap.** The existing agent is **Type `Function (python)`** (named-argument `main` entry point); the replacement is **Type `Agent (python)`** (flat JSON payload validated against `entry-points.json`). Maestro strictly validates the agent's input schema — a key-name mismatch produces a live runtime error (`Input does not conform to schema / Agent.InputArgumentsSchema / Required properties [...] are not present`). The caseplan binding, resource reference, and input/output mapping must all be re-pointed and re-mapped, and the compiled `.bpmn` regenerated.

---

## 2. How consumption works (one agent run, including its LLM Gateway call)

A single run draws from **one pool only: Platform Units.** There is **no separate AI/LLM credit bucket** — the LLM Gateway (AI Trust Layer) is a governance/routing layer, not a billing silo.

| Cost component | What it is | PU drawn | Source |
|---|---|---|---|
| **Coded-agent execution** | One BYOA execution, Small machine (default), ≤5-min threshold | **0.2 PU** | docs.uipath.com/agents/.../coded-agents-licensing; licensing.uipath.com |
| **LLM Gateway call (UiPath-hosted Standard model)** | The single `enrich` UiPathChat call (Sonnet family = Standard tier), billed per LLM call in 64k input-token increments | **+0.2 PU** | docs.uipath.com/agents/.../licensing (Table 3) |
| **— OR — LLM Gateway call (BYOM/BYO-subscription)** | If the model routes as customer-managed | **+0 PU** (flat execution charge already counts it) | licensing.uipath.com |
| **Maestro orchestration of the agent task** | No documented additional charge for the `AI Agent (UiPath)` task wrapper beyond the agent run | **0 PU** (inferred) | metering-table absence |
| **Heals** | UI-automation self-healing only — agent makes no UI Automation calls | **0** | docs.uipath.com/agents/.../user-guide-ha/licensing |
| **ScreenPlay Runs** | Studio NL-driven UI automation — not used | **0** | docs.uipath.com/agents/.../user-guide-screenplay/licensing |

**Per-run total:** **~0.4 PU** (UiPath-hosted Standard model) or **~0.2 PU** (BYOM path, or any run that takes the graceful offline fallback and makes zero LLM calls).

> Model tier matters for the LLM-call slice — Basic (Haiku/Flash/4o-mini) = 0.16 PU/call; Standard (Sonnet 4.x, GPT-4o/4.1) = 0.2 PU/call; Premium (Opus) = 0.4 PU/call.

> **Separately metered (not part of this agent's per-run cost):** Maestro *case-instance* execution = **1 PU per process instance**; Context Grounding DeepRAG queries = 0.2 PU each.

---

## 3. Evidence table

| Claim | Source | Confidence |
|---|---|---|
| Platform Units are the single Unified-Pricing consumable (May 2025) consolidating AI/Robot/Agent Units; fully fungible single pool | docs.uipath.com/automation-cloud/.../release-notes/may-2025; licensing.uipath.com | High |
| Any agent execution (low-code AND coded) consumes Platform Units at run time; design-time Studio Web tests use LLM quota, not licensing units | docs.uipath.com/agents/.../user-guide/licensing | High |
| Coded Agents (BYOA), Small machine, ≤5-min = 0.2 PU per execution (multipliers: Standard ×2, Medium ×4, Large ×10) | docs.uipath.com/agents/.../coded-agents-licensing | High |
| UiPath-hosted Standard-model LLM call = 0.2 PU/call (Basic 0.16, Premium 0.4), billed per 64k input-token increment | docs.uipath.com/agents/.../licensing (Table 3) | High |
| BYOM/BYO-subscription path = flat 0.2 PU per agent execution; LLM call NOT separately metered | licensing.uipath.com | Medium-High |
| Agent execution consumes NO unattended-robot license (key difference vs Function-type, metered in Robot Units) | docs.uipath.com/agents/.../licensing; serverless FAQ | High |
| LLM Gateway / AI Trust Layer is a governance/routing layer, not a separate billing pool | docs.uipath.com/.../admin-guide/about-ai-trust-layer | High |
| Heals apply only to UI Automation failures; irrelevant to a Python/LangGraph coded agent (3 PU/heal when used) | docs.uipath.com/agents/.../user-guide-ha/licensing | High |
| ScreenPlay Runs are a Studio NL-UI-automation feature; not consumed by coded agents (0.20 PU/run when used) | docs.uipath.com/agents/.../user-guide-screenplay/licensing | High |
| Coded agents (PackageType=Agent) run on Automation Cloud Robots – Serverless, deployed as `.nupkg` Orchestrator processes; invokable from Maestro | docs.uipath.com/agents/.../about-coded-agents | High |
| Maestro "Start and wait for agent" invokes BOTH low-code and coded agents identically | docs.uipath.com/maestro/.../using-agents-in-maestro | High |
| Maestro sends inputs as flat JSON `{"key":"value"}`; agent must return matching JSON keys; schema strictly validated | docs.uipath.com/maestro/.../using-agents-in-maestro; forum.uipath.com/t/.../5708346 | High (doc) / Medium (forum) |
| `uipath init` generates `entry-points.json`, `bindings.json`, `agent.mermaid`; agent invoked via `uipath run agent` | uipath.github.io/uipath-python/langchain/quick_start | High |
| Maestro case instance = 1 PU per process instance; business rule = 0.2 PU | docs.uipath.com/maestro/.../licensing-unified-pricing | High |

---

## 4. Integration implications (swapping in Studio Web)

**Runtime availability — confirmed, no new provisioning needed.** The folder already runs 6+ `Agent`-type processes, an Agentic process, and three Case Management processes at v1.0.24. That proves the ACR-Serverless agent runtime and the folder's unattended-robot identity are already satisfied. The target agent is **already PUBLISHED at v0.1.0 as Type `Agent (python)`** in this folder, so deployment prerequisites (published, in-folder, PackageType=Agent) are met. **Verify only:** the folder has an unattended robot identity assigned.

**What must change to swap `Function` → `Agent`:**

1. **Entry point / invocation surface.** Function exposes named workflow args via `main`. Agent exposes the LangGraph graph via `entry-points.json` (generated by `uipath init`), invoked as `uipath run agent`. Studio Web reads `entry-points.json` to populate the I/O schema selector. The operative artifact for a *coded* langgraph agent is **`entry-points.json` + `langgraph.json`**, not the low-code `agent.json`.

2. **Caseplan binding / resourceKey.** The agent task must be re-pointed from the Function process to the **Agent process name** `forensic-self-exam-agent-langgraph`. Per this project's build mechanics, solution binding resolution uses the process resource *name* (= package name), and `pack-solution` does **not** regenerate the `resources/` registration `bindingType` — so the binding must be **hand-edited** after packing.

3. **Input/output schema mapping (highest-risk step).** Maestro sends a flat JSON payload validated against the agent's `entry-points.json`. The caseplan task's I/O mapping must be **re-mapped key-by-key** to the LangGraph graph's typed input keys — exact names. A mismatch yields `Agent.InputArgumentsSchema / Required properties [...] are not present` at runtime. *Mitigating asset:* the langgraph agent's `entry-points.json` already exposes the same 3 inputs (`clearflow_indicators`, `nimbus_indicators`, `clearflow_self_victim`) and same outputs (`route_to`, `clearflow_vector_status`, `rationale`, `error_*`) as the original — so the mapping should be 1:1.

4. **`.bpmn` regeneration — REQUIRED.** Runtime executes the compiled `caseplan.json.bpmn`, not `caseplan.json`, and only the Studio Web browser canvas regenerates the `.bpmn` (CLI pack/upload does not). After re-pointing the binding and re-mapping I/O, open the caseplan in the canvas, regenerate, then `download --extract` and commit the fresh `.bpmn` before pack/deploy.

> **Gap:** No primary source exhaustively documents the **Case Management** task's binding-selector UI flow for swapping an agent process (documented path is BPMN service tasks). Validate against the live canvas.

---

## 5. Budget math

**Per-run cost:** ~0.4 PU (UiPath-hosted Standard) or ~0.2 PU (BYOM / offline fallback).

**Standalone agent capacity of 10K PU:** ~25,000 runs at 0.4 PU; ~50,000 at 0.2 PU.

**Full-demo scenario (the realistic budget):**

| Layer | Count | PU each | Subtotal |
|---|---|---|---|
| Maestro case instances (master + children + grandchildren) | ~25 + 225 + 300 = ~550 | 1 PU | ~550 PU |
| `forensic-self-exam-agent-langgraph` runs (~3 per case path ≈ 75) | ~75 | 0.4 PU | ~30 PU |
| Other Agent Builder / agentic runs | (varies) | 0.2 PU/call | tens of PU |

**Total estimated full-demo burn: ~600–700 PU out of 10,000** — headroom for ~14× full re-runs. **Exhaustion risk for a judging-ready run: effectively zero.**

> Maestro-layer count and "~3 agent runs per case path" are INFERRED from the project architecture, not documented quantities — confirmed *rates*, estimated *counts*.

**Exhaustion flags:** tenant pool is allocation-based and finite (hard ceiling until Aug 11 2026 — monitor Admin → Licenses → Consumables); 64k-input-token increment rule; future Context Grounding/DeepRAG adds 0.2 PU/query.

---

## 6. Risks & open questions (ranked, highest demo-breaking first)

1. **[HIGH — most likely to break the demo] Input/output schema mismatch on the Function→Agent swap.** *Mitigation:* dump `entry-points.json`, re-map every Studio Web task I/O key to match, dry-run the agent task before the full case run.
2. **[HIGH — silent failure] Stale compiled `.bpmn`.** If the canvas isn't regenerated after the swap, the case keeps executing the old Function binding. *Mitigation:* regenerate via canvas → `download --extract` → commit, before packing.
3. **[MEDIUM — binding resolution] Hand-edit of `bindingType` / resource name after pack.** *Mitigation:* hand-edit `resources/` binding to the Agent-type process name.
4. **[MEDIUM — verify, likely fine] Folder unattended-robot identity.** Existing running Agent processes strongly imply it's assigned; confirm in folder settings.
5. **[LOW — billing precision] LLM Gateway metering shape (per-call vs BYOM).** Both trivially cheap. *Mitigation:* check AI Trust Layer → LLM Configurations.
6. **[LOW — assumption] No separate Maestro orchestration charge for the task wrapper.** Inferred from metering-table absence; case-instance 1 PU is already budgeted in §5.
7. **[LOW — gap] Case-Management binding-selector UI flow not exhaustively documented.** Validate hands-on in the canvas.

---

**Bottom line:** Platform Units power this agent cleanly; 10K is ~14× the full-demo need; Heals/ScreenPlay are irrelevant. Approve the swap on the **budget** dimension with high confidence. Treat it as **engineering-gated, not budget-gated**: the win-or-lose work is the schema re-mapping (Risk 1) and the `.bpmn` regeneration + binding hand-edit (Risks 2–3). Verify folder robot identity (Risk 4) and LLM-config metering shape (Risk 5) during the next rehearsal.
