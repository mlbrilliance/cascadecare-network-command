# CascadeCare Network Command

## Project Intent

CascadeCare Network Command is a UiPath Maestro Case demonstration built for AgentHack 2026 Track 1. It shows how an AI-driven case management system orchestrates a multi-stakeholder cyber crisis across healthcare payment networks, evolving from isolated incidents into a coordinated, enterprise-wide response.

ClearFlow Health Network is the protagonist -- a fictional US healthcare payment intermediary whose pricing engine and payment network serve multiple hospital systems and payers. When anomalous claim-flow drops hit several provider customers simultaneously, ClearFlow must determine whether it is the breach vector, a bystander, or a co-victim, all while managing competing obligations to providers, payers, regulators, and its own cyber insurer.

The demo shows how a multi-customer provider cyber cascade is managed as one evolving case with three-level nesting: a master crisis case at the top, per-customer parent cases in the middle, and per-BAA/per-regulator grandchild cases at the bottom. Five master-level reversals (goal shifts) drive the narrative across a 90-day simulated timeline, with child-case events (PHI exfiltration, liquidity stress) adding depth at the parent level.

## Naming Conventions

| Element | Committed Name |
|---|---|
| Project | CascadeCare Network Command |
| Protagonist | ClearFlow Health Network |
| Product: Pricing | ClearFlow Pricing Engine (CPE) |
| Product: Payments | ClearFlow Payment Network (CPN) |
| Lead provider | Northstar Regional Health (7-hospital system) |
| Provider Alpha | Urban academic medical center |
| Provider Beta | Rural community hospital |
| Provider Gamma | Multi-state for-profit chain |
| Provider Delta | Specialty surgical center |
| Provider Epsilon | Children's hospital |
| Payer (active) | Apex Health Plan (commercial antagonist) |
| Payer (active) | SummitBlue Medicare Advantage (federal angle) |
| Payer (named) | Union Prairie Benefits |
| Payer (named) | Lakeshore TPA Services |
| Vendor / attack vector | Nimbus Patient Engagement Platform |
| Cyber insurer | Aurora Specialty |
| Outside counsel | Hawthorne Mercer LLP |
| Forensic firm | Northwall Forensics |

## IP Safety Rules

ZERO TOLERANCE for real company names. Every commit must pass /audit-ip-safety.

Forbidden tokens (case-insensitive, substring match):

```
zelis, aetna, cigna, unitedhealth, bcbs, hartley, rivet, zipp, zapp,
change healthcare, optum, cotiviti, wex
```

Also forbidden:
- Real patient names
- Real claim numbers or NPI numbers
- Real litigation case references
- Any identifiable real-world healthcare entity

If /audit-ip-safety finds a match, the commit is blocked. No exceptions.

## AgentHack 2026 — Competitive Playbook

**Deadline: June 29, 2026 at 11:45 PM EDT.** Early submission is better — judging starts June 3.

### Platform features to integrate (judges will notice)

| Feature | Slice | Why |
|---|---|---|
| Per-provider spawn fan-out | 014 | Reversal 3's 6-child simultaneous spawn, each child seeded with its provider slug. ⚠️ `=datafabric.qem:` expressions FAIL runtime evaluation in spawn inputs (400300, proven 2026-06-10) — StakeholderId is a literal slug; do not claim runtime qem: fan-out |
| `hitlTask` output variable (May 25) | 014 | Wire into Reversal 4 post-HITL stage — reads full reviewer context |
| `Maestro.NotificationService` task (May 28) | 014/015 | Send targeted notifications at grandchild SLA-breach; 2-day-old feature |
| Three-level nesting via `case-management` task | done | Judges built this; no other visible entry uses it |
| Hybrid BPMN + Case | done | UiPath CPO named this "most sophisticated pattern" |
| Trust Layer PHI/PII visible in demo | 015 | Healthcare entrants routinely skip this |

### Bonus points (free, most teams miss this)

The coding-agent bonus requires (a) which tool = Claude Code, (b) how it contributed, (c) verifiable evidence (prompt logs/screenshots). Document in `CLAUDE_CODE_USAGE.md` (Slice 016). This is 2 points for 30 minutes of work.

