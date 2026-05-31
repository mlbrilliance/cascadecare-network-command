# Cascade Command — Requirements Document

**A UiPath Maestro Case Orchestration Layer for a Healthcare Payment Intermediary Navigating a Multi-Customer Ecosystem Crisis**

*Submission target: UiPath AgentHack 2026, Track 1 (Maestro Case), $50,000 prize.*

*Document owner: Nick Sudh*
*Document version: 2.0 (protagonist shift: payment intermediary, not hospital)*
*Document type: Build specification for Claude Code execution*

---

## 0. How to Use This Document

This is a build spec, not a strategy doc. Hand the entire file to Claude Code. The intended workflow:

1. Claude Code reads sections 1–5 to understand the protagonist and architecture.
2. Claude Code builds the repo skeleton per section 5 in one pass.
3. Claude Code then implements sections 6–11 in the order specified by section 12 ("Implementation Phases").
4. Each phase has acceptance criteria in section 13; do not advance phases until criteria pass.
5. The demo narrative in section 3 is canonical. Every reversal in section 3 must be demonstrable by section 13's acceptance criteria.

When Claude Code has questions or proposes deviations, surface them in `DEVIATIONS.md`. Do not deviate silently.

The project name is **Cascade Command**. The name captures the central case-shape (a cascading multi-customer ecosystem crisis) and the operator posture (command, not defense). Use it consistently across the repo (`cascade-command/`), the Devpost submission, demo slides, README header, and voiceover.

---

## 1. Project Context

### 1.1 What this is

A working demonstration that UiPath Maestro Case can orchestrate the eighteen-month, multi-customer, multi-jurisdictional crisis response that a US healthcare payment intermediary must run when *multiple* of its provider customers suffer simultaneous or correlated cyber incidents — and that no other tool category in the market today can.

The protagonist is **Stratos** (fictional), a healthcare payment intermediary sitting between 750+ payers and 1.5M+ providers, processing ~1.5M claims daily at industry scale. The crisis is not "one of Stratos's customers got attacked." The crisis is "three of Stratos's customers showed correlated anomalies within 72 hours and Stratos doesn't yet know if the cause is sector-wide threat actor activity, a shared third-party vendor compromise, or Stratos itself."

The case Stratos runs is fundamentally different from the case a victim hospital runs. A hospital under attack is in *survival* posture. A payment intermediary at the moment its ecosystem fractures is in *fiduciary collision* posture — serving both sides of every broken transaction, with competing legal obligations to providers, payers, and regulators, and a market that's watching to see if it holds together.

### 1.2 Why this protagonist, why now

Three convergent realities make this the right submission right now (May 2026):

**Healthcare payment intermediaries are themselves under unprecedented operational pressure.** Multiple Sherman Act Section 1 antitrust class actions are in active discovery against major repricing and claim-pricing platforms; the DOJ has filed Statements of Interest endorsing plaintiffs' theories. These intermediaries are simultaneously dealing with the operational fallout of the Change Healthcare attack of February 2024 — still rippling through US provider revenue cycles in 2026 — and a sustained cadence of US hospital ransomware incidents. They are spending heavily on automation, AI, and orchestration to manage the operational pressure. They are the exact buyer profile for a Maestro Case layer.

**The multi-customer cascade pattern is genuinely novel.** Every commercial tool in the market handles "one customer in crisis." None handle "multiple correlated customers in crisis where the protagonist must determine whether it is the cause, the bystander, or the next victim — while simultaneously meeting legal obligations to both sides of every disrupted transaction." That is a case-shape no incumbent tool models.

**The 2026 regulatory environment makes this even sharper.** State AG enforcement is exploding in the CFPB enforcement gap. The DOJ's Civil Cyber-Fraud Initiative is actively reaching healthcare cybersecurity attestations. Cyber insurance carriers are increasingly disputing coverage. Every one of those vectors lands on the payment intermediary that touches the affected customers, often before it lands on the customers themselves.

### 1.3 What success looks like

- Working Maestro Case implementation that survives the five canonical demo reversals (section 3).
- A three-level case nesting demonstration (master case → per-customer crisis cases → stage-level cases) that no incumbent has shipped.
- The Multi-Customer Pattern Detector agent demonstrably triggers Reversal 1 and motivates the entire goal-shift sequence.
- A keynote-grade demo narrative deliverable in three minutes (section 3.2).
- A submission that wins Track 1 of AgentHack 2026.

### 1.4 What this is NOT

- Not a security incident response platform. Cycode, Halcyon, and Morphisec already do that lane.
- Not a GRC compliance tracker. ServiceNow GRC and OneTrust already do that lane.
- Not a legal e-discovery tool. Relativity and Everlaw already do that lane.
- Not a customer (hospital) revenue cycle product. Epic, Cerner, and the major payment intermediaries already do those lanes.
- It is the **case layer above all of them, run from the perspective of the payment intermediary** — and that case layer does not exist commercially today.

---

## 2. The Use Case (One-Page Summary)

### 2.1 The protagonist

**Stratos** — a fictional US healthcare payment intermediary processing ~1.5M claims daily across 750+ payers and 1.5M+ providers. Operates the synthetic Stratos Pricing Engine (SPE) for claim repricing, the synthetic Stratos Payment Network (SPN) for provider payment delivery, an IDR objection desk under the No Surprises Act, and a Revenue Cycle Analytics capability for provider customers. Privately held, PE-backed. All references to Stratos in this build are fictional; no real-world payment intermediary is named, modeled on specifically, or implicitly referenced (see section 11.3).

### 2.2 The crisis Stratos faces

Day 0, 06:14 ET. Stratos's Claim Flow Anomaly Detector fires on a 91% drop in claim volume from **Provider Customer Alpha**, a regional health system in the Southeast. The pattern matches ransomware-driven downtime events Stratos has seen before. The Master Stratos Crisis Response Case opens.

Day 0, 14:22 ET. The Anomaly Detector fires again — **Provider Customer Beta**, a different state, different geography, similar telemetry shape.

Day 1, 09:08 ET. A third anomaly — **Provider Customer Gamma**, even earlier in the curve. The Multi-Customer Pattern Detector agent surfaces an alarming correlation. Three of Stratos's provider customers showing the same telemetry signature within 27 hours. The question that drives the entire rest of the case: *is this coordinated threat actor activity, a shared third-party vendor compromise, or is Stratos itself the vector?*

Over the next 18 months, Stratos's Master Crisis Response Case must orchestrate:

1. **Internal forensic determination.** Is Stratos compromised? (No — but proving the negative takes a week and requires coordination across infrastructure, security, and SOC teams.)
2. **Vector attribution.** What do Alpha, Beta, Gamma share that other Stratos customers don't? (Reveal in Reversal 2: they share a SaaS vendor called Nimbus Patient Engagement Platform.)
3. **Per-customer crisis response.** Each affected customer becomes a child crisis case with its own stages, regulatory cascade, litigation exposure, and Stratos-customer contract obligations.
4. **Cross-customer pattern analysis.** As more customers surface anomalies (a fourth, fifth, eventually six), Stratos must determine whether each is the same root cause or a different one.
5. **Multi-jurisdiction regulatory response.** State DOIs, HHS OCR, possibly FTC inquire. Each inquiry creates discovery obligations that span all affected customers, and each affected customer's BAA has different terms about what Stratos can disclose to regulators about them.
6. **Cross-customer contract collision.** Payer customers (Sentinel Health, Liberty Health Plans) demand data access to "protect their interests." Stratos's BAAs with provider customers vary. Three-way contract collisions emerge.
7. **Vendor relationship management.** Stratos's commercial relationship with Nimbus is delicate. Stratos may need to publicly identify Nimbus as the attack vector (helps stop the bleeding) or stay silent (preserves a commercial partnership and avoids antitrust optics). Multi-party HITL.
8. **Litigation defense at scale.** Class action plaintiffs file against Nimbus first. Eventually they name Stratos as a co-defendant under negligent-monitoring theories ("Stratos saw the telemetry anomalies first; why didn't Stratos warn the market?"). Stratos becomes a participant in litigation it didn't start.
9. **Market and investor posture.** Stratos's PE owners convene emergency board calls. Stratos's competitors are watching. Stratos's other 1.5M unaffected provider customers are watching. The market's confidence in Stratos depends on visibly competent crisis orchestration.

