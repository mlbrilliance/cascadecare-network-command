# Demo Video Script — ≤5 minutes, live run (S026)

Strategy (per win-plan): **record the entire live run once**, then cut/speed-up in post. The
contest requires the solution running live (no slides) and **each agent named on screen** — the
narration below names all **11** distinct agents (5 coded incl. **two LangGraph** agents +
6 Agent Builder); add lower-third captions at each agent beat as insurance.

---

## 🎬 Window map — what to open, and where (launch order)

Open these as browser tabs/windows before recording and bring the numbered one forward at each
`▶ ON SCREEN` cue below. URLs are for the judging tenant `staging.uipath.com / hackathon26_042 /
DefaultTenant`, folder `Shared/CascadeCare-v110`. Deep-links marked `[HUMAN: confirm]` — paste the
exact URL from your browser once you navigate there, so a click during recording is instant.

| # | Window / view | What to show | URL / nav path |
|---|---|---|---|
| ① | **Studio Web — master case canvas** | The 3-level Maestro Case design (7 stages, reversal path) | `staging.uipath.com/hackathon26_042/DefaultTenant` → **Studio Web** → solution `clearflow-solution` → open `clearflow-master-crisis` canvas `[HUMAN: confirm deep-link]` |
| ② | **Maestro — Case Instances** | Live instance heatmap; the Reversal-3 fan (13 instances, 3 levels) | `…/DefaultTenant/orchestrator_` → **Maestro** → **Cases → Instances**, folder `CascadeCare-v110` `[HUMAN: confirm]` |
| ③ | **Action Center — Tasks/Actions** | The two HITL gates (fiduciary review; obligation file/withdraw) | `…/DefaultTenant/actions_` → **Tasks** (assigned to you) `[HUMAN: confirm]` |
| ④ | **Orchestrator — Processes & Jobs** | Deployed agents/processes, the hourly **janitor** trigger, the run's jobs | `…/DefaultTenant/orchestrator_` → folder **Shared/CascadeCare-v110** → **Automations ▸ Processes** and **Jobs** `[HUMAN: confirm]` |
| ⑤ | **Dashboard (Coded Web App)** | Live command center — cascade, gauge, reversal timeline, roster, **Compliance Ledger**, operator console | `https://hackathon26_042.staging.uipath.host/clearflow-network-command` (sign in first; **v1.0.15**) |
| ⑥ | **Data Fabric — AuditRecord** *(optional B-roll)* | The immutable ledger entity rows directly in DF | `…/DefaultTenant` → **Data Fabric → Entities → AuditRecord** (entity `252cd5cc…`) `[HUMAN: confirm]` |
| ⑦ | **AI Trust Layer / LLM Gateway** *(optional, brief)* | PHI/PII policy view on an agent's LLM call | `…/DefaultTenant` → **Admin ▸ AI Trust Layer** (or the agent run trace's Gateway panel) `[HUMAN: confirm]` |
| ⑧ | **Terminal** *(optional closing tag)* | Maestro Case Kit CLI (`maestro-case explain` / `lint`) | local shell in the repo root |

Pre-flight (before recording):
1. `docs/DEMO-RUNBOOK.md` auth + the A6 zombie sweep so window ② shows a clean Case Instances view (no stale Running rows). The hero run is `CFCS-67730745` (its 6 ledger rows are already in DF/window ⑤).
2. Sign in to window ⑤ (dashboard) **once now** so the Compliance Ledger is already loaded when you cut to it (fresh sign-in carries the `DataFabric.Data.Read` scope).
3. Window ③ (Action Center) logged in as the assignee for the two HITL gates.
4. OBS/recorder at 1080p+; a visible system clock is fine (proves live).

Timing assumes the proven wall-clock pacing (R3 at t+150s). Speed up dead air 4–8× in post;
keep agent runs and spawns at 1× so motion is visible.

---

## Shot list + narration

