# AGENTS.md -- CascadeCare Network Command

> Shared behavioral rules for every coding agent runtime — Claude Code, Codex, Gemini CLI, Copilot,
> Cursor, Windsurf, and open-source harnesses. Tool-specific addenda live in CLAUDE.md, GEMINI.md,
> and .github/copilot-instructions.md.

---

## Project Intent

CascadeCare Network Command is a UiPath Maestro Case demonstration built for AgentHack 2026 Track 1. It orchestrates a multi-stakeholder healthcare cyber crisis -- a financial shockwave cascading across hospital systems, payers, regulators, and a cyber insurer -- through a single evolving case with three-level nesting and five master-level reversals (goal shifts).

ClearFlow Health Network, a fictional US healthcare payment intermediary, discovers anomalous claim-flow drops across multiple provider customers. The system must determine whether ClearFlow is the breach vector, a bystander, or a co-victim, while managing competing legal and fiduciary obligations across all parties.

**Runtime posture**: UiPath Maestro Case IS the runtime. No external Python service runs during the demo. Every agent, workflow, and HITL gate is a UiPath asset visible in UiPath Automation Cloud.

---

## Naming Conventions

All names are fictional. No real company, provider, payer, or person names are permitted anywhere in the codebase.

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

---

## IP Safety Rules

ZERO TOLERANCE for real company names. Every commit must pass an IP safety audit.

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

If an IP safety check finds a match, the commit is blocked. No exceptions.

---

## File and Folder Conventions

| Directory | Purpose | Rules |
|---|---|---|
| `maestro_case/` | UiPath Maestro Case definitions | One subdirectory per case (master/parent/grandchild). `caseplan.json` is the source of truth. Never hand-copy into the solution package — use `scripts/pack-solution.sh`. |
| `maestro_bpmn/` | UiPath Maestro BPMN models | Ideal-response happy-path model with gateway divergence into Maestro Case |
| `maestro_flow/` | UiPath Maestro Flow definitions | Demo Driver flow (`clearflow-demo-driver`) |
| `agents/` | Agent definitions and prompts | `agents/prompts/*.md` for system prompts. `agents/<name>/` for Agent Builder JSON and Coded Agent Python packages |
| `api_workflows/` | Integration Service API Workflows | One subdirectory per external system mock (~13 total) |
| `apps/` | UiPath Apps | Narrative dashboard (`clearflow-network-command`) |
| `scripts/` | Build and data utilities | `pack-solution.sh` assembles `clearflow-solution.uipx`; `seed_data_fabric.sh` seeds Data Fabric |
| `src/cascadecare/uipath/` | Build-time Python wrappers | OAuth helper and thin `uip` CLI wrapper — dev/build use only, NOT present at demo runtime |
| `tests/` | Test files | Mirror `src/` structure; test file must exist before source file |
| `knowledge/` | Source-of-truth documents | IMMUTABLE. Never modify these files under any circumstance |
| `docs/` | Documentation | Architecture, usage examples, changelog |
| `specs/003-uipath-native/` | Active specification | Canonical plan, tasks, data model, case vocabulary, event contracts |

Rules:
- NEVER save working files or tests to the project root.
- NEVER modify files in `knowledge/`. It is an immutable reference directory.
- ALWAYS read a file before editing it.
- Keep files under 500 lines.
- All agent prompts live in `agents/prompts/*.md`. Never inline prompts in any other file.

---

## TDD Requirement

Test-Driven Development is mandatory:

1. Write a failing test FIRST in `tests/`.
2. Write the minimum source code in `src/` to make it pass.
3. A test file MUST exist before its corresponding source file in `agents/` and Python packages.
4. Tests must pass before any commit. Install tooling with `uv sync --extra dev`, then run `uv run pytest` locally. There is no CI workflow (`.github/workflows/` is empty); the local `uv run pytest` gate is authoritative.
5. Case vocabulary consistency tests must pass locally via `uv run pytest tests/unit/case_vocabulary tests/unit/event_contracts`: every cross-case reference in all three caseplan.json files must resolve against `specs/003-uipath-native/case-vocabulary.yaml`.

---

## Three-Level Case Nesting

The case model uses three levels of nesting via the native `case-management` task type in Maestro Case V20:

```
Master Crisis Case (1)  ← clearflow-master-crisis/content/caseplan.json
  |
  +-- Provider Parent Cases (6: Northstar, Alpha-Epsilon)  ← clearflow-stakeholder-parent/content/caseplan.json
  |     +-- Per-BAA Grandchild Cases                       ← clearflow-obligation-grandchild/content/caseplan.json
  |     +-- Per-Regulator Grandchild Cases
  |
  +-- Payer Parent Cases (2 active: Apex, SummitBlue)
  |     +-- Compliance Grandchild Cases
  |
  +-- Vendor Parent Case (Nimbus)
        +-- Investigation Grandchild Cases
```

