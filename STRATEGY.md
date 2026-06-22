---
name: CascadeCare Network Command
last_updated: 2026-06-22
---

# CascadeCare Network Command Strategy

## Target problem
Healthcare payment intermediaries hit by a multi-provider cyberattack face a coordination
collapse: anomaly detectors fire, but nothing tracks 37+ legal obligations across 6
providers over 90 days, enforces SLAs, routes human decisions only where required, and
produces an auditable case record.

## Our approach
Use UiPath Maestro Case as the native crisis orchestrator — three levels of nested cases,
five goal reversals with targeted stage re-entry, and autonomous agent-driven progression —
so the incident command structure reflects real crisis behavior without bespoke orchestration
code, and every LLM call flows through the UiPath Trust Layer by default.

## Who it's for
**Primary:** UiPath AgentHack judges and healthcare automation buyers evaluating Maestro
Case's capability ceiling.
**Secondary:** UiPath's healthcare vertical sales team.

## Judging criteria (max 27 pts)
| # | Criterion | Weight | Current state |
|---|---|---|---|
| C1 | Originality, creativity, real-world applicability | 1–5 | ✅ Strong |
| C2 | Orchestration & agent collaboration | 1–5 | ✅ Strong (3-level nesting) |
| C3 | Exception, failure, edge-case handling | 1–5 | ✅ Shipped — four-layer defense-in-depth; forensic silent-error fixed test-first |
| C4 | UiPath component variety | 1–5 | ✅ Strong — 13-surface component inventory in README |
| C5 | Presentation quality (video + deck + Devpost) | 1–5 | ⚠ In progress — Devpost copy + deck brief drafted; demo video pending (human) |
| +2 | Coding agent bonus (Claude Code docs in Devpost) | +2 | ✅ Documented — `CODING_AGENTS.md` + `CLAUDE_CODE_USAGE.md` |

**Strong submission signals (UiPath guidance):** Intelligent exception/edge-case handling ·
Visibility into case status · Clear auditability · Meaningful human oversight.

## Prize landscape
_Verified 2026-06-16 from https://uipath-agenthack.devpost.com/rules (full $50,000 / 3-track structure)._
_The 2025 "$10K Agent of the Future" / "Specialist Coded Agent Challenge" are CLOSED 2025 events — NOT in 2026._

| Prize | Amount | Status / target | Notes |
|---|---|---|---|
| Grand Prize | $8,000 | aspirational | best overall (replaces 2025 "$10K Agent of the Future") |
| **Best of UiPath Maestro Case — OUR TRACK** | $5,000 | **primary target** | Runner-up $3,000 · Honorable Mention $2,000 |
| Most Creative Solution | $3,000 | special award — in reach | regulated-vertical originality |
| Best Demo / Presentation | $3,000 | special award — in reach | needs the ≤5-min live video |
| Best Cross-Platform Integration | $1,500 | special award — in reach | ViVE bridge + multi-product surfaces |
| Best First-Time Builder | $1,500 | special award — check eligibility | first-time-entrant constraint |
| **Best Product Feedback** | $1,500 | DRAFTED → submit | individual award; `docs/submission/PRODUCT-FEEDBACK.md`; **closes Jul 2** |
| **People's Choice** | $500 × 3 | forum/social push | community vote **Jul 3–30**; standalone (any participant) |
| Coding-agent bonus | +2 pts | documented | within Platform Usage; lifts max score to 27 |

**Rules that shape strategy:** a project can win **at most 2 prizes** — one Overall/Track prize **+** one Special
Award. Best Product Feedback is an *individual* award and People's Choice is *standalone* (any participant,
regardless of finalist status), so both likely stack on top of the project cap. **Deadlines (all EDT):** main
submission **Jun 29 11:45 PM** · product-feedback form **Jul 2 11:45 PM** (earlier — don't miss it) · People's
Choice voting **Jul 3–30**. The `forms.office.com/e/KitjGLF5k1` feedback URL is unverified for 2026 — a human
must click it to confirm it's the current form (Devpost doesn't publish the URL publicly).

## Key metrics
- End-to-end run completion rate (✅ v1.0.32 live-proven)
- HITL branch fidelity — Reversal-4 fiduciary gate Approve + Deny paths
- Context Grounding retrieval relevance (BAA-corpus)
- Criterion-3 evidence visible in demo (retry badge, forensic agent output, Faulted recovery)
- Demo wall-clock runtime (≤5 minutes)
- Judging outcome (Jun 3–Jul 14 2026)

