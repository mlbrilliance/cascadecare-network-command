# Healthcare Financial Shockwave Case PRD

Date: 2026-05-23

Working title: **CascadeCare Network Command**

Fictional protagonist: **ClearFlow Health Network**

Keynote line:

> When a hospital goes dark from ransomware, the payment network feels the shock before the legal world catches up. CascadeCare Network Command uses Maestro Case to govern the healthcare financial shockwave as claims, payments, regulators, litigants, insurers, payers, providers, and patients all start pulling on the same facts.

## 1. Executive Summary

Build a UiPath Maestro Case demo from the perspective of a fictional U.S. healthcare financial network operator, **ClearFlow Health Network**.

ClearFlow is not the attacked hospital. ClearFlow is the intermediary sitting between payers, providers, TPAs, IDR workflows, remittance streams, payment integrity operations, and provider payment rails. It sees claim-flow anomalies, payer/provider friction, payment backlog, IDR posture changes, and evidence requests before any single stakeholder sees the whole blast radius.

The triggering event is a ransomware attack at **Northstar Regional Health**, a fictional hospital system. The product is not a ransomware response tool. It is a **network shockwave case layer** that opens when a cyber event at one provider threatens claims liquidity, payer obligations, provider solvency, HIPAA/business-associate duties, IDR strategy, customer trust, and litigation evidence across the ecosystem.

The parent case belongs to ClearFlow:

`HealthcareFinancialShockwaveCase`

The case manager agent coordinates child cases across:

- Claim-flow anomaly detection
- Provider recovery support
- Payer coordination
- Payment and remittance continuity
- IDR posture and forbearance decisions
- Business associate / PHI exposure assessment
- Evidence preservation and legal hold
- Payer/provider conflict governance
- Customer communications
- Regulator and litigation response support
- Board and executive risk reporting

The differentiator is that ClearFlow's role changes during the case. It starts as an early-warning sensor, becomes a recovery coordinator, then becomes a business associate evidence holder, then becomes a conflicted intermediary when payer and provider incentives diverge, and may later become a discovery participant in litigation. Workflow tools assign tasks. Maestro Case governs the evolving role, evidence, decisions, and access boundaries.

## 2. Product Thesis

The hard problem is not "a hospital was hacked." The hard problem is that the U.S. healthcare financial network has no neutral case layer when one provider's cyber event becomes a multi-party operating crisis.

ClearFlow begins with operational uncertainty:

- Is the claim-volume collapse a bad feed, a clearinghouse outage, a ransomware event, or deliberate provider downtime?
- Which payers, provider groups, facilities, claims, remittances, and IDR disputes are affected?
- Which payments must be accelerated to preserve provider liquidity?
- Which payer controls, edits, and IDR objections should continue unchanged?
- Which logs contain PHI?
- Which evidence is operational, customer-facing, insurer-facing, regulator-facing, privileged, or litigation-hold?
- When does ClearFlow stop being a neutral connector and become a conflicted participant?

This is a true Maestro Case problem because:

- The case goal changes as facts mature.
- The same participant has multiple roles at once.
- Child cases share evidence but require different access scopes.
- Payer/provider incentives diverge mid-case.
- Deterministic robot work lives inside a non-deterministic parent case.
- Human legal, financial, and operational approvals are non-linear.

## 3. Research Anchors

### 3.1 HIPAA / OCR

The HHS HIPAA Breach Notification Rule requires covered entities and business associates to notify affected individuals after a breach of unsecured PHI. For breaches affecting 500 or more individuals, covered entities must notify HHS without unreasonable delay and no later than 60 days after discovery. HHS also states that ransomware is a HIPAA security incident and may constitute a breach depending on the facts and circumstances.

Sources:

- HHS Breach Notification Rule: https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html
- HHS ransomware fact sheet: https://www.hhs.gov/hipaa/for-professionals/security/guidance/cybersecurity/ransomware-fact-sheet/index.html
- HHS OCR breach portal: https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf

### 3.2 No Surprises Act / IDR Volume

CMS reports that, as of March 31, 2026, 5,729,954 Federal IDR disputes had been initiated since April 15, 2022. In March 2026 alone, 313,828 disputes were initiated, and certified IDR entities closed 285,766 disputes. This validates that IDR is a massive, high-volume operational layer that can be disrupted by healthcare cyber events.

Source:

- CMS IDR reports: https://www.cms.gov/nosurprises/policies-and-resources/Reports

### 3.3 SEC Cyber Disclosure

Public companies must disclose material cybersecurity incidents on Form 8-K within four business days after determining materiality. In this demo, ClearFlow may have to support public-company customers or its own board with evidence, but the app must not provide legal advice.

Sources:

- SEC statement on cybersecurity disclosures: https://www.sec.gov/newsroom/speeches-statements/gensler-statement-cybersecurity-072623
- SEC Form 8-K: https://www.sec.gov/files/form8-k.pdf

