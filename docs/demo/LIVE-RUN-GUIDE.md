# CascadeCare — Live Run Guide (start to finish, for a first-timer)

This walks you through everything left to do on the live UiPath tenant, in order, with
**what to type**, **what you should see**, **what to write down**, and **what to do if it
breaks**. You do not need to understand the internals — just follow the steps top to bottom.

> If you only have 10 minutes and just want the demo to run, skip to **Part 5** (the master
> case may already be deployed). Come back to Parts 2–4 if something is missing or stale.

---

## 0. The mental model (read once, 2 minutes)

You are going to do four things:

| Part | What | Why |
|---|---|---|
| **2 (item a)** | Re-deploy the solution with the fixed BPMN→case binding | So the "incident → spawn master case" step actually fires |
| **3 (item b)** | Delete leftover practice deployments | So there's exactly one clean deployment (`CascadeCare-Full`) |
| **4 (item c)** | Load synthetic data into Data Fabric | So the AI agents have providers/payers/claims/BAAs to read |
| **5** | Run the demo and watch it | The actual R1→R5 story on screen |

You will watch **three surfaces**:

1. **Terminal** — where you type `uip ...` commands. Returns JSON; you read status + copy a few IDs.
2. **Browser (UiPath Cloud)** — `https://staging.uipath.com/hackathon26_042/` (org `hackathon26_042`,
   tenant `DefaultTenant`). This is where the case canvas + fan-out animation render. **This is the
   on-camera surface.**
3. **The Apps dashboard** (optional) — the narrative screen, once published.

**Golden rules**
- Every `uip` command returns JSON. Look for a `status` / `state` field. `Succeeded`, `SuccessfulActivate`,
  `SuccessfulUninstall` = good. Anything with `Failed` / `error` = stop and capture it (see Part 6).
- When a step says **📋 copy this**, paste that value into the next step. These hand-offs (package
  version, folder key, release key) are the #1 thing people get wrong.
- Nothing here deletes your work. The one destructive command (uninstall) is guarded and asks for `--confirm`.

---

## 1. One-time setup

### 1.1 Confirm the CLI is installed
```bash
uip --version
```
**✅ Expect:** a version number.
**❌ If "command not found":** install with `npm install -g @uipath/uipath-cli` (or ask me), then re-run.

### 1.2 Log in (interactive — opens a browser)
```bash
uip login
```
**👀 What happens:** a browser tab opens asking you to sign in to UiPath. Sign in as
**puneetsatyawan@gmail.com** (the account with full tenant rights). Approve, return to the terminal.
**✅ Expect:** the terminal prints something like `Logged in` / shows your org + tenant.
**❌ If it fails:** make sure you picked org `hackathon26_042` and tenant `DefaultTenant`. Re-run `uip login`.

> The login token lasts a while but can expire mid-session. If any later command suddenly says
> "unauthorized" or "token expired", just run `uip login` again and continue.

### 1.3 See what's already deployed (your baseline)
```bash
uip solution deploy list --output table
```
**👀 What you'll see:** a table of deployments (name, status, version, folder). You're looking for
names starting with `CascadeCare-`.
**📋 Write down:** which `CascadeCare-*` deployments exist right now. You'll likely see some of:
`CascadeCare-Full`, `CascadeCare-Core`, `CascadeCare-Smoke`, `CascadeCare-Live`, `CascadeCare-Demo`.
This list tells you what Parts 2–3 need to clean up.

---

## 2. Part A — deploy the binding fix (item a)

**Goal:** publish the corrected solution and run it as a clean `CascadeCare-Full` deployment.

### 2.1 Re-assemble the solution from source
```bash
bash scripts/pack-solution.sh
```
**✅ Expect:** a list of `✓ Found ...` / `Packed ...` lines, then
`✓ 9 manifest projects all resolve on disk` and `pack-solution.sh complete.`
**❌ If it says a source directory is missing:** stop, copy the message, send it to me.

### 2.2 Pack into a deployable package
```bash
uip solution pack maestro_case/clearflow-solution --output json
```
**✅ Expect:** JSON ending in success, with a path to a `.zip` package.
**📋 Copy this:** the **package path** (the `.zip` location) from the output.

### 2.3 Publish the package to the tenant feed
```bash
uip solution publish <PASTE .zip PATH FROM 2.2> --output json
```
**✅ Expect:** JSON confirming the package was published.
**📋 Copy this:** the **package name** and **package version** from the output (e.g. name
`clearflow-solution`, version like `1.0.4`). You need both in step 2.5.

### 2.4 Remove the OLD `CascadeCare-Full` (so we can deploy the fixed one cleanly)
First check if it exists (from your Part 1.3 list). **If `CascadeCare-Full` is NOT in the list, skip to 2.5.**
```bash
uip solution deploy uninstall CascadeCare-Full --output json
```
**✅ Expect:** `status: SuccessfulUninstall` (this can take 1–3 minutes; it polls).
**❌ If it errors:** capture it (Part 6) but you can still try 2.5 — if 2.5 then says the name is in
use, come back and resolve this first.

