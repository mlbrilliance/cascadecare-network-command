# Handoff — CascadeCare Network Command (2026-06-16)

> For the **next coding agent on a clean session.** Read this top-to-bottom, then the three
> authoritative references in §7. This doc references other artifacts by path — it does **not**
> duplicate them. Everything described here is **committed and pushed**; nothing is in flight.

---

## 1. TL;DR — where things stand

CascadeCare is a **UiPath Maestro Case** demo for **AgentHack 2026 — Track 1** (a multi-stakeholder
healthcare-payment cyber crisis run as one 3-level nested case with 5 goal reversals). It is **built
and live end-to-end** on UiPath Automation Cloud (`clearflow-solution` 1.0.32, folder
`Shared/CascadeCare-v110`). **The build is essentially done.** Recent work has been **submission
polish** (docs, diagram, README, prize accuracy), not new runtime features.

- **Repo HEAD:** `79d52e2` on `master`, **clean working tree, local == origin.**
- **Remote:** `https://github.com/mlbrilliance/cascadecare-network-command.git`
- **The remaining work is mostly human-only** (submit forms, capture screenshots, email judges,
  rotate tokens) plus two optional agent drafting tasks. See §5.

---

## 2. What this project is (60-second orientation)

- **Pure-UiPath at runtime; Python is build-time tooling only.** The Maestro Case canvas IS the
  orchestrator. Read `CLAUDE.md` (root) for the hard rules — IP safety, architecture, conventions,
  the "stop and ask" list. Read `README.md` for the full narrative + component inventory.
- **3 Maestro Cases** (master → stakeholder-parent → grandchild), **11 agents** (6 Agent Builder on
  Claude Sonnet 4.6 BYO-LLM + 5 Coded incl. 1 **LangGraph** `StateGraph`), 19 API Workflows, 9 Data
  Fabric entities, 2 Context Grounding indexes, 2 BPMN, 1 Flow, 1 App = **37 artifacts / 13 surfaces.**
- **Live hero moment:** Reversal 3 (Day 30) fans the master out to 6 stakeholder-parents → 6
  obligation-grandchildren (13 instances, 3 levels) on one canvas.
- **Architecture diagram** (current + accurate): `docs/images/architecture.svg` / `.png`, plus an
  animated `docs/images/architecture.gif`. Source generators live in `/tmp` (uncommitted — see §6).

---

## 3. Repo state & how to verify it yourself

```bash
make resume                       # cross-session SQLite memory (.agent-os/memory/project_memory.db)
uv run pytest && uv run mypy src/ # THE gate — must be green before any commit (683 pass / 7 skip, mypy clean)
git status -sb                    # expect: ## master, clean
git --no-pager log --oneline -12  # this session's trail (see §4)
```

If `uv run pytest` and `uv run mypy src/` are not both green, **do not commit** — that is the
project's non-negotiable pre-commit gate (`CLAUDE.md`).

---

## 4. What shipped this session (by commit — don't re-do these)

All on `master`, pushed. Inspect with `git show <sha>` rather than re-deriving:

| SHA | What |
|---|---|
| `2d3b90f` | forensic LangGraph `enrich_node` now **surfaces** `error_type`/`error_message` instead of swallowing (Criterion-3) |
| `6427abd` | `FORENSIC_FORCE_ENRICH_ERROR` env hook — OFF by default; deterministic live exceptions take. See `agents/forensic-self-exam-agent-langgraph/agent.py` + its tests |
| `910b2f1` | **architecture diagram** rebuilt to live-caseplan truth + embedded (README/Devpost); `docs/submission/PRODUCT-FEEDBACK.md` drafted; corrected the bogus "$10K Specialist Challenge" claim |
| `2b418ec` | committed `architecture.png` (carve-out from the `*.png` gitignore) |
| `c845863` | **verified 2026 prize table** in `STRATEGY.md` (real $50k/3-track structure) |
| `fd06f10` | **stage-name reconcile** (docs → live caseplan names) + README beautification v1 |
| `9a7196d` | README **research-hardened** (reliable `<h1/p align>` centering, alert-out-of-`<details>` fix, **Judging Criteria** table) |
| `f8a9a43` | **animated architecture GIF** (`docs/images/architecture.gif`, 764 KB, schematic — not live footage) embedded in README |
| `79d52e2` | the GIF plan doc (`docs/plans/2026-06-16-001-feat-architecture-animation-gif-plan.md`) |

