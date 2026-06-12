# HANDOFF — Master Case Auto‑Walk COMPLETE (5/7 stages) → Finish with Action Center HITL

**Date:** 2026‑06‑06
**Branch:** `slice-023-autowalk-5stages` (this commit)
**Live solution:** `clearflow-solution@1.0.12` deployed+active in **`Shared/CascadeCare-v110`**
**Tenant:** staging.uipath.com / `hackathon26_042` / `DefaultTenant`
**Authoritative memory:** `~/.claude/.../memory/master-case-autostart-bpmn-fix.md` (read it first — it has every fix + recipe)

---

## 0. TL;DR for the next agent

The master Maestro Case (`clearflow-master-crisis`) now **auto‑walks 5 of 7 stages on its own** with **all 5 AI agents executing and 0 real incidents**. It stops at **Stage 5 = Fiduciary Review**, where the **Reversal‑4 HITL action** (`tvlKcFYnW`, "Tri‑Party Fiduciary Conflict Review") faults `170015 "No app found in folder"` because no Action Center app/action is deployed/wired.

**The user is creating an Action Center app/action in Studio Web and will give you its details.** Your job: **wire the `tvlKcFYnW` action task to that Action Center app, redeploy, confirm the gate renders + pauses, then drive (or let the human drive) the case through Stage 6 (Litigation Defense) → Stage 7 (Closed).** HITL via Action Center is **mandatory** for the hackathon — do NOT replace it with an auto‑form.

---

## 1. What works RIGHT NOW (verified live on v110)

Auto‑walk: **Initial Response → Multi‑Customer Investigation → Vector Isolation → Regulatory Response → Fiduciary Review**.

| Agent | elementId | Type | Status |
|---|---|---|---|
| Claim‑Flow Anomaly Detector | tBMXe7xGw, tTNOuRcy1 | coded | ✅ Completed |
| Multi‑Customer Pattern Detector | tMCPCor02 | coded | ✅ Completed |
| Forensic Self‑Exam | tFSEXam01 | coded | ✅ Completed |
| Vector Hypothesis | tumu72Wei | low‑code (Claude) | ✅ Completed |
| BAA Boundary Reasoner | tNWPCipI7 | low‑code (Claude + Context Grounding) | ✅ Completed |
| **Tri‑Party Fiduciary Conflict Review** | **tvlKcFYnW** | **action (HITL)** | ❌ 170015 "No app found" ← YOUR TASK |

Spawn command (no inputs):
```
uip maestro case process run clearflow-solution.caseManagement.clearflow-master-crisis \
  de7b7c18-d743-4c8c-b555-9bd3b96fe524 \
  --release-key <master release key in v110> -i '{}'
```
Watch it: `uip maestro case instance get -f <folderKey> <instanceId>` (cursors), `... instance element-executions -f <folderKey> <instanceId>`, `... instance incidents -f <folderKey> <instanceId>`.

---

## 2. Live tenant identifiers (v110)

- **v110 folder key (GUID):** `de7b7c18-d743-4c8c-b555-9bd3b96fe524`
- **v110 folder numeric Id (for OData headers):** `3059530`
- **Shared folder key:** `dbc3d831-3724-402d-bd61-94e6afd8bdf3` (numeric Id `2984540`)
- **master‑crisis processKey:** `clearflow-solution.caseManagement.clearflow-master-crisis` (release key changes per deploy — get via `uip or processes list --folder-key <v110>`)
- **BAA‑corpus CG index:** created IN v110 (id `bc3b9560-…`), backed by bucket **`baa-corpus-docs`** (v110 bucket Id `198554`), 6 BAA docs ingested (Successful). The agent resolves CG in its EXECUTION folder, so the index MUST live in v110 (not Shared).
- **Coded agent processes in v110** (created via `uip or processes create`, names MUST match bindings): `claim-flow-anomaly-detector`, `forensic-self-exam-agent`, `multi-customer-pattern-detector`.
- **Low‑code agent releases** must be renamed PascalCase→kebab after EVERY redeploy (see §5).

---

## 3. Auth — python `uipath` tool token expires hourly (CRITICAL)