### 2.5 Deploy the fixed solution as `CascadeCare-Full`
```bash
uip solution deploy run \
  --name CascadeCare-Full \
  --package-name <NAME FROM 2.3> \
  --package-version <VERSION FROM 2.3> \
  --folder-name CascadeCare-Full \
  --parent-folder-path Shared \
  --output json
```
**⏱ Takes:** a few minutes (it provisions cases, agents, the BPMN, the flow — 9 projects — and activates them).
**✅ Expect:** the JSON ends with `DeploymentSucceeded` and then `SuccessfulActivate`.
**📋 Copy this:** the **folder path/key** of the new deployment from the output (you'll need the
folder key in Part 5 if you use the CLI to launch).
**❌ Common errors → see Part 6:**
- `Error 1654` (entry points) — was fixed offline; if it reappears, capture the exact project it names.
- `Error 2005` (entry points configuration) — same; note which `api_workflows/*` project.
- "deployment name already in use" — go back to 2.4 and uninstall `CascadeCare-Full` first.

> **Why this part matters:** before the fix, the BPMN's "spawn master case" step pointed at a name
> (`clearflow-crisis`) that didn't exist in the solution, so it silently did nothing. We retargeted it
> to `clearflow-master-crisis`. You won't *see* this directly — you confirm it works in Part 5 when an
> incident actually spawns a case.

---

## 3. Part B — clean up the stale deployments (item b)

**Goal:** leave exactly one deployment (`CascadeCare-Full`).

### 3.1 Preview what will be removed (safe — changes nothing)
```bash
bash scripts/cleanup_deployments.sh --dry-run
```
**✅ Expect:** a printed plan listing `CascadeCare-Core`, `-Smoke`, `-Live`, `-Demo` as
"would uninstall", and the line `CascadeCare-Full is never touched`.

### 3.2 Actually remove them
```bash
bash scripts/cleanup_deployments.sh --confirm
```
**⏱ Takes:** ~1–3 min per deployment that actually exists.
**👀 What you'll see:** for each name — `uninstalling ... ✓ uninstalled`, or `absent (skip)` if it
wasn't there (that's fine — the script is safe to re-run).
**✅ Expect:** `Cleanup complete. CascadeCare-Full left intact.`
**❌ If one says `✗ FAILED`:** capture that name + message (Part 6). The others still proceed.

### 3.3 Confirm the end state
```bash
uip solution deploy list --output table
```
**✅ Expect:** only `CascadeCare-Full` remains among the `CascadeCare-*` rows, status active.

---

## 4. Part C — seed the Data Fabric (item c)

**Goal:** load 9 entities (providers, payers, BAAs, claim telemetry, etc.) and 2 search indexes so the
agents read real data.

### 4.1 Preview the data offline (no tenant call — safe)
```bash
bash scripts/seed_data_fabric.sh --emit-json | head -40
```
**✅ Expect:** a big JSON blob starting with `"entities": { "Provider": ...`. This is just a preview so
you can see the shape; it doesn't touch the tenant.

### 4.2 Apply it to the tenant
```bash
UIPATH_LIVE=1 bash scripts/seed_data_fabric.sh --apply
```
**⏱ Takes:** a couple of minutes (it creates each entity, inserts records, then creates 2 indexes).
**👀 What you'll see:** lines like `==> Ensuring entity Provider (6 records)` then the underlying
`$ uip df entities create ...` / `$ uip df records insert ...`, then
`==> Creating Context Grounding index BAA-corpus`, ending with `==> Live seed complete.`
**✅ Expect:** no `error` lines; it finishes with "Live seed complete."
**❌ Most likely snags (capture per Part 6):**
- An entity "already exists" — usually safe to ignore; tell me and I'll make the script skip-if-exists.
- A field-type rejection on `uip df entities create` — the schema mapping may need a tweak; copy the
  exact entity + message.
- `uip context-grounding create` asking for a folder/bucket — copy the prompt; indexes may need a
  `--folder-path Shared` argument I can add.

### 4.3 Confirm in the browser
Open `https://staging.uipath.com/hackathon26_042/` → **Data Service / Data Fabric** → **Entities**.
**✅ Expect:** to see `Provider` (6 rows), `Payer` (4), `BAA` (6), `ClaimTelemetry` (lots), etc.
Then **Context Grounding** (under AI Center / Agents) shows `BAA-corpus` and `ClaimTelemetry-corpus`.

---

## 5. Part D — run the demo and watch it (R1 → R5)

There are two ways to start the master case. **Use Path B (browser) for the actual demo** — it always
works and it's what the camera films. Path A (CLI) is a faster dry-run if you're comfortable.

### Path B — browser (recommended, demo-safe)

