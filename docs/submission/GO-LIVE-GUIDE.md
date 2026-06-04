# CascadeCare — Go-Live & Submission Guide (novice edition)

> **Who this is for:** someone who has never touched UiPath, Maestro, Orchestrator, or Studio Web.
> Every step says **who does it**, **exactly what to do**, **what you should see**, and **what to do if it goes wrong**.
>
> **Last updated:** 2026-06-04 (v1.0.5 deployed + activated to `Shared/CascadeCare-v105` with the spawn `folderId` fix; current step = **STEP 4**, re-trigger the BPMN to confirm the case spawns) · **Branch:** `slice-023-reentry-agent-memory` · **Tenant:** `staging.uipath.com/hackathon26_042/DefaultTenant`
>
> **How to read the owner tags:**
> - 🟢 **ME** = Claude Code can do this alone, offline, no tenant/browser. Just ask.
> - 🟡 **YOU-RUN** = a command that hits the live tenant. *I write it; you run it* (or paste it here prefixed with `!` and the output comes back to me).
> - 🔴 **HUMAN-ONLY** = no automation possible — clicking in a browser, recording, registering apps, submitting forms, sending email.

---

## 0. The 30-second mental model

Your project is a **bundle of files in this repo**. To make it real, that bundle gets **packed into a `.zip`** (a `.uipx` "solution") and **uploaded + installed** ("deployed") onto a **website** (UiPath Automation Cloud). Then you **press go** ("trigger") and watch it run in the browser.

| Term | Plain English | Where it lives |
|---|---|---|
| **Automation Cloud** | The website where everything runs. | `staging.uipath.com/hackathon26_042` |
| **Tenant** | Your private workspace on that website. | `DefaultTenant` |
| **Orchestrator** | The part that runs and schedules jobs. | inside the tenant |
| **Folder** | A labelled box on the tenant that holds one deployment. | e.g. `CascadeCare-v104` (current) |
| **Studio Web** | The browser editor where you draw/fix flowcharts & cases. *(The screenshot you sent was this.)* | browser |
| **Maestro Case** | The long-running "case file" — your crisis, with stages. You have **3** (master → parent → grandchild). | the runtime brain |
| **Maestro BPMN** | A flowchart process. The file we just fixed (`ideal-incident-response`) is one. | `maestro_bpmn/` |
| **Maestro Flow** | The "Demo Driver" that plays the demo like a script. | `maestro_flow/` |
| **Agent / Agent Builder** | The 7 AI agents that reason about the crisis. | `agents/` |
| **Data Fabric** | The database of made-up providers, payers, contracts (BAAs), telemetry. | tenant DB |
| **Context Grounding** | Search indexes the agents read (over BAAs + telemetry). | tenant |
| **Solution (`.uipx`)** | One zip bundling ALL projects so they deploy together. | `maestro_case/clearflow-solution/` |
| **Deploy** | Upload + install that zip into a folder. | `uip solution deploy` |
| **Trigger / Run** | Press go — start one execution. | browser or CLI |
| **`uip`** | The command-line tool that talks to the tenant. Version **1.1.0**. | your terminal |

**The big truth:** ~95% of the *building* is finished. What's left is **deploy → trigger → rehearse → record → submit**. Several of those last steps are *inherently human* — the contest requires a human-recorded live video and a human-filled submission form.

---

## 1. ⏰ Time-critical (do these first)

| When | What | Owner | Why it can't slip |
|---|---|---|---|
| **June 5 (tomorrow)** | Email **`andreea.tomescu@uipath.com`** to request **UiPath Labs access for judges**. | 🔴 HUMAN-ONLY | Without it, judges may not be able to see your live tenant at all. |
| Now → June 29 | Final submission on Devpost. Judging is **rolling** (started June 3), so earlier = more eyeballs. | 🔴 + 🟢 | Hard deadline. |
| June 9, 3–4 PM UTC | (Optional) Best-practices session w/ a prior winner (Ebru Sarikaya). | 🔴 | Free intel. |

