---
description: "Slice 017 — Submission package (offline portion) implementation tasks"
---

# Tasks: Slice 017 — Submission Package

**Input**: `specs/003-uipath-native/tasks.md` §Slice 017; `CODING_AGENTS.md`;
`CLAUDE_CODE_USAGE.md`; `specs/003-uipath-native/data-model.md`; the 27 built UiPath artifacts.

**Goal**: The offline-completable Devpost submission artifacts are DONE and machine-verified —
a README that names every UiPath component (judge inventory) and reflects the **real** built
state, a confirmed MIT LICENSE, and a README-completeness TDD gate. Human-capture artifacts
(Devpost page, 5-min live demo video, deck) are scaffolded with honest status and carried forward.

> **Convention note (recorded Slice 016 decision):** `setup-plan.sh` clobbers the shared
> `plan.md`, so this slice's plan/analyze/tasks are authored directly into this file, exactly as
> slices 013/015/016 were. The shared `plan.md` remains the canonical pure-UiPath pivot plan.

---

## /speckit.plan — approach

**Why this slice exists.** The current `README.md` (105 lines) was written at Slice ~004 and is
now materially **dishonest about state**: it marks Slices 005–016 as "planned" when every one of
those artifacts has been authored and offline-validated. A Devpost judge reading it would
conclude the project is a skeleton. The submission requirement is the opposite: the README must
inventory **every** UiPath component so judges can confirm breadth, while staying honest about
what is live-on-tenant vs. authored-offline-pending-publish.

**Strategy.** Drive the inventory from the filesystem, not from memory. A pytest gate enumerates
the real artifact directories and asserts each slug appears in the README; static domain lists
(Data Fabric entities, Context Grounding indexes, Trust Layer pools) — which are *specified* in
`data-model.md` rather than being standalone runtime files — are checked against a frozen list.
This makes "names every component" machine-checked and self-maintaining: add an API workflow,
the gate fails until the README names it.

**Honesty repairs found during analyze (must fix in the rewrite):**
1. `scripts/seed_data_fabric.sh` is referenced by both the old README quickstart **and**
   `CODING_AGENTS.md`, but **does not exist** (`scripts/` has `gen_api_entry_points.py`,
   `pack-solution.sh`, and tooling only). Data Fabric entities are *specified* in `data-model.md`;
   seeding is not yet scripted. The README must not imply a runnable seed step that has no script.
2. Runtime status: the honest framing is "authored + offline-validated; tenant publish/run
   tracked in `DEVIATIONS.md` + run-playbook" — not "planned", and not "live" (open install
   blockers remain: API entry-points re-add, Maestro folder context, BPMN 1654 — per
   `slice014-deploy-findings` + run-playbook).

**Out of scope (human-capture, carried forward):** recording the 5-min demo on UiPath Automation
Cloud, the Devpost project page, the slide deck, the 1-min coding-agent reel, and the
`agenthack-2026-submission` git tag (the tag asserts a recorded live demo exists — it must not be
applied from an offline session).

---

## /speckit.analyze — canonical component inventory (source of truth for README + gate)

Enumerated from the repo on 2026-05-31. **27 core artifacts** + domain assets.

### Maestro Cases (3) — `maestro_case/<slug>/content/caseplan.json`
- `clearflow-master-crisis`
- `clearflow-stakeholder-parent`
- `clearflow-obligation-grandchild`

### Agent Builder agents (4, low-code, Claude BYO-LLM) — `agents/<slug>/agent.json`
- `vector-hypothesis-agent`
- `baa-boundary-reasoner` (+ Context Grounding on `BAA-corpus`)
- `fiduciary-conflict-detector`
- `negligent-monitoring-risk-agent`

### Coded Agents (3, Python SDK) — `agents/<slug>/agent.py`
- `claim-flow-anomaly-detector`
- `multi-customer-pattern-detector`
- `forensic-self-exam-agent`

### API Workflows (14, `Type:"Api"`) — `api_workflows/<slug>/main.json`
`counsel-hawthorne`, `insurer-aurora-specialty`, `payer-apex`, `payer-lakeshore`,
`payer-summitblue`, `payer-union-prairie`, `provider-alpha`, `provider-beta`, `provider-delta`,
`provider-epsilon`, `provider-gamma`, `provider-northstar`, `regulator-tn-doi`, `vendor-nimbus`

