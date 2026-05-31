# GitHub Copilot Instructions — CascadeCare Network Command

> These instructions are Copilot-specific. Universal project rules live in AGENTS.md.
> This file imports them and adds the Copilot workflow layer on top.

@AGENTS.md

---

## Architecture

CascadeCare is a UiPath Maestro Case demonstration for AgentHack 2026 Track 1.

**RUNTIME IS UIPATH. PYTHON IS BUILD-TIME ONLY.**

| Layer | Technology |
|---|---|
| Case orchestration | UiPath Maestro Case — 3 levels: master / stakeholder-parent / obligation-grandchild |
| Process model | UiPath Maestro BPMN (ideal-response happy path) |
| Demo driver | UiPath Maestro Flow (`clearflow-demo-driver`) |
| Reasoning agents (4) | UiPath Agent Builder (Claude BYO-LLM via LLM Gateway) |
| Computation agents (3) | UiPath Coded Agents / Python SDK |
| Mock external systems | Integration Service API Workflows (~13) |
| Reference data + BAAs | UiPath Data Fabric |
| Semantic retrieval | UiPath Context Grounding |
| LLM governance | UiPath Trust Layer (PHI/PII on every call) |
| HITL | UiPath Action Center |
| Narrative UI | UiPath Apps |
| Build-time Python | `uv` + `pytest` + `ruff` + `mypy` |

**No FastAPI. No LangGraph. No PostgreSQL. No Next.js.**
Those were removed in Slice 004 (2026-05-26 pivot). The current canonical spec is
`specs/003-uipath-native/`.

---

## Session start — every session

Before writing a single line of code:

```bash
python .agent-os/scripts/resume.py     # or:  make resume
```

Paste the output as the **first message** in the session. Tell me:
- What you understand the current state to be (completed slices, in-progress, next)
- Any risks or open decisions carried forward

I will confirm or correct before we start. **Do not begin work until confirmed.**

---

## Spec-kit workflow — per slice

Slices are already planned in `specs/003-uipath-native/tasks.md`. Skip `/speckit.specify`.

For each slice (or half-slice if large), run in order:

```
1. /speckit.plan        paste the slice from tasks.md + tech constraints for this slice
2. /speckit.analyze     check plan vs spec vs data-model for inconsistencies
3. /speckit.tasks       break into subtasks with [P] for parallel; each must be testable
4. /speckit.implement   Spec Gate fires per function — show SPEC block, wait for LGTM
```

**Hard rule**: NEVER touch `.specify/` except via spec-kit commands.
The root `tasks.md` is the master slice tracker. Spec-kit's `.specify/` is the
implementation detail layer. Never conflate them.

---

## Spec Gate — per function (fires inside /speckit.implement)

Before writing ANY function, show this block and wait for "LGTM":

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

**HIGH RISK functions** (Coded Agents, caseplan.json logic, auth/OAuth flows):
also enumerate every failure mode and how each is handled.

---

## Autopilot (yolo) protocol

When I say **"autopilot"** or **"yolo"**, run the subtask → checkpoint → next-subtask
loop automatically. Three things halt autopilot — nothing else does:

1. A failed acceptance test (checkpoint PASSED=0)
2. A Spec Gate function waiting for my LGTM
3. A session-summary request after a full slice completes

### Passing subtasks (automatic — no prompt needed)

```bash
make checkpoint TASK=<id> NAME=<subtask> PASSED=1 DETAILS="<one sentence>"
```

Proceed immediately to next subtask. Silent.

### Failing subtasks (halt)

```bash
make checkpoint TASK=<id> NAME=<subtask> PASSED=0 DETAILS="<what failed>"
```

Then show:
1. The failing test output
2. Your diagnosis of the cause
3. Your proposed fix

Wait for me to say "fix it", "override", or give a correction. Do not proceed.

### Slice complete (all subtasks passed)