### caseplan.json V20 canonical rules (from UiPath/skills PR #216)

- Expressions: `=js:vars.x` (NOT `$vars.x`)
- Prefixes: `=vars`, `=js:`, `=metadata`, `=bindings`, `=datafabric`, `=response`, `=string.Format`
- Six exit types: `exit-only`, `wait-for-user`, `return-to-origin`, `terminal`, `send-to-stage`, `rework-stage-and-return`
- Root MUST include: `caseAppEnabled: true`, `publishVersion: 2`, `intsvcActivityConfig: "v2"`, `caseAppConfig`
- Variable dedup: suffix from 2 (e.g. `error2`)

### Required submission artifacts (Devpost)

1. Devpost project page (title, track=Track 1, business problem, architecture, screenshots)
2. Demo video ≤5 min on YouTube/Vimeo — must show solution running live, not slides; name each agent
3. Public GitHub repo under MIT/Apache 2.0 with README covering all UiPath components + setup + "Built with Coding Agents"
4. Solution running live on UiPath Automation Cloud

### Contact

- UiPath Labs access (required for judges): andreea.tomescu@uipath.com (apply by June 5)
- Best practices session: June 9, 3–4 PM UTC — Ebru Sarikaya (prior winner)
- Product feedback form for $1,500 award: submit before June 25

## File and Folder Conventions

Pure-UiPath project layout. Every runtime asset is a UiPath artifact; Python only exists as dev-time tooling.

| Directory | Purpose | Rules |
|---|---|---|
| `maestro_case/` | Maestro Case definitions (3 caseplan.json files) and the uipx solution | Use `uipath-maestro-case` and `uipath-solution` skills. V20 schema. |
| `maestro_bpmn/` | Maestro BPMN process models | Use `uipath-maestro-bpmn` skill |
| `maestro_flow/` | Maestro Flow definitions (Demo Driver) | Use `uipath-maestro-flow` skill |
| `agents/` | Agent Builder agents + Coded Agents (Python SDK) | Each subdir is one agent. `uipath-agents` for low-code; `uipath-coded-apps` for Python SDK |
| `agents/prompts/` | Agent prompt templates | Markdown files ONLY. NEVER inline prompts in Python |
| `api_workflows/` | Integration Service API Workflow definitions | One per external system. Use `uipath-api-workflow` skill |
| `apps/` | UiPath Apps screens (narrative dashboard) | Use `uipath-coded-apps` skill |
| `src/cascadecare/uipath/` | Dev-time wrappers (`auth.py`, `maestro_client.py`) | Build-time only — never runs at demo time |
| `tests/` | Test files for the dev-time wrappers and Coded Agents | Mirror `src/` and `agents/` structure; test file must exist before source file in Coded Agents |
| `knowledge/` | Source-of-truth documents | NEVER modify. Pre-write hook enforces immutability |
| `docs/` | Documentation (including `coding-agents/` evidence and `archive/` for superseded specs) | |
| `scripts/` | One-shot CLI scripts (e.g., `seed_data_fabric.sh`) | Build-time only |
| `specs/` | Active specs (`specs/003-uipath-native/` is canonical) | Old specs archived to `docs/archive/` |

NEVER save working files or tests to the project root.

## Three-Level Case Nesting

Realized via THREE caseplan.json files wired with the native `case-management` task type (Maestro Case V20 Private Preview Guide). No Postgres mirror, no Level-flag superset.

```
clearflow-master-crisis (1 instance)
  |
  +-- via `case-management` task at "Regulatory Response" stage:
  |
  +-- clearflow-stakeholder-parent (~9 instances)
  |   - 6 provider parents (Northstar + Alpha-Epsilon)
  |   - 2 active payer parents (Apex, SummitBlue)
  |   - 1 vendor parent (Nimbus)
  |     |
  |     +-- via `case-management` task at "Subpoena Response" / "Compliance" stage:
  |     |
  |     +-- clearflow-obligation-grandchild (~12 instances)
  |         - Per-BAA obligation grandchildren
  |         - Per-regulator response grandchildren
  |         - Per-investigation grandchildren
```

