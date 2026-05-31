# ARCHIVED: specs/002-case-schema

**Archived**: 2026-05-26
**Reason**: Project trajectory pivoted to pure-UiPath. This spec described a PostgreSQL-mirrored, Python-orchestrated 3-level case schema. That architecture has been superseded.

## What replaced it

`specs/003-uipath-native/` — pure-UiPath architecture where Maestro Case is canonical case state, three caseplan.json files realize 3-level nesting via the native `case-management` task type, agents run inside UiPath (4 Agent Builder + 3 Coded Agents), mocks live in Data Fabric with API Workflow fronts, and a Maestro Flow Demo Driver fires events at compressed intervals against real-time Maestro Triggers.

## Why this content is kept (not deleted)

- Evidence of the design exploration that led to the pure-UiPath posture
- Some data-model concepts (Provider, Payer, Vendor, Regulator categorization; BAA term modeling; reversal taxonomy) inform the new Data Fabric entities even though the persistence layer is different
- Compliance with software-archaeology hygiene — don't lose history

## Do NOT

- Implement against any contracts in `contracts/case_repository.py` — those targeted SQLAlchemy and are obsolete
- Run any migrations referenced in `plan.md` — Alembic is removed from the project
- Treat any test files referenced here as canonical — the tests at `tests/unit/models/` and `tests/integration/models/` were deleted as part of Slice 004

## See also

- `/home/webfiji/.claude/plans/the-project-trajectory-has-radiant-knuth.md` — the approved trajectory plan with all 13 architectural decisions
- `CLAUDE.md` — updated project conventions (post-pivot)
- `DEVIATIONS.md` — Studio Web upload blocker resolution
