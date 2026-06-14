# CascadeCare Demo-Ready Handoff — 2026-06-14

Next-agent briefing for the final demo prep sprint before the June 29 AgentHack 2026 deadline.

---

## Project Snapshot

**What it is**: CascadeCare Network Command — a UiPath Maestro Case demo for AgentHack 2026
Track 1. A multi-stakeholder healthcare-payment cyber crisis as one evolving case with
three-level nesting (master → 6 stakeholder-parents → 6 obligation-grandchildren), driven by
five master-level reversals across a 90-day simulated timeline. Protagonist: ClearFlow Health
Network (fictional payment intermediary).

**Live tenant**: `staging.uipath.com/hackathon26_042/DefaultTenant`
**Solution folder**: `Shared/CascadeCare-v110` (folder key `de7b7c18-d743-4c8c-b555-9bd3b96fe524`)
**Repo**: `https://github.com/mlbrilliance/cascadecare-network-command`
**Branch**: `master` (all session work merged here as of 2026-06-14)
**Deadline**: June 29 2026, 11:45 PM EDT. Rolling judging opens June 3.

---

## What Was Accomplished This Session

### 1. `scripts/demo_autocomplete.py` (NEW — committed `ef3c01d`)
Script to auto-complete excess Action Center tasks before going live, leaving exactly
4 tasks for the presenter (2 Fiduciary + 2 Obligation Response).

- Classification by title substring: "Fiduciary" vs "Obligation Response"
- `partition_tasks(tasks, keep=2)` — keeps last 2 per bucket, auto-completes the rest
- Alternating decisions: `auto_fiduciary_decision(i)` → Approve/Deny; `auto_obligation_disposition(i)` → filed/withdrawn
- Realistic payload builders: `build_fiduciary_payload`, `build_obligation_payload`

**Status: Script logic is correct but BROKEN in practice** — see known issues below.

### 2. `tests/unit/scripts/test_demo_autocomplete.py` (NEW — 18 tests, all pass)
Full unit test suite for the autocomplete script. All 18 pass (`uv run pytest`).

### 3. `docs/demo/PRESENTATION-SCRIPT.md` updated (commit `f0e1ecf`)
Scene 3 opening line now explicitly uses the 17-task queue as a scale visual:
> "ClearFlow is currently holding 17 simultaneous compliance decisions — two payer fiduciary
> conflicts and fifteen obligation responses — all waiting for human review. I'm going to
> action four of them live."

---

## Critical Open Issues (Highest Priority for Next Agent)

### ❌ ISSUE 1: Action Center fields are EMPTY (highest priority)

**Symptom**: Both HITL gate apps show blank fields when opened in Action Center:
- **Fiduciary App (CascadeCare)**: PayerDemand, AffectedProviderBAAs, ClearFlowObligations,
  ConflictAnalysis — all blank
- **Obligation Response App**: ObligationType, Jurisdiction, BAAReference — all blank

**Root cause (definitively confirmed)**: `Actions.HITL` v2 activity only processes 8 registered
input parameters (`name`, `folderPath`, `_label`, `taskTitle`, `priority`, `labels`,
`actionCatalogName`, `recipient`). Custom named inputs like `PayerDemand` are silently ignored.
Three caseplan/BPMN fix attempts (v1.0.25, v1.0.26, v1.0.27) all failed because the fix must
be in the App definition, not the caseplan.

**Fix required (user action in UiPath Apps Studio browser UI)**:

Open each app in Apps Studio and replace `=ActionProperties.*` bindings with static text:

**App 1 — CascadeCare (Fiduciary gate)**:
| Field | Hardcoded static text |
|---|---|
| Payer Demand | `Apex Health Plan invokes the operational-visibility clause in Schedule D of the ClearFlow-Apex Master Network Agreement, demanding direct access to provider claim records within 72 hours or it will withhold remittances.` |
| Affected Provider BAAs | `Northstar Regional Health BAA §4.2: prohibits redisclosure of claim-level PHI to payers outside treatment-payment-operations chain. Provider Alpha BAA §3.1: bars disclosure without separate BAA. Both BAAs obligate ClearFlow to reject third-party PHI access demands.` |
| Clear Flow Obligations | `ClearFlow is bound by provider BAAs to act as faithful business associate and disclose claim PHI only as those agreements permit. Aurora Specialty insurer freeze directive also bars data sharing pending forensic review.` |
| Conflict Analysis | `CONFLICT DETECTED — Three-way obligation collision: (1) Apex contractual demand for PHI access vs. provider BAA confidentiality terms, (2) provider BAA redisclosure bar vs. payer operational-visibility clause, (3) insurer freeze directive vs. Apex 72-hour ultimatum. Complying with Apex violates at minimum two BAAs and the Aurora directive.` |

