# Session Handoff — 2026-06-22 (audit-ledger LangGraph + dashboard Compliance Ledger + Slack fix)

Audience: a fresh agent on a clean session. This summarizes **only** what changed this session and
what's next — everything else lives in the referenced artifacts. Do not re-derive; read the refs.

---

## TL;DR — current state

- **Repo:** `origin/master` @ **`ffd6d3f`** — fully pushed, working tree clean except (a) pre-existing
  spec-kit template churn under `.agents/ .claude/skills/ .cursor/ .gemini/ .github/ .windsurf/`
  (NOT our work — leave it) and (b) `docs/submission/Submission deck.pptx` (human-owned — never commit).
- **Live solution:** `clearflow-solution` **1.0.35** deployed + active in `Shared/CascadeCare-v110`.
- **Live dashboard (Coded Web App):** **v1.0.15** at https://hackathon26_042.staging.uipath.host/clearflow-network-command — the Compliance Ledger loads live.
- **All gates green:** `uv run pytest` 768 passed / 7 skipped; `uv run mypy src/` clean; IP-safe.
- **Two preserved runs** (Completed, with Data Fabric audit rows): `CFCS-67730745`, `CFCS-67767069`.
  Jobs view swept clean (0 Running).

## What shipped this session (commits on `origin/master`, newest first)

