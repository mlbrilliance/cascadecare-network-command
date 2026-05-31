# Quickstart: Three-Level Case Schema

**Slice**: 002 | **Date**: 2026-05-25

Gets a developer from zero to a running three-level case hierarchy in under 5 minutes.

---

## Prerequisites

- Docker Desktop running (for PostgreSQL)
- `uv` installed (`pip install uv` or `brew install uv`)
- `.env` file configured (copy `.env.example`, set `DATABASE_URL`)

---

## Step 1 — Start the database

```bash
docker compose up -d postgres
```

Verify it is accepting connections:

```bash
docker compose exec postgres pg_isready -U cascadecare
# Expected: /var/run/postgresql:5432 - accepting connections
```

---

## Step 2 — Install dependencies (including Alembic)

```bash
uv sync --extra dev
```

Alembic is included in dev dependencies after slice 002. Verify:

```bash
uv run alembic --version
# Expected: alembic 1.13.x
```

---

## Step 3 — Run the Maestro Case probe (required before migrations)

```bash
uv run python -m cascadecare.probe.maestro_nesting
```

This writes a result entry to `DEVIATIONS.md` regardless of outcome. Check the output:

```bash
tail -20 DEVIATIONS.md
```

Expected: a timestamped entry describing the Maestro nesting probe result.

---

## Step 4 — Run database migrations

```bash
cd src/cascadecare/db
uv run alembic upgrade head
```

Expected output:

```
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001, three_level_case_schema
```

Verify tables exist:

```bash
docker compose exec postgres psql -U cascadecare -c "\dt" cascadecare_dev
# Expected: master_crisis_cases, parent_cases, grandchild_cases,
#           case_state_events, case_metadata
```

---

## Step 5 — Run the unit tests

```bash
uv run pytest tests/unit/models/ -v
```

Expected: all tests pass, ≥90% line coverage reported.

---

## Step 6 — Run the integration tests

```bash
uv run pytest tests/integration/models/ -v
```

This exercises the full hierarchy traversal against the real PostgreSQL instance started in Step 1.

---

## Step 7 — Verify IP safety

```bash
# From project root
/audit-ip-safety
# or:
grep -riE "zelis|aetna|cigna|unitedhealth|bcbs|change healthcare|optum|cotiviti|wex" \
  src/cascadecare/models/ tests/unit/models/ tests/integration/models/
# Expected: no matches
```

---

## What was created

| Path | Purpose |
|------|---------|
| `src/cascadecare/models/base.py` | SQLAlchemy `DeclarativeBase` |
| `src/cascadecare/models/case.py` | ORM models: MasterCrisisCase, ParentCase, GrandchildCase |
| `src/cascadecare/models/case_event.py` | ORM model: CaseStateEvent (append-only) |
| `src/cascadecare/models/case_metadata.py` | ORM model: CaseMetadata (JSONB) |
| `src/cascadecare/db/engine.py` | Async engine factory |
| `src/cascadecare/db/session.py` | AsyncSession context manager |
| `src/cascadecare/db/migrations/` | Alembic root + revision `0001` |
| `src/cascadecare/probe/maestro_nesting.py` | Maestro nesting probe script |
| `tests/unit/models/test_case.py` | Unit tests for core case models |
| `tests/unit/models/test_case_event.py` | Unit tests for state event log |
| `tests/unit/models/test_case_metadata.py` | Unit tests for JSONB metadata |
| `tests/integration/models/test_case_hierarchy.py` | Integration test: full hierarchy traversal |
| `DEVIATIONS.md` | Maestro probe result entry |

---

## Common issues

**`DATABASE_URL` not set**
```
pydantic_settings.BaseSettings: missing required env var DATABASE_URL
```
→ Copy `.env.example` to `.env` and fill in the value.

**Alembic `Can't locate revision` error**
→ Run `uv run alembic stamp head` to re-sync Alembic's version table, then `uv run alembic upgrade head`.

**`asyncpg` / `psycopg` driver error**
→ Ensure `psycopg[binary]` is installed: `uv add psycopg[binary]`

**Test `event loop is closed`**
→ Add `asyncio_mode = "auto"` to `pyproject.toml` under `[tool.pytest.ini_options]`.
