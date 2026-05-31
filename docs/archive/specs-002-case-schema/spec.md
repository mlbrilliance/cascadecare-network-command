# Feature Specification: Three-Level Case Schema

**Feature Branch**: `002-case-schema`

**Created**: 2026-05-25

**Status**: Draft

**Input**: Slice 002 — Three-Level Case Schema (CascadeCare Network Command Master Build Roadmap)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Operator creates a master crisis case and watches child cases spawn beneath it (Priority: P1)

ClearFlow's crisis response team receives the first signal that multiple providers are experiencing simultaneous claim-flow drops. An operator opens the CascadeCare command center and triggers a new master crisis case. As the investigation deepens, the system automatically creates provider-level parent cases beneath the master, one per affected customer. Each parent case tracks that customer's specific situation independently while remaining linked to the shared crisis above.

**Why this priority**: The three-level hierarchy is the architectural backbone of the entire demo. Without it, no downstream agent, UI panel, or reversal event can work correctly. This story must succeed before any other story is testable.

**Independent Test**: Can be fully tested by triggering case-creation events for the master crisis and two provider parent cases, then verifying that the parent cases appear linked under the master in a query, and that each case independently holds its own status and metadata.

**Acceptance Scenarios**:

1. **Given** no active crisis exists, **When** an operator creates a new master crisis case with a unique identifier and an initial goal statement, **Then** the master case is persisted with status `open`, a creation timestamp, and zero child cases.
2. **Given** a master crisis case exists, **When** the system receives a provider-level crisis event for Northstar Regional Health, **Then** a provider parent case is created, linked to the master as its parent, and the master case's child count increments by one.
3. **Given** a master crisis case with three provider parent cases, **When** an operator queries the case hierarchy, **Then** the response returns the master case plus all three linked parent cases in a single traversal.
4. **Given** an operator deletes (closes) a parent case, **When** the master case is queried, **Then** the master case reflects the updated child count and the closed parent case remains in history with a closed status.

---

### User Story 2 — A regulator subpoena spawns grandchild cases beneath the correct provider parent (Priority: P2)

At Day 30 of the crisis, ClearFlow receives a subpoena from the Tennessee Department of Insurance. This triggers the third reversal: the system must create one grandchild compliance case per provider parent case that falls under TN DOI jurisdiction, while simultaneously leaving unaffected provider parent cases unchanged. Each grandchild case is independently trackable and holds its own regulator metadata, response deadline, and privilege flag.

**Why this priority**: Grandchild case creation is the moment the three-level nesting is stressed in a real scenario. It proves that the schema genuinely supports a third level, not just two levels with a workaround. Required for Reversal 3 to fire correctly.

**Independent Test**: Can be fully tested by creating a parent case and then issuing a simulated subpoena event that targets it, then verifying that a grandchild case appears beneath that parent with the correct regulator metadata, while a sibling parent case has no new children.

**Acceptance Scenarios**:

1. **Given** a provider parent case for Northstar Regional Health, **When** a TN DOI subpoena event is received that names Northstar as a covered entity, **Then** a grandchild compliance case is created under Northstar's parent case, linked to the parent, and tagged with `regulator: TN_DOI` and a response deadline.
2. **Given** a provider parent case for Provider Delta (specialty surgical center) that is outside TN DOI jurisdiction, **When** the same subpoena event is processed, **Then** no grandchild case is created under Provider Delta's parent case.
3. **Given** a grandchild case exists under a parent, **When** the grandchild case's status is updated to `responded`, **Then** the parent case's metadata reflects the update but the master case status is unchanged.
4. **Given** a three-level hierarchy exists (master → parent → grandchild), **When** the full hierarchy is traversed, **Then** the traversal completes in a single query and returns all three levels correctly linked.

---

### User Story 3 — The system probes Maestro Case nesting capability and logs any gaps (Priority: P3)

Before committing to the PostgreSQL-backed three-level model, the system makes one attempt to verify whether UiPath Maestro Case natively supports three-level case nesting. The result — pass or gap — is recorded in `DEVIATIONS.md` with a clear statement of what was tried and what workaround (if any) is in use. Operators and auditors can read DEVIATIONS.md to understand the architecture decision.