Hero demo moment: Reversal 3 (Day 30, wall-clock t+150s) — TN DOI subpoena triggers 6 grandchild spawns simultaneously in a visible fan on the canvas.

## Agent Topology

Runtime: **Maestro Case canvas IS the orchestrator.** Stage transitions + `case-management` task spawns carry what was formerly the Master Case Manager. Agents invoke as `type: "agent"` tasks within stages. No LangGraph; no Python harness.

| Agent | Type | Skill | LLM | Role |
|---|---|---|---|---|
| (Master Case Manager) | — | — | — | Absorbed into Maestro Case stage logic |
| Claim Flow Anomaly Detector | Coded Agent (Python SDK) | `uipath-coded-apps` | UiPath first-party | Classifies anomaly score on claim telemetry |
| Multi-Customer Pattern Detector | Coded Agent | `uipath-coded-apps` | UiPath first-party | Cross-provider correlation; emits cascade signal |
| Forensic Self-Exam Agent | Coded Agent | `uipath-coded-apps` | UiPath first-party | Coordinates other agents; routing |
| Vector Hypothesis Agent | Agent Builder (low-code) | `uipath-agents` | Claude (BYO-LLM) | Determines attack vector (ClearFlow vs Nimbus) |
| BAA Boundary Reasoner | Agent Builder | `uipath-agents` | Claude (BYO-LLM) + Context Grounding on `BAA-corpus` | Analyzes BAA terms; identifies cross-BAA conflicts |
| Fiduciary Conflict Detector | Agent Builder | `uipath-agents` | Claude (BYO-LLM) | Multi-party obligation conflicts; HITL form payload |
| Negligent Monitoring Risk Agent | Agent Builder | `uipath-agents` | Claude (BYO-LLM) | Co-defendant exposure for Reversal 5 |

All agent prompts live in `agents/prompts/*.md`. Never inline prompts in Python code.

All LLM calls flow through UiPath LLM Gateway so Trust Layer policies (PHI/PII detection, content filtering) apply uniformly.

## Demo Structure: Five Reversals

| # | Name | Day | Master Goal Shift |
|---|---|---|---|
| 1 | Multi-customer correlation | 1 | "Assist isolated customers" -> "Determine if ClearFlow is the vector" |
| 2 | ClearFlow cleared + Nimbus identified | 5 | "Am I the cause?" -> "Visible bystander with strategic posture decision" |
| 3 | State DOI subpoena collision | 30 | Three-level nesting goes live; 6 grandchild cases spawn |
| 4 | Payer demands vs BAAs | 45 | Fiduciary Conflict Detector fires; tri-party HITL gate |
| 5 | Litigation cascade | 90 | Bystander -> co-defendant; privilege reshuffles |

Child-case events (not master reversals):
- Day 3: PHI exfiltration signal -> Business Associate Exposure child case
- Day 14: Provider liquidity stress -> Payment Continuity escalation

## TDD Rules

- Test file MUST exist before source file in `agents/`, `shim/`, `mocks/`
- Pre-write hook enforces this constraint
- `uv run pytest` must pass before any commit
- Acceptance tests cover all five reversals end-to-end

## Escalation and Stop Conditions

Stop work and ask a human if:
1. A clarifying question would change more than 2 files
2. A regulatory citation cannot be verified against knowledge/ sources
3. A dependency not listed in pyproject.toml is needed
4. Any change would modify files in knowledge/
5. Acceptance criteria are ambiguous or contradictory
6. IP safety check would fail

## Technology Stack

Pure-UiPath at runtime. Python only as build-time tooling.

**UiPath ecosystem (runtime — all assets live on UiPath Automation Cloud)**:
- UiPath Studio Web (authoring all assets)
- UiPath Maestro Case (3 case definitions, V20 schema)
- UiPath Maestro BPMN (ideal-response playbook)
- UiPath Maestro Flow (Demo Driver)
- UiPath Agent Builder (4 low-code agents)
- UiPath Coded Agents (3 Python SDK agents)
- UiPath Integration Service / API Workflows (~13 mock fronts)
- UiPath Data Fabric (synthetic provider/payer/BAA/telemetry entities)
- UiPath Context Grounding (BAA-corpus, ClaimTelemetry-corpus indexes)
- UiPath Trust Layer (PHI/PII guardrails on every LLM call)
- UiPath LLM Gateway + BYO-LLM (Anthropic registered for heavy reasoning)
- UiPath Apps (narrative dashboard)
- UiPath Action Center (HITL gate at Reversal 4)
- UiPath Orchestrator (Robot/jobs runtime)

