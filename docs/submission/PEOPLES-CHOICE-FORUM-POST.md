# People's Choice — UiPath Community Forum Post (draft)

> **Purpose:** the community-facing post for the AgentHack 2026 **People's Choice** award
> ($500 ×3; community voting **Jul 3–30, 2026 EDT**). Post on the UiPath Community Forum once the
> project gallery + voting open. Tone: enthusiastic, credible, developer-friendly — community
> devs vote for things they find *cool and reusable*, so the open-source give-back is front and
> center.
>
> **Before posting (human):** fill every `[HUMAN: …]` placeholder, upload the hero image, and
> confirm the architecture diagram renders. Forum image embeds use either an uploaded image or a
> markdown image link — host `docs/images/architecture.png` somewhere public (GitHub raw URL works)
> and paste it.

---

**Title:** CascadeCare Network Command — the UiPath Maestro Case that conducts UiPath's own healthcare agents through a live crisis

**Category/Tags:** `AgentHack 2026`, `Maestro`, `Case Management`, `Agent Builder`, `Coding Agents`

---

![CascadeCare architecture — three nested Maestro Case levels, 11 agents, Trust Layer, platform foundation](`[HUMAN: public image URL for docs/images/architecture.png — e.g. the GitHub raw link]`)

### TL;DR

UiPath just shipped healthcare AI agents — Medical Records Summarization, Claim Denial
Prevention, Prior Authorization — and each does one job, for one provider, in isolation.
**CascadeCare is the UiPath Maestro Case that makes them work as a team when a crisis hits.**

UiPath named the orchestration product *Maestro* for a reason: the agents are the musicians,
the Maestro is the conductor. CascadeCare is what that conductor looks like leading the
orchestra through the hardest piece in healthcare — a **payment-network cyberattack that freezes
claims across six hospital systems**, managed end-to-end as **one living, three-level case**,
live on UiPath Automation Cloud.

### What it actually does

A master crisis case spawns a case **per stakeholder**, and each of those spawns a case **per
legal obligation** — **three levels of native Maestro Case nesting** — while **five goal
reversals** reshape the response across a simulated 90-day timeline. Along the way it:

- runs **12 AI agents** (6 Agent Builder on Claude Sonnet 4.6 BYO-LLM + 6 Coded Python agents,
  **two of them LangGraph `StateGraph` agents** via `uipath-langchain`),
- routes **every LLM call through the UiPath LLM Gateway + Trust Layer** (PHI/PII guardrails),
- **pauses for a human** at the two decisions a machine shouldn't make alone — and *reads that
  ruling downstream* to reshape the litigation posture,
- and then does the part most case demos never show: **every case completes** — master, six
  children, six grandchildren — each with a full audit trail.

### The hero moment 🎯

**Day 30: a state subpoena lands, and the master case fans out six stakeholder cases at once** —
each immediately spawning its own obligation case. **13 coordinated case instances, three levels
deep, on one canvas.** Inside each, the BAA Boundary Reasoner — grounded in that provider's
*actual* business-associate agreement via Context Grounding — returns a **different lawful
answer** for each provider. Six providers, six answers, one subpoena.

### Why it matters

Healthcare is UiPath's #1 vertical for 2026. The agents that do the work just shipped — but
nothing coordinates them through a multi-stakeholder crisis. CascadeCare is that missing layer,
**UiPath-native at runtime** (the Maestro Case canvas *is* the orchestrator — no external
harness), so the health vertical could adopt it with a connector swap. The decisions and
timeliness it tracks are the same ones The Joint Commission, NCQA, and ACHC hold healthcare
organizations accountable for — and the case file it produces is survey-grade audit evidence.

### Built with a coding agent — and we gave something back 🛠️

The entire repo — **37 UiPath artifacts and every test, test-first** — was authored by **Claude
Code**. And we went beyond the demo: we packaged our hardest-won, undocumented Maestro Case
discoveries into **[Maestro Case Kit](https://pypi.org/project/maestro-case-kit/)** — a free,
open-source, **offline & credential-free** toolkit (CLI + MCP server + agent skills) that
explains cryptic Maestro error codes and lints caseplans in CI. Anyone building on Maestro Case
can install it today:

```bash
pipx install maestro-case-kit
maestro-case explain 400300      # cryptic error code → proven cause + fix (offline)
maestro-case lint path/to/caseplan-dir
```

### See it / try it

- 🎬 **Demo video (≤5 min, live run):** `[HUMAN: YouTube/Vimeo URL]`
- 💻 **Code (MIT):** `[HUMAN: GitHub repo URL]`
- 🏆 **Devpost project:** `[HUMAN: Devpost project URL]`
- 📊 **Live operator dashboard:** https://hackathon26_042.staging.uipath.host/clearflow-network-command

If this resonates, **a People's Choice vote would mean a lot** 🙏 — and if you build on Maestro
Case, grab the Kit and tell us what footguns to add next. Happy to answer anything in the
thread!

*— Team CascadeCare · AgentHack 2026 · Track 1 (UiPath Maestro Case)*

---

> **Honesty notes (keep when editing, delete before posting):** the cast (ClearFlow, providers,
> payers) is fictional/IP-safe; the crisis *class* is real and the platform is real (live on
> Automation Cloud). The ViVE healthcare agents are orchestrated as case tasks — represented by
> API-workflow mocks in the demo (a connector swap from production). Don't claim runtime
> `qem:` Data Fabric fan-out (literal slugs); don't claim CascadeCare "implements" any
> accreditation standard — it produces the audit/SLA evidence those bodies expect. The
> architecture image is a schematic diagram, not live-tenant footage.