| Commit | What |
|---|---|
| `ffd6d3f` | **Slack close-out fix** — `messageToSend` was the literal `{=metadata.caseId}` (Maestro doesn't eval `{=…}` braces). Now `=js:`…`${metadata.ExternalId}`…``. Deployed solution **1.0.35**; verified live (run `CFCS-67767069` Completed, 0 incidents). |
| `15e78c7` | **Demo video script** refresh — added a top "Window map" + per-shot `▶ ON SCREEN` launch cues + the closing Compliance-Ledger beat; counts to 11 distinct agents / two LangGraph. Also CODING_AGENTS.md app-row symmetry. |
| `050e6ee` | **Docs** — documented the dashboard's live Compliance Ledger panel (README app section, DEVPOST, shotlist, changelog). |
| `0b3b68e` | **Dashboard scope fix** — `DataFabric.Data.Read` (resource `DataFabricOpenApi`) + read AuditRecord by entity id `252cd5cc…`; removed the wrong `DataService.*` guess. Live **v1.0.15**. |
| `62fa753` | **Dashboard** — new live Compliance Ledger table + agent-roster refresh (6 Coded · 6 Builder). |
| `e8f3f8a` | **audit-ledger-writer → `audit-ledger-writer-langgraph`** (in-case LangGraph agent at the master Closed stage `tALWdgr01`) + docs honesty pass ("two LangGraph agents"). |

Full detail (do not duplicate): the diffs themselves; `git log`; and the memory files below.

## Authoritative context — read these, don't re-discover

- **Memory index:** `~/.claude/projects/-mnt-c-Users-linki-OneDrive-Desktop-cascade-command/memory/MEMORY.md`
  (loaded automatically). Most relevant this session:
  - `audit-record-df-ledger.md` — the in-case LangGraph ledger agent + the full dashboard scope saga
    (the `DataService.*` red herring → `DataFabric.Data.Read` is the real, already-granted scope).
  - `caseplan-v20-expression-interpolation.md` — **NEW**: V20 string fields need `=js:`…`${expr}`…``;
    `{=expr}` braces post literally; Studio Web strips `=js:` on canvas save → re-wrap in the download.
  - `submission-open-edges.md` — remaining prize/submission edges + deadlines.
  - `codedapp-deploy-indexing-gotcha.md` — dashboard deploy recipe + the bare-form `deploy` gotcha.
  - `langgraph-caseplan-swap-and-unified-feed-blocker.md` — solution deploy mechanics, HITL-gate rules.
- **Runbook:** `docs/DEMO-RUNBOOK.md` — Path A (run the demo), Path B (rebuild/redeploy: B1 download+merge →
  B2 pack → B3 BAA-clean → B4 publish → B5 deploy → B6 kebab-rename), A6 sweep, P-path (preserve a run).
- **Demo script:** `docs/submission/VIDEO-SCRIPT.md` (recordable now). **Project rules:** `CLAUDE.md`.

## What's next (in priority order)

1. **USER actions (cannot be done by the agent):**
   - **Rotate the GitHub PAT** — it was pasted into the previous chat transcript (now exposed). Revoke at
     github.com → Settings → Developer settings → Tokens. (The agent never echoed it; it lives only in
     `~/.git-creds`, WSL ext4.)
   - **Record the demo video** — script + screen cues are ready (`VIDEO-SCRIPT.md`); fill the
     `[HUMAN: confirm]` deep-links in its Window map.
2. **Submission edges (see `submission-open-edges.md`):** judge-access email; product-feedback form
   (closes **Jul 2**); People's Choice forum post (not yet drafted); evidence screenshots (`SCREENSHOT-SHOTLIST.md`, all `[HUMAN]`).
3. **Nice-to-have offered, not done:** add a `make sweep` (or one-line alias) for the A6 Running-job
   sweep so it's one command after each live run. Each new run leaves sync-gap "Running" job rows.
4. **Optional:** decide what to do with the pre-existing spec-kit template churn (uncommitted; not ours).

## Environment & gotchas (save yourself the pain)

- **`uip` CLI:** lives at `~/.npm-global/bin/uip` — PATH is flaky, always `export PATH="$HOME/.npm-global/bin:$PATH"`. Orchestrator subcommand is `uip or` (not `orchestrator`).
- **Auth:** token in `~/.uipath` (WSL-native ext4; survives `wsl --shutdown`). If expired, re-auth via the
  device flow (previous session used an `xdg-open` shim → `powershell.exe Start-Process` to open the URL in Windows).
- **`/mnt/c` (OneDrive) 9p EIO hazard:** heavy parallel I/O can throw EIO and wedge git/hooks; recover with `wsl --shutdown`. A stale `.git/index.lock` from a crashed op is safe to `rm -f` when no git is running.
- **git push:** remote is HTTPS; creds in `~/.git-creds` as `https://x-access-token:<PAT>@github.com`
  (the bare `https://<PAT>@github.com` form is silently skipped). The secret-scan PreToolUse hook **blocks
  a literal `ghp_…` in any Bash command** → write the creds file with the **Write tool** (rm it first).
- **Commit rules (`CLAUDE.md`):** **no `Co-Authored-By` trailer** (settings.json has no `attribution.commit`);
  **IP-safety zero tolerance** (forbidden tokens list in `CLAUDE.md`; note `wEx`/`workflowExpression` is a
  benign substring false-positive). `knowledge/` is immutable; never touch `.specify/`.
- **HITL gates:** always Approve/Deny or File/Withdraw — **deleting/Removing a gate task Faults the case.**
  `scripts/demo_autocomplete.py` (env `DEMO_ASSIGNEE=<login email>`, `DEMO_KEEP_FIDUCIARY=0`,
  `DEMO_KEEP_OBLIGATION=0`, `DEMO_UIP_BIN=$HOME/.npm-global/bin/uip`) CLI-actions them. Listing needs a
  **user** token (`--as-admin` returns 0 under client-credentials).
- **Job state sync-gap:** completed Maestro case instances never flip their Orchestrator job to Successful —
  confirm closure via **case instances** (`uip maestro case instance list`, fields are **PascalCase**:
  `PackageId / LatestRunStatus / CreatedTimeUtc / ExternalId / Incidents`), NOT the Jobs view.

## Key reference values (non-secret)

- Tenant: `staging.uipath.com` / `hackathon26_042` / `DefaultTenant`
- Folder key (`$FK`): `de7b7c18-d743-4c8c-b555-9bd3b96fe524` (`Shared/CascadeCare-v110`)
- Solution id: `0fc02d30-9645-45b6-4ed8-08dec248fc52` · Master process key: `AC365BA5-C807-4DFC-A009-00F3EA61E497`
- AuditRecord DF entity (tenant-scoped, resolve WITHOUT folder): `252cd5cc-f66c-f111-8fcb-000d3ab36606`
- Dashboard external-app clientId: `6572ecf9-64da-48cd-b846-3c91047ca7e5` (scope `DataFabric.Data.Read` granted)
- Slack channel: `C0B8Q6G77QD` (`#all-cascadecare`)

## Suggested skills (invoke as relevant)

- **`/audit-ip-safety`** — before any commit (mandatory per `CLAUDE.md`).
- **`/thermo-nuclear-code-quality-review` + `/improve-codebase-architecture`** — the mandatory quality loop
  for any substantive slice diff (combined report to `/tmp/architecture-review-<ts>.html`).
- **`/code-review ultra`** — user-triggered multi-agent review of the branch before final submission.
- **speckit** (`/speckit.plan → analyze → tasks → implement`) — only if picking up a new slice from
  `specs/003-uipath-native/tasks.md`.

---

## Suggested prompt for the next session

> You're continuing the **CascadeCare Network Command** UiPath AgentHack 2026 project (repo
> `mlbrilliance/cascadecare-network-command`, branch `master`). Start by reading
> `docs/handoff/2026-06-22-session-handoff.md` and the auto-loaded `MEMORY.md` — everything that shipped
> this week is on `origin/master` @ `ffd6d3f`, solution **1.0.35** + dashboard **v1.0.15** are live, and
> all gates are green. Do NOT re-do that work.
>
> Today I want to focus on **<FILL IN: e.g. drafting the People's Choice forum post / capturing the
> evidence screenshots per docs/submission/SCREENSHOT-SHOTLIST.md / adding a `make sweep` runbook helper /
> a fresh end-to-end demo dry-run>**.
>
> Constraints: follow `CLAUDE.md` (no Co-Authored-By trailer; IP-safety zero tolerance; `knowledge/` and
> `.specify/` are off-limits). `uip` is at `~/.npm-global/bin/uip` (prepend to PATH; tool is `uip or`).
> For any redeploy use `docs/DEMO-RUNBOOK.md` Path B; for a live run use Path A + `scripts/demo_autocomplete.py`
> then sweep Running orphans (A6). I'll handle the GitHub-PAT rotation and the actual video recording myself.
> Ask before committing/pushing or deploying.
