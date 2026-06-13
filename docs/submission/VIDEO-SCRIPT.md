# Demo Video Script — ≤5 minutes, live run (S026)

Strategy (per win-plan): **record the entire live run once**, then cut/speed-up in post. The
contest requires the solution running live (no slides) and **each agent named on screen** — the
narration below names all 10; add lower-third captions at each agent beat as insurance.

Pre-flight (before recording):
1. `docs/DEMO-RUNBOOK.md` auth + A6 zombie sweep (clean Case Instances view — no stale Running rows).
2. Two browser tabs ready: **Maestro > Case Instances** (heatmap) and the master case canvas.
3. Action Center tab logged in (for the two HITL gates).
4. OBS/recorder at 1080p+; system clock visible is fine (proves live).

Timing assumes the proven wall-clock pacing (R3 at t+150s). Speed up dead air 4–8× in post;
keep agent runs and spawns at 1× so motion is visible.

---

## Shot list + narration

### 0:00–0:25 — Cold open: the problem (canvas, zoomed out)
*Show: master case canvas, all 7 stages visible.*

> "When a healthcare payment network goes dark, every hospital it serves stops getting paid
> within days. This is CascadeCare Network Command — a UiPath Maestro Case that manages that
> entire crisis as one living case file. ClearFlow Health Network — a fictional payment
> intermediary — just saw claim flows drop at several hospitals at once. Watch it run live."

### 0:25–0:55 — Reversal 1: correlation (Initial Response → Multi-Customer Investigation)
*Show: case started; anomaly tasks running. Caption each agent as it fires.*

> "Day one. The **Claim Flow Anomaly Detector** — a Python coded agent — classifies the
> telemetry drop. The **Multi-Customer Pattern Detector** correlates six providers and finds
> the same signature everywhere. The case goal itself shifts: this isn't six support tickets —
> ClearFlow may be the breach vector. That goal shift is Reversal 1, and the case canvas
> re-routes around it."

### 0:55–1:25 — Reversal 2: vector isolation
*Show: Vector Isolation stage; agent run trace (LLM Gateway / Trust Layer panel if quick).*

> "The **Forensic Self-Exam Agent** coordinates the internal sweep, and the **Vector
> Hypothesis Agent** — Claude, running through UiPath's LLM Gateway with Trust Layer PHI
> policies on every call — clears ClearFlow and points at the Nimbus patient-engagement
> vendor. Reversal 2: ClearFlow is a bystander with a strategic posture decision."

### 1:25–2:50 — **HERO: Reversal 3 — the cascade fan** (~2:30 per shot plan)
*Show: split between master canvas (Regulatory Response stage) and Case Instances view.
This is the money shot — let the 6 spawns land at 1×.*

> "Day 30. A Tennessee DOI subpoena hits. The master case spawns **six stakeholder parent
> cases simultaneously** — one per hospital system, each seeded with its provider identity —
> using Maestro's native case-management task. And each parent immediately spawns its own
> obligation grandchild. Thirteen coordinated case instances, **three levels of native case
> nesting**, on one screen. In each parent, the **Assess Claim Disruption agent** scores the
> provider's liquidity risk, and the **BAA Boundary Reasoner** decides what ClearFlow may
> legally disclose — six providers, six different answers."

### 2:30–2:50 — Context Grounding proof (overlay on a BAA agent trace)
*Show: the BAA Boundary Reasoner's run trace / output for Northstar — scroll the rationale so
the §-cited corpus text and the cross-BAA conflicts are on screen. (Live-proven 2026-06-13:
job 77c506d8 quotes the corpus section-by-section and flags Alpha + Delta conflicts.)*

> "And this isn't the model guessing. The BAA Boundary Reasoner **retrieves each provider's
> actual Business Associate Agreement from a UiPath Context Grounding index** and grounds every
> citation in the retrieved text. For Northstar it returns a **conditional** disclosure
> position — and flags that the same production would *violate* Alpha's and Delta's BAAs, which
> restrict disclosure to counsel only. Six BAAs, real retrieval, genuinely conflicting answers."

