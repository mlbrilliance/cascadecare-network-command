# Forensic Agent Resilience (Criterion-3) — CORRECTED

> **Correction (2026-06-15, verified in Studio Web).** An earlier version of this doc told a
> human to set `Error handling → Element-level retries` on the **Forensic Self-Examination**
> case task. **That section does not exist on Maestro *Case* agent tasks.** Element-level
> auto-retry is a Maestro **Process (BPMN)** properties-panel feature
> ([docs](https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/properties-panel)) —
> it applies to BPMN process task elements (Service / Agent / API Workflow / Queue Item), **not**
> to Case Management tasks. The case agent-task properties panel only exposes General /
> Entry rules / Implementation (Type, Agent, Inputs, Outputs) / Update variables. Confirmed by
> direct UI inspection of the `clearflow-master-crisis` case plan.

## So how is the forensic *case* task made resilient?

Maestro **Case** handles task failure differently from a BPMN process — there is no per-element
auto-retry badge. The actual, available Criterion-3 layers for the forensic case task are:

| Layer | Failure handled | Mechanism | Status |
|---|---|---|---|
| 1. In-agent error surfacing | LLM enrichment fails (520/auth/offline) | `enrich_node` catches, surfaces `error_type`/`error_message`, still returns a valid route — agent does **not** fault | ✅ shipped 2026-06-15 |
| 2. Case rework / re-entry | A stage's work needs to be redone | `rework-stage-and-return` exit type + stage re-entry rules (already in the master-crisis caseplan; drives the 5 reversals) | ✅ already in case |
| 3. SLA escalation | Stage/case exceeds its SLA | `slaRules` → `escalationRule` (notification on breach / at-risk — already in `metadata`) | ✅ already in case |
| 4. Operator instance retry | Persistent fault on a live instance | `uip maestro case instance retry <id>` (or the Case Instance Management console) | ✅ available |

This is a genuinely strong, **case-native** exception story — it just is not "an element retry
badge." The demo/Devpost framing should describe Layers 1–4 above, not BPMN element retry.

## What to actually capture for evidence (`docs/evidence/`)

- Layer 1: the forensic agent output showing `error_type`/`error_message` populated on an
  induced enrichment failure (proves graceful degradation).
- Layer 3: the SLA escalation rule firing (or its config) on the master crisis case.
- Layer 4: an operator `instance retry` recovering a faulted instance (the `Action History`
  audit trail records the retry — strong auditability evidence).

## If you genuinely want element-level retry on the agent

It would require expressing the forensic agent as a task in a **Maestro BPMN Process**, not a
Case task — out of scope for this submission (the case canvas is the orchestrator). Do not
pursue for AgentHack.