**Python (build-time / Coded Agents only)**:
- Python 3.12+ (LTS), managed by `uv` 0.7.12+
- `uipath` SDK 2.10.79+ (CLI + Python wrappers)
- `httpx` 0.28.1+ (HTTP client used by dev-time wrappers)
- Ruff 0.15.16+ + mypy 1.12.0+ (linting and type checking)
- pytest 8.3.0+ + pytest-asyncio 0.24.0+ + pytest-cov 7.1.0+ (testing dev-time wrappers + Coded Agents)

**Removed in Slice 004** (no longer in pyproject.toml): LangGraph, LangChain, Anthropic SDK (direct calls go through LLM Gateway), Pydantic Settings, SQLAlchemy, psycopg, LanceDB, Polars, Faker, FastAPI, Uvicorn, Pydantic (no models), Alembic.

---

# Ruflo -- Claude Code Configuration

## Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary -- prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root -- use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- NEVER add a `Co-Authored-By` trailer to user commits unless this project's `.claude/settings.json` has `attribution.commit` set (#2078). The Claude Code Bash tool may suggest one in its default commit-message template -- ignore it. `Co-Authored-By` is semantic authorship attribution under git/GitHub convention; the tool is the facilitator, not a co-author.
- Keep files under 500 lines
- Validate input at system boundaries

## Agent Comms (SendMessage-First Coordination)

Named agents coordinate via `SendMessage`, not polling or shared state.

```
Lead (you) <-> architect <-> developer <-> tester <-> reviewer
              (named agents message each other directly)
```

### Spawning a Coordinated Team

```javascript
// ALL agents in ONE message, each knows WHO to message next
Agent({ prompt: "Research the codebase. SendMessage findings to 'architect'.",
  subagent_type: "researcher", name: "researcher", run_in_background: true })
Agent({ prompt: "Wait for 'researcher'. Design solution. SendMessage to 'coder'.",
  subagent_type: "system-architect", name: "architect", run_in_background: true })
Agent({ prompt: "Wait for 'architect'. Implement it. SendMessage to 'tester'.",
  subagent_type: "coder", name: "coder", run_in_background: true })
Agent({ prompt: "Wait for 'coder'. Write tests. SendMessage results to 'reviewer'.",
  subagent_type: "tester", name: "tester", run_in_background: true })
Agent({ prompt: "Wait for 'tester'. Review code quality and security.",
  subagent_type: "reviewer", name: "reviewer", run_in_background: true })

// Kick off the pipeline
SendMessage({ to: "researcher", summary: "Start", message: "[task context]" })
```

### Patterns

| Pattern | Flow | Use When |
|---------|------|----------|
| **Pipeline** | A -> B -> C -> D | Sequential dependencies (feature dev) |
| **Fan-out** | Lead -> A, B, C -> Lead | Independent parallel work (research) |
| **Supervisor** | Lead <-> workers | Ongoing coordination (complex refactor) |

### Rules

- ALWAYS name agents -- `name: "role"` makes them addressable
- ALWAYS include comms instructions in prompts -- who to message, what to send
- Spawn ALL agents in ONE message with `run_in_background: true`
- After spawning: STOP, tell user what's running, wait for results
- NEVER poll status -- agents message back or complete automatically

## Swarm & Routing

### Config
- **Topology**: hierarchical-mesh (anti-drift)
- **Max Agents**: 15
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

