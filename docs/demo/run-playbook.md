# CascadeCare — Live Run Playbook (R1→R5)

> ⚠️ **SUPERSEDED (2026-06-12).** This playbook describes the Slice-015 era
> (`CascadeCare-Core`, v0.1.0 coded agents, Error-2005 recovery). All of those
> blockers are resolved and the deployment moved on. For the current live run
> procedure (auth, deploy recipe, A5 closure check, A6 zombie sweep) see
> [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md) — current deployment:
> `clearflow-solution` 1.0.23 on `Shared/CascadeCare-v110`. The body below is
> kept only as a historical record.

How to launch the ClearFlow master crisis case on the tenant for a demo dry run,
and how to recover when the Maestro folder/release-key context can't be resolved
from the CLI. Written for Slice 015 Phase 2 (T018).

> **Status:** the master case (`clearflow-master-crisis`) + 4 Agent Builder agents
> are deployed and activated to the Orchestrator folder `CascadeCare-Core`
> (DeploymentSucceeded / SuccessfulActivate, Slice 014). The 3 Coded Agents are in
> the tenant feed @ v0.1.0. The 14 API workflows now carry the install metadata
> that cleared Error 2005 offline (Slice 015 T016/T017) but their live re-add +
> install-confirm is still pending a tenant session.

---

## Path A — CLI trigger (preferred)

The blocker recorded in Slice 014 was that `uip maestro case process list -f <key>`
rejected the folder keys returned by `uip or folders` ("Response returned an error
code"). Maestro Case runs in a **Maestro-specific folder context** that is not
always the same GUID surface as the Orchestrator folder. Resolve it in this order:

```bash
# 0. Authenticate
uip login

# 1. Find where the solution actually deployed — note the *folder path*.
uip solution deploy list --output json
#    → locate the CascadeCare-Core deployment; read its folder path + status.

# 2. Resolve that folder PATH to its folder KEY (GUID).
uip orchestrator folders list --output json
#    → match on FullyQualifiedName == "CascadeCare-Core" (or the path from step 1);
#      take its Key (GUID).

# 3. List the Case processes IN that folder. If step 2's key is rejected, the
#    Maestro folder context differs — try the folder key of the *Modern* folder
#    that hosts the Maestro process, and any child folder created by deploy.
uip maestro case process list --folder-key <FOLDER_GUID> --output json
#    → take the release-key (GUID) of clearflow-master-crisis.

# 4. Launch R1. The master case declares no required start inputs (all root
#    variables carry defaults), so the kickoff payload is empty `{}`.
uip maestro case process run \
  --release-key <RELEASE_GUID> \
  --inputs @docs/demo/inputs/r1-kickoff.json \
  --validate --output json
```

**If step 3 still returns "Response returned an error code":** the release/folder
pairing is wrong, not the auth. Re-derive the folder key from the deployment's own
output (step 1) rather than from `orchestrator folders list`, and confirm the
deployment is **activated** (`uip solution deploy list` status `SuccessfulActivate`,
not just `DeploymentSucceeded`). An inactive deployment exposes no runnable release.

---

## Path B — Maestro UI trigger (fallback)

When the CLI folder/release context can't be resolved in time, trigger from the
browser — this always works and is demo-safe:

1. Open the Designer URL for the deployed solution:
   `https://staging.uipath.com/hackathon26_042/studio_/designer/8ca3e38b-cdb3-45dc-87e7-041f5f3480c8?solutionId=167dda12-98eb-47d9-f741-08debdbdd466`
2. Switch to the **CascadeCare-Core** folder (top-left folder picker).
3. Open **Maestro → Processes**, select **clearflow-master-crisis**.
4. Click **Start / Run**, paste the R1 inputs (same JSON as Path A step 4), confirm.
5. Watch the case canvas — the stage transitions and the Reversal-3 grandchild fan
   render live here (this is the on-camera surface).

The Maestro Flow **Demo Driver** (`maestro_flow/clearflow-demo-driver`) fires the
downstream reversal events at compressed intervals once the master case is live.

---

## Reversal cue sheet (for narration)

| # | t+ (wall clock) | Trigger | What the camera shows |
|---|---|---|---|
| R1 | 0s | Case start (Path A/B) | Master case opens; "Assist isolated customers" goal |
| R2 | ~25s | Demo Driver event | ClearFlow cleared; Nimbus identified as vector |
| R3 | ~150s | TN DOI subpoena | **Hero fan** — 6 grandchild cases spawn simultaneously |
| R4 | ~45s sim (≈t+200s) | Payer-demand event | Fiduciary Conflict Detector → tri-party HITL gate |
| R5 | ~90d sim (≈t+260s) | Litigation event | Bystander → co-defendant; privilege reshuffle |

---

## Open items (carried forward — tenant session)

- **API workflows live install-confirm**: re-add the 14 `api_workflows/*` (now with
  `entry-points.json` + `bindings_v2.json`) to the solution and confirm Orchestrator
  install no longer raises Error 2005. Offline pack already proves all
  descriptor-declared files are present.
- **BPMN Error 1654**: the `.bpmn` is offline-valid and its `entry-points.json`
  matches the maestro-bpmn skill canon (id ↔ `uipath:entryPointId`, correct
  `filePath`). Error 1654 needs a live install to reproduce/diagnose.
- **Coded App**: blocked on a tenant-registered OAuth External Application (human).
