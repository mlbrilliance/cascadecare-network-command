# Spec 003: Tasks (Slices 004 → 017)

This is the executable slice plan for the pure-UiPath build. Each slice ends with a green verify gate + a commit. AI coding agents (Claude Code, Codex) should claim slices in order unless dependencies allow parallel work.

---

## Slice 004 — Foundation reset
**Goal**: Delete legacy Python; archive old spec; grant Studio Web scopes; scaffold this spec.

**Tasks**:
- [x] Update auto-memory with new trajectory (`/home/webfiji/.claude/projects/.../memory/`)
- [x] Archive `specs/002-case-schema/` → `docs/archive/specs-002-case-schema/` with ARCHIVED.md
- [x] Delete legacy directories: `src/cascadecare/{orchestration,models,db,probe,evidence,mocks,shim,data}/`, related tests, `scripts/demo_quickstart.py`, root artifacts (`alembic.ini`, `agentdb.rvf*`)
- [x] Trim `pyproject.toml`: remove langgraph, langchain, anthropic, pydantic-settings, sqlalchemy, psycopg, lancedb, polars, faker, fastapi, uvicorn, alembic, aiosqlite. Run `uv sync`.
- [x] Scaffold `specs/003-uipath-native/{plan,data-model,tasks}.md`
- [ ] Update `DEVIATIONS.md`: mark Studio Web upload blocker resolved (user granted scopes 2026-05-26)
- [ ] Update `CLAUDE.md`: refresh Technology Stack + Agent Topology sections to match pure-UiPath posture
- [ ] Verify: `uv sync` passes (✅ done), `uv run pytest` passes (only `tests/unit/uipath/test_maestro_client.py` remains), `/audit-ip-safety` passes
- [ ] Commit: `feat(slice-004): foundation reset — pure-UiPath trajectory, legacy Python removed`

---

## Slice 005 — Data Fabric seeding
**Goal**: 9 entities in Data Fabric + Context Grounding indexes built.

**Tasks**:
- Define entities: Provider, Payer, Vendor, Regulator, Insurer, Counsel, BAA, ClaimTelemetry, RegulatorTemplate (see `data-model.md`)
- Author `scripts/seed_data_fabric.sh` using `uip data-fabric` CLI commands
- Seed: 6 providers, 4 payers, 1 vendor, 1 regulator, 1 insurer, 1 counsel, 6 heterogeneous BAAs, 4320 claim telemetry rows, 1 regulator template
- Build Context Grounding indexes: `BAA-corpus`, `ClaimTelemetry-corpus`
- Verify: `uip data-fabric entities list` returns 9 entities; record counts match; `/audit-ip-safety` passes
- Use `uipath-data-fabric` skill
- Commit: `feat(slice-005): Data Fabric seeded with synthetic providers, payers, BAAs, claim telemetry`

---

## Slice 006 — Integration Service API Workflows — ✅ authored offline (connector reads + triggers pending tenant)
**Goal**: ~13 API Workflows that read from Data Fabric and emit events.

> **Status (2026-05-28):** 14 workflow files authored at `api_workflows/<slug>/main.json` (the
> count is 14, not 13 — one per `source_systems` slug; `multi-customer-pattern-detector` is the
> Coded agent, not a workflow). Each is a valid CNCF Serverless Workflow emitting its event
> payload; 58-case structural test green. REMAINING (online): replace the JsInvoke payload
> stand-in with the live Data Fabric connector read (`uip api-workflow registry stub`), wire the
> Maestro Trigger emission, add `project.json` (`Type:"Api"`), and `uip solution pack`/`publish`.

**Tasks**:
- Author one API Workflow per external system (6 providers + 4 payers + 1 vendor + 1 regulator + 1 insurer + 1 counsel = 13)
- Each workflow reads from Data Fabric entities + shapes payload + emits as Maestro Trigger-compatible event
- Verify: `uip integration-service workflows list` returns 13; each workflow passes its own validation
- Use `uipath-api-workflow` skill
- Commit: `feat(slice-006): 13 Integration Service API Workflows fronting Data Fabric mocks`

---

## Slice 007 — Trust Layer + BYO-LLM
**Goal**: Anthropic registered as BYO-LLM; Trust Layer PHI/PII policies active tenant-wide.

