# CascadeCare — The Architecture Diagram, Explained Simply

A plain-language companion to [`docs/images/architecture.png`](../images/architecture.png).
Read it to learn the picture; use the **"Say it out loud"** script when you present it.
No jargon is used without a plain definition (see the glossary at the end).

---

## In one breath

> One smart "case file" runs an entire healthcare-payment crisis from start to finish.
> It moves through stages, calls AI helpers at each step, splits into smaller cases as the
> crisis spreads, pauses for a human at the big decisions, and keeps a permanent record —
> all inside UiPath, with nothing bolted on from outside.

That's the whole picture. The rest of this doc just slows it down.

---

## The big idea (no jargon)

UiPath sells AI "agents" — small programs that each do one healthcare job well (read a
medical record, fight a denied claim, approve a treatment). They're good, but each works
**alone, for one hospital at a time**.

Now imagine a real disaster: a cyberattack freezes payments across **six hospital systems
at once**. Suddenly you don't need one clever helper — you need a **conductor** who decides
*which* helper runs, *for which* hospital, *in what order*, and *under which legal rule* —
and who keeps everyone in sync for 90 days while the situation keeps changing.

**CascadeCare is that conductor.** The diagram is a picture of the conductor at work.

A helpful way to hold it in your head: *the AI agents are the musicians; the UiPath Maestro
Case is the conductor; CascadeCare is the conductor leading the orchestra through the hardest
piece in healthcare.*

---

## A guided tour of the picture (top to bottom)

The diagram has **two big numbered boxes**. Box ① is the conductor doing its job. Box ② is the
supporting cast underneath. Read it top to bottom, left to right.

### The title strip (very top)
The name, a one-line description, and a tag that says this is an **AgentHack 2026, Track 1**
entry. "Live on Automation Cloud" means it's really running on UiPath's cloud, not a mock-up.

### Box ① — "Orchestration" (the conductor at work)

**The row of seven boxes** is the master case moving through **seven stages**, left to right,
over a simulated **90 days**: *Initial Response → Multi-Customer Investigation → Vector
Isolation → Regulatory Response → Fiduciary Review → Litigation Defense → Closed.* Think of
them as chapters in the story of the crisis. The **arrows between them** mean the case moves
itself forward — nobody is clicking "next."

**The small orange tags (R1…R5)** above the boxes are the **five reversals** — the five moments
where new bad news changes the plan. The crisis isn't a straight line; it keeps surprising you.

**The dashed curved arrow** (top) is the cleverest part: at Reversal 5 the case can **go back and
re-open an earlier chapter** it had already finished. A normal workflow can't walk backwards;
a case can.

**The little colored pills under each box** are the **AI agents** — the thinking helpers that
run *inside* that stage. For example, under "Vector Isolation" sit the *Forensic Self-Exam*
agent and the *Vector Hypothesis* agent. The caption says it plainly: **12 agents total — 6
low-code + 6 coded, 2 of them built with LangGraph.** A ⚡ bolt marks the LangGraph ones.

**The stacked boxes lower-left** show the case **splitting into smaller cases**. At Reversal 3
(Day 30) a subpoena makes the master spawn **6 "stakeholder" cases** (one per hospital), and
each of those spawns **1 "obligation" case** — so you end up with **13 live cases at once,
nested 3 levels deep.** That fan-out is the signature move; the diagram even labels "13 live
case instances."

**The two gold padlock pills** ("HITL gate" and "file / withdraw") are the **two points where the
case stops and waits for a human** to make a high-stakes legal call. The machine does the work;
a person makes the judgment.

**The gold bar across the bottom of Box ①** is the **Trust Layer**: every single AI call passes
through a privacy checkpoint (no patient data leaks). It sits under everything on purpose — it
governs all of it.

**The "Closed" box (far right, green)** is where the case ends — and notice the last agent,
*Audit Ledger · LangGraph*. The moment the case closes, that agent **writes a permanent,
tamper-evident record** of what happened. "✓ all instances Completed" means every one of the
13 cases finished cleanly.

### Box ② — "Data, Integration & Surfaces" (the supporting cast)

These are the UiPath pieces the conductor relies on:

- **Data Fabric** — the database of (made-up) hospitals, insurers, and contracts.
- **Context Grounding** — search indexes the agents read so their answers are grounded in real
  documents, not guesses.
- **Integration Service** — the connectors to the outside world (19 of them) that stand in for
  hospitals, insurers, regulators, and three of UiPath's own healthcare products.
- **Maestro BPMN / Maestro Flow** — the process models and the "demo driver" that plays the
  crisis like a script.
