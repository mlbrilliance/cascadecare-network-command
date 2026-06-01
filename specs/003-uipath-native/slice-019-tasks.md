---
description: "Slice 019 — Live-deployment completion: BPMN→case bridge binding + deploy cleanup + Data Fabric seed"
---

# Tasks: Slice 019 — Live-Deployment Completion

**Input**: Slice 018 carry-forward (memory `slice018-case-diagram-deploy-mechanics`);
`specs/003-uipath-native/data-model.md` §Data Fabric entities; `scripts/pack-solution.sh`;
the solution resource manifests under `maestro_case/clearflow-solution/resources/solution_folder/`.

**Goal**: Close the three remaining Slice 018 carry-forward items so the live R1→R5 demo can run
on a single clean deployment with agents reading real Data Fabric data:
(a) the Maestro BPMN `is_cascade?` gateway can actually spawn the master crisis case (binding
resolves), (b) only `CascadeCare-Full` remains deployed, (c) Data Fabric is seeded + Context
Grounding indexes exist.

> **Convention note (recorded Slice 016 decision, reaffirmed 013/015/016/017):** `setup-plan.sh`
> clobbers the shared `plan.md`, so this slice's plan/analyze/tasks are authored directly into
> this file. The shared `plan.md` remains the canonical pure-UiPath pivot plan.

> **Session-mode note:** This is an **offline** authoring session (no live tenant calls). Each
> item below is split into an **offline-authorable** part (done + machine-verified here) and a
> **live-only** part (exact commands authored + flagged for human/online execution). No tenant
> mutation happens from this session.

---

## /speckit.plan — approach

### Why this slice exists

Slice 018 got the **full solution** (`clearflow-solution v1.0.3`, 9 projects) to
`DeploymentSucceeded` on `CascadeCare-Full`, and proved cases render live. Three threads were left
dangling, all of which block a clean end-to-end hero demo:

1. **(a) BPMN→case bridge is broken.** The BPMN `clearflow-ideal-incident-response` has a call
   activity `Call_SpawnMasterCrisis` (`Orchestrator.StartCaseMgmtProcessAsync`) whose
   `releaseKey = =bindings.Binding_MasterCrisisCase`. That binding currently points at resource
   key `clearflow-crisis` — **a key no solution resource owns** — so the spawn cannot resolve at
   runtime. The hero "BPMN detects cascade → spawns master case" beat silently no-ops.
2. **(b) Deployment clutter.** Slices 014–018 left up to four stale deployments
   (`CascadeCare-Core`, `-Smoke`, `-Live`, `-Demo`) alongside the canonical `CascadeCare-Full`.
   Judges (and our own smoke runs) need exactly one unambiguous deployment.
3. **(c) Agents have no data to read.** Data Fabric is unseeded, so every agent that reads
   Provider/Payer/BAA/ClaimTelemetry entities runs against an empty store. The R1→R5 narrative
   needs the 9 entities + the two Context Grounding indexes populated. `seed_data_fabric.sh` was
   referenced by docs in Slice 016/017 but **never written** (name-honesty leak already flagged).

### Strategy

**(a) — resolve, don't guess.** The binding-resolution key was treated as ambiguous in the Slice
018 handoff (caseplan `name = clearflow-crisis` vs project/dir `clearflow-master-crisis`). It is
**not** ambiguous: the determinative artifact is the packed solution resource manifest. See the
analyze section — the only `caseManagement` process resource the solution declares is named
`clearflow-master-crisis`, and the BPMN's generated `runtimeDependencies[].bindingType` is
`clearflow-crisis`, which matches **no** resource. Fix = retarget the canonical BPMN
`bindings_v2.json` to `clearflow-master-crisis`, re-pack (regenerates the solution copy +
the `ClearFlowIdealIncidentResponse.json` `bindingType`), assert the generated `bindingType` now
equals the case process `resource.name`. A pytest gate makes this self-checking (binding must
reference a real solution process resource — kills the whole dangling-binding class of bug).

