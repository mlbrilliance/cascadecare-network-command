# Claude Code Foundation Bootstrap — CascadeCare / Cascade Command

> Paste everything below after your `/grill-with-docs` command. Enter Plan Mode (Shift+Tab twice) before sending. Toggle extended thinking on (Alt+T / Option+T). Use the word **ultrathink** to maximize reasoning depth on the planning pass.

---

## 1. Your Role

You are the **lead architect and tech program manager** for a 7-week solo hackathon build that needs to win UiPath AgentHack 2026 Track 1 ($50K) and serve as the lighthouse demo at UiPath FUSION 2026. The human is Nick Sudh, an RPA/agentic engineering practitioner at WEX Inc. You are operating in **Plan Mode**. Do not write code, edit files, or run any tool that mutates state until you have produced a complete plan, surfaced every ambiguity, and the human has explicitly approved the plan.

Your output for this session is a **foundation plan** that another set of AI agents (downstream subagents, Codex, GitHub Copilot, Cursor, future Claude Code sessions) can pick up and execute against. The artifacts you produce in the *next* session (after plan approval) must be self-contained enough that those downstream agents need zero additional context.

---

## 2. Mission

Build **a working UiPath Maestro Case + Maestro Apps demonstration of healthcare financial shockwave orchestration** — the case layer that opens when a provider cyber event becomes a multi-party claims, payments, IDR, evidence, regulatory, and litigation crisis seen first by a healthcare payment intermediary.

The build must demonstrate case-shape complexity that BPMN cannot model: evolving case goals, evolving participant roles, multi-level case nesting, cross-case evidence sharing with privilege-aware access, and non-sequential human approval gates.

Target outcomes, ranked:

1. **Win AgentHack 2026 Track 1.** Submission per https://forum.uipath.com/t/uipath-agenthack-is-live-50-000-in-prizes-three-tracks-and-7-weeks-to-build/5746132.
2. **Earn the FUSION 2026 lighthouse showcase slot.** This means the demo and narrative must be keynote-grade, not engineer-grade.
3. **Stand as a reusable reference architecture** for any B2B intermediary navigating a multi-customer cascade crisis. Healthcare is the demo vertical; the pattern generalizes.

---

## 3. Inputs — Read in This Order

Read every file in `@knowledge/` in this exact order, with this exact emphasis:

1. **`@knowledge/REQUIREMENTS.md`** — **AUTHORITATIVE on architecture, agent topology, case-shape patterns, three-level case nesting, acceptance criteria, IP-safety posture, regulatory citations.** When in conflict with the other two, this wins.
2. **`@knowledge/multi-vector-healthcare-cyber-crisis-prd.md`** — Supplementary on regulatory anchors (HIPAA, NSA IDR, SEC, FCA), participant taxonomy, agent responsibility detail, mock API endpoint shapes, and synthetic data file list.
3. **`@knowledge/healthcare-shockwave-build-brief.md`** — Supplementary on UI/UX requirements (Command Center, Shockwave Timeline, Child Case Board, Participant Graph, Evidence Graph, Decision Modal, Executive Brief), demo event button sequencing, and visual design register.

Then read the screenshots in `@knowledge/screenshots/` for the Maestro/Maestro Case UI patterns you must echo.

Then consult these external references (do not block on them — read them once for context, then stop):

- https://docs.uipath.com/maestro/automation-cloud/latest/user-guide/overview (Maestro core docs)
- https://www.uipath.com/blog/product-and-updates/introducing-maestro-case-new-uipath-capability (Maestro Case announcement)
- https://www.uipath.com/platform/agentic-automation/agentic-orchestration (Agentic orchestration positioning)
- https://www.linkedin.com/posts/adam-mancino-bab42021_uipath-just-announced-maestro-case-a-major-share-7460717979413024768-1FHg/ (additional Maestro Case context)

