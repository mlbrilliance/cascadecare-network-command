---
name: CascadeCare Network Command
last_updated: 2026-06-15
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
| C3 | Exception, failure, edge-case handling | 1–5 | ⚠ Gap — forensic agent silent error; retry not yet visible |
| C4 | UiPath component variety | 1–5 | ⚠ Gap — components table missing from README |
| C5 | Presentation quality (video + deck + Devpost) | 1–5 | ⚠ Gap — video/deck/Devpost not yet created |
| +2 | Coding agent bonus (Claude Code docs in Devpost) | +2 | ⚠ Gap — unclaimed |

**Strong submission signals (UiPath guidance):** Intelligent exception/edge-case handling ·
Visibility into case status · Clear auditability · Meaningful human oversight.

## Prize landscape
| Prize | Amount | Status | Effort |
|---|---|---|---|
| Track 1 main judging | ~$TBD | In progress | 14 days |
| Specialist Coded Agent Challenge | $10,000 | Unverified eligibility | 1 day docs |
| Product feedback form | $1,500 | Not started | 15 min |
| People's Choice (community vote, Jul 3–30) | $500 | Not started | Forum post |
| Coding agent bonus | +2 pts | Not started | 4–6 hrs docs |

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
6. **Coding agent bonus docs** — `CODING_AGENTS.md` + Devpost section with Claude Code screenshots → unlocks +2 pts AND feeds Specialist Challenge ($10K)
7. **docs/evidence/ screenshot set** — 6+ annotated screenshots from live v1.0.32 runs (retry badge, forensic output, HITL gate, fan-out, closure, Faulted case)
8. **Demo script rewrite (Crisis-First)** — open on Faulted case → CVR-frame Reversal-3 fan-out → WHO Surgical Timeout at HITL gate → completion
9. **Rubric-mapping Devpost editorial** — label every Devpost paragraph with C1–C5 criterion; cut anything unmapped
10. **UiPath components table** — add to README.md (Criterion 4 direct)
11. **Dashboard "Audit Trail" reframe** — rename panel, add HIPAA/SOC-2 framing
12. **ICS-214 decision log** — generate from live run data via `demo_autocomplete.py`, format as timestamped attributed log

### Tier 3 — This week (prizes & completeness)
13. **Forum community post** — UiPath Community Forum, before July 3, seeds People's Choice votes
14. **Specialist Coded Agent submission** — verify requirements, submit 4-agent bundle
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

### Agent layer (5 Coded + 6 Agent Builder = 11; see README "Agent inventory" table)
- 5 Coded Agents (Python SDK, UiPath LLM Gateway / Trust Layer):
  - `claim-flow-anomaly-detector` — classifies payment anomalies (deterministic + advisory enrich)
  - `multi-customer-pattern-detector` — cross-provider pattern analysis
  - `forensic-self-exam-agent-langgraph` — **LIVE** LangGraph StateGraph routing (Vector Isolation `tFSEXam01`)
  - `forensic-self-exam-agent` — original Python-SDK forensic agent, superseded by the LangGraph version
  - `case-job-janitor` — ops utility; hourly trigger, sweeps zombie Orchestrator jobs (not in any caseplan)
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