**(b) — author the runbook, execute live.** Offline we can't (and must not) call the tenant. We
author an idempotent, copy-pasteable uninstall runbook + a guarded `scripts/cleanup_deployments.sh`
that uninstalls the stale set and asserts `CascadeCare-Full` survives. The script refuses to run
without an explicit `--confirm` flag and never touches `CascadeCare-Full`.

**(c) — drive the seed from `data-model.md`, not from memory.** `data-model.md` already specifies
all 9 entities (fields, FKs, seed counts, the 3 engineered BAA conflict patterns). We author
`scripts/seed_data_fabric.sh` that (1) creates/ensures the 9 Data Fabric entity schemas, (2)
upserts the synthetic rows (sourced from `data-model.md` + the committed API-workflow mock
fixtures + `knowledge/` — read-only), and (3) creates the `BAA-corpus` and `ClaimTelemetry-corpus`
Context Grounding indexes. A pytest gate validates the script's row payloads are well-formed and
IP-clean **without** calling the tenant (dry-run/`--emit-json` mode the script supports). The
script's live mode is gated behind `UIPATH_LIVE=1` + auth, exactly like the existing tooling
pattern.

### Constitution check

| Principle | Compliance |
|---|---|
| I. TDD-first | (a) binding-resolution gate, (c) seed-payload gate — both authored RED-first against current state. (b) script has a structural unit test. |
| II. IP safety | `/audit-ip-safety` whole-repo before commit; seed-payload gate re-asserts the forbidden-token denylist over every seeded string. |
| III. Externalized prompts | No prompt changes this slice. |
| IV. Surgical edits | (a) is a 2-line value change in one canonical file + regen; caseplan `name` is **left untouched** (not the resolution key — see analyze). |
| VII. Secrets via .env | Seed/cleanup scripts read auth from env only; no creds committed. |
| VIII. knowledge/ immutable | Seed reads `knowledge/` read-only; never writes there. |

### Offline-vs-live split (explicit)

| Item | Offline-authorable (this session) | Live-only (human/online) |
|---|---|---|
| (a) | Edit canonical `bindings_v2.json`; re-pack; binding-resolution gate green | `uip solution publish/deploy` `CascadeCare-Full`; trigger BPMN; confirm master case spawns |
| (b) | `scripts/cleanup_deployments.sh` + runbook + structural test | Run the uninstall commands against the tenant |
| (c) | `scripts/seed_data_fabric.sh` + seed-payload gate (dry-run) | Run seed with `UIPATH_LIVE=1`; verify entities + CG indexes in tenant |

### Out of scope

Re-recording the demo video; Devpost page; the `agenthack-2026-submission` tag (still waits for a
recorded live demo). Any change to the caseplan `name` field (deliberately avoided — see analyze).

---

## /speckit.analyze — cross-artifact consistency findings

Run read-only over the BPMN binding artifacts, the packed solution resource manifests, the three
caseplans, and the docs that name the seed script. **1 critical (resolved offline), 0 unresolved
blockers.**

### F1 — (a) binding-resolution key — RESOLVED (was the open Slice-018 ambiguity)

**Determinative evidence** (packed solution resource manifests are the binding-resolution source
of truth, not the caseplan):

| Artifact | Field | Value |
|---|---|---|
| `…/solution_folder/process/caseManagement/clearflow-master-crisis.json` | `resource.name` / `spec.name` | **`clearflow-master-crisis`** (the only `caseManagement` process resource) |
| `…/solution_folder/process/processOrchestration/ClearFlowIdealIncidentResponse.json` | `runtimeDependencies[].bindingType` | `clearflow-crisis` → **matches no resource (dangling)** |
| `maestro_case/clearflow-master-crisis/caseplan.json` | `name` | `clearflow-crisis` (internal case-def id; **not** the binding key) |
| `maestro_case/clearflow-master-crisis/project.uiproj` | `Name` | `clearflow-master-crisis` (= package name = process `resource.name` = binding key) |