### 3.4 False Claims Act / Civil Cyber-Fraud

DOJ says FY2025 False Claims Act settlements and judgments exceeded $6.8B, with more than $5.7B related to healthcare. DOJ's Civil Division describes cybersecurity FCA matters as including failure to comply with required cybersecurity standards, misrepresenting cybersecurity controls, failing to monitor systems, and failing to timely report cyber incidents and breaches. In this demo, ClearFlow does not decide FCA liability; it preserves and scopes evidence when federal-program attestations become relevant.

Sources:

- DOJ FY2025 FCA results: https://www.justice.gov/opa/pr/false-claims-act-settlements-and-judgments-exceed-68b-fiscal-year-2025
- DOJ Civil Fraud Section practice areas: https://www.justice.gov/civil/practice-areas-0

### 3.5 Healthcare Payment Network Disruption

Major healthcare cyber events can disrupt claims processing, payments, pharmacy services, revenue-cycle operations, provider cash flow, and regulatory investigations across the healthcare ecosystem. This validates the core demo premise: the payment and claims network may experience the crisis as a financial shockwave, not merely as an IT incident.

Use this as a market pattern only. The demo, sample data, generated artifacts, and UI must not reference any real healthcare cyber incident or real intermediary.

### 3.6 Healthcare Financial Intermediary Market Pattern

Use a fictional company, **ClearFlow Health Network**, as a composite healthcare financial intermediary. Do not name, depict, imply, imitate, or target any real vendor in the demo, UI, code, screenshots, narration, sample documents, or submission.

The market pattern is real and common in U.S. healthcare. Intermediaries may support:

- Claims pricing and payment integrity
- Out-of-network pricing and reimbursement recommendations
- Network access and supplemental network workflows
- No Surprises Act / IDR support
- QPA-related data support
- Open negotiation record support
- Provider ACH payments
- Remittance and EOP/EOB delivery
- Denial and payment trend analytics
- Claims communications
- Provider and member communications
- Payer/provider portal workflows

The demo should use the pattern, not a real-company profile.

### 3.7 Intermediary Neutrality and Conflict Pattern

The strongest business pattern is a participant whose neutrality changes under stress.

During normal operations, ClearFlow may be a connector between payers and providers. During a crisis, incentives diverge:

- Providers want cash acceleration, objection pauses, expedited remits, and payer leniency.
- Payers want overpayment prevention, continued edits, continued IDR objections, and fraud/waste/abuse safeguards.
- Patients want uninterrupted care and transparent notices.
- Regulators and litigants want records.
- ClearFlow must preserve trust across all sides while protecting PHI, contracts, evidence, and role-specific access.

The case layer must detect when ClearFlow's role changes from neutral operator to conflict-governed participant.

## 4. Demo World

Use only fictional organizations.

### Case Owner

**ClearFlow Health Network**

- U.S. healthcare financial network operator
- Connects payers, providers, claims workflows, remittance streams, provider payments, payment integrity, and IDR support
- Maintains claim-flow telemetry across multiple payer/provider relationships
- Operates under business associate agreements and customer contracts

### Triggering Provider

**Northstar Regional Health**

- 7-hospital regional system
- 1.8M annual patient encounters
- 18,000 employees
- Core systems affected: EHR access, revenue cycle, claims submission, prior authorization responses, payment posting, patient scheduling

### Payer Customers

- **Apex Health Plan**
- **Union Prairie Benefits**
- **SummitBlue Medicare Advantage**
- **Lakeshore TPA Services**

### Other Participants

- Northstar breach counsel
- ClearFlow legal/compliance
- ClearFlow network operations
- ClearFlow payer account team
- ClearFlow provider account team
- Forensic firm
- Cyber insurer
- HHS OCR
- State AG offices
- Plaintiffs' counsel
- Board risk committee
- Neutral IDR administrator

### Cyber Event

Ransomware attack at Northstar causes:

- 91% drop in 837 claim submissions
- 73% drop in 835 remittance posting
- 64% 837 rejection rate
- Surge in 277 claim status inquiries
- IDR dispute backlog growth
- Provider cash-at-risk spike
- Later forensic finding of PHI exfiltration

### Core Case

- `CASE-2026-CF-0421-SHOCKWAVE`
- Type: `HealthcareFinancialShockwaveCase`
- Owner: `ClearFlow Health Network`
- Trigger: `Northstar claim-flow anomaly`
- Intake goal: `Determine whether a claim-flow shock is operational, cyber, or reportable, and stabilize network financial flows`

## 5. ClearFlow Role Evolution

ClearFlow is the case owner, but its role still evolves.

### Day 0: Network Sensor

- Detects claim, remittance, rejection, and status anomalies.
- Opens the parent case before Northstar formally confirms ransomware.
- Notifies internal network operations and account teams.