**Maestro Case is in preview.** Official documentation may be incomplete. Where official docs are silent, defer to Maestro core docs (BPMN, event-sourced backbone, Action Center HITL, Process Apps for UI). Log any preview-version gaps in `DEVIATIONS.md` as you encounter them.

---

## 4. Known Conflicts You Must Surface Before Planning

The three knowledge docs contain unresolved naming conflicts. **Do not silently pick one set.** Surface these to the human using the `AskUserQuestion` tool during the grill phase. Present the conflict, recommend a resolution, ask for explicit confirmation.

| Element | REQUIREMENTS.md (authoritative) | PRD + Build Brief (supplementary) |
|---|---|---|
| Project name | Cascade Command | CascadeCare Network Command |
| Protagonist intermediary | Stratos | ClearFlow Health Network |
| Stratos product names | Stratos Pricing Engine (SPE), Stratos Payment Network (SPN) | (not specified by these names) |
| Triggering provider(s) | Abstract: Provider Customer Alpha, Beta, Gamma, Delta, Epsilon, Zeta | Named single hospital: Northstar Regional Health |
| Crisis shape | Multi-customer cascade (3–6 simultaneous provider crises with correlation analysis) | Single-provider shockwave (Northstar) with downstream cascade across payer ecosystem |
| Payer customers | Sentinel Health, Liberty Health Plans, Cornerstone Health, Highland Blues TN/MS | Apex Health Plan, Union Prairie Benefits, SummitBlue Medicare Advantage, Lakeshore TPA Services |
| Signature agent | Multi-Customer Pattern Detector (correlation across simultaneous customer anomalies) | Network Flow Anomaly Agent (claim/remittance/IDR anomaly explanation) |
| Attack vector | Nimbus Patient Engagement Platform (revealed as shared third-party vendor) | Ransomware at Northstar (no shared-vendor reveal) |
| Case nesting | Three levels: master → parent → grandchild | Two levels: parent → child |
| Number of demo reversals | Five | Seven |

**Recommended resolution** (state this clearly when grilling the human):

- Keep **REQUIREMENTS.md's three-level nesting, multi-customer cascade thesis, and five-reversal structure** — these are the structural differentiators that make this Maestro Case-native rather than BPMN-shaped.
- Adopt the **PRD's regulatory citations, agent responsibility detail, and mock API endpoint shapes** — these are sharper than what's in REQUIREMENTS.md.
- Adopt the **Build Brief's UI/UX taxonomy and visual register** — these are the strongest UI direction in the three docs.
- For names, ask the human to pick **one** of the following options:
  - **Option A — Honor REQUIREMENTS.md as-stated:** Cascade Command / Stratos / Alpha–Zeta / Nimbus / Sentinel + Liberty. Treat the PRD and Build Brief as superseded on names.
  - **Option B — Honor the newer Build Brief naming:** CascadeCare Network Command / ClearFlow / Northstar (single triggering provider) / Apex + Union Prairie + SummitBlue + Lakeshore. Treat REQUIREMENTS.md as superseded on names but keep its architecture.
  - **Option C — Hybrid:** CascadeCare Network Command (better brand) / ClearFlow Health Network (better protagonist name for the demo) / abstract Greek-letter provider customers Alpha–Zeta plus Northstar as the *named* lead-affected provider (sharpens the demo without losing the multi-customer cascade pattern) / Apex/Union Prairie/SummitBlue/Lakeshore payers / Nimbus as vendor.

**State the recommendation: Option C.** It preserves the keynote-grade brand from the PRD, preserves the multi-customer architectural complexity from REQUIREMENTS.md, and lets the demo open on a specific named provider (more emotional anchor) while still demonstrating cross-customer correlation when additional Greek-letter providers surface in Reversal 1.

Do not advance to planning until the human picks A, B, or C.

---

## 5. This Session's Output

This session produces **a plan and a foundation, not the build**. The build executes in subsequent sessions, gated phase-by-phase.

