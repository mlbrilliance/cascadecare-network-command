# Evidence — Coded Agents (3, Python SDK)

**Authoring agent:** Claude Code + the `uipath-coded-apps` skill, **test-driven** (test files
written before source, enforced by the pre-write hook). **Slice:** 009.
**Framework:** UiPath Coded Function; UiPath first-party LLM for enrichment.

| Artifact | Logic |
|---|---|
| `agents/claim-flow-anomaly-detector/` | Anomaly score + severity bands; `critical` ≥0.70 matches the `provider-claim-anomaly` trigger. |
| `agents/multi-customer-pattern-detector/` | Emits the cascade signal iff ≥3 providers anomalous. |
| `agents/forensic-self-exam-agent/` | Routing + ClearFlow vector-status determination. |

Each: `agent.py` (pydantic Input/Output + deterministic core + lazy LLM-enrichment hook) +
`uipath.json` + `entry-points.json` + a build-system-free `pyproject.toml`.

## Real prompt excerpt — `claim-flow-anomaly-detector`

> "You assess claim-flow telemetry for a single provider customer and classify how anomalous
> the observed claim volume is relative to that provider's 30-day baseline."
> — [`agents/prompts/claim_flow_anomaly_detector.md`](../../agents/prompts/claim_flow_anomaly_detector.md)

## Verifiable evidence

- `tests/unit/agents/<name>/` — 60 logic tests + a 7-agent registry-consistency gate, authored
  **before** the agents (TDD).
- `docs/changelog.md` §"Slice 009".
