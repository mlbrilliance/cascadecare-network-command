# Telling the CascadeCare Story — Value Proposition & Narrative Playbook

> **This is the canonical source for how we explain CascadeCare** — to judges, to the
> public, in the README, in the demo video, in the deck, in the forum post. If any other
> document's pitch drifts from this one, this one wins. The goal of this doc is a single
> thing: **make the value proposition impossible to misunderstand.**

---

## 0. The problem this doc solves

CascadeCare is easy to *show* and hard to *say*. The demo is visually obvious — cases fan
out, agents fire, a human approves a gate. But when someone asks *"so… what is it, and why
does it matter?"*, the honest-but-confusing answer is "a UiPath Maestro Case that
orchestrates a fictional healthcare payment crisis with five reversals and three-level case
nesting." That sentence is **accurate and useless** — it describes the *mechanism*, not the
*value*.

The fix is to **lead with UiPath's own healthcare agents and the gap between them**, not with
the fictional crisis. The crisis is the *proving ground*; the *product* is the orchestration
pattern.

---

## 1. The pitch (memorize this)

**The literal one-breath version:**

> **CascadeCare is the UiPath Maestro Case that makes UiPath's healthcare AI agents work as a
> team when a crisis hits.**

**The full version (one idea, three beats):**

> UiPath ships healthcare AI agents that each do one job. CascadeCare is the Maestro Case that
> *conducts* them through a crisis — one living case file that runs the medical-records,
> claim-denial, and prior-auth agents across a multi-hospital payment-network attack, escalates
> the legal calls to a human, and keeps a complete audit trail of who decided what, when, and why.

And the line that makes it stick:

> **UiPath named the orchestration product "Maestro" for a reason. The agents are the
> musicians; the Maestro is the conductor. CascadeCare is what the conductor looks like
> leading the orchestra through the hardest piece there is — a live crisis where the score
> keeps changing mid-performance.**

---

## 2. The unlock: agents are soloists, Maestro is the conductor

This single metaphor de-confuses the whole project. Use it early and often.

- **UiPath's healthcare agents are soloists.** At ViVE 2026, UiPath launched its agentic
  healthcare solutions — **Medical Records Summarization, Claim Denial Prevention, Prior
  Authorization**. Each is excellent at *one job for one provider*. A soloist.
- **A crisis needs an orchestra, and an orchestra needs a conductor.** When a payment network
  goes dark across six hospital systems, you don't need a *better soloist* — you need someone
  to decide which agent plays, for which provider, in what order, under which legal
  constraints, and when to stop the music and ask a human.
- **That conductor is UiPath Maestro Case.** CascadeCare is the reference performance: it
  proves Maestro Case can conduct UiPath's own healthcare agents through a real crisis without
  missing a beat — and produce a complete record of the performance.

> The gap is **not** "we need more agents." UiPath already has the agents. The gap is **"who
> runs them together, under pressure, with a human accountable for the high-stakes calls."**
> CascadeCare is that missing layer — and it's UiPath-native, so the health vertical can adopt
> it tomorrow.

---

## 3. The three sentences that de-confuse it

If you only have 20 seconds, say these three:

1. **The problem.** When a healthcare payment network is cyber-attacked, every hospital it
   serves stops getting paid within days — and the company in the middle has to answer
   regulators, payers, and insurers *at the same time*, honoring a different confidentiality
   contract with each one.
2. **The gap.** UiPath ships agents that each handle one piece — summarize records, prevent
   claim denials, keep prior-auths moving — but nothing coordinates them across a
   multi-stakeholder crisis that changes shape over 90 days.
3. **CascadeCare.** It's the UiPath Maestro Case that *is* that coordinator: one evolving case
   file that drives the agents, tracks every legal obligation, escalates the judgment calls to
   a human, and keeps the whole thing auditable — proven live on Automation Cloud.

---

## 4. The 30-second elevator

> "Healthcare is UiPath's #1 vertical for 2026 — they just launched AI agents for medical
> records, claim denials, and prior auth. Those agents each do one job. **CascadeCare is the
> Maestro Case layer that makes them work as a team when a crisis hits.** We picked the hardest
> crisis in healthcare — a payment-network cyberattack that freezes claims across six hospital
> systems — and built a single living case that manages the whole cascade: it spawns a case per
> stakeholder and per legal obligation (three levels of native case nesting), runs eleven AI
> agents through UiPath's governed LLM Gateway, reshapes its own goal five times as the crisis
> evolves, and pauses for a human at the two decisions a machine shouldn't make alone. Every
> case completes, and every decision is recorded. It's the crisis orchestrator for the
> healthcare agents UiPath already ships."

---

## 5. The 3–4 minute spoken narrative (for the live finale / demo intro)

