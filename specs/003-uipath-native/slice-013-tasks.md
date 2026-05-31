---
description: "Slice 013 — UiPath Apps Narrative Dashboard implementation tasks"
---

# Tasks: Slice 013 — UiPath Apps Narrative Dashboard

**Input**: `specs/003-uipath-native/plan.md`, `research.md`, `data-model.md`

**Format**: `[ID] [P?] [Story] Description with exact file path`

## User Stories

- **US1** (P1): Demo operator sees live cascade tree + reversal timeline in one screen
- **US2** (P2): Demo operator monitors agent activity feed in real time
- **US3** (P3): Demo operator fires overrides (reversal triggers, grandchild spawns, HITL gate)

---

## Phase 1: Setup — Directory scaffolding

**Purpose**: Create directory structure before any file writes (pre-write hook requires test before source)

- [ ] T001 Create `tests/unit/apps/clearflow_network_command/` directory
- [ ] T002 Create `apps/clearflow-network-command/backend/` directory
- [ ] T003 [P] Create `specs/003-uipath-native/event-contracts/` directory (if not exists)

**Checkpoint**: Directories exist; no source files yet

---

## Phase 2: Foundational — TDD Gate (CRITICAL — C1)

**Purpose**: Write ALL test files before any source file exists. Gate: tests must be RED.

⚠️ **CRITICAL**: Pre-write hook will block source files without corresponding tests. Do Phase 2 completely before Phase 3.

- [ ] T004 [P] Write `tests/unit/apps/clearflow_network_command/__init__.py` (empty file — pytest discovery)
- [ ] T005 [P] [US1][US2][US3] Write `tests/unit/apps/clearflow_network_command/test_models.py` — unit tests for all Pydantic models: CaseStatus, AgentType, AgentStatus, OverrideAction enums; CaseNode, ReversalEvent, AgentActivity, OverrideControl, CascadeTree, DashboardPayload validation; invalid enum rejection; None/optional fields
- [ ] T006 [P] [US1][US2][US3] Write `tests/unit/apps/clearflow_network_command/test_dashboard.py` — tests for `build_fixture_payload()`: returns DashboardPayload; cascade_tree.master.level==0; len(reversal_timeline)==5; all reversals inactive on init; len(agent_activity)==7; agent_ids match the 7 known agents; len(override_controls)==8; all controls enabled on init; refreshed_at is ISO-8601 string; `UIPATH_LIVE` env-var guard: with flag unset, fixture path is taken
- [ ] T007 GATE: run `uv run pytest tests/unit/apps/` — MUST fail with ImportError (models not yet written); abort if unexpectedly green

**Checkpoint**: Tests exist and are RED — TDD gate passed ✅

---

## Phase 3: US1 — Cascade Tree + Reversal Timeline

**Goal**: Demo operator sees the three-level case hierarchy and reversal timeline from a single endpoint.

**Independent Test**: `test_dashboard.py::test_cascade_tree_structure` and `test_dashboard.py::test_reversal_timeline_init` pass GREEN.

### Implementation — US1

- [ ] T008 [US1] Write `apps/clearflow-network-command/backend/models.py` — Pydantic models: CaseStatus, AgentType, AgentStatus, OverrideAction enums; CaseNode, ReversalEvent, AgentActivity, OverrideControl, CascadeTree, DashboardPayload. Under 200 lines. IP-safe: all display names use fictional names only.
- [ ] T009 [US1] Write `apps/clearflow-network-command/backend/dashboard.py` — `build_fixture_payload() -> DashboardPayload` returning fully populated fixture: 1 master + 9 parent + 6 grandchild nodes (Day-30 state); 5 reversals; 7 agents (3 coded + 4 builder); 8 override controls. `UIPATH_LIVE` env-var guard (live reads stubbed, raise NotImplementedError). Under 250 lines.
- [ ] T010 [US1] GATE: `uv run pytest tests/unit/apps/clearflow_network_command/test_models.py tests/unit/apps/clearflow_network_command/test_dashboard.py` — must be GREEN

**Checkpoint**: US1 data layer is complete and tested ✅

---

## Phase 4: US2 — Agent Activity Feed

**Goal**: Demo operator can query agent status; feed shows 7 agents with type, status, invocation count.

**Independent Test**: `test_dashboard.py::test_agent_activity_*` pass GREEN.

### Implementation — US2

