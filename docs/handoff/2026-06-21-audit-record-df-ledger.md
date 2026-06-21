# Handoff — AuditRecord Data Fabric ledger (2026-06-21)

**For:** the next coding agent, fresh session.
**Mission this session was:** make the "immutable audit record" claim honest by persisting
a **detailed, immutable, queryable audit ledger to Data Fabric**, produced by a real run.
**Status: core delivered + live-verified. Nothing committed yet. Two live-touching decisions remain.**

> Background context is in auto-memory (loaded each session). Read these first, don't re-derive:
> - `memory/audit-record-df-ledger.md` — full detail of what's wired + every gotcha (authoritative).
> - `memory/submission-open-edges.md` — submission checklist; hero run `CFCS-67598194` preservation.
> - `memory/orchestrator-cleanup-v110-only.md` — tenant is trimmed to `Shared/CascadeCare-v110` only.
> - `CLAUDE.md` — IP-safety (zero tolerance), SPEC-gate, TDD, caseplan/redeploy conventions.

---

## 1. What is DONE and verified live (do not redo)

- **`AuditRecord` Data Fabric entity created** — id `252cd5cc-f66c-f111-8fcb-000d3ab36606`.
- **Ledger populated for hero run `CFCS-67598194`** — **6 detailed immutable rows** (one per
  stakeholder northstar/alpha/beta/gamma/delta/epsilon; epsilon `withdrawn`, rest `filed`),
  each with `obligationType/disposition/privilegeFlag/jurisdiction/requestingParty/recordedAt/auditSummary`.
  Verify: `uip df records list 252cd5cc-f66c-f111-8fcb-000d3ab36606 --output json`.
- **Tested writer** — `src/cascadecare/audit_ledger.py` (pure `compose_audit_records` /
  `select_new` / `run_ledger` + lazy-SDK `main`); 15 tests in
  `tests/unit/cascadecare/audit_ledger/`; **15 + docs/inventory tests green, mypy clean.**
- **Idempotent ops runner** — `scripts/populate_audit_ledger.py <case_ref> --recorded-at <iso>`.
- **Honesty fix** — `README.md:~370` no longer says `generate-audit-record` "writes a per-action
  audit record"; it now describes the Action-History entry + the DF ledger writer.

## 2. Key decision already made (and why) — don't silently reverse it

The writer is **build-time/ops tooling in `src/`, NOT a deployed coded agent.** Putting an
`agent.py` under `agents/` would count it as a 6th live coded agent and force "5 Coded Agents /
37 runtime artifacts" → 6/38 across README/DEVPOST/CODING_AGENTS/CLAUDE_CODE_USAGE — but those
say artifacts are *running live on Automation Cloud*, and it is **not deployed**. So the live
inventory honestly stays **5/37**. The ledger is real regardless of where the writer lives.

## 3. Uncommitted working tree (branch `master`, HEAD `0798f58`)

```
 M README.md                              # honesty fix (line ~370)
?? src/cascadecare/audit_ledger.py        # writer core (tested)
?? scripts/populate_audit_ledger.py       # idempotent ops runner
?? tests/unit/cascadecare/                # 15 tests (audit_ledger/)
?? "docs/submission/Submission deck.pptx" # PRE-EXISTING, human-owned — DO NOT commit
```
Nothing is staged. The DF entity + rows already exist in the tenant (live), independent of git.

## 4. Open decisions for THIS session (all touch the live solution — confirm with the user)

1. **Commit the work** (recommended first). Suggested message scope: `feat(audit-ledger): AuditRecord
   Data Fabric compliance ledger + tested writer`. Run the full gate first (§6). Do **not** add a
   `Co-Authored-By` trailer unless `.claude/settings.json` sets `attribution.commit`.
2. **Promote to a deployed 6th coded agent?** Would bump counts to 6/38 in README/DEVPOST/
   CODING_AGENTS/CLAUDE_CODE_USAGE + the inventory test, and requires a **v110 solution redeploy**
   (gotcha-heavy — see memory) + a **fresh run**. Higher judge value, higher risk to the preserved
   hero run. **User's call — do not do unprompted.**
3. **Fresh re-run** (user earlier chose "rebuild now, re-run after"): start `clearflow-master-crisis`
   in v110, let it walk to all-Completed (action the HITL gate — Approve/Deny, **never delete it or
   the case Faults**), then `uv run python scripts/populate_audit_ledger.py CFCS-<new> --recorded-at <iso>`.
4. **(Optional) In-case enrichment of `generate-audit-record`** so the live API-workflow entry is
   also detailed — needs a redeploy; lower priority than the DF ledger which is already done.

## 5. Hazards / hard rules (will bite a fresh agent)

- **IP safety zero-tolerance** — only committed fictional names; `/audit-ip-safety` must pass before commit.
- **DF STRING fields cap at 200 chars** — longer value silently fails the insert. camelCase field
  names (underscore drops on insert); never field name `id` (reserved).
- **Per-instance case vars are transient** — `GET /instances/{id}/global-variables` 404s
  (`PIMS-410201`) after completion. Ledger detail comes from the canonical scenario, not live vars.
- **In-case DF write needs human OAuth** — `Create Entity Record` activity exists but needs a
  dataservice IS connection (none); `uip is connections create` is a browser OAuth flow.
- **HITL gates: Approve/Deny only — deleting a gate task Faults the case** (incident 160009).
- **OneDrive/WSL I/O hazard** — repo on `/mnt/c` can throw EIO + leave a stale `.git/index.lock`
  (hit this session; cleared with `rm -f .git/index.lock`). `wsl --shutdown` if git wedges.
- **Coded-app deploy hangs** on `-v`/`--path-name`; use the bare deploy form (see CLAUDE.md).

## 6. Verification commands (run before any commit)

```bash
uv run pytest && uv run mypy src/                                   # full gate (CLAUDE.md)
uv run pytest tests/unit/cascadecare/audit_ledger/ -q               # writer unit tests (15)
uv run python scripts/populate_audit_ledger.py CFCS-67598194 \
    --recorded-at 2026-06-20T03:38:40Z                              # expect: 0 written / 6 skipped
uip df records list 252cd5cc-f66c-f111-8fcb-000d3ab36606 --output json   # 6 live rows
```

## 7. Suggested skills to invoke

- **`uipath-data-fabric`** — if extending the entity / records / the writer's DF calls.
- **`uipath-platform`** — any tenant op (`uip df`, jobs, folders); load before UiPath API calls.
- **`uipath-solution`** + **`uipath-agents`** — only if the user opts to promote/deploy the writer
  as a coded agent (pack/publish/deploy + the v110 redeploy dance).
- **`audit-ip-safety`** and **`thermo-nuclear-code-quality-review`** + **`improve-codebase-architecture`**
  — the mandatory quality loop before committing a slice (CLAUDE.md).
- **`rehearse-demo`** — if the user pivots back to demo/submission readiness.
- **`tdd`** — any new code must be test-first (pre-write hook enforces test-before-source).

## 8. Do NOT

- Commit `docs/submission/Submission deck.pptx` (human-owned).
- Bump "5 Coded Agents / 37 artifacts" unless the writer is actually deployed (overclaim).
- Promise judges a live per-instance variable dump (transient blob).
- Re-create the `AuditRecord` entity or re-insert the 6 rows (already live + idempotent).