## Priority action list
Ordered by impact × effort (see `docs/ideation/agentHack-judging-gaps-2026-06-15.html` for full ranked list).

### Tier 1 — Do immediately (zero/near-zero code)
1. ✅ **DONE (2026-06-15)** — **Fix forensic agent silent error**: `enrich_node` now populates `error_type`/`error_message` on failure (never swallows, never faults the graph, routing untouched). TDD red→green; full suite 680 passed; `mypy src/` clean. Working tree, uncommitted.
2. **Product feedback form** — https://forms.office.com/e/KitjGLF5k1 — $1,500, 15 min (human task)
3. **Email judge access** — andreea.tomescu@uipath.com (judging prerequisite, human task)
4. ~~Configure Maestro element-level retry on the forensic task~~ — **CORRECTED 2026-06-15: not applicable.** Element-level auto-retry is a Maestro **Process (BPMN)** feature; Maestro **Case** agent tasks do not expose it (verified in Studio Web). The forensic case task's resilience is case-native instead — see the corrected layers in [`docs/MAESTRO-RETRY-CONFIG.md`](docs/MAESTRO-RETRY-CONFIG.md). No action needed here.
5. **Pre-answer gate-delete gotcha** — add "Known Edge Cases" section to Devpost: gate deletion → Faulted + ErrorCode 160009, intentional incident recording

### Tier 2 — This week (documentation & submission)
6. **Coding agent bonus docs** — `CODING_AGENTS.md` + Devpost section with Claude Code screenshots → unlocks the **+2 coding-agent bonus** (max score 27; document the tool, its contribution, and verifiable evidence)
7. **docs/evidence/ screenshot set** — 6+ annotated screenshots from live v1.0.35 runs (retry badge, forensic output, HITL gate, fan-out, closure, Faulted case)
8. **Demo script rewrite (Crisis-First)** — open on Faulted case → CVR-frame Reversal-3 fan-out → WHO Surgical Timeout at HITL gate → completion
9. **Rubric-mapping Devpost editorial** — label every Devpost paragraph with C1–C5 criterion; cut anything unmapped
10. **UiPath components table** — add to README.md (Criterion 4 direct)
11. **Dashboard "Audit Trail" reframe** — rename panel, add HIPAA/SOC-2 framing
12. **ICS-214 decision log** — generate from live run data via `demo_autocomplete.py`, format as timestamped attributed log

### Tier 3 — This week (prizes & completeness)
13. **Forum community post** — UiPath Community Forum, before July 3, seeds People's Choice votes
14. ~~**Specialist Coded Agent submission**~~ — RESOLVED 2026-06-16: not a 2026 prize (closed 2025 event); the coding-agent value is the +2 bonus (item 6)
15. **Prompt logs in Devpost** — include 2 `agents/prompts/*.md` files as Trust Layer architecture evidence
16. **90-second Criterion-3 exhibit video** — standalone clip: Faulted → forensic agent → recovery

### Tier 4 — Only if time permits
17. Chaos Monkey mock-520 injection during demo (live recovery; requires demo stability)
18. Deny branch as a demo beat — human Deny is recorded (`reviewerDecision`) and consumed by the R5 posture agents; both gate outcomes advance the case (data-driven, NOT a stage rework — corrected 2026-06-15)

## Tracks

### Case architecture
Three-level Maestro Case nesting: `clearflow-master-crisis` → `clearflow-stakeholder-parent`
(~9) → `clearflow-obligation-grandchild` (~12). Five goal reversals; the Reversal-5 co-defendant
beat re-opens the Multi-Customer Investigation stage via a `return-to-origin` exit (targeted
re-entry). Hero moment at Reversal 3 (Day 30): 6 grandchild spawns fan out on the canvas.