- **Action Center** — where the two human approvals actually appear for a person to act on.
- **Coded Web App** — the live dashboard, including a **Compliance Ledger** that shows the
  permanent record from the Closed stage.

The line on the right — "13 UiPath product surfaces · 38 runtime artifacts" — is just the
headline count of how many different UiPath pieces are used.

### The "Vertical bridge" strip
This says CascadeCare doesn't replace UiPath's healthcare agents — it **conducts them**. Each
hospital case can call UiPath's real ViVE-2026 products (Medical Records Summarization, Claim
Denial Prevention, Prior Authorization). So it's adoptable tomorrow.

### The bottom strip
On the left: **"Built end-to-end with Claude Code"** — an AI coding agent wrote the entire
thing, test-first. On the right: the **color key** (legend) for the whole diagram.

---

## What the colors mean (the legend, in plain words)

| Color | Means |
|---|---|
| **Orange** | A Maestro Case stage (a chapter of the case) |
| **Violet** | A low-code "Agent Builder" agent (runs on Claude Sonnet 4.6) |
| **Cyan** | A coded agent (written in Python); ⚡ = built with LangGraph |
| **Green** | A platform service (a built-in UiPath capability) |
| **Gold** | A human gate (the case waits for a person) |

---

## The numbers, and what each one means

| Number | Plain meaning |
|---|---|
| **3 case levels** | The case nests three deep: master → hospital → obligation. |
| **5 reversals** | Five times the plan changes mid-crisis. |
| **12 agents** | 12 AI helpers (6 low-code + 6 coded; 2 use LangGraph). |
| **13 live instances** | At the peak, 13 cases run at the same time. |
| **2 human gates** | Two points where a person must decide. |
| **13 product surfaces** | 13 different UiPath products are used together. |
| **38 artifacts** | 38 built pieces ship in the solution. |
| **768 tests** | 768 automated checks, all written before the code. |

---

## Say it out loud (a ~60-second script)

> "This is one UiPath Maestro Case running a healthcare-payment crisis end to end. Across the
> top, the master case moves itself through seven stages over ninety days, and these orange
> tags are five reversals — five times the situation changes and the case re-routes itself,
> even reopening an earlier step.
>
> Under each stage sit the AI agents that do the reasoning — twelve in all, six low-code and
> six coded, two of them built with LangGraph. Every one of their calls passes through the
> Trust Layer, the gold bar — so patient data never leaves UiPath's privacy boundary.
>
> Down here is the signature move: at Reversal 3, a subpoena makes the master fan out into six
> hospital cases at once, each spawning its own obligation case — thirteen live cases, three
> levels deep. Twice, the case stops for a human to make a legal ruling.
>
> When it closes, a LangGraph agent writes a permanent, tamper-evident audit record. Below,
> the data, integrations, and surfaces it all runs on — thirteen UiPath products, thirty-eight
> artifacts. And it plugs straight into UiPath's own healthcare agents. The whole thing was
> built end to end with Claude Code."

---

## Mini-glossary (plain definitions)

- **Maestro Case** — UiPath's tool for long-running "case files" that can branch, pause, and
  change course. Here, the case file *is* the orchestrator.
- **Agent** — a small AI program that does one reasoning job (e.g. spot an anomaly, read a
  contract). *Low-code* ones are built in UiPath's visual Agent Builder; *coded* ones are
  written in Python.
- **LangGraph** — a way to build a coded agent as a small "graph" of steps. Two of our agents
  use it, deployed through `uipath-langchain`.
- **Trust Layer** — UiPath's privacy/safety checkpoint that inspects every AI call for patient
  or personal data.
- **Data Fabric** — UiPath's built-in database for structured business data.
- **Context Grounding** — UiPath's document search that lets an agent ground its answer in real
  source text instead of guessing.
- **HITL gate** — "Human-in-the-loop." A point where the case pauses for a person to approve or
  decide.
- **`case-management` task** — the native Maestro feature that lets one case spawn another; this
  is how the 3-level nesting happens, with no outside orchestrator.
- **BAA** — Business Associate Agreement; the contract that says what a partner may do with
  health data. The legal agent grounds each answer in the right BAA.
- **Reversal** — a scripted moment where new information changes the master goal and the case
  re-routes.
- **Fan-out** — one case spawning many at once (here, 6 hospital cases from one subpoena).

---

*Source of truth for the narrative: [`STORY.md`](STORY.md). If anything here drifts from
STORY.md, STORY.md wins. The diagram is a schematic — not live-tenant footage.*
