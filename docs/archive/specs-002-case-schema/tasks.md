# Tasks: Three-Level Case Schema

**Input**: Design documents from `specs/002-case-schema/`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md) | **Contracts**: [contracts/case_repository.py](./contracts/case_repository.py)

**⚠️ Constitution I — TDD-First (NON-NEGOTIABLE)**: Every test task MUST be completed and the test confirmed FAILING before the corresponding implementation task begins. The pre-write hook blocks source files in `agents/`, `shim/`, `mocks/` if the test file does not exist. For `models/`, `db/`, `probe/` the same discipline is enforced by task ordering below.

## Format: `[ID] [P?] [USN?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on sibling tasks)
- **[USN]**: Maps to User Story N from spec.md
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add missing dependencies and create directory scaffolding. No user story work begins here.

- [X] T001 Add `alembic>=1.13` to `[project.optional-dependencies] dev` in `pyproject.toml` and run `uv sync --extra dev`
- [X] T002 Add `[tool.pytest.ini_options]` section to `pyproject.toml` with `asyncio_mode = "auto"` (required for pytest-asyncio with async tests)
- [X] T003 [P] Create missing source directories: `src/cascadecare/db/`, `src/cascadecare/db/migrations/`, `src/cascadecare/db/migrations/versions/`, `src/cascadecare/probe/`
- [X] T004 [P] Create missing test directories and `__init__.py` files: `tests/unit/models/`, `tests/unit/probe/`, `tests/integration/models/`
- [X] T005 [P] Create placeholder `__init__.py` files for all new source packages: `src/cascadecare/db/__init__.py`, `src/cascadecare/probe/__init__.py`

**Checkpoint**: `uv sync --extra dev` passes; `uv run alembic --version` prints a version string; all directories exist.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story model can be implemented.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T006 Create `src/cascadecare/models/base.py` — `DeclarativeBase` subclass named `Base`, shared `metadata` object, `created_at` and `updated_at` mixin using `mapped_column(TIMESTAMPTZ, server_default=func.now())`
- [X] T007 Create `src/cascadecare/db/engine.py` — async engine factory `create_async_engine_from_settings()` that reads `DATABASE_URL` from the pydantic-settings `Settings` object in `src/cascadecare/config.py`; never hardcodes credentials
- [X] T008 Create `src/cascadecare/db/session.py` — `AsyncSession` context manager `get_session()` for use in tests and agent code; uses engine from T007
- [X] T009 Initialise Alembic: run `uv run alembic init src/cascadecare/db/migrations` from project root, then edit `alembic.ini` at project root to set `script_location = src/cascadecare/db/migrations` and `sqlalchemy.url` to read from environment variable `DATABASE_URL`
- [X] T010 Edit `src/cascadecare/db/migrations/env.py` — configure for async engine using `run_sync`; import `Base.metadata` from `src/cascadecare/models/base.py` so Alembic can autogenerate revisions; import all model modules so they register with `Base.metadata`
- [X] T011 Create `src/cascadecare/models/__init__.py` — re-export `Base` and all model classes (will be filled in as models are added in later phases)

**Checkpoint**: `uv run alembic current` runs without error (returns `<no revision>`); async engine factory is importable; `get_session()` is importable.

---

## Phase 3: User Story 1 — Operator creates a master crisis case and watches parent cases spawn (Priority: P1) 🎯 MVP

**Goal**: Persist a master crisis case and one or more provider/payer/vendor parent cases beneath it; verify the FK chain and basic status transitions with state-event logging.

**Independent Test**: Create a `MasterCrisisCase` and three `ParentCase` rows in an in-memory SQLite session (or mocked session), query them back, confirm relationships. No database migration required for unit tests.

### Tests for User Story 1 (TDD — write these FIRST, confirm they FAIL before T018)