*This is the "what is this and why does it matter" you say before/over the demo. The finale
format is 3-min present + 4-min demo + 3-min Q&A — this is your 3-min present.*

**(0:00) Open on the stakes.**
"At ViVE this year, UiPath shipped three agents that do real clinical and billing work —
Medical Records Summarization, Claim Denial Prevention, Prior Authorization. Healthcare is
UiPath's biggest bet for 2026, and these are the tip of the spear. They're great — but each does
one job, for one provider, in isolation."

**(0:30) Name the gap.**
"Now imagine the worst day in healthcare operations: the payment network in the middle gets
cyber-attacked, and six hospital systems stop getting paid at once. This actually happened in
the mid-2020s — it's the most consequential class of healthcare cyber event on record. On that
day, those brilliant agents aren't enough. Who decides which one runs, for which hospital, in
what order? Who tracks the legal obligations to a regulator, four payers, and an insurer — each
with a different confidentiality contract? Who escalates the calls a machine shouldn't make
alone? Nobody. That's the gap."

**(1:15) Land the answer.**
"That coordinator is UiPath Maestro Case — and CascadeCare is the reference build of exactly
that. It manages the entire crisis as **one living case file.** A master crisis case spawns a
case per stakeholder, and each of those spawns a case per legal obligation — three levels of
native case nesting, all on the UiPath canvas."

**(2:00) The hero moment.**
"Watch Day 30. A state subpoena lands, and the master case fans out **six stakeholder cases at
once** — each one immediately spawns its own obligation case. Thirteen coordinated cases, three
levels deep, on one screen. Inside each, a legal-reasoning agent reads that provider's
confidentiality contract — its *business-associate agreement* — and gives a **different lawful
answer** for each provider. Six providers, six answers, one subpoena."

**(2:40) The human, and the close.**
"At Day 45 the case stops and asks a human to rule on a three-way legal conflict — and that
ruling is recorded *and read downstream*, reshaping the litigation posture. And through all of
it, every LLM call runs through UiPath's Trust Layer — so patient data never leaves the
governance boundary. Then the part most demos never show: **every case completes** — master, six
children, six grandchildren — each with a full audit trail. CascadeCare is the crisis
orchestrator for the healthcare agents UiPath already ships. It's adoptable tomorrow."

---

## 6. Why a *crisis* and not a happy path (the #1 confusion)

People ask: *"why all the drama — the reversals, the litigation, the subpoena?"* The answer is
the strongest point in the whole pitch:

> **Orchestration only proves its worth under exceptions and change.** A linear, happy-path
> workflow doesn't need Maestro Case — a simple flow would do. Case management earns its keep
> exactly when goals shift, work fans out across stakeholders, obligations conflict, and humans
> must step in. A crisis isn't gratuitous drama — **it's the stress test that proves the
> orchestration layer works.** We picked the hardest realistic healthcare crisis on purpose,
> because passing it is the proof.

And the generalization that makes it commercial:

> The *pattern* — a master case that fans out per-stakeholder and per-obligation, driven by
> governed agents with human gates and a full audit trail — is **reusable for any complex,
> exception-heavy healthcare case**: a prior-authorization appeals storm, a claim-denial
> cascade, multi-provider care coordination, a breach-notification rollout. The cyberattack is
> the demo; the pattern is the product.

---

## 7. The vertical bridge — why UiPath can adopt this tomorrow

This is the "real-world applicability / adoption potential" argument (Judging Criterion 1).

- CascadeCare doesn't *replace* UiPath's healthcare agents — **it orchestrates them.** Inside
  every stakeholder case, at the Impact Assessment stage, it invokes Medical Records
  Summarization, Claim Denial Prevention, and Prior Authorization as case tasks.