**Convention corroboration:** every case-management spawn already in the caseplans references its
target by **project/package name**, never the caseplan `name`:
`.clearflow-stakeholder-parent`, `.clearflow-obligation-grandchild`, `.vector-hypothesis-agent`,
`.baa-boundary-reasoner`, etc. (caseplans use a leading-dot solution-relative form; the BPMN
`bindings_v2.json` schema uses the **bare** `resource.name`, no dot — confirmed by the existing
`bindingType` value having no dot).

**Conclusion:** BPMN binding `resourceKey`/`resource` → **`clearflow-master-crisis`** (bare, no
dot). The caseplan `name` field is **left untouched** (F5).

### F2 — seed-script doc honesty (MEDIUM)

`docs/usage-examples.md` (L4, L18, L137) and `docs/architecture.md` (L153) still describe
`scripts/seed_data_fabric.sh` as "**planned — Slice 005**". Once (c) writes the script the
"planned" claim is false **and** the slice number is wrong. `README.md` + `CODING_AGENTS.md` are
already honest (slice-017 fix holds — confirmed no live references). → Reword the two `docs/` files
to "Slice 019" and drop "(planned)" as part of (c).

### F3 — master tracker gap (LOW)

`specs/003-uipath-native/tasks.md` terminates at Slice 017; Slices 018 (done) and 019 are
post-roadmap and unrecorded. → Append Slice 018 + Slice 019 entries in the finish step.

### F4 — dual-copy drift (LOW, informational)

The solution-nested copies (`maestro_case/clearflow-solution/…`) also carry `clearflow-crisis`.
**Do not hand-edit** — `pack-solution.sh` regenerates them from the canonical
`maestro_bpmn/…/bindings_v2.json` after the F1 fix (per `caseplan-canonical-vs-packsolution`).

### F5 — caseplan `name` mismatch (LOW, leave as-is)

`caseplan.json name = "clearflow-crisis"` ≠ project name. It is the case-def internal id, not the
binding key, and nothing spawns by it. Changing it is unnecessary churn and risks the live-deployed
case identity → **deliberately not changed** (Surgical Edits principle).

---

## /speckit.tasks — dependency-ordered subtasks

### User Stories

- **US1** (P1): At runtime, the BPMN `is_cascade?` gateway's `Call_SpawnMasterCrisis` resolves its
  binding to the deployed master crisis case and starts it (hero "BPMN spawns case" beat works).
- **US2** (P2): Exactly one deployment (`CascadeCare-Full`) exists on the tenant; a guarded script
  uninstalls the stale set without ever touching `CascadeCare-Full`.
- **US3** (P3): Data Fabric holds the 9 entities + the 2 Context Grounding indexes, seeded by a
  real, idempotent, IP-clean `scripts/seed_data_fabric.sh`; docs that name it are honest.

### Tasks

**(a) BPMN → master-case bridge binding**

- **T-a1** [US1] (TDD RED) [P] — `tests/unit/maestro_bpmn/test_bpmn_case_binding.py`: assert the
  canonical `maestro_bpmn/clearflow-ideal-incident-response/bindings_v2.json` `resourceKey` and
  `resource` reference a process resource that **actually exists** in the packed solution
  (`maestro_case/clearflow-solution/resources/solution_folder/process/**/*.json` `resource.name`).
  Parametrize so any future dangling BPMN binding fails. Authored RED (current `clearflow-crisis`
  has no matching resource).
- **T-a2** [US1] (GREEN) — Edit canonical
  `maestro_bpmn/clearflow-ideal-incident-response/bindings_v2.json`: `resourceKey` + `resource`
  `clearflow-crisis` → `clearflow-master-crisis` (bare, no leading dot). 2-line surgical change.
- **T-a3** [US1] — `bash scripts/pack-solution.sh` to regenerate the solution-nested copies +
  `ClearFlowIdealIncidentResponse.json` `runtimeDependencies[].bindingType`. Then assert the
  regenerated `bindingType == "clearflow-master-crisis"` (T-a1 gate now green end-to-end).
- **T-a4** [US1] (LIVE — human/online) — `uip solution pack` + `publish` + `deploy` `CascadeCare-Full`;
  trigger the BPMN with `affectedCustomerCount >= 3`; confirm a `clearflow-master-crisis` case
  instance spawns. Commands authored in the runbook; not executed this session.

