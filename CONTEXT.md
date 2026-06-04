# CONTEXT.md — Domain Vocabulary

> The shared language of this project. Agents use these terms exactly.
> The improve-codebase-architecture skill and grill-with-docs skill read this.
> Keep definitions to one sentence. Add terms as the project's language sharpens.

## Terms

**Reversal** — a master-level goal shift that changes what the crisis case is trying to achieve (five reversals drive the demo narrative).

**Master Crisis Case** — the single top-level Maestro Case instance (`clearflow-master-crisis`) that holds the entire cyber-crisis lifecycle.

**Stakeholder Parent Case** — a mid-level case (`clearflow-stakeholder-parent`) representing one party (provider, payer, or vendor) affected by the crisis.

**Obligation Grandchild Case** — a leaf-level case (`clearflow-obligation-grandchild`) scoped to one BAA, one regulator response, or one investigation thread.

**Cascade Signal** — the output of the Multi-Customer Pattern Detector indicating correlated anomalies across two or more provider customers, triggering Reversal 1.

**CPE** — ClearFlow Pricing Engine; the fictional pricing product that may be a breach vector.

**CPN** — ClearFlow Payment Network; the fictional payment-routing product whose claim-flow telemetry is monitored.

**BAA** — Business Associate Agreement; each provider has one with ClearFlow, and the BAA Boundary Reasoner analyzes its terms during Reversal 3 and 4.

**HITL Gate** — Human-in-the-Loop gate in UiPath Action Center where a human approves or rejects the agent's recommendation (fires at Reversal 4).

**Fan-spawn** — the visible simultaneous creation of multiple grandchild cases on the Maestro canvas (hero moment at Reversal 3, Day 30).

**Trust Layer** — UiPath's PHI/PII detection and content-filtering layer applied to every LLM Gateway call.

**LLM Gateway** — UiPath's BYO-LLM routing layer; Claude is registered for heavy-reasoning agents, UiPath first-party for computation agents.

**Vertical Bridge** — the positioning that CascadeCare is the Maestro Case orchestration layer ABOVE UiPath's ViVE-2026 Healthcare Agentic Solutions (Medical Records Summarization, Claim Denial Prevention & Resolution, Prior Authorization), coordinating them during a multi-party crisis.

**Case Orchestrator Agent** — the agent (promoted from the Forensic Self-Exam Agent) whose output drives master-case stage transitions, making the master case agent-driven rather than purely rule-driven.

**Agent-driven progression** — the top of the Academy's human→model→agent spectrum: an agent (not a fixed rule) decides the case's next stage from real-time data, events, and context.

**Agent Memory** — UiPath key-value agent memory that carries cascade-signal history, vector-hypothesis evolution, and posture decisions across the 90-day crisis timeline.

**OOTB Case App** — the out-of-the-box Maestro Case App (activity timeline with actor type + "Reworked" badge, SLA KPI tiles) that leads judge-facing demo beats; the bespoke `clearflow-network-command` App is the cinematic wrapper around it.

**Targeted re-entry** — re-entering a prior stage and re-running ONLY selected tasks (not the whole stage), a signature Maestro Case capability the demo must show explicitly.