**Tasks**:
- Register Anthropic key: `uip llm-configuration byo-connections add ...`
- Configure Trust Layer policy: PHI detection + PII filtering on every LLM Gateway call
- Test: send a known-PHI string through any LLM call; confirm Trust Layer redacts or alerts
- Verify: `uip llm-configuration list` shows Anthropic registered; Trust Layer status report shows policies active
- Use `uipath-platform` + `uipath-governance` skills
- Commit: `feat(slice-007): BYO-LLM (Anthropic) registered; Trust Layer PHI/PII policies active`

---

## Slice 008 — Agent Builder agents (4) — ✅ authored offline (validate/migrate + caseplan wiring pending tenant)
**Goal**: 4 low-code agents authored with Context Grounding bindings.

**Tasks**:
- `agents/vector-hypothesis/agent.json` — Vector Hypothesis Agent (reasoning over investigation evidence)
- `agents/baa-boundary-reasoner/agent.json` — BAA Boundary Reasoner (Context Grounding on `BAA-corpus`)
- `agents/fiduciary-conflict-detector/agent.json` — Fiduciary Conflict Detector (cross-BAA reasoning + HITL form payload generation)
- `agents/negligent-monitoring-risk/agent.json` — Negligent Monitoring Risk Agent (litigation exposure reasoning)
- All prompts in `agents/prompts/*.md`
- All route through Claude via BYO-LLM
- Verify: each agent passes its own validation; smoke-test against a small synthetic query; Trust Layer fires on PHI inputs
- Use `uipath-agents` skill
- Commit: `feat(slice-008): 4 Agent Builder agents with Context Grounding and BYO-LLM`

---

## Slice 009 — Coded Agents (3) — ✅ authored offline w/ TDD (codedagent init/deploy pending tenant)
**Goal**: 3 Python SDK Coded Agents published to Studio Web.

**Tasks**:
- `agents/claim-flow-anomaly/` — Python package; classifies anomaly score on incoming telemetry; uses UiPath first-party LLM
- `agents/multi-customer-pattern/` — Python package; cross-provider correlation math; emits cascade signal when ≥3 providers anomalous
- `agents/forensic-self-exam/` — Python package; coordinates other agents; uses UiPath first-party LLM for routing
- Each agent has its own `pyproject.toml` and `agent.py`
- Prompts in `agents/prompts/*.md`
- Verify: each agent publishes successfully via `uip coded-agent publish`; smoke-test via `uip coded-agent invoke`
- Use `uipath-coded-apps` skill
- Commit: `feat(slice-009): 3 Coded Agents (Python SDK) published to Studio Web`

---

## Slice 010 — Case definitions (3 caseplan.json files) — ✅ authored offline (deploy-time wiring pending tenant)
**Goal**: Master + parent + grandchild case definitions wired via native `case-management` task type.

> **Status (2026-05-28):** All 3 V20 caseplans authored; master Regulatory-Response stage carries the
> 6-spawn Reversal-3 fan; solution regenerated via `pack-solution.sh`; 183 tests green. REMAINING
> (online, requires tenant): child-case `entityKey`/IO-schema resolution (`registry pull` / `tasks
> describe`), solution-manifest member registration (`uip solution project add`), `uip solution
> validate` + publish, and the 7 `type:"agent"` task wirings (Slices 008/009). The `uip maestro case
> validate` + Studio Web preview check below run in that online session.

**Tasks**:
- Modify `maestro_case/clearflow-master-crisis/content/caseplan.json` — enrich V20 schema; add `case-management` tasks for 6 stakeholder spawns at Reversal 3 stage; wire all 7 agents as `type: "agent"` tasks at appropriate stages
- Author `maestro_case/clearflow-stakeholder-parent/content/caseplan.json` — V20; per-stakeholder stages; `case-management` tasks for grandchild spawns
- Author `maestro_case/clearflow-obligation-grandchild/content/caseplan.json` — V20; leaf-level case for individual obligations
- Engineer canvas layout for hero cascade visualization at Reversal 3 (6 grandchild spawns in a horizontal fan)
- All three include Trust Layer-aware action tasks where appropriate
- Action task at Reversal 4: tri-party HITL gate (priority "Critical")
- Verify: `uip maestro case validate` passes on all 3 files; layout renders telegenically (manual check via Studio Web preview)
- Use `uipath-maestro-case` skill
- Commit: `feat(slice-010): 3-level case definitions with native case-management nesting`

---