1. Open `https://staging.uipath.com/hackathon26_042/`.
2. Top-left **folder picker** → switch to **CascadeCare-Full**.
3. Go to **Maestro → Processes** (or **Orchestrator → Processes**).
4. Find **clearflow-master-crisis** → click **Start / Run**.
5. Inputs: paste `{}` (the master case starts with all defaults). Confirm.
6. **👀 Watch the case canvas open.** You should see the case in its first stage with the goal
   *"Assist isolated customers."* This is **R1**.

Then the **Demo Driver** flow fires the later events on a compressed timer. Watch for:

| Beat | ~When | What you should see on the canvas |
|---|---|---|
| **R1** | t+0s | Master case opens; goal "Assist isolated customers" |
| **R2** | ~t+25s | Goal shifts — ClearFlow cleared, **Nimbus** named as the vector |
| **R3** | ~t+150s | **HERO MOMENT** — 6 child ("grandchild") cases spawn at once in a visible fan |
| **R4** | ~t+200s | Fiduciary conflict → a **human approval task** appears (Action Center) |
| **R5** | ~t+260s | Goal shifts to co-defendant; privilege reshuffles |

**✅ The single most important thing to confirm:** that starting the case (R1) leads to stages
advancing and, at R3, **multiple child cases appear**. That proves the binding fix + nesting work.

**To fire the reversal events** (if they don't auto-run): start the Demo Driver flow —
**Maestro → Flows → clearflow-demo-driver → Run**.

### Path A — CLI (advanced dry-run)

```bash
# 1. find the folder key for CascadeCare-Full
uip orchestrator folders list --output json
#    → find the entry whose name/FullyQualifiedName is CascadeCare-Full; copy its Key (GUID)

# 2. list the case processes in that folder, get the release key
uip maestro case process list --folder-key <FOLDER_GUID_FROM_STEP_1> --output json
#    → find clearflow-master-crisis; copy its release key (GUID)

# 3. launch R1 (note: process-key then folder-key are positional; do NOT add --validate)
uip maestro case process run clearflow-master-crisis <FOLDER_GUID> \
  --release-key <RELEASE_GUID> \
  --inputs @docs/demo/inputs/r1-kickoff.json \
  --output json
```
**✅ Expect:** JSON with a started instance id.
**❌ If step 2 says "Response returned an error code":** the folder key is the Orchestrator folder but
Maestro wants its own folder context. Re-read the folder key from the **deployment's own output**
(Part 2.5) instead of from `folders list`, and confirm the deployment status is `SuccessfulActivate`
(not just `DeploymentSucceeded`). If still stuck — **use Path B**; it bypasses this entirely.

---

## 6. How to capture an error (so I can fix it fast)

When **anything** prints `Failed` / `error` / a number like `1654` / `2005`, copy this template and
fill it in (paste the whole thing back to me):

```
STEP: (e.g. "2.5 deploy run" / "4.2 seed --apply")
COMMAND I RAN:
  <paste the exact command>
WHAT I EXPECTED: <one line, from this guide>
WHAT I GOT (paste the full output, especially any "error"/"status"/code):
  <paste>
TENANT STATE (if relevant): output of `uip solution deploy list --output table`
```

**Quick triage table:**

| You see | Likely meaning | First thing to try |
|---|---|---|
| `Error 1654` "entry points definition invalid" | a project's package metadata shape | copy which project it names; send to me |
| `Error 2005` "entry points configuration missing" | an API workflow missing install metadata | note the `api_workflows/*` name; send to me |
| "Response returned an error code" on `case process list` | Maestro folder-context mismatch | use the deployment's own folder key, or switch to **Path B** |
| "deployment name already in use" | `CascadeCare-Full` still exists | run 2.4 uninstall, then retry 2.5 |
| "unauthorized" / "token expired" | login lapsed | `uip login` again, continue |
| binding/spawn "does nothing" at R1→R3 | the binding fix didn't deploy | confirm Part 2 used the freshly-published version |

**Tip:** add `--log-level debug --log-file /tmp/uip-<step>.log` to any `uip` command to capture a full
log file you can send me, e.g.
`uip solution deploy run ... --log-level debug --log-file /tmp/uip-deploy.log`.

---

## 7. Done checklist

- [ ] `uip solution deploy list` shows **only** `CascadeCare-Full`, active
- [ ] Data Fabric shows the 9 entities populated; 2 Context Grounding indexes exist
- [ ] Starting `clearflow-master-crisis` opens the case (R1)
- [ ] At R3 you see **6 child cases fan out** (the hero moment)
- [ ] R4 produces a human approval task; R5 shifts the goal to co-defendant
- [ ] You recorded the run (screen capture) for the submission video

When all boxes are checked, tell me — that's when the `agenthack-2026-submission` tag gets applied.

> Terse engineer reference (commands only, assumes context): `docs/demo/run-playbook.md`.
> The full why/what behind these steps: `specs/003-uipath-native/slice-019-tasks.md`.
