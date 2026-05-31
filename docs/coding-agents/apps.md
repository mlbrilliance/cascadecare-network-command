# Evidence — UiPath Apps narrative dashboard (1)

**Authoring agent:** Claude Code + the `uipath-coded-apps` skill. **Slices:** 013 (authoring),
015 (branding).

`apps/clearflow-network-command/` is the single-screen narrative dashboard: cascade tree +
reversal timeline + agent-activity feed + override controls, with a Coded App backend
(`models.py` + `dashboard.py` + `main.py`).

- TDD: 45 backend tests authored before source (Slice 013); a 7-assertion branding gate added
  in Slice 015 (`test_dashboard_branding.py`).
- Slice 015 added a top-level `theme` block to `app.json` (brandName, logo, semantic palette
  hex, Inter typography) — fictional ClearFlow brand only.
- The `reversal_timeline` carries the "★ Hero moment" highlight on Reversal 3 (the App carries
  the hero emphasis since Maestro canvas layout is editor-only and not authorable in source).

## Verifiable evidence

- `tests/unit/apps/clearflow_network_command/` — 59 tests (45 backend + 7 branding + IP/guard).
- `specs/003-uipath-native/event-contracts/override-post.json` — the override contract.
- `docs/changelog.md` (Slice 013 entry); `specs/003-uipath-native/slice-015-tasks.md` §Phase 3.
