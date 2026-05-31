# Deviations Log

Tracks intentional deviations from specification when implementation realities differ from design.

| Date | Slice | Spec Section | Deviation | Rationale | Approved By |
|------|-------|-------------|-----------|-----------|-------------|
| 2026-05-26 | 004 | All Slice 002 work | Project trajectory pivoted to pure-UiPath after AgentHack rules review | Maestro Case canvas IS the runtime; Python-orchestrated case mirror dropped | User (`/grill-with-docs` session) |
| 2026-05-26 | 003 | UiPath Publish | Studio Web upload blocker **RESOLVED** | User granted Studio Web + Maestro + Integration Service + Data Fabric + UiPath Apps + Action Center scopes to external app | User |

---

## RESOLVED: Studio Web Upload Scope — 2026-05-26

**Status**: ✅ `RESOLVED`

The external app `e7145523-3cdd-40f1-b2f2-c1b105aa217f` was granted the following scopes by the user in the UiPath Cloud Admin portal on 2026-05-26:

- Studio Web (publish)
- Maestro (full)
- Integration Service
- Data Fabric
- UiPath Apps
- Action Center

This unblocks `uip solution upload`, `uip data-fabric` operations, `uip integration-service` workflows, and Action Center HITL task management. End-to-end smoke test will occur in Slice 014 (Solution packaging + publish).

Tenant: `https://staging.uipath.com/hackathon26_042/DefaultTenant`

---

## SUPERSEDED: Maestro Case Nesting Probe — 2026-05-26

**Status**: `superseded` — by the Maestro Case Management Private Preview Guide which documents native sub-case support via the `case-management` task type.

Original finding: a probe HTTP call suggested V20 lacked native nested cases. The Private Preview Guide later clarified the probe was looking at the wrong layer; the schema-level `case-management` task type DOES support spawning sub-cases from within a stage. The current plan uses 3 caseplan.json files (master/parent/grandchild) wired via this native task type. See `specs/003-uipath-native/plan.md`.

---

## SUPERSEDED: PostgreSQL Persistence — 2026-05-26

**Status**: `superseded` — Postgres dropped entirely as of Slice 004.

Original plan stored case state in a PostgreSQL mirror alongside Maestro Case for audit, querying, and FastAPI shim purposes. The pure-UiPath posture (Decision 1) made Postgres redundant: Maestro Case is canonical for case state; Data Fabric holds reference data; Context Grounding holds indexable text. The ORM, migrations, alembic config, and related tests were deleted in Slice 004.