**Why this priority**: Required for honest reporting to the AgentHack judges and for maintaining the demo's architectural integrity. Does not block implementation because the PostgreSQL fallback is designed from the start.

**Independent Test**: Can be fully tested by reviewing `DEVIATIONS.md` after the probe runs — the file must contain a timestamped entry describing the probe outcome, regardless of whether Maestro natively supports three-level nesting.

**Acceptance Scenarios**:

1. **Given** the probe script runs against the Maestro Case API or preview environment, **When** the probe completes, **Then** `DEVIATIONS.md` is updated with: the probe date, the API endpoint or feature tested, the result (native support / partial support / not supported), and the chosen workaround.
2. **Given** Maestro does not support three-level nesting, **When** the probe result is recorded, **Then** the workaround entry in `DEVIATIONS.md` explicitly states "PostgreSQL + UI rendering fallback" and references the relevant schema file.
3. **Given** the probe result has been logged, **When** a new developer reads `DEVIATIONS.md`, **Then** they can understand the limitation and the workaround without asking anyone.

---

### User Story 4 — BAA-specific grandchild cases track per-provider legal obligations separately (Priority: P2)

Each of the six provider customers has a materially different Business Associate Agreement (BAA) with ClearFlow. When a PHI exfiltration signal arrives at Day 3, the system must create per-BAA grandchild cases under the appropriate provider parent cases. Each grandchild case carries the BAA identifier, the specific breach obligations from that BAA, and an independent status so that a BAA closure for one provider does not affect the others.

**Why this priority**: BAA-level tracking is the other primary use of the grandchild level (alongside regulator compliance). Together they validate that the grandchild case type is genuinely polymorphic and not hard-coded for one scenario.

**Independent Test**: Can be fully tested by creating two provider parent cases, each with a different BAA ID, then firing a PHI exfiltration event, and verifying that two separate grandchild BAA cases appear with distinct BAA metadata and independent statuses.

**Acceptance Scenarios**:

1. **Given** a PHI exfiltration event references Northstar Regional Health's BAA, **When** the event is processed, **Then** a grandchild BAA-obligation case is created under Northstar's parent case, tagged with Northstar's BAA identifier and the relevant breach obligation clauses.
2. **Given** separate grandchild BAA cases exist for Northstar and Provider Alpha, **When** Northstar's BAA case is closed, **Then** Provider Alpha's BAA case status remains unchanged.
3. **Given** a BAA grandchild case, **When** it is queried, **Then** the response includes the parent case ID, the master case ID, the BAA identifier, the obligation type, and the current status — in a single lookup.

---

### Edge Cases

- What happens when a grandchild case creation is attempted for a parent case that has already been closed?
- How does the system handle a duplicate master crisis case creation with the same identifier?
- What happens if the three-level hierarchy traversal encounters a cycle (malformed data)?
- How does the system behave if a grandchild case's parent case is deleted before the grandchild is resolved?
- What is the maximum number of grandchild cases a single parent case can hold without query degradation?
- How does case status propagation work when multiple grandchild cases under one parent have conflicting statuses?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST persist case records at three distinct levels: master crisis case, parent case, and grandchild case, each independently queryable and independently statusable.
- **FR-002**: The system MUST enforce parent-child relationships such that every parent case is linked to exactly one master case, and every grandchild case is linked to exactly one parent case.
- **FR-003**: The system MUST support the following case types at the parent level: provider-customer case, payer-customer case, vendor case.
- **FR-004**: The system MUST support the following case types at the grandchild level: per-BAA obligation case, per-regulator compliance case, investigation case.
- **FR-005**: Every case at every level MUST carry: unique identifier, case type, status (`open`, `in-progress`, `escalated`, `closed`), creation timestamp, last-updated timestamp, and a free-text goal or summary field.
- **FR-006**: The system MUST support traversal of the full three-level hierarchy in a single query, returning master case, all linked parent cases, and all linked grandchild cases.
- **FR-007**: The system MUST allow a case at any level to carry one or more typed metadata bags (e.g., regulator metadata, BAA metadata, privilege flag) without requiring schema changes per metadata type.
- **FR-008**: The system MUST log a case-state transition event every time a case status changes, capturing: which case changed, the previous status, the new status, the triggering agent or operator, and the timestamp.
- **FR-009**: The system MUST allow a parent case to remain open while some of its grandchild cases are closed, and vice versa — parent and grandchild statuses are independent.
- **FR-010**: The system MUST reject any attempt to create a grandchild case under a non-existent parent case, returning a clear error indicating the missing parent.
- **FR-011**: The system MUST probe UiPath Maestro Case for native three-level nesting support and write the result to `DEVIATIONS.md` before any schema migration is executed.
- **FR-012**: Migration scripts MUST be idempotent — re-running them against an already-migrated database MUST produce no errors and no duplicate records.
- **FR-013**: The system MUST provide a query interface for: all cases under a given master; all grandchildren under a given parent; all cases of a given type and status; and the full ancestor chain for any case.