- [X] T012 [P] [US1] Write `tests/unit/models/test_case.py` — `test_master_case_default_values`: assert `status == "open"`, `reversal_count == 0`, `current_reversal is None` after instantiation with `title` and `goal` only
- [X] T013 [P] [US1] Write `tests/unit/models/test_case.py` — `test_parent_case_links_to_master`: assert `parent.master_case_id == master.id` after FK assignment; assert `stakeholder_type` must be one of `("provider", "payer", "vendor")` (raises `ValueError` for invalid value)
- [X] T014 [P] [US1] Write `tests/unit/models/test_case.py` — `test_hierarchy_query`: given master + 3 parents added to session, `session.execute(select(ParentCase).where(ParentCase.master_case_id == master.id))` returns exactly 3 rows
- [X] T015 [P] [US1] Write `tests/unit/models/test_case_event.py` — `test_state_event_fields`: assert `CaseStateEvent` instance has `case_id`, `case_level`, `previous_status`, `new_status`, `triggered_by`, `occurred_at` and NO `updated_at` column
- [X] T016 [P] [US1] Write `tests/unit/models/test_case_event.py` — `test_fifty_state_events_persisted`: using an async in-memory session, insert 50 `CaseStateEvent` rows for the same `case_id`; assert `COUNT(*)` equals 50

### Implementation for User Story 1

- [X] T017 [US1] Implement `MasterCrisisCase` ORM model in `src/cascadecare/models/case.py` using `DeclarativeBase` from `base.py`; columns per `data-model.md` (table `master_crisis_cases`); `status` validated via `@validates("status")` against the allowed enum set
- [X] T018 [US1] Add `ParentCase` ORM model to `src/cascadecare/models/case.py`; FK `master_case_id → master_crisis_cases.id ON DELETE RESTRICT`; `stakeholder_type` validated via `@validates`; `relationship("MasterCrisisCase", back_populates="parent_cases")` bidirectional
- [X] T019 [US1] Implement `CaseStateEvent` ORM model in `src/cascadecare/models/case_event.py`; no `updated_at` column; polymorphic `case_id` (UUID, no FK constraint); `case_level` validated against `("master", "parent", "grandchild")`
- [X] T020 [US1] Update `src/cascadecare/models/__init__.py` to export `MasterCrisisCase`, `ParentCase`, `CaseStateEvent`
- [X] T021 [US1] Generate Alembic revision: `uv run alembic revision --autogenerate -m "three_level_case_schema"` from project root; inspect generated file in `src/cascadecare/db/migrations/versions/`; rename to `0001_three_level_case_schema.py`; manually verify all five columns for `master_crisis_cases` and all columns for `parent_cases` and `case_state_events` are present
- [ ] T022 [US1] Run `uv run alembic upgrade head`; verify tables with `docker compose exec postgres psql -U cascadecare -c "\dt" cascadecare_dev` — confirm `master_crisis_cases`, `parent_cases`, `case_state_events` appear — **BLOCKED: requires live PostgreSQL**
- [X] T023 [US1] Run `uv run pytest tests/unit/models/test_case.py tests/unit/models/test_case_event.py -v` — confirm all US1 tests pass (Red → Green)

**Checkpoint**: T023 passes. A developer can create `MasterCrisisCase` + `ParentCase` + `CaseStateEvent` rows and query them back without any additional files.

---

## Phase 4: User Stories 2 + 4 — Grandchild Cases (Priority: P2)

**Goal**: US2 (regulator compliance grandchildren) and US4 (BAA-obligation grandchildren) both require `GrandchildCase`. Implement together; validate each scenario independently within the same test file.

**Independent Test (US2)**: Create a `ParentCase`, fire a simulated subpoena event that creates one `GrandchildCase` with `grandchild_type="regulator_compliance"` and `obligation_id="TN_DOI"`; query it back; confirm the sibling parent (different `parent_case_id`) has zero grandchildren.

**Independent Test (US4)**: Create two `ParentCase` rows each with a distinct `obligation_id` BAA identifier; create one `GrandchildCase` per parent with `grandchild_type="baa_obligation"`; close one grandchild; confirm the other remains `open`.