## Slice 011 — Maestro BPMN ideal-response model — ✅ authored offline (uip maestro bpmn validate pending tenant)
**Goal**: BPMN model documenting the happy path; gateway diverges into master case.

**Tasks**:
- Author `maestro_bpmn/clearflow-ideal-incident-response/process.bpmn`
- Stages: intake → triage → contain → notify → close
- Gateway `is_cascade?` after triage diverges into spawn of master case
- Verify: `uip maestro bpmn validate` passes
- Use `uipath-maestro-bpmn` skill
- Commit: `feat(slice-011): Maestro BPMN ideal-response model with cascade divergence`

---

## Slice 012 — Maestro Flow Demo Driver — ✅ authored offline (real api-workflow nodes + validate pending tenant)
**Goal**: Maestro Flow that fires API Workflow calls at compressed intervals.

**Tasks**:
- Author `maestro_flow/clearflow-demo-driver/flow.json`
- 7 scheduled steps firing API Workflow calls at: t+10s, t+25s, t+45s, t+75s, t+120s, t+165s, t+210s
- Each step targets the appropriate API Workflow for the simulated event
- Verify: `uip maestro flow validate` passes; dry-run shows correct sequence
- Use `uipath-maestro-flow` skill
- Commit: `feat(slice-012): Maestro Flow Demo Driver with compressed reversal timeline`

---

## Slice 013 — UiPath Apps narrative dashboard — ✅ authored offline (tenant validation + live bindings pending Slice 014)
**Goal**: One screen aiding the demo narrative.

> **Status (2026-05-30):** All artifacts authored at `apps/clearflow-network-command/` (TDD: 45 tests green).
> Backend: `models.py` + `dashboard.py` + `main.py` + `pyproject.toml`.
> Frontend: `app.json` (4-zone screen) + `project.json`.
> Contract: `specs/003-uipath-native/event-contracts/override-post.json`.
> REMAINING (online): `uip coded-app publish`; wire live Data Fabric + Maestro Case reads; `uip apps publish`; smoke-test in tenant.

**Tasks**:
- [x] Author `apps/clearflow-network-command/` (UiPath Apps with Coded App backend)
- [x] Single screen: cascade tree + reversal timeline + agent activity feed + override controls
- [x] TDD: 45 unit tests green (models + dashboard assembly + IP-safety + UIPATH_LIVE guard)
- [x] IP safety audit clean
- [ ] Verify: app loads in tenant; data binds to Data Fabric + Maestro Case state correctly (Slice 014)
- [x] Use `uipath-coded-apps` skill
- [ ] Commit: `feat(slice-013): UiPath Apps narrative dashboard for demo cuts`

---

## Slice 014 — Solution packaging + Studio Web publish
**Goal**: All assets bundled in `clearflow-solution.uipx` and published.

> **Status (2026-05-31): UPLOADED — smoke test pending.** All offline wiring + 8-project
> solution uploaded to staging.uipath.com/hackathon26_042 (SolutionId 167dda12-98eb-47d9-f741-08debdbdd466).
> Only the end-to-end R1→R5 smoke test remains.

**Tasks**:
- [x] Wire `qem:` Data Fabric fan-out into Reversal-3 stakeholder spawns (master caseplan)
  > Corrected 2026-06-10: `=datafabric.qem:Provider[...]` fails runtime evaluation in spawn
  > inputs (400300) — replaced with literal provider slugs. Do not claim runtime qem: fan-out.
- [x] Wire `hitlTask` output variable capturing reviewer context into Reversal-4 HITL gate
- [x] Add `Maestro.NotificationService` task to grandchild caseplan at SLA-breach
- [x] Wire live Data Fabric + Maestro Case reads in `apps/clearflow-network-command/backend/dashboard.py`
- [x] Update `maestro_case/clearflow-solution/` via `bash scripts/pack-solution.sh` (now bundles 8 projects: 3 cases + 4 Agent Builder agents + 1 BPMN; coded agents/app/flow/API workflows deploy separately)
- [x] ~~`uip solution validate`~~ — no such CLI subcommand; validation happens server-side on `upload` (pack-solution.sh sanity-checks manifest-resolves-on-disk instead)
- [x] `uip solution upload` succeeds — Designer URL: `https://staging.uipath.com/hackathon26_042/studio_/designer/8ca3e38b-cdb3-45dc-87e7-041f5f3480c8?solutionId=167dda12-98eb-47d9-f741-08debdbdd466`
- [~] End-to-end smoke test: deployment DONE, case-run PENDING.
  - ✅ 3 Coded Agents deployed to tenant feed @ v0.1.0
  - ✅ Core solution (3 cases + 4 Agent Builder agents) deployed + activated to Orchestrator folder `CascadeCare-Core` (DeploymentSucceeded/SuccessfulActivate)
  - ⚠️ `uip maestro case process run` blocked: `process list -f <key>` rejects the `uip or folders` keys ("Response returned an error code"); need the correct Maestro folder context / release-key. Trigger from Maestro UI or resolve folder context in follow-up.
  - ⚠️ Full 23-project deploy: 14 API workflows fail Orchestrator install (Error 2005 "Entry points configuration missing/corrupted") + BPMN (Error 1654 "entry points definition invalid"). They PACK + PUBLISH fine; Orchestrator install-time entry-points extraction needs per-package entry-points definitions (next layer of work).
  - ⏸️ Coded App: blocked on a tenant-registered OAuth External Application (human action).