1. Mark slice complete in `tasks.md` (today's date)
2. `make checkpoint TASK=<id> NAME=slice_complete PASSED=1 DETAILS="all acceptance criteria met"`
3. Query DB for unblocked slices; tell me what's next
4. **STOP** and ask me for the session summary with exactly this prompt:

> "Slice `<id>` is complete. Please provide the session summary so I can save it.
> Do not generate it for me — these are your words, not mine.
>
> SUMMARY (what was built, what you found, any surprises):
> DECISIONS (non-obvious choices + rationale):
> BLOCKERS (anything unresolved):
> NEXT (which slice to start next):"

5. After I provide values, run `make save-session` with **exactly** what I typed.

**Never auto-generate the session summary.** Always ask me.

---

## Session end — every session

```bash
make save-session TASK=<slice_id> SUMMARY="..." DECISIONS="..." BLOCKERS="none" NEXT="<next>"
```

Write the summary yourself (2–4 sentences). What was built, what was found, any surprises.

---

## MCP tools available in this project

Use these proactively — don't guess when documentation is a search away:

| MCP | When to use |
|-----|-------------|
| `context7` | UiPath SDK docs, Python library docs (uipath, pytest, httpx, ruff) |
| `ref-tools` | Token-efficient search across public + private technical docs |
| `exa` | Neural semantic search when keyword search misses the right result |
| `tavily` | Real-time web: regulatory citations, UiPath release notes, CVE lookups |

For UiPath Maestro Case V20 schema questions, always search `context7` or `ref-tools`
before guessing — that schema is not reliably in your training data.

---

## Memory commands (quick reference)

```bash
make resume                                         # session start
make load-context                                   # alias for resume
make checkpoint TASK=S013 NAME=step PASSED=1 DETAILS="..."
make checkpoint TASK=S013 NAME=step PASSED=0 DETAILS="..."
make save-session TASK=S013 SUMMARY="..." DECISIONS="..." BLOCKERS="..." NEXT="S014"
make log-decision TASK=S013 DECISION="..." RATIONALE="..." ALT="..."
make init-db                                        # first-time or if DB is lost
```

---

## /handoff skill — use at slice boundaries

Run `/handoff` at:
- End of every working session (slice complete or mid-slice)
- Before context feels sluggish (less precise answers = context window pressure)
- Before `/speckit.implement` on any large slice (strip planning noise)

**Pattern:**

```
/handoff "Completed [slice ID — name]. Next: [slice ID — name].
  Context: [one sentence: non-obvious state not in tasks.md or memory DB].
  Skills: [uipath-maestro-case / uipath-agents / uipath-coded-apps / etc.]"
```

At the **next session**: `make resume`, paste output, then paste the handoff doc.
Total resume time: under 2 minutes.

The handoff file is saved to OS temp. Copilot prints the path when it runs.

---

## /improve-codebase-architecture skill — timing

**Do NOT run during active slice work.** Python scaffolding must be substantive first.

Run after Slices 009–013 complete (all 7 agents wired + tested, BPMN + flow authored),
before the final polish slices.

`CONTEXT.md` (domain vocabulary) is already populated. Update it if domain terms evolve
before running the skill.

---

## /improve-codebase-architecture ↔ thermo-nuclear-code-quality-review — bidirectional

These two skills are complementary and run as a pair across the project lifecycle.

**`/improve-codebase-architecture`** (milestone-based, after Slices 013–015): identifies shallow
modules, coupling, and depth opportunities across the Python scaffolding.

**`thermo-nuclear-code-quality-review`** (ongoing, every slice diff): enforces structural
excellence with seven non-negotiable standards:
1. Structural simplification — reframe to make whole branches disappear
2. File-size limits — flag any file crossing 1,000 lines
3. Spaghetti prevention — scattered conditionals → dedicated abstractions
4. Design-first bias — structural cleanliness over "it works"
5. Type and boundary clarity — no unnecessary optionality, explicit typed models
6. Canonical layer discipline — no feature leakage, no helper duplication
7. Atomic orchestration — eliminate unnecessary sequentialization

Approval withheld unless: no structural regression · obvious simplifications not skipped ·
file-size boundaries respected · clear architectural separation maintained.

**The bidirectional loop:**
1. `/improve-codebase-architecture` identifies candidates → apply thermo-nuclear to the proposed
   restructuring *before implementing* — confirm no new anti-patterns are introduced
2. Every slice diff → thermo-nuclear review → structural smells → check if they reveal a deeper
   architecture issue to queue for the next `/improve-codebase-architecture` milestone
3. If thermo-nuclear flags ≥3 issues in one slice → trigger an early architecture review rather
   than waiting for the milestone

**Practical cadence:**
- Thermo-nuclear: every slice diff (ongoing)
- `/improve-codebase-architecture`: after Slices 013–015 (milestone)

---

## Protected files — immutable, enforced by hooks

| File / path | Why |
|---|---|
| `knowledge/*` | Source-of-truth docs, never modified by build |
| `maestro_case/*/content/caseplan.json` | Canonical sources; solution copy generated by `pack-solution.sh` |
| `.agent-os/memory/project_memory.db` | Session state — only via helper scripts |

Edits to these paths are **blocked** by the PreToolUse hook in `.claude/settings.json`
(exit code 2 = hard block). On non-Claude agents, the AGENTS.md instruction applies.

---

## IP safety — zero tolerance

Forbidden tokens (case-insensitive, substring match):

```
zelis, aetna, cigna, unitedhealth, bcbs, hartley, rivet, zipp, zapp,
change healthcare, optum, cotiviti, wex
```

Also forbidden: real patient names, real claim numbers or NPI numbers,
real litigation case references, any identifiable real-world healthcare entity.

Run `make audit` before every commit. The pre-commit hook also enforces this.

---

## Stop conditions — ask human before proceeding

1. A clarifying question would change more than 2 files
2. A regulatory citation cannot be verified against `knowledge/` sources
3. A dependency not in `pyproject.toml` is needed
4. Any change touches `knowledge/`
5. Acceptance criteria are ambiguous or contradictory
6. IP safety check would fail

---

## Active slice state (as of 2026-05-30)

Slices 004–012 complete. See `specs/003-uipath-native/tasks.md` for the full slice list.

| Reference | Path |
|---|---|
| Slice plan (active) | `specs/003-uipath-native/tasks.md` |
| Full plan | `specs/003-uipath-native/plan.md` |
| Data model | `specs/003-uipath-native/data-model.md` |
| Case vocabulary | `specs/003-uipath-native/case-vocabulary.yaml` |
