# Deck Brief — CascadeCare Network Command (for Claude Cowork → UiPath AgentHack PPTX)

> **Hand this file to Claude Cowork (or any deck designer) to build the mandatory AgentHack
> submission slide deck *inside the official UiPath template*.** Everything Cowork needs is here:
> the exact UiPath design system (extracted from the real template), a slide-by-slide spec with
> final on-slide copy and verbatim speaker notes, and which template layout to use for each slide.
> The narrative is drawn from [`STORY.md`](STORY.md); the diagram walkthrough is in
> [`ARCHITECTURE-EXPLAINER.md`](ARCHITECTURE-EXPLAINER.md). **If anything here drifts from
> STORY.md, STORY.md wins.**

## ⭐ The golden rule: maintain the UiPath template design

The official template is **`docs/submission/Submission deck.pptx`** (the AgentHack-provided deck,
also at <https://bit.ly/3R0MsHU>). **Do not invent a new look.** Open that file, keep its slide
masters, layouts, colors, fonts, and the UiPath/AgentHack branding, and **replace the placeholder
text with the copy below.** This is a **light, UiPath-branded** deck — *not* the dark
"glassmorphism" of the repo dashboard. The only dark element is the architecture diagram image,
which sits on a **Dark** layout variant (the template provides them).

### How Cowork should operate on the file
1. Start from `Submission deck.pptx`. Keep theme, masters, logo, page numbers, and the title lockup.
2. The template ships **7 starter slides** in this order — reuse them, don't restyle them:
   `1 Title · 2 Team · 3 Problem statement and proposed solution · 4 Benefits and technologies
   used · 5 Solution architecture · 6 Miscellaneous (duplicate for extra content) · 7 Closing`.
3. Build the **9 slides** specified below by filling those starter slides and duplicating the
   "Miscellaneous" content slide for the three extra narrative slides. **Keep the deck under
   10 slides** (the template's own rule).
4. Put each slide's **speaker notes** verbatim into the notes field — together they are the
   3-minute finale script.
5. Export to `.pptx`, host on Google Drive/OneDrive/Dropbox with **"anyone with the link can
   view,"** and paste the link into Devpost. (Public access is a hard AgentHack requirement.)

---

## The UiPath design system (extracted from `Submission deck.pptx` — use exactly)

- **Canvas:** 16:9 widescreen, **13.32 in × 7.50 in** (the template's native size — don't resize).
- **Font:** **Calibri** for everything (headings and body). It is the template's major *and* minor
  font. Do not substitute.
- **Backgrounds:** light — **white `#FFFFFF`** and **off-white `#F6F6F6`**. Most slides are white.
  The template also offers **Dark** and **Teal** layout variants (see layout list) for emphasis.
- **Text:** near-black **`#172024`** for body/headings on light slides; **white `#FFFFFF`** on the
  Dark/Teal variants; secondary gray **`#9D9D9D`**.
- **Accent palette (UiPath brand — reuse consistently):**
  | Role | Hex | Use for |
  |---|---|---|
  | **UiPath orange (primary)** | **`#FA4616`** | titles' accent rule, key numbers, the one highlight per slide, CTAs |
  | Teal | `#1E6482` | secondary headings, section dividers |
  | Cyan | `#0BA2B3` | coded-agent / technical callouts |
  | Purple | `#8B288A` | low-code agent callouts |
  | Maroon | `#A32200` | risk / "the gap" emphasis |
  | Coral | `#FA7678` | soft highlight, chips |
  | Link cyan | `#5BCBDE` | hyperlinks |
- **Furniture (keep the template's):** UiPath logo + "AgentHack" lockup where the template places
  them; **slide numbers** bottom corner; a thin **orange `#FA4616`** accent rule under titles.
- **Layouts available in the template** (call them by name when building):
  `Title Slide · Section Header · Title and Content (+ Dark / + Teal) · Headline only (+ Dark /
  + Teal) · Statement · Slide with logo (+ Dark / + Teal) · Comparison · Quote · Content with
  photo · Thank You`.
- **Hero asset:** [`docs/images/architecture.png`](../images/architecture.png) — the architecture
  diagram. It is **dark**, so place it on a **"Title and Content Dark"** (or "Headline only Dark")
  layout so it sits cleanly. It is a **schematic — never label it a screenshot.**
- **Tone:** confident, concrete, honest. No clip-art, no stock "AI brain" images, no emoji on
  slides. One idea and one orange highlight per slide.

> **Palette note:** the *deck chrome* uses the UiPath brand colors above. The *embedded
> architecture image* keeps its own palette (it's a picture) — that's expected and fine.

---

## Length / pacing
**9 slides** (under the 10-slide cap) ≈ a **3-minute** spoken present (finale = 3-min present +
4-min demo + 3-min Q&A). Slides 1–4 set up the *story* (~75s), 5–8 are the *proof* (~90s),
9 is the *close* (~15s + Q&A). Judges may also score on the deck **alone**, so every slide must
stand without narration.

---

# The deck — slide by slide

> Format per slide: **template layout → slide title → on-slide copy (final words) → speaker notes
> (verbatim) → visual → design notes.** Copy is final text; paste it as-is.

## Slide 1 — Title  ·  *layout: Title Slide*
- **Title:** **CascadeCare Network Command**
- **Subtitle / tagline:** *The living case layer for healthcare financial shockwaves — a UiPath
  Maestro Case, live on Automation Cloud.*
- **On slide:** keep the template's "UiPath AgentHack · Build the AI agents of tomorrow" lockup.
  Add a small chip row: `Track 1 · UiPath Maestro Case` · `Live on Automation Cloud` ·
  `Built with Claude Code`.
- **Notes:** "CascadeCare Network Command — a UiPath Maestro Case for Track 1, running live on
  Automation Cloud, built end to end with Claude Code."
- **Visual:** the template's title styling; optionally a dimmed crop of the architecture spine.
- **Design:** UiPath orange `#FA4616` on the project name accent rule; Calibri; light background.

## Slide 2 — Team & Project  ·  *layout: the template's team slide*
- **On slide:** `[HUMAN: team members — name · role · email for each]`. **Project title:**
  CascadeCare Network Command. **Track:** Track 1 · UiPath Maestro Case.
- **Notes:** "We're [team] — and our project is CascadeCare Network Command, in the Maestro Case
  track."
- **Visual:** the template's team layout, unchanged.
- **Design:** keep the template's placeholders' styling; just swap names/roles.

## Slide 3 — Problem & Solution  ·  *layout: Problem statement and proposed solution*
- **Problem (left):** *"UiPath just shipped healthcare AI agents — Medical Records Summarization,
  Claim Denial Prevention, Prior Authorization. Each does one job, for one provider, in
  isolation."* **Why it matters:** *"When a payment-network cyberattack freezes claims across six
  hospital systems at once, those soloists aren't enough — there's no conductor deciding which
  agent runs, for which provider, in what order, under which legal rule. Today that's a manual
  war room: 3 agents × 6 providers = 18 disconnected runs, no shared state, no SLA clock, no legal
  layer, no human gates, no audit."*
- **Solution (right):** *"CascadeCare is the UiPath Maestro Case that conducts those agents through
  the crisis. One living case file orchestrates the whole 90-day response — UiPath-native, the
  case canvas **is** the orchestrator (no external harness)."* **What makes it unique:** *"It
  reshapes itself as the crisis evolves (5 reversals), nests 3 levels deep, and produces a
  tamper-evident audit record — an orchestration pattern, not a linear workflow."*
- **Notes:** "UiPath named the product *Maestro* for a reason: the agents are the musicians, the
  Maestro is the conductor. We didn't build a better agent — we built the thing that makes
  UiPath's agents work as a team when a crisis hits."
- **Visual:** left/right split; three small soloist chips (Medical Records / Claim Denial / Prior
  Auth) on the Problem side; one orange "conductor" bar on the Solution side.
- **Design:** maroon `#A32200` for the "18 disconnected runs" pain stat; UiPath orange `#FA4616`
  for the one-line solution claim.

## Slide 4 — Solution architecture  ·  *layout: Title and Content **Dark** (hosts the dark image)*
- **Title:** **One living case file — the whole crisis in one picture**
- **On slide:** full-bleed [`docs/images/architecture.png`](../images/architecture.png). Minimal
  overlay caption: *"One evolving Maestro Case · 3 nested levels · 12 agents · every LLM call
  governed by the Trust Layer."*
- **Notes:** "Here's the whole system. The Maestro Case canvas *is* the orchestrator — no external
  harness. Across the top, the master case walks itself through seven stages; agents plug into
  each stage; it fans out to 13 nested cases; two human gates; and the data, integration, and
  surfaces underneath. A plain-language walkthrough is in our ARCHITECTURE-EXPLAINER."
- **Visual:** the architecture diagram, full-bleed on a Dark layout.
- **Design:** Dark layout so the dark schematic sits cleanly; white Calibri caption; orange
  underline on the title. **Label it a schematic, not a screenshot.**

## Slide 5 — The hero moment: one subpoena, 13 cases  ·  *layout: Miscellaneous (duplicate) / Statement*
- **Title:** **Reversal 3 — the master fans out**
- **On slide:** *"Day 30: a state insurance-regulator subpoena. The master spawns **6 stakeholder
  cases at once**, each spawns an obligation case → **13 live case instances, 3 levels of native
  nesting.**"* Sub-line: *"Six providers, six lawful answers, one subpoena — a legal-reasoning
  agent grounds each answer in that provider's actual Business Associate Agreement via Context
  Grounding."* Small strip: the **5 reversals** (Day 1 correlate → Day 5 vector cleared → Day 30
  fan-out → Day 45 fiduciary human gate → Day 90 co-defendant), noting *the case can re-open a
  settled stage at Reversal 5.*
- **Notes:** "This is the money shot — six cases land on the canvas simultaneously, each with its
  own obligation child: thirteen coordinated instances, three levels deep. And five times across
  the crisis, new information changes the goal and the case re-routes itself — even reopening a
  settled stage."
- **Visual:** the fan-out region of the diagram, **or** `[capture: Case Instances view showing the
  6-way fan]` from [`SCREENSHOT-SHOTLIST.md`](SCREENSHOT-SHOTLIST.md) (shot 2).
- **Design:** big orange `#FA4616` "13" as the focal number; keep one idea on the slide.

## Slide 6 — 12 agents, governed, with humans in the loop  ·  *layout: Title and Content / Comparison*
- **Title:** **A governed, multi-framework agent layer — and humans where it counts**
- **On slide (left):** *"**12 agents** — 6 Agent Builder (Claude Sonnet 4.6 BYO-LLM) + 6 Coded
  (Python SDK), **two LangGraph `StateGraph`** agents via `uipath-langchain`. Every LLM call →
  UiPath LLM Gateway → Trust Layer (PHI/PII guardrails). PHI never leaves the governance
  boundary."*
- **On slide (right):** *"**2 human gates.** At Reversal 4, a three-way legal conflict stops the
  case for a human ruling — recorded with who / why / when, and **read downstream** to reshape the
  litigation posture. Both Approve and Deny advance — the decision is *data*, not a rewind."*
- **Notes:** "Twelve agents across two frameworks, and crucially every single LLM call routes
  through UiPath's Trust Layer. And we keep humans accountable for the calls a machine shouldn't
  make alone — here the human's ruling literally changes the downstream response, and the case
  records it."
- **Visual:** agent roster grid (violet = low-code, cyan = coded, ⚡ = LangGraph) + amber Trust
  Layer bar; on the right, `[capture: Action Center fiduciary gate form]` (shot 3).
- **Design:** purple `#8B288A` for low-code, cyan `#0BA2B3` for coded; orange `#FA4616` for the
  Trust Layer headline.

## Slide 7 — Benefits & technologies used  ·  *layout: Benefits and technologies used*
- **On slide (fill the template's fields):**
  - **End-user:** healthcare payment-network operations, compliance, and legal teams.
  - **User department:** crisis/incident response, fiduciary & regulatory operations.
  - **Industries:** healthcare; payment intermediaries / clearinghouses.
  - **UiPath products used:** Maestro Case · Maestro BPMN · Maestro Flow · Agent Builder · Coded
    Agents · Integration Service · Data Fabric · Context Grounding · Action Center · Apps · LLM
    Gateway · Trust Layer · AI Trust Layer governance — **13 product surfaces, 38 artifacts.**
  - **Other integrations / tech:** Python SDK, **LangGraph** via `uipath-langchain`, Claude Sonnet
    4.6 BYO-LLM, 19 Integration Service API Workflows (CNCF Serverless), built with **Claude Code**.
  - **Benefits, impact & outcomes:** *"Turns a manual multi-stakeholder war room into one auditable
    case. Fails safe — agents degrade instead of crashing, the case never stalls, and **master + 6
    children + 6 grandchildren all reach Completed.** Produces survey-grade audit + SLA-timeliness
    evidence (the record accreditors look for). Adoptable with a connector swap."*
- **Notes:** "Thirteen UiPath products, thirty-eight artifacts. Crisis software is judged by what
  it does when things break: when the Gateway fails, the forensic agent surfaces the error and
  still routes correctly — the case keeps moving. And the part most demos never show: every case
  completes, each with a full audit trail."
- **Visual:** the template's structured fields; a small "all Completed" proof badge or
  `[capture: all-Completed Case Instances]` (shot 6).
- **Design:** keep the template's field layout; orange `#FA4616` on the "all Completed" outcome.

## Slide 8 — Adoptable tomorrow + built with a coding agent  ·  *layout: Miscellaneous (duplicate)*
- **Title:** **The crisis orchestrator for the agents UiPath already ships**
- **On slide (left — vertical bridge):** *"Inside each stakeholder case, CascadeCare invokes
  UiPath's ViVE-2026 agents — Medical Records Summarization · Claim Denial Prevention · Prior
  Authorization. In the demo these are API-workflow mocks; swapping in the live solutions is a
  connector change, not a redesign."*
- **On slide (right — built with Claude Code, +2 bonus):** *"Claude Code authored **every one of 38
  UiPath artifacts** and every test, test-first — the +2 coding-agent bonus. **Above & beyond:** we
  packaged our hardest-won UiPath discoveries into **Maestro Case Kit** — an open-source, offline
  CLI + MCP server + agent skills (`pip install maestro-case-kit`) UiPath could dogfood."*
- **Notes:** "This isn't a science project — it's the missing coordination layer over the agents
  UiPath just launched, and it produces the accreditation-grade record their customers are audited
  against. And the whole thing was built with Claude Code under a test-gated workflow — which also
  shipped reusable open-source tooling for Maestro Case itself."
- **Visual:** the vertical-bridge bar + three ViVE chips (left); a terminal mock of
  `maestro-case explain 400300` + the PyPI badge (right).
- **Design:** cyan `#0BA2B3` for the tooling callout; orange `#FA4616` for "+2 bonus".

## Slide 9 — Why it wins / Closing  ·  *layout: Thank You / Closing*
- **On slide:** five compact ticked rows (one per Phase-1 criterion, from [`STORY.md`](STORY.md) §12):
  **Business Impact**, **Platform Usage**, **Technical Execution**, **Completeness**, **Creativity**.
  Closing line: **"The crisis is the demo. The orchestration pattern is the product."**
  Footer links: `[HUMAN: GitHub repo]` · `[HUMAN: live dashboard]` · `[HUMAN: demo video]`.
- **Notes:** "Three nested case levels, twelve agents, five reversals, two human gates, thirteen
  product surfaces, governed end to end — live, and built with Claude Code. CascadeCare is the
  crisis orchestrator for the healthcare agents UiPath already ships."
- **Visual:** the template's closing layout; a small architecture thumbnail + the "all Completed"
  badge.
- **Design:** UiPath orange `#FA4616` on the closing line; keep the template's Thank-You styling.

---

## Appendix — facts to keep exact (do not drift)
- **Live deploy:** `clearflow-solution` **1.0.35** → `Shared/CascadeCare-v110`; full cascade
  Completed (preserved runs `CFCS-67730745`, `CFCS-67767069`). Dashboard Coded Web App **v1.0.15**.
- **Counts:** **12 agents** (6 Agent Builder + 6 Coded; **2 LangGraph**), **38 runtime artifacts**,
  **13 UiPath product surfaces**, **5 reversals**, **3 case levels**, **13 live instances** at
  fan-out, **2 HITL gates**, **19 API Workflows**, **768 offline tests**.
- **Architecture image:** `docs/images/architecture.png` — schematic, *not* live footage; never
  label it a screenshot. Plain-language walkthrough: [`ARCHITECTURE-EXPLAINER.md`](ARCHITECTURE-EXPLAINER.md).
- **Honesty guardrails (see [`STORY.md`](STORY.md) §13):** no runtime `qem:` fan-out (spawn ids are
  literal slugs); **Deny advances, it does not rewind**; ViVE agents are **mocks** in the demo; do
  **not** claim "implements NCQA / Joint Commission compliance" (we produce the *evidence* they
  look for); **no accreditation clause numbers** on slides; only the committed fictional names.
- **Screenshots:** drop real captures where a slide says `[capture: …]` — see
  [`SCREENSHOT-SHOTLIST.md`](SCREENSHOT-SHOTLIST.md).

## Design-fidelity checklist (Cowork: verify before export)
- [ ] Built **inside** `Submission deck.pptx`; template masters/layouts/logo/page-numbers intact.
- [ ] **Calibri** throughout; light backgrounds; **UiPath orange `#FA4616`** as the one accent.
- [ ] Architecture diagram sits on a **Dark** layout; labeled a schematic.
- [ ] **≤ 10 slides** (this spec is 9). One idea + one orange highlight per slide.
- [ ] Speaker notes pasted verbatim (the 3-minute script).
- [ ] All counts match the appendix; no honesty-guardrail violations; no forbidden names.
- [ ] Exported `.pptx` hosted with public "anyone with the link can view"; link in Devpost.
