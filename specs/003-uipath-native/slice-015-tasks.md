---
description: "Slice 015 — Polish & Dress Rehearsal implementation tasks"
---

# Tasks: Slice 015 — Polish & Dress Rehearsal

**Input**: `specs/003-uipath-native/plan.md`, `research.md`

**Format**: `[ID] [P?] [Story] Description with exact file path`

## User Stories

- **US1** (P1): A judge sees the Reversal-3 hero moment — 6 stakeholder cases spawn in a crisp, visible horizontal fan on the master canvas.
- **US2** (P2): A judge sees a branded, on-narrative UiPath Apps dashboard (ClearFlow logo, palette, typography).
- **US3** (P3): The demo runs end-to-end (R1→R5) within 300s, three times in a row — **GATED on the run-blocker**.

**Phase split** (from the analyze report): Phase 1 (US1+US2) is fully **offline-unblocked** and independently shippable. Phase 2 (US3) is **BLOCKED-pending-run-unblock** (entry-points install + Maestro folder context).

---

## Phase 1: Foundational — offline TDD gate

**Purpose**: Write the offline structure tests before the artifact edits. These are JSON/config gates (not under agents//shim//mocks/, so the pre-write hook doesn't force them — but plan.md commits to them).

- [~] T001 [P] [US1] ~~Write `test_master_fan_layout.py`~~ **DROPPED (impl finding)**: Maestro Case canvas layout is editor-only auto-layout — `layout` is `{}` in both source AND the tenant download; nodes carry no x/y; `operate.json` has none. Nothing to test offline. US1 decision: **accept default auto-layout** (the 6 simultaneous spawns stay visible, just not hand-fanned).
- [X] T002 [P] [US2] Write `tests/unit/apps/clearflow_network_command/test_dashboard_branding.py` — asserts app.json carries a `theme` block (palette hex for accent/muted/success/warning/danger, logo ref, typography.fontFamily, brandName) + zero forbidden IP tokens. 7 assertions.
- [X] T003 GATE: ran `uv run pytest test_dashboard_branding.py` → RED (5 fail on missing theme, 2 pass JSON+IP). TDD gate passed.

**Checkpoint**: Both offline tests exist and are RED — TDD gate passed ✅

---

## Phase 2: US1 — Reversal-3 hero fan layout — ❌ CLOSED (not achievable offline)

**Decision (2026-05-31): accept default editor auto-layout.** Implementation
discovery: Maestro Case canvas positions are NOT stored in the caseplan source
or the tenant download (`layout: {}` everywhere; no node x/y; `operate.json`
clean). A "visible horizontal fan" is only producible by manual drag in Studio
Web, which does not persist to source / survive re-deploy → not committable, not
reproducible. The 6 spawns remain visibly simultaneous in their default
arrangement; the hero-moment emphasis is carried instead by the Apps
`reversal_timeline` ("★ Hero moment" highlight on Reversal 3, already in app.json).

- [~] T004 [US1] CLOSED — `layout` block is empty; nothing to baseline.
- [~] T005–T008 [US1] CLOSED — no source layout edit; auto-layout accepted.

**Checkpoint**: US1 resolved by decision (no source change) ✅

---

## Phase 3: US2 — UiPath Apps branding (OFFLINE, unblocked now)

**Goal**: The dashboard screen carries the ClearFlow brand (logo, palette, typography), fictional names only.

**Independent Test**: `test_dashboard_branding.py` passes GREEN; `/audit-ip-safety` green.

- [X] T009 [US2] A1 resolved: app.json is a bespoke declarative screen spec (schemaVersion 2.0) using semantic color tokens (accent/muted/success/warning/danger) with no prior theme block. Real UiPath coded-app theming is React/CSS (per uipath-coded-apps skill); this project's brandable surface is the self-authored app.json → extend it with a top-level `theme` block (project-internal convention; renders once the app-deploy shape is resolved).
- [X] T010 [US2] Added top-level `theme` block to `apps/clearflow-network-command/app.json` (brandName, logo `assets/clearflow-logo.svg`, palette hex incl. accent #0E7C86, typography Inter) — fictional brand only.
- [X] T011 [US2] `uv run pytest tests/unit/apps/clearflow_network_command/` → 59 passed (7 branding + 52 existing).

**Checkpoint**: Branding green offline ✅

---

## Phase 4: Phase-1 publish + commit (OFFLINE)

- [~] T012 N/A — the branding change is in `app.json` (the UiPath App), not the `maestro_case` solution. No caseplan changed this slice → no solution re-pack/upload needed (and US1 layout was dropped). The App deploys via its own (still-blocked) mechanism.
- [~] T013 N/A — no fan-layout coords to round-trip (US1 closed); solution unchanged.
- [X] T014 Ran the IP-safety audit (audit-ip-safety command spec) → **PASS**. Every token match in the repo is a denylist *definition* (constitution/CLAUDE/AGENTS/Makefile/test) or a substring collision (gzipped→zipp, newExperiences→wex); slice-015 files clean.
- [X] T015 Commit Phase-1: `feat(slice-015): polish — Apps branding theme (offline); US1 fan = editor auto-layout`

**Checkpoint**: Offline polish shipped and pushed — Phase 1 complete ✅

---

## Phase 5: US3 — Run-blocker resolution (⛔ BLOCKED-pending-run-unblock)

**Goal**: Make R1→R5 actually runnable so dry runs can pass.

**Independent Test**: one API-workflow package installs without Error 2005; the master case can be triggered (CLI or Maestro UI).

- [X] T016 [US3] **Root cause found + fixed offline (install-confirm tenant-gated).** Empirical pack probe (`uip solution pack`, offline) proved the Api packager writes a `package-descriptor.json` declaring `content/entry-points.json` + `content/bindings_v2.json` but never generates them for `Type:"Api"` projects → "entry points configuration missing" = Error 2005. Authored `api_workflows/provider-northstar/entry-points.json` (V20 shape, schema `https://cloud.uipath.com/draft/2024-12/entry-point`, `filePath:"main.json"`, `type:"process"`, `uniqueId` GUID, input/output from `main.json`) + `bindings_v2.json`; re-pack proved **all descriptor-declared files now present** in the nupkg. Live install-confirm carried forward.
- [X] T017 [US3] Fanned out via `scripts/gen_api_entry_points.py` (deterministic `uuid5(slug)`) → all 14 `api_workflows/*` carry `entry-points.json` + `bindings_v2.json`; gate `tests/unit/api_workflows/test_entry_points.py` (57 assertions) GREEN; full suite 472 passed. **BPMN (Error 1654):** assessed — the `.bpmn` is offline-valid, carries `<uipath:entryPointId value="Entry_IdealIncidentResponse"/>` matching its `entry-points.json` `id`, with the skill-canonical shape + correct `filePath`; no offline defect found → 1654 needs a live install to reproduce (carried forward). Solution re-add + re-upload is the tenant step (pack-solution.sh note updated).
- [X] T018 [US3] Wrote `docs/demo/run-playbook.md` — Path A (CLI folder-key → release-key → `case process run`, with the Slice-014 `-f` rejection recovery) + Path B (Maestro-UI trigger fallback) + reversal cue sheet + `docs/demo/inputs/r1-kickoff.json` (`{}` — master case takes no required start inputs).

**Checkpoint**: Offline run-blocker authoring DONE + proven by pack; live launch + install-confirm carried to a tenant session ⏸️ (Phase 6 stays gated).

---

## Phase 6: US3 — Dry runs, latency, recording (⛔ GATED on Phase 5)

**Goal**: 3 clean 300s dry runs with the R3 fan visible and crisp.

**Independent Test**: `docs/demo/dry-run-log.md` records 3 consecutive runs ≤300s, each noting R3 fan visible.

- [ ] T019 [US3] Define a concrete latency bar (resolve A2: e.g. each agent step completes < N s for live narration) and record it in `docs/demo/dry-run-log.md`
- [ ] T020 [US3] Run dry-run #1; record wall-clock total + per-stage timings + R3-fan-visible note; review narrative tightness
- [ ] T021 [US3] If any agent step exceeds the T019 bar, add cache/warm-up at that step (only on a measured miss); else skip
- [ ] T022 [US3] Run dry-runs #2 and #3; record each; confirm 3 consecutive ≤300s runs with R3 fan crisp
- [ ] T023 Final commit: `feat(slice-015): polish — hero moment engineered; demo timing locked`

**Checkpoint**: Acceptance gate met — Slice 015 complete ✅

---

## Dependencies & Execution Order

- **Phase 1 (T001–T003)** before Phase 2/3 (RED tests first).
- **T001, T002** are [P] (different files). **T004–T008 (US1)** ‖ **T009–T011 (US2)** are independent — run in parallel.
- **Phase 4** after both US1 + US2 green.
- **Phase 5 (T016–T018)** is BLOCKED until the run-blocker authoring is done; **Phase 6** depends on Phase 5.
- If Phase 5 cannot clear this session (next-layer authoring / human folder/OAuth action), ship Phase 1 (offline polish) and carry Phases 5–6 forward — flagged, never silently marked complete.

## MVP Scope

**Phase 1 (US1 + US2)** is the shippable MVP for this slice — the hero-moment fan + branded dashboard land offline today. US3 (live dry runs) is the stretch, gated on the run-blocker.

## Parallel Example

```
# After T001–T003 are RED, run US1 and US2 tracks concurrently:
Track A (US1): T004 → T005 → T006 → T007 → T008   # fan layout
Track B (US2): T009 → T010 → T011                  # Apps branding
# Converge at T012 (pack) → T013 → T014 → T015 (commit)
```
