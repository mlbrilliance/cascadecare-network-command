---
title: LangGraph Agent Conversion — Candidate Selection
date: 2026-06-14
branch: feat/langgraph-agent
status: approved-for-implementation
---

# LangGraph Agent Conversion: Candidate Selection

## Ranked Candidates

| Rank | Agent | LangGraph fit | Reason |
|------|-------|--------------|--------|
| 1 | **forensic-self-exam-agent** | ★★★★★ | 3-branch conditional routing maps to conditional edges; LLM enrichment becomes a skippable graph node |
| 2 | multi-customer-pattern-detector | ★★★☆☆ | Cross-provider aggregation is interesting, but the routing is just one if-chain |
| 3 | claim-flow-anomaly-detector | ★★☆☆☆ | Pure scorer — no meaningful graph topology |
| 4 | case-job-janitor | ★☆☆☆☆ | SDK utility, no LLM, no reasoning |

## Why forensic-self-exam-agent wins

The agent embodies a 3-branch routing decision:

```
clearflow_indicators > 0       → vector-hypothesis  (still under investigation)
clearflow == 0, nimbus > 0     → baa-boundary       (cleared / co-victim)
clearflow == 0, nimbus == 0    → escalate           (no evidence — human review)
```

This maps directly to a LangGraph `StateGraph` with:

- **`clamp_node`** — sanitize negative indicator counts → zero
- **`route_node`** — deterministic routing; writes `route_to` + `clearflow_vector_status` into state
- **Conditional edge** — if `route_to == "escalate"` skip LLM (no evidence, no rationale worth generating) → `END`; otherwise → `enrich_node`
- **`enrich_node`** — calls UiPath LLM Gateway for plain-language rationale; catches auth errors so the graph is testable offline

The graph compiles to a single `graph` variable exported at module level — the UiPath SDK recognises `type: "agent"` in `uipath.json` and invokes the compiled graph directly.

## Architectural note

This conversion sits at the *agent SDK layer*, not the orchestration layer. Maestro Case still drives the process; the LangGraph graph is just the implementation of one agent's reasoning. The `main()` function is removed; `uipath.json` is updated to `type: "agent"` with `filePath: "agent"`.

## SPEC

**Purpose:** Convert `forensic-self-exam-agent` routing logic to a LangGraph `StateGraph`
demonstrating framework-agnostic agent layer under Maestro Case.

**Inputs:**
- `clearflow_indicators: int` — count of ClearFlow-implicating forensic indicators (≥0 after clamp)
- `nimbus_indicators: int` — count of Nimbus-implicating indicators (≥0 after clamp)
- `clearflow_self_victim: bool` — true if ClearFlow's own systems were also compromised

**Outputs (in `ForensicState`):**
- `route_to: str` — one of `vector-hypothesis`, `baa-boundary`, `escalate`
- `clearflow_vector_status: str` — one of `unknown`, `cleared`, `co-victim`
- `rationale: str` — LLM-generated plain-language explanation (empty if escalate or LLM unavailable)
- `error_type: str`, `error_message: str` — populated on graph-level exceptions

**Edge cases:**
- Negative indicator counts → clamped to 0 in `clamp_node`
- LLM unavailable (no UiPath auth) → `enrich_node` catches exception, `rationale` = `""`
- Both indicators zero → `escalate` path, LLM skipped entirely

**Side effects:**
- Calls UiPath LLM Gateway only when `route_to != "escalate"` (Trust Layer PHI/PII guardrails apply)

**One-line test:**
`assert invoke({"clearflow_indicators": 0, "nimbus_indicators": 3, "clearflow_self_victim": False})["route_to"] == "baa-boundary"`
