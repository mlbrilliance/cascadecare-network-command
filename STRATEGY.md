---
name: CascadeCare Network Command
last_updated: 2026-06-14
---

# CascadeCare Network Command Strategy

## Target problem
Healthcare payment intermediaries hit by a multi-provider cyberattack face a coordination
collapse: anomaly detectors fire, but nothing tracks 37+ legal obligations across 6
providers over 90 days, enforces SLAs, routes human decisions only where required, and
produces an auditable case record.

## Our approach
Use UiPath Maestro Case as the native crisis orchestrator — three levels of nested cases,
five goal reversals with targeted stage re-entry, and autonomous agent-driven progression —
so the incident command structure reflects real crisis behavior without bespoke orchestration
code, and every LLM call flows through the UiPath Trust Layer by default.

## Who it's for
**Primary:** UiPath AgentHack judges and healthcare automation buyers evaluating Maestro
Case's capability ceiling.
**Secondary:** UiPath's healthcare vertical sales team.

## Key metrics
- End-to-end run completion rate
- HITL branch fidelity (Reversal 4 fiduciary gate)
- Context Grounding retrieval relevance (BAA-corpus)
- Demo wall-clock runtime (≤5 minutes)
- Judging outcome (Jun 3–Jul 14 2026)

## Tracks

### Case architecture
Three-level Maestro Case nesting: `clearflow-master-crisis` → `clearflow-stakeholder-parent`
(~9) → `clearflow-obligation-grandchild` (~12). Five goal reversals with `rework-stage-and-return`
and `send-to-stage` exit types. Hero moment at Reversal 3 (Day 30): 6 grandchild spawns fan
out on the canvas.

### Agent layer
- 3 Coded Agents (Python SDK, UiPath first-party LLM via Trust Layer): claim-flow-anomaly-detector,
  multi-customer-pattern-detector, forensic-self-exam-agent
- 4 Agent Builder agents (low-code, Claude BYO-LLM): BAA Boundary Reasoner (Context Grounding),
  Classify Obligation, Fiduciary Conflict Detector, Vector Hypothesis
- 1 ops utility Coded Agent: case-job-janitor (hourly trigger, sweeps zombie jobs)

### Vertical bridge
CascadeCare demonstrates Maestro Case orchestrating UiPath's own ViVE-2026 Healthcare
Agentic Solutions (Medical Records Summarization, Claim Denial Prevention, Prior Auth)
as sub-agents. This positions ClearFlow as the Maestro layer above UiPath's own solutions.

### LangGraph agent conversion
One Coded Agent converted to LangGraph/LangChain running on the UiPath Python SDK,
demonstrating that Maestro Case is framework-agnostic at the agent layer. The converted
agent uses LangGraph's conditional graph to express the same routing logic with explicit
state, typed edges, and LLM-enriched narration as a graph node.

## Milestones
- 2026-06-14 — LangGraph conversion branch cut (`feat/langgraph-agent`)
- 2026-06-29 — AgentHack 2026 submission deadline (11:45 PM EDT)
- 2026-07-14 — Finalist judging window closes

## Not working on
- A live Python/LangGraph runtime harness replacing Maestro Case canvas
- Real patient/company/litigation references
- General-purpose crisis platform
- Non-UiPath orchestration (no LangGraph, no Python harness at the *case* layer)
