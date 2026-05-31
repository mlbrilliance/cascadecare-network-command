# CascadeCare Network Command Constitution

## Core Principles

### I. TDD-First (NON-NEGOTIABLE)

Every code file under agents/, shim/, mocks/ requires a corresponding test file in tests/. Write the failing test before writing the implementation. The pre-write hook blocks source file creation if the test file doesn't exist. Red-Green-Refactor cycle strictly enforced. Every reversal requires an end-to-end acceptance test in tests/demo/test_all_reversals.py.

### II. IP Safety (ZERO TOLERANCE)

No real company names anywhere — code, mocks, fixtures, UI strings, demo voiceover, documentation, README, screenshots, any artifact. Forbidden tokens (case-insensitive): zelis, aetna, cigna, unitedhealth, bcbs, hartley, rivet, zipp, zapp, change healthcare, optum, cotiviti, wex. No real patient names, claim numbers, litigation references. The /audit-ip-safety command must run green before any commit.

### III. Externalized Agent Prompts

All agent prompts live in agents/prompts/*.md. Never inline a prompt in Python code. Each prompt file follows the skeleton defined in the agent-prompt-author subagent specification. Prompts are the source of truth for agent behavior.

### IV. Surgical Edits

Prefer Edit over Write when modifying existing files. Never overwrite a file you haven't first read in the current session. Refactors touching >10 files require a DEVIATIONS.md entry first with rationale and approval.

### V. Three-Level Case Nesting

Master crisis case → per-customer parent cases → per-BAA/per-regulator grandchild cases. This structure is a non-negotiable architectural differentiator. If Maestro Case preview doesn't support three levels natively, implement the third level via case-relationship metadata in PostgreSQL with the UI rendering the third level visually. Log any workarounds in DEVIATIONS.md.

### VI. Evidence Provenance (NON-NEGOTIABLE)

Every evidence artifact must trace to: source case, source agent, timestamp, and confidence level — across all three nesting levels. The evidence pack export must include a provenance manifest that a regulator or litigation support team could follow from any evidence item back to its origin.

### VII. Secrets via .env Only

No secrets in code, fixtures, committed files, or documentation. All API keys, connection strings, and credentials via .env file only. The .env file is in .gitignore and never committed.

### VIII. Knowledge Directory is Immutable

The knowledge/ directory contains source-of-truth requirements documents. These are never modified by any build process, agent, or human during the project. The pre-write hook blocks all writes to knowledge/. If requirements change, the human updates knowledge/ manually and a new foundation session re-reads them.

## Development Workflow

- Slice-based development via tasks.md master roadmap
- /start-slice verifies dependencies before beginning work
- /finish-slice runs acceptance tests before marking complete
- Per-feature specs live in specs/{slice-id}/
- Spec-kit manages the specify → plan → tasks → implement cycle per feature

## Quality Gates

- All tests pass (pytest)
- Linter passes (ruff check)
- Type checker passes (mypy)
- IP safety audit passes (/audit-ip-safety)
- DEVIATIONS.md updated for any spec divergence

## Governance

This constitution supersedes all other development practices for this project. Amendments require: documentation in DEVIATIONS.md, explicit human approval, and an updated version number below.

**Version**: 1.0.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-25
