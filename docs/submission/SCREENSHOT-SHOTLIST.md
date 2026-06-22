# Screenshot Shot-List — make the capture session mechanical

> **Goal:** capture every image the submission needs in one sitting, with zero guesswork. Each
> shot below has an exact **what to capture**, the **caption** to paste, the **judging criterion**
> it proves, and the **DEVPOST.md slot** it fills. Capture in order; they follow one live run.
>
> Two homes for the files:
> - **Product/tenant shots** → `docs/evidence/` (create the dir on first capture). These are the
>   7 Devpost attachments (uploaded to the Devpost project page; committing them is good evidence).
> - **Coding-agent shots** → `docs/coding-agents/screenshots/` (the +2-bonus reel; the channel
>   README is already scaffolded there).
>
> **Format:** PNG, ≥1600px wide, light UI zoom so text is legible when scaled down. Crop browser
> chrome but keep the system clock visible on at least the canvas + closure shots (proves live).

## Prep (once)
1. Follow [`docs/DEMO-RUNBOOK.md`](../DEMO-RUNBOOK.md) **Path A** to auth and start a fresh run;
   approve both HITL gates (A4); confirm all-Completed (A5). For a run you want to keep for judges,
   use **Path P** (preserve-a-run) so the view survives the rolling judging window.
2. Open three browser tabs: **Maestro → Case Instances**, the **master case canvas**, and
   **Action Center → Tasks** (all in the `CascadeCare-v110` folder).
3. Keep one terminal visible for the `[VERIFY]` CLI confirmations.

---

## The 7 Devpost attachments (product/tenant)

| # | Filename (`docs/evidence/`) | What to capture (exact state) | Caption to paste | Proves (criterion) | Fills DEVPOST slot |
|---|---|---|---|---|---|
| 1 | `01-master-canvas.png` | The **master case canvas**, zoomed to show all 7 stages (Initial Response → … → Closed) with the reversal/return-to-origin path visible. | "One master Maestro Case drives the 90-day crisis — five goal reversals across seven stages, the case re-routing itself." | C2 Orchestration · C5 Creativity | Screenshot **1** (`:208`) |
| 2 | `02-reversal3-fanout.png` | **Maestro → Case Instances**, captured right as Reversal 3 lands: the master + **6 stakeholder children** (+ their grandchildren) appear together. Show the 13-instance fan. | "Reversal 3 (Day 30): a state subpoena fans out six stakeholder cases at once — 13 coordinated instances, three levels of native nesting." | C2 Orchestration (hero) | Screenshot **2** (`:209`) |
| 3 | `03-fiduciary-gate.png` | **Action Center → Tasks** → the **Tri-Party Fiduciary Conflict Review** task open, all four fields populated (Payer Demand, Affected Provider BAAs, ClearFlow Obligations, Conflict Analysis). | "The case stops for a human at the three-way legal conflict — a tri-party ruling recorded with who / why / when, and read downstream." | C3 Exceptions · human accountability | Screenshot **3** (`:210`) |
| 4 | `04-case-app.png` | The **OOTB Case App** for a case instance: caseSummary + timeline + SLA tiles + stakeholder/obligation sections rendering on **1.0.32**. | "The out-of-the-box UiPath Case App: live case timeline, SLA tiles, and stakeholder/obligation sections." | C2 Platform Usage · C4 Variety | Screenshot **4** (`:211`) — clears `[VERIFY: 1.0.32]` |
| 5 | `05-trust-layer.png` | An **agent run trace / LLM Gateway policy view** showing the **Trust Layer** PHI/PII policy applied on a call (e.g., a BAA Boundary Reasoner or Vector Hypothesis call). | "Every LLM call routes through the UiPath LLM Gateway → Trust Layer — PHI/PII guardrails on each invocation." | C2 Platform Usage · governance | Screenshot **5** (`:212`) |
| 6 | `06-all-completed.png` | **Case Instances** filtered to this run, **every instance = Completed** (master + 6 + 6). System clock visible. | "The part most case demos never show: every case completes — master, six children, six grandchildren — each with a full audit trail." | C3 Exceptions · C4 Completeness | Screenshot **6** (`:213`) |
| 7 | `07-exception-handling.png` | Criterion-3 proof — **either** the forensic LangGraph agent's run output surfacing `error_type` / `error_message` on a forced Gateway failure while still returning the route, **or** the **Action History** showing an `instance retry` recovery. (Use `FORENSIC_FORCE_ENRICH_ERROR` per `DEMO-criterion3-and-fanout.md` to film the degrade deterministically.) | "Fails safe: when the LLM Gateway drops, the forensic agent surfaces the error and still routes correctly — the case never crashes. Recovery + the retry are in the Action History." | C3 Exceptions (top of band) | Screenshot **7** (`:214`) |

