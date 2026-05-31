# Data Model: Three-Level Case Schema

**Phase**: 1 | **Date**: 2026-05-25 | **Research**: [research.md](./research.md)

---

## Entity Relationship Overview

```
master_crisis_cases (1)
  │
  ├── parent_cases (many, via master_case_id FK)
  │     │
  │     └── grandchild_cases (many, via parent_case_id FK)
  │
case_state_events (many per case at any level, via polymorphic case_id + case_level)
case_metadata     (many per case at any level, via polymorphic case_id + case_level)
```

---

## Table: `master_crisis_cases`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Stable identifier across all references |
| `title` | `VARCHAR(255)` | NOT NULL | Human-readable crisis title |
| `goal` | `TEXT` | NOT NULL | Current master goal statement (updated on reversals) |
| `status` | `VARCHAR(50)` | NOT NULL, CHECK in enum | `open` \| `in_progress` \| `escalated` \| `closed` |
| `reversal_count` | `INTEGER` | NOT NULL, default 0 | How many goal reversals have occurred |
| `current_reversal` | `TEXT` | NULLABLE | Short description of the current reversal |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Immutable creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Updated on every status/goal change |

**Indexes**: PK on `id`; index on `status`

**Enum values for `status`**: `open`, `in_progress`, `escalated`, `closed`

---

## Table: `parent_cases`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `master_case_id` | `UUID` | NOT NULL, FK → `master_crisis_cases.id` ON DELETE RESTRICT | Links to the master crisis |
| `stakeholder_name` | `VARCHAR(255)` | NOT NULL | e.g., "Northstar Regional Health" |
| `stakeholder_type` | `VARCHAR(50)` | NOT NULL, CHECK in enum | `provider` \| `payer` \| `vendor` |
| `goal` | `TEXT` | NOT NULL | Current goal for this stakeholder relationship |
| `status` | `VARCHAR(50)` | NOT NULL, CHECK in enum | Same enum as master |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: PK on `id`; index on `master_case_id`; index on `(master_case_id, status)`

**Enum values for `stakeholder_type`**: `provider`, `payer`, `vendor`

---

## Table: `grandchild_cases`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `parent_case_id` | `UUID` | NOT NULL, FK → `parent_cases.id` ON DELETE RESTRICT | Links to parent stakeholder case |
| `grandchild_type` | `VARCHAR(50)` | NOT NULL, CHECK in enum | `baa_obligation` \| `regulator_compliance` \| `investigation` |
| `obligation_id` | `VARCHAR(255)` | NOT NULL | BAA identifier, regulator name, or investigation ID |
| `status` | `VARCHAR(50)` | NOT NULL, CHECK in enum | Same status enum |
| `privilege_flag` | `VARCHAR(50)` | NULLABLE | `attorney_client` \| `work_product` \| NULL |
| `response_deadline` | `TIMESTAMPTZ` | NULLABLE | Regulatory or BAA response deadline |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: PK on `id`; index on `parent_case_id`; index on `(parent_case_id, grandchild_type)`

**Enum values for `grandchild_type`**: `baa_obligation`, `regulator_compliance`, `investigation`

**Enum values for `privilege_flag`**: `attorney_client`, `work_product`

---

## Table: `case_state_events`

> Append-only. No UPDATE or DELETE operations permitted via application layer.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `case_id` | `UUID` | NOT NULL | The case that transitioned (any level) |
| `case_level` | `VARCHAR(20)` | NOT NULL, CHECK in enum | `master` \| `parent` \| `grandchild` |
| `previous_status` | `VARCHAR(50)` | NOT NULL | Status before transition |
| `new_status` | `VARCHAR(50)` | NOT NULL | Status after transition |
| `triggered_by` | `VARCHAR(255)` | NOT NULL | Agent name, operator ID, or `system` |
| `note` | `TEXT` | NULLABLE | Free-text explanation |
| `occurred_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | Immutable; no `updated_at` column |

**Indexes**: PK on `id`; index on `(case_id, case_level)`; index on `occurred_at` DESC

**Note**: No FK constraint on `case_id` (polymorphic across three tables). Application layer enforces referential integrity and validates `case_level` matches the target table.

---

## Table: `case_metadata`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | |
| `case_id` | `UUID` | NOT NULL | Case at any level |
| `case_level` | `VARCHAR(20)` | NOT NULL, CHECK in enum | `master` \| `parent` \| `grandchild` |
| `metadata_type` | `VARCHAR(100)` | NOT NULL | e.g., `baa_terms`, `regulator_context`, `insurer_policy` |
| `payload` | `JSONB` | NOT NULL | Typed JSON blob; schema validated at application layer |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` | |

**Indexes**: PK on `id`; GIN index on `payload`; index on `(case_id, case_level, metadata_type)`

---

## State Transition Rules

```
open ──────────────────────────────► in_progress
open ──────────────────────────────► closed (e.g., false positive, no action needed)
in_progress ───────────────────────► escalated
in_progress ───────────────────────► closed
escalated ─────────────────────────► in_progress (de-escalation)
escalated ─────────────────────────► closed
```

**Invariants**:
- A grandchild case can only be created if its parent case is NOT `closed`.
- A parent case can only be created if its master case is NOT `closed`.
- Status is independent across levels — master `open` does not force parent `open`.
- A case state event MUST be written in the same transaction as any status change.

---

## Sample Hierarchy (Demo Scenario)

```
MasterCrisisCase
  id: "crisis-001"
  title: "ClearFlow Multi-Provider Cyber Cascade"
  goal: "Determine if ClearFlow is the breach vector"
  status: in_progress
  reversal_count: 1

  ParentCase [provider]
    id: "parent-northstar-001"
    stakeholder_name: "Northstar Regional Health"
    stakeholder_type: provider
    status: in_progress

    GrandchildCase [baa_obligation]
      id: "gc-northstar-baa-001"
      grandchild_type: baa_obligation
      obligation_id: "BAA-NORTHSTAR-2024"
      status: open
      privilege_flag: work_product

    GrandchildCase [regulator_compliance]
      id: "gc-northstar-tn-doi-001"
      grandchild_type: regulator_compliance
      obligation_id: "TN_DOI"
      status: open
      response_deadline: 2026-07-25T00:00:00Z

  ParentCase [payer]
    id: "parent-apex-001"
    stakeholder_name: "Apex Health Plan"
    stakeholder_type: payer
    status: open

  ParentCase [vendor]
    id: "parent-nimbus-001"
    stakeholder_name: "Nimbus Patient Engagement Platform"
    stakeholder_type: vendor
    status: open
```

---

## Validation Rules

| Rule | Enforced At |
|------|-------------|
| `status` must be in the allowed enum | DB CHECK + SQLAlchemy validator |
| `grandchild_type` must be in allowed enum | DB CHECK + SQLAlchemy validator |
| Parent case must exist before grandchild created | FK constraint + service layer guard |
| Master case must exist before parent created | FK constraint |
| State events must be written with status updates | Service layer, tested by unit test |
| `case_level` in events/metadata must match actual table | Application layer guard |
| `privilege_flag` only on `grandchild_cases` | Model design (column absent from other tables) |
