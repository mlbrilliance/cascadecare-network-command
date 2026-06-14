# CascadeCare — Demo Runbook (run the full 3-level walk again)

How to re-run the CascadeCare Network Command demo end-to-end: the master crisis case
auto-walks five agent stages, spawns the Reversal-3 stakeholder fan, each child walks and
spawns an obligation-grandchild, and two HITL gates (master Reversal-4 + grandchild) pause
for human approval before the case closes with a Slack notification.

There are two paths:

- **Path A — Just run the demo** (solution already deployed; nothing changed). Start here.
- **Path B — Rebuild & redeploy** (you edited a case in Studio Web, or you're deploying to a
  fresh folder/tenant). Do this first, then Path A.

---

## Reference values (staging tenant)

| Thing | Value |
|---|---|
| Tenant | `staging.uipath.com` / `hackathon26_042` / `DefaultTenant` |
| Deployment folder | `Shared/CascadeCare-v110` |
| Folder key | `de7b7c18-d743-4c8c-b555-9bd3b96fe524` |
| Solution id (Studio Web) | `0fc02d30-9645-45b6-4ed8-08dec248fc52` |
| Master process key | `AC365BA5-C807-4DFC-A009-00F3EA61E497` |
| Child process key | `98CE7F31-2A62-40C1-A9E4-053B31908E0F` |
| Grandchild process key | `5C399FE2-C0AB-4CCA-B1E3-0A61D06051FE` |
| Master HITL app | `CascadeCare` (in `Shared/CascadeCare-v110`) |
| Grandchild HITL app | `Regulatory/Contractual Obligation Response` (id `de1f291b-…`) |

> Process keys are **stable across solution upgrades**. They only change on a brand-new
> deployment folder — in that case re-list them (see Path B step 7).

Set a shell variable once per session:

```bash
export FK=de7b7c18-d743-4c8c-b555-9bd3b96fe524
```

---

## Path A — Run the demo (solution already deployed)

### A1. Confirm you're authenticated

```bash
uip --version                      # expect 1.195+ (UiPath switched versioning Jun 2026)
uip login status --output json     # check current org/tenant
uip or processes list --folder-key $FK --output json | grep -c clearflow
```

The CLI access token expires (~58 h refresh window). When it lapses, every read returns
empty/`null` and `processes list` fails with *"Not logged in … refresh token is invalid or
expired."* **Re-authenticate against the staging tenant** (the demo is NOT on the default
`cloud.uipath.com` — you must pass `--authority`):

```bash
uip login --authority https://staging.uipath.com --organization hackathon26_042 --interactive
```

A browser opens against **staging.uipath.com**; log in and approve. When prompted by
`--interactive`, pick **DefaultTenant**. Success looks like:

```json
{ "Result": "Success", "Code": "Authenticated",
  "Data": { "UIPATH_URL": "https://staging.uipath.com",
            "UIPATH_ORGANIZATION_NAME": "hackathon26_042",
            "UIPATH_TENANT_NAME": "DefaultTenant" } }
```

> **Gotchas:**
> - Plain `uip login` defaults to `cloud.uipath.com` (the *wrong* cloud) — always include
>   `--authority https://staging.uipath.com`.
> - If you don't want the tenant picker, swap `--interactive` for `--tenant DefaultTenant`.
> - Running this from the IDE: prefix with `!` so the browser-login output returns in-session
>   (`! uip login --authority … --organization hackathon26_042 --interactive`).

### A2. Start the master crisis case

```bash
uip or jobs start AC365BA5-C807-4DFC-A009-00F3EA61E497 --folder-key $FK --output json
```

This returns a job key in `Pending`. The master begins auto-walking immediately.

> **⭐ This is the only process you kick off manually.** Starting `clearflow-master-crisis`
> cascades to *everything else automatically* — you never start children, grandchildren,
> agents, or workflows by hand (they expect to be spawned with parent context):
>
> | Started automatically by the master | Mechanism |
> |---|---|
> | The 7 agents (coded + low-code) | `type:"agent"` tasks inside the master's stages |
> | ~6 **child** cases (`clearflow-stakeholder-parent`) | the master's `case-management` spawn tasks (Regulatory Response stage) |
> | **grandchild** cases (`clearflow-obligation-grandchild`) | each child's `Spawn Obligation Grandchild` `case-management` task |
> | `register-stakeholder`, `generate-audit-record`, 3× ViVE API workflows | tasks inside the child/grandchild stages |
>
> **Optional — the scripted reversal timeline.** `clearflow-demo-driver` (a Maestro Flow) does
> **not** start the master; it just fires the 5 reversals / scenario events on a timeline into
> a running case. The master walks fine without it. For the full narrative, start it
> *alongside* the master:
>
> ```bash
> # find its process key, then start it (same pattern as the master)
> uip or processes list --folder-key $FK --output json \
>   | python3 -c "import sys,json;print([ (p['Key'],p['Name']) for p in json.load(sys.stdin)['Data'] if p['Name']=='clearflow-demo-driver'])"
> uip or jobs start <demo-driver-key> --folder-key $FK --output json
> ```