### 5.1 Plan Mode deliverables (this turn)

Produce, in plan-mode output:

1. **Conflict resolution summary** — three options surfaced, your recommendation stated, awaiting human decision.
2. **Confirmed project context** — committed name, protagonist, provider customer convention, payer roster, agent roster, signature agent, number of reversals, case nesting depth. Do not write to disk yet; just state it back to the human.
3. **Foundation Phase plan** — exactly what files you will create/update in the foundation phase (next section lists these), with one-paragraph descriptions of contents.
4. **Open clarifying questions** — surfaced via `AskUserQuestion`, in priority order. Maximum 5 at a time.
5. **Identified risks** specific to a 7-week solo build with Maestro Case in preview.

### 5.2 Foundation Phase deliverables (next session, after human approves the plan)

Once the plan is approved and you exit Plan Mode, you will produce the following files in one disciplined session. **All other build work is deferred until these foundation files exist and the human has reviewed them.**

| Path | Purpose | Owner of source content |
|---|---|---|
| `CLAUDE.md` | Always-loaded Claude Code instructions: project intent in 3 paragraphs, naming conventions, IP-safety rules, file/folder conventions, "never modify" paths, default behaviors, escalation rules. Keep under 200 lines — this consumes context every turn. | You synthesize from REQUIREMENTS.md + PRD + Build Brief + resolved names. |
| `AGENTS.md` | OpenAI Codex / agents.md convention equivalent of CLAUDE.md, covering same ground in tool-agnostic phrasing so Codex, Cursor, Windsurf, Copilot CLI can pick the project up. | Mirror CLAUDE.md content in tool-agnostic phrasing. |
| `.github/copilot-instructions.md` | GitHub Copilot Chat instructions — same essence as CLAUDE.md but in Copilot's expected format. | Mirror CLAUDE.md content. |
| `docs/overview.md` | Executive-grade project overview: problem statement, protagonist, thesis, what makes this a Maestro Case use case rather than a BPMN use case, success criteria, who this is for. ~600 words. | Compress REQUIREMENTS.md sections 1–2 + Build Brief positioning. |
| `docs/architecture.md` | Full technical architecture: layer diagram, three-level case structure, agent topology (LangGraph runtime + master/child/specialized agent hierarchy), robot inventory, mock external systems, data layer, UI surfaces (Process Apps preferred, Next.js fallback), Maestro Case + Process Apps + Data Fabric + Action Center integration map. Include the architecture diagram from REQUIREMENTS.md §4.2 as ASCII; add an SVG version to `docs/images/architecture.svg`. | Compress REQUIREMENTS.md §4–9 + PRD §13–14. |
| `docs/usage-examples.md` | Worked walkthroughs: (a) the 3-minute demo flow with what the operator sees on each screen, (b) how to trigger each demo event button locally, (c) how to run the agent runtime standalone for testing, (d) how to export an evidence pack. | New — synthesize from PRD §8 (reversals) + Build Brief demo buttons. |
| `.vscode/tasks.json` | VS Code tasks for common ops: `seed-synthetic-data`, `run-mocks`, `run-agents`, `run-ui`, `run-demo`, `run-tests`, `lint`, `typecheck`, `export-evidence-pack`, `reset-demo-state`. Each task documented with `detail`. | New. |
| `pyproject.toml` | Python project config using `uv` or `poetry` (pick `uv` — faster, modern). Dependencies: `fastapi`, `uvicorn`, `langgraph`, `langchain-anthropic`, `anthropic`, `pydantic`, `sqlalchemy`, `psycopg[binary]`, `lancedb`, `polars` or `pandas`, `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`, `pytest-cov`, `faker`. Python 3.12 minimum. Strict ruff + mypy configs. Pre-commit hook integration. | New. |
| `tasks.md` (root) | **Master Build Roadmap.** Slice-level dependency map across the entire 7-week project. Each slice has: ID, name, owner, status (pending/in-progress/done/blocked), dependencies (other slice IDs), acceptance criteria reference, link to its spec-kit feature directory. **This is distinct from spec-kit's per-feature `specs/{id}/tasks.md` files** — that confusion must be called out at the top of this file. | New. |
| `.specify/memory/constitution.md` (spec-kit) | The project's "constitution" — immutable principles spec-kit enforces on every change: TDD-first (write failing test before any code), no real-company names in any artifact, prefer surgical edits over rewrites, all agent prompts externalized to `agents/prompts/*.md`, all secrets via `.env` only, Maestro Case three-level nesting honored or workaround logged in DEVIATIONS.md, evidence pack provenance non-negotiable. | New — derive from REQUIREMENTS.md §0, §11.3, §13, §14. |
| `DEVIATIONS.md` | Empty initially. Heading and table format: `Date | Slice | Spec section | Deviation | Rationale | Approved by`. | New. |
| `README.md` | Top-of-repo orientation: 30-second pitch, repo map, quickstart, link to docs, link to demo video (placeholder URL). | New. |