Native `case-management` task type wires parent-spawn and grandchild-spawn. No relational mirror, no external DB.
Deviations from this structure are logged in `DEVIATIONS.md`.

---

## Agent Topology

Runtime: UiPath. All agents run inside UiPath Automation Cloud — no external Python process at demo time.

### Agent Builder agents (4 — low-code, LLM + tools, heavy reasoning via Claude BYO-LLM)

| Agent | Role | LLM |
|---|---|---|
| Vector Hypothesis Agent | Enumerates and evaluates attack-vector hypotheses; surfaces Nimbus at Reversal 2 | Claude (BYO-LLM) |
| BAA Boundary Reasoner | Analyzes each provider's BAA terms against active subpoena scope; six BAAs, six answers | Claude (BYO-LLM) |
| Fiduciary Conflict Detector | Identifies when ClearFlow's obligations to two or more participants conflict; drives Reversal 4 | Claude (BYO-LLM) |
| Negligent Monitoring Risk Agent | Assesses co-defendant exposure; drives Reversal 5 | Claude (BYO-LLM) |

### Coded Agents (3 — Python SDK published to Studio Web, numerical/correlation logic)

| Agent | Role | LLM |
|---|---|---|
| Claim Flow Anomaly Detector | Detects per-customer claim volume anomalies from CPN telemetry | UiPath first-party |
| Multi-Customer Pattern Detector | Correlates anomalies across provider customers; drives Reversal 1 | UiPath first-party |
| Forensic Self-Exam Agent | Coordinates ClearFlow's internal investigation; drives Reversal 2 | UiPath first-party |

All agent system prompts live in `agents/prompts/*.md`. Never inline prompts in Python code or JSON.

---

## Demo Structure: Five Reversals

| # | Name | Day | Master Goal Shift |
|---|---|---|---|
| 1 | Multi-customer correlation | 1 | "Assist isolated customers" → "Determine if ClearFlow is the vector" |
| 2 | ClearFlow cleared + Nimbus identified | 5 | "Am I the cause?" → "Visible bystander with strategic posture decision" |
| 3 | State DOI subpoena collision | 30 | Three-level nesting hero moment — 6 grandchild cases fan-spawn on canvas |
| 4 | Payer demands vs BAAs | 45 | Fiduciary Conflict Detector fires; tri-party HITL gate in Action Center |
| 5 | Litigation cascade | 90 | Bystander → co-defendant; privilege flags reshuffle on grandchild cases |

Child-case events (not master reversals):
- Day 3: PHI exfiltration signal → Business Associate Exposure parent case
- Day 14: Provider liquidity stress → Payment Continuity grandchild escalation

---

## Technology Stack

| Layer | Technology |
|---|---|
| Orchestration | UiPath Maestro Case (3-level, V20 schema, `case-management` task type) |
| Process model | UiPath Maestro BPMN (ideal-response happy path) |
| Demo driver | UiPath Maestro Flow (`clearflow-demo-driver`) |
| Agents (reasoning) | UiPath Agent Builder (4 agents, Claude BYO-LLM via LLM Gateway) |
| Agents (computation) | UiPath Coded Agents / Python SDK (3 agents, UiPath first-party LLM) |
| Mock external systems | Integration Service API Workflows (~13, one per external system) |
| Reference data + BAAs | UiPath Data Fabric (entities: Provider, Payer, Vendor, Regulator, Insurer, Counsel, BAA, ClaimTelemetry) |
| Semantic retrieval | UiPath Context Grounding (indexes over BAA corpus + claim telemetry) |
| LLM governance | UiPath Trust Layer (PHI/PII detection on every LLM Gateway call) |
| LLM routing | UiPath LLM Gateway (UiPath first-party for light tasks; Claude BYO-LLM for heavy reasoning) |
| HITL | UiPath Action Center |
| Narrative UI | UiPath Apps (`clearflow-network-command` — cascade tree + reversal timeline) |
| Solution packaging | `clearflow-solution.uipx` published via `uip solution upload` |
| Build-time auth | Python `src/cascadecare/uipath/` (dev only, not in demo runtime) |
| Linting | Ruff + mypy |
| Testing | pytest + pytest-asyncio + pytest-cov |

---

## Escalation and Stop Conditions

Stop work and ask a human if:

1. A clarifying question would change more than 2 files
2. A regulatory citation cannot be verified against `knowledge/` sources
3. A dependency not listed in `pyproject.toml` is needed
4. Any change would modify files in `knowledge/`
5. Acceptance criteria are ambiguous or contradictory
6. IP safety check would fail

---

## SPEC GATE — mandatory before any implementation

Before writing ANY new function, produce this block and wait for explicit user approval ("LGTM" / "approved"):

```
SPEC: <function_name>
Purpose: <one sentence — what it does and why it exists>
Inputs: <name: type: description for each parameter>
Outputs: <return type: description>
Edge cases handled:
  - <case: what happens>
Side effects: <files written, state changed, external calls>
Test: <one-line description of the unit test that proves it works>
```

Do not write a single line of implementation until the spec is approved. For HIGH RISK functions, additionally enumerate every failure mode and its handling.

---

## MEMORY SYSTEM

Project state persists in `.agent-os/memory/project_memory.db` (SQLite).
Helper scripts in `.agent-os/scripts/`:

- `python .agent-os/scripts/resume.py` — run at the **START of every session**. Prints last handoff, active tasks, and recent decisions.
- `python .agent-os/scripts/checkpoint.py` — run **after each subtask**. Records pass/fail. A failed checkpoint halts work until resolved.
- `python .agent-os/scripts/save_session.py` — run at the **END of every session**. Records what was done, decisions made, and what's next.
- `python .agent-os/scripts/log_decision.py` — run whenever a non-obvious choice is made so future sessions know the rationale.

At session start, always run `resume.py` first. At task completion, always run `checkpoint.py` then `save_session.py`.

---

## AUTOPILOT MODE

When the user says "autopilot" or "yolo", run the full subtask → checkpoint → next-subtask loop automatically without asking permission between passing steps. Only three things halt autopilot:

1. A failed acceptance test (checkpoint PASSED=0)
2. A Spec Gate function awaiting approval
3. A session-summary request after a slice completes

**After every passing subtask** (automatic, silent):
```
make checkpoint TASK=<id> NAME=<subtask> PASSED=1 DETAILS="<one sentence>"
```
Proceed to the next subtask immediately without prompting.

**After a failing subtask** (halt):
```
make checkpoint TASK=<id> NAME=<subtask> PASSED=0 DETAILS="<what failed>"
```
Show: failing test output · diagnosis · proposed fix. Wait for "fix it", "override", or a correction before proceeding.

**After a full slice completes**: run the task-complete checkpoint, mark the slice done in `tasks.md`, query the DB for unblocked slices, then STOP and ask for the session summary. Never generate it.

---

## Spec-kit Workflow — per slice

Slices are pre-defined in `specs/003-uipath-native/tasks.md`. Skip `/speckit.specify`.

For each slice, run in order:
1. `/speckit.plan` — paste the slice from tasks.md + tech constraints for this slice
2. `/speckit.analyze` — check plan vs spec vs data-model for inconsistencies
3. `/speckit.tasks` — break into individually testable subtasks; mark `[P]` for parallel
4. `/speckit.implement` — Spec Gate fires per function; show SPEC block, wait for LGTM

**Rule**: NEVER touch `.specify/` except via spec-kit commands. The root `tasks.md` is the master
tracker; `.specify/` is the per-slice implementation layer. Never conflate them.

---

## Session Start and End

**Every session start** — before writing any code:
```
python .agent-os/scripts/resume.py     # or:  make resume
```
Paste the output. State your understanding (completed slices, in-progress, next, carried-forward risks). Wait for the user to confirm before starting work.

**Every session end:**
```
make save-session TASK=<slice> SUMMARY="..." DECISIONS="..." BLOCKERS="..." NEXT="..."
```
The summary must be the user's words — ask for it, never generate it yourself.

---

## MCP Tools (when agent runtime supports MCP)

| Tool | Purpose |
|------|---------|
| `context7` | Up-to-date library/SDK docs — UiPath, Python stdlib, pytest, httpx |
| `ref-tools` | Token-efficient search across public + private documentation |
| `exa` | Neural semantic search (non-keyword, concept-level results) |
| `tavily` | Real-time web: regulatory citations, CVEs, UiPath release notes |

For UiPath Maestro Case V20 schema questions, always search before guessing — this schema is not reliably in training data.

Install: `bash scripts/setup-mcps.sh` (after filling in API keys in `.env`)

---

## /handoff skill — when and how to use

Run `/handoff` at these specific moments:

1. **End of every slice** — slice complete, or session ended without completing one
2. **Context pressure** — agent responses becoming less precise or repeating earlier constraints
3. **Before `/speckit.implement`** on a large slice — strip planning noise before coding starts