### Day 1: Recovery Coordinator

- Prioritizes critical claims, payer outreach, and backup routing options.
- Identifies providers at cash-flow risk.
- Coordinates payer leniency requests.

### Day 3: Business Associate Evidence Holder

- Forensics confirms possible PHI exfiltration at the provider.
- ClearFlow determines whether its own claim/payment flows contain affected PHI.
- Evidence preservation, log scoping, and breach-support obligations begin.

### Day 14: IDR and Payment Posture Operator

- Northstar-related IDR disputes are piling up.
- Payers and providers request different treatment.
- ClearFlow must decide whether normal edits, objections, and payment integrity workflows continue unchanged.

### Day 21: Litigation Evidence Custodian

- Patient class action is filed against the provider and related parties.
- ClearFlow logs and communications become potentially discoverable.
- Legal hold and scoped access are required.

### Day 45: Coverage and Settlement Leverage Dependency

- Provider's cyber insurer disputes or reserves rights.
- ClearFlow must understand whether unpaid claims, delayed payments, and operational costs may become damages evidence.
- Settlement leverage shifts across child cases.

### Day 60: Conflicted Network Participant

- Provider asks ClearFlow to pause IDR objections and accelerate payment flows.
- Payer asks ClearFlow to preserve objections and controls.
- ClearFlow is no longer just coordinating operations; it must route a conflict-governed human decision.

### Day 90: Multi-Proceeding Evidence Steward

- New regulatory, whistleblower, or litigation requests require cross-checking prior statements.
- ClearFlow must prevent inconsistent disclosures across customers, regulators, insurer, and courts.

## 6. Parent / Child Case Model

### Parent Case

`HealthcareFinancialShockwaveCase`

Fields:

- `case_id`
- `case_name`
- `owner_org`
- `triggering_provider`
- `status`
- `current_goal`
- `goal_history`
- `current_day`
- `network_risk_score`
- `claims_impacted`
- `cash_at_risk`
- `payment_delay_risk`
- `payer_count_impacted`
- `provider_count_impacted`
- `phi_exposure_status`
- `idr_backlog_count`
- `conflict_state`
- `privilege_mode`
- `case_manager_agent_summary`
- `open_decisions`
- `child_case_rollup`
- `evidence_graph`
- `participant_graph`
- `timeline_events`

### Child Case Types

1. `NetworkFlowAnomalyCase`
2. `ProviderRecoverySupportCase`
3. `PayerCoordinationCase`
4. `PaymentAndRemittanceContinuityCase`
5. `IDRPostureCase`
6. `BusinessAssociateExposureCase`
7. `EvidencePreservationCase`
8. `CustomerCommunicationsCase`
9. `RegulatorAndLitigationSupportCase`
10. `ConflictGovernanceCase`
11. `BoardRiskOversightCase`
12. `ClaimsRevenueStabilizationCase`

Each child case must have:

- Stage list
- Participants
- Deadlines
- Evidence scope
- Access scope
- Privilege classification
- Dependencies on parent facts
- Dependencies on other child cases
- Recent agent recommendations
- Human approvals

## 7. Required Case Stages

### Parent Case Stages

1. **Network Signal Intake**
   - Ingest ClearFlow telemetry: 837, 835, 999, 277, denial trends, payment events, IDR status.
   - Determine whether the signal looks like a feed outage, provider downtime, payer issue, or cyber shock.

2. **Shockwave Classification**
   - Estimate network blast radius.
   - Identify affected payers, provider groups, claim classes, remittance files, and IDR disputes.

3. **Role and Duty Assessment**
   - Determine ClearFlow's role per customer contract, BAA, payment workflow, IDR function, and evidence obligations.

4. **Financial Stabilization**
   - Prioritize claims, payment reroutes, payer outreach, provider support, and exception handling.

5. **Conflict Governance**
   - Detect payer/provider incentive divergence.
   - Trigger human gates when ClearFlow cannot act as a neutral operator without governance.

6. **Evidence and Access Control**
   - Preserve logs and communications.
   - Classify evidence as operational, customer-facing, privileged, regulator-facing, insurer-facing, or litigation-hold.

7. **Cross-Case Dependency Management**
   - Track how breach findings, insurance positions, class actions, and IDR decisions affect network operations.

8. **Resolution and Trust Restoration**
   - Close the case only when financial flows, evidence obligations, customer communications, and unresolved conflicts are stabilized.

### IDR Posture Case Stages

1. Dispute inventory
2. Eligibility and missing-data analysis
3. Payer/provider financial impact
4. Forbearance option modeling
5. Conflict review
6. Human decision
7. Action packet generation
8. Monitoring and rollback

### Business Associate Exposure Case Stages