- [x] Use `uipath-solution` skill
- [x] Commit: 4 commits (e335c4a feat, 9f3d8dc 3-case manifest, 9de6008 bundle fix, + chore 3714cd3)

---

## Slice 015 — Polish & dress rehearsal
**Goal**: Hero moment looks spectacular; demo flows tightly within 300s.

**Tasks**:
- Tune canvas layout — position the 6 stakeholder-spawn `case-management` tasks in a visible horizontal fan in the master case's "Regulatory Response" stage
- Brand styling on UiPath Apps screen (logo, color palette, typography)
- Multiple demo dry runs; record each; review for narrative tightness
- Identify any agent latency issues; add cache/warm-up where needed
- Verify: 3 successful 300-second dry runs in a row, all with R3 fan-spawn visible and crisp
- Commit: `feat(slice-015): polish — hero moment engineered; demo timing locked`

---

## Slice 016 — Coding-agent evidence consolidation — ✅ offline channels done (video/screenshots → Slice 017)
**Goal**: All 4 evidence channels populated; nothing left undocumented.

> **Status (2026-05-31):** Channels 1–2 complete offline — `CODING_AGENTS.md` +
> `CLAUDE_CODE_USAGE.md` (27-artifact authorship table + (a)/(b)/(c) bonus triad)
> and 7 per-type pages under `docs/coding-agents/` + README. Channels 3–4
> scaffolded with honest PENDING status (`docs/prompt-logs/README.md` cites the 7
> committed `agents/prompts/*.md`; `docs/coding-agents/screenshots/README.md` is a
> capture checklist). Gate `tests/unit/docs/test_coding_agents_evidence.py` (22
> assertions) GREEN; full suite 494 passed; IP-safety clean. Detail in
> `slice-016-tasks.md`. CARRIED FORWARD to Slice 017 (human capture): the 1-min
> coding-agent reel + live-session screenshots/transcripts.

**Tasks**:
- Write `CODING_AGENTS.md` at repo root — canonical reference
- Populate `docs/coding-agents/` — one markdown per UiPath artifact noting which coding agent authored it + prompt excerpts
- Populate `docs/prompt-logs/` — sanitized prompt+response transcripts (captured during slices 005–015)
- Capture `docs/coding-agents/screenshots/` — coding-agent session captures at key build moments
- Cut a short coding-agent reel (1 minute) for inclusion in the 5-minute demo or as supplementary footage
- Verify: every UiPath artifact has at least one evidence channel documenting its authorship; cross-links work
- Commit: `feat(slice-016): coding-agent evidence consolidated across 4 channels`

---

## Slice 017 — Submission package — ✅ offline portion done (Devpost page / live video / deck → human capture)
**Goal**: Devpost submission complete; all 4 required artifacts in place.

> **Status (2026-05-31):** Offline-completable artifacts DONE + machine-verified. `README.md`
> rewritten to the real built state — full UiPath component inventory (27 artifacts + 9 Data
> Fabric entities + 2 Context Grounding indexes + 2 Trust Layer pools), honest live-vs-offline
> status, Built-with-Coding-Agents section, MIT `LICENSE` linked. New gate
> `tests/unit/docs/test_readme_completeness.py` (15 assertions, filesystem-driven) GREEN; full
> suite 509 passed; IP-safety clean. Name-honesty fix: `CODING_AGENTS.md` no longer claims the
> non-existent `seed_data_fabric.sh`. Carry-forward in `docs/submission/README.md`: Devpost page,
> ≤5-min live demo video, deck, 1-min coding-agent reel, and the `agenthack-2026-submission` tag
> (tag waits for the recorded live demo). Spec-kit artifact: `slice-017-tasks.md`.