- In *this demo*, those three are represented by **API-workflow mocks** standing in for the
  ViVE products (we don't hold live licenses to them). **The orchestration pattern is real;
  swapping the mocks for the live solutions is a connector change, not a redesign.** Say it
  exactly this honestly — it's both true and compelling.
- The whole system is **UiPath-native at runtime** — the Maestro Case canvas *is* the
  orchestrator. There's no external Python harness running the show. That's what makes it
  immediately adoptable by the health vertical rather than a science project.

---

## 8. Regulatory & accreditation framing (TJC · NCQA · ACHC · HIPAA)

> **Honesty boundary first:** CascadeCare does **not** implement any accreditation standard,
> and we never claim it "ensures NCQA/Joint Commission compliance." What's true — and powerful —
> is that **the crisis it manages sits squarely inside the obligations these bodies enforce,
> and the evidence it produces is exactly what their surveyors ask for.** Use these as
> *real-world relevance and adoption framing*, not as implemented features. Per project policy,
> do **not** put specific standard code numbers on camera or in committed claims unless verified
> against a cited source — speak to *what each body governs*, not *clause X.Y.Z*.

Why this matters: it shows the judges that the scenario isn't invented drama — it lands on the
exact accountability frameworks U.S. healthcare organizations are audited against.

- **The Joint Commission (TJC)** accredits hospitals. Its **Emergency Management** and
  continuity-of-operations expectations require providers to keep operating *and documenting*
  through a disruption, and its information-management expectations treat a system-of-record as
  essential. **CascadeCare's per-provider impact assessment, obligation tracking, and case
  Action History are exactly the continuity + documentation evidence a TJC surveyor would ask
  for after an outage.**
- **NCQA (National Committee for Quality Assurance)** accredits health plans (payers). Its
  **Utilization Management** standards put *timeliness clocks* on prior-authorization and claim
  decisions — and **those clocks don't pause for a cyberattack.** CascadeCare's case/stage
  **SLA → escalation** layer *is* a compliance clock (on-track / at-risk / breached), and the
  **Prior Authorization** agent it orchestrates is what keeps those decisions moving during the
  freeze. NCQA's delegation/oversight expectations over business associates map directly to the
  **BAA Boundary Reasoner**'s per-contract reasoning.
- **ACHC (Accreditation Commission for Health Care)** accredits home health, hospice, DME, and
  pharmacy. Its regulatory-compliance and record-management standards, and continuity-of-care
  expectations during disruption, are the *downstream* organizations a payment-network freeze
  hits hardest — **the stakeholders CascadeCare fans out a case for.**
- **HIPAA / Business Associate Agreements** are already first-class in the story: the **Trust
  Layer** keeps PHI inside the governance boundary on every LLM call, and the BAA Boundary
  Reasoner reasons about lawful disclosure under each provider's BAA.

**The one-liner:** *"The decisions and timeliness CascadeCare tracks are the same ones The Joint
Commission, NCQA, and ACHC hold healthcare organizations accountable for — and the case file it
produces is the survey-ready evidence those audits demand."*

---

## 9. Value-proposition canvas (who / pain / gain)

| | |
|---|---|
| **Who** | UiPath's healthcare vertical + its customers (health systems, payers, BPOs) who are *already* buying the ViVE-2026 agents and need a crisis/coordination layer over them. |
| **The pain (today)** | A multi-stakeholder healthcare crisis = a manual war room. 3 agents × 6 providers = **18 disconnected runs** with no shared state, no SLA clock, no legal layer, no human gates, no audit. The intermediary answers one subpoena six conflicting ways. |
| **The gain (with CascadeCare)** | **One living case file.** It routes the agents, tracks every obligation across 90 days, escalates the legal calls to a human, records who decided what and when, and adapts as the situation reverses five times — 13 coordinated cases on one canvas, every one driven to Completed. |
| **Why us / why now** | Healthcare is UiPath's #1 2026 push; the agents just shipped; nothing orchestrates them under crisis yet. CascadeCare is first-mover, UiPath-native, and adoptable with a connector swap. |

**Before → after, in one line:** *"Without CascadeCare, a payment-network crisis is eighteen
disconnected agent runs and a war room. With it, it's one auditable case that conducts them."*

---

## 10. Audience cuts (same story, different emphasis)

- **Judge (Track 1 / Maestro Case):** emphasize the *orchestration mechanics* — 3-level native
  nesting, the case progressing itself via agents, the Reversal-3 fan-out, the consumed HITL
  ruling, exception handling, and 13 product surfaces. Tie each beat to a criterion (see §12).
- **UiPath executive / vertical lead:** emphasize *adoption* — "this is the crisis orchestrator
  for the agents you already ship; swap mocks for connectors and it's production; it produces
  the accreditation-grade audit trail your customers are surveyed against."
- **Developer / community (People's Choice):** emphasize *how it's built* — Maestro Case canvas
  as the orchestrator, LangGraph agent via `uipath-langchain`, governed BYO-LLM, and the
  open-source **Maestro Case Kit** they can install today.
- **Public / non-technical:** use the conductor metaphor and the ER analogy — "the agents are
  specialists; CascadeCare is the incident commander who runs the whole response and keeps the
  record straight."

---

## 11. Soundbites (reuse verbatim)

- "UiPath named it *Maestro* for a reason — CascadeCare is the conductor under fire."
- "The agents are soloists. A crisis needs an orchestra. CascadeCare conducts."
- "We didn't build a better agent. We built the thing that makes UiPath's agents work as a team."
- "The smoke alarm, the 911 call, the incident command, the specialists on scene — CascadeCare
  is what makes all four work together instead of independently."
- "Six providers, six lawful answers, one subpoena — grounded in each provider's actual BAA."
- "The part most case demos never show: *every case completes*, with a full audit trail."
- "The crisis is the demo. The orchestration pattern is the product."
- "Adoptable tomorrow: swap the mocks for connectors and it's production."

---

## 12. Map the story to the 5 judging criteria (so every beat earns a point)

| Criterion (Phase 1) | The story beat that proves it |
|---|---|
| **1 · Business Impact & Adoption** | The vertical bridge — crisis orchestrator for UiPath's own ViVE agents; accreditation-grade audit trail; adoptable with a connector swap. |
| **2 · Platform Usage** | 13 UiPath product surfaces, Maestro Case canvas as the orchestrator, governed BYO-LLM via Trust Layer, LangGraph via `uipath-langchain` — *plus the +2 coding-agent bonus* (built with Claude Code) and the open-source Maestro Case Kit. |
| **3 · Technical Execution / Feasibility** | 3-level native nesting, the case progressing itself, four-layer exception handling (agents degrade, the case never crashes), the consumed HITL ruling. |
| **4 · Completeness of Delivery** | Live on Automation Cloud (1.0.32), full cascade Completed end-to-end, public repo + README + ≤5-min video + deck. |
| **5 · Creativity & Innovation** | A self-reshaping crisis case with five goal reversals and a six-way fan-out — an orchestration pattern, not a linear toy. |

---

## 13. What NOT to say (honesty guardrails — non-negotiable)

- ❌ "Data Fabric drives the fan-out at runtime." → ✅ Spawn identities are **literal provider
  slugs**; runtime `=datafabric.qem:` in spawn inputs fails (`400300`) — a platform edge case we
  *avoided* and filed feedback on.
- ❌ "Deny rewinds / rolls back a stage." → ✅ **Both Approve and Deny advance** to Reversal 5;
  the decision is *data* (`reviewerDecision`) consumed downstream, not a stage rework.
- ❌ "We run UiPath's live ViVE products." → ✅ We **orchestrate** them as case tasks; in the demo
  they're API-workflow **mocks**; swapping in the live solutions is a connector change.
- ❌ "CascadeCare ensures NCQA / Joint Commission compliance." → ✅ It produces the **audit trail
  and SLA-timeliness evidence** those bodies expect; it does not implement their standards.
- ❌ Cite specific accreditation clause numbers on camera. → ✅ Speak to *what each body governs*.
- ❌ "The architecture animation is live tenant footage." → ✅ It's a **schematic diagram**; the
  live proof is the video + the tenant.
- ❌ Overstate Context Grounding. → ✅ It's **live + retrieval-verified** (BAA-corpus); claim
  retrieval, not fine-tuning.
- Numbers to keep consistent everywhere: **11 agents** (6 Agent Builder + 5 Coded, 1 LangGraph),
  **37 runtime artifacts**, **13 product surfaces**, **5 reversals**, **3 case levels**, **13
  live instances** at fan-out, **2 HITL gates**, live deploy **1.0.32 → CascadeCare-v110**.

---

## 14. FAQ — answer the confusions head-on

**Q: Is CascadeCare an agent?**
No. It's the **orchestration layer** (a UiPath Maestro Case) that *runs* agents. Eleven agents
plug into it as tasks.

**Q: So what does it actually *do*?**
It manages a multi-stakeholder healthcare crisis as one evolving case — deciding which agent
runs for which stakeholder under which legal constraint, tracking every obligation, pausing for
human rulings, and recording everything — end to end, live.

**Q: Why is it fictional? Is that a weakness?**
The *cast* is fictional (IP-safe), but the *crisis class* is real (mid-2020s payment-network
cyberattacks) and the *platform* is real (live on UiPath Automation Cloud). Fictional names
protect IP; nothing about the architecture is simulated.

**Q: Why should UiPath care?**
Because it's the missing crisis/coordination layer over the healthcare agents UiPath just
shipped — first-mover, native, and adoptable with a connector swap. It also produces the
accreditation-grade audit trail UiPath's healthcare customers are surveyed against.

**Q: What's the single most impressive thing to point at?**
Reversal 3: the master case spawning **six stakeholder cases simultaneously**, each spawning an
obligation case — **13 coordinated case instances, three levels deep, on one canvas** — and then
*all of them completing*.

---

## 15. Where this story lives (keep these in sync)

- **README.md** — "What This Is" + "Why This Matters" lead with the vertical bridge (this story).
- **docs/submission/DEVPOST.md** — project page copy.
- **docs/submission/VIDEO-SCRIPT.md** — the ≤5-min shot list + narration (this story, filmed).
- **docs/submission/DECK-BRIEF.md** — the slide adaptation of this story.
- **docs/submission/PEOPLES-CHOICE-FORUM-POST.md** — the community cut.

If you change the pitch, change it **here first**, then propagate.