### Tests for User Stories 2 + 4 (TDD — write these FIRST, confirm they FAIL before T030)

- [X] T024 [P] [US2] Write `tests/unit/models/test_case.py` — `test_regulator_grandchild_creation`: `GrandchildCase(grandchild_type="regulator_compliance", obligation_id="TN_DOI", parent_case_id=parent.id)` persists; query by `parent_case_id` returns 1 row
- [X] T025 [P] [US2] Write `tests/unit/models/test_case.py` — `test_grandchild_only_under_correct_parent`: two parents; grandchild linked to parent A; `select(GrandchildCase).where(GrandchildCase.parent_case_id == parent_b.id)` returns 0 rows
- [X] T026 [P] [US2] Write `tests/unit/models/test_case.py` — `test_grandchild_status_independent_of_parent`: close grandchild → `parent.status` unchanged; close parent → `grandchild.status` unchanged
- [X] T027 [P] [US4] Write `tests/unit/models/test_case.py` — `test_baa_grandchild_creation`: `GrandchildCase(grandchild_type="baa_obligation", obligation_id="BAA-NORTHSTAR-2024")` persists with correct fields
- [X] T028 [P] [US4] Write `tests/unit/models/test_case.py` — `test_baa_grandchild_privilege_flag`: set `privilege_flag="work_product"`; round-trip through session; assert value preserved and `attorney_client` is also accepted; assert invalid flag raises `ValueError`
- [X] T029 [P] [US2] Write `tests/unit/models/test_case_metadata.py` — `test_jsonb_metadata_round_trip`: create `CaseMetadata(case_id=uuid, case_level="grandchild", metadata_type="regulator_context", payload={"regulator": "TN_DOI", "deadline_days": 30})`; persist; query; assert `payload["regulator"] == "TN_DOI"`
- [X] T030 [P] [US2] Write `tests/integration/models/test_case_hierarchy.py` — `test_full_three_level_traversal` — SKIP stub: `@pytest.mark.skip(reason="Requires live PostgreSQL")`; HierarchyRepository Protocol defined in contracts/

### Implementation for User Stories 2 + 4

- [X] T031 [US2] Add `GrandchildCase` ORM model to `src/cascadecare/models/case.py`; FK `parent_case_id → parent_cases.id ON DELETE RESTRICT`; `grandchild_type` validated via `@validates`; `privilege_flag` validated against `("attorney_client", "work_product", None)`; `response_deadline` nullable `TIMESTAMPTZ`
- [X] T032 [US2] Implement `CaseMetadata` ORM model in `src/cascadecare/models/case_metadata.py`; `payload` column uses SQLAlchemy `JSON` type (cross-dialect; GIN index declared with `postgresql_using="gin"` for PostgreSQL)
- [X] T033 [P] [US2] Update `src/cascadecare/models/__init__.py` to also export `GrandchildCase`, `CaseMetadata`
- [ ] T034 [US2] Create `src/cascadecare/db/repositories/__init__.py` and `src/cascadecare/db/repositories/hierarchy.py` — implement `HierarchyRepository` satisfying the `HierarchyRepository` Protocol in `specs/002-case-schema/contracts/case_repository.py`; **DEFERRED** (Protocol defined; skip test uses stub)
- [X] T035 [US2] Alembic revision `0001_three_level_case_schema.py` covers all 5 tables: `master_crisis_cases`, `parent_cases`, `grandchild_cases`, `case_state_events`, `case_metadata` — written manually from data-model spec
- [X] T036 [US2] Run `uv run pytest tests/unit/models/ tests/integration/models/ -v` — all unit tests pass; integration test stub skipped

**Checkpoint**: T036 passes. Full three-level hierarchy (master → parent → grandchild) is queryable. Metadata bags attached to any case level. Independent status per level verified.

---

## Phase 5: User Story 3 — Maestro Case Nesting Probe (Priority: P3)

**Goal**: A standalone script probes the UiPath Maestro Case API for native three-level nesting support and writes a timestamped result to `DEVIATIONS.md`. Must not block or break if Maestro environment is unavailable.