1. Data-flow mapping
2. PHI exposure triage
3. BAA obligation review
4. Customer notice support
5. Evidence preservation
6. Counsel review
7. Closure memo

### Payment and Remittance Continuity Case Stages

1. Payment rail status
2. Remittance backlog assessment
3. Provider liquidity triage
4. Payer exception request
5. Payment acceleration or hold decision
6. Reconciliation
7. Closure

### Regulator and Litigation Support Case Stages

1. Request intake
2. Evidence scope
3. Privilege/access review
4. Production approval
5. Consistency check against prior statements
6. Response packet generation

## 8. Choreographed Demo Reversals

### Reversal 1: Day 0 Network Shock Detected First

The case opens from ClearFlow network telemetry, not a SOC alert:

- Claim volume from Northstar drops 91%.
- Remittance posting drops 73%.
- 837 rejection rate jumps from 2% to 64%.
- Claim status inquiries spike.
- IDR disputes tied to Northstar begin aging abnormally.

Case manager agent:

> ClearFlow has detected a healthcare financial shockwave. The current goal is to determine whether this is a feed issue, provider downtime, cyber disruption, or reportable data event while stabilizing claims and payments across affected payers and providers.

### Reversal 2: Day 3 PHI Exfiltration Signal

Forensics confirms data exfiltration at Northstar before encryption.

Effects:

- Parent goal changes from `classify operational shock` to `stabilize network flows and preserve breach-related evidence`.
- Business Associate Exposure child case opens.
- Evidence preservation child case escalates.
- ClearFlow logs become scoped by PHI relevance.
- Customer communications require legal approval.

### Reversal 3: Day 14 Provider Liquidity Stress

Northstar reports payroll and vendor-payment pressure because claims cannot be submitted, acknowledged, or reconciled normally.

Effects:

- Payment and Remittance Continuity child case escalates.
- Claims Revenue Stabilization child case opens.
- Payer Coordination child cases open for high-impact payers.
- Case manager agent recommends prioritized exception handling for high-value, time-sensitive, and government-program claims.

### Reversal 4: Day 21 Class Action Filed

A patient class action is filed against Northstar.

Effects:

- Regulator and Litigation Support child case moves active.
- ClearFlow communications and logs become potential evidence.
- Legal hold applies to selected evidence.
- Access scopes split between operations team and counsel-reviewed materials.

### Reversal 5: Day 45 Insurance Reservation of Rights

Northstar's cyber insurer issues a reservation of rights.

Effects:

- ClearFlow must preserve payment-delay, claims-backlog, and operational-cost evidence.
- Board Risk Oversight escalates because network exposure and customer trust risk increase.
- Case manager agent flags that insurer-facing statements and litigation-facing statements must remain consistent.

### Reversal 6: Day 60 Payer/Provider Conflict

Northstar asks ClearFlow to pause IDR objections and payment-integrity challenges for crisis-related claims. A payer customer asks ClearFlow to maintain controls and objections.

Effects:

- ClearFlow role changes from recovery coordinator to conflict-governed participant.
- Conflict Governance child case opens.
- IDR Posture child case reopens.
- Human approval required:
  - ClearFlow General Counsel
  - ClearFlow Chief Compliance Officer
  - Payer legal representative
  - Provider legal representative
  - Neutral case administrator

### Reversal 7: Day 90 Cross-Proceeding Consistency Risk

A regulator, whistleblower, or litigation request asks for evidence that overlaps prior customer communications, payer notices, insurer packets, and breach-support materials.

Effects:

- Evidence and Access Control stage reopens.
- Case manager agent detects inconsistent prior statements.
- Privilege and Access Agent recommends scoped production packages.
- Board brief updates with legal and trust risk.

## 9. Agents

### 9.1 Maestro Case Manager Agent

Responsibilities:

- Maintain current parent case goal.
- Detect goal changes.
- Recommend child case creation.
- Reopen stages when new facts invalidate prior decisions.
- Maintain participant graph and role changes.
- Track payer/provider conflict state.
- Track dependencies between child cases.
- Summarize executive status.
- Identify stale approvals invalidated by new facts.

Outputs:

- `current_goal`
- `goal_change_reason`
- `recommended_case_actions`
- `stage_reopen_recommendations`
- `participant_access_recommendations`
- `conflict_state`
- `executive_brief`

### 9.2 Network Flow Anomaly Agent

Responsibilities:

- Analyze synthetic 837/835/277/999 flows.
- Detect claim submission drops, remittance disruptions, payer rejection spikes, aging IDR disputes, and payment delays.
- Estimate cash at risk and affected payers/providers.

Outputs:

- `anomaly_score`
- `probable_shock_type`
- `affected_payers`
- `affected_provider_groups`
- `affected_claims_count`
- `cash_at_risk`
- `idr_aging_risk`
- `recommended_priority_claims`