**The pattern** (fill in the brackets; the rest is verbatim):

```
/handoff "Completed [slice ID — slice name]. Next: [slice ID — slice name].
  Context: [one sentence about state or decisions not in tasks.md or the memory DB].
  Skills: [pick from: uipath-maestro-case / uipath-agents / uipath-coded-apps /
    uipath-maestro-bpmn / uipath-maestro-flow / uipath-api-workflow /
    baa-boundary-reasoning / audit-ip-safety]."
```

At the **next session start**: run `python .agent-os/scripts/resume.py`, paste its output,
then paste the handoff doc content. Together they replace a 20-minute re-explanation
with a 2-minute confirmation.

The handoff file is saved to OS temp (`/tmp/` on Linux/macOS, `%TEMP%` on Windows).
The agent prints the exact path when it runs.

---

## /improve-codebase-architecture skill — timing

**Do NOT run during active slice work (Slices 004–012).** The Python scaffolding is
still being built; architecture reviews need enough code to have real friction.

Run after:
- Slices 009–013 complete (all 7 agents wired + tested, BPMN + flow authored)
- Before the final polish slices (016–017)

**Setup:** `CONTEXT.md` at the repo root is already populated with domain vocabulary —
the skill reads it automatically. Update `CONTEXT.md` if domain terms evolve before
running the skill.

**Candidates the skill will likely flag** in this project:
- Coupling between the three Coded Agents if they share logic ad-hoc instead of via
  a clean internal interface in `src/cascadecare/uipath/`
- The `src/cascadecare/uipath/` wrapper being a shallow module (lots of pass-through,
  minimal encapsulation of the UiPath SDK auth flow)

---

## /improve-codebase-architecture ↔ thermo-nuclear-code-quality-review — bidirectional

These two skills are complementary and should run as a pair across the project lifecycle.

**`/improve-codebase-architecture`** — milestone-based (after Slices 013–015): finds shallow
modules, coupling, and depth opportunities in the Python scaffolding.

**`thermo-nuclear-code-quality-review`** — ongoing (every slice diff): enforces structural
excellence with seven non-negotiable standards:
1. **Structural simplification** — search aggressively for reframings that make whole branches and conditionals disappear
2. **File-size limits** — flag any file crossing 1,000 lines
3. **Spaghetti prevention** — scattered ad-hoc conditionals → dedicated abstractions
4. **Design-first bias** — structural cleanliness over "it works"
5. **Type and boundary clarity** — no unnecessary optionality, explicit typed models over loosely-shaped objects
6. **Canonical layer discipline** — no feature leakage, no canonical-helper duplication
7. **Atomic orchestration** — eliminate unnecessary sequentialization where parallel structures are cleaner

Approval is withheld unless the change: shows no structural regression · avoids obvious simplification opportunities · respects file-size boundaries · maintains clear architectural separation.

**The bidirectional loop:**
1. `/improve-codebase-architecture` identifies candidates → apply the thermo-nuclear framework to
   the proposed restructuring *before implementing* — confirm no new anti-patterns are introduced
2. After every slice diff → thermo-nuclear review → if structural smells surface → check whether
   they reveal a deeper architecture issue to queue for the next milestone
3. If thermo-nuclear flags ≥3 structural issues in one slice → trigger an early
   `/improve-codebase-architecture` run rather than waiting for the milestone

**Practical cadence:**
- Thermo-nuclear: every slice diff (ongoing, ~continuous)
- `/improve-codebase-architecture`: after Slices 013–015 (milestone-based)

---

## Constitution Principles

1. **UiPath-native first** -- Every runtime asset is a UiPath artifact. No external service runs during the demo.
2. **TDD-first** -- Write failing test before any Python code.
3. **No real company names** -- Zero tolerance. Forbidden token list enforced.
4. **Externalized agent prompts** -- All agent prompts in `agents/prompts/*.md`. Never inline.
5. **Surgical edits** -- Prefer editing over rewriting. Never overwrite without reading first.
6. **Three-level nesting honored** -- Master → parent → grandchild via native `case-management` task type. Workarounds logged in DEVIATIONS.md.
7. **Evidence provenance non-negotiable** -- Every artifact traces to source case, agent, and timestamp.
8. **Secrets via .env only** -- No secrets in code, fixtures, or committed files.
9. **knowledge/ is immutable** -- Source-of-truth docs are never modified by the build.
10. **pack-solution.sh is the only build step** -- The solution package is assembled by the script; never hand-copy caseplan.json files.