**(b) Deployment cleanup**

- **T-b1** [US2] — `scripts/cleanup_deployments.sh`: idempotent uninstall of the stale set
  (`CascadeCare-Core`, `CascadeCare-Smoke`, `CascadeCare-Live`, `CascadeCare-Demo`). Refuses to run
  without `--confirm`; hard-codes `CascadeCare-Full` to a keep-list it will never uninstall;
  `--dry-run` prints the plan. Reads auth from env only.
- **T-b2** [US2] (TDD) [P] — `tests/unit/scripts/test_cleanup_deployments.py`: structural assertions
  — `CascadeCare-Full` is in the keep-list and never in the uninstall set; script aborts without
  `--confirm`; the stale set is exactly the four expected names; no hard-coded secrets.
- **T-b3** [US2] (LIVE — human/online) — Run `bash scripts/cleanup_deployments.sh --confirm`; verify
  `uip` deployment list shows only `CascadeCare-Full`.

**(c) Data Fabric seed + Context Grounding**

- **T-c1** [US3] (TDD RED) [P] — `tests/unit/scripts/test_seed_data_fabric.py`: run the seed script
  in `--emit-json` (dry-run, no tenant) and assert: all 9 entity types present
  (Provider/Payer/Vendor/Regulator/Insurer/Counsel/BAA/ClaimTelemetry/RegulatorTemplate); row
  counts match `data-model.md` (6 providers, 6 BAAs, etc.); FKs resolve (every `baa_id`/`provider_id`
  points at a seeded row); the 3 engineered BAA conflict patterns are present; `BAA-corpus` +
  `ClaimTelemetry-corpus` index-create steps emitted; **every seeded string is IP-clean**
  (forbidden-token denylist). Authored RED (no script yet).
- **T-c2** [US3] (GREEN) — `scripts/seed_data_fabric.sh`: emits the entity schemas + synthetic rows
  (sourced from `data-model.md` + committed API-workflow mock fixtures + read-only `knowledge/`) +
  the 2 CG index-create calls. Supports `--emit-json` (offline, for the gate) and live mode gated
  behind `UIPATH_LIVE=1` + auth, mirroring existing tooling. Uses `uip data-fabric` CLI in live mode.
- **T-c3** [US3] — Fix F2 doc-honesty: `docs/usage-examples.md` + `docs/architecture.md` reword
  `seed_data_fabric.sh` from "(planned — Slice 005)" to "Slice 019" (no longer planned).
- **T-c4** [US3] (LIVE — human/online) — `UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh`; verify
  9 entities populated + 2 CG indexes built in the tenant.

**Cross-cutting / finish**

- **T-x1** — `uv run pytest` full suite green (incl. 3 new gates); `uv run mypy src/` clean if touched.
- **T-x2** — `/audit-ip-safety` whole-repo clean (seed content is the high-risk surface).
- **T-x3** — `/thermo-nuclear-code-quality-review` ↔ `/improve-codebase-architecture` on the slice
  diff; apply any Blocker findings before commit.
- **T-x4** — F3: append Slice 018 (done) + Slice 019 entries to `specs/003-uipath-native/tasks.md`.
- **T-x5** — Commit `feat(slice-019): BPMN→case bridge binding + deploy cleanup + Data Fabric seed`.
  Do **not** tag (live demo still unrecorded).

### Parallelism

- T-a1, T-b2, T-c1 are independent RED gates → `[P]` author together.
- (a) is fully sequential (T-a1→a2→a3); (b) and (c) are independent of (a) and of each other.
- All LIVE tasks (T-a4, T-b3, T-c4) are deferred to a human/online session.

## Verification

- **Offline (this session):** T-a1/a2/a3 green (binding resolves to a real solution resource);
  T-b1/b2 (guarded cleanup script + structural test); T-c1/c2/c3 (seed script + dry-run gate +
  doc honesty). Full `uv run pytest` green; `/audit-ip-safety` clean; thermo/arch loop no Blockers.
