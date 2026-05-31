# Evidence — Maestro BPMN ideal-response model (1)

**Authoring agent:** Claude Code + the `uipath-maestro-bpmn` skill. **Slice:** 011.

`maestro_bpmn/clearflow-ideal-incident-response/` documents the happy-path playbook
(intake → triage → contain → notify → close) with an `is_cascade?` gateway that diverges into
spawning the ClearFlow master crisis case.

## How Claude Code authored / validated it

- Modeled the BPMN skeleton + UiPath extension XML; the cascade decision is computed in the
  gateway expression (`=vars.affectedCustomerCount>=3`) rather than a scriptTask, after a
  Slice-014 finding that editor variable-injection fails on a JS scriptTask.
- The root start event carries `<uipath:entryPointId value="Entry_IdealIncidentResponse"/>`
  matching `entry-points.json` `id`, with `filePath` `/content/<bpmn>#Start_IncidentIntake`
  per the maestro-bpmn metadata-regeneration canon.
- Verified offline: `uip maestro bpmn validate` → `Status: "Valid"` (1 process, 1 start event,
  9 UiPath extensions).

**Carried forward:** Orchestrator install Error 1654 ("entry points definition invalid") — the
`.bpmn` is offline-valid and the entry-points are skill-canonical, so 1654 needs a live install
to reproduce/diagnose (documented in `docs/demo/run-playbook.md`).

## Verifiable evidence

- `tests/unit/maestro_bpmn/` offline gate; `uip maestro bpmn validate` output.
- `docs/changelog.md` §"Slice 011".
