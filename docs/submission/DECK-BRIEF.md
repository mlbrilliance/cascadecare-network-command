# Deck Brief — CascadeCare Network Command (for Claude cowork → PPTX)

> **Hand this file to Claude cowork (or any deck designer) to build the mandatory AgentHack
> submission slide deck.** It is a complete, slide-by-slide spec: every slide has a title, the
> one key message, the on-slide content, speaker notes, and the visual to use. The narrative is
> drawn from [`STORY.md`](STORY.md) — if anything here drifts from STORY.md, STORY.md wins.

## How to use this
1. Build **~14 slides** in 16:9. Keep them visual — judges skim. One idea per slide.
2. Use the **design system** below for a consistent, modern, "glassy" look that matches the
   repo's architecture diagram and live dashboard.
3. Put the **speaker notes** verbatim into each slide's notes field (they're the 3-minute
   finale script).
4. Export to `.pptx`, then host on Google Drive/OneDrive/Dropbox with **"anyone with the link
   can view"** (a hard AgentHack requirement) and paste the link into Devpost.

## Design system
- **Theme:** dark "glassmorphism" — deep charcoal-navy background (`#0B1020`→`#070A12`), frosted
  translucent cards with soft glows, thin glowing borders. Matches `docs/images/architecture.png`.
- **Accent palette (semantic, reuse consistently):** orange `#FF9A5C` = Maestro Case /
  orchestration; violet `#9D8CF0` = Agent Builder (Claude Sonnet 4.6); cyan `#4FD0F5` = Coded
  Agent (Python SDK); green `#43D49A` = platform/healthy; gold `#F6C04A` = human gate; amber
  `#F6B73C` = Trust Layer.
- **Text:** light `#EAF2FF` headings, muted `#9FB2CC` body. Font: Segoe UI / Inter / Helvetica.
- **Furniture:** small "Track 1 · Maestro Case" chip top-right on every slide; slide number
  bottom-right; a thin orange accent rule under each title.
- **Hero asset:** `docs/images/architecture.png` (the glassy architecture diagram) — full-bleed
  on the architecture slide. Other suggested visuals are noted per slide; replace any "[capture]"
  with a real screenshot from `SCREENSHOT-SHOTLIST.md` where available.
- **Tone:** confident, concrete, honest. No clip-art. No stock "AI brain" images.

## Length / pacing
14 slides ≈ a 3-minute spoken present (the finale is 3-min present + 4-min demo + 3-min Q&A).
Slides 1–5 are the *story* (≈90s), 6–11 the *proof* (≈75s), 12–14 the *close* (≈15s + Q&A).

---

## Slide 1 — Title
- **Key message:** This is a UiPath Maestro Case, live on Automation Cloud.
- **On slide:** "CascadeCare Network Command" · tagline *"The living case layer for healthcare
  financial shockwaves"* · chips: `Track 1 · UiPath Maestro Case`, `Live on Automation Cloud`,
  `Built with Claude Code`. Small: "AgentHack 2026".
- **Visual:** a tight crop of the architecture diagram's orchestration spine as the backdrop,
  dimmed.
- **Notes:** "CascadeCare Network Command — a UiPath Maestro Case for Track 1, running live on
  Automation Cloud."

## Slide 2 — The hook: healthcare is UiPath's 2026 bet
- **Key message:** UiPath just shipped healthcare agents — but they're soloists.
- **On slide:** "Healthcare is UiPath's #1 vertical for 2026." Three cards: **Medical Records
  Summarization**, **Claim Denial Prevention**, **Prior Authorization** (the ViVE-2026 agents).
  Caption: *"Each does one job, for one provider, in isolation."*
- **Visual:** three glassy agent cards (cyan/violet), spaced apart (visually "soloists").
- **Notes:** "At ViVE 2026, UiPath launched agentic healthcare solutions. They're great — but
  each does one job, for one provider, in isolation."

## Slide 3 — The gap: who conducts them in a crisis?
- **Key message:** A multi-stakeholder crisis needs a conductor; nothing fills that role today.
- **On slide:** Big question: *"When a crisis hits six hospitals at once — who decides which
  agent runs, for which provider, in what order, under which legal constraint?"* Below, the
  ugly status quo: "3 agents × 6 providers = **18 disconnected runs.** No shared state. No SLA
  clock. No legal layer. No human gates. No audit."
- **Visual:** 18 faint scattered nodes with no connections (chaos), vs. a single conductor
  silhouette implied.
- **Notes:** "On the worst day in healthcare operations, those soloists aren't enough. Today
  there's no conductor — just a manual war room."