### 0:00–0:25 — Cold open: the problem
**▶ ON SCREEN → ① Studio Web · master case canvas, zoomed out (all 7 stages visible).**

> "When a healthcare payment network goes dark, every hospital it serves stops getting paid
> within days. This is CascadeCare Network Command — a UiPath Maestro Case that manages that
> entire crisis as one living case file. ClearFlow Health Network — a fictional payment
> intermediary — just saw claim flows drop at several hospitals at once. Watch it run live."

### 0:25–0:55 — Reversal 1: correlation
**▶ ON SCREEN → ② Maestro · Case Instances (case starting) — caption each agent as it fires.**

> "Day one. The **Claim Flow Anomaly Detector** — a Python coded agent — classifies the
> telemetry drop. The **Multi-Customer Pattern Detector** correlates six providers and finds
> the same signature everywhere. The case goal itself shifts: this isn't six support tickets —
> ClearFlow may be the breach vector. That goal shift is Reversal 1, and the case canvas
> re-routes around it."

### 0:55–1:25 — Reversal 2: vector isolation
**▶ ON SCREEN → ① Studio Web · Vector Isolation stage + the agent run trace; optional quick cut to ⑦ Trust Layer policy panel.**

> "The **Forensic Self-Exam Agent** — a **LangGraph** state graph on the UiPath Python SDK —
> coordinates the internal sweep, and the **Vector Hypothesis Agent** — Claude, running through
> UiPath's LLM Gateway with Trust Layer PHI policies on every call — clears ClearFlow and points
> at the Nimbus patient-engagement vendor. And it fails safe: if the Gateway ever drops, the agent
> surfaces the error and still routes correctly — the case never crashes. Reversal 2: ClearFlow is
> a bystander with a strategic posture decision."

### 1:25–2:30 — **HERO: Reversal 3 — the cascade fan**
**▶ ON SCREEN → split ① Studio Web (Regulatory Response stage) + ② Maestro Case Instances. This is the money shot — let the 6 spawns land at 1×.**

> "Day 30. A Tennessee DOI subpoena hits. The master case spawns **six stakeholder parent
> cases simultaneously** — one per hospital system, each seeded with its provider identity —
> using Maestro's native case-management task. And each parent immediately spawns its own
> obligation grandchild. Thirteen coordinated case instances, **three levels of native case
> nesting**, on one screen. In each parent, the **Assess Claim Disruption agent** scores the
> provider's liquidity risk, and the **BAA Boundary Reasoner** decides what ClearFlow may
> legally disclose — six providers, six different answers."

### 2:30–2:50 — Context Grounding proof
**▶ ON SCREEN → ② Maestro · the BAA Boundary Reasoner's run trace for Northstar — scroll the rationale so the §-cited corpus text and the cross-BAA conflicts are visible. (Live-proven 2026-06-13: job 77c506d8 quotes the corpus section-by-section and flags Alpha + Delta conflicts.)**

> "And this isn't the model guessing. The BAA Boundary Reasoner **retrieves each provider's
> actual Business Associate Agreement from a UiPath Context Grounding index** and grounds every
> citation in the retrieved text. For Northstar it returns a **conditional** disclosure
> position — and flags that the same production would *violate* Alpha's and Delta's BAAs, which
> restrict disclosure to counsel only. Six BAAs, real retrieval, genuinely conflicting answers."

### 2:50–3:20 — Vertical bridge (inside one parent case)
**▶ ON SCREEN → ① Studio Web · one stakeholder parent's Impact Assessment stage (the 3 ViVE solution tasks).**

> "Inside every stakeholder case, CascadeCare orchestrates UiPath's own ViVE-2026 healthcare
> solutions — Medical Records Summarization quantifies PHI exposure, Claim Denial Prevention
> protects revenue, Prior Authorization keeps care moving. CascadeCare is the crisis layer for
> the healthcare agents UiPath already ships."

### 3:20–4:00 — Reversal 4: the human gate
**▶ ON SCREEN → ① Studio Web (master pauses at Fiduciary Review) → cut to ③ Action Center; complete the tri-party form on camera.**

