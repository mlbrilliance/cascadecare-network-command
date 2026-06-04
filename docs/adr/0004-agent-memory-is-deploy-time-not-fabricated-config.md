# ADR-0004: Agent Memory is a deploy-time toggle, not fabricated offline config

- **Status:** accepted
- **Date:** 2026-06-03

## Context
S022 ("agent-driven progression + Agent Memory") splits into S022.A (master is
agent-driven — done) and S022.B (Agent Memory). For S022.B we audited where UiPath
Agent Memory is actually configured. Findings, all verified against the synced
`uipath-agents` skill references and the repo's own agent definitions:

- **Low-code `agent.json` has no memory field.** Its `settings` block holds only
  `model` / `maxTokens` / `temperature` / `engine` / `maxIterations` / `mode`. There is
  no `agentMemory` / `isAgentMemoryEnabled` toggle at the agent.json root or in `settings`.
- **Agent Memory is a solution-resource concern.** It lives in the solution-side agent
  declaration as `spec.agentMemory` (+ `retentionAction` / `retentionPeriod` /
  `staleRetentionPeriod`). That declaration is **generated and refreshed by the CLI** at
  `uip solution project add` time — it is not a file we own offline, and it is absent from
  the repo because the agents are added to the solution during the (human-gated) live deploy.
- **The coded `memorySpace` binding must never be hand-authored** (skill Hard Rule) — it is
  derived from UiPath Python SDK calls. The coded agents make no memory-space SDK call, and
  the runtime memory SDK API is undocumented.
- **Eval-sets carry `agentMemoryEnabled` / `agentMemorySettings`**, but the settings shape is
  undocumented; populating it would be invention.
- **The actual cross-timeline requirement is already met.** The master case persists the
  state that has to survive the 90-day / 5-reversal timeline — `CaseGoal`, `ReversalNumber`,
  `ClearFlowVectorStatus`, `GrandchildCaseCount`, `SimulatedDay` — as root `inputOutputs`
  variables, backed by Data Fabric. Per-agent memory is additive polish, not a functional gap.

## Decision
Do **not** fabricate any offline agent-memory config. Treat enabling `spec.agentMemory: true`
on the reasoning agents (Vector Hypothesis, BAA Boundary Reasoner, Fiduciary Conflict Detector,
Negligent Monitoring Risk) as an **optional deploy-time toggle** performed during
`uip solution project add` / in Studio Web, recorded as an optional step in the live runbook.
The cross-timeline state requirement is satisfied by the master's root variables + Data Fabric,
which stands on its own.

## Rationale
Every offline path to "turn on agent memory" is either (a) CLI-owned (hand-editing the solution
agent decl reintroduces the exact dangling-resource failure class fixed in Slice-019), or (b)
dependent on an undocumented settings/runtime shape (invention). The project's standing rules —
"do not invent," "keep minimal + honest," and "stop if a dependency/shape cannot be verified" —
all point to documenting the real location rather than forging a flag that looks like a feature.

## Alternatives considered
- Add `agentMemory: true` to a hand-authored solution agent decl — rejected: CLI regenerates it
  and a hand-rolled decl dangles (Slice-019 class).
- Flip `agentMemoryEnabled: true` in the 7 eval-sets — rejected: requires undocumented
  `agentMemorySettings`; changes eval semantics for no demonstrable gain.
- Hand-author a coded `memorySpace` binding — rejected: violates the skill Hard Rule (bindings
  derive from SDK calls) and the runtime API is undocumented.

## Consequences
- S022.B ships as a decision + an optional runbook step (LIVE-RUN-GUIDE "Part E"), not code.
- Cross-timeline continuity in the demo is carried by master root variables + Data Fabric — future
  reviews should NOT flag "the agents have no memory" as a defect; it is a recorded, deliberate
  boundary.
- If/when UiPath documents the runtime memory API, revisit to wire per-agent recall as polish.
- Future architecture reviews should NOT re-suggest hand-authoring solution agent decls or
  `memorySpace` bindings to "enable memory."