**App 2 — Regulatory/Contractual Obligation Response**:
| Field | Hardcoded static text |
|---|---|
| Obligation Type | `baa-compliance` |
| Jurisdiction | `TN-DOI (Tennessee Department of Insurance) — Federal HIPAA 45 CFR 164 also applies` |
| BAA Reference | `TN-DOI-SUBP-2024-0312` |

After saving + publishing each app, ALL future runs will show populated fields immediately.
No caseplan/BPMN/deployment changes needed.

---

### ✅ ISSUE 2 (RESOLVED 2026-06-14): autocomplete works via the `uip tasks` CLI

**The earlier "impossible via API" conclusion was WRONG on two counts** — proven live this session:

1. **Listing works.** `uip tasks list --as-admin` (normal `uip login` user token) returned all
   143 AppTasks (126 Completed, 17 Pending). The "returns 0" was specific to the *client-credentials*
   OAuth app the old script used — client credentials only see their own tasks. Not a platform limit.
2. **Completion works via the right endpoint.** The 405s came from hitting the *generic*
   `Tasks(id)/...OData.Complete` action and the `forms/AppTasks/SaveAndCompleteAppTasks` form
   endpoint by hand. The correct route for AppTasks is `POST /tasks/AppTasks/CompleteAppTask`,
   which `uip tasks complete <id> --type AppTask --folder-id <fid> --action <outcome> --data '{...}'`
   uses. Completion attempts no longer 405 — they reach the real endpoint.
3. **No coded agent needed.** A deployed on-platform agent would be *worse* for the pre-demo use
   case (it runs on a schedule and could clear the tasks you want to keep). Dropped.

**`scripts/demo_autocomplete.py` was rewritten** this session to drive the CLI:
- `uip tasks list --as-admin` → filter Pending AppTasks → 2+2 partition → **`uip tasks assign`
  (REQUIRED) → `uip tasks complete`**. An unassigned task fails "This action is no longer
  assigned to you", so the script assigns each task to `DEMO_ASSIGNEE` first.
- **Set `DEMO_ASSIGNEE=<your Action-Center login email>` for a real run** (no default). `--dry-run`
  needs no assignee.
- Orphan-aware: completion returning "This action has been already deleted" is reported, not fatal.
- 36 unit tests pass; mypy clean. Verified live end-to-end: a fresh grandchild obligation task was
  assigned + completed → `Completed`; the orphan path was exercised against the dead queue.
- Outcomes verified live: **Fiduciary = Approve/Deny**; **Obligation accepts any action string**
  (no fixed outcomes), so the File/Withdraw defaults complete cleanly.

**⚠ DEMO LANDMINE — the current 17 Action Center tasks are ORPHANED (dead).** Every one returns
"This action has been already deleted": their backing Maestro case instances were stopped (manual
`jobs stop` or the hourly case-job-janitor sweep). They CANNOT be completed AND cannot be actioned
live on stage (Action Center "Approve" click fails too). **The "show 17 tasks as scale, action 4
live" plan in PRESENTATION-SCRIPT.md Scene 3 will FAIL with these tasks.** Required: start a FRESH
master run, then action the kept tasks live *before* stopping any jobs and within 24 h (janitor
threshold).

---

### ✅ ISSUE 3 (RESOLVED 2026-06-14): the extra Fiduciary tasks are accumulation, not a bug

**Symptom**: ~6 Fiduciary tasks instead of 1.

**The "Fiduciary HITL stage inside the stakeholder loop" hypothesis was WRONG.** The caseplans
prove it: `clearflow-master-crisis/caseplan.json` has exactly ONE `action`-type task (the Fiduciary
gate `tvlKcFYnW`), in a single `Fiduciary Review` stage, NOT inside any loop. "Fiduciary" appears in
zero stakeholder/grandchild caseplans. The Obligation Response gate is the grandchild's single
`action` task.

**Actual cause**: one Fiduciary task fires per master *instance*. The 17 live tasks (6 Fiduciary +
11 Obligation) are **accumulated across ~6 past master runs** that were never cleared — because
nobody could complete them (Issue 2). Clear them and re-run once → 1 Fiduciary + N obligation from
that single run. No `.bpmn`/caseplan change needed; the mitigation is clearing stale tasks between
rehearsals (now possible via the rewritten autocomplete script).