### 9.3 Business Associate Exposure Agent

Responsibilities:

- Map claim/payment data flows containing PHI.
- Identify whether ClearFlow data, logs, or files may be implicated.
- Recommend BAA-driven evidence and notice support actions.

Outputs:

- `phi_flow_map`
- `exposure_likelihood`
- `customer_notice_support_tasks`
- `evidence_needed`

### 9.4 Payment Continuity Agent

Responsibilities:

- Prioritize claims and remittances.
- Recommend payer exception requests.
- Identify payment acceleration options.
- Flag reconciliation risk.

Outputs:

- `provider_liquidity_score`
- `payer_exception_requests`
- `payment_acceleration_options`
- `reconciliation_backlog`

### 9.5 IDR Posture Agent

Responsibilities:

- Analyze affected No Surprises Act disputes.
- Detect ineligible, missing-data, crisis-delayed, and high-financial-impact disputes.
- Recommend continue, pause, batch, settle, or neutral-review options.
- Consider payer/provider conflict.

Outputs:

- `idr_backlog`
- `eligibility_summary`
- `forbearance_options`
- `conflict_risk`
- `recommended_human_gate`

### 9.6 Conflict Governance Agent

Responsibilities:

- Detect when ClearFlow's neutral operating posture is no longer sufficient.
- Identify conflicting duties to payer and provider customers.
- Recommend access separation, approval gates, and decision forums.

Outputs:

- `conflict_detected`
- `conflict_type`
- `affected_parties`
- `recommended_governance_structure`
- `required_approvers`

### 9.7 Privilege and Access Agent

Responsibilities:

- Classify evidence as operational, customer-facing, regulator-facing, insurer-facing, counsel-privileged, litigation-hold, or restricted-party.
- Recommend participant access scopes.
- Prevent inappropriate evidence reuse across child cases.

Outputs:

- `evidence_classification`
- `participant_scope_changes`
- `privilege_warnings`
- `production_package_recommendations`

### 9.8 Statement Consistency Agent

Responsibilities:

- Compare statements made in payer notices, provider notices, insurer packets, board briefs, regulator responses, and litigation materials.
- Flag inconsistencies and outdated approvals.

Outputs:

- `inconsistency_flags`
- `statements_requiring_review`
- `recommended_corrections`

## 10. UiPath Robot / Connector Simulations

Implement mock robots if real systems are unavailable. Each robot should create visible timeline events.

Robots:

1. **Network Telemetry Robot**
   - Imports synthetic 837/835/277/999 and IDR status data.
   - Creates anomaly event.

2. **Payer Outreach Robot**
   - Drafts payer exception requests and SLA-waiver packets.

3. **Provider Support Robot**
   - Drafts provider recovery status updates and payment-priority reports.

4. **IDR Action Packet Robot**
   - Creates continue, pause, settle, or neutral-review action packet.

5. **Evidence Hold Robot**
   - Applies legal hold tags to claim-flow logs, remittance records, communications, and IDR artifacts.

6. **Customer Communications Robot**
   - Generates payer/provider customer notice drafts.

7. **Regulator/Litigation Support Robot**
   - Generates counsel-reviewed evidence production packet drafts.

8. **Executive Brief Robot**
   - Generates board and executive HTML/PDF brief from case state.

## 11. Data Model

### Case

```json
{
  "id": "CASE-2026-CF-0421-SHOCKWAVE",
  "type": "HealthcareFinancialShockwaveCase",
  "name": "Northstar Network Financial Shockwave",
  "ownerOrg": "ClearFlow Health Network",
  "triggeringProvider": "Northstar Regional Health",
  "status": "active",
  "currentGoal": "Stabilize network financial flows and preserve breach-related evidence",
  "networkRiskScore": 91,
  "currentDay": 45,
  "parentCaseId": null,
  "childCaseIds": [],
  "participants": [],
  "evidenceIds": [],
  "timelineEventIds": [],
  "openDecisionIds": []
}
```

### Participant

```json
{
  "id": "PART-CLEARFLOW",
  "name": "ClearFlow Health Network",
  "type": "case_owner_intermediary",
  "roles": [
    {
      "role": "network_sensor",
      "startDay": 0,
      "endDay": 1
    },
    {
      "role": "recovery_coordinator",
      "startDay": 1,
      "endDay": 21
    },
    {
      "role": "business_associate_evidence_holder",
      "startDay": 3,
      "endDay": null
    },
    {
      "role": "conflict_governed_intermediary",
      "startDay": 60,
      "endDay": null
    }
  ],
  "accessScope": ["network_telemetry", "claims_flow", "payment_backlog", "idr_posture", "customer_comms"],
  "restrictedEvidenceIds": ["EV-PRIV-001"]
}
```

### Evidence