### Agent layer (6 Coded + 6 Agent Builder = 12; see README "Agent inventory" table)
- 6 Coded Agents (Python SDK, UiPath LLM Gateway / Trust Layer):
  - `claim-flow-anomaly-detector` — classifies payment anomalies (deterministic + advisory enrich)
  - `multi-customer-pattern-detector` — cross-provider pattern analysis
  - `forensic-self-exam-agent-langgraph` — **LIVE** LangGraph StateGraph routing (Vector Isolation `tFSEXam01`)
  - `forensic-self-exam-agent` — original Python-SDK forensic agent, superseded by the LangGraph version
  - `case-job-janitor` — ops utility; hourly trigger, sweeps zombie Orchestrator jobs (not in any caseplan)
  - `audit-ledger-writer-langgraph` — Coded **LangGraph Agent** (`uipath-langchain`); wired **in-case** at the master's Closed stage (task `tALWdgr01`), writes immutable, idempotent, queryable `AuditRecord` rows to Data Fabric live during the run (6 per run) — a survey-ready compliance ledger complementing Maestro's Action History. Live-proven 1.0.34 (run `CFCS-67730745`)
- 6 Agent Builder agents (low-code, **Claude Sonnet 4.6 BYO-LLM** via UiPath LLM Gateway):
  - `baa-boundary-reasoner` — Context Grounding on BAA-corpus; PHI/PII compliance routing (R3)
  - `vector-hypothesis-agent` — attack-vector hypothesis (Vector Isolation)
  - `fiduciary-conflict-detector` — tri-party conflict → HITL gate payload (R4)
  - `negligent-monitoring-risk-agent` — co-defendant exposure (R5)
  - `assess-claim-disruption` — per-provider disruption + liquidity (stakeholder-parent)
  - `classify-obligation` — obligation classification (obligation-grandchild)

### Vertical bridge
CascadeCare demonstrates Maestro Case orchestrating UiPath's own ViVE-2026 Healthcare
Agentic Solutions (Medical Records Summarization, Claim Denial Prevention, Prior Auth)
as sub-agents. Positions ClearFlow as the Maestro layer above UiPath's own solutions.

### LangGraph agent conversion
`forensic-self-exam-agent-langgraph` converted to LangGraph/LangChain running on the
UiPath Python SDK — demonstrates Maestro Case is framework-agnostic at the agent layer.
LangGraph conditional graph expresses routing logic with typed edges and LLM-enriched
narration as a graph node. Live-proven in v1.0.32 (job 26c32c0a Successful).

### Exception resilience (Criterion 3 focus) — case-native defense-in-depth
- **Layer 1 (in-agent):** forensic agent catches LLM/enrichment failures, surfaces `error_type`/`error_message`, degrades gracefully without faulting (shipped 2026-06-15)
- **Layer 2 (targeted re-entry):** `return-to-origin` re-opens the Multi-Customer Investigation stage at Reversal 5, re-running only the cross-provider correlation (`shouldRunOnlyOnce` skips settled work) — already in the caseplan
- **Layer 3 (SLA escalation):** `slaRules` → `escalationRule` notifications on breach/at-risk (already in the caseplan)
- **Layer 4 (instance retry):** operator `uip maestro case instance retry` for persistent faults
- NOTE: Maestro **Case** agent tasks do NOT have BPMN-style element-level auto-retry (verified 2026-06-15); see `docs/MAESTRO-RETRY-CONFIG.md`
- Structured error output from all Coded Agents (error_type, error_message fields)
- HITL gate: Approve and Deny both advance the case identically; the decision is **data-driven** (`reviewerDecision` consumed by R5 posture agents) and recorded as an auditable ruling — NOT a stage rework (corrected 2026-06-15)
- Gate-delete → Faulted + ErrorCode 160009 pre-disclosed in Devpost
- Forensic agent self-exam fires on each case run to route based on system state

## Milestones
- 2026-06-15 — v1.0.32 live end-to-end proven (all 3 levels + closure + HITL gate)
- 2026-06-15 — LangGraph swap shipped (forensic-self-exam-agent-langgraph, commit 141eea0)
- 2026-06-22 — Target: Tier 1+2 actions complete, video recorded, Devpost draft ready
- 2026-06-29 — AgentHack 2026 submission deadline (11:45 PM EDT)
- 2026-07-03 — People's Choice voting opens (forum post needed before this date)
- 2026-07-14 — Finalist judging window closes

## Not working on
- A live Python/LangGraph runtime harness replacing Maestro Case canvas
- Real patient/company/litigation references
- General-purpose crisis platform
- Non-UiPath orchestration at the case layer
- Any feature not tied to a specific judging criterion or prize
