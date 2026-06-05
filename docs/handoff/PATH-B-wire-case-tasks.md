# HANDOFF — Path B: Wire master-case tasks to auto-execute

> **Goal for the next session:** make `clearflow-master-crisis` **self-advance through all 7 stages** when spawned, so the demo runs end-to-end without manual task completion. Today it spawns correctly but **sits in Initial Response** because its tasks are deploy-time placeholders.
>
> **Branch:** `slice-023-reentry-agent-memory` · **Tenant:** `staging.uipath.com/hackathon26_042/DefaultTenant` · **Date:** 2026-06-04
> **Read first:** this file, then `docs/submission/GO-LIVE-GUIDE.md` (the live runbook + master error table).

---

## 1. What already works (verified live — do NOT redo)

| Capability | State | Evidence |
|---|---|---|
| Full solution deploy | ✅ v1.0.6 in `Shared/CascadeCare-v106` | folder key `ba9208f7-cf5c-4504-9475-ff4472f8a65e`, all 9 projects Active |
| BPMN → Case spawn | ✅ confirmed | `ClearFlowIdealIncidentResponse` (isCascade=true) spawns `clearflow-master-crisis`, Running |
| Data Fabric seed | ✅ 9 entities, 4,320 telemetry rows (4,176 anomalous) | `scripts/seed_data_fabric.sh` (live-fixed) |
| Demo Driver flow | ✅ runs all 30 steps clean (timer fixed) | trace ebb6576d — completes t+0→t+260s |
| Master case spawns | ✅ but **sits in Initial Response** | trace 3ca139ba |

**The Demo Driver is independent ambiance** — its 14 `Fire …` script nodes only *return* payloads; they do NOT dispatch to the case. The case is meant to **self-advance** (see §2), not be driven by the flow.

## 2. Why it stalls — the mechanism

`maestro_case/clearflow-master-crisis/caseplan.json` has **7 stages**. Stage 1 (`Initial Response`) enters on `case-entered`; every later stage enters on **`selected-stage-completed`** — i.e. the case walks itself **only if each stage's tasks complete**. They don't, because the tasks are placeholders:

| Stage | Task(s) | Type | Current binding state | Path-B work |
|---|---|---|---|---|
| Initial Response | Assess Affected Providers | `process` | **`data: {}` — EMPTY, no process bound** | **First blocker.** Bind a process, OR convert to an auto-completing/no-op task, OR a `core.action.script`-style step. |
| Multi-Customer Investigation | Claim Flow Anomaly Detection · Multi-Customer Correlation | `agent`×2 | name/folderPath bound; **inputs=0 outputs=0** | Wire agent I/O schemas so they invoke + complete. Agents = `claim-flow-anomaly-detector`, `multi-customer-pattern-detector` (Coded). |
| Vector Isolation | Vector Hypothesis · Forensic Self-Exam | `agent`×2 | bound; inputs=0 (Forensic outputs=1) | Wire I/O. `vector-hypothesis-agent` (low-code), `forensic-self-exam-agent` (Coded). |
| Regulatory Response | BAA Boundary + **6× Spawn Stakeholder Parent** | `agent` + `case-management`×6 | all 6 spawns → `.clearflow-stakeholder-parent` (name+folderPath) | 🌟 **the hero fan.** Verify the 6 spawns fire; wire BAA agent I/O. |
| Fiduciary Review | Tri-Party Fiduciary Conflict Review | `action` | taskTitle/priority/inputs/outputs | HITL/Action Center task — completes on human approval (OK for demo; decide if "auto" is wanted). |
| Litigation Defense | Litigation Defense Posture Review | `agent` | bound; inputs=0 outputs=0 | Wire I/O. `negligent-monitoring-risk-agent` (low-code). |
| Closed | — | — | — | terminal |

### Caseplan bindings (already present — `=bindings.bXXX` → resourceKey)
All 7 agents + stakeholder-parent are bound by `name`+`folderPath` (solution-relative `.resourceKey`):
`.claim-flow-anomaly-detector`, `.multi-customer-pattern-detector`, `.vector-hypothesis-agent`, `.forensic-self-exam-agent`, `.baa-boundary-reasoner`, `.negligent-monitoring-risk-agent`, `.clearflow-stakeholder-parent`.

## 3. The two big risks to resolve FIRST

1. **The 3 Coded Agents may not be deployed in v106.** The solution manifest only bundles the **4 low-code Agent Builder agents** (`baa-boundary-reasoner`, `fiduciary-conflict-detector`, `negligent-monitoring-risk-agent`, `vector-hypothesis-agent`) + the 3 cases + BPMN + flow. The **3 Coded Agents** (`claim-flow-anomaly-detector`, `multi-customer-pattern-detector`, `forensic-self-exam-agent`) are deployed **separately** via `uip codedagent` (see `scripts/pack-solution.sh` header). **Verify all 7 agent bindings resolve in the v106 folder** before wiring I/O — an unresolved agent binding = the stage never completes. Multi-Customer Investigation (stage 2) needs 2 Coded Agents, so this is the *next* blocker after the process task.
2. **The `process` task is empty (`data: {}`).** Decide its implementation. Options: (a) bind it to a real Orchestrator process / API workflow; (b) replace it with a task type that auto-completes; (c) make Initial Response's completion not depend on it. This gates EVERYTHING — the case can't leave stage 1 until it resolves.