```json
{
  "id": "EV-NET-ANOMALY-001",
  "title": "Northstar claim-flow anomaly",
  "source": "ClearFlow Network Telemetry",
  "day": 0,
  "classification": "operational",
  "privilege": "none",
  "linkedCaseIds": ["CASE-2026-CF-0421-SHOCKWAVE", "CHILD-NETWORK-FLOW"],
  "summary": "Claim volume down 91%, 837 rejection rate up to 64%, remittance posting down 73%.",
  "confidence": 0.94
}
```

### Decision Gate

```json
{
  "id": "DEC-IDR-FORBEARANCE-001",
  "title": "Change IDR posture for Northstar crisis-related disputes?",
  "day": 60,
  "status": "pending",
  "requiredApprovers": [
    "ClearFlow General Counsel",
    "ClearFlow Chief Compliance Officer",
    "Apex Health Plan Legal",
    "Northstar Legal",
    "Neutral Case Administrator"
  ],
  "options": [
    "continue_all_controls",
    "pause_crisis_related_objections",
    "settle_high_value_disputes",
    "route_to_neutral_review"
  ],
  "agentRecommendation": "route_to_neutral_review",
  "rationale": "ClearFlow's role has shifted from network recovery coordinator to conflict-governed intermediary; unilateral action could prejudice payer or provider customers."
}
```

## 12. UI Requirements

### 12.1 Network Command Center

Purpose: judge-facing and executive-facing home screen.

Must show:

- Parent case name and owner: ClearFlow Health Network
- Triggering provider: Northstar Regional Health
- Current goal
- Current crisis day
- Network risk score
- Claims impacted
- Cash at risk
- IDR backlog
- Payers impacted
- Providers impacted
- Open child cases
- Active deadlines
- Next human decisions
- "Case goal changed" banner
- "Participant role changed" banner

### 12.2 Shockwave Timeline

Must show:

- Day 0 network anomaly
- Day 3 PHI exfiltration signal
- Day 14 provider liquidity stress
- Day 21 class action
- Day 45 insurance reservation of rights
- Day 60 payer/provider conflict
- Day 90 cross-proceeding consistency risk

Each timeline event must link to evidence, role changes, and child case changes.

### 12.3 Participant and Role Graph

Must visualize:

- ClearFlow network operations
- ClearFlow legal/compliance
- ClearFlow payer account team
- ClearFlow provider account team
- Northstar legal/revenue cycle
- Affected payer legal/compliance
- Forensic firm
- Cyber insurer
- HHS OCR
- State AGs
- Plaintiffs' counsel
- Board risk committee
- Neutral case administrator

ClearFlow must visibly change role over time even though it owns the parent case.

### 12.4 Child Case Board

Columns:

- Not triggered
- Monitoring
- Active
- Blocked
- Conflict-governed
- Evidence hold
- Closed

Cards:

- Network Flow Anomaly
- Provider Recovery Support
- Payer Coordination
- Payment and Remittance Continuity
- IDR Posture
- Business Associate Exposure
- Evidence Preservation
- Customer Communications
- Regulator and Litigation Support
- Conflict Governance
- Board Risk Oversight
- Claims Revenue Stabilization

### 12.5 Evidence Graph

Must show shared evidence reused across child cases:

- Claim-flow telemetry
- Remittance backlog
- IDR dispute inventory
- Forensic PHI finding
- Payer communications
- Provider communications
- Insurer correspondence
- Legal hold tags
- Board briefs

Each evidence item must display:

- Source
- Confidence
- Classification
- Privilege status
- Linked child cases
- Who can access
- Whether under legal hold

### 12.6 Agent Workspace

Show agent outputs with:

- Input evidence
- Reasoning summary
- Confidence
- Recommendation
- Human approval required
- Action taken or blocked

### 12.7 Human Decision Modal

Required decision modals:

- Confirm shockwave classification
- Approve payer exception requests
- Approve provider recovery support packet
- Approve PHI/BAA evidence scope
- Approve IDR posture change
- Approve conflict governance structure
- Approve evidence production packet
- Approve executive/board brief

## 13. Demo Script

### Opening

"ClearFlow Health Network is not the hospital. It is the financial network operator that sees claims, remittance, payment, and IDR flows across payers and providers. At 8:42 AM, ClearFlow sees the shock before anyone has a complete explanation."

Action:

- Click `Ingest Network Telemetry`.
- Claim anomaly appears.
- Parent case opens.

### Day 0

Show:

- Claims down 91%.
- 837 rejects up 64%.
- Remittance posting down 73%.
- IDR disputes aging abnormally.
- Case manager sets goal: determine whether this is a feed issue, provider downtime, cyber event, or reportable data event while stabilizing financial flows.

### Day 3

Action:

- Click `Receive Forensic Signal`.

Show:

- PHI exfiltration signal confirmed by provider's forensic firm.
- Business Associate Exposure child case opens.
- Evidence Preservation child case escalates.
- Customer communications require legal approval.
- Parent goal changes.

