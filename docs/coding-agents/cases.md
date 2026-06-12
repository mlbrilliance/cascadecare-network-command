# Evidence — Maestro Case definitions (3)

**Authoring agent:** Claude Code + the `uipath-maestro-case` skill. **Slice:** 010.
**Contract:** Maestro Case V20 schema (product reached **Controlled GA, 2026-03-30**), three caseplan.json files wired via
the native `case-management` task type — no Postgres mirror, no Level-flag superset.

| Artifact | Role |
|---|---|
| `maestro_case/clearflow-master-crisis/` | Top crisis case; its Regulatory Response stage (`Stage_JM1SVs`) carries the six `case-management` spawn tasks, all gated on BAA Boundary Analysis so they fire simultaneously — the visible **Reversal-3 fan**. |
| `maestro_case/clearflow-stakeholder-parent/` | Per-customer parent (Onboarding → Impact Assessment → Obligation Determination → Resolved); spawns obligation grandchildren. |
| `maestro_case/clearflow-obligation-grandchild/` | Leaf case (Intake → Response → Discharged) for a single BAA / regulatory obligation. |

## How Claude Code authored these

- Read the V20 Private Preview guide via `uipath-maestro-case`; authored all three
  caseplans to the canonical V20 rules (`=js:` expressions, six exit types,
  `caseAppEnabled`/`publishVersion:2`/`intsvcActivityConfig:"v2"`, variable dedup).
- Encoded `metadata.slaRules` on every case after discovering the compiler ignores
  `defaultSla` (Slice 014 decision) — grandchild at Slice 010, master (90d) + parent (45d)
  added in **Slice 021**.
- Wired the qem: Data Fabric fan-out + `hitlTask` output variable + `Maestro.NotificationService`
  task (Slice 014 platform-feature integration).
- **Slice 021:** lifted the grandchild's stage-level escalation pattern up to master + parent —
  per-stage `slaRules` whose `escalationRule` fires `sla-breached` + `at-risk` (80%) notification
  actions to `=metadata.caseOwner`, tuned so reversal timing flips on-canvas at-risk/breached
  badges. Gate: `tests/unit/maestro_case/test_slice021_sla_escalation.py`.

## Verifiable evidence

- `tests/unit/maestro_case/test_caseplan_structure.py` + `test_slice014_features.py` (offline V20 gates).
- `specs/003-uipath-native/case-vocabulary.yaml` — the stage/task ID registry the caseplans satisfy.
- `docs/changelog.md` §"Slice 010 — Three-Level Case Nesting".