- **Live (carried forward):** T-a4 (BPMN spawns master case), T-b3 (only `CascadeCare-Full` remains),
  T-c4 (entities + indexes populated). Captured in the run-playbook for the online session.

---

## /speckit.implement — results (offline session)

| Task | Status | Evidence |
|---|---|---|
| T-a1 | ✅ | `tests/unit/maestro_bpmn/test_bpmn_case_binding.py` — authored RED (proved `clearflow-crisis` dangling) |
| T-a2 | ✅ | canonical `bindings_v2.json` `resourceKey`+`resource` → `clearflow-master-crisis` |
| T-a3 | ✅ | `pack-solution.sh` regenerated copies; **also** fixed the committed registration manifest `runtimeDependencies[].bindingType` (pack-solution does NOT regen it); gate extended to pin the deploy-time key + drift. 5 binding tests GREEN |
| T-a4 | ⏸ LIVE | runbook: `uip solution pack/publish` + `deploy run CascadeCare-Full` → trigger BPMN (`affectedCustomerCount>=3`) → confirm `clearflow-master-crisis` case spawns |
| T-b1 | ✅ | `scripts/cleanup_deployments.sh` — keep-list guard, `--confirm` required, `--dry-run` default, idempotent |
| T-b2 | ✅ | `tests/unit/scripts/test_cleanup_deployments.py` — 8 structural tests GREEN |
| T-b3 | ⏸ LIVE | `bash scripts/cleanup_deployments.sh --confirm` → verify only `CascadeCare-Full` remains |
| T-c1 | ✅ | `tests/unit/scripts/test_seed_data_fabric.py` — 19 tests GREEN (counts, FKs, 3 conflict patterns, CG indexes, IP-clean, determinism) |
| T-c2 | ✅ | `scripts/seed_data_fabric.py` (data-table generator) + `scripts/seed_data_fabric.sh`. `--emit-json` emits 6/4/1/1/1/1/6/4320/1 records + 2 CG indexes |
| T-c3 | ✅ | `docs/usage-examples.md` + `docs/architecture.md` reworded (no longer "planned — Slice 005"; `uip data-fabric`→`uip df`/`uip context-grounding`) |
| T-c4 | ⏸ LIVE | `UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply` → verify 9 entities + 2 indexes |
| T-x1 | ✅ | `uv run pytest` — 541 passed / 7 skipped (+32 new) |
| T-x2 | ✅ | `/audit-ip-safety` whole-repo clean (all matches are denylist defs or `gzipped`/`unzipped` collisions) |
| T-x3 | ✅ | thermo-nuclear ↔ architecture loop — **0 Blockers**; report `/tmp/architecture-review-20260531-205602.html` |
| T-x4 | ✅ | this slice file + tasks.md Slice 018/019 entries |
| T-x5 | ✅ | commit (no tag — live demo unrecorded) |

### Carried-forward polish (architecture review, deferred)

Extract `src/cascadecare/ip_safety.py` (`FORBIDDEN` + `find_forbidden(text)`) and route all **5** duplication
sites (4 test modules + `seed_data_fabric.py`) through it. Supersedes the narrower slice-017 `tests/conftest.py`
note — a test-only constant can't serve the runtime seed script. `Worth Exploring`, not a Blocker.

### Live runbook (T-a4 / T-b3 / T-c4 — human/online session)

```bash
uip login                                                   # interactive, full entitlements
# (a) ship the binding fix
bash scripts/pack-solution.sh
uip solution publish maestro_case/clearflow-solution --output json
uip solution deploy run  <pkg> CascadeCare-Full --output json    # atomic; one bad project rolls back all
#   trigger the BPMN with affectedCustomerCount>=3 → confirm a clearflow-master-crisis case spawns
# (b) clean up
bash scripts/cleanup_deployments.sh --dry-run                # review
bash scripts/cleanup_deployments.sh --confirm                # uninstall stale; keeps CascadeCare-Full
# (c) seed
UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply       # 9 entities + 2 CG indexes
```