> ⚠️ **Deadline timezone:** the project's own notes disagree — `CLAUDE.md` says **11:45 PM PDT**, the intel memory says **EDT**. **Confirm the exact time on the Devpost page itself** and treat the earlier of the two as your real deadline.

---

## 2. Where things stand right now (snapshot)

### ✅ Done / built (offline, machine-verified)
- All **runtime artifacts authored**: 3 Maestro Cases, 4 Agent Builder agents, 3 Coded Agents, 14 API Workflows, 1 BPMN, 1 Maestro Flow, 1 App.
- **Full solution packs clean** (`clearflow-solution`, 9 projects).
- **Case diagrams render** live (the "Unable to load diagram" bug is fixed).
- **BPMN Error 1654 fixed** (canonical `processorchestration` shape).
- **BPMN → case binding fixed offline** (`clearflow-crisis` → `clearflow-master-crisis`) — *needs a re-deploy to take effect live.*
- **Today's fix:** the `ideal-incident-response` BPMN's `isCascade` variable + by-name gateway (committed `24b5e59`).
- **Data Fabric seed tooling** + cleanup tooling exist and pass dry-run gates.
- **Submission docs**: README (names every component), LICENSE (MIT), `CODING_AGENTS.md`, `CLAUDE_CODE_USAGE.md`.
- Test suite ~541 passing; IP-safety audit clean.

### ✅ Just completed (2026-06-04, live)
- **Deployed clean, twice.** v1.0.4 → `CascadeCare-v104` (isCascade fix); first live run proved the cascade gateway works but faulted at the spawn node (`170005 folderId`). **v1.0.5** → **`Shared/CascadeCare-v105`** adds the spawn fix (type `v2` + `name`/`folderPath` bindings). All 9 projects passed the atomic install both times.
  - v1.0.5: DeploymentKey `cb489f53-c3be-4a26-a888-6fee76fcf0a3` · FolderKey **`bc56e117-70f0-4234-b320-b751df1c4546`** · InstanceId `3bd167a3-…_v6`.

### ⏸ Pending (mostly live tenant + human capture)
1. ~~**Re-deploy** so the fixes go live.~~ ✅ **DONE** → `CascadeCare-v105` (v1.0.5).
2. ~~**Re-trigger the BPMN** in `CascadeCare-v105` → confirm a `clearflow-master-crisis` case spawns.~~ ✅ **DONE & CONFIRMED 2026-06-04** — BPMN completed all-green, spawn node green, master case `clearflow-master-crisis-66114817` spawned + Running in CascadeCare-v105 with all stages/reversals rendered, no incidents.
3. **Run the 5 reversals** end-to-end (demo dry-run).
4. **Seed Data Fabric** live.
5. **Clean up** stale/failed deployments.
6. **(Optional)** Unblock the UiPath **App** (OAuth External Application).
7. **Record** the ≤5-min demo video + 1-min coding-agent reel.
8. **Write & submit** the Devpost page.
9. **Build** the slides deck.
10. **Tag** `agenthack-2026-submission` (only *after* the live video exists).

### Current tenant deployments (live query, 2026-06-04)
- ✅ **`CascadeCare-v105`** — folder key **`bc56e117-70f0-4234-b320-b751df1c4546`**, `clearflow-solution v1.0.5`, all 9 projects, **Active**. **← THIS is now your master deployment** (has isCascade + the spawn folderId fix).
- ⤵️ **`CascadeCare-v104`** — folder key `82485e42-1f2a-4ec8-8621-2ebfc31b2dbe`, `v1.0.4`, Active but **superseded** (faults on spawn — no folder identity). Uninstall in Step 7.
- ⤵️ **`CascadeCare-Full`** — folder key `73941f02-6602-4585-b9a8-5a391179845d`, `v1.0.3`, superseded (predates the fixes). Keep as fallback or uninstall.
- 🧹 Stale/failed to remove: `CascadeCare-Demo` (v1.0.2), `CascadeCare-Live` (**Failed**, v1.0.1), `CascadeCare-Core` (`clearflow-core` v1.0.0).

---

## 3. The three buckets at a glance