```bash
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

### Agent Routing

| Task | Agents | Topology |
|------|--------|----------|
| Bug Fix | researcher, coder, tester | hierarchical |
| Feature | architect, coder, tester, reviewer | hierarchical |
| Refactor | architect, coder, reviewer | hierarchical |
| Performance | perf-engineer, coder | hierarchical |
| Security | security-architect, auditor | hierarchical |

### When to Swarm
- **YES**: 3+ files, new features, cross-module refactoring, API changes, security, performance
- **NO**: single file edits, 1-2 line fixes, docs updates, config changes, questions

### 3-Tier Model Routing

| Tier | Handler | Use Cases |
|------|---------|-----------|
| 1 | Agent Booster (WASM) | Simple transforms -- skip LLM, use Edit directly |
| 2 | Haiku | Simple tasks, low complexity |
| 3 | Sonnet/Opus | Architecture, security, complex reasoning |

## Memory & Learning

### Before Any Task
```bash
npx @claude-flow/cli@latest memory search --query "[task keywords]" --namespace patterns
npx @claude-flow/cli@latest hooks route --task "[task description]"
```

### After Success
```bash
npx @claude-flow/cli@latest memory store --namespace patterns --key "[name]" --value "[what worked]"
npx @claude-flow/cli@latest hooks post-task --task-id "[id]" --success true --store-results true
```

### MCP Tools (use `ToolSearch("keyword")` to discover)

| Category | Key Tools |
|----------|-----------|
| **Memory** | `memory_store`, `memory_search`, `memory_search_unified` |
| **Bridge** | `memory_import_claude`, `memory_bridge_status` |
| **Swarm** | `swarm_init`, `swarm_status`, `swarm_health` |
| **Agents** | `agent_spawn`, `agent_list`, `agent_status` |
| **Hooks** | `hooks_route`, `hooks_post-task`, `hooks_worker-dispatch` |
| **Security** | `aidefence_scan`, `aidefence_is_safe`, `aidefence_has_pii` |
| **Hive-Mind** | `hive-mind_init`, `hive-mind_consensus`, `hive-mind_spawn` |

### Background Workers

| Worker | When |
|--------|------|
| `audit` | After security changes |
| `optimize` | After performance work |
| `testgaps` | After adding features |
| `map` | Every 5+ file changes |
| `document` | After API changes |

```bash
npx @claude-flow/cli@latest hooks worker dispatch --trigger audit
```

### Project memory (session persistence)

The `.agent-os/memory/project_memory.db` SQLite DB is the session-persistence store for this project (7 tables: tasks, decisions, checkpoints, handoffs, spec-gate log, sessions, artifacts).

```bash
# Session START — before writing any code:
make resume                                              # prints last handoff + DB state

# After every subtask (autopilot):
make checkpoint TASK=<id> NAME=<name> PASSED=1 DETAILS="..."
make checkpoint TASK=<id> NAME=<name> PASSED=0 DETAILS="..."   # halts autopilot

# Session END:
make save-session TASK=<slice> SUMMARY="..." DECISIONS="..." BLOCKERS="..." NEXT="..."

