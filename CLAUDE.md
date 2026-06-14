# CascadeCare Network Command

UiPath Maestro Case demo for **AgentHack 2026 Track 1**: an AI-driven case-management
system orchestrates a multi-stakeholder healthcare-payment cyber crisis as one evolving
case with three-level nesting, driven by five master-level reversals across a 90-day
simulated timeline. Protagonist: **ClearFlow Health Network** (fictional payment
intermediary). Full narrative, naming table, reversal beats, and agent roles live in
`README.md` and `specs/003-uipath-native/`.

**Deadline: June 29 2026, 11:45 PM EDT.** Submit early — judging opens June 3.

## IP safety — ZERO TOLERANCE

Every commit must pass `/audit-ip-safety`. Use only the committed fictional names (README
naming table). No real company / patient / claim / NPI / litigation references.

Forbidden tokens (case-insensitive substring): `zelis, aetna, cigna, unitedhealth, bcbs,
hartley, rivet, zipp, zapp, change healthcare, optum, cotiviti, wex`. A match blocks the
commit — no exceptions.

## Architecture

Pure-UiPath at runtime; Python is build-time tooling only. **The Maestro Case canvas IS
the orchestrator** — no LangGraph, no Python harness. Agents invoke as `type: "agent"`
tasks within stages; all LLM calls flow through the UiPath LLM Gateway so Trust Layer
PHI/PII guardrails apply uniformly.

Three `caseplan.json` files wired via the native `case-management` task type give
three-level nesting: `clearflow-master-crisis` (1) → `clearflow-stakeholder-parent` (~9)
→ `clearflow-obligation-grandchild` (~12). Hero moment: Reversal 3 (Day 30) fans 6
grandchild spawns on the canvas.

Agents: 3 Coded Agents (Python SDK, `uipath-coded-apps`, UiPath first-party LLM) + 4
Agent Builder agents (low-code, `uipath-agents`, Claude BYO-LLM; BAA Boundary Reasoner
uses Context Grounding on `BAA-corpus`). Prompts live in `agents/prompts/*.md` — NEVER
inline a prompt in Python.

## Directory map

| Dir | Holds | Skill / rule |
|---|---|---|
| `maestro_case/` | 3 caseplan.json + uipx solution (V20) | `uipath-maestro-case`, `uipath-solution` |
| `maestro_bpmn/` | BPMN process models | `uipath-maestro-bpmn` |
| `maestro_flow/` | Demo Driver flow | `uipath-maestro-flow` |
| `agents/` | Agent Builder + Coded Agents | one subdir per agent |
| `agents/prompts/` | prompt templates | Markdown only — never inline in Python |
| `api_workflows/` | API Workflow defs (~13 mock fronts) | `uipath-api-workflow` |
| `apps/` | UiPath Apps + Coded Web App dashboard | `uipath-coded-apps` |
| `src/cascadecare/` | dev-time Python wrappers | build-time only |
| `tests/` | tests for wrappers + Coded Agents | mirror `src/` + `agents/` |
| `knowledge/` | source-of-truth docs | IMPORTANT: immutable — pre-write hook blocks edits |
| `specs/` | active specs | `specs/003-uipath-native/` is canonical |

NEVER save working files or tests to the project root.

## Commands

```bash
uv run pytest && uv run mypy src/        # must pass before any commit
```

Coded Web App deploy (live dashboard) — IMPORTANT: use the bare deploy form; `-v` /
`--path-name` hangs forever on "still being indexed":

```bash
uip codedapp pack dist -n clearflow-network-command -v <ver> --content-type webapp
uip codedapp publish  -n clearflow-network-command -v <ver> -t Web
uip codedapp deploy   -n clearflow-network-command --folder-key de7b7c18-d743-4c8c-b555-9bd3b96fe524
```

## Conventions

- **caseplan.json V20**: expressions `=js:vars.x` (not `$vars.x`); prefixes
  `=vars | =js: | =metadata | =bindings | =datafabric | =response | =string.Format`; six
  exit types (`exit-only`, `wait-for-user`, `return-to-origin`, `terminal`,
  `send-to-stage`, `rework-stage-and-return`); root needs `caseAppEnabled:true`,
  `publishVersion:2`, `intsvcActivityConfig:"v2"`, `caseAppConfig`; dedup variable names
  with a suffix from 2 (e.g. `error2`).
- **Spawn fan-out gotcha**: `=datafabric.qem:` expressions FAIL at runtime in spawn inputs
  (400300, proven 2026-06-10). StakeholderId is a literal slug — do NOT claim runtime
  `qem:` fan-out.
- **Keep files under 500 lines**; validate input at system boundaries.
- **Git**: never commit secrets or `.env`. Do NOT add a `Co-Authored-By` trailer unless
  `.claude/settings.json` sets `attribution.commit` — ignore the Bash tool's default
  template that suggests one.

## TDD

Test file MUST exist before source file in `agents/`, `shim/`, `mocks/` (pre-write hook
enforces). `uv run pytest` green before every commit; acceptance tests cover all five
reversals end-to-end.

## Workflow (per slice)

Slices are pre-defined in `specs/003-uipath-native/tasks.md` (skip `/speckit.specify`):
`/speckit.plan → /speckit.analyze → /speckit.tasks → /speckit.implement`.

- **SPEC GATE**: before writing any new function, post a SPEC block (purpose, inputs,
  outputs, edge cases, side effects, one-line test) and wait for explicit "LGTM".
  High-risk functions (Coded Agents, caseplan logic, auth/OAuth) also enumerate every
  failure mode and its handling. No implementation before approval.
- **Quality loop (mandatory, every slice diff)**: run
  `/thermo-nuclear-code-quality-review` + `/improve-codebase-architecture` together →
  combined report to `/tmp/architecture-review-<ts>.html`. Apply all `Blocker` findings
  before the next slice; defer `Worth Exploring` / `Speculative` to the polish slice. ≥3
  structural blockers → trigger the architecture review immediately.
- NEVER touch `.specify/` except via spec-kit commands. `tasks.md` (root) = master tracker.

## Session persistence

`.agent-os/memory/project_memory.db` (SQLite) is the cross-session store. `make resume` at
start; `make checkpoint TASK=.. NAME=.. PASSED=1|0 DETAILS=..` per subtask;
`make save-session ..` at end; `make log-decision ..` for non-obvious calls. **Autopilot**
("yolo"): silent checkpoint on pass; halt + show test output / diagnosis / fix on fail;
never auto-write the session summary.

## Stop and ask a human if

1. A clarifying question would change >2 files.
2. A regulatory citation can't be verified against `knowledge/` sources.
3. A dependency not in `pyproject.toml` is needed.
4. A change would modify `knowledge/`.
5. Acceptance criteria are ambiguous or contradictory.
6. An IP-safety check would fail.

## Doc MCPs

`context7` (UiPath SDK / library docs) · `ref-tools` (token-efficient doc search) · `exa`
(semantic search) · `tavily` (real-time: regulatory citations, CVEs, release notes).