## Slide 4 — The unlock: Maestro is the conductor
- **Key message:** UiPath named it "Maestro" for a reason; CascadeCare is the conductor under fire.
- **On slide:** *"The agents are the musicians. The Maestro is the conductor. CascadeCare is the
  conductor leading the orchestra through the hardest piece — a live crisis where the score
  keeps changing."* One line: **"We didn't build a better agent. We built the thing that makes
  UiPath's agents work as a team."**
- **Visual:** the same 3 agent cards from slide 2, now wired under one orchestrating "Maestro
  Case" bar (orange) — soloists → orchestra.
- **Notes:** Deliver the conductor metaphor. This is the slide that makes the whole thing click.

## Slide 5 — The proving ground: the hardest crisis in healthcare
- **Key message:** We picked the hardest realistic crisis on purpose — it's the stress test.
- **On slide:** "A payment-network cyberattack freezes claims across six hospital systems —
  the most consequential class of healthcare cyber event of the mid-2020s." Then: *"Orchestration
  only proves its worth under exceptions and change. The crisis is the stress test — passing it
  is the proof."* Protagonist: **ClearFlow Health Network (fictional)** — the payment
  intermediary in the middle.
- **Visual:** a timeline ribbon Day 1 → Day 90 with the 5 reversal markers.
- **Notes:** "We didn't invent drama for its own sake — a happy-path workflow wouldn't need
  Maestro Case. A crisis is exactly where case management earns its keep."

## Slide 6 — The solution in one picture (ARCHITECTURE — hero slide)
- **Key message:** One living case file orchestrates the whole crisis, UiPath-native.
- **On slide:** full-bleed `docs/images/architecture.png`. Minimal text overlay: "One evolving
  Maestro Case · 3 nested levels · 12 agents · governed by the Trust Layer."
- **Visual:** the architecture diagram itself (already on-brand).
- **Notes:** "Here's the whole system. The Maestro Case canvas *is* the orchestrator — no
  external harness. Master crisis case at the top, agents plugged into stages, the data and
  integration foundation below."

## Slide 7 — The hero moment: Reversal 3 fan-out
- **Key message:** A subpoena makes the master fan out 13 coordinated cases, three levels deep.
- **On slide:** "Day 30 — a state insurance-regulator (DOI) subpoena. The master spawns **6
  stakeholder cases at once**, each spawns an obligation case → **13 live case instances, 3
  levels of native nesting.**" Sub-line: *"Six providers, six lawful answers, one subpoena — a
  legal-reasoning agent grounds each in that provider's actual business-associate agreement
  (BAA)."*
- **Visual:** the fan-out portion of the diagram, or `[capture: Case Instances view showing the
  6-way fan]` from the shot-list.
- **Notes:** "This is the money shot — six cases land simultaneously on the canvas, each with its
  own obligation child. Thirteen coordinated instances, three levels deep."

## Slide 8 — The case reshapes itself: 5 reversals
- **Key message:** The case re-routes *itself* as the crisis evolves — that's the orchestration.
- **On slide:** the 5-reversal table (Day 1 correlate → Day 5 vector cleared/Nimbus → Day 30
  subpoena fan-out → Day 45 fiduciary human gate → Day 90 litigation/co-defendant).
- **Visual:** the reversal timeline with the return-to-origin arc (re-opens the investigation at R5).
- **Notes:** "Five times, new information changes the master goal, and the case re-routes itself —
  including re-opening a settled stage at Reversal 5."

## Slide 9 — 12 agents, 2 frameworks, all governed
- **Key message:** A multi-framework agent layer, every call through the Trust Layer.
- **On slide:** "**12 agents** — 6 Agent Builder (Claude Sonnet 4.6 BYO-LLM) + 6 Coded (Python
  SDK), two **LangGraph `StateGraph`** agents via `uipath-langchain`." Banner: *"Every LLM call →
  UiPath LLM Gateway → Trust Layer (PHI/PII guardrails). PHI never leaves the governance
  boundary."*
- **Visual:** agent roster grid colored by type (violet/cyan), with the amber Trust Layer bar.
- **Notes:** "Twelve agents across two frameworks — and crucially, every single LLM call routes
  through UiPath's Trust Layer."

## Slide 10 — Humans stay accountable (2 HITL gates)
- **Key message:** The machine escalates the calls a machine shouldn't make alone — and the
  ruling is consumed downstream.
