# Evidence — Integration Service API Workflows (14)

**Authoring agent:** Claude Code + the `uipath-api-workflow` skill. **Slices:** 006 (authoring),
015 (install-metadata fix). **Contract:** `Type:"Api"`, CNCF Serverless Workflow DSL 1.0.0.

One workflow per external-system source_system slug, each emitting its Maestro-Trigger event:
6 `provider-*` → `provider-claim-anomaly`; 4 `payer-*` → `payer-demand`; `vendor-nimbus` →
`vendor-attribution`; `regulator-tn-doi` → `regulatory-subpoena` | `litigation-event`;
`insurer-aurora-specialty` → `insurer-directive`; `counsel-hawthorne` → privilege utility.

## Empirical diagnosis — Orchestrator Error 2005 (Slice 015 T016/T017)

Claude Code did not guess the fix. It packed a single Api project offline with the real CLI
(`uip solution init` → `project add` → `uip solution pack`) and unzipped the nupkg:

- The packer-generated `package-descriptor.json` declared `content/entry-points.json` and
  `content/bindings_v2.json` in its `files` map — **but the packer never generated them for
  `Type:"Api"` projects.** Declared-but-absent files = "entry points configuration missing"
  → Error 2005.
- Fix: each `api_workflows/<slug>/` now commits `entry-points.json` (V20 shape, derived from
  `main.json`) + `bindings_v2.json`. A re-pack proved **all descriptor-declared files present**.
- Generated reproducibly by [`scripts/gen_api_entry_points.py`](../../scripts/gen_api_entry_points.py)
  (deterministic `uuid5(slug)`); the live install-confirm is tenant-gated (carried forward).

## Verifiable evidence

- `tests/unit/api_workflows/test_workflow_structure.py` (58-case DSL gate) +
  `test_entry_points.py` (57-assertion install-metadata gate).
- `api_workflows/README.md` — slug→event mapping.
- `docs/changelog.md` §"Slice 006"; `specs/003-uipath-native/slice-015-tasks.md` §Phase 5.