### A3. Watch the cascade

The master walks 5 agent stages (~1–4 min depending on LLM Gateway latency), then the
**Regulatory Response** stage spawns the 6-child fan, each child walks and spawns a
grandchild.

Reliable progress signal — count fresh jobs by level:

```bash
uip or jobs list --folder-key $FK --output json \
  | python3 -c "import sys,json;from collections import Counter;d=json.load(sys.stdin)['Data'];\
c=Counter();\
[c.update({(('GRANDCHILD' if 'obligation-grandchild' in (j.get('ProcessName') or '') else 'CHILD' if 'stakeholder-parent' in (j.get('ProcessName') or '') else 'MASTER' if 'master-crisis' in (j.get('ProcessName') or '') else 'x'), j.get('State')):1}) for j in d];\
print({f'{k[0]}:{k[1]}':v for k,v in sorted(c.items()) if k[0]!='x'})"
```

A `GRANDCHILD:*` entry = the full three levels are live. (Before the fix, no grandchild job
ever existed.)

### A4. Approve the two HITL gates in Action Center

The case pauses at two human-approval gates. Open **Action Center → Tasks** in the
`CascadeCare-v110` folder and click **Approve** on each:

1. **Tri-Party Fiduciary Conflict Review** (master, Reversal 4) → drives Stage 6
   (negligent-monitoring) → Stage 7 **Closed** → Slack close-out fires.
2. **Prepare & File Obligation Response** (grandchild) → completes the obligation case.

> These gates *must* be approved by a human — that's the demo's HITL story. There is no CLI
> shortcut (the AppTask completion API is undocumented/SPA-only).

### A5. Confirm closure

> ⚠️ **Do NOT use the Orchestrator Jobs view/API to confirm completion.** On this tenant a
> completed Maestro case instance **never flips its Orchestrator job to Successful** — the
> job row says "Running" forever (proven 2026-06-12: masters whose instances completed 1 and
> 3 days earlier still showed Running jobs). Cancelled instances DO flip to Stopped. The
> source of truth is the **case instance** (Maestro Monitoring UI, or the CLI below).

```bash
# every instance of this run should reach Completed after the gate approvals
# (master after Reversal-4 Approve; grandchildren after their File clicks)
uip maestro case instance list --folder-key $FK \
  | python3 -c "import sys,json;raw=sys.stdin.read();d=json.loads(raw[raw.find('{'):])['Data'];\
print([(x['packageId'].split('.')[-1], x['latestRunStatus'], x['createdTimeUtc'][11:19]) for x in d])"
```

### A6. Pre-judging sweep — clear zombie "Running" job rows

Because of the sync gap above, every completed demo run leaves its case jobs showing
**Running** in the Orchestrator Jobs view forever. Before judges look at the tenant, sweep
them to Stopped. **Rules (proven 2026-06-12):**

- Killing the job shell does NOT touch the case instance — Monitoring keeps showing
  **Completed** (verified on 27 jobs).
- Use the **bulk** form (2+ keys) — it force-stops to **Stopped instantly**. A single-key
  `--strategy Kill` lands in `Terminating` (cleared only by the ~daily platform sweeper);
  `SoftStop` hangs in `Stopping`. To stop ONE job instantly, pass its key twice.
- Only sweep jobs whose instances are terminal (`Completed`/`Cancelled`). NEVER cancel a
  Completed *instance* to clean a job — that flips Monitoring to Cancelled.

```bash
# enumerate zombie Running case jobs, then bulk-stop them
KEYS=$(uip or jobs list --folder-key $FK --state Running --output json \
  | python3 -c "import sys,json;raw=sys.stdin.read();d=json.loads(raw[raw.find('{'):])['Data'];\
print(' '.join(j['Key'] for j in d if 'clearflow' in (j.get('ProcessName') or '')))")
[ -n "$KEYS" ] && uip or jobs stop $KEYS   # bulk = instant Stopped
```