**Tasks**:
- Rewrite `README.md` — UiPath components list (every Maestro Case, BPMN, Flow, agent, API Workflow, Data Fabric entity, Context Grounding index, Trust Layer policy, UiPath Apps screen), setup instructions, prerequisites, "Built with Coding Agents" section, LICENSE (MIT or Apache 2.0)
- Add `LICENSE` file (MIT or Apache 2.0)
- Compose Devpost project page (title, track=Track 1, business problem, how it works, screenshots)
- Record 5-minute demo video (multiple takes; pick the strongest)
- Upload to YouTube/Vimeo
- Build presentation deck (use AgentHack-provided template)
- Final IP-safety audit on whole repo
- Verify: all 4 submission artifacts present and linked; demo video runs end-to-end on UiPath Automation Cloud (not slides); LICENSE present; README mentions every UiPath component
- Commit: `feat(slice-017): submission package complete — Devpost, demo video, deck, README`
- Tag: `agenthack-2026-submission`

---

## Slice 018 — Live-deployment unblock (cases render + BPMN installs) — ✅ done (post-roadmap)
**Goal**: Both Slice-014 live-install blockers cleared end-to-end on the tenant.

> **Status (2026-05-31):** (1) Cases "Unable to load diagram" — `caseplan.json.bpmn` is generated
> ONLY by the Studio Web designer canvas; the 3 case projects were wrongly `content/`-nested when
> the packer needs FLAT layout. Flattened all 3 + committed generated diagrams; cases render live
> (5d1a4f6). (2) BPMN Error 1654 — aligned entry-points/package-descriptor/operate/.bpmn to the
> canonical `processorchestration` shape discovered by diffing a fresh `uip maestro bpmn init`
> scaffold (61a10cd). Full solution `clearflow-solution v1.0.3` (9 projects) DeploymentSucceeded
> to `CascadeCare-Full`. 509 tests pass; IP clean. Carried forward → Slice 019.

---

## Slice 019 — Live-deployment completion (binding + cleanup + seed) — ✅ offline done (live ops → human)
**Goal**: Close the 3 Slice-018 carry-forwards so the live R1→R5 demo runs on one clean deployment.

> **Status (2026-05-31):** Offline portions DONE + machine-verified via spec-kit flow
> (`slice-019-tasks.md`). (a) BPMN→case bridge: binding `clearflow-crisis` was dangling (matched no
> solution resource); retargeted canonical `bindings_v2.json` + the committed registration manifest
> `bindingType` to `clearflow-master-crisis` (the real process-resource name); 5-assert
> binding-resolution gate GREEN. (b) `scripts/cleanup_deployments.sh` — guarded uninstall of stale
> deployments (keep-list protects `CascadeCare-Full`, `--confirm` required); 8-assert gate GREEN.
> (c) `scripts/seed_data_fabric.sh` + `seed_data_fabric.py` — data-table seed of 9 entities (4341
> rows) + 2 CG indexes; 19-assert dry-run gate GREEN (counts, FKs, 3 BAA conflict patterns,
> IP-clean, deterministic). Full suite 541 passed/7 skipped; IP clean; thermo-nuclear ↔
> architecture loop 0 Blockers. Carry-forward (human/online): T-a4 BPMN spawns case, T-b3 single
> clean deployment, T-c4 live seed — runbook in `slice-019-tasks.md`. Polish candidate: extract
> `src/cascadecare/ip_safety.py` (FORBIDDEN now in 5 sites).

---

## Cross-cutting rules

- **TDD**: Slice 009 (Coded Agents) requires test files before source files (`tests/unit/agents/<name>/test_*.py` before `agents/<name>/agent.py`)
- **IP safety**: every commit passes `/audit-ip-safety`
- **Pre-write hook**: `knowledge/` is immutable; never modify files there
- **Prompts**: never inline in Python; always in `agents/prompts/*.md`
- **`uv run pytest`** passes before each commit

## Quality bar

Per Decision 10: scope is FULL — nothing cut. AI coding agents drive end-to-end with manual review. Quality bar: judging panel stands up and claps.