### 2.3 Why no existing tool can run this case

Existing tools handle one customer in crisis, one regulator at a time, one contract relationship at a time. None hold the cross-cutting view Stratos needs. ServiceNow GRC tracks tasks but cannot model an evolving multi-customer correlation hypothesis. Cyber IR platforms manage Stratos's own technical state but cannot represent Stratos's six provider customers as parallel-but-correlated cases. Legal hold platforms preserve evidence but cannot reason about why BAA terms across six provider customers produce six different legal answers to a single state subpoena. Hospital revenue cycle products run the providers' side, not Stratos's.

**What Stratos needs is a case layer that holds the entire ecosystem-wide crisis as a single living business entity with internal nested structure.** That case layer is Maestro Case.

### 2.4 The Maestro Case insight (for this protagonist)

The Master Stratos Crisis Response Case has a known goal — *navigate the crisis with operational continuity, legal defensibility, and market position preserved* — but the path depends on context that evolves in three dimensions simultaneously:

1. **Across customers** (which providers are affected, in what order, with what severity)
2. **Across regulators** (which jurisdictions inquire, with what scope, on what timeline)
3. **Across counterparties** (which payers, vendors, insurers, plaintiffs surface, with what posture)

Each dimension creates child cases. Child cases share evidence. Child cases create cross-dependencies on each other. **The grandparent case (Stratos's Master Crisis Response) governs the entire structure.** That three-level nesting is what makes this Maestro Case-native and BPMN-impossible.

---

## 3. Demo Narrative & Reversal Choreography

The demo is a **three-minute simulated time-lapse** that compresses 18 months into 180 seconds, narrated by the Master Case Manager Agent.

### 3.1 Scene-by-scene script

**Scene 0 — Setup (0:00–0:15).** Black screen. Voiceover: "Sitting between 750 payers and 1.5 million providers, a US healthcare payment intermediary sees the entire system's bloodstream in real time. When that bloodstream hemorrhages in multiple places at once, the intermediary has thirty seconds to make decisions that will play out across thousands of customer contracts and ten regulatory regimes for the next eighteen months. This is the case management layer that doesn't exist today." Cut to Maestro Case empty timeline UI showing Stratos's logo.

**Scene 1 — Detection (0:15–0:35).** Day 0, 06:14. Stratos's Claim Flow Anomaly Detector fires on Provider Customer Alpha. The Master Stratos Crisis Response Case opens. A child case spawns: "Provider Alpha Crisis." The Case Manager Agent narrates: "Goal: assess Stratos's obligations to Provider Alpha and Stratos's exposure. Current confidence in classification: low." Day 0, 14:22. Provider Beta. Day 1, 09:08. Provider Gamma. Three child cases now live under the master.

**Scene 2 — Reversal 1: The correlation surfaces (0:35–1:00).** Day 1, 11:30. The **Multi-Customer Pattern Detector Agent** posts the demo's signature event: "Telemetry signatures across Alpha, Beta, Gamma show 91% correlation. Three independent ransomware events at three unaffiliated customers within 27 hours is below 0.3% baseline likelihood. Recommend immediate working hypothesis: coordinated threat actor or shared upstream vector." The Case Manager Agent: "**Goal critically shifted.** Previous goal: assist three isolated customers. New goal: determine whether Stratos is the vector, contain potential blast radius across remaining 1.5M providers. All existing child cases reclassified as related; new internal child case opens: 'Stratos Forensic Self-Examination.'" Participant count jumps from 14 to 28 as Stratos's internal SOC, infrastructure, and security leadership join the case as full participants. This is the moment that defines the demo.

**Scene 3 — Reversal 2: Stratos is not the vector (1:00–1:25).** Day 5. Stratos's internal forensic team completes infrastructure review: no internal compromise found. The Case Manager Agent: "Stratos confirmed not the vector. Goal shifts again." The Vector Hypothesis Agent posts: "Provider Customers Alpha, Beta, Gamma share three vendors in common. Two are widely-used; one — **Nimbus Patient Engagement Platform** — is the strongest correlate. 83% of similarly-affected customer profile uses Nimbus; <5% of unaffected customers do." A new child case spawns: "Nimbus Attribution Investigation." The Case Manager Agent: "Stratos is no longer a potential cause. Stratos is now the most-visible bystander in a sector-wide attack, with unique telemetry visibility into the propagation. Strategic question opens: disclose pattern publicly or maintain confidence pending verification?" Multi-party HITL gate spawns — Stratos GC, Stratos COO, Stratos CISO, board liaison.

**Scene 4 — Reversal 3: The state DOI subpoena collision (1:25–1:50).** Day 30. The Tennessee Department of Insurance subpoenas Stratos for "all claim flow records and internal correspondence relating to anomalous customer activity in the past 90 days." The BAA Boundary Reasoner Agent surfaces six different legal positions: Provider Alpha's BAA permits regulatory disclosure under one set of conditions, Provider Beta's BAA requires customer notification first, Provider Gamma's BAA includes a contractual non-disclosure clause that may conflict with the subpoena, and three other affected customers each have their own terms. **One subpoena, six legal answers.** The Case Manager Agent routes the case to a multi-jurisdiction legal HITL gate. Participant count: 28 → 41. A child Regulatory Response case spawns under the master, with six sub-cases (one per affected customer's BAA position) nested under it. That's three levels deep, live on the demo screen.

