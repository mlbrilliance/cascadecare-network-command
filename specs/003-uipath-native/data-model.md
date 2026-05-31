# Spec 003: Data Model

## Persistence boundary

**State of record is the UiPath cloud.** There is no relational database in this project. Case state lives in Maestro Case. Reference data and synthetic claim telemetry live in Data Fabric. BAA documents and indexable text live in Context Grounding (over Data Fabric).

The data shapes below describe what the AI coding agents must create when seeding Data Fabric in Slice 005.

## Data Fabric entities

### Provider

Represents a healthcare provider customer of ClearFlow Health Network.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "northstar", "alpha", "beta", "gamma", "delta", "epsilon" |
| `display_name` | string | "Northstar Regional Health", etc. |
| `vertical` | string | "academic", "rural", "for_profit_chain", "specialty_surgical", "childrens" |
| `hospital_count` | int | Northstar=7; others=1 |
| `npi_count` | int | synthetic — number of clinicians; range 50–5000 |
| `monthly_claim_volume` | int | synthetic — range 10k–500k |
| `monthly_revenue_band` | string | "small", "medium", "large", "enterprise" |
| `risk_profile` | string | "primary_care_dominant", "high_acuity", "surgical_concentrated", "pediatric" |
| `baa_id` | string | FK to BAA |
| `business_continuity_runway_days` | int | how many days they can sustain claim flow disruption — Northstar=45, Alpha=60, Beta=10, Gamma=30, Delta=20, Epsilon=15 |

Seed 6 providers.

### Payer

Represents a payer (health plan) in the cascade.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "apex", "summitblue", "union-prairie", "lakeshore" |
| `display_name` | string | "Apex Health Plan", etc. |
| `payer_type` | string | "commercial", "medicare_advantage", "tpa", "self_funded_admin" |
| `activity_level` | string | "active_antagonist", "active_federal", "named_only", "named_only" |
| `regulatory_jurisdiction` | string | "multi_state", "federal", "state", "state" |
| `outstanding_payments_band` | string | "small", "medium", "large", "very_large" |

Seed 4 payers (Apex + SummitBlue are active, Union Prairie + Lakeshore are named-only for narrative texture).

### Vendor

Represents the attack vector (Nimbus Patient Engagement Platform).

| Field | Type | Notes |
|---|---|---|
| `id` | string | "nimbus" |
| `display_name` | string | "Nimbus Patient Engagement Platform" |
| `vendor_type` | string | "patient_engagement_saas" |
| `connected_providers` | array<string> | provider ids using Nimbus — all 6 |
| `breach_evidence_signal_strength` | string | "weak" → "moderate" → "strong" as story progresses |

Seed 1 vendor.

### Regulator

Represents regulators that can issue inquiries.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "tn-doi" |
| `display_name` | string | "Tennessee Department of Insurance" |
| `regulator_type` | string | "state_insurance_dept" |
| `jurisdiction` | string | "Tennessee" |
| `subpoena_template_id` | string | FK to RegulatorTemplate |
| `response_deadline_days` | int | typically 14 |

Seed 1 regulator (TN DOI; expand to multi-state in future polish).

### Insurer

Represents ClearFlow's cyber insurer.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "aurora-specialty" |
| `display_name` | string | "Aurora Specialty" |
| `insurer_type` | string | "cyber_specialty" |
| `policy_limits_band` | string | "large" |
| `policy_directives` | array<string> | e.g., "no public statement without counsel review", "retain Northwall Forensics", "preserve all logs" |

Seed 1 insurer.

### Counsel

Represents outside counsel coordinating ClearFlow's response.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "hawthorne-mercer" |
| `display_name` | string | "Hawthorne Mercer LLP" |
| `counsel_type` | string | "cyber_breach_response" |
| `privilege_directives` | array<string> | which grandchild cases are subject to attorney-client vs work-product privilege |

Seed 1 counsel firm.

### BAA (Business Associate Agreement)

One per provider — heterogeneous on purpose, this is the core of the conflict story.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "baa-northstar", "baa-alpha", etc. |
| `provider_id` | string | FK to Provider |
| `version` | string | e.g., "2024.03" |
| `notification_window_hours` | int | varies 24–72 across providers |
| `requires_pre_disclosure_consultation` | bool | true for some providers, false for others |
| `permitted_disclosures` | array<string> | which parties ClearFlow may notify without consent |
| `forbidden_disclosures` | array<string> | which parties ClearFlow may NOT notify under any circumstance |
| `indemnification_clause` | string | clause text summary |
| `governing_law` | string | varies — TN, IL, DE, NY |
| `document_blob_url` | string | pointer to full BAA document for Context Grounding |

Seed 6 BAAs (one per provider). Engineer at least 3 distinct conflict patterns:
1. Northstar's BAA requires 24h notification but Alpha's BAA forbids notification before forensic review (conflict on Day 5)
2. Apex Health Plan demands data Alpha's BAA forbids disclosing without consent (conflict at Reversal 4)
3. SummitBlue Medicare Advantage triggers federal reporting that Beta's BAA permits but Epsilon's forbids

### ClaimTelemetry

