# Feature Specification: Repo Scaffolding

**Feature Branch**: `001-repo-scaffolding`

**Created**: 2026-05-25

**Status**: Draft

**Input**: User description: "Slice 001 — create all source and test directories with __init__.py files, docker-compose.yml with PostgreSQL, Pydantic config.py, and .env.example"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Finds Every Package Directory (Priority: P1)

A developer clones the repository and verifies that every Python package directory exists with an `__init__.py` file, ready for downstream slices to add modules. The directory tree matches the canonical structure defined in CLAUDE.md and the architecture doc.

**Why this priority**: Without the directory skeleton, no downstream slice can add agents, mocks, shim endpoints, data loaders, or models. Every subsequent slice depends on these directories existing.

**Independent Test**: Run `python -c "from cascadecare import agents, shim, mocks, data, models, evidence"` and confirm all imports succeed. Verify test subdirectories exist.

**Acceptance Scenarios**:

1. **Given** the repository after Slice 001, **When** a developer lists the directory tree under `src/cascadecare/`, **Then** the following directories exist, each containing an `__init__.py`: `agents/`, `agents/prompts/`, `shim/`, `mocks/`, `data/`, `models/`, `evidence/`.
2. **Given** the repository after Slice 001, **When** a developer lists the directory tree under `tests/`, **Then** the following directories exist, each containing an `__init__.py`: `unit/`, `integration/`, `demo/`.
3. **Given** the repository after Slice 001, **When** a developer lists the project root, **Then** the directories `config/` and `ui/` exist (no `__init__.py` required since they are not Python packages).

---

### User Story 2 - Developer Starts PostgreSQL Locally (Priority: P1)

A developer runs `docker compose up -d` and gets a PostgreSQL instance ready for the case schema work in Slice 002. The `docker-compose.yml` references `.env` for credentials and never hardcodes secrets.

**Why this priority**: PostgreSQL is the persistence layer for the three-level case nesting. Slice 002 cannot begin without it.

**Independent Test**: Run `docker compose up -d` and verify PostgreSQL accepts connections on the configured port with the configured database name.

**Acceptance Scenarios**:

1. **Given** Docker is installed and `.env` is populated from `.env.example`, **When** the developer runs `docker compose up -d`, **Then** a PostgreSQL container starts and accepts connections on port 5432 with database name `cascadecare`.
2. **Given** the `docker-compose.yml` file, **When** a reviewer inspects it, **Then** all credentials (username, password, database name) are sourced from environment variables referencing `.env`, with no hardcoded secrets.

---

### User Story 3 - Developer Configures the Application (Priority: P2)

A developer copies `.env.example` to `.env`, fills in values, and the application reads them via a Pydantic settings model in `config.py`. This centralizes all configuration for downstream slices.

**Why this priority**: Configuration is needed by the shim (Slice 003), mock systems (Slices 004-005), and the agent runtime (Slice 007). Establishing the pattern early prevents ad-hoc config approaches later.

**Independent Test**: Import `cascadecare.config` and verify it loads settings from environment variables without errors.

**Acceptance Scenarios**:

1. **Given** `.env.example` exists, **When** a developer copies it to `.env` and imports `cascadecare.config`, **Then** the settings object loads without validation errors and exposes database connection fields.
2. **Given** no `.env` file exists, **When** a developer imports `cascadecare.config`, **Then** default values are used for non-sensitive fields and clear errors indicate which required fields are missing.

---

### Edge Cases

- What happens when `docker compose up` is run without a `.env` file? PostgreSQL should still start using the default values defined in `docker-compose.yml`'s environment variable defaults.
- What happens when a directory already exists from a previous partial run? The scaffolding should be idempotent — re-running does not fail or overwrite existing content.
- What happens when `uv sync` is run after scaffolding changes? It should succeed without errors, confirming no dependency conflicts were introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The following directories MUST exist under `src/cascadecare/`, each containing an `__init__.py`: `agents/`, `agents/prompts/`, `shim/`, `mocks/`, `data/`, `models/`, `evidence/`.
- **FR-002**: The `agents/prompts/` directory MUST exist for externalized agent prompt files (markdown). No Python prompts are inlined.
- **FR-003**: The following directories MUST exist under `tests/`, each containing an `__init__.py`: `unit/`, `integration/`, `demo/`.
- **FR-004**: The directories `config/` and `ui/` MUST exist at the project root. These are not Python packages and do not require `__init__.py`.
- **FR-005**: A `docker-compose.yml` MUST define a PostgreSQL service on port 5432 with database name `cascadecare`, sourcing credentials from `.env` environment variables.
- **FR-006**: A `.env.example` MUST document all required environment variables with placeholder values: database host, port, name, user, password, and any application-level settings.
- **FR-007**: A `src/cascadecare/config.py` MUST define a Pydantic `BaseSettings` model that loads configuration from `.env` files and environment variables.
- **FR-008**: `uv sync` MUST succeed after all scaffolding changes are applied.
- **FR-009**: All new `__init__.py` files MUST be empty or contain only a module-level docstring. No logic in scaffolding init files.
- **FR-010**: No agent logic, mock endpoints, database models, or Next.js initialization is included in this slice.

### Key Entities

- **Package Directory**: A Python directory with `__init__.py` that establishes an importable namespace for downstream modules.
- **Configuration Settings**: A Pydantic model that centralizes application settings sourced from environment variables and `.env` files.
- **Docker Compose Service**: A containerized PostgreSQL instance configured for local development.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 7 source directories and 3 test directories exist with `__init__.py` files after scaffolding.
- **SC-002**: `python -c "from cascadecare import agents, shim, mocks, data, models, evidence"` succeeds without errors.
- **SC-003**: `docker compose config` validates the `docker-compose.yml` without errors and shows no hardcoded credentials.
- **SC-004**: `uv sync` completes successfully after all changes.
- **SC-005**: `uv run pytest` exits cleanly (exit code 0 or 5 for no tests collected) with no import errors.
- **SC-006**: `.env.example` contains at least 5 documented environment variables.

## Assumptions

- Docker is available on the developer's machine for PostgreSQL but is not required to run the Python test suite.
- The `pyproject.toml` already exists with core dependencies from the foundation phase. No new dependencies are added unless required for `config.py` (Pydantic is already listed).
- The `knowledge/` directory already exists from the foundation phase and is not modified.
- The `scripts/` directory already exists from the foundation phase.
- The `ui/` directory is an empty placeholder — Next.js initialization is out of scope.
- The `agents/prompts/` directory contains no prompt files yet — those are added in Slice 007+.