> "Day 45. Payers demand data the BAAs forbid. The **Fiduciary Conflict Detector** maps the
> three-way conflict and the case **stops for a human** — a tri-party ruling in Action Center.
> I rule as counsel, with my rationale — and the case records *who* decided, *why*, and *when*.
> This decision isn't cosmetic: it's read downstream, framing ClearFlow as cooperative or
> contesting in the litigation stage. Down at the grandchild level, the **Classify Obligation
> agent** has already triaged each obligation, and its own file-or-withdraw human gate works the
> same way."

### 4:00–4:30 — Reversal 5 + closure proof
**▶ ON SCREEN → ① Studio Web (Litigation Defense stage) → ② Maestro Case Instances as everything drains to Completed. Optional B-roll: ④ Orchestrator Jobs.**

> "Day 90. The litigation cascade lands and the **Negligent Monitoring Risk Agent** re-scores
> ClearFlow's co-defendant exposure — privilege reshuffles, the posture changes one last time.
> And then the part most case-management demos never show: **every case completes.** Master,
> six children, six grandchildren — all Completed. Even the cleanup is agentic: a coded agent,
> the **Case Job Janitor**, sweeps platform job-state drift on an hourly Orchestrator trigger."

### 4:30–5:00 — Close: the immutable ledger + command center
**▶ ON SCREEN → ⑤ Dashboard (Coded Web App). Land on the cascade + reversal timeline, then scroll to the *Compliance Ledger* panel showing the live AuditRecord rows + integrity-hash badges. (Optional B-roll: ⑥ Data Fabric AuditRecord entity.) End card with repo URL.**

> "And the moment the case closes, an **eleventh** agent fires: **audit-ledger-writer** — a
> **second LangGraph agent**, wired right into the case's closing stage — writes an **immutable
> compliance ledger** to UiPath Data Fabric, one survey-ready row per obligation. Here it is,
> live on our command center — a UiPath Coded Web App — six immutable rows for this run, each with
> its disposition, privilege, and a content-integrity fingerprint. Three nested case levels,
> eleven named agents, five goal reversals, two human gates, **thirteen UiPath product surfaces**,
> Trust Layer on every LLM call — and when an agent's Gateway call fails, it degrades gracefully
> instead of crashing the case. All UiPath-native, all live on Automation Cloud, and built
> end-to-end with Claude Code. CascadeCare Network Command: the living case layer for healthcare
> financial shockwaves."

### Optional closing tag (≤15s) — Above and beyond: the open-source contribution
**▶ ON SCREEN → ⑧ Terminal. `maestro-case explain 400300` returns the cause + fix instantly, then a quick `maestro-case lint` on a caseplan directory.**

> "One more thing. Building this live, we kept hitting undocumented Maestro Case error codes
> that return zero search results. So we packaged that hard-won knowledge into a free,
> open-source toolkit — **Maestro Case Kit** — that explains those errors and lints caseplans
> in CI, with no UiPath login. We even hit this exact bug in UiPath's *own* official skills —
> since fixed upstream — so the kit ships a guard that catches it in your code. Beyond the demo,
> we shipped something UiPath could adopt tomorrow."

---

## Agent name checklist (all 11 distinct agents must be spoken or captioned)

Coded (5 distinct; the original Python forensic agent is superseded by its LangGraph version):
- [ ] Claim Flow Anomaly Detector (coded · Python SDK) — 0:25
- [ ] Multi-Customer Pattern Detector (coded · Python SDK) — 0:25
- [ ] Forensic Self-Exam Agent (coded · **LangGraph**) — 0:55
- [ ] Case Job Janitor (coded · Python SDK, ops) — 4:00
- [ ] **Audit Ledger Writer** (coded · **LangGraph**, in-case at the Closed stage) — 4:30