- **On slide:** "Two human gates. At Reversal 4, a three-way legal conflict stops the case for a
  human ruling — recorded with *who / why / when*, and **read downstream** to reshape the
  litigation posture (cooperative vs. contesting). *Both Approve and Deny advance — the decision
  is data, not a rewind.*"
- **Visual:** `[capture: Action Center fiduciary gate form]` from the shot-list.
- **Notes:** "Judges specifically reward keeping humans accountable for high-impact decisions —
  here the human's ruling literally changes the downstream response, and the case records it."

## Slide 11 — Fails safe + every case completes (Criterion 3)
- **Key message:** Agents degrade instead of crashing; the case never stalls; everything completes.
- **On slide:** the 4-layer exception model (in-agent graceful degradation → structured coded
  errors → case-native SLA/escalation + re-entry → operator retry + audit). Big proof line:
  **"Master + 6 children + 6 grandchildren — all Completed."**
- **Visual:** `[capture: all-Completed Case Instances heatmap]` from the shot-list.
- **Notes:** "Crisis software is judged by what it does when things break. When the Gateway
  fails, the forensic agent surfaces the error and still routes correctly — the case keeps
  moving. And the part most demos never show: every case completes."

## Slide 12 — The vertical bridge: adoptable tomorrow
- **Key message:** This is the crisis orchestrator for the agents UiPath already ships.
- **On slide:** "Inside each stakeholder case, CascadeCare invokes UiPath's ViVE-2026 agents —
  Medical Records Summarization · Claim Denial Prevention · Prior Authorization." Honest note:
  *"In the demo these are API-workflow mocks; swapping in the live solutions is a connector
  change, not a redesign."* Plus the accreditation tie-in: *"The audit trail + SLA timeliness it
  produces is the survey-grade evidence The Joint Commission, NCQA, and ACHC (hospital,
  health-plan, and home-health accreditors) look for."*
- **Visual:** the vertical-bridge bar from the diagram; three ViVE solution chips.
- **Notes:** "This isn't a science project — it's the missing coordination layer over the agents
  UiPath just launched, and it produces the accreditation-grade record their customers are
  audited against."

## Slide 13 — Built with Claude Code (+2 bonus) + open-source give-back
- **Key message:** A coding agent authored 100% of it — and shipped reusable tooling for the platform.
- **On slide:** "Claude Code authored **every one of 38 UiPath artifacts** and every test,
  test-first — the +2 coding-agent bonus (max score 27)." Then: "**Above & beyond:** we extracted
  our hardest-won UiPath discoveries into **Maestro Case Kit** — an open-source, offline CLI +
  MCP server + agent skills (`pip install maestro-case-kit`) UiPath could dogfood."
- **Visual:** a terminal mock of `maestro-case explain 400300` + the PyPI badge.
- **Notes:** "Claude Code built the whole thing under a test-gated workflow — and went beyond the
  demo to ship reusable open-source tooling for Maestro Case itself."

## Slide 14 — Why it wins / close
- **Key message:** One auditable case that conducts UiPath's healthcare agents through a crisis.
- **On slide:** the 5-criteria one-liners (from STORY.md §12) as five compact rows, each ticked.
  Closing line: **"The crisis is the demo. The orchestration pattern is the product."** Footer:
  repo / live dashboard / demo-video links (`[HUMAN: paste]`).
- **Visual:** the architecture diagram thumbnail + the "all Completed" proof badge.
- **Notes:** "Three nested case levels, twelve agents, five reversals, two human gates, thirteen
  product surfaces, governed end to end — live, and built with Claude Code. CascadeCare is the
  crisis orchestrator for the healthcare agents UiPath already ships."

---

## Appendix — assets & facts to keep exact (do not drift)
- Live deploy: **`clearflow-solution` 1.0.34 → `Shared/CascadeCare-v110`**; full cascade Completed.
- Counts: **12 agents** (6 Agent Builder + 6 Coded; 2 LangGraph), **38 runtime artifacts**, **13
  UiPath product surfaces**, **5 reversals**, **3 case levels**, **13 live instances** at fan-out,
  **2 HITL gates**.
- Architecture image: `docs/images/architecture.png` (schematic — *not* live footage; never label
  it as a screenshot).
- Honesty guardrails: see [`STORY.md`](STORY.md) §13 — no runtime `qem:` fan-out; Deny advances
  (not rewinds); ViVE agents are mocks in the demo; no "implements NCQA/TJC compliance" claim; no
  unverified accreditation clause numbers on slides.
- Screenshots to drop in where a slide says `[capture: …]`: see
  [`SCREENSHOT-SHOTLIST.md`](SCREENSHOT-SHOTLIST.md).