### Day 14

Action:

- Click `Provider Liquidity Stress`.

Show:

- Payment and Remittance Continuity escalates.
- Payer Coordination opens for high-impact payers.
- Payment Continuity Agent recommends exception packets.
- Provider Support Robot drafts recovery support report.

### Day 21

Action:

- Click `Class Action Filed`.

Show:

- Regulator and Litigation Support becomes active.
- Legal hold applies to selected evidence.
- Evidence access restrictions change.

### Day 45

Action:

- Click `Insurance Reservation`.

Show:

- Payment-delay evidence is preserved for potential damages analysis.
- Board risk escalates.
- Statement Consistency Agent tracks insurer, customer, and litigation-facing statements.

### Day 60

Action:

- Click `Payer/Provider Conflict`.

Show:

- Provider requests pause on IDR objections and payment-integrity challenges.
- Payer requests normal controls continue.
- Conflict Governance child case opens.
- IDR Posture reopens.
- ClearFlow role changes to conflict-governed intermediary.
- Human decision gate opens.

### Day 90

Action:

- Click `Cross-Proceeding Request`.

Show:

- Regulator/litigation evidence request overlaps prior communications.
- Statement Consistency Agent flags inconsistency risk.
- Privilege and Access Agent recommends scoped production packages.

### Closing

"This is not ransomware response. The technical incident is only the trigger. ClearFlow's crisis is the network shockwave: claims, payments, IDR, breach evidence, customer trust, and legal exposure all changing at once. Maestro Case keeps one living case coherent while agents reason, robots act, and humans make the consequential calls."

## 14. Architecture Requirements

### 14.1 Core Architecture

Recommended prototype architecture:

- Frontend: React / Next.js or equivalent
- Backend: Node/Express or Python/FastAPI mock API
- Case engine: in-memory JSON state or lightweight database
- Agent layer: LangGraph or agent-like service wrappers
- UiPath layer: mock robot actions represented as callable endpoints and visible timeline events
- Data: static JSON fixtures plus event mutations

### 14.2 Maestro / LangGraph Split

Maestro Case owns:

- Parent and child case lifecycle
- Stage state
- Participant and role graph
- Evidence graph
- Human approvals
- Reopen logic
- Conflict governance state
- Audit trail
- Deadline rollups

LangGraph owns:

- Network anomaly reasoning
- PHI/BAA exposure reasoning
- Payment continuity reasoning
- IDR posture recommendations
- Conflict detection
- Evidence classification
- Statement consistency checking

Robots own:

- System actions
- Packet drafts
- Document generation
- Data pulls
- Customer communications drafts
- Evidence hold tagging

Humans own:

- Legal determinations
- Customer-facing commitments
- Conflict-governance decisions
- IDR posture decisions
- Evidence production approvals
- Board-level risk decisions

### 14.3 Required Mock API Endpoints

```txt
POST /api/demo/reset
POST /api/demo/day0-network-anomaly
POST /api/demo/day3-phi-signal
POST /api/demo/day14-liquidity-stress
POST /api/demo/day21-class-action
POST /api/demo/day45-insurance-reservation
POST /api/demo/day60-conflict
POST /api/demo/day90-cross-proceeding-request

GET  /api/cases
GET  /api/cases/:id
GET  /api/cases/:id/timeline
GET  /api/cases/:id/evidence
GET  /api/cases/:id/participants
GET  /api/cases/:id/decisions
POST /api/decisions/:id/approve
POST /api/decisions/:id/reject

POST /api/agents/case-manager/run
POST /api/agents/network-flow-anomaly/run
POST /api/agents/business-associate-exposure/run
POST /api/agents/payment-continuity/run
POST /api/agents/idr-posture/run
POST /api/agents/conflict-governance/run
POST /api/agents/privilege-access/run
POST /api/agents/statement-consistency/run

POST /api/robots/payer-outreach
POST /api/robots/provider-support
POST /api/robots/idr-action-packet
POST /api/robots/evidence-hold
POST /api/robots/customer-comms
POST /api/robots/evidence-production
POST /api/robots/executive-brief
```

## 15. Synthetic Data Requirements

Create realistic mock datasets:

1. `network_flow_events.json`
   - 837 submissions
   - 835 remittance events
   - 999 acknowledgements
   - 277 claim status events
   - payer IDs
   - provider TINs
   - claim amounts
   - payment dates
   - denial codes

2. `payer_provider_relationships.json`
   - payer customers
   - provider customers
   - account owners
   - contract flags
   - SLA terms
   - BAA flags

3. `idr_disputes.json`
   - 500 mock disputes
   - eligibility flags
   - QPA values
   - offered amounts
   - provider billed charges
   - dispute stage
   - payer/provider financial impact