Synthetic claim flow telemetry — feeds the Claim Flow Anomaly Detector.

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `provider_id` | string | FK to Provider |
| `period_start` | datetime | hourly buckets |
| `claim_count` | int | bucketed |
| `total_billed_amount` | decimal | |
| `anomaly_score` | float | 0.0–1.0; pre-computed for demo |
| `anomaly_flag` | bool | true after Day 1 for all 6 providers (cascade start) |

Seed 30 days × 24 hours × 6 providers = 4320 rows. Pre-engineer anomalies starting Day 1 to trigger R1.

### RegulatorTemplate

Pre-canned regulator inquiry document templates.

| Field | Type | Notes |
|---|---|---|
| `id` | string | "tn-doi-subpoena-2026" |
| `regulator_id` | string | FK to Regulator |
| `template_type` | string | "subpoena", "civil_investigative_demand", "regulatory_inquiry" |
| `legal_basis` | string | e.g., "TCA 56-7-1003 et seq." (fictional but plausible) |
| `discovery_requests` | array<string> | list of items demanded |
| `response_form_url` | string | pointer to response form for Action Center |

Seed 1 template (TN DOI subpoena). This drives the Reversal 3 hero moment.

## Context Grounding indexes

### BAA-corpus

Indexes all 6 BAA documents (`BAA.document_blob_url`). Used by:
- BAA Boundary Reasoner agent (retrieval of relevant clauses)
- Fiduciary Conflict Detector agent (cross-BAA conflict detection)

### ClaimTelemetry-corpus

Indexes claim telemetry summaries (rolled-up text representations). Used by:
- Claim Flow Anomaly Detector (cross-referencing historical patterns)
- Multi-Customer Pattern Detector (cross-provider correlation queries)

## Maestro Case variables (per case definition)

Each of the 3 caseplan.json files declares its own variables. Examples:

### Master case (`clearflow-master-crisis`)
- `master_goal` (string) — updated on each reversal
- `reversal_number` (int, 0–5)
- `clearflow_vector_status` (string) — "unknown" | "self_suspected" | "cleared" | "co_defendant"
- `current_simulated_day` (int)
- `grandchild_case_count` (int)

### Stakeholder parent case (`clearflow-stakeholder-parent`)
- `stakeholder_id` (string)
- `stakeholder_type` (string) — "provider" | "payer" | "vendor" | "regulator" | "insurer" | "counsel"
- `parent_goal` (string)
- `parent_status` (string) — "open" | "in_progress" | "escalated" | "closed"
- `master_case_id` (string) — back-ref

### Obligation grandchild case (`clearflow-obligation-grandchild`)
- `obligation_type` (string) — "baa-compliance" | "regulatory-response" | "investigation" (see case-vocabulary.yaml → variables.obligation_grandchild.var_obligation_type)
- `obligation_id` (string)
- `privilege_flag` (string) — "attorney-client" | "work-product" | "operational" (see case-vocabulary.yaml → variables.stakeholder_parent.var_privilege_flag)
- `response_deadline` (datetime)
- `parent_case_id` (string) — back-ref

## Slice 013: Dashboard Payload Models (Coded App backend)

These Pydantic models are the contract between the Coded App backend and the UiPath Apps frontend.

### DashboardPayload (root)
| Field | Type | Description |
|---|---|---|
| `cascade_tree` | `CascadeTree` | Three-level case hierarchy snapshot |
| `reversal_timeline` | `list[ReversalEvent]` | Five master reversals with active flags |
| `agent_activity` | `list[AgentActivity]` | Per-agent latest status (7 agents) |
| `override_controls` | `list[OverrideControl]` | Demo operator buttons |
| `refreshed_at` | `str` | ISO-8601 timestamp |

### CascadeTree
| Field | Type |
|---|---|
| `master` | `CaseNode` |
| `parents` | `list[CaseNode]` (max 9) |
| `grandchildren` | `list[CaseNode]` (max 12) |

### CaseNode
| Field | Type |
|---|---|
| `id` | `str` |
| `display_name` | `str` |
| `stage` | `str` |
| `status` | `CaseStatus` (active/suspended/completed/pending) |
| `parent_id` | `str \| None` |
| `level` | `int` (0=master, 1=parent, 2=grandchild) |

### ReversalEvent
| Field | Type |
|---|---|
| `number` | `int` (1–5) |
| `name` | `str` |
| `day` | `int` |
| `wall_clock_seconds` | `int` |
| `goal_from` | `str` |
| `goal_to` | `str` |
| `active` | `bool` |

### AgentActivity
| Field | Type |
|---|---|
| `agent_id` | `str` |
| `display_name` | `str` |
| `agent_type` | `AgentType` (coded/builder) |
| `status` | `AgentStatus` (idle/running/completed/error) |
| `last_output` | `str \| None` |
| `invocation_count` | `int` |
| `last_invoked_at` | `str \| None` |

### OverrideControl
| Field | Type |
|---|---|
| `id` | `str` |
| `label` | `str` |
| `action` | `OverrideAction` |
| `enabled` | `bool` |
| `tooltip` | `str` |

### OverrideAction enum
`fire_reversal_1..5`, `spawn_grandchildren`, `trigger_hitl_gate`, `reset_demo`

## Forbidden content

The CLAUDE.md forbidden-token list applies to ALL Data Fabric seed content. No real company names, no real patient names, no real claim numbers, no real NPI numbers, no real litigation references. Every seed entity must pass `/audit-ip-safety` before commit.