---

## Demo Flow (for next agent to validate)

```
0. The 17 tasks currently in Action Center are ORPHANED (dead). They cannot be actioned.
   Start FRESH — do NOT demo against the existing queue.

1. Start master crisis run(s):
   uip maestro case process run AC365BA5-C807-4DFC-A009-00F3EA61E497 de7b7c18-d743-4c8c-b555-9bd3b96fe524
   For BOTH Approve AND Deny live (2 Fiduciary tasks): trigger TWICE.

2. Wait ~2 min for grandchild obligation cases + Action Center tasks to appear

3. Pace the queue, leaving 2 Fiduciary + 2 Obligation for the stage:
   uv run python scripts/demo_autocomplete.py --dry-run   # preview
   uv run python scripts/demo_autocomplete.py             # complete the excess
   (open Action Center to show the queue as a scale visual if desired)

4. Complete 4 tasks live — BEFORE stopping any jobs, within 24 h (janitor sweep window):
   - 1 Fiduciary → Approve
   - 1 Fiduciary → Deny
   - 1 Obligation Response → File
   - 1 Obligation Response → Withdraw

5. Case advances on canvas — show branches closing
```

⚠ Never `jobs stop` / let the janitor sweep while tasks are pending — it orphans them
(the action is deleted; the task becomes uncompletable). Action the kept tasks first.

---

## File Map

| Path | Purpose | Status |
|---|---|---|
| `scripts/demo_autocomplete.py` | Demo pacing script (CLI-driven; lists+completes via `uip tasks`) | Rewritten 2026-06-14, uncommitted |
| `tests/unit/scripts/test_demo_autocomplete.py` | 33 unit tests (all pass) | Updated 2026-06-14, uncommitted |
| `docs/demo/PRESENTATION-SCRIPT.md` | Full scene-by-scene + judge Q&A | Updated `f0e1ecf` |
| `docs/demo/DEMO-RUNBOOK.md` | Step-by-step run ops | Prior session |
| `maestro_case/clearflow-master-crisis/caseplan.json.bpmn` | Master crisis compiled BPMN | v1.0.27 (ineffective custom inputs) |
| `maestro_case/clearflow-obligation-grandchild/caseplan.json.bpmn` | Grandchild compiled BPMN | v1.0.27 (ineffective custom inputs) |
| `apps/` | UiPath Apps (CascadeCare + Obligation Response) | NOT updated yet — needs Studio fix |

---

## What NOT to Change

- **`.bpmn` files**: Three failed attempts already. The fix is in Apps Studio, not the BPMN.
- **`knowledge/`**: Immutable — pre-write hook blocks edits.
- **`tasks.md` (root)**: Only touch via `/speckit` commands.
- **IP safety**: Forbidden tokens (commit blocked): `zelis, aetna, cigna, unitedhealth, bcbs,
  hartley, rivet, zipp, zapp, change healthcare, optum, cotiviti, wex`

---

## Deployment Commands (for reference)

```bash
# Pack + publish + deploy coded web app
uip codedapp pack dist -n clearflow-network-command -v <ver> --content-type webapp
uip codedapp publish  -n clearflow-network-command -v <ver> -t Web
uip codedapp deploy   -n clearflow-network-command --folder-key de7b7c18-d743-4c8c-b555-9bd3b96fe524
# WARNING: bare deploy only — -v/--path-name hangs on "still being indexed" forever

# Start a case run
uip maestro case process run AC365BA5-C807-4DFC-A009-00F3EA61E497 de7b7c18-d743-4c8c-b555-9bd3b96fe524

# Push to GitHub (HTTPS with token — SSH not available in WSL)
git push https://<username>:<token>@github.com/mlbrilliance/cascadecare-network-command.git <branch>:master
```

---

## Suggested Skills

- `/speckit.implement` — for building the robot-based autocomplete coded agent (if wanted)
- `/thermo-nuclear-code-quality-review` + `/improve-codebase-architecture` — mandatory quality
  loop before any new slice commit
- `/handoff` — at end of next session

---

## Memory References

Full cross-session memory index: `/home/webfiji/.claude/projects/-mnt-c-Users-linki-OneDrive-Desktop-cascade-command/memory/MEMORY.md`

Key entries relevant to next session:
- `codedapp-deploy-indexing-gotcha.md` — deploy command gotcha (bare deploy only)
- `caseplan-bpmn-compile-gotcha.md` — why BPMN edits need Studio Web canvas regen
- `run-1024-complete.md` — last fully-proven clean run state