4. `evidence_items.json`
   - network anomaly
   - forensic PHI signal
   - payment backlog report
   - payer emails
   - provider emails
   - class action notice summary
   - insurer reservation summary
   - regulator/litigation request summary

5. `participants.json`
   - internal ClearFlow participants
   - payer participants
   - provider participants
   - counsel participants
   - regulator/litigation participants
   - role timeline
   - access scopes

6. `communications.json`
   - payer notice drafts
   - provider status updates
   - board briefs
   - evidence production packets
   - statement text for consistency checks

7. `data_flow_map.json`
   - PHI-bearing flows
   - systems
   - file types
   - log retention
   - evidence owners

## 16. Acceptance Criteria

The build is successful only if all of these are true:

1. The demo opens from ClearFlow network telemetry, not hospital SOC detection.
2. ClearFlow owns the parent case.
3. Northstar is the triggering provider, not the product protagonist.
4. The parent case goal changes at least three times.
5. At least five child cases are created during the demo.
6. At least one stage reopens due to new evidence.
7. ClearFlow's role changes during the demo.
8. A payer/provider conflict triggers a human decision gate.
9. Evidence is shared across child cases but scoped differently by role and privilege.
10. At least four human approval gates are required.
11. At least three robot actions create visible timeline events.
12. The final executive brief is generated from case state and timeline.
13. The UI makes it obvious this is not a linear workflow.
14. All organizations, products, portals, claim IDs, policies, contracts, litigation documents, and correspondence are fictional.

## 17. Competitive Positioning

Do not pitch this as:

- Cyber incident response
- Ransomware containment
- Hospital breach management
- HIPAA notification automation
- IDR workflow automation
- Claims repricing
- GRC task tracking

Pitch it as:

> The living case layer for healthcare financial shockwaves, where one provider cyber event becomes a multi-party claims, payments, IDR, evidence, customer-trust, and legal-governance crisis.

Existing tools:

- SOAR handles technical response.
- GRC handles control tasks.
- E-discovery handles litigation documents.
- Insurance platforms handle insurance claims.
- Revenue-cycle tools handle billing and claims operations.
- Healthcare financial intermediaries handle claims, pricing, payments, IDR, and communications.

The missing layer:

- One parent case owned by the network operator.
- One evidence graph with role-scoped access.
- One participant graph with evolving roles.
- One agentic case manager that re-plans when goals shift.
- One conflict-governance structure when payer/provider incentives diverge.
- One human-led decision model across legal, financial, regulatory, and operational consequences.

## 18. Guardrails

1. Do not name, reference, resemble, or imply any real healthcare payment, repricing, clearinghouse, IDR, or payment-integrity vendor in the demo.
2. Use only fictional organizations, products, portals, claim IDs, policies, contracts, litigation documents, and correspondence.
3. Do not reference real litigation in the UI, video, pitch, sample documents, or generated evidence.
4. Do not submit anything to real HHS, CMS, SEC, OCR, payer, provider, or insurer portals.
5. Do not use real patient data.
6. Do not produce legal advice; produce decision-support drafts for human counsel.
7. All regulatory and contract matrices can be synthetic but must be plausible.

## 19. Build Priorities

Priority 1:

- Parent case model owned by ClearFlow
- Child cases
- Timeline
- Participant and role graph
- Evidence graph
- Demo event buttons
- Case manager agent summaries
- Human decision gates

Priority 2:

- Network anomaly data
- IDR conflict decision
- Payment continuity case
- Payer/provider relationship data
- Revenue-at-risk rollup

Priority 3:

- Business Associate Exposure case
- Evidence preservation
- Customer communications drafts
- Statement consistency checks

Priority 4:

- Polished command center
- Generated executive brief
- Exportable evidence pack
- UiPath robot event visualization

## 20. What To Hand To Judges

One-line description:

> CascadeCare Network Command uses UiPath Maestro Case to coordinate healthcare financial shockwaves after a provider cyber event disrupts claims, payments, IDR, customer trust, evidence governance, and payer/provider obligations across the network.

Thirty-second pitch:

> ClearFlow Health Network is not the hospital. It is the financial network operator that sees the claims and payment shock first. When a provider ransomware event hits, ClearFlow must stabilize claim flows, support provider liquidity, coordinate payers, preserve PHI-related evidence, govern IDR posture, respond to litigation and regulator requests, and manage payer/provider conflicts. Each proceeding shares facts but has different participants, evidence rules, deadlines, and incentives. CascadeCare Network Command makes that shockwave a living Maestro Case so agents can reason, robots can execute, and humans can make the consequential calls.

Why UiPath:

- Maestro Case manages context complexity.
- LangGraph agents reason through specialized case stages.
- UiPath robots execute deterministic system actions.
- Humans remain in charge of legal, financial, regulatory, and public decisions.