**Key correction to internalize:** the **"$10K Specialist Coded Agent Challenge" is a CLOSED 2025
event — NOT an AgentHack 2026 prize.** The 2026 coding-agent value is the **+2 bonus** (max score 27).
Do not reintroduce the $10K framing anywhere.

---

## 5. Open items (prioritized; owner-tagged)

### 🔴 Time-sensitive (HUMAN)
1. **Product-feedback form — submit before 2026-07-02, 11:45 PM EDT** (earlier than the Jun 29 main
   deadline). Draft is ready at `docs/submission/PRODUCT-FEEDBACK.md`. Human must (a) confirm
   `forms.office.com/e/KitjGLF5k1` resolves to the **2026** form (Devpost doesn't publish the URL), and
   (b) paste + submit. Worth **$1,500**.
2. **Email judge access** → `andreea.tomescu@uipath.com`; also confirm UiPath Labs access. External
   lead time. Without it, "it's live" is unverifiable by judges.
3. **Decide preserve-a-run vs video.** Judging is rolling (Jun 3–Jul 14); the `case-job-janitor` +
   zombie-sweep can leave a judge an **empty Case Instances view** days later. Either freeze one
   all-Completed run + pause the janitor, OR make the video the canonical artifact (Devpost currently
   promises both).
4. 🔐 **Rotate the two compromised git tokens.** A PAT is stored in `~/.git-creds` (the push
   credential) and another was pasted into an earlier chat. **Both are compromised — rotate them.
   NEVER echo or commit either token.**
5. **Studio Web:** re-pick `ClearFlowVectorStatus` in the Vector Isolation *Update variables* mapping,
   then Publish — clears a false "variable may have been removed" warning BEFORE any republish (see
   memory `maestro-element-retry-canvas-only`).

### 🟢 Optional drafting (AGENT can do)
6. **People's Choice forum post** — valid **$500** (3 winners), community voting **Jul 3–30**. Lead
   with the new diagram/GIF. UiPath Community Forum.
7. **Evidence screenshot shot-list** — exact filename + caption + which-criterion-each-proves, so the
   human's live-tenant capture is a 15-min click-through. Fills the `[HUMAN]` placeholders in
   `docs/submission/DEVPOST.md` and could yield a real live-run GIF (the one thing the schematic GIF
   isn't).

### Lower priority / known debt
8. `docs/architecture.md` was a stale Slice-005-era doc; the worst parts were fixed (`fd06f10`) but a
   fuller refresh is possible. `docs/handoff/PATH-B-wire-case-tasks.md` and `knowledge/REQUIREMENTS.md`
   still carry old (non-live) parent/grandchild stage names — `knowledge/` is **immutable**, leave it.

---

## 6. Gotchas & landmines (operational traps that WILL bite)

- **OneDrive/WSL `index.lock`.** The repo is on `/mnt/c` (OneDrive). Commits intermittently fail with a
  stale `.git/index.lock`. Guard EVERY commit: `[ -f .git/index.lock ] && rm -f .git/index.lock`
  before `git add`. Severe EIO can need `wsl --shutdown` (memory `onedrive-wsl-io-hazard`).
- **Image assets are gitignored.** `.gitignore` ignores `*.png`/`*.gif`/etc. (reference-only policy)
  with **explicit carve-outs**: `!docs/images/architecture.png` and `!docs/images/architecture.gif`.
  Any new committed image needs its own `!`-negation, else `git add` silently no-ops. Verify with
  `git check-ignore <path>` and `git cat-file -e HEAD:<path>` after committing.
- **Diagram generators are in `/tmp`** (`/tmp/gen_arch.py` static, `/tmp/build_anim.py` GIF) and are
  **NOT committed** (lost on a fresh session). To regenerate the diagram/GIF you must re-author them
  from the committed `docs/images/architecture.svg` as reference, or promote them to `scripts/`.
  Rendering needs `cairosvg` (already installed in the `uv` venv) + Pillow; run via `uv run python`.
- **Deadline is EDT, not PDT.** Main submission **Jun 29 2026 11:45 PM EDT**. The Devpost rules-page
  banner shows "PDT" — that's a display artifact; the legal text says EDT. Don't bank the extra 3h.
- **Live caseplan stage names are authoritative** for any diagram/doc (parent: Stakeholder Onboarding
  → Impact Assessment → Obligation Determination → Stakeholder Resolved; grandchild: Obligation Intake
  → Response → Discharged). Older docs drifted; the diagram + README now match the caseplans.
- **HITL gates: ACTION them (Approve/Deny, File/Withdraw) — never DELETE.** Deleting a gate task in
  Action Center **Faults** the case (`ErrorCode 160009`, `IncidentType "User"`). Live-proven.
- **`=datafabric.qem:` fails at runtime in spawn inputs** (`400300`). Fan-out uses literal stakeholder
  slugs. Do NOT claim runtime `qem:` fan-out anywhere.
- **No `Co-Authored-By` trailer** unless `.claude/settings.json` sets `attribution.commit` (it doesn't).
  Ignore the Bash tool's default trailer template.
- **TDD pre-write hook:** test file must exist before source file in `agents/`, `shim/`, `mocks/`.
  **IP-safety:** every commit must pass `/audit-ip-safety` (forbidden-token denylist in `CLAUDE.md`).
  **Never** save working files/tests to the repo root.

---

## 7. Authoritative references (where truth lives — read these)

- **`CLAUDE.md`** (root) — the rulebook: architecture, IP safety, conventions, gates, "stop and ask".
- **`README.md`** — full narrative, live status, component/agent inventory, judging-criteria table.
- **`STRATEGY.md`** — verified 2026 prize landscape, key metrics, priority action list (Tiers 1–4).
- **Auto-memory index:** `~/.claude/projects/-mnt-c-Users-linki-OneDrive-Desktop-cascade-command/memory/MEMORY.md`
  — one-line pointers to durable facts. Especially: `submission-open-edges` (the live prize/open-items
  checklist), `langgraph-caseplan-swap-and-unified-feed-blocker` (live-proven run + closure),
  `maestro-element-retry-canvas-only`, `onedrive-wsl-io-hazard`, `apptask-completion-via-uip-cli`.
- **Submission drafts:** `docs/submission/` (DEVPOST.md, VIDEO-SCRIPT.md, PRODUCT-FEEDBACK.md,
  DEMO-criterion3-and-fanout.md, GO-LIVE-GUIDE.md).
- **Run procedure:** `docs/DEMO-RUNBOOK.md` / `docs/demo/run-playbook.md`. Deviations: `DEVIATIONS.md`.
- **Session store:** `make resume` at start; `make checkpoint …` per subtask; `make save-session …`
  at end; `make log-decision …` for non-obvious calls (see `CLAUDE.md` "Session persistence").

---

## 8. Suggested skills for the next session

- **`/ce-work`** — to execute the People's Choice post or screenshot shot-list against a quick plan.
- **`/ce-plan`** — if a task needs structure first (the GIF this session went `/ce-plan` → execute).
- **`/audit-ip-safety`** — run before every commit (forbidden-token check); mandatory.
- **`/thermo-nuclear-code-quality-review` + `/improve-codebase-architecture`** — the mandatory
  quality loop if you touch any source slice (`CLAUDE.md` "Quality loop").
- **`/code-review ultra`** — user-triggered multi-agent cloud review of the branch (billed; cannot be
  launched by the agent).

---

### First five minutes for the next agent
1. `git status -sb` (expect clean `master` at `79d52e2`) and `uv run pytest && uv run mypy src/`.
2. Skim `CLAUDE.md` + `README.md` + `STRATEGY.md` + memory `submission-open-edges`.
3. Pick from §5 — most-valuable is help with the **People's Choice post** or **screenshot shot-list**;
   the rest is human-gated. Confirm with the user before starting.