Agent Builder (6 · Claude BYO-LLM):
- [ ] Vector Hypothesis Agent — 0:55
- [ ] Assess Claim Disruption — 1:25
- [ ] BAA Boundary Reasoner — 1:25
- [ ] Fiduciary Conflict Detector — 3:20
- [ ] Classify Obligation — 3:20
- [ ] Negligent Monitoring Risk Agent — 4:00

## Honesty guardrails

- Never say "Data Fabric drives the fan-out at runtime" — spawn identities are literal
  provider slugs (runtime `qem:` in JobArguments fails; product feedback filed).
- Context Grounding IS live (both indexes ingested + retrieval-verified 2026-06-12) — you may
  say "the BAA Boundary Reasoner retrieves each provider's BAA text from a Context Grounding
  index"; do NOT claim more than retrieval (e.g., no "fine-tuned" language).
- **Audit ledger / Compliance Ledger panel:** the ledger is written **in-case at the Closed stage**
  by `audit-ledger-writer-langgraph` (live-proven v1.0.34, run `CFCS-67730745`, 6 rows, idempotent on
  duplicate fire) and the dashboard reads it **live** from Data Fabric (`DataFabric.Data.Read`). Say
  "immutable, append-only, survey-ready ledger." Do **not** claim cryptographic tamper-proofing — the
  per-row integrity badge is a **presentational content fingerprint**, not a cryptographic seal.
- If a transient LLM Gateway 520 faults an agent mid-recording: `uip maestro case instance
  retry <id>` resumes the run — cut the pause in post rather than restarting.
- Both Approve and Deny **advance** the fiduciary gate the same way — the decision is data-driven
  (`reviewerDecision` consumed downstream), NOT a stage rework. Never narrate Deny as "rewinding"
  a stage. **Never delete/Remove a gate task** to advance it — that Faults the case; always Approve/Deny
  (or File/Withdraw).
- **Maestro Case Kit framing:** it's a **define-once Python** toolkit (CLI + MCP server + agent
  skills) — do NOT call it "printing-press-generated" (a spike proved printing-press only wraps
  external APIs, not static validators). v1 is offline/credential-free; the auth operators are a
  v2 roadmap, not shipped — don't demo them. The `uip maestro` namespace bug is **already fixed
  upstream** on UiPath's `main` — do NOT claim a "contribute-back PR" or that "we fixed UiPath's
  skills." Say: "we found this bug in UiPath's own skills (since fixed upstream) and shipped a
  `check-cli` guard against it."

## Post-production

- Cut to ≤5:00; speed dead air 4–8×, keep spawns/gates/the ledger reveal at 1×.
- Lower-third captions at every agent beat (checklist above).
- Separate 1-minute coding-agent reel: screen captures of Claude Code sessions
  (`docs/coding-agents/screenshots/`), narrated over the CLAUDE_CODE_USAGE.md highlights.
  **Close the reel on the open-source contribution** (the strongest "above and beyond" beat):
  Claude Code didn't just build the demo — it extracted the project's hardest-won, undocumented
  UiPath discoveries into **Maestro Case Kit**, a free, installable toolkit (CLI + MCP server +
  agent skills, all offline/credential-free). Show two terminal runs live: `maestro-case explain
  400300` (cryptic error → proven cause + fix) and `maestro-case lint <caseplan-dir>` (catches
  footguns in CI). Note we found this exact bug in UiPath's own official skills (since fixed
  upstream) and shipped a `check-cli` guard against it. One line for the judges: *"the +2
  coding-agent value made concrete — tooling UiPath could dogfood."*
- Separate **90-second Criterion-3 clip** (exception handling) per
  `docs/submission/DEMO-criterion3-and-fanout.md`: in-agent graceful degradation (the agent
  surfacing `error_type` and still routing) + the recorded/consumed HITL ruling + an `instance
  retry` recovery with its Action-History audit trail. Submit as a supplemental video — it lets a
  time-boxed judge score Criterion 3 at the top of the band in under two minutes, while most
  submissions never show a single failure.
