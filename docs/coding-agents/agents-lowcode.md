# Evidence — Agent Builder agents (4, low-code)

**Authoring agent:** Claude Code + the `uipath-agents` skill. **Slice:** 008.
**LLM:** Claude via UiPath BYO-LLM (`anthropic.claude-sonnet-4-6`), every call through the
LLM Gateway so Trust Layer PHI/PII guardrails apply.

| Artifact | Reversal | Notes |
|---|---|---|
| `agents/vector-hypothesis-agent/` | R2 | Attack-vector determination (ClearFlow vs Nimbus). |
| `agents/baa-boundary-reasoner/` | R3 | Per-provider BAA-vs-subpoena; Context Grounding on `BAA-corpus`. |
| `agents/fiduciary-conflict-detector/` | R4 | Tri-party conflict + HITL form payload. |
| `agents/negligent-monitoring-risk-agent/` | R5 | Co-defendant exposure. |

Each carries `agent.json` + `entry-points.json` + `project.uiproj`; the system prompt is
**byte-identical** to its `agents/prompts/*.md` template (prompts are never inlined in code).

## Real prompt excerpt — `baa-boundary-reasoner`

> "You analyze ONE provider customer's Business Associate Agreement (BAA) terms against the
> scope of a regulatory subpoena … Because each BAA differs, one subpoena produces six
> different defensible positions — the six-answer problem. … Ground every term you cite in
> retrieved `BAA-corpus` text — do not invent BAA language."
> — [`agents/prompts/baa_boundary_reasoner.md`](../../agents/prompts/baa_boundary_reasoner.md)

## Verifiable evidence

- [`agents/prompts/*.md`](../../agents/prompts/) — the four committed prompt templates.
- `agents/<key>/agent.json` — input/output schemas mirroring `entry-points.json`.
- `docs/changelog.md` §"Slice 008".