### 🟢 Bucket A — I can do alone, right now
- Commit code (✅ today's fix already committed).
- Draft the **Devpost page text** (business problem, architecture, component inventory).
- Write the **5-minute video narration script** + click-by-click run checklist.
- Final IP-safety audit, README/changelog polish.
- Prepare **exact copy-paste commands** for every live step.
- Diagnose any error output you paste back from a live run.

### 🟡 Bucket B — You run, I write the command
- `uip login`, pack, publish, deploy.
- Trigger the BPMN + case.
- Seed Data Fabric live.
- Clean up old deployments.

### 🔴 Bucket C — Only you (human)
- Email for **Labs access** (June 5).
- **Click in Studio Web canvas** — re-import the fixed BPMN; re-generate case diagrams (these are *only* produced by the browser canvas).
- **Register an OAuth External Application** in Admin (unblocks the App).
- **Record** the demo video + reel; upload to YouTube/Vimeo.
- **Submit** the Devpost form.
- **Build** the slides.

---

## 4. Pre-flight — get your machine ready (one time)

> 🟡/🔴 You do this once per session. These are *prerequisites* for every live step below.

### 4.1 Open a terminal in the project
```bash
cd /mnt/c/Users/linki/OneDrive/Desktop/cascade_command
```

### 4.2 Make the packager find .NET (required before any pack/build)
The solution packager needs the .NET 8 SDK, installed user-local at `~/.dotnet`:
```bash
export PATH="$HOME/.dotnet:$PATH"
```
**What to expect:** no output = success. (Run this in *every new terminal* before packing.)

### 4.3 Check the CLI is present
```bash
uip --version
```
**Expect:** `1.1.0` (or similar). If "command not found," the `uip` CLI isn't installed — tell me and I'll give install steps.

### 4.4 ⚠️ Known environment hazard — OneDrive/WSL
This repo lives on a Windows OneDrive path mounted into WSL. Occasionally the mount throws an **`EIO` (input/output) error** that kills `git`, file writes, or the pre-write hooks mid-command.
- **Symptom:** a command suddenly fails with `EIO`, `Input/output error`, or a wedged hook.
- **Fix:** from a **Windows PowerShell** (not WSL), run `wsl --shutdown`, wait 10 seconds, reopen the terminal, `cd` back, and retry. Nothing is corrupted — it's just the mount.

---

## 5. THE RUNBOOK (do in order)

Each step: **Owner → Why → Do → Expect → If it breaks.**

---

### STEP 1 — Confirm today's BPMN fix in the real editor
**Owner:** 🔴 HUMAN-ONLY (browser) — I've already committed the file.

**Why:** The command-line validator says "Valid," but your own past notes warn it's *too lenient* to catch Studio Web variable problems. The **editor is the real judge.** We need to see the red errors actually gone.

**Do:**
1. Open Studio Web → the `clearflow-solution` → the `ClearFlowIdealIncidentResponse` process.
2. **Re-import / re-sync** it from the repo (so the canvas picks up commit `24b5e59`).
3. Look at the **Health analyzer** panel on the left (where the red dots were).

**Expect:** The four earlier errors are **gone**:
- ~~`vars.Var_IsCascade does not exist`~~
- ~~`vars.Var_AffectedCustomerCount does not exist`~~
- ~~`incidentId is not set at this point`~~
- ~~`Process response` references a removed variable~~

The **"Case management *"** field should auto-populate with the master crisis case once the binding resolves (it pulls from `bindings_v2.json`).

**If it breaks:**
- If **any** "does not exist" error remains → **copy the exact text and send it to me.** Do **not** try to fix it by hand in the canvas.
- ⚠️ **Never hand-delete the "Process response" output row** in the canvas. There's a known Studio Web bug: delete+save *multiplies* that row (one copy per field) and it snowballs. The correct fix is always: fix the source file → re-upload (upload *wholesale-replaces* the BPMN and cleans duplicates).

---

### STEP 2 — Log in to the tenant
**Owner:** 🟡 YOU-RUN

**Why:** Every live command needs your authenticated session. The interactive login carries **full permissions**; the saved automation key only has a subset, so always use interactive.

**Do:**
```bash
uip login
```
A browser window opens → sign in as **`puneetsatyawan@gmail.com`**.

**Expect:** Terminal prints something like `Login successful`. You're now connected.

**If it breaks:** If the browser doesn't open, the CLI usually prints a URL — paste it into a browser manually. If login succeeds but later commands say "unauthorized," you likely logged into the wrong tenant — re-run and pick `hackathon26_042 / DefaultTenant`.

---

### STEP 3 — Re-deploy the full solution (ships the fixes) ✅ DONE 2026-06-04
**Owner:** 🟡 YOU-RUN — **completed.**

**Why:** The old folder predated two fixes: the BPMN→case **binding** (without it, the flow runs but silently spawns *no* case), and the **isCascade** fix. Re-deploying shipped both.

**What actually happened — the corrected 4-step recipe** (the first two are *local*, no tenant; the last two hit the tenant). ⚠️ The original draft was wrong: `publish` needs the **`.zip` produced by `pack`**, *not* the solution directory.
```bash
export PATH="$HOME/.dotnet:$PATH"                                              # Step 4.2
bash scripts/pack-solution.sh                                                  # 1. stage sources (local)
uip solution pack maestro_case/clearflow-solution dist --version 1.0.4 --output json   # 2. build dist/clearflow-solution_1.0.4.zip (local)
uip solution publish dist/clearflow-solution_1.0.4.zip --output json          # 3. publish zip to feed (tenant)
uip solution deploy run \                                                      # 4. install + auto-activate (tenant)
  --name cascadecare-v104 \
  --package-name clearflow-solution --package-version 1.0.4 \
  --folder-name CascadeCare-v104 --parent-folder-path "Shared" --output json
```

**Result (recorded):** `DeploymentSucceeded` + `SuccessfulActivate` → folder **`Shared/CascadeCare-v104`** (FolderKey `82485e42-1f2a-4ec8-8621-2ebfc31b2dbe`). The pack log confirmed `ProcessOrchestration BPMN validation completed` (the isCascade fix survived). The `dotnet CLI is not available… package signing` warning is **benign** — unsigned is fine here.

**To re-deploy again later** (e.g. after another fix): bump `--version` (e.g. `1.0.5`) in steps 2–4 and use a **fresh `--folder-name`** to dodge Error 4004.

**If it breaks (for next time):**
| Error | Meaning | Fix |
|---|---|---|
| `Invalid file type. Expected a .zip` | You ran `publish` on the **directory**, skipping `pack`. | Run `uip solution pack <dir> dist --version X` first, then publish the `.zip`. |
| **Error 1654** "entry points definition invalid" | A BPMN/case package shape regressed. | Paste it to me — the canonical fix is documented (commit `61a10cd`). |
| **Error 2005** "Package metadata extraction failed" | An API-workflow is missing its `entry-points.json`/`bindings_v2.json`. | Paste it to me — fix is documented (commit `98b6749`). |
| **Error 4004** on deploy | The folder name already holds a deployment. | Deploy to a fresh `--folder-name`, **or** uninstall the old one first (Step 7). |
| Rolls back entirely | Deployment is **atomic** — one bad project fails all 9. | The error names the culprit project; paste it to me. |

---

### STEP 4 — Trigger the BPMN and confirm a case spawns  ◀️ **YOU ARE HERE**
**Owner:** 🔴 HUMAN-ONLY via browser *(recommended)* — 🟡 CLI alternative below.

**Why:** This is the heart of the demo: the incident-response flowchart must **spawn the master crisis case.** It's also the live smoke-test that the v1.0.4 binding fix actually works.

**Do (browser — easiest, and you'll be here for the video anyway):**
1. In the tenant, switch to the **`CascadeCare-v105`** folder (top-left folder picker). *(Shared/CascadeCare-v105 — the current deployment with the spawn fix.)*
2. Open **Maestro → Processes** → select **`ClearFlowIdealIncidentResponse`**.
3. Click **Start / Run**, and in the inputs set:
   - **`isCascade` = `true`**  ← *(today's fix: this boolean now drives the cascade branch)*
   - `affectedCustomerCount` = `3` (harmless to include)
   - `incidentId` = any string, e.g. `INC-001`
4. Confirm.

**Expect:** A brand-new **`clearflow-master-crisis`** case instance appears in **Maestro → Cases** with status **Open**, goal *"Determine if ClearFlow is the breach vector."*

> **🧪 Run history (2026-06-04):**
> - **v1.0.4 run:** Intake → Triage → `is_cascade?` green, **correctly took the `cascade` branch** (`isCascade=true` confirmed working). Faulted at the spawn node with `170005 folderId missing`.
> - **Fix shipped in v1.0.5:** the spawn activity (`Orchestrator.StartCaseMgmtProcessAsync`) now uses type **`v2`** with inline **`name` + `folderPath`** bindings to `clearflow-master-crisis` — the folder identity that was missing. Deployed to **`CascadeCare-v105`**.
> - ✅ **CONFIRMED 2026-06-04:** re-run in v105 completed all-green; the spawn node went green and `clearflow-master-crisis-66114817` spawned + is Running in CascadeCare-v105 (Folder shown in the spawn trace = `CascadeCare-v105`, proving the `folderPath` binding resolved). The async spawn child shows Status `Unset` / `masterCaseId` blank — expected for fire-and-continue `...Async`; the BPMN launches the crisis without waiting.

**If it breaks:**
- **`170005` — "Required field 'folderId' missing in the input args to RPA task"** (faults at `Spawn master crisis case`) → ✅ **RESOLVED in v1.0.5.** Root cause: the `StartCaseMgmtProcessAsync` call activity had only a `releaseKey` binding, no folder identity. Fix (committed): type `v1`→`v2`; context inputs `name` (=bindings, propertyAttribute `name`) + `folderPath` (=bindings, propertyAttribute `folderPath`), both `resourceKey="clearflow-master-crisis"`; keep the required `JobArguments` + `Process response`/`Orchestrator.RunJob` output. **How we found the exact contract:** the **`uip solution pack` CLI is the authoritative validator** — stricter than both the Studio Web Health analyzer and the canvas. It printed the precise required/forbidden inputs. Always trust the packer's error over the editor for this activity.
- Flow runs but **no case appears** → the binding fix didn't make it into the deployed package. Re-check Step 3 used the freshly-packed `.zip`; tell me and I'll verify the registration manifest.
- The cascade branch is **skipped** → you didn't set `isCascade = true`. The gateway condition is `=vars.isCascade == true`. *(Confirmed working on 2026-06-04.)*

**Do (CLI alternative):** *(folder key for `CascadeCare-v105` = `bc56e117-70f0-4234-b320-b751df1c4546`)*
```bash
uip maestro case process run "<dotted-ProcessKey>" bc56e117-70f0-4234-b320-b751df1c4546 \
  --release-key <RELEASE_GUID> --inputs '{"isCascade":true,"affectedCustomerCount":3,"incidentId":"INC-001"}'
```
> Need the `<dotted-ProcessKey>` + `<RELEASE_GUID>`? Paste me `uip maestro case process list bc56e117-70f0-4234-b320-b751df1c4546 --output json` and I'll fill them in. (Browser is genuinely easier here — use it unless you're scripting.)
> ⚠️ **Do NOT add `--validate`** — it calls a broken schema lookup that throws a *misleading* `1654 "Invalid package key format"`. Without it, the run succeeds. Use the **Orchestrator folder key directly** (there is no separate "Maestro folder"); `case process list` may reject it, but `process run` accepts it.

---

### STEP 5 — Seed the Data Fabric database (live)
**Owner:** 🟡 YOU-RUN

**Why:** The agents reason over synthetic providers/payers/BAAs/telemetry. If the database is empty, their output is hollow. Do this *before* a full reversal run.

**Do:**
```bash
UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply
```

**Expect:** It creates **9 entity types** (6 providers, 4 payers, 1 vendor, 1 regulator, 1 insurer, 1 counsel, 6 BAAs, ~4,320 telemetry rows, 1 template) + **2 Context Grounding indexes** (`BAA-corpus`, `ClaimTelemetry-corpus`). Verify in **Data Fabric → Entities** that the row counts are non-zero.

**If it breaks:** Without `UIPATH_LIVE=1` it runs in *dry-run* (emits JSON, touches nothing) — if you see JSON instead of tenant writes, you forgot the flag. Index build can take a minute; refresh the Context Grounding page.

---

### STEP 6 — Run the 5 reversals end-to-end (demo dry-run)
**Owner:** 🔴 HUMAN-ONLY (browser)

**Why:** This is your rehearsal. You want every transition to render cleanly *before* the camera is on.

**Do:**
1. With the master case open (Step 4), the **Demo Driver Flow** (`maestro_flow/clearflow-demo-driver`) fires the reversal events at compressed intervals. Start it from **Maestro → Flows** in the same folder.
2. At **Reversal 4**, a **human-approval task** appears in **Action Center** → open it and **Approve** (this is the tri-party HITL gate).
3. Watch the **case canvas** — stage transitions and the grandchild fan render here. This is your on-camera surface.

**Expect — the reversal cue sheet (also your narration timeline):**

| # | t+ (wall clock) | Trigger | What the camera shows |
|---|---|---|---|
| R1 | 0s | Case start (Step 4) | Master case opens; goal *"Assist isolated customers."* |
| R2 | ~25s | Demo Driver event | ClearFlow **cleared**; Nimbus identified as the vector. |
| **R3** | **~150s** | **TN DOI subpoena** | **★ HERO: 6 grandchild cases spawn simultaneously** in a fan. |
| R4 | ~t+200s | Payer-demand event | Fiduciary Conflict Detector → **HITL approval gate** (you approve). |
| R5 | ~t+260s | Litigation event | Bystander → **co-defendant**; privilege reshuffles. |

**If it breaks:** If a reversal doesn't fire, note **which one** and what the canvas showed, and paste it here. If R3 doesn't fan out 6 grandchildren, the grandchild binding/seed may be missing — tell me.

---

### STEP 7 — Clean up stale deployments
**Owner:** 🟡 YOU-RUN

**Why:** Old failed deployments clutter the tenant and confuse judges. Your live folder is now **`CascadeCare-v104`** (and optionally keep `CascadeCare-Full` v1.0.3 as a fallback).

> 🚨 **STOP before running this.** `scripts/cleanup_deployments.sh`'s hard keep-list currently guards **`CascadeCare-Full`**, *not* `CascadeCare-v105` (your current live folder). If you run it as-is, it may **uninstall the wrong thing.** Ask me to update the keep-list to protect `CascadeCare-v105` first — don't run `--confirm` until then. (Stale folders now also include `CascadeCare-v104`.)

**Do:**
```bash
bash scripts/cleanup_deployments.sh --dry-run    # review what WOULD be removed — SAFE, changes nothing
# (after I update the keep-list to include CascadeCare-v104:)
bash scripts/cleanup_deployments.sh --confirm    # actually uninstall the stale ones
```

**Expect:** `--dry-run` lists removal candidates (`CascadeCare-Demo`, `CascadeCare-Live`, `CascadeCare-Core`, etc.). **Verify `CascadeCare-v104` is NOT in the removal list** before you ever run `--confirm`.

**If it breaks:** If an uninstall errors, paste it here. (Easiest alternative: uninstall one at a time with `uip solution deploy uninstall <name> --output json`.)

---

### STEP 8 — (Optional) Unblock the UiPath App dashboard
**Owner:** 🔴 HUMAN-ONLY (Admin) + 🟢 ME (wire-up)

**Why:** The narrative dashboard App is blocked on a tenant **OAuth External Application** registration (and a known app-shape quirk).

**Do (you):**
1. Automation Cloud → **Admin → External Applications → Add Application**.
2. Create a **confidential** app, grant the relevant scopes, set a redirect URI.
3. Copy the **Client ID**, **Client Secret**, **scopes**, **redirect URI** and give them to me.

**Then (me):** I wire those into the app config and re-attempt deploy.

**Expect:** If it works, the dashboard becomes viewable. **If you're short on time, SKIP this** — the App is *not* a required submission artifact. The required "live" artifact is the **case/agent run**, which you already have.

---

### STEP 9 — Record the demo video
**Owner:** 🔴 HUMAN-ONLY (record) + 🟢 ME (script)

**Why:** Required artifact. Must show the solution **running live on Automation Cloud (not slides)**, ≤5 minutes, and **name each agent** as it fires.

**Do:**
1. Ask me for the **word-for-word narration script** (timed to ~5:00, hero moment at ~2:30).
2. Screen-record the live run from Steps 4–6 following the script.
3. Do 2–3 takes; pick the strongest.
4. Also grab a **1-minute "built with coding agents" reel** (bonus points) — show Claude Code authoring/diagnosing.
5. Upload to **YouTube or Vimeo** (public or unlisted).

**Expect:** Two video links (main + reel).

---

### STEP 10 — Write & submit the Devpost page
**Owner:** 🔴 HUMAN-ONLY (submit) + 🟢 ME (draft)

**Why:** Required artifact.

**Do:**
1. Ask me to **draft the full page text** — title, **Track 1**, business problem, "how it works," architecture diagram callouts, and the complete UiPath-component inventory.
2. On Devpost: paste the text, add screenshots, paste the video link, list teammates, attach the GitHub repo + LICENSE.
3. **Submit.**

**Expect:** A complete, submitted project page.

---

### STEP 11 — Tag the release
**Owner:** 🟢 ME (only after the live video exists)

**Why:** The project has an honesty rule: the `agenthack-2026-submission` tag asserts a *recorded live demo*. Tagging from an offline session would be dishonest.

**Do:** After the video is recorded, tell me — I apply the tag at the same commit as the final video upload.

---

## 6. Master error reference (paste any of these to me)

| Error / symptom | Where | Root cause | Action |
|---|---|---|---|
| `Error 1654` "entry points definition is invalid" | deploy / install | BPMN or case package shape regressed | Documented fix (`61a10cd`) — paste to me |
| `1654` "Invalid package key format" | `case process run` | The **`--validate`** flag's broken lookup | **Remove `--validate`** |
| `Error 2005` "Package metadata extraction failed" | API-workflow install | missing `entry-points.json`/`bindings_v2.json` | Documented fix (`98b6749`) — paste to me |
| `Error 4004` | deploy run | Folder already holds a **failed** deployment | Fresh `--folder-name` or uninstall first |
| `170005` "Required field 'folderId' missing in the input args to RPA task" | runtime, at a `StartCaseMgmtProcessAsync` / `StartJob` call activity | The activity has `releaseKey` but **no folder identity** | ✅ Fixed in v1.0.5: type `v2` + inline `name`/`folderPath` bindings (`resourceKey="clearflow-master-crisis"`) + keep `JobArguments` & `Process response`/`Orchestrator.RunJob` output |
| Pack fails: `... does not support context input "_label"` / `missing required input payload "JobArguments"` / `output name must be "Process response"` | `uip solution pack` | The **CLI packer is the authoritative validator** for activity contracts — stricter than the Health analyzer and the Studio Web canvas | Read the packer error literally; it names every required/forbidden input. Trust it over the editor |
| Flow runs, **no case spawns** | runtime | binding `clearflow-crisis` was dangling | Ensure re-deploy used the fixed `.zip` |
| "does not exist" on a `=vars.X` | Studio Web editor | reference uses the wrong form — this editor resolves by **name**, not id; declarations must be `id==name`, process-scoped, `custom="true"` | Tell me; I fix the source + you re-upload |
| "Process response" row multiplies | Studio Web editor | known canvas delete+save bug | **Never hand-delete**; fix source → re-upload (wholesale replace) |
| "Unable to load diagram" on a case | runtime | `caseplan.json.bpmn` missing / project was `content/`-nested | Diagrams are generated **only** by the browser canvas; project must be **flat** |
| `EIO` / `Input/output error` / wedged hook | any command | OneDrive/WSL mount stall | `wsl --shutdown` (from PowerShell), wait, retry |
| `dotnet`/pack fails to start | pack/build | .NET not on PATH | `export PATH="$HOME/.dotnet:$PATH"` |

---

## 7. Submission artifact checklist (Devpost)

| # | Artifact | Status | Owner |
|---|---|---|---|
| 1 | Public GitHub repo (MIT) + README naming every component | ✅ DONE | — |
| 2 | Devpost project page (Track 1) | ⬜ PENDING | 🔴 you (🟢 I draft) |
| 3 | Demo video ≤5 min, **live**, names each agent | ⬜ PENDING | 🔴 you (🟢 I script) |
| 4 | Solution running **live** on Automation Cloud | ⬜ PENDING | 🟡 deploy + 🔴 verify |
| Bonus | Coding-agent evidence (`CODING_AGENTS.md`, `CLAUDE_CODE_USAGE.md`) | ✅ DONE | — |
| Bonus | 1-min coding-agent reel | ⬜ PENDING | 🔴 you |
| Supp. | Slides deck (AgentHack template) | ⬜ PENDING | 🔴 you |
| Supp. | Live screenshots / prompt logs | ⬜ PENDING | 🔴 you (capture during run) |

> **Tag rule:** do **not** apply `agenthack-2026-submission` until artifact #3 (live video) exists.

---

## 8. Command cheat-sheet (copy-paste appendix)

```bash
# --- every session ---
cd /mnt/c/Users/linki/OneDrive/Desktop/cascade_command
export PATH="$HOME/.dotnet:$PATH"
uip login                                   # interactive, as puneetsatyawan@gmail.com

# --- deploy the fixes (4 steps; bump --version + --folder-name each time) ---
bash scripts/pack-solution.sh                                                          # stage (local)
uip solution pack maestro_case/clearflow-solution dist --version 1.0.5 --output json   # -> dist/clearflow-solution_1.0.5.zip (local)
uip solution publish dist/clearflow-solution_1.0.5.zip --output json                   # publish zip (tenant)
uip solution deploy run --name cascadecare-v105 --package-name clearflow-solution \
  --package-version 1.0.5 --folder-name CascadeCare-v105 --parent-folder-path "Shared" --output json
#   need DeploymentSucceeded + SuccessfulActivate

# --- inspect deployments / get folder key ---
uip solution deploy list --output json     # CascadeCare-v105 FolderKey = bc56e117-70f0-4234-b320-b751df1c4546

# --- find run keys for the v105 folder ---
uip maestro case process list bc56e117-70f0-4234-b320-b751df1c4546 --output json

# --- trigger the BPMN (CLI; browser is easier) ---
uip maestro case process run "<dotted-ProcessKey>" bc56e117-70f0-4234-b320-b751df1c4546 \
  --release-key <RELEASE_GUID> \
  --inputs '{"isCascade":true,"affectedCustomerCount":3,"incidentId":"INC-001"}'
#   (NO --validate)

# --- seed the database (live) ---
UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply

# --- clean up old deployments ---
bash scripts/cleanup_deployments.sh --dry-run
bash scripts/cleanup_deployments.sh --confirm

# --- inspect real tenant state ---
uip solution deploy list --output json
uip solution download <solutionId> -d /tmp/inspect -n clearflow-solution --extract

# --- recover from a OneDrive/WSL EIO stall (run in Windows PowerShell) ---
wsl --shutdown
```

---

## 9. What to ask me for next (Bucket A — I'll start on your word)

1. **Devpost page draft** — ready-to-paste copy.
2. **5-minute video narration script** + a click-by-click run checklist for demo day.
3. **Exact deploy commands** with the current package name/version filled in (I'll read the freshly-packed `.uipx`).
4. Diagnosis of **any error** you paste from a live run.

When you're ready for the live tenant steps, paste **`! uip login`** here and we'll walk Steps 2–7 together with me reacting to the real output.