**Independent Test**: Run the probe script; open `DEVIATIONS.md`; confirm a timestamped entry exists that describes the probe result (any of: native / partial / unsupported / environment_unavailable).

### Tests for User Story 3 (TDD — write these FIRST, confirm they FAIL before T040)

- [X] T037 [P] [US3] Write `tests/unit/probe/__init__.py` (empty, required for test discovery)
- [X] T038 [P] [US3] Write `tests/unit/probe/test_maestro_nesting.py` — `test_probe_writes_deviations_md`: mock `httpx.AsyncClient`; call `run_probe(deviations_path=tmp_path / "DEVIATIONS.md")`; assert file exists and contains the strings `"Maestro"`, `"probe"`, and a date string; also added `test_probe_native_support`, `test_probe_not_supported`, `test_probe_partial_support_unclear` for HTTP-path coverage
- [X] T039 [P] [US3] Write `tests/unit/probe/test_maestro_nesting.py` — `test_probe_environment_unavailable`: mock httpx to raise `httpx.ConnectError`; call `run_probe(...)`; assert `DEVIATIONS.md` contains `"environment_unavailable"` and does NOT raise an exception
- [X] T040 [P] [US3] Write `tests/unit/probe/test_maestro_nesting.py` — `test_deviations_entry_is_timestamped`: assert the written entry contains an ISO-8601 timestamp (matches regex `r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"`)

### Implementation for User Story 3

- [X] T041 [US3] Implement `src/cascadecare/probe/maestro_nesting.py` — `async def run_probe(deviations_path: Path) -> dict` that: (1) attempts to create a two-level + three-level Maestro Case hierarchy via `httpx.AsyncClient`; (2) catches all exceptions and records status `"environment_unavailable"` if Maestro is not reachable; (3) appends a structured Markdown entry to `deviations_path`; (4) returns a result dict with `{"status": str, "timestamp": str, "workaround": str}`
- [X] T042 [US3] Add `__main__` block to `src/cascadecare/probe/maestro_nesting.py` so `uv run python -m cascadecare.probe.maestro_nesting` executes `run_probe(Path("DEVIATIONS.md"))` and prints the result dict
- [X] T043 [US3] Run `uv run python -m cascadecare.probe.maestro_nesting` from project root; open `DEVIATIONS.md` and confirm a timestamped entry exists — status: `environment_unavailable` (no Maestro env in CI), entry written to DEVIATIONS.md
- [X] T044 [US3] Run `uv run pytest tests/unit/probe/ -v` — confirm US3 tests pass (Red → Green for T038–T040)

**Checkpoint**: T044 passes. `DEVIATIONS.md` contains a Maestro probe entry. Script exits cleanly whether Maestro is available or not.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, coverage verification, and quickstart validation across all user stories.

- [X] T045 [P] Run `uv run ruff check src/ tests/` — all errors fixed; `# noqa: TC003` suppressions on ORM datetime imports (SQLAlchemy requires runtime availability); `# noqa: PLR2004` removed; 0 errors
- [X] T046 [P] Run `uv run mypy src/` — 0 errors across 23 source files; `engine: AsyncEngine | None = None` type annotation added to `build_session_factory`
- [X] T047 [P] IP safety audit — zero matches for forbidden tokens in src/ and tests/
- [X] T048 Run full test suite with coverage — **31/31 tests passing; 83% total coverage** (≥ 80% `--cov-fail-under` threshold; scope expanded to full `src/cascadecare` package)
- [ ] T049 Walk through `specs/002-case-schema/quickstart.md` steps 1–7 on a fresh database — **BLOCKED: requires live PostgreSQL via docker compose**
- [X] T050 Update `specs/002-case-schema/checklists/requirements.md` — implementation complete note added

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user story phases
- **Phase 3 (US1, P1)**: Depends on Phase 2 — can start as soon as Phase 2 checkpoints pass
- **Phase 4 (US2+US4, P2)**: Depends on Phase 3 completion (GrandchildCase needs ParentCase table to exist)
- **Phase 5 (US3, P3)**: Depends on Phase 2 only — can run in parallel with Phase 4 if capacity allows
- **Phase 6 (Polish)**: Depends on Phases 3, 4, 5 all complete