---

## Path B — Rebuild & redeploy from source

Do this when you changed a case in Studio Web, edited a caseplan locally, or are deploying
to a fresh folder. Run from the repo root.

> ✅ **Resolved 2026-06-10 (was DEFERRED-FIXES P1):** the grandchild app `de1f291b` now has
> blocking **File / Withdraw** outcomes, and deployment **1.0.21** binds the gate to it from
> canonical — live and repo agree, and the gate pauses. Path B redeploys are safe for the
> grandchild gate again.

### B1. (Only if you edited cases in the Studio Web canvas) Download + re-merge

The canvas regenerates the compiled `caseplan.json.bpmn` and **drops** the hand-applied
fixes (start events, HITL app wiring, required-task flags). Re-apply them deterministically:

```bash
rm -rf /tmp/dl && uip solution download 0fc02d30-9645-45b6-4ed8-08dec248fc52 -d /tmp/dl --extract
python3 scripts/merge-canvas-download.py /tmp/dl/0fc02d30-9645-45b6-4ed8-08dec248fc52   # master fixes
python3 scripts/merge-child-grandchild.py /tmp/dl/0fc02d30-9645-45b6-4ed8-08dec248fc52  # child + grandchild fixes
```

What the merge scripts restore (so a canvas round-trip never regresses the deploy):
- **master**: mainline start event, HITL `tvlKcFYnW → CascadeCare` app binding, entry-points,
  removal of canvas-added duplicate `error` outputs on the 6 spawns, Slack connection.
- **child**: mainline start event (trigger `468d60f1`) + entry-points, and `isRequired=true`
  on `Spawn Obligation Grandchild` + the 3 ViVE tasks.
- **grandchild**: `Prepare & File Obligation Response` Human-action wired to the
  `Regulatory/Contractual Obligation Response` app.

> If you did **not** touch the canvas, skip B1 — the committed caseplans are already correct.

### B2. Pack the solution from canonical sources

```bash
bash scripts/pack-solution.sh
uip solution pack maestro_case/clearflow-solution dist -n clearflow-solution -v 1.0.19
```

Bump the version (`1.0.19`, `1.0.20`, …) each deploy.

### B3. BAA-clean the package

The packaged zip carries 3 folder-scoped Context-Grounding resources that the live folder
already provisioned — an upgrade-deploy must **not** try to re-create them. Drop them and
revert the BAA agent's runtime dependency (there is no `unzip` in WSL, so use Python):

```bash
python3 - <<'PY'
import zipfile
V='1.0.19'
SRC=f'dist/clearflow-solution_{V}.zip'; OUT=f'dist/clearflow-solution_{V}_clean.zip'
DROP={'resources/Shared/index/BAA-corpus.json',
 'resources/solution_folder/bucket/orchestratorBucket/baa-corpus-docs.json',
 'resources/solution_folder/index/BAA-corpus_1.json'}
SUB='resources/solution_folder/process/agent/BAABoundaryReasoner.json'
clean=zipfile.ZipFile('dist/clearflow-solution_1.0.8.zip').read(SUB)  # known-clean runtimeDependencies:[]
zin=zipfile.ZipFile(SRC)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as zo:
    for it in zin.infolist():
        if it.filename in DROP: continue
        zo.writestr(it, clean if it.filename==SUB else zin.read(it.filename))
zc=zipfile.ZipFile(OUT)
assert not [n for n in zc.namelist() if 'baa-corpus' in n.lower()], 'BAA leftover!'
print('clean zip OK:', len(zc.namelist()), 'entries ->', OUT)
PY
```

### B4. Publish

```bash
uip solution publish dist/clearflow-solution_1.0.19_clean.zip --wait --output json
# expect State: Ready
```

### B5. Deploy (upgrade in place)

```bash
uip solution deploy run \
  --name CascadeCare-v110 --folder-name CascadeCare-v110 --parent-folder-path Shared \
  --package-name clearflow-solution --package-version 1.0.19 --timeout 600 --output json
# expect Status: DeploymentSucceeded | ActivationStatus: SuccessfulActivate
```

### B6. Re-rename the 6 low-code agents PascalCase → kebab

