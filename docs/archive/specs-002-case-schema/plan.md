# Implementation Plan: Three-Level Case Schema

**Branch**: `master` | **Date**: 2026-05-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-case-schema/spec.md`

---

## Summary

Implement the PostgreSQL-backed three-level case hierarchy (master crisis case → per-stakeholder parent case → per-obligation grandchild case) that underpins every agent, UI panel, and reversal event in the CascadeCare demo. The implementation is SQLAlchemy ORM models with Alembic migrations. A lightweight Maestro Case probe script runs before migrations and writes its result to `DEVIATIONS.md`. All source files are preceded by their test files (TDD-First, per Constitution).

---

## Technical Context

**Language/Version**: Python 3.12 (managed by uv)

**Primary Dependencies**:
- `sqlalchemy>=2.0` — ORM; DeclarativeBase + mapped_column pattern
- `alembic>=1.13` — migration management (to be added to pyproject.toml)
- `psycopg[binary]>=3.2` — async-capable PostgreSQL driver (already in deps)
- `pydantic>=2.9` — model validation and serialisation (already in deps)
- `httpx>=0.27` — Maestro Case probe HTTP calls (already in deps)

**Storage**: PostgreSQL 16 (Docker Compose service from slice 001)

**Testing**: pytest 8.3 + pytest-asyncio + pytest-cov (all present in dev deps)

**Target Platform**: Linux server (Docker Compose local; CI GitHub Actions)

**Project Type**: Library — ORM models + migration scripts consumed by all upstream slices

**Performance Goals**: Full three-level hierarchy traversal (1 master + 9 parents + ≤18 grandchildren) in <500 ms locally; state-event log write in <50 ms

**Constraints**:
- No secrets in committed files (DB URL via `.env`)
- `knowledge/` directory is immutable — no writes
- Test file must exist before any source file in `agents/`, `shim/`, `mocks/` (pre-write hook enforces)
- Files under 500 lines (Constitution IV)
- Alembic migrations must be idempotent

**Scale/Scope**: Demo dataset only — 1 master, 9 parents, ≤18 grandchildren, ≤90 state events per demo run

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. TDD-First | ✅ MUST PASS | `tests/unit/models/test_case.py` created before `src/cascadecare/models/case.py`. Pre-write hook enforces. |
| II. IP Safety | ✅ PASS | All entity names are fictional (ClearFlow, Northstar, Apex, etc.). No forbidden tokens. |
| III. Externalized Prompts | ✅ N/A | No agent prompt files in this slice. |
| IV. Surgical Edits | ✅ PASS | New files created; only `pyproject.toml` and `CLAUDE.md` modified (both read first). |
| V. Three-Level Nesting | ✅ CORE | This slice *is* the implementation of this principle. |
| VI. Evidence Provenance | ✅ FOUNDATION | `CaseStateEvent` captures source case, source actor, and timestamp. Confidence field included at the metadata layer. |
| VII. Secrets via .env | ✅ PASS | `DATABASE_URL` in `.env` only; `config.py` reads via pydantic-settings. |
| VIII. Knowledge Immutable | ✅ PASS | `knowledge/` not touched. |

**Gate result: PASS — proceed to Phase 0.**

---

## Project Structure

### Documentation (this feature)

```text
specs/002-case-schema/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── case_repository.py   # Python Protocol interfaces
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
src/cascadecare/
├── models/
│   ├── __init__.py          # Re-export all models
│   ├── base.py              # DeclarativeBase + metadata
│   ├── case.py              # MasterCrisisCase, ParentCase, GrandchildCase
│   ├── case_event.py        # CaseStateEvent (immutable log)
│   └── case_metadata.py     # CaseMetadata (JSONB extension bag)
├── db/
│   ├── __init__.py
│   ├── engine.py            # Async engine factory; reads DATABASE_URL from env
│   ├── session.py           # AsyncSession factory + context manager
│   └── migrations/          # Alembic root
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
│           └── 0001_three_level_case_schema.py
└── probe/
    ├── __init__.py
    └── maestro_nesting.py   # Maestro Case probe + DEVIATIONS.md writer

tests/
├── unit/
│   └── models/
│       ├── __init__.py
│       ├── test_case.py         # MasterCrisisCase, ParentCase, GrandchildCase
│       ├── test_case_event.py   # CaseStateEvent immutability + log count
│       └── test_case_metadata.py  # JSONB bag round-trip
└── integration/
    └── models/
        ├── __init__.py
        └── test_case_hierarchy.py  # Full hierarchy traversal against real DB
```

**Structure Decision**: Single-project layout (backend only). Frontend (`ui/`) is slice 013. Probe script lives in `src/cascadecare/probe/` — small, scoped, deletable after demo.

---

## Complexity Tracking

No constitution violations requiring justification.