### Strongly recommended extras (not in the 7, but high-leverage)
| # | Filename (`docs/evidence/`) | What to capture | Caption | Use it for |
|---|---|---|---|---|
| 8 | `08-baa-six-answers.png` | A **BAA Boundary Reasoner** run trace whose rationale quotes the corpus section-by-section and shows a *different* disclosure position for two providers (e.g., one conditional, one restricted). | "Six providers, six lawful answers, one subpoena — each grounded in that provider's actual BAA via Context Grounding." | The hero "six-answer problem"; README/video/deck slide 7 |
| 9 | `09-dashboard.png` | The live **Coded Web App** dashboard (Energy-Flow cascade + containment gauge + reversal timeline + the **Compliance Ledger** panel showing live immutable `AuditRecord` rows with integrity hashes). | "The live operator command center — a UiPath Coded Web App, with the immutable Data Fabric compliance ledger surfaced live." | C5 Presentation; deck close |

---

## Coding-agent bonus shots (`docs/coding-agents/screenshots/`)

These earn the **+2 coding-agent bonus** (Platform Usage). Capture 2–4; the README in that folder
lists the channel.

| # | Filename | What to capture | Caption | Proves |
|---|---|---|---|---|
| C1 | `claude-code-tdd.png` | A Claude Code session writing a **failing test before the source** (TDD), e.g., the forensic `enrich_node` red→green cycle. | "Claude Code authored every artifact test-first — a failing test proved the bug before the fix landed." | Bonus (verifiable evidence) |
| C2 | `claude-code-uip-cli.png` | A Claude Code session driving the real **`uip` CLI** (e.g., `uip maestro case instance list` or a deploy). | "Claude Code drove the live `uip` CLI and the official `uipath-*` authoring skills." | Bonus (how it contributed) |
| C3 | `maestro-case-kit.png` | A terminal running `maestro-case explain 400300` (or `lint`) from the open-source kit. | "Above & beyond: the open-source Maestro Case Kit — reusable Maestro tooling, built by the coding agent." | Bonus + C4 Tooling |

---

## `[VERIFY]` items to confirm live (terminal, while capturing)

Run these so the Devpost copy's `[VERIFY]` markers can be cleared honestly:

- **OOTB Case App renders on 1.0.32** (`DEVPOST.md:80`, `:211`): open the Case App for a live
  instance and confirm caseSummary + sections render → if yes, change `[VERIFY: 1.0.32]` /
  `[VERIFY: 1.0.24 deployed + renders]` to a plain claim; if not, *delete the claim* rather than
  overstate. Capture = shot **4**.
- **Closure proof** (`A5`): `uip maestro case instance list` showing all instances `Completed`
  → back stops shot **6**. (Remember: the Orchestrator **Jobs** view never flips — use **Case
  Instances** as truth, per runbook A5.)

## After capture — fill the slots
1. Drop shots 1–7 into the Devpost project page's screenshot section (and commit copies to
   `docs/evidence/`).
2. In [`DEVPOST.md`](DEVPOST.md): replace each `[HUMAN]` screenshot reference and clear the two
   `[VERIFY]` markers (or delete the unproven claim).
3. Add the repo URL (`DEVPOST.md:199`), video URL (`:200`), and Labs-access confirmation (`:202`).
4. Cross-check every count against [`STORY.md`](STORY.md) §13 before publishing.