Node `uip` refreshes silently; the python tool (Context Grounding, `uip context-grounding …`) uses a SEPARATE token that 401s when stale. To refresh non‑interactively:
```bash
RT=$(grep '^UIPATH_REFRESH_TOKEN=' ~/.uipath/.auth | cut -d= -f2-)
AT=$(curl -s -X POST "https://staging.uipath.com/identity_/connect/token" \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "client_id=36dea5b8-e8bb-423d-8e7b-c808df8f1c00" \
  --data-urlencode "refresh_token=$RT" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
# write AT into BOTH ~/.uipath/.auth and repo .env (UIPATH_ACCESS_TOKEN=) lines
```
`36dea5b8-e8bb-423d-8e7b-c808df8f1c00` = the CLI public client_id (from `@uipath/context-grounding-tool/dist/tool.js` DEFAULT_CLIENT_ID). Do NOT use UIPATH_APP_ID/SECRET (→ `invalid_client`). The raw Orchestrator OData API (curl) uses the same Bearer token + header `X-UIPATH-OrganizationUnitId: <folder numeric Id>`.

---

## 4. THE IMMEDIATE TASK — wire the Action Center HITL

### 4a. Details to collect from the user (they're creating the app)
Ask for ALL of:
1. **Action Center app / action name** (exact, as deployed) and whether it's an **App action** or a **Form**.
2. **Catalog name** the action is registered under in Action Center.
3. **Folder** it's deployed/visible in (must be reachable from v110 — ideally deploy it INTO `CascadeCare-v110`).
4. **Input schema** the app expects (so we pass the fiduciary‑conflict payload from the `fiduciary-conflict-detector` agent — payer_demand, affected_provider_baas, clearflow_obligations, plus the agent's conflict output).
5. **Output schema** the app returns — MUST produce the four outputs the action task already declares: `ReviewerId`, `ReviewerDecision`, `ReviewerContext`, `ReviewTimestamp` (these feed the post‑HITL stages).
6. The app's **deployment key / process identifier** once published.

### 4b. The action task to wire
File: `maestro_case/clearflow-master-crisis/caseplan.json` → node `Stage_LKuLeU` (Fiduciary Review) → task `tvlKcFYnW`:
```json
{ "id":"tvlKcFYnW","type":"action",
  "data":{ "taskTitle":"Tri-Party Fiduciary Conflict: Apex vs ClearFlow vs Provider BAAs",
           "priority":"High","inputs":[],
           "outputs":[ReviewerId, ReviewerDecision, ReviewerContext, ReviewTimestamp] } }
```
Currently `inputs:[]` and **no app/catalog binding** → the runtime can't find an app (170015). You must add the app/catalog reference + input mappings. **You'll need the exact Maestro Case "action" task → Action Center app binding schema** — inspect `.uipath-skills/skills/uipath-maestro-case/references/` (case-editing-operations.md, implementation.md) and/or compare with a Studio‑Web‑authored action that references an app (author one in the canvas, `uip maestro case download --extract`, diff the JSON). Do NOT guess the schema.

### 4c. CRITICAL deploy mechanics for action‑task edits
The runtime executes the COMPILED `caseplan.json.bpmn`, NOT `caseplan.json`. CLI pack does **not** regenerate the `.bpmn`. So either:
- Author the action wiring in the **Studio Web canvas**, then `uip maestro case download --extract` to pull the regenerated `caseplan.json` + `.bpmn` (PREFERRED — and also lets you do the durable node‑reorder fix, see §6), OR
- Hand‑patch the `.bpmn` like the prior fixes (see git log `400caf6`) — fragile.

### 4d. After the gate renders
Spawn → case pauses at the Action Center task (Suspended/waiting). Either a human completes it in Action Center, OR complete it via CLI to drive to Closed (provide ReviewerDecision etc.). Then verify Stage 6 **Litigation Defense** runs `negligent-monitoring-risk-agent` (tNWP… / thCAPt9PP) and Stage 7 **Closed** (note: Closed stage is empty unless the `case-closed-notification` BPMN is wired — see `maestro_bpmn/case-closed-notification/`, scaffolded, optional).

---

## 5. The full redeploy recipe (when you change caseplan/agents/.bpmn)

```bash
# 1. assemble canonical sources into the solution
bash scripts/pack-solution.sh
# 2. pack a NEW version
uip solution pack maestro_case/clearflow-solution /tmp/vNEW -v 1.0.NN --output json
# 3. BAA-CLEAN the zip (pack re-injects publish-breaking folder-scoped BAA resources from the tenant)
python3 - <<'PY'
import zipfile,io,json
P='/tmp/vNEW/clearflow-solution_1.0.NN.zip'; OUT=P.replace('.zip','_clean.zip')
good=zipfile.ZipFile('dist/clearflow-solution_1.0.8.zip').read('resources/solution_folder/process/agent/BAABoundaryReasoner.json')
DROP={'resources/Shared/index/BAA-corpus.json','resources/solution_folder/bucket/orchestratorBucket/baa-corpus-docs.json','resources/solution_folder/index/BAA-corpus_1.json'}
SUB='resources/solution_folder/process/agent/BAABoundaryReasoner.json'
zin=zipfile.ZipFile(P); zout=zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    if it.filename in DROP: continue
    zout.writestr(it, good if it.filename==SUB else zin.read(it.filename))
zout.close(); print('clean:',OUT)
PY
# 4. publish + upgrade v110 (deploy run with same --name upgrades in place; no 4004)
uip solution publish /tmp/vNEW/clearflow-solution_1.0.NN_clean.zip --wait --output json
uip solution deploy run --name CascadeCare-v110 --package-name clearflow-solution \
  --package-version 1.0.NN --folder-name CascadeCare-v110 --parent-folder-path "Shared" --output json
# 5. RE-RENAME low-code releases (redeploy resets them to PascalCase → bindings 170007)
#    For each: uip or processes edit <key> -n <kebab-name>   (get keys: uip or processes list --folder-key <v110>)
#    vector-hypothesis-agent, baa-boundary-reasoner, fiduciary-conflict-detector, negligent-monitoring-risk-agent
# 6. (coded agent processes + BAA-corpus index persist across solution upgrades — only recreate if you make a NEW folder)
```

---

## 6. Gotchas / non‑obvious facts (READ)

- **Compiled `.bpmn` is the runtime truth.** Only Studio Web canvas regenerates it; CLI pack ships whatever `.bpmn` is on disk. The master `.bpmn` currently has a **hand‑patched start event** (commit `400caf6`) — if anyone regenerates it via canvas WITHOUT first reordering nodes so `Stage_ugoiTN` (Initial Response, `case-entered`) is **nodes index 0**, the start event disappears and the case stops walking. Durable fix = reorder nodes + canvas regen.
- **Agent index‑binding `folderPath` is stripped by pack** and the runtime resolves CG in the EXECUTION folder anyway → CG indexes must be in v110.
- **CG index names are tenant‑unique** (can't have BAA‑corpus in both Shared and v110).
- **Coded agents** can't deploy to Solution folders via `uip codedagent deploy -f` (no feed). They're in the **tenant feed**; bind into the folder with `uip or processes create --package-key <name> --package-version 0.1.0 --name <name> --folder-key <v110>` (name MUST match the case binding default).
- **Low‑code agents** deploy as PascalCase releases but case bindings use kebab → rename every redeploy (§5).
- **Serverless execution** works in solution‑deployed folders (v110); manually‑created folders 170007 "no unattended robot."
- **Benign noise during the walk:** repeated `450007 "Duplicate message subscription"` / `450013` incidents — case still advances; ignore.
- **OneDrive/WSL:** `rm -f .git/index.lock` if git commits fail with a lock error; `wsl --shutdown` for EIO.
- **The `clearflow-network-command` app** is a declarative Studio‑Web dashboard (NOT the HITL form) and can't be CLI‑built (no local frontend source). Don't try to deploy it for the HITL.

---

## 7. Key commits (branch `slice-023-autowalk-5stages`)
- `400caf6` — master `.bpmn` mainline start‑event fix (THE auto‑walk root cause)
- `ab7d096` — scenario‑default inputs for the 4 low‑code agents
- `3977948` — synthetic BAA corpus (`corpus/baa-corpus/`, ingested into the v110 CG index)
- `3cd5446` — `.agent-builder/` regeneration (agents load in Studio Web)
- (this commit) — `maestro_bpmn/case-closed-notification/` scaffold + this handoff

## 8. First moves for the new session
1. `cat ~/.claude/.../memory/master-case-autostart-bpmn-fix.md` (full context).
2. Refresh the python token (§3) if doing CG; node `uip` likely still works.
3. Confirm current state: `uip maestro case process run … -i '{}'` then check it walks to Stage 5 and faults at `tvlKcFYnW` 170015.
4. Collect the Action Center app details from the user (§4a).
5. Determine the Maestro action→app binding schema (§4b), wire `tvlKcFYnW`, redeploy (§5), confirm the gate renders, drive to Closed.