- [ ] T011 [US2] Write `apps/clearflow-network-command/backend/main.py` — UiPath Coded App entry point: imports dashboard + models; registers `GET /dashboard` handler returning `DashboardPayload.model_dump()`; registers `POST /override` handler accepting `{"action": OverrideAction}` and returning `{"accepted": true, "action": action}` (stub — full wiring in Slice 014). SPEC block:
  ```
  SPEC: register_handlers
  Purpose: Wire Coded App HTTP handlers for GET /dashboard and POST /override
  Inputs: app instance from uipath SDK
  Outputs: none (side effect: handlers registered)
  Edge cases: invalid action enum → 422; missing body → 422
  Side effects: none at import time
  Test: test_dashboard.py covers payload shape; main.py tested at Slice 014 deploy
  ```
- [ ] T012 [US2] Write `apps/clearflow-network-command/backend/pyproject.toml` — Coded App package manifest: `name = "clearflow-network-command-backend"`, `[project.entry-points."uipath.coded_app"]`, version, Python ≥3.12 requirement, dependencies: `uipath`, `pydantic>=2`

**Checkpoint**: US2 complete — 7-agent feed available via GET /dashboard ✅

---

## Phase 5: US3 — Override Controls + UiPath Apps JSON

**Goal**: Demo operator sees 4-zone screen in UiPath Apps with override buttons; screen binds to Coded App backend.

**Independent Test**: `project.json` validates as `Type: App`; `app.json` has 4 `container` zones; all zone `dataSource` keys reference `/dashboard` endpoint.

### Implementation — US3

- [ ] T013 [US3] Write `apps/clearflow-network-command/project.json` — UiPath Apps project manifest: `{ "type": "App", "name": "ClearFlow Network Command", "version": "1.0.0", "backend": "backend/", "screens": ["main"] }`. No real company names.
- [ ] T014 [P] [US3] Write `apps/clearflow-network-command/app.json` — Single-screen UiPath Apps V2 definition: 4 container zones (cascadeTree, reversalTimeline, agentActivityFeed, overrideControls). Each zone has: `id`, `title`, `dataSource: { endpoint: "/dashboard", field: "<zone_field>" }`, `components` array. Override zone has 8 button components with `action` mapped to OverrideAction values. Screen header: "ClearFlow Network Command". Under 400 lines.
- [ ] T015 [P] [US3] Write `specs/003-uipath-native/event-contracts/override-post.json` — POST /override contract: request `{ "action": "fire_reversal_1..5 | spawn_grandchildren | trigger_hitl_gate | reset_demo" }`, response `{ "accepted": true, "action": "<action>" }`, error 422 `{ "detail": "invalid action" }`, error 409 `{ "detail": "control already fired", "control_id": "<id>" }`

**Checkpoint**: US3 complete — app.json renders 4-zone screen with override buttons ✅

---

## Phase 6: Polish + Quality Gates

- [ ] T016 Add `UIPATH_LIVE=false` to `.env.example` (append, surgical edit)
- [ ] T017 GATE: `uv run pytest` — full suite GREEN (models + dashboard + existing tests)
- [ ] T018 GATE: `/audit-ip-safety` — GREEN (no forbidden tokens in any new file)
- [ ] T019 Update `specs/003-uipath-native/tasks.md` — mark Slice 013 complete with status note
- [ ] T020 `make checkpoint TASK=013 NAME=slice-013-apps-dashboard PASSED=1 DETAILS="UiPath Apps screen + Coded App backend authored offline; pytest green; IP-safe"`
- [ ] T021 `make save-session TASK=013 SUMMARY="Slice 013 complete: apps/clearflow-network-command authored" DECISIONS="Single DashboardPayload endpoint; fixture mode until Slice 014 tenant" BLOCKERS="none" NEXT="Slice 014: solution packaging + tenant publish"`
- [ ] T022 `git commit -m "feat(slice-013): UiPath Apps narrative dashboard — 4-zone screen + Coded App backend"`

---

## Dependencies

- **Phase 1**: No deps — start immediately
- **Phase 2**: After Phase 1 — BLOCKS Phases 3–5 (C1 TDD gate)
- **Phase 3**: After Phase 2 gate (T007 RED)
- **Phase 4**: After Phase 3 (T010 GREEN) — models must exist
- **Phase 5**: After Phase 3 (T010 GREEN); parallel with Phase 4
- **Phase 6**: After T017 GREEN + T018 GREEN

## Parallel Opportunities

```bash
# Phase 2 — all test files in parallel:
T004, T005, T006 simultaneously

# Phase 5 — app.json and override contract in parallel:
T014, T015 simultaneously
```

## Total

- Tasks: 22
- Parallel: T004+T005+T006, T014+T015
- Phases: 6
- Critical gate: T007 (RED confirms TDD compliance)