# Log a non-obvious decision:
make log-decision TASK=<id> DECISION="..." RATIONALE="..." ALT="..."
```

## Agents

**Core**: `coder`, `reviewer`, `tester`, `planner`, `researcher`
**Architecture**: `system-architect`, `backend-dev`, `mobile-dev`
**Security**: `security-architect`, `security-auditor`
**Performance**: `performance-engineer`, `perf-analyzer`
**Coordination**: `hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`
**GitHub**: `pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`

Any string works as a custom agent type.

## Build & Test

- ALWAYS run tests after code changes
- ALWAYS verify build succeeds before committing

```bash
uv run pytest && uv run mypy src/
```

## CLI Quick Reference

```bash
npx @claude-flow/cli@latest init --wizard           # Setup
npx @claude-flow/cli@latest swarm init --v3-mode     # Start swarm
npx @claude-flow/cli@latest memory search --query "" # Vector search
npx @claude-flow/cli@latest hooks route --task ""    # Route to agent
npx @claude-flow/cli@latest doctor --fix             # Diagnostics
npx @claude-flow/cli@latest security scan            # Security scan
npx @claude-flow/cli@latest performance benchmark    # Benchmarks
```

26 commands, 140+ subcommands. Use `--help` on any command for details.

## Setup

```bash
# Claude Flow CLI — v3.10.40+ (uses @latest for auto-updates)
claude mcp add claude-flow -- npx -y @claude-flow/cli@latest
npx @claude-flow/cli@latest daemon start
npx @claude-flow/cli@latest doctor --fix
```

**Agent tool** handles execution (agents, files, code, git). **MCP tools** handle coordination (swarm, memory, hooks). **CLI** is the same via Bash.

## SPEC GATE

Before writing ANY new function, show this block and wait for explicit "LGTM":

```
SPEC: <function_name>
Purpose: <one sentence>
Inputs: <name: type: description>
Outputs: <return type: description>
Edge cases: <case: what happens>
Side effects: <files written, state changed, external calls>
Test: <one-line unit test description>
```

HIGH RISK functions (Coded Agents, caseplan.json logic, auth/OAuth flows): also enumerate every failure mode and how each is handled. Do not write a single line of implementation until the spec is approved.

## AUTOPILOT MODE

When the user says "autopilot" or "yolo":

**Passing subtask** (automatic, silent):
```bash
make checkpoint TASK=<id> NAME=<subtask> PASSED=1 DETAILS="<one sentence>"
```
Proceed to next subtask immediately.

**Failing subtask** (halt):
```bash
make checkpoint TASK=<id> NAME=<subtask> PASSED=0 DETAILS="<what failed>"
```
Show: failing test output · diagnosis · proposed fix. Wait for "fix it", "override", or a correction.

**Slice complete**: task-complete checkpoint + update tasks.md + query DB for unblocked slices + ask for session summary. Three halt conditions only. Never auto-generate the session summary.

## Project MCPs (documentation and search)

| Tool | When to use |
|------|-------------|
| `context7` | UiPath SDK / Python library docs (uipath, pytest, httpx, ruff) |
| `ref-tools` | Token-efficient doc search (public + private) |
| `exa` | Neural semantic search |
| `tavily` | Real-time web: regulatory citations, CVEs, release notes |

Install: `bash scripts/setup-mcps.sh` (after filling in API keys in `.env`)

## /handoff — at slice boundaries

```
/handoff "Completed [slice]. Next: [slice]. Context: [1 sentence]. Skills: [uipath-maestro-case|uipath-agents|...]"
```

Saves to OS temp. At next session: `make resume` + handoff doc content = 2-minute resume.

## /improve-codebase-architecture ↔ /thermo-nuclear-code-quality-review

**MANDATORY BIDIRECTIONAL LOOP — runs on every slice diff, no exceptions.**

- Run both skills together after every slice commit — they are always paired.
- `/thermo-nuclear-code-quality-review`: structural excellence enforcement on the diff — simplification, <1,000-line files, no spaghetti, data tables over constructor repetition, direct flows over wrapper chains, no sys.path hacks in tests.
- `/improve-codebase-architecture`: depth/seam/locality audit — identifies shallow modules, pass-through layers, misplaced seams.
- Generate the combined HTML report to `/tmp/architecture-review-<timestamp>.html`.
- **All `Blocker`-level findings must be applied before the next slice starts.**
- `Worth Exploring` / `Speculative` findings may be deferred to the polish slice.
- If thermo-nuclear finds ≥3 structural blockers in one slice → trigger `/improve-codebase-architecture` immediately (don't wait for the scheduled review).
- Architecture review proposes candidate refactors → thermo-nuclear verifies the refactor doesn't introduce new smells before it is implemented.

## Spec-kit Workflow — per slice

Slices are pre-defined in `specs/003-uipath-native/tasks.md`. Skip `/speckit.specify`.

```
/speckit.plan       paste slice from tasks.md + tech constraints
/speckit.analyze    catch inconsistencies before coding
/speckit.tasks      subtasks with [P] for parallel; each individually testable
/speckit.implement  Spec Gate per function — SPEC block → LGTM → code
```

Rule: NEVER touch `.specify/` except via spec-kit commands. `tasks.md` (root) = master tracker; `.specify/` = implementation layer.

> References: `specs/003-uipath-native/plan.md` · `data-model.md` · `tasks.md`
> Archived: `docs/archive/specs-002-case-schema/` (pre-pivot spec, 2026-05-26)
