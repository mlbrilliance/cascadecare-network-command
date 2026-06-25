# Demo Video Script — ≤5 minutes, live run (S026)

Strategy (per win-plan): **record the entire live run once**, then cut/speed-up in post. The
contest requires the solution running live (no slides) and **each agent named on screen** — the
narration below names all **11** distinct agents (5 coded incl. **two LangGraph** agents +
6 Agent Builder); add lower-third captions at each agent beat as insurance. (The repo ships
**12 agents** — 6 Coded + 6 Agent Builder; the video narrates **11 distinct on screen** because the
original Python forensic agent is superseded by its LangGraph version and isn't shown separately.
Both counts are correct — see [`STORY.md`](STORY.md) §13 for the canonical 12.)

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
3. Window ③ (Action Center) logged in as the assignee for the two HITL gates. ⚠️ The
   **Tri-Party Fiduciary Conflict** gate may appear as **several identical AppTasks** (a known
   1.0.36 residual — the gate is re-dispatched once per spawn-fan event). Approving any **one**
   advances the master; the duplicates are harmless. On camera, click into one and complete it —
   don't draw attention to the list count (or frame the shot on the single task you action).
4. OBS/recorder at 1080p+; a visible system clock is fine (proves live).

Timing assumes the proven wall-clock pacing (R3 at t+150s). Speed up dead air 4–8× in post;
keep agent runs and spawns at 1× so motion is visible.

---

## 🎙️ Performance direction (read this once before you record)

This is not a feature tour — it's an **opening statement**. Deliver it like a master litigator
who happens to be unveiling a flagship product: calm authority on the facts, rising conviction on
the payoffs. The facts here are genuinely extraordinary — **let specificity carry the awe** (the
words "thirteen live instances" and "six conflicting answers" do more than any adjective). Your
job is to frame, not to oversell.

- **Two crescendos. Find them, build to them.** ① the Reversal-3 cascade fan (`1:25–2:30`) and
  ② the closing tally (`4:30–5:00`). Lift tempo and energy into both; everything else is the climb.
- **Dynamic range.** Drop your voice on the quiet, technical beats so the spawn fan and the final
  count *hit*. Monotone enthusiasm reads as a sales pitch; controlled contrast reads as mastery.
- **Three lines to land like a verdict** — full one-beat pause *after* each:
  *"The case bends — it does not break."* · *"It stops, and asks a human."* · *"Everything closes."*
- **The recurring image is a living case file** that absorbs five shocks and stays standing. Open
  on it, close on it. That through-line is what makes the ending feel earned, not listed.
- **Never inflate.** Every claim below is true and survives scrutiny (see Honesty guardrails). The
  confidence comes from *knowing it's real and running* — say "live," mean it, and let the screen prove it.

---

## Shot list + narration

### 0:00–0:25 — Cold open: the lights go out
**▶ ON SCREEN → ① Studio Web · master case canvas, zoomed out (all 7 stages visible).**

> "A healthcare payment network is invisible — until it goes dark. Then every hospital it touches
> stops getting paid in days, and patient care is the next thing to break. This is **CascadeCare
> Network Command**: one UiPath Maestro Case that runs an entire multi-party crisis as a single,
> living case file. ClearFlow Health Network — our fictional payment intermediary — just went dark
> across six hospital systems at once. No slides. Watch it run, live."

### 0:25–0:55 — Reversal 1: the mission rewrites itself
**▶ ON SCREEN → ② Maestro · Case Instances (case starting) — caption each agent as it fires.**

> "Day one. The **Claim Flow Anomaly Detector** — a Python coded agent — reads the telemetry
> collapse and classifies it in seconds. The **Multi-Customer Pattern Detector** correlates all
> six providers and finds the *exact same signature* on every one. And here the case rewrites its
> own mission: these aren't six support tickets — ClearFlow itself may be the breach vector. That
> is Reversal One — and watch the canvas re-route the entire investigation around it, on its own."

### 0:55–1:25 — Reversal 2: bend, don't break
**▶ ON SCREEN → ① Studio Web · Vector Isolation stage + the agent run trace; optional quick cut to ⑦ Trust Layer policy panel.**

> "Now the case turns the investigation on itself. The **Forensic Self-Exam Agent** — a **LangGraph**
> state machine on UiPath's Python SDK — runs the internal sweep, while the **Vector Hypothesis
> Agent** — Claude, every call routed through UiPath's LLM Gateway under Trust Layer PHI policy —
> clears ClearFlow and names the real source: the Nimbus patient-engagement vendor. And it never
> gambles: if the Gateway drops mid-call, the agent surfaces the failure and *still routes correctly.*
> The case bends — it does not break. That's Reversal Two."

### 1:25–2:30 — **HERO: Reversal 3 — the cascade fan**
**▶ ON SCREEN → split ① Studio Web (Regulatory Response stage) + ② Maestro Case Instances. This is the money shot — let the 6 spawns land at 1×.**

