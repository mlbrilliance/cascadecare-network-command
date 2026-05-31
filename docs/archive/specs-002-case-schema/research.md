# Research: Three-Level Case Schema

**Phase**: 0 | **Date**: 2026-05-25 | **Plan**: [plan.md](./plan.md)

---

## Decision 1: Hierarchy representation — separate tables vs. self-referential

**Decision**: Three separate ORM tables (`master_crisis_cases`, `parent_cases`, `grandchild_cases`) with explicit FK columns.

**Rationale**:
- Each level carries genuinely different columns (e.g., `stakeholder_type` only on parent; `obligation_type`, `privilege_flag`, `response_deadline` only on grandchild). Forcing all into one table would require nullable columns at every level — an EAV smell.
- Three explicit tables make the architecture self-documenting and match the Constitution's language exactly.
- A single self-referential `cases` table with a `level` discriminator (Adjacency List pattern) would be simpler to migrate to four levels, but the spec explicitly says four levels will never exist. Premature flexibility is not worth the cost in clarity here.
- SQLAlchemy's `relationship()` with explicit FK columns makes eager-loading all three levels in one query straightforward via `joinedload`.

**Alternatives considered**:
- **Self-referential / Adjacency List**: Single `cases` table, `parent_id` nullable FK pointing to same table. Simpler schema, harder to enforce level-specific constraints at the DB layer. Rejected because level-specific columns would all be nullable — schema doesn't enforce invariants.
- **Nested Set / Closure Table**: Supports arbitrary depth, enables efficient subtree queries. Overkill for a fixed three-level demo; adds update complexity. Rejected.
- **Materialized Path**: Store full path as string (e.g., `master-uuid/parent-uuid/grandchild-uuid`). Simple reads, complex updates, no FK referential integrity. Rejected.

---

## Decision 2: Metadata extensibility — JSONB column vs. separate EAV table

**Decision**: `JSONB` column (`payload`) on a `case_metadata` join table, with a `metadata_type` discriminator string.

**Rationale**:
- PostgreSQL `JSONB` is indexed, queryable with `->>` operators, and does not require schema changes when a new metadata type is added.
- A separate `CaseMetadata` table (with `case_id`, `case_level`, `metadata_type`, `payload JSONB`) keeps the three core case tables clean while allowing arbitrary metadata extension.
- Alembic migrations for new metadata *types* require zero schema changes — only application-layer changes to the Pydantic model for that type.
- This satisfies FR-007 (typed metadata bags without schema changes) without requiring an EAV pattern.

**Alternatives considered**:
- **Inline JSONB column on each case table**: Simpler, but bloats the core tables and makes type-level validation harder. Rejected.
- **EAV (key-value rows)**: Maximum flexibility, zero schema changes. Loses type safety, makes queries painful. Rejected.
- **Polymorphic SQLAlchemy inheritance** (concrete / joined table): Would require a migration per new metadata type. Rejected.

---

## Decision 3: CaseStateEvent — append-only vs. mutable status column

**Decision**: Mutable `status` column on each case table **plus** an append-only `case_state_events` log table.

**Rationale**:
- The mutable `status` column satisfies O(1) current-status lookups without a subquery.
- The append-only `CaseStateEvent` table satisfies FR-008 (every transition logged) and FR-013 (ancestor chain query) and VI (Evidence Provenance).
- The log is written in the same transaction as the status update — no eventual consistency risk.
- `CaseStateEvent` rows are never updated or deleted (immutable by application convention; `updated_at` column omitted intentionally).

**Alternatives considered**:
- **Status-column only**: Loses history. Rejected (FR-008 explicit requirement).
- **Event-sourcing only (no mutable column)**: Current status derived from event log. Clean but O(n) for current-status reads. Too slow for frequent dashboard polling. Rejected.

---

## Decision 4: Alembic for migrations

**Decision**: Add `alembic>=1.13` to `pyproject.toml` dev dependencies; configure with async engine support.

**Rationale**:
- Alembic is the de-facto SQLAlchemy migration tool. Already implied by the project stack.
- `alembic upgrade head` is idempotent when run against an already-migrated DB (FR-012).
- Async-mode Alembic (`run_sync` inside `async_engine_from_config`) works with the existing `psycopg` async driver.
- One revision file per slice (`0001_three_level_case_schema.py`) keeps history clean.

**Alternatives considered**:
- **Manual SQL scripts**: No downgrade support, no revision tracking. Rejected.
- **SQLAlchemy `create_all()`**: Not suitable for production-like demo environments; cannot represent schema history. Rejected.

---

## Decision 5: Maestro Case probe approach

**Decision**: A standalone Python script (`src/cascadecare/probe/maestro_nesting.py`) that attempts to create a two-level case hierarchy via the Maestro Case REST API (or SDK), then attempts to create a third-level case as a child of the second-level case. Result (success / partial / unsupported / environment unavailable) is written to `DEVIATIONS.md`.

**Rationale**:
- The probe must be runnable before migrations and independently of the agent runtime.
- `httpx` (already in deps) is sufficient for REST calls.
- If the Maestro Case environment is not configured (no credentials in `.env`), the probe exits cleanly with status `environment_unavailable` and logs that status — it never blocks the migration.
- The probe result does not change the implementation (PostgreSQL fallback is used regardless), but it is required for honest architectural documentation (FR-011).

**Alternatives considered**:
- **UiPath Python SDK**: Would require adding a new dependency; the SDK may not be available in CI. Rejected.
- **Skipping probe entirely**: Violates FR-011 and Constitution V (log workarounds in DEVIATIONS.md). Rejected.

---

## Decision 6: SQLAlchemy async vs. sync

**Decision**: Use SQLAlchemy 2.0 **async** engine and `AsyncSession` throughout.

**Rationale**:
- The shim (slice 003) is FastAPI with `async def` endpoints. Sync SQLAlchemy inside async FastAPI requires `run_in_executor` wrapping — an antipattern.
- `psycopg[binary]` v3 natively supports the SQLAlchemy async interface.
- All tests run with `pytest-asyncio` (already in dev deps).
- Alembic migrations themselves run synchronously via `run_sync(conn.run_sync(Base.metadata.create_all))` — this is the standard Alembic async pattern.

**Alternatives considered**:
- **Sync SQLAlchemy**: Simpler, but requires thread pool hacks in FastAPI. Rejected.

---

## Resolved Clarifications

No `[NEEDS CLARIFICATION]` markers were present in the spec. All decisions above were informed by the project's CLAUDE.md tech stack, pyproject.toml dependencies, and Constitution.