### Maestro BPMN (1) — `maestro_bpmn/<slug>/<slug>.bpmn`
- `clearflow-ideal-incident-response`

### Maestro Flow (1, Demo Driver) — `maestro_flow/<slug>/<slug>.flow`
- `clearflow-demo-driver`

### UiPath Apps (1) — `apps/<slug>/app.json`
- `clearflow-network-command`

### Data Fabric entities (9) — specified in `data-model.md`
`Provider`, `Payer`, `Vendor`, `Regulator`, `Insurer`, `Counsel`, `BAA`, `ClaimTelemetry`,
`RegulatorTemplate`

### Context Grounding indexes (2)
`BAA-corpus` (real `resource.json` under the BAA Boundary Reasoner), `ClaimTelemetry-corpus`

### Trust Layer policy pools (2)
PHI/PII detection; content filtering — applied uniformly via the LLM Gateway on every LLM call.

---

## /speckit.tasks — dependency-ordered subtasks

## User Stories

- **US1** (P1): A Devpost judge reads `README.md` and can confirm every UiPath product surface
  the project uses, each named, with honest live-vs-offline status and a working LICENSE link.
- **US2** (P2): The "Built with Coding Agents" section points judges to the bonus evidence
  (`CODING_AGENTS.md` / `CLAUDE_CODE_USAGE.md` / `docs/coding-agents/`).
- **US3** (P3): A README-completeness gate fails CI if any future artifact is added without
  being named in the README (self-maintaining inventory).

### Tasks

- **T001** [US3] (TDD RED) — `tests/unit/docs/test_readme_completeness.py`: enumerate the real
  artifact dirs (cases, low-code agents, coded agents, API workflows, BPMN, Flow, App) from the
  filesystem; assert each slug is named in `README.md`. Add frozen lists for the 9 DF entities,
  2 CG indexes, 2 Trust Layer pools. Assert: LICENSE file exists + linked from README;
  "Built with Coding Agents" section names Claude Code and links `CODING_AGENTS.md`; no forbidden
  real-company tokens; README does **not** reference the non-existent `seed_data_fabric.sh`.
  Author RED (against the current stale README).
- **T002** [US1, US2] (GREEN) — Rewrite `README.md`: full inventory tables naming every component;
  honest status column (authored/offline-validated; tenant publish per `DEVIATIONS.md`); fixed
  quickstart (no fake seed step); "Built with Coding Agents" section; LICENSE link; prerequisites.
- **T003** — Confirm `LICENSE` (MIT) present and the README link resolves.
- **T004** — Scaffold `docs/submission/README.md`: Devpost page checklist, 5-min video shot-list
  pointer (reuse `docs/demo/run-playbook.md`), deck checklist, and the tag-after-demo rule.
  Honest PENDING status — no fabricated links.
- **T005** — Fix the `seed_data_fabric.sh` name-honesty leak in `CODING_AGENTS.md` (it claims the
  script exists). Reword to "Data Fabric seeding (specified in `data-model.md`)".
- **T006** — `uv run pytest` full suite green (incl. new gate); `/audit-ip-safety` whole-repo clean.
- **T007** — Run `/thermo-nuclear-code-quality-review` ↔ `/improve-codebase-architecture` on the
  slice diff; apply any Blocker findings.
- **T008** — Update `specs/003-uipath-native/tasks.md` Slice 017 status (offline done; human
  capture carried forward). Commit `feat(slice-017): submission package — README inventory +
  completeness gate`. **Do NOT** tag `agenthack-2026-submission` (waits for recorded live demo).

## Verification

- Gate `test_readme_completeness.py` GREEN; full suite green; IP audit clean.
- README names all 27 artifacts + 9 DF entities + 2 CG indexes + 2 Trust Layer pools.
- LICENSE present + linked. No reference to non-existent scripts.
- Carry-forward (human): live demo recording, Devpost page, deck, coding-agent reel, submission tag.