### 2:50–3:20 — Vertical bridge (inside one parent case)
*Show: one stakeholder parent's Impact Assessment stage with the 3 solution tasks.*

> "Inside every stakeholder case, CascadeCare orchestrates UiPath's own ViVE-2026 healthcare
> solutions — Medical Records Summarization quantifies PHI exposure, Claim Denial Prevention
> protects revenue, Prior Authorization keeps care moving. CascadeCare is the crisis layer for
> the healthcare agents UiPath already ships."

### 3:20–4:00 — Reversal 4: the human gate (Action Center)
*Show: master pauses at Fiduciary Review; switch to Action Center; complete the form on camera.*

> "Day 45. Payers demand data the BAAs forbid. The **Fiduciary Conflict Detector** maps the
> three-way conflict and the case **stops for a human** — a tri-party approval in Action
> Center. I'm approving as counsel… and the case resumes. Down at the grandchild level, the
> **Classify Obligation agent** has already triaged each obligation, and its own file-or-
> withdraw human gate works the same way."

### 4:00–4:35 — Reversal 5 + closure proof
*Show: Litigation Defense stage, then Case Instances view as everything drains to Completed.*

> "Day 90. The litigation cascade lands and the **Negligent Monitoring Risk Agent** re-scores
> ClearFlow's co-defendant exposure — privilege reshuffles, the posture changes one last time.
> And then the part most case-management demos never show: **every case completes.** Master,
> six children, six grandchildren — all Completed. Even the cleanup is agentic: a fourth coded
> agent, the **Case Job Janitor**, sweeps platform job-state drift on an hourly trigger."

### 4:35–5:00 — Close (Case App / dashboard + repo)
*Show: OOTB Case App summary + sections [VERIFY on 1.0.24]; fall back to the all-Completed
heatmap if Case App isn't live. End card with repo URL.*

> "Three nested case levels, ten named agents, five goal reversals, two human gates, Trust
> Layer on every LLM call — all UiPath-native, all live on Automation Cloud, and built
> end-to-end with Claude Code. CascadeCare Network Command: the living case layer for
> healthcare financial shockwaves."

---

## Agent name checklist (all 10 must be spoken or captioned)

- [ ] Claim Flow Anomaly Detector (coded) — 0:25
- [ ] Multi-Customer Pattern Detector (coded) — 0:25
- [ ] Forensic Self-Exam Agent (coded) — 0:55
- [ ] Vector Hypothesis Agent (Agent Builder) — 0:55
- [ ] Assess Claim Disruption (Agent Builder) — 1:25
- [ ] BAA Boundary Reasoner (Agent Builder) — 1:25
- [ ] Fiduciary Conflict Detector (Agent Builder) — 3:20
- [ ] Classify Obligation (Agent Builder) — 3:20
- [ ] Negligent Monitoring Risk Agent (Agent Builder) — 4:00
- [ ] Case Job Janitor (coded) — 4:00

## Honesty guardrails

- Never say "Data Fabric drives the fan-out at runtime" — spawn identities are literal
  provider slugs (runtime `qem:` in JobArguments fails; product feedback filed).
- Context Grounding IS live (both indexes ingested + retrieval-verified 2026-06-12) — you may
  say "the BAA Boundary Reasoner retrieves each provider's BAA text from a Context Grounding
  index"; do NOT claim more than retrieval (e.g., no "fine-tuned" language).
- If a transient LLM Gateway 520 faults an agent mid-recording: `uip maestro case instance
  retry <id>` resumes the run — cut the pause in post rather than restarting.

## Post-production

- Cut to ≤5:00; speed dead air 4–8×, keep spawns/gates at 1×.
- Lower-third captions at every agent beat (checklist above).
- Separate 1-minute coding-agent reel: screen captures of Claude Code sessions
  (`docs/coding-agents/screenshots/`), narrated over the CLAUDE_CODE_USAGE.md highlights.