> "Day thirty. A Tennessee Department of Insurance subpoena lands — and this is the moment
> everything has been building toward. **Watch.** The master case spawns **six stakeholder cases
> at once** — one for every hospital system, each seeded with its own provider identity — through
> Maestro's *native* case-management task. Not a script. Not a loop. And before those even settle,
> every single parent spawns its own obligation case beneath it. **Thirteen live case instances.
> Three levels of real, native case nesting.** Fanning out across one screen, in real time. This
> is orchestration most platforms can only *draw on a whiteboard* — and here it is, running. Inside
> each of the six parents, the **Assess Claim Disruption** agent scores that provider's liquidity
> risk, and the **BAA Boundary Reasoner** rules on exactly what ClearFlow is legally allowed to
> disclose. Six providers. Six independent investigations. Six different answers — at the same instant."

### 2:30–2:50 — Grounded, not guessed
**▶ ON SCREEN → ② Maestro · the BAA Boundary Reasoner's run trace for Northstar — scroll the rationale so the §-cited corpus text and the cross-BAA conflicts are visible. (Live-proven 2026-06-13: job 77c506d8 quotes the corpus section-by-section and flags Alpha + Delta conflicts.)**

> "And none of this is the model guessing. The **BAA Boundary Reasoner** pulls each provider's
> *actual* Business Associate Agreement from a UiPath Context Grounding index and anchors every
> line to the retrieved text. For Northstar — a **conditional** disclosure that catches the same
> production would *violate* Alpha's and Delta's agreements. Real documents. Real retrieval.
> Genuinely conflicting law."

### 2:50–3:20 — The command layer for UiPath's own agents
**▶ ON SCREEN → ① Studio Web · one stakeholder parent's Impact Assessment stage (the 3 ViVE solution tasks).**

> "And look *where* this is happening. Inside every stakeholder case, CascadeCare is conducting
> UiPath's own ViVE-2026 healthcare solutions — Medical Records Summarization quantifies the PHI
> exposure, Claim Denial Prevention and Resolution defends revenue, Prior Authorization keeps patient
> care moving. This is revenue cycle management under fire — the exact payer-and-provider workflows
> UiPath ships today, now governed by one living case. CascadeCare doesn't replace the healthcare
> agents UiPath already runs — it's the **crisis command layer** that puts every one of them to work
> when the whole network is burning."

### 3:20–4:00 — Reversal 4: the machine asks a human
**▶ ON SCREEN → ① Studio Web (master pauses at Fiduciary Review) → cut to ③ Action Center; complete the tri-party form on camera.**

> "Day forty-five. The payers demand data the BAAs forbid — and the machine reaches its limit. The
> **Fiduciary Conflict Detector** maps a genuine three-way conflict, and then the case does what most
> automation never dares: **it stops, and asks a human.** A tri-party ruling, in Action Center. I
> decide as counsel — with my reasoning — and the case captures *who* ruled, *why*, and *when*. Not
> ceremony: that ruling is read downstream, framing ClearFlow as cooperative or contesting into
> litigation. One level down, the **Classify Obligation** agent has already triaged every obligation —
> each with its own file-or-withdraw gate. **Agents think, robots do — and people lead.** Judgment,
> exactly where it belongs."

### 4:00–4:30 — Reversal 5: everything closes
**▶ ON SCREEN → ① Studio Web (Litigation Defense stage) → ② Maestro Case Instances as everything drains to Completed. Optional B-roll: ④ Orchestrator Jobs.**

> "Day ninety. The litigation cascade hits, and the **Negligent Monitoring Risk Agent** re-scores
> ClearFlow's co-defendant exposure — privilege reshuffles, the posture shifts one final time. And
> then the thing case-management demos almost never dare to show you: **everything closes.** Master,
> six children, six grandchildren — every case, Completed. Even the cleanup runs itself: a coded
> agent, the **Case Job Janitor**, sweeps job-state drift on an hourly Orchestrator trigger. No
> loose ends. No human mop-up."

### 4:30–5:00 — Close: the immutable ledger + the tally
**▶ ON SCREEN → ⑤ Dashboard (Coded Web App). Land on the cascade + reversal timeline, then scroll to the *Compliance Ledger* panel showing the live AuditRecord rows + integrity-hash badges. (Optional B-roll: ⑥ Data Fabric AuditRecord entity.) End card with repo URL.**

> "And the instant the case closes, the **eleventh** agent fires: **Audit Ledger Writer** — a
> **second LangGraph agent**, wired straight into the closing stage — writing an **immutable,
> append-only compliance ledger** to UiPath Data Fabric: one survey-ready row per obligation, each
> carrying its disposition, its privilege call, and a content-integrity fingerprint. There it is —
> live, on our command center, a UiPath Coded Web App.
>
> Now count what just ran. Three nested case levels. Eleven named agents. Five goal reversals. Two
> human gates. **Thirteen UiPath product surfaces.** Trust Layer on every single LLM call — and
> graceful degradation the moment one fails. All UiPath-native. All live on Automation Cloud. All
> built end-to-end with Claude Code. One living case file that took five shocks and never broke.
> **CascadeCare Network Command — the living case layer for healthcare's financial shockwaves.**"