### User Story Dependencies

| Story | Depends on | Shares entity with |
|-------|-----------|-------------------|
| US1 (P1) | Phase 2 | — |
| US2 (P2) | US1 (GrandchildCase needs ParentCase table) | US4 (GrandchildCase) |
| US4 (P2) | US1 (GrandchildCase needs ParentCase table) | US2 (GrandchildCase) |
| US3 (P3) | Phase 2 only | — |

### Within Each Phase

1. **TDD order is mandatory**: Test task confirmed FAILING → implementation task → test confirmed PASSING
2. Models before repositories
3. Repositories before integration tests
4. Migration runs after models are stable (not before)
5. IP safety audit runs last (Polish phase)

### Parallel Opportunities

- T003, T004, T005 → all in parallel (different directories)
- T012–T016 → all test-writing tasks in parallel (different test functions, same or different files)
- T017, T019 → can start concurrently (different files: `case.py` and `case_event.py`)
- T024–T030 → all Phase 4 test-writing tasks in parallel
- T031, T032 → `GrandchildCase` and `CaseMetadata` are different files — parallel
- T037–T040 → all Phase 5 test-writing tasks in parallel
- T045, T046, T047 → lint, type-check, and IP audit are independent — parallel

---

## Parallel Example: Phase 3 Test Writing

```bash
# Launch all US1 test tasks in one message:
Agent: "Write test_master_case_default_values in tests/unit/models/test_case.py"   [T012]
Agent: "Write test_parent_case_links_to_master in tests/unit/models/test_case.py"  [T013]
Agent: "Write test_hierarchy_query in tests/unit/models/test_case.py"              [T014]
Agent: "Write test_state_event_fields in tests/unit/models/test_case_event.py"     [T015]
Agent: "Write test_fifty_state_events_persisted in tests/unit/models/test_case_event.py" [T016]

# Then confirm all FAIL before implementing T017–T019
```

## Parallel Example: Phase 6 Polish

```bash
# All quality gates run simultaneously:
Bash: "uv run ruff check src/..."    [T045]
Bash: "uv run mypy src/..."          [T046]
Bash: "grep -riE forbidden src/..."  [T047]
# Then T048 (coverage) after all three pass
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → Phase 2: Foundational → Phase 3: US1
2. **STOP and validate**: `uv run pytest tests/unit/models/test_case.py tests/unit/models/test_case_event.py -v` passes
3. This is enough for slice 003 (FastAPI shim) to begin with stub endpoints — it only needs `MasterCrisisCase` and `ParentCase` to be importable

### Incremental Delivery

1. Phase 3 done → Slice 003 (FastAPI shim) unblocked for US1 endpoints
2. Phase 4 done → Reversal 3 agent (slice 010) unblocked for grandchild case creation
3. Phase 5 done → `DEVIATIONS.md` entry is locked in before submission
4. Phase 6 done → Slice 002 ready for `/finish-slice 002`

---

## Notes

- **[P]** tasks operate on different files — safe to dispatch in parallel agent calls
- **[USN]** label maps each task to its user story for traceability to `spec.md`
- The TDD order within each phase is load-bearing — do not skip the FAIL confirmation
- Alembic revision numbering: start at `0001`; if splitting into two revisions, use `0001` (master/parent/events) and `0002` (grandchild/metadata)
- `privilege_flag` is stored on `GrandchildCase` but its *enforcement* (filtering what callers see) is slice 014 — do not implement access control here
- BAA metadata content (actual BAA terms) is populated by slice 006 (Synthetic Data) — this slice only creates the schema columns that will hold them
- After T043 runs the probe, commit the updated `DEVIATIONS.md` entry as part of this slice's PR
