# Evidence — Maestro Flow Demo Driver (1)

**Authoring agent:** Claude Code + the `uipath-maestro-flow` skill. **Slice:** 012.

`maestro_flow/clearflow-demo-driver/flow.json` is the Demo Driver: it fires the API-Workflow
calls at compressed wall-clock intervals so the 90-day narrative plays in ~300 seconds.

- 7 scheduled steps at t+10s, t+25s, t+45s, t+75s, t+120s, t+165s, t+210s, each targeting the
  API Workflow for the simulated reversal event.
- Verified offline against the `.flow` structure gate.

## Verifiable evidence

- `tests/unit/maestro_flow/test_flow_structure.py` (offline gate, 9 cases).
- `docs/demo/run-playbook.md` — how the Demo Driver drives R1→R5 once the master case is live.
- `docs/changelog.md` §"Slice 012".