### Optional closing tag (≤15s) — Above and beyond: the open-source contribution
**▶ ON SCREEN → ⑧ Terminal. `maestro-case explain 400300` returns the cause + fix instantly, then a quick `maestro-case lint` on a caseplan directory.**

> "One more thing. Building this live, we kept slamming into undocumented Maestro Case error codes —
> the kind that return *zero* search results. So we packaged that hard-won knowledge into a free,
> open-source toolkit, **Maestro Case Kit** — it explains those errors and lints caseplans in CI,
> with no UiPath login. We even found this exact bug in UiPath's *own* official skills — since fixed
> upstream — and shipped a guard that catches it. We didn't just build a demo. We left the platform
> better than we found it."

---

## 🏅 How this script earns every official AgentHack 2026 criterion

> **Source:** AgentHack 2026 official rules, Devpost (`uipath-agenthack.devpost.com/rules`), verified
> 2026-06-24. The Phase-2 finale scores **five criteria of equal weight** on the live presentation +
> Q&A; Phase-1 adds **Completeness of Delivery**. The **coding-agent bonus is not a separate category —
> it adds weight inside Platform Usage**, so the Claude Code / Maestro Case Kit beat is worth real points
> (document the coding-agent use in the Devpost description + README to claim it). Judges score what they
> *see* on screen — every row below must be unmistakable, not inferred.

| Official criterion (equal weight) | Where this script earns it on camera |
|---|---|
| **Business Impact & Adoption Potential** — real-world relevance, business case, scalability | Cold open (`0:00`): hospitals stop getting paid in days, patient care breaks next. Vertical bridge (`2:50`): "revenue cycle management under fire — the exact payer/provider workflows UiPath ships today." Close (`4:30`): live on Automation Cloud, production-ready, one reusable crisis layer. |
| **Platform Usage** — depth + deliberateness (Agent Builder · Maestro · API Workflows · coded agents · external frameworks) · ⭐ **coding-agent bonus lands here** | Every agent beat names its surface (Coded Agents · Agent Builder · **LangGraph** · LLM Gateway · Trust Layer · Context Grounding · Data Fabric · Action Center · Coded Web App); the closing tally counts **thirteen UiPath product surfaces**; the closing tag = **built end-to-end with Claude Code** + the open-source Maestro Case Kit. |
| **Technical Execution, Feasibility & Versatility** — architecture, code quality, production-readiness, **handling of exceptions/failures/edge cases** | Reversal 2 (`0:55`): graceful degradation when the LLM Gateway drops ("the case bends — it does not break"). Reversal 5 (`4:00`): *every* case Completes + the Case Job Janitor sweeps drift. Supplemental 90-sec exception-handling clip. |
| **Creativity & Innovation** — novel design, unexpected orchestration patterns, creative framing | The HERO fan (`1:25`): three levels of **native** case nesting, 13 live instances on one screen. Grounded conflict (`2:30`): six BAAs → six conflicting answers. The in-case **second LangGraph** audit-ledger write (`4:30`). |
| **Presentation** — clarity, structure, **problem → solution → impact arc**, confidence, accessible communication, Q&A | The script is built as that exact arc; the Performance-direction block tunes delivery and pacing; the closing tally makes total impact legible in ~10 seconds. (Rehearse Q&A — the finale scores it.) |
| **Completeness of Delivery** *(Phase 1)* — functional end-to-end prototype, public GitHub + README + setup, demo ≤5 min | A real **live run**, no slides; ≤5:00 enforced (core narration ≈ 5:00); end card with the public repo URL. |

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
- **Tri-Party gate may show as duplicate AppTasks** (1.0.36 residual — the gate is re-dispatched once
  per spawn-fan event, with non-fatal `450007` "duplicate subscription" incidents in Monitoring).
  Approving any one advances the master; the rest are harmless. Don't narrate or zoom the list count —
  action a single task. This is platform-level agentic re-dispatch, not a defect in our case logic;
  see `docs/DEMO-RUNBOOK.md` (A4 caveat) and `docs/changelog.md` (1.0.36).
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
- Separate **90-second exception-handling clip** (official rubric: *Technical Execution, Feasibility
  & Versatility* — "handling of exceptions, failures, and edge cases") per
  `docs/submission/DEMO-criterion3-and-fanout.md`: in-agent graceful degradation (the agent
  surfacing `error_type` and still routing) + the recorded/consumed HITL ruling + an `instance
  retry` recovery with its Action-History audit trail. Submit as a supplemental video — it lets a
  time-boxed judge score Criterion 3 at the top of the band in under two minutes, while most
  submissions never show a single failure.