**Scene 5 — Reversal 4: The payer demands collide with the BAAs (1:50–2:15).** Day 45. Sentinel Health (one of Stratos's largest payer customers) demands real-time access to claim flow data on all affected provider customers, citing Sentinel's contract right to "operational visibility for quality assurance purposes." Liberty Health Plans follows. Stratos faces a three-way contract collision: Stratos's BAA with each provider customer (varies), Stratos's master agreement with each payer (varies), and Stratos's ethical and reputational obligations to its broader ecosystem. The **Multi-Party Fiduciary Conflict Detector Agent** identifies that this is not a legal-clarity problem; it's a fiduciary-conflict problem where Stratos cannot serve both sides cleanly. The Case Manager Agent escalates to a tri-party human gate: Stratos legal + payer legal + provider legal. The voiceover: "No system on earth handles this today. Maestro Case does."

**Scene 6 — Reversal 5: The litigation cascade (2:15–2:40).** Day 90. Class action plaintiffs file the first complaints against **Nimbus** for negligent security. Day 120, plaintiffs name Stratos as a co-defendant under a novel "negligent monitoring" theory: *Stratos's telemetry showed the anomaly pattern first, and Stratos had a duty to escalate to the market or to Nimbus*. The Case Manager Agent: "Posture inversion. Stratos was the bystander; Stratos is now a co-defendant. Posture across the six provider crisis cases must recalibrate. Provider customers who were Stratos's clients become potentially adverse if the negligent-monitoring theory has them naming Stratos in their own cross-claims for indemnification." The Litigation Defense child case spawns. Privilege boundaries reshuffle across the entire case tree. Participant count: 41 → 58.

**Scene 7 — Closeout (2:40–3:00).** Time-lapse to Day 540. The Master Case Manager Agent surfaces a board package generated from the entire case tree: "Final state: six provider crisis cases closed at managed postures. Three state DOI inquiries resolved without enforcement action. Two litigation matters in active settlement. BAA renegotiations completed with four customers; modernized terms now uniformly include sector-wide anomaly disclosure clauses. Aurora Specialty cyber coverage claim settled at 73% recovery. Stratos market position: 1.46M provider customers retained of 1.5M baseline; net commercial impact $47M against an exposed liability ceiling that peaked at $1.8B. Evidence pack: 14.3 million artifacts across 27 child and grandchild cases, 100% provenance-traced." Cut to keynote frame: *"When the bloodstream of US healthcare hemorrhages in multiple places at once, the intermediary that sees it first decides whether the ecosystem holds together. Maestro Case is the layer that lets it."*

### 3.2 Keynote frame (single sentence for Fusion stage)

> *"Sitting between 750 payers and 1.5 million providers, a payment intermediary sees the entire system's bloodstream in real time. When that bloodstream breaks in multiple places at once, the intermediary has to make decisions that will play out across thousands of contracts and ten regulatory regimes for the next eighteen months. Maestro Case is the orchestration layer for those decisions."*

### 3.3 What judges should walk away saying

If the demo lands, the conversation in the judging room should be:

- *"That's the first Maestro Case demo I've seen with three levels of nested cases live on screen."*
- *"The Multi-Customer Pattern Detector reversal is genuinely the protagonist's moment. The goal of the case changed twice in 30 seconds."*
- *"They didn't pick the easy victim story. They picked the harder protagonist whose obligations conflict in every direction."*
- *"This is healthcare-specific but the multi-customer cascade pattern generalizes to any B2B SaaS, payment processor, or platform-economy intermediary."*

---

## 4. Architecture & Tech Stack

### 4.1 Tech stack (explicit choices)

**Orchestration layer.** UiPath Maestro Case (preview). Maestro Process Apps for the case UI. UiPath Automation Cloud for hosting. UiPath Action Center for human-in-the-loop gates.

**Agentic reasoning layer.** LangGraph (Python, latest version). LangGraph is intentionally chosen over UiPath Native Agent Builder for the Master Case Manager Agent and child stage manager agents because LangGraph's graph-of-states model maps cleanly to Maestro Case's nested case structure and gives us deterministic, replayable agent traces — which matters for judges and for the evidence-pack requirement.

**LLMs.** Anthropic Claude (latest available via Anthropic API) as the reasoning backbone for all agents. Optionally OpenAI GPT-4o as a fallback for diversity. No local models for the demo — latency and reliability matter more than cost.

**Robots (RPA).** UiPath Studio for deterministic BPMN sub-flows: state AG subpoena response distribution, regulator notification submission, BAA-compliance check execution, Stratos's internal Jira/GitHub task creation for forensic work, cyber insurance claim filing.

**Mock external systems.** Built as FastAPI services in Python, hosted in local Docker Compose. Pretend to be: six provider customers (Alpha through Zeta) each with their own systems, three payer customers, two state DOIs, HHS OCR, a SaaS vendor (Nimbus Patient Engagement Platform), a cyber insurance carrier (Aurora Specialty), and Stratos's own internal SOC/SIEM.

**Data layer.** PostgreSQL for case state (multi-level case relationships). LanceDB for evidence-pack semantic search. The case-relationship schema must support three-level nesting (grandparent → parent → child) as first-class records.

**Frontend / case UI.** UiPath Maestro Process Apps if feasible. Falls back to a custom React (Next.js, App Router, TypeScript) console if Process Apps cannot model the three-level nested case views the demo needs. Use Tailwind plus shadcn/ui.

**Demo runtime.** Local Docker Compose composition that brings up: PostgreSQL, LanceDB, all mock services, the LangGraph agent runtime, the FastAPI orchestration shim that bridges Maestro Case events to LangGraph and back. The Maestro Case tenant is hosted on UiPath Cloud and connects to the local services via tunneled HTTPS (ngrok or Cloudflare Tunnel).

**Coding agent.** Claude Code is the primary developer for this project. Per the AgentHack bonus criteria, coding agent integration counts. Specifically: the **BAA Boundary Reasoner Agent** uses Claude Code at runtime (via the Anthropic API with extended tool use) to generate per-customer BAA disclosure analyses from each affected provider's BAA terms and the active regulatory inquiry's scope. This is not pre-generated. The coding agent reasons live during the case, with its session logs captured in the case evidence pack.

### 4.2 Architecture diagram (text representation; build SVG before submission)

```
┌─────────────────────────────────────────────────────────────────┐
│                  UiPath Maestro Case (Cloud)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   MASTER CASE: Stratos Crisis Response                   │   │
│  │   Case Manager Agent (master-level reasoning)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                  │                  │                    │
│       ▼                  ▼                  ▼                    │
│  ┌─────────┐       ┌─────────┐       ┌─────────────┐            │
│  │Provider │       │Vendor   │       │Regulatory   │            │
│  │Crisis A │  ...  │Attrib.  │       │Response     │  ...        │
│  └────┬────┘       └─────────┘       └──────┬──────┘            │
│       │                                     │                    │
│       ▼                                     ▼                    │
│  ┌────────┐                          ┌────────────┐              │
│  │Stage:  │                          │Per-BAA     │              │
│  │Detect  │                          │Subcase TN  │              │
│  └────────┘                          └────────────┘              │
│                                                                  │
│  Shared Evidence Pack across all nested cases                   │
│  Shared Participant Registry with per-case access scopes        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Webhooks + REST (tunneled)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│             Local Orchestration Shim (FastAPI + Docker)          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   LangGraph Agent Runtime (Python)                       │   │
│  │   Master agents:                                          │   │
│  │   ┌────────────────┐ ┌──────────────────┐                │   │
│  │   │ Master Case    │ │ Multi-Customer   │                │   │
│  │   │ Manager        │ │ Pattern Detector │                │   │
│  │   └────────────────┘ └──────────────────┘                │   │
│  │   Specialized agents:                                     │   │
│  │   ┌────────────┐ ┌────────────┐ ┌────────────┐          │   │
│  │   │ Claim Flow │ │ Vector     │ │ BAA Bound. │          │   │
│  │   │ Anomaly    │ │ Hypothesis │ │ Reasoner   │          │   │
│  │   ├────────────┤ ├────────────┤ ├────────────┤          │   │
│  │   │ Forensic   │ │ Multi-Party│ │ Negligent  │          │   │
│  │   │ Self-Exam  │ │ Conflict   │ │ Monitor    │          │   │
│  │   ├────────────┤ ├────────────┤ ├────────────┤          │   │
│  │   │ Market     │ │ Coverage   │ │ Board Pkg  │          │   │
│  │   │ Posture    │ │ Reasoner   │ │ Generator  │          │   │
│  │   └────────────┘ └────────────┘ └────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   Mock External Systems (FastAPI services)               │   │
│  │   • 6 Provider Customer mocks (Alpha–Zeta)               │   │
│  │   • 2 Payer Customer mocks                               │   │
│  │   • Nimbus SaaS vendor mock                              │   │
│  │   • 2 State DOI endpoints + HHS OCR portal               │   │
│  │   • Aurora Specialty cyber insurer mock                  │   │
│  │   • Stratos internal SIEM/SOC mock                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   PostgreSQL (case state, 3-level relationships)         │   │
│  │   LanceDB (evidence-pack semantic search)                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ▲
                            │ Studio + Orchestrator
                            │
┌─────────────────────────────────────────────────────────────────┐
│             UiPath Robots (deterministic BPMN sub-flows)         │
│   • Subpoena response distribution per BAA-scoped sub-case       │
│   • Regulator notification submission                            │
│   • BAA-compliance check execution                               │
│   • Internal Jira/GitHub forensic task creation                  │
│   • Cyber insurance claim filing                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Hybrid orchestration principle

Per UiPath's positioning: BPMN is for flow complexity, Case is for context complexity, and the win is being able to run both on the same event-sourced backbone. The demo illustrates this. Inside each case, deterministic sub-flows (subpoena response distribution, regulator notification, BAA-compliance checks, cyber insurance claim filing) are explicitly BPMN sub-processes spawned by case stages. The Master Case Manager and specialized agents are not BPMN — they are agentic context-evolution reasoners running across three levels of nested cases.

---

## 5. Repository Structure

Create exactly this structure in one pass before implementing logic:

```
cascade-command/
├── README.md                          # Project overview, demo script, judging criteria mapping
├── REQUIREMENTS.md                    # This document
├── DEVIATIONS.md                      # Empty initially; Claude Code logs deviations here
├── ARCHITECTURE.md                    # Detailed architecture doc with SVG
├── DEMO_SCRIPT.md                     # The 3-minute narration script with timing
├── docker-compose.yml                 # Local stack composition
├── .env.example                       # Environment variable template
├── pyproject.toml                     # Python dependencies (uv/poetry)
│
├── maestro/                           # UiPath Maestro Case artifacts
│   ├── case-definitions/
│   │   ├── master-stratos-crisis.json # The grandparent case schema
│   │   ├── child-cases/
│   │   │   ├── provider-crisis.json   # Template; 6 instances (Alpha–Zeta)
│   │   │   ├── forensic-self-exam.json
│   │   │   ├── vendor-attribution.json
│   │   │   ├── regulatory-response.json
│   │   │   ├── contract-collision.json
│   │   │   ├── litigation-defense.json
│   │   │   └── market-posture.json
│   │   ├── grandchild-cases/
│   │   │   ├── per-baa-subpoena-response.json
│   │   │   └── per-state-regulatory.json
│   │   └── shared-evidence-schema.json
│   ├── stages/
│   │   ├── detection.json
│   │   ├── classification.json
│   │   ├── pattern-correlation.json
│   │   ├── obligation-mapping.json
│   │   ├── strategic-decision.json
│   │   ├── execution.json
│   │   └── closure.json
│   ├── bpmn-subflows/
│   │   ├── subpoena-response-distribution.bpmn
│   │   ├── regulator-notification.bpmn
│   │   ├── baa-compliance-check.bpmn
│   │   ├── forensic-jira-spawn.bpmn
│   │   ├── cyber-insurance-claim.bpmn
│   │   └── evidence-pack-export.bpmn
│   └── webhooks/
│       └── webhook-handlers.md
│
├── agents/                            # LangGraph agent runtime
│   ├── __init__.py
│   ├── runtime.py                     # LangGraph runtime entry point
│   ├── master_case_manager.py         # The grandparent case manager
│   ├── child_case_managers/
│   │   ├── __init__.py
│   │   ├── provider_crisis_manager.py # One per provider crisis child case
│   │   ├── forensic_self_exam_manager.py
│   │   ├── vendor_attribution_manager.py
│   │   ├── regulatory_response_manager.py
│   │   ├── contract_collision_manager.py
│   │   ├── litigation_defense_manager.py
│   │   └── market_posture_manager.py
│   ├── specialized/
│   │   ├── __init__.py
│   │   ├── claim_flow_anomaly_detector.py
│   │   ├── multi_customer_pattern_detector.py    # SIGNATURE AGENT
│   │   ├── vector_hypothesis.py
│   │   ├── baa_boundary_reasoner.py              # Uses Claude Code at runtime
│   │   ├── forensic_self_exam.py
│   │   ├── multi_party_fiduciary_conflict.py
│   │   ├── negligent_monitor_risk.py
│   │   ├── coverage_reasoner.py
│   │   ├── market_posture.py
│   │   └── board_package_generator.py
│   ├── prompts/                       # Externalized prompts; one .md per agent
│   │   ├── master_case_manager.md
│   │   ├── multi_customer_pattern_detector.md
│   │   ├── baa_boundary_reasoner.md
│   │   └── ...
│   └── tools/
│       ├── __init__.py
│       ├── evidence_pack.py
│       ├── participant_registry.py
│       ├── case_relationship.py        # Three-level nesting model
│       └── case_state.py
│
├── shim/                              # FastAPI orchestration shim
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │   ├── maestro_webhooks.py
│   │   ├── agent_callbacks.py
│   │   └── mock_systems.py
│   └── models/
│       ├── case.py
│       ├── case_relationship.py       # Grandparent/parent/child model
│       ├── stage.py
│       ├── participant.py
│       └── event.py
│
├── mocks/                             # Mock external systems
│   ├── providers/
│   │   ├── provider_alpha.py
│   │   ├── provider_beta.py
│   │   ├── provider_gamma.py
│   │   ├── provider_delta.py
│   │   ├── provider_epsilon.py
│   │   └── provider_zeta.py
│   ├── payers/
│   │   ├── sentinel_health.py
│   │   ├── liberty_health.py
│   │   └── generic_payer.py
│   ├── nimbus_saas/                   # The eventual attack vector
│   │   └── main.py
│   ├── regulators/
│   │   ├── tn_doi.py
│   │   ├── ms_doi.py
│   │   ├── hhs_ocr.py
│   │   └── ftc.py
│   ├── stratos_internal/              # Stratos's own infrastructure mocks
│   │   ├── siem.py
│   │   ├── soc_ticket_queue.py
│   │   ├── spe_api.py                 # Stratos Pricing Engine
│   │   ├── spn_api.py                 # Stratos Payment Network
│   │   ├── idr_objection_queue.py
│   │   └── claim_flow_telemetry.py
│   └── cyber_insurer/
│       └── aurora_specialty.py
│
├── data/                              # Synthetic data
│   ├── providers/                     # Per-customer data
│   │   ├── alpha/                     # Alpha-specific data
│   │   │   ├── baa_terms.json         # Their BAA with Stratos
│   │   │   ├── patient_count.json
│   │   │   ├── claim_baseline.csv
│   │   │   └── claim_attack.csv
│   │   ├── beta/
│   │   ├── gamma/
│   │   ├── delta/
│   │   ├── epsilon/
│   │   └── zeta/
│   ├── nimbus/
│   │   ├── customer_list.json         # Who uses Nimbus across Stratos's customer base
│   │   └── attack_timeline.json
│   ├── regulatory/
│   │   ├── tn_doi_subpoena.json       # The Reversal 3 subpoena
│   │   ├── hipaa_state_rules.json
│   │   └── ocr_portal_fields.json
│   ├── stratos_internal/
│   │   ├── soc_logs_baseline.json
│   │   └── forensic_findings.json
│   └── fixtures/
│       ├── crisis_timeline.json       # The canonical 18-month timeline
│       └── reversal_triggers.json     # Choreographed reversal events
│
├── ui/                                # Case UI (Next.js if Process Apps insufficient)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── scripts/                           # Demo automation
│   ├── seed_synthetic_data.py
│   ├── run_demo.py                    # Triggers the 3-minute time-lapse
│   ├── reset_state.py
│   └── export_evidence_pack.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── demo/
│   │   └── test_all_reversals.py      # Acceptance test for the 5 reversals
│   └── fixtures/
│
└── docs/
    ├── presentation/                  # For submission video and Fusion talk
    ├── images/
    └── reference/                     # Source citations for regulatory claims
```

---

## 6. Maestro Case Model

### 6.1 The three-level case structure

This is the architectural commitment that makes the protagonist-shift demo work:

**Grandparent (master) case:** Stratos Crisis Response Case. One instance. Lifespan: detection through final closure (12–24 months typical).

**Parent (child) cases:** Spawned as the crisis unfolds. Typical instances:
- Per-Provider-Crisis (one per affected provider customer; 3–6 in demo, more possible)
- Stratos Forensic Self-Examination (one instance)
- Vendor Attribution Investigation (one instance, attaches to Nimbus)
- Regulatory Response (one instance, with grandchildren per regulator)
- Contract Collision (one or more, per material multi-party conflict)
- Litigation Defense (one instance, with grandchildren per matter)
- Market Posture (one instance, runs the entire crisis duration)

**Grandchild (sub-cases) within parent cases:** Spawned by parent stages as needed. Examples:
- Per-BAA-Subpoena-Response under Regulatory Response (one per affected provider's BAA terms when a single subpoena affects multiple BAAs)
- Per-State-Regulatory under Regulatory Response (one per state inquiry)
- Per-Litigation-Matter under Litigation Defense (one per case filed against Stratos)
- Per-Settlement-Negotiation under Litigation Defense (one per ongoing negotiation)

### 6.2 Case identifier conventions

- Master: `SCR-{YYYYMMDD}-master` (one only)
- Parent: `SCR-{YYYYMMDD}-{type}-{slug}` (e.g., `SCR-20260615-provider-alpha`)
- Grandchild: `SCR-{YYYYMMDD}-{parent_type}-{parent_slug}-{child_type}-{child_slug}` (e.g., `SCR-20260615-reg-tn_doi-baa-alpha`)

### 6.3 Master case stages

| Stage | Trigger | Goal at stage start | Exit criteria | Can reopen? |
|---|---|---|---|---|
| Detection | First customer anomaly | Confirm whether real incident vs noise | Confirmed by CISO + Case Mgr Agent | Yes — when new anomalies arrive |
| Classification | Multiple anomalies present | Determine: isolated, coordinated, or self-caused | Working hypothesis stabilized | Yes — repeatedly until vector confirmed |
| Pattern Correlation | Multi-Customer Pattern Detector activated | Identify shared vector among affected customers | Vector hypothesis stated with confidence ≥80% | Yes — when new affected customers appear |
| Obligation Mapping | Vector hypothesis established | Enumerate Stratos's obligations across all participants | Complete obligation matrix | Yes — when new participants arrive |
| Strategic Decision | Obligations mapped | Resolve fiduciary conflicts to executable posture | All HITL gates resolved | Yes — when new conflicts arise |
| Execution | Posture set | Operate the response across all child cases | All child cases reach terminal | Yes — non-sequential |
| Closure | All child terminal | Final evidence pack, board sign-off | Board approves | No — terminal |

### 6.4 Participants (canonical list)

The participant registry is dynamic across all three levels. Initial participants on master case open:

- Stratos CISO, COO, GC, CFO, CEO, Board Chair
- Stratos PE owner board representative
- Stratos internal SOC, infrastructure, security leads
- Stratos's outside cyber counsel (synthetic firm: "Hawthorne Mercer LLP")
- Stratos's outside forensic firm (synthetic: "Northwall Forensics")
- Aurora Specialty (cyber insurance carrier)

Joined as crisis unfolds:
- Six provider customer GCs and CISOs (Alpha–Zeta)
- Three payer customer GCs (Sentinel Health, Liberty Health Plans, plus a third TBD)
- Nimbus Patient Engagement Platform legal team
- State DOI staff (TN, MS initial; expanding)
- HHS OCR (regulator participant)
- DOJ Civil Division (if FCA qui tam unsealed)
- Class action plaintiffs' counsel (multiple firms; synthetic)
- Press (passive read-only participant)
- Stratos's other 1.5M provider customers (aggregate-level participant for posture/comms purposes)

Each participant carries:
- `participant_id`
- `display_name`
- `role` (regulator | counsel | vendor | adversary | board | press | aggregate)
- `case_access_scope` — which of the three case levels they can see, and which evidence categories
- `obligations` (Stratos's contractual obligations to them; their contractual obligations to Stratos)
- `joined_at`, `role_history[]`
- `contact_channels`

### 6.5 SLAs (statutory and contractual)

Encoded as first-class case rules across all three levels:

- HIPAA Breach Notification Rule (60 days from discovery, with BAA reporting obligations to provider customers within shorter contractual windows)
- State Breach Notification (51 variants)
- State DOI inquiry response timelines (varies)
- Cyber insurance claim notice (30 days)
- Payer-Stratos contract notification clauses (per-payer)
- Provider-Stratos BAA obligation clauses (per-provider)
- SEC Item 1.05 if applicable (where parent of Stratos is publicly traded)

The Master Case Manager Agent maintains a live SLA dashboard across all nested cases. SLA breach risk on a grandchild case triggers escalation to the appropriate parent and master-level human gate.

### 6.6 The six case-shape patterns this implementation must demonstrate

These are the patterns BPMN cannot model and that judges will look for. Each must have at least one explicit moment in the demo:

1. **Three-level case nesting.** Master → parent → grandchild visible simultaneously on the case UI.
2. **Goal changes at the master level driven by child-case events.** The Multi-Customer Pattern Detector at child level triggers master-level goal shift.
3. **Participant acquires new role mid-case across multiple cases simultaneously.** When Nimbus is named as the attack vector, Nimbus's role across every affected provider's case shifts at once.
4. **Cross-case evidence sharing with privilege-aware access.** A subpoena response in one BAA grandchild case may affect another BAA grandchild case; privilege scopes must remain enforced even within the shared evidence pack.
5. **Single trigger event spawns multi-level reactions.** State DOI subpoena (one event) spawns six BAA grandchild sub-cases, each with their own legal posture; the master case routes a strategic HITL gate above all of them.
6. **Evidence trail as a first-class artifact, provenance-traced across all three levels.** Closure requires the master to produce a unified evidence pack spanning grandparent through grandchild.

---

## 7. Agent Specifications

Each agent below is a LangGraph node or sub-graph. The Master Case Manager Agent is the top-level graph; child case managers are sub-graphs; specialized agents are sub-graph nodes called by the appropriate level.

### 7.1 Master Case Manager Agent

**Role:** Governs the entire master crisis lifecycle. Reasons about goal shifts at the master level. Decides when to spawn child cases. Reasons about cross-child dependencies. Escalates to the highest human gates.

**LLM:** Claude (latest, "thinking" / extended reasoning mode if available).

**Critical behaviors unique to the master level:**
- Must re-derive `master_goal_statement` every turn from current state across all child cases.
- When child-case events suggest the master goal has shifted, emit a `master_goal_shift` event and reason about whether existing parent cases need re-prioritization.
- Maintains the "fiduciary obligation matrix": at any point in the case, which obligations does Stratos hold to which participants, and which are in tension with which others.
- Never autonomously decides on the four "highest human gate" categories: public market disclosure, ransom payment exposure across affected customers, vendor attribution disclosure (Nimbus naming), settlement amounts >$5M. Always escalates to multi-party HITL.

**Prompt file:** `agents/prompts/master_case_manager.md`. Must include the six case-shape patterns from section 6.6 as explicit principles.

### 7.2 Child Case Manager Agents

One per child case type. Each is a LangGraph sub-graph specialized for the type of crisis the child case handles.

**Provider Crisis Child Manager.** One instance per affected provider customer. Manages Stratos's relationship to that specific provider through their crisis. Outputs flow up to the master.

**Forensic Self-Examination Child Manager.** Determines whether Stratos's own systems are compromised. Coordinates Stratos's internal SOC, infrastructure, security teams.

**Vendor Attribution Child Manager.** Once spawned, investigates whether a shared third-party vendor (Nimbus) is the actual vector. Coordinates evidence collection across affected provider cases.

**Regulatory Response Child Manager.** Manages all regulatory inquiries. Spawns grandchild sub-cases per regulator and per BAA-affected provider.

**Contract Collision Child Manager.** Manages multi-party contract conflicts. The Sentinel Health real-time data demand triggers an instance.

**Litigation Defense Child Manager.** Manages all litigation matters where Stratos is a participant.

**Market Posture Child Manager.** Runs for the entire crisis duration. Coordinates investor communications, customer comms, press posture.

### 7.3 Specialized Agents

#### 7.3.1 Claim Flow Anomaly Detector

The demo opener. Detects per-customer anomalies. Inputs: 24h claim flow telemetry from `mocks/stratos_internal/claim_flow_telemetry.py`. Outputs anomaly score, pattern match against historical incidents, recommendation.

#### 7.3.2 Multi-Customer Pattern Detector (SIGNATURE AGENT)

**Why this is the signature agent:** This is the agent that drives Reversal 1. When multiple customer anomalies surface, this agent computes pattern correlation across them and flags when correlation exceeds baseline likelihood.

**Inputs:** All active provider-crisis child cases, each with their current telemetry and incident profile.

**Outputs:**
- `correlation_score`: float 0–1 between affected customers
- `correlation_basis`: structured analysis of what they share (geography, network, shared vendors, timing)
- `working_hypotheses`: list of possible vectors (coordinated threat actor, shared vendor compromise, Stratos as vector)
- `recommended_master_goal_shift`: boolean and proposed new goal statement
- `confidence`: per-hypothesis confidence scores

**Implementation:** Use a combination of statistical correlation (telemetry pattern similarity) and LLM-based reasoning over customer profiles (shared vendors, infrastructure, geographies). Cache its outputs in the master case evidence pack as the canonical correlation analysis.

#### 7.3.3 Vector Hypothesis Agent

Once the Multi-Customer Pattern Detector establishes high correlation, this agent enumerates and evaluates hypotheses for the cause. Surfaces the Nimbus shared-vendor hypothesis in Reversal 2.

#### 7.3.4 BAA Boundary Reasoner Agent (THIS IS THE CODING AGENT INTEGRATION)

**Why this agent uses Claude Code at runtime:** Each affected provider customer has a different BAA with Stratos. When a regulator subpoenas Stratos for data on those customers (Reversal 3), each BAA produces a different legal position on what Stratos can disclose. Six BAAs, six different answers. Calling Claude Code at runtime to reason over each BAA's text plus the active subpoena's scope is the bonus-points-earning coding-agent moment for the AgentHack judges.

**Inputs:**
- Active subpoena or regulatory inquiry (scope, jurisdiction, deadline)
- Each affected provider's BAA terms (from `data/providers/{customer}/baa_terms.json`)
- Stratos's standard disclosure positions

**Outputs:** Per-customer disclosure analysis, with: what Stratos can/must/should disclose, what notification Stratos must give to that customer first, what redactions are required, what timeline applies.

**Implementation:** Claude Code session per affected customer, with tools to read BAA terms and the subpoena, and to compute the disclosure decision. Cache all sessions in the case evidence pack.

#### 7.3.5 Forensic Self-Examination Agent

Coordinates Stratos's internal forensic investigation. Reasons over Stratos's own SIEM logs, infrastructure telemetry, and security control state. Outputs the "Stratos compromised: yes/no" determination that drives the Reversal 2 transition.

#### 7.3.6 Multi-Party Fiduciary Conflict Detector

When Stratos's obligations to two or more participants conflict (Reversal 4: provider BAA versus payer data-access right), this agent surfaces the conflict, characterizes it (legal-clarity problem vs fiduciary-conflict problem vs strategic-positioning problem), and recommends the HITL gate structure.

#### 7.3.7 Negligent Monitoring Risk Agent

Drives Reversal 5. Reasons about Stratos's exposure to "negligent monitoring" theories — the novel litigation theory where Stratos's unique telemetry visibility creates a duty to escalate that, if breached, supports liability. Coordinates with the Litigation Defense Child Case Manager.

#### 7.3.8 Coverage Reasoner Agent

Reasons about Aurora Specialty (cyber insurance) coverage across the multiple affected customer events. Cyber policies typically don't anticipate multi-customer cascading scenarios. Identifies coverage gaps, sub-limit issues, and dispute risks.

#### 7.3.9 Market Posture Agent

Runs continuously through the crisis. Maintains the "what does the market think about Stratos right now" reasoning surface. Inputs include press coverage signals, competitor activity, customer churn signals, board pressure. Outputs recommended posture adjustments.

#### 7.3.10 Board Package Generator Agent

Generates board-ready summaries from the entire case tree on demand. Triggered by master case events (emergency board call), regulatory milestones, or scheduled cadence. Pulls from every child and grandchild case. Outputs a structured deck with: overall posture, customer-by-customer status, regulatory state, litigation state, financial exposure, market posture.

### 7.4 Agent prompts

All prompts live in `agents/prompts/*.md`. Each prompt file follows this skeleton:

```
# Agent Name

## Role
One paragraph describing the agent's purpose at its case level (master/child/specialized).

## Inputs
JSON schema or structured description.

## Outputs
JSON schema.

## Reasoning principles
For master-level agents, include the six case-shape patterns from REQUIREMENTS.md section 6.6.
For child-level agents, include the rule that child-level decisions must surface to the master when they trigger master-goal-shift conditions.
For specialized agents, include the rule that the agent never speaks beyond its specialization.

## Examples
2-3 worked examples.

## Anti-examples
1-2 examples of behavior the agent must NOT exhibit.
```

---

## 8. Robot Specifications

UiPath robots handle the deterministic, BPMN-shaped sub-flows. Build these in UiPath Studio.

### 8.1 Subpoena Response Distribution Robot

Takes the BAA Boundary Reasoner's per-customer disclosure analyses and distributes the responses to: the regulator (per their portal), to each affected customer's notification channel (per BAA terms), and to Stratos's outside counsel for review. Idempotent.

### 8.2 Regulator Notification Robot

Submits regulatory notifications to mock state DOI portals and HHS OCR portal. Handles per-state notification rules.

### 8.3 BAA-Compliance Check Robot

Runs deterministic checks on whether a proposed action (data disclosure, customer notification, vendor coordination) complies with the affected customer's BAA. Output feeds back into the child case for HITL approval.

### 8.4 Internal Jira/GitHub Forensic Task Spawn Robot

When the Forensic Self-Examination Child Case spawns sub-investigations, this robot creates Jira tickets and GitHub issues for Stratos's internal teams.

### 8.5 Cyber Insurance Claim Filing Robot

Files claim notices and updates with Aurora Specialty. Tracks claim status, coordinates with Coverage Reasoner Agent on coverage disputes.

### 8.6 Stratos API Integration Robot

Coordinates SPE (Stratos Pricing Engine) and SPN (Stratos Payment Network) operations during the crisis. Manages decisions like: pause payment delivery to Provider Alpha, hold reprocessing of held claims, manage IDR objection posture per affected customer.

### 8.7 Evidence Pack Export Robot

On closure, packages the entire three-level case tree's evidence into a tamper-evident archive (zip + manifest with SHA-256 hashes per artifact). Demonstrates the unified evidence pack across nested cases.

---

## 9. Mock External Systems

All mocks are FastAPI services. Each ships with deterministic fixtures so the demo replays identically every run.

### 9.1 Provider Customer Mocks (Six)

Each provider mock (Alpha through Zeta) exposes:
- `GET /telemetry/claim-flow` — claim flow telemetry (baseline + attack-day)
- `GET /baa/terms` — their BAA terms with Stratos
- `POST /notification/incoming` — Stratos's notifications to them
- `GET /infrastructure/profile` — what vendors they use (for the Vector Hypothesis Agent)

Six instances let the demo show: Alpha/Beta/Gamma in the first wave, Delta/Epsilon/Zeta surfacing later, and one or two remaining clean as control.

### 9.2 Nimbus Patient Engagement Platform Mock

The eventual attack vector. Endpoints:
- `GET /customer-list` — which Stratos customers use Nimbus
- `GET /security-disclosure` — Nimbus's eventual public security disclosure
- `POST /partnership-comms` — Stratos's communications channel with Nimbus

Includes a "panic state" toggle that simulates Nimbus's public posture flipping mid-crisis.

### 9.3 Payer Customer Mocks (Sentinel Health, Liberty Health Plans)

Eligibility, claim status, and prior auth endpoints, plus a `POST /demand-data-access` endpoint that triggers Reversal 4.

### 9.4 State DOI and HHS OCR Portal Mocks

State DOI endpoints (TN, MS initial) include a `POST /subpoena` endpoint that triggers Reversal 3. HHS OCR portal handles HIPAA breach notification submission.

### 9.5 Stratos Internal Systems

Mocks for Stratos's own SIEM, SOC ticket queue, SPE/SPN claim and payment APIs, IDR objection queue, and claim flow telemetry. The telemetry mock is the data source for the Anomaly Detector.

### 9.6 Aurora Specialty Cyber Insurer Mock

Policy retrieval, claim filing, claim status, and the coverage dispute endpoint that may trigger a parallel coverage litigation scenario.

---

## 10. Synthetic Data Specifications

All data is synthetic; no real PHI under any circumstances.

### 10.1 Stratos as protagonist

Stratos's operational scale is represented at industry-scale numbers (1.5M claims daily, 750+ payers, 1.5M+ providers, $155B priced annually) at category-level only. These numbers are publicly disclosed for the payment intermediary category at large; encode them as industry-public statistics, not as the actual numbers of any real company.

### 10.2 Provider customer profiles

Each provider customer (Alpha–Zeta) has:
- A profile (regional health system, urban academic medical center, rural community hospital network — diverse)
- A BAA with Stratos (varies materially across customers in regulatory disclosure clauses, breach notification timelines, indemnity terms)
- A list of third-party vendors (some include Nimbus, some don't — Nimbus appears in 3 of 6 affected customers in the demo timeline)
- A patient count (varies from 100K to 2M)
- Claim flow telemetry (baseline + attack-day)

### 10.3 BAA terms diversity

The BAA terms file for each customer is the most demo-critical synthetic data. Each must differ materially in:
- Disclosure of subpoena/regulatory inquiries (some require customer notification first; some permit Stratos to respond directly; some are silent)
- Breach notification timelines (some 24h, some 72h, some standard 60 days)
- Multi-customer-correlation clauses (most are silent; one or two have modern clauses requiring sector-wide anomaly notification)
- Indemnification scopes (varying)

These differences drive Reversal 3 — six different legal answers to one subpoena.

### 10.4 Nimbus vector data

`data/nimbus/customer_list.json` lists the subset of Stratos's customers using Nimbus. The overlap with affected customers is what the Vector Hypothesis Agent surfaces in Reversal 2.

`data/nimbus/attack_timeline.json` encodes when Nimbus's compromise occurred relative to the visible customer impacts.

### 10.5 Crisis timeline

`data/fixtures/crisis_timeline.json` encodes the canonical 18-month timeline with every event that fires during the demo. The demo runner reads this file and emits events in sequence with time compression.

### 10.6 Reversal triggers

`data/fixtures/reversal_triggers.json` encodes the five demo reversals with precise trigger conditions and expected case state changes. Acceptance tests in `tests/demo/test_all_reversals.py` verify each fires correctly.

---

## 11. The Protagonist Layer (Detailed)

### 11.0 Why this layer matters and how it's positioned

This layer is the differentiator. The protagonist is Stratos. The entire build is run from Stratos's perspective. Build the agents, mocks, and demo flow with Stratos's viewpoint as the canonical reasoning frame.

### 11.1 Stratos's competing obligations (the core case-shape)

At any moment in the case, Stratos holds simultaneous obligations to:

- **Provider customers (six affected, 1.5M unaffected)** — BAA-defined, varying per customer
- **Payer customers (Sentinel Health, Liberty Health Plans, and others)** — master agreement-defined, varying per payer
- **Regulators (state DOIs, HHS OCR, possibly FTC, possibly state AGs)** — statute-defined, varying per jurisdiction
- **Aurora Specialty (cyber insurance carrier)** — policy-defined
- **Nimbus Patient Engagement Platform** — commercial-relationship-defined
- **PE owners and board** — fiduciary-defined
- **Stratos employees, suppliers, vendors** — employment and contract-defined
- **The market** — reputation-defined

Most of these are in tension with at least one other at any given moment. The case manager agents' job is to identify the tensions, characterize them, and surface them to HITL gates with the right scope.

### 11.2 Stratos's case-level state evolution

The master case's strategic posture evolves through five canonical phases:

1. **Uncertain bystander.** "We have anomalies. We don't yet know what."
2. **Potential cause.** "Multiple anomalies correlated. We might be the vector."
3. **Confirmed bystander.** "Internal forensics clear. We're the most-visible bystander."
4. **Strategic actor.** "We have unique visibility. What we do shapes the sector's response."
5. **Co-defendant.** "Our visibility is now a litigation theory. We're inside the case."

Each phase transition is a master-level goal shift that propagates re-prioritization across all child cases. **Demonstrating this phase evolution explicitly on the UI is what wins Track 1.**

### 11.3 Production realism and IP-safety notes

All references to the payment intermediary in this build, in code, in mocks, in the demo, and in any supporting materials use the fictional entity name **Stratos** and the fictional product names **Stratos Pricing Engine (SPE)**, **Stratos Payment Network (SPN)**, and a generic **Revenue Cycle Analytics** layer. The provider customer names are abstract Greek-letter placeholders (Alpha, Beta, Gamma, Delta, Epsilon, Zeta). Payer customer names (Sentinel Health, Liberty Health Plans) and the SaaS vendor name (Nimbus Patient Engagement Platform) are clearly fictional. The cyber insurance carrier (Aurora Specialty) is fictional.

No real-world payment intermediary, payer, SaaS vendor, or insurance carrier is named, modeled on specifically, or implicitly referenced in marketing language. Mock API surfaces, business decisions, fiduciary positions, BAA terms, and crisis behaviors are invented for the demonstration. Industry-public statistics about US healthcare payment intermediaries at large (e.g., aggregate claim flow volume, payer and provider counts) may be cited at industry scale without attribution to any specific company. Do not represent any of Stratos's depicted behavior as factual conduct of any real company.

If asked at Fusion about real-world analogs, decline to name companies; describe the category and the structural problem.

---

## 12. Implementation Phases

Phases are sequential. Each phase has acceptance criteria in section 13. Do not advance until criteria pass.

### Phase 1 — Scaffolding (target: days 1–3)

- Create the full repo structure from section 5.
- `docker-compose.yml` brings up PostgreSQL and a "hello world" FastAPI shim.
- All `__init__.py` files exist; package imports clean.
- README with project overview and quickstart.

### Phase 2 — Maestro Case skeleton with three-level nesting (target: days 4–8)

- UiPath Cloud tenant configured.
- Master case definition created.
- Child case template definitions created (provider crisis, forensic self-exam, etc.).
- Grandchild case template definitions created (per-BAA subpoena, per-state regulatory).
- Three-level case-relationship schema implemented in PostgreSQL.
- Webhook endpoints stubbed.
- Smoke test: open master case, spawn one parent, spawn one grandchild under that parent, all three visible in case UI simultaneously.

### Phase 3 — Mocks and synthetic data (target: days 9–17)

- All six provider mocks (Alpha through Zeta) running with differentiated BAA terms.
- Nimbus, payer mocks, regulator mocks, Stratos internal mocks all running.
- Synthetic data generated for each provider's profile.
- BAA terms JSON populated with materially-differing terms across the six.
- Crisis timeline fixture written.
- Smoke test: each mock returns deterministic responses to canned inputs.

### Phase 4 — LangGraph agent runtime with master/child/specialized hierarchy (target: days 18–25)

- Master Case Manager Agent runs.
- Child case manager agents stubbed and routable.
- Claim Flow Anomaly Detector and Multi-Customer Pattern Detector fully implemented.
- Agent prompts externalized in `agents/prompts/`.
- Acceptance test: feed crisis timeline through; master case opens, three provider crisis children spawn within first 30 simulated minutes.

### Phase 5 — Reversals 1 and 2 (target: days 26–32)

- Reversal 1 (Multi-Customer Pattern Detector surfaces correlation, master goal shift) demonstrable.
- Forensic Self-Examination Child Case fully runs.
- Reversal 2 (Vector Hypothesis Agent identifies Nimbus, master goal shifts again) demonstrable.
- Acceptance test: both reversals fire on their canonical trigger events, master goal statement visibly changes twice.

### Phase 6 — Reversals 3 and 4 (target: days 33–39)

- BAA Boundary Reasoner Agent fully implemented, calling Claude Code at runtime.
- Reversal 3 (state DOI subpoena → six grandchild BAA cases) demonstrable.
- Multi-Party Fiduciary Conflict Detector fully implemented.
- Reversal 4 (Sentinel Health real-time data demand) demonstrable.
- Acceptance test: subpoena triggers six grandchild sub-cases visible in UI; conflict detector triggers tri-party HITL gate.

### Phase 7 — Reversal 5 and closure (target: days 40–45)

- Negligent Monitoring Risk Agent fully implemented.
- Reversal 5 (Stratos named as co-defendant) demonstrable.
- Closure stage implemented; Board Package Generator works; evidence pack export Robot working across three levels.
- All five reversals run end-to-end.

### Phase 8 — Demo polish and submission (target: days 46–49)

- Demo UI (Process Apps or Next.js fallback) polished with three-level case visualization.
- 3-minute video recorded.
- Submission package per AgentHack requirements.
- Rehearse twice end-to-end.

---

## 13. Acceptance Criteria

### 13.1 Functional acceptance

- [ ] All five canonical demo reversals fire correctly when triggered (`pytest tests/demo/test_all_reversals.py` green).
- [ ] The 3-minute demo runner (`scripts/run_demo.py`) produces a deterministic, replayable trace.
- [ ] Evidence pack export produces a tamper-evident archive with SHA-256 manifest spanning all three case levels.
- [ ] At least one BPMN sub-flow runs inside a case stage (proving hybrid orchestration).
- [ ] The BAA Boundary Reasoner Agent calls Claude Code at runtime and generates at least 6 customer-specific BAA disclosure analyses that pass a sanity check.

### 13.2 Case-shape acceptance (the six patterns from 6.6)

- [ ] Three-level case nesting demonstrated and visually clear on UI.
- [ ] Master-goal-shift driven by child-case event demonstrated (Reversal 1).
- [ ] Participant role change propagating across multiple cases simultaneously demonstrated (Nimbus role shift in Reversal 2).
- [ ] Cross-case evidence sharing with privilege-aware access demonstrated.
- [ ] Single trigger event spawning multi-level reactions demonstrated (state subpoena → six grandchild cases).
- [ ] Evidence trail provenance-traced across all three levels and exportable.

### 13.3 Demo acceptance

- [ ] Three-minute demo runs cleanly start-to-finish in under 3:15.
- [ ] Each reversal is visually obvious on the case UI.
- [ ] Master case goal statement visibly changes at the protagonist's two pivotal moments (Reversals 1 and 5).
- [ ] No system errors in three consecutive practice runs.

### 13.4 Submission acceptance

- [ ] Devpost submission complete.
- [ ] Video uploaded.
- [ ] Repo public (or shared-private per AgentHack rules).
- [ ] README clearly maps features to Track 1 judging criteria.

---

## 14. Risks and Open Questions

### 14.1 Things that could go wrong

**Maestro Case three-level nesting may not be a first-class feature.** Maestro Case is in preview and may only natively support two-level nesting. Mitigation: implement the third level via custom case-relationship metadata in PostgreSQL with the UI rendering nesting visually. If this is the case, log it in `DEVIATIONS.md` and document the workaround.

**The Multi-Customer Pattern Detector is the demo's signature moment.** If it doesn't fire convincingly, the demo loses its center. Mitigation: invest extra time in this agent's prompt design, give it carefully-tuned synthetic telemetry to compute over, and rehearse Reversal 1 specifically.

**Naming and IP risk.** Multiple real payment intermediaries are currently in active litigation. Mitigation already applied throughout: Stratos is fictional, provider customers are Greek-letter placeholders, payer and vendor names are clearly invented. Do not reintroduce real company names anywhere in the build.

**Realism risk on regulatory and contract details.** BAA terms diversity drives Reversal 3. The six synthetic BAAs must read as plausible to a healthcare attorney. Build them with care; cite generic BAA templates in `docs/reference/`.

**Demo cohesion risk.** Five reversals in three minutes is tight, especially with the three-level case visualization. The voiceover script is the cohesion mechanism. Rehearse.

### 14.2 Decisions Nick still needs to make

- Branding (logo, color, single visual identity for Cascade Command).
- Submission video host platform.
- Whether to build the Next.js UI or rely fully on Process Apps.
- Whether to demonstrate one main customer crisis with two parallel surfacing, or all six provider crises in full parallel (recommended: three full + three surfacing for visual richness without overwhelming the demo).

### 14.3 Open questions for Claude Code to flag during build

If Claude Code encounters ambiguity, log in `DEVIATIONS.md`:

- Specific Maestro Case API limitations for three-level nesting.
- Cases where prompt design hits LLM reasoning limits (especially the Multi-Customer Pattern Detector).
- BAA terms realism gaps that may affect demo credibility.
- Mock service realism issues.

---

## 15. Submission Checklist (AgentHack Track 1 alignment)

| Judging criterion | How this submission demonstrates it |
|---|---|
| Orchestrates dynamic, exception-heavy business processes | The protagonist runs an 18-month crisis with five path-changing reversals across three levels of nested cases. |
| Moves work through stages | Seven master-level stages plus per-child-case stages plus grandchild stages, each with explicit entry/exit criteria. |
| Handoffs between agents, robots, and people | 10+ specialized agents (across master, child, and specialized) + 7 UiPath robots + 5 distinct human approval gate types. |
| Humans in charge at key decision points | Four mandatory HITL gates: public market disclosure, vendor attribution disclosure (Nimbus naming), settlement amounts >$5M, multi-party fiduciary conflict resolution. |
| Real working solution | All five reversals demonstrably fire end-to-end against the running stack. |
| Bonus: coding agent integration | The BAA Boundary Reasoner Agent calls Claude Code at runtime to generate six customer-specific BAA disclosure analyses. Demonstrated and visible in the case evidence pack. |
| Bonus: protagonist sophistication | Stratos as protagonist demonstrates competing obligations across eight participant classes — a case-shape complexity no incumbent tool models. |

---

## Appendix A: Regulatory and Legal References

- **HIPAA Breach Notification Rule.** 45 CFR §§ 164.400–414. Per-state addenda summarized in Privacy Rights Clearinghouse 50-State Survey (2026 edition).
- **State Attorneys General coordination patterns.** Mayer Brown State AG Task Force materials; Cozen O'Connor "State AG Enforcement During CFPB Gap" (2026).
- **DOJ False Claims Act recoveries FY2025.** $6.8B reported per K&L Gates and Vinson & Elkins client alerts (Jan 2026).
- **Civil Cyber-Fraud Initiative.** DOJ announcement October 2021; recent settlements per Aerojet, GE precedents.
- **SEC Item 1.05 status.** Debevoise Form 8-K Tracker (May 21, 2026 update). Business Roundtable response to SEC reform of Regulation S-K.
- **US healthcare payment intermediary antitrust litigation (industry trend).** ArentFox Schiff health care antitrust roundup (2026); HFMA reporting on motion-to-dismiss rulings in repricing/payment-integrity antitrust cases (2026). Cite as a category trend, not by named defendant.
- **No Surprises Act IDR process.** Congressional Research Service R48738; HHS Third Report to Congress (February 2026).
- **Change Healthcare aftermath.** Nixon Peabody 2025 client alerts; HHS OCR FAQs; HIPAA Journal timeline.
- **Negligent monitoring litigation theory.** Novel theory tracked in healthcare cybersecurity litigation commentary (2026); cite at trend-level.

Maintain a `docs/reference/sources.md` file with full URLs and snapshot dates. Judges may verify.

---

## Appendix B: Glossary

- **BAA.** Business Associate Agreement under HIPAA. Defines what a business associate (Stratos) can and cannot do with PHI on behalf of a covered entity (a provider customer).
- **BPMN.** Business Process Model and Notation. Workflow-shaped, deterministic.
- **Case (Maestro sense).** A living business entity with evolving context, participants, evidence.
- **Civil Cyber-Fraud Initiative.** DOJ program applying False Claims Act to cybersecurity attestations.
- **DOI.** Department of Insurance (state-level regulator of insurance and payment intermediaries).
- **FCA.** False Claims Act.
- **HITL.** Human in the loop.
- **IDR.** Independent Dispute Resolution (No Surprises Act).
- **Master case.** The grandparent case in a three-level nested case structure.
- **Negligent monitoring.** Novel litigation theory that a party with unique observational visibility into harm has a duty to escalate.
- **Nimbus Patient Engagement Platform.** Fictional SaaS vendor used as the eventual attack vector in this build.
- **OCR.** HHS Office for Civil Rights.
- **PHI.** Protected Health Information.
- **Provider Customer Alpha/Beta/Gamma/Delta/Epsilon/Zeta.** Fictional abstract provider customer names used in this build.
- **Qui tam.** "Who as well" — FCA whistleblower action.
- **SLA.** Service Level Agreement.
- **SPN.** Stratos Payment Network. Fictional provider payments platform name used in this build.
- **SPE.** Stratos Pricing Engine. Fictional claim pricing platform name used in this build.
- **Stratos.** Fictional US healthcare payment intermediary; protagonist of this build.
- **Three-level case nesting.** The architectural pattern of master → parent → grandchild cases that this build demonstrates.

---

## Document Control

This document is the canonical build spec, version 2.0. If the implementation diverges, log the divergence in `DEVIATIONS.md` with rationale. Do not silently deviate. Re-read this document at the start of every build session.

*End of REQUIREMENTS.md v2.0*