### 5.3 Spec-kit initialization (foundation phase)

Run `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` and then initialize the project: `specify init --here --ai claude`. This creates `.specify/`, `.claude/commands/speckit.*`, and the templates directory.

After initialization, populate `.specify/memory/constitution.md` per section 5.2 above and verify the `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.clarify`, `/speckit.analyze`, `/speckit.implement` commands are registered. Do **not** run `/speckit.specify` or beyond in the foundation phase — those are per-slice operations.

### 5.4 Claude Code extensions to install (foundation phase)

Install these into the project's `.claude/` directory. Each is justified — do not install Claude Code extensions speculatively.

**Skills (`.claude/skills/`)** — on-demand domain knowledge:

| Skill | Purpose | Trigger |
|---|---|---|
| `baa-boundary-reasoning` | How to reason about a single regulatory inquiry against multiple differing BAA terms; produces structured per-customer disclosure analyses. | Activated when BAA Boundary Reasoner Agent runs or when a regulatory inquiry hits multiple affected provider customers. |
| `case-shape-patterns` | The six case-shape patterns Maestro Case must demonstrate. Includes worked examples of each. | Activated when designing any new case stage, child case, or grandchild case. |
| `synthetic-baa-author` | How to author plausible, materially-differing BAA terms across 6 provider customers so Reversal 3 (six legal answers to one subpoena) lands. | Activated during synthetic data generation slices. |
| `demo-rehearsal-runner` | How to dry-run the 3-minute demo end-to-end against the local stack, including expected state transitions per second. | Activated when rehearsing or testing the demo runner. |
| `regulatory-citer` | How to cite US healthcare regulatory sources (HIPAA, NSA IDR, SEC 1.05, FCA Civil Cyber-Fraud) precisely without making up case numbers or settlement amounts. | Activated whenever regulatory text appears in code, prompts, or docs. |

Each skill is a directory with `SKILL.md` containing a name, description (the trigger phrase), and the instructions Claude loads on activation. Skills cost ~100 tokens each at startup (name + description only). Load on demand.

**Subagents (`.claude/agents/`)** — specialized sub-Claude instances for delegated investigation:

| Subagent | Purpose | When to dispatch |
|---|---|---|
| `bpmn-modeler` | Reads UiPath Maestro docs and writes BPMN sub-flow JSON for a given deterministic action (subpoena distribution, regulator notification, BAA-compliance check). | When a slice introduces a new BPMN sub-flow under a case stage. |
| `agent-prompt-author` | Writes externalized agent prompt files at `agents/prompts/*.md` per the skeleton in REQUIREMENTS.md §7.4. | When implementing a new specialized agent. |
| `mock-service-author` | Generates a FastAPI mock service per the API endpoint shapes in the PRD §14.3, with deterministic fixtures and realistic latency. | When implementing a new mock external system. |
| `evidence-schema-author` | Designs the cross-case shared evidence schema with privilege-aware access scopes, per case-shape pattern 4. | One-time during foundation; revisited if evidence model needs to evolve. |