The upgrade resets agent process names to their PascalCase project names; the case bindings
resolve by the **kebab** name. Re-rename (looks them up by name, so it's deploy-agnostic):

```bash
uip or processes list --folder-key $FK --output json \
| python3 -c "
import sys,json
d=json.load(sys.stdin)['Data']
M={'AssessClaimDisruptionAgent':'assess-claim-disruption','ClassifyObligationAgent':'classify-obligation',
   'NegligentMonitoringRiskAgent':'negligent-monitoring-risk-agent','BAABoundaryReasoner':'baa-boundary-reasoner',
   'VectorHypothesisAgent':'vector-hypothesis-agent','FiduciaryConflictDetector':'fiduciary-conflict-detector'}
for it in d:
    if it.get('Name') in M: print(it['Key'], M[it['Name']])
" | while read key name; do
    uip or processes edit "$key" -n "$name" --output json | grep -o '"Result":"[^"]*"'
    echo "  -> $name"
  done
```

Verify none remain PascalCase (except `ClearFlowIdealIncidentResponse`, the BPMN playbook,
which is intentionally left alone):

```bash
uip or processes list --folder-key $FK --output json \
  | python3 -c "import sys,json;print([j['Name'] for j in json.load(sys.stdin)['Data'] if any(c.isupper() for c in j['Name']) and j['Name']!='ClearFlowIdealIncidentResponse'] or 'all kebab ✓')"
```

### B6.5 Context Grounding corpora (live since 2026-06-12)

Both indexes live in `Shared/CascadeCare-v110` and are populated from committed,
seed-derived docs:

| Index | Bucket | Docs |
|---|---|---|
| `BAA-corpus` (key `bc3b9560…`) | `baa-corpus-docs` | `data/context-grounding/baa-corpus/*.txt` (6 BAAs) |
| `ClaimTelemetry-corpus` | `claimtelemetry-corpus-docs` | `data/context-grounding/claimtelemetry-corpus/*.txt` (6 providers) |

Regenerate + re-upload after any seed-table change (`python3 scripts/gen_cg_corpus.py`,
gate test `tests/unit/scripts/test_gen_cg_corpus.py`):

```bash
# the context-grounding tool uses the PYTHON SDK's auth — bridge the uip session token:
TOKEN=$(uip login refresh --output json | python3 -c "import sys,json;raw=sys.stdin.read();print(json.loads(raw[raw.find('{'):])['Data']['AccessToken'])")
export UIPATH_URL="https://staging.uipath.com/hackathon26_042/DefaultTenant" UIPATH_ACCESS_TOKEN="$TOKEN"
uv run python - <<'PY'
from pathlib import Path
from uipath.platform import UiPath
sdk = UiPath(); FP = 'Shared/CascadeCare-v110'
for bucket, src, index in (("baa-corpus-docs", "data/context-grounding/baa-corpus", "BAA-corpus"),
        ("claimtelemetry-corpus-docs", "data/context-grounding/claimtelemetry-corpus", "ClaimTelemetry-corpus")):
    for p in sorted(Path(src).glob("*.txt")):
        sdk.buckets.upload(name=bucket, blob_file_path=p.name, content=p.read_text(),
                           content_type="text/plain", folder_path=FP)
    sdk.context_grounding.ingest_data(sdk.context_grounding.retrieve(index, folder_path=FP), folder_path=FP)
PY
# poll retrieve() until lastIngestionStatus == Successful, then smoke-search
```

> **Gotchas (live-proven 2026-06-12):** docs must be **.txt** — CG extraction silently skips
> `.md` (ingestion says Successful, search returns 0). The bucket previously held 6
> contradictory legacy `baa_txt_*.txt` drafts (e.g. 5-business-day notification vs the seeded
> 24h) — deleted; never let bucket docs disagree with the seeded Data Fabric terms.

### B7. (Fresh folder only) Re-publish the two Action Center apps + Slack connection

The HITL apps and the Slack connection are **folder-scoped**. If you deployed to a *new*
`CascadeCare-vXXX` folder, you must also, in Studio Web:

- Publish the `CascadeCare` app into that folder.
- Publish the `Regulatory/Contractual Obligation Response` app into that folder.
- Re-create the `webfiji` Slack connection in that folder.
- Re-list the process keys (`uip or processes list --folder-key <new>`) and update this
  runbook's reference table.

Otherwise the HITL gates fault with `170015 "No app found in folder"`.

Now run **Path A**.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Case stalls at the first "anomaly detection" stage for many minutes | The **coded** agents (claim-flow / multi-customer) cold-start or the LLM Gateway is slow | Environmental — wait, or cancel + restart the master. Not a definition defect. |
| `uip ... list` / `get` returns empty or `null` repeatedly | Staging tenant read-API degradation | Retry later; cross-check via **Action Center** (gate render/approve) — the reliable ground truth. |
| Child spawns but sits `Running` with no progress | Missing mainline start event in the child caseplan | Re-run `scripts/merge-child-grandchild.py` (B1) and redeploy. |
| Grandchild never spawns | `Spawn Obligation Grandchild` not `isRequired` | Same — the merge script flips it; redeploy. |
| HITL gate faults `170015 "No app found"` | App not deployed in the case's folder, or empty `=bindings.` in the compiled `.bpmn` | Re-publish the app into the folder (B7); re-run the merge script. |
| Agent task can't resolve at runtime | Agent left PascalCase after upgrade | Re-run B6. |
| `publish` fails `400 duplicate Resource key` | Packed the *downloaded* solution directly | Always pack the canonical `maestro_case/clearflow-solution` (B2), never the download. |

### Clean up stale instances (optional, before a clean demo)

Old runs leave child/grandchild instances parked at HITL gates or `caseEndMessageCatchEvent`
(they show `Running` but are effectively done). They don't block new runs, but to tidy:

```bash
bash scripts/cleanup_deployments.sh        # or cancel individually:
# uip maestro case instance cancel <instanceId> --folder-key $FK
```

---

## What "success" looks like

1. `master-crisis` job goes `Pending → Running`.
2. Within a few minutes, 6 (×2 due to a benign platform dup) `stakeholder-parent` jobs appear
   and **walk** (not stuck).
3. `obligation-grandchild` jobs appear — **three levels live**.
4. Two Action Center tasks render: *Tri-Party Fiduciary Conflict Review* and *Prepare & File
   Obligation Response*. Approve both — all four display fields (Payer Demand, Affected Provider
   BAAs, ClearFlow Obligations, Conflict Analysis) should now be populated.
5. Master reaches **Completed**; the Slack close-out notification fires.

---

## Judge Q&A — Production Trigger Architecture

> *"This is a demo. How would CascadeCare detect a real crisis without someone manually kicking
> it off?"*

**The short answer:** In production, `clearflow-master-crisis` is never started manually. The
`ClearFlowIdealIncidentResponse` BPMN — already live on the tenant — is the event-driven entry
point. Its `Start: Incident Intake` node binds to an Integration Service webhook trigger (SIEM
alert, EDI monitoring feed, or claim-queue watchdog). Swapping the 14 mock API workflows for live
EDI connector endpoints is the only production-readiness delta.

**The signal chain:**

```
Provider goes dark
  ↓
EDI 837 claim submissions stop → provider API workflow detects silence
  ↓
claim-flow-anomaly-detector (scheduled every 15 min via Orchestrator time trigger)
  outputs: claim_drop_pct=94%, anomaly_score=0.97, severity="critical"
  ↓
multi-customer-pattern-detector correlates across all providers
  conclusion: same fingerprint on 3+ providers → cascade confirmed
  ↓
Integration Service event fires → ClearFlowIdealIncidentResponse BPMN
  Triage task → is_cascade? gateway → Spawn clearflow-master-crisis
  ↓
Master crisis case live. Reversal 1 begins. Zero human intervention.
```

**Why two independent agents before escalation:**
`claim-flow-anomaly-detector` scores a single provider's telemetry. `multi-customer-pattern-detector`
correlates across all providers simultaneously. Both must fire before the BPMN's `is_cascade?`
gateway routes to case creation — preventing false positives from a single-provider outage
triggering a full multi-stakeholder crisis response.

**Time-to-detect vs. historical reality:**
The real CH/Change Healthcare-class incident went undetected at scale for days. CascadeCare's
polling interval is 15 minutes. First-responder organizations took hours to activate. CascadeCare
spawns the master case within seconds of cascade confirmation.

**"Why not just kick off the claim-flow-anomaly-detector directly instead of the master crisis case?"**

In production you DO kick off the anomaly detector — it runs on an Orchestrator time trigger every
15 minutes. They are **sequential steps, not alternatives**:

```
claim-flow-anomaly-detector fires (Layer 1 — Detection)
  → BPMN catches event, confirms cascade (Layer 1 → 2 handoff)
  → master crisis case spawns (Layer 2 — Orchestration)
  → Medical Records / Claim Denial / Prior Auth invoked per-stakeholder (Layer 3 — Execution)
```

A Python function scores telemetry, returns a severity score, and exits. It holds no state. After
it fires — who coordinates 6 providers over 90 days? Who manages the BAA compliance, the DOI
subpoena, the payer fiduciary conflict, the insurer freeze directive, the SLA escalations, and
the two HITL gates? That is Maestro Case.

**"Why not just run the Healthcare Agents (Medical Records, Claim Denial, Prior Auth) directly?"**

Those agents each handle one clinical job for one provider. Without the orchestration layer: 3
agents × 6 providers = 18 manual invocations with no shared state, no SLA tracking, no legal
layer (BAA / subpoena / fiduciary conflict), and no case record. CascadeCare tells those agents
when to run, for which provider, under which legal constraints, in what order.

**One-liner for the judges:**
> *"The anomaly detector is the smoke alarm. The BPMN is the 911 call. The master crisis case is
> the incident command. The healthcare agents are the specialists on scene. You need all four —
> and CascadeCare is what makes them work together instead of independently."*

**"The scenario we're demonstrating — a payment network going dark across multiple providers — is
exactly what the Change Healthcare incident looked like in the first 72 hours. CascadeCare shows
how an AI-driven Maestro Case, triggered automatically by anomaly detection, would manage that
in real time rather than through manual war-room coordination."**

**Governance from first call:**
All LLM calls flow through the UiPath LLM Gateway → Trust Layer (PHI/PII detection + content
filtering) from the very first agent invocation in the BPMN triage task. No raw provider data
ever leaves the UiPath governance boundary.

---

## HITL Gate Branch Reference

### Gate 1 — Tri-Party Fiduciary Conflict Review (master crisis R4, Stage `Stage_LKuLeU`, task `tvlKcFYnW`)

Pre-populated fields (read-only, surfaced by Fiduciary Conflict Detector agent):
- **Payer Demand** — Apex Health Plan's operational-visibility clause demand
- **Affected Provider BAAs** — Northstar + Provider Alpha BAA confidentiality terms
- **ClearFlow Obligations** — BAA trustee obligations + Aurora insurer freeze directive
- **Conflict Analysis** — Three-way collision summary from the agent

Human fills in: Reviewer ID, Decision, Context narrative, Timestamp.

| Choice | Output var `reviewerDecision` | Downstream effect |
|---|---|---|
| **Approve** | `"approved"` | R5 frames ClearFlow as cooperative. Weaker BAA protection, lower adversarial friction with Apex. Disclosure risk if providers challenge. |
| **Deny** | `"denied"` | R5 frames ClearFlow as contesting payer demand. Stronger HIPAA/BAA compliance posture. Higher adversarial risk with Apex. |

Either choice: master crisis advances to R5 (co-defendant stage). The `reviewerDecision` variable
is read by R5 agent tasks to adapt their posture analysis.

### Gate 2 — Prepare & File Obligation Response (grandchild R2, Stage `Stage_F95sBP`, task `t9BUmAX8k`)

Pre-populated fields (read-only, set at grandchild spawn time):
- **Obligation Type** — e.g. `baa-compliance`, `regulatory-response`, `litigation-hold`
- **Jurisdiction** — TN-DOI / Federal HIPAA 45 CFR 164
- **BAA Reference** — subpoena reference ID from the DOI filing

Human fills in: Reviewer ID, Response Disposition (filed/withdrawn), Response Narrative, Filed Timestamp.

| Choice | Output var `responseDisposition` | Downstream effect |
|---|---|---|
| **File** | `"filed"` | `Generate Audit Record` task logs `disposition=filed`. Grandchild closes with full compliance record. No escalation. |
| **Withdraw** | `"withdrawn"` | Audit record logs `disposition=withdrawn` — permanent compliance gap. Grandchild closes but flags an unresolved obligation. In production triggers SLA breach escalation + stakeholder-parent notification. |

### Why cases keep running while HITL gates are open

Nested cases are independent by design. Master crisis advances through reversals while grandchildren
handle obligations in parallel — identical to how a real incident command operates. The demo
compresses 90 days to minutes; the architecture is unchanged.

**If a judge challenges this:** "HITL gates pause only the specific case that needs human input.
The master crisis R4 gate and the 18 grandchild gates are all open simultaneously — each waiting
independently. This is correct behavior. In production, Day 45 (R4) events happen regardless of
whether individual Day 30 (R3) obligation filings are complete."