### Key Entities

- **MasterCrisisCase**: Represents the enterprise-wide crisis event. Attributes: unique ID, title, goal statement, status, creation/update timestamps, reversal count, current reversal description.
- **ParentCase**: Represents one stakeholder's involvement in the crisis. Attributes: unique ID, master case reference, stakeholder name, stakeholder type (provider / payer / vendor), status, creation/update timestamps, goal statement.
- **GrandchildCase**: Represents a discrete legal, regulatory, or investigative obligation within a stakeholder's case. Attributes: unique ID, parent case reference, grandchild type (BAA-obligation / regulator-compliance / investigation), obligation identifier (BAA ID or regulator name), status, privilege flag, response deadline, creation/update timestamps.
- **CaseStateEvent**: An immutable log entry. Attributes: event ID, case ID, case level, previous status, new status, triggering actor, timestamp, free-text note.
- **CaseMetadata**: A typed key-value extension bag attached to any case. Attributes: metadata ID, case ID, metadata type, payload (structured JSON), created timestamp.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can create a master case, three parent cases, and six grandchild cases through the data layer and verify all relationships in under 5 minutes using the seed script.
- **SC-002**: The full three-level hierarchy for the CascadeCare demo scenario (1 master + 9 parents + up to 18 grandchildren) can be retrieved in a single round-trip in under 500 milliseconds in a local development environment.
- **SC-003**: All five demo reversals can trigger case state transitions without schema changes — the schema accommodates all planned reversal scenarios from the start.
- **SC-004**: 100% of state transition events are captured in the case history log with no silent drops, verified by a test that fires 50 consecutive state changes and counts log entries.
- **SC-005**: The Maestro Case probe result is recorded in `DEVIATIONS.md` within the same run that executes migrations, so the architectural decision is always traceable.
- **SC-006**: Migration scripts run cleanly against a fresh database with zero manual intervention, verified by the CI pipeline.
- **SC-007**: All model-layer unit tests pass, achieving at least 90% line coverage across case models and the state-transition log.

---

## Assumptions

- The Maestro Case probe is treated as a best-effort inspection. If the Maestro environment is unavailable, the probe records "environment unavailable" in DEVIATIONS.md and the PostgreSQL-backed model proceeds as the sole implementation.
- Three-level nesting is required from the start; there is no planned phase where two levels suffice and a third is added later.
- Case identifiers are system-generated UUIDs; human-readable slugs are optional display attributes, not primary keys.
- Privilege flags (attorney-client, work product) are stored on grandchild cases but their enforcement (filtering visibility) is the responsibility of a later slice (014 — Evidence Graph with Privilege Filters), not this one.
- The six provider BAA metadata sets and the regulatory jurisdiction mappings (which providers fall under TN DOI) are expected to be populated by the Synthetic Data slice (006); this slice only establishes the schema that will hold them.
- The database is PostgreSQL 15+ running in the local Docker Compose environment defined in slice 001.
- Multi-tenancy (data isolation between different ClearFlow operator roles) is out of scope for this slice.