**Hooks (`.claude/settings.json`)** — deterministic enforcement that doesn't depend on Claude remembering:

| Hook | When | What it does |
|---|---|---|
| `PreToolUse` on `Write`/`Edit` to `knowledge/**` | Before write | Block all writes to knowledge/ — these are source-of-truth docs, never mutated by the build. |
| `PreToolUse` on `Write` to any new source file in `agents/`, `shim/`, `mocks/` | Before write | Require that a corresponding test file already exists in `tests/`. TDD enforcement. |
| `PostToolUse` on `Edit` to `tasks.md` | After write | Validate that all slice IDs are unique and all dependencies reference existing slices. |
| `PostToolUse` on any `pytest` run | After run | If green, prompt Claude to mark the current slice's status in `tasks.md`. If red, prompt to surface the failure. |
| `PreToolUse` on git commit | Before commit | Block commit if `tasks.md` not updated since last code change OR if any `agents/prompts/*.md` was modified without a corresponding test update. |

**Custom slash commands (`.claude/commands/`)** — beyond `/grill-with-docs`:

| Command | Purpose |
|---|---|
| `/start-slice <slice-id>` | Reads `tasks.md`, fetches the named slice, verifies its dependencies are `done`, sets status to `in-progress`, opens the slice's spec-kit feature directory, runs `/speckit.specify` if not yet specified. |
| `/finish-slice <slice-id>` | Runs the slice's acceptance tests, if green marks `done` in `tasks.md`, generates a one-paragraph completion summary in `docs/changelog.md`, commits with a structured message. |
| `/rehearse-demo` | Resets demo state, runs the demo timeline runner end-to-end, captures the case state at each reversal, produces a Markdown report comparing actual vs. expected per Reversal acceptance criteria. |
| `/audit-ip-safety` | Greps the entire repo for any of: Zelis, Aetna, Cigna, UnitedHealthcare, BCBS, Hartley, Rivet, ZIPP, ZAPP, plus any real patient names or real claim numbers. Fails loudly if any are found. Runs as part of pre-submission checks. |

---

## 6. Process — How to Run This Plan-Mode Session

### Step 1: Ultrathink-pass read