## 4. How tasks complete in Maestro Case (the model to confirm)

Agent/process tasks with `entryConditions` (e.g. `current-stage-entered`) should auto-invoke when the stage enters, and mark the task complete on return. A stage with `marksStageComplete` semantics advances when its required tasks complete. **Confirm against the Maestro Case V20 docs** (skill: `uipath-maestro-case`) exactly what makes:
- an `agent` task auto-run and auto-complete (does it need non-empty inputs/outputs? a trigger? `shouldRunOnlyOnce`?),
- a `process` task complete,
- a `case-management` task spawn + count as complete (we proved the inline name+folderPath binding pattern works for the BPMN spawn — §6).

Start by reading the V20 guide on task auto-execution before editing the caseplan.

## 5. Hard-won contracts (reuse — verified live, see memory)

- **BPMN→Case spawn (`Orchestrator.StartCaseMgmtProcessAsync`)**: type `v2` + inline `<uipath:binding>` pair (`name` + `folderPath`, propertyAttribute each) + keep `JobArguments` + `Process response`/`Orchestrator.RunJob` output. The single `releaseKey` form throws runtime **170005 "folderId missing"**. (commit 6ec62c5)
- **`uip solution pack` is the AUTHORITATIVE activity-contract validator** — stricter than the Studio Web Health analyzer and canvas. It prints exact required/forbidden inputs. Trust it.
- **Studio Web cloud solution copy is STALE** (no isCascade, old dangling binding). **Ship from the repo via CLI**, never from a browser Publish.
- **Data Fabric `uip df`**: see `~/.claude/.../memory/datafabric-cli-seed-contract.md` — records insert needs entity **ID** not name; field `id` reserved → `slug`; **underscore field names silently drop on insert → camelCase**.
- **Maestro Flow `core.logic.delay`**: the `definitions[]` entry needs `model.values` mapping `inputs.timerValue`→BPMN timer, else runtime **190001 "Invalid timer expression"**. (commit 66e9dc1)
- **OneDrive/WSL** throws `EIO` + leaves `.git/index.lock`. Fix: `rm -f .git/index.lock` and retry; hard reset is `wsl --shutdown` from PowerShell.
- `export PATH="$HOME/.dotnet:$PATH"` before any pack/build.

## 6. Deploy recipe (bump version + FRESH folder each time → dodge Error 4004)

```bash
export PATH="$HOME/.dotnet:$PATH"
bash scripts/pack-solution.sh                                                           # stage canonical sources into the solution (local)
uip solution pack maestro_case/clearflow-solution dist --version 1.0.7 --output json    # -> dist/clearflow-solution_1.0.7.zip (local)
uip solution publish dist/clearflow-solution_1.0.7.zip --output json                    # publish (tenant)
uip solution deploy run --name cascadecare-v107 --package-name clearflow-solution \
  --package-version 1.0.7 --folder-name CascadeCare-v107 --parent-folder-path "Shared" --output json
```
Then re-spawn: run `ClearFlowIdealIncidentResponse` (isCascade=true) in the new folder and watch the master case walk its stages.

## 7. Tenant coordinates

| Thing | Value |
|---|---|
| Current folder | `Shared/CascadeCare-v106` key `ba9208f7-cf5c-4504-9475-ff4472f8a65e` |
| Data Fabric Provider entity ID | `ab501a56-6c60-f111-8fcb-000d3a45fabb` (others via `uip df entities list`) |
| Login | `uip login` as `puneetsatyawan@gmail.com` → `hackathon26_042 / DefaultTenant` |
| Stale folders to clean (Step 7) | v105, v104, CascadeCare-Full/Demo/Live/Core — **update cleanup keep-list to protect v106/v107 first** |

## 8. TDD + commit discipline

- Test file before source in `agents/`. `uv run pytest` must pass before commit (currently **579 passing, 7 skipped**).
- Caseplan logic is HIGH-RISK per `CLAUDE.md` SPEC GATE — show a SPEC block + get LGTM before editing caseplan task wiring.
- IP-safety: zero real company names (audit forbidden-token list lives in `scripts/seed_data_fabric.py`). Note one false-positive: the past-tense verb for "compress into a .zip" (z-i-p-p-e-d) contains a forbidden substring — write "packed into a .zip" instead.
- No `Co-Authored-By` trailer (no `attribution.commit` set).

## 9. Suggested first moves in the clean session

1. `make resume` (if available) + read this doc + `git log --oneline -10`.
2. Read the `uipath-maestro-case` skill on **task auto-execution** (§4) — this is the crux.
3. **Verify all 7 agent bindings resolve in v106** (esp. the 3 Coded Agents §3.1) — deploy any missing.
4. Decide + implement the `process` task fix (§3.2) — unblocks stage 1.
5. SPEC-gate the caseplan task-wiring change → wire agent I/O → repack v1.0.7 → redeploy → spawn → watch it walk.
6. Iterate stage-by-stage; the win condition is the case reaching **Closed** on its own, with the **6-parent fan** visible at Regulatory Response.