**Ultrathink.** Allocate maximum reasoning budget. Read all three knowledge docs in the order specified. Read the screenshots. Skim the four URLs (don't deep-dive). Build a complete mental model of: protagonist, case shape, agent topology, demo choreography, regulatory anchors, UI surfaces, naming tension, IP-safety posture, build phases.

Internal sanity check before producing output: Can I explain this project's thesis in one sentence? Can I name the five (or seven) reversals from memory? Can I list every file I'm about to create and why each one matters? If no, re-read.

### Step 2: Conflict surfacing via AskUserQuestion

Use `AskUserQuestion` to surface the naming conflict (section 4 above) and at most 4 additional clarifying questions. Limit yourself to 5 questions total in the first batch. Examples of the kinds of questions worth asking:

- "Project name and protagonist: Option A (Cascade Command / Stratos / Alpha–Zeta), Option B (CascadeCare Network Command / ClearFlow / Northstar), or Option C (hybrid: CascadeCare / ClearFlow / Northstar + Alpha–Zeta cascade)?"
- "Python dependency manager: uv (recommended, modern) or Poetry (more familiar)?"
- "UI framework: UiPath Process Apps native (preferred, judges will favor it), Next.js fallback (more visual control), or build both in parallel?"
- "Should the demo open from Stratos/ClearFlow's claim-flow telemetry (case-shape native) or from a SIEM alert at the provider (more familiar to cyber audiences)?"
- "Demo richness: 3 full provider crises + 3 surfacing (recommended), or all 6 in full parallel (visually richer, slower to build)?"

Wait for human responses before continuing. Do not invent answers.

### Step 3: Present the foundation plan

After receiving answers to step 2, present:

- Confirmed names, protagonists, and conventions (in a small table)
- Full foundation file list per section 5.2 with one-line descriptions
- Spec-kit initialization steps per 5.3
- Claude Code extension installation list per 5.4
- The Master Build Roadmap structure: slice count estimate, week-by-week phasing, critical path
- Specific risks with mitigations: Maestro Case preview gaps, three-level nesting workarounds, 7-week solo capacity, demo rehearsal time required

### Step 4: Gate

Stop. Wait for explicit human approval ("approved" or "yes, execute the foundation"). Do not exit Plan Mode without it.

### Step 5: After approval

Exit Plan Mode. Execute the foundation phase as one disciplined session. Run `pytest` and `ruff check` after the session. Surface anything that didn't land. Report back: "Foundation phase complete. Ready for slice 001." Do not advance to any build slice until the human approves the foundation artifacts.

---

## 7. Master Build Roadmap structure (for `tasks.md`)

Use this structure for `tasks.md`. Each slice is 1–3 days of focused work for a solo builder.

```markdown
# Master Build Roadmap — [project name]

> Note: This file is the slice-level project roadmap. Per-feature task breakdowns
> live inside `specs/{slice-id}/tasks.md` and are generated by `/speckit.tasks`.

## Legend
- Status: pending | in-progress | done | blocked
- Owner: claude-code | human | downstream-agent

## Critical path
[ASCII or Mermaid diagram of slice dependencies]

## Slices

### Slice 001 — Repo Scaffolding
- Status: pending
- Owner: claude-code
- Depends on: (none)
- Acceptance: REQUIREMENTS.md §13.1 functional acceptance items 1–2
- Spec-kit feature: `specs/001-repo-scaffolding/`
- Estimate: 1 day

### Slice 002 — Maestro Case Three-Level Schema (PostgreSQL)
- Status: pending
- Owner: claude-code
- Depends on: 001
- Acceptance: REQUIREMENTS.md §6.1 and §13.2 acceptance items 1, 4
- Spec-kit feature: `specs/002-case-three-level-schema/`
- Estimate: 2 days
- Risk: Maestro Case preview may not natively support 3 levels; design schema to be Maestro-agnostic for now.

[... continue for all slices ...]
```

Approximate slice inventory (you may refine in plan-mode output):

1. Repo scaffolding (foundation done = prerequisite, not a slice)
2. Three-level case schema in Postgres + relationship model
3. FastAPI shim + Maestro webhook handlers (stubs)
4. Mock external systems wave 1: provider customers Alpha–Zeta
5. Mock external systems wave 2: payers + Nimbus + regulators + insurer
6. Synthetic data: provider profiles, BAA terms (the differentiating ones), claim flow telemetry baseline and attack-day
7. LangGraph runtime + master case manager agent (stubbed reasoning)
8. Claim Flow Anomaly Detector + Multi-Customer Pattern Detector (Reversal 1 fires)
9. Forensic Self-Exam + Vector Hypothesis (Reversal 2 fires)
10. BAA Boundary Reasoner with Claude Code runtime integration (Reversal 3 — coding agent bonus moment)
11. Multi-Party Fiduciary Conflict Detector (Reversal 4 fires)
12. Negligent Monitoring Risk + litigation defense child case (Reversal 5 fires)
13. Case UI v1: Command Center, Shockwave Timeline, Child Case Board (Process Apps or Next.js)
14. Case UI v2: Participant Graph, Evidence Graph with privilege filters
15. Case UI v3: Agent Workspace, Decision Modal, Executive Brief
16. UiPath robots: BPMN sub-flows for subpoena fanout, regulator notification, BAA-compliance check, evidence pack export
17. Demo runner with deterministic time-lapse + reversal triggers
18. Evidence pack export with provenance manifest
19. Acceptance test suite covering all five reversals end-to-end
20. Demo polish: visual design, voiceover script, 3-minute video recording
21. Submission package per AgentHack Devpost requirements

---

## 8. Constraints and Guardrails

These are non-negotiable. Encode them in `CLAUDE.md` and `.specify/memory/constitution.md`.

**IP safety:**
- No real company names anywhere — code, mocks, fixtures, UI strings, demo voiceover, slide decks, README, README screenshots, any artifact.
- Forbidden tokens (case-insensitive grep): `zelis`, `aetna`, `cigna`, `unitedhealth`, `bcbs`, `hartley`, `rivet`, `zipp`, `zapp`, `change healthcare`, `optum`, `cotiviti`, plus any real patient name or real claim number patterns.
- The `/audit-ip-safety` slash command must run green before any commit on the submission branch.

**TDD:**
- Every code file under `agents/`, `shim/`, `mocks/` requires a corresponding test file. The pre-commit hook blocks if missing.
- Every reversal requires an end-to-end acceptance test in `tests/demo/test_all_reversals.py`.
- Test before code. Hook enforces order.

**Surgical edits:**
- Prefer `Edit` over `Write` when modifying existing files. Never overwrite a file you haven't first read in the current session.
- Refactors >10 files require an entry in `DEVIATIONS.md` first.

**Externalized prompts:**
- All agent prompts live in `agents/prompts/*.md`. Never inline a prompt in Python code.
- Each prompt file follows the skeleton in REQUIREMENTS.md §7.4.

**Maestro Case preview gaps:**
- Whenever a Maestro Case API turns out to be unavailable, missing, or behaves differently than documented, log in `DEVIATIONS.md` with: date, what you tried, what you saw, what workaround you used.
- For three-level nesting specifically: if Maestro Case only supports two levels, implement the third via case-relationship metadata in PostgreSQL with the UI rendering the third level visually. Do not block the build on this.

**Stop conditions:**
- Stop and ask the human if: a clarifying question would change >2 files, you encounter a regulatory citation you can't verify, you would need to install a dependency not in `pyproject.toml`, you would need to modify anything in `knowledge/`, or a phase's acceptance criteria are ambiguous.

---

## 9. Definition of Done — This Foundation Session

Before declaring the foundation phase complete:

- [ ] All files in section 5.2 exist with substantive content (not stubs).
- [ ] Spec-kit is initialized; `/speckit.constitution` was run and `.specify/memory/constitution.md` populated.
- [ ] All Claude Code skills, subagents, hooks, and slash commands per section 5.4 are installed and validated.
- [ ] `tasks.md` lists all slices with dependencies mapped, critical path identified, week-by-week phasing visible.
- [ ] `pytest` runs (even with zero tests yet) — environment is sane.
- [ ] `ruff check` and `mypy` run on the empty scaffolding without errors.
- [ ] `/audit-ip-safety` runs green.
- [ ] A git commit titled `foundation: cascade command bootstrap complete` is made.
- [ ] You produce a summary report listing: every file created, every extension installed, the next 3 slices to start with, the first major risk identified during the build.

After producing the summary, **stop and wait**. Do not start slice 001 without explicit human go-ahead.

---

## 10. Reminders

- **Plan Mode is read-only**. Do not edit anything until the human approves the plan and you exit Plan Mode.
- **Ultrathink** on the first reading pass and the conflict-resolution analysis. Normal thinking is sufficient for the foundation execution.
- **One question batch at a time**, max 5. Wait for answers.
- **You are not the writer of the next several months of this codebase** — you are the architect setting it up so any downstream agent can pick it up. Optimize for clarity of intent and discoverability of context, not for cleverness.
- **The human paid 50K in opportunity cost to get here**. The protagonist shifts, the naming iterations, the regulatory research — that's done. Your job is to ship.

Begin with the ultrathink read. Surface conflicts. Ask up to 5 questions. Wait.
