# Claude Code Build Brief: CascadeCare Network Command

Date: 2026-05-23

Purpose: build a polished hackathon demo prototype for **CascadeCare Network Command**, a UiPath Maestro Case concept shown from the perspective of a fictional healthcare financial network operator.

## North Star

Build a clickable, data-rich demo that proves this is not hospital ransomware response and not a linear workflow.

The protagonist is **ClearFlow Health Network**, a fictional intermediary that sees claims, payments, remittance, payment integrity, payer/provider communication, and IDR activity across the network.

The triggering event is a ransomware attack at **Northstar Regional Health**, but Northstar is not the main product owner. ClearFlow owns the parent case because ClearFlow must manage the financial shockwave across payers, providers, evidence, customers, and conflicts.

## Product Name

**CascadeCare Network Command**

Tagline:

> The living case layer for healthcare financial shockwaves.

## Demo Thesis

When one provider goes dark, the payment network feels it first:

- Claims stop flowing.
- Remittance posting collapses.
- Rejections spike.
- Payers disagree about exceptions.
- Providers need liquidity.
- IDR disputes age.
- PHI evidence may be implicated.
- Customer communications diverge.
- Litigation and regulator requests arrive later.

Maestro Case holds this as one evolving case, not disconnected tickets.

## Required User Experience

Create a serious enterprise command-center UI. It should feel like a healthcare operations, legal, and financial risk cockpit, not a marketing landing page.

First screen:

- Network Command Center
- Parent case: `Northstar Network Financial Shockwave`
- Owner: `ClearFlow Health Network`
- Triggering provider: `Northstar Regional Health`
- Current goal
- Crisis day
- Network risk score
- Cash at risk
- Claims impacted
- IDR backlog
- Payers impacted
- Providers impacted
- Open child cases
- Upcoming human decisions
- Case goal change banner
- Participant role change banner

Core views:

1. Command Center
2. Shockwave Timeline
3. Child Case Board
4. Participant / Role Graph
5. Evidence Graph
6. Agent Workspace
7. Human Decision Queue
8. Executive Brief

## Demo Event Buttons

Create prominent but professional demo controls:

1. `Day 0: Ingest Network Telemetry`
2. `Day 3: PHI Exfiltration Signal`
3. `Day 14: Provider Liquidity Stress`
4. `Day 21: Class Action Filed`
5. `Day 45: Insurance Reservation`
6. `Day 60: Payer/Provider Conflict`
7. `Day 90: Cross-Proceeding Request`
8. `Reset Demo`

Each button mutates the case state, adds timeline events, updates child cases, updates evidence, and creates or reopens decisions.

## State Progression

### Initial State

No active crisis.

Dashboard shows normal network baselines:

- Daily claims: 42,800
- 837 rejection rate: 2.1%
- Remittance posting rate: 98.4%
- Active IDR disputes: 1,240
- Network risk score: 12

### Day 0

Network telemetry detects:

- Claims down 91%
- 837 rejection rate up to 64%
- Remittance posting down 73%
- 277 status inquiries up 310%
- Northstar-related IDR disputes aging abnormally

Create parent case:

- `CASE-2026-CF-0421-SHOCKWAVE`
- Current goal: `Classify network shock and stabilize financial flows`

Open child cases:

- Network Flow Anomaly
- Provider Recovery Support
- Payer Coordination

Case manager says:

> ClearFlow has detected a healthcare financial shockwave. The current goal is to determine whether this is a feed issue, provider downtime, cyber disruption, or reportable data event while stabilizing claims and payments across affected payers and providers.

### Day 3

Provider forensic signal says PHI exfiltration likely occurred before encryption.

Change current goal:

`Stabilize network flows and preserve breach-related evidence`

Open child cases:

- Business Associate Exposure
- Evidence Preservation
- Customer Communications

Add evidence:

- Forensic PHI signal
- Data-flow map
- Claim file PHI exposure risk

Create decision:

- `Approve PHI/BAA evidence scope`

### Day 14

Northstar liquidity stress emerges.

Metrics:

- Cash at risk: `$47.8M`
- Claims impacted: `83,420`
- Payroll-critical reimbursement exposure: `$12.4M`

Open or escalate:

- Payment and Remittance Continuity
- Claims Revenue Stabilization
- Payer Coordination

Robot actions:

- Generate payer exception packets
- Generate provider recovery report

Create decision:

- `Approve payer exception request bundle`

### Day 21

Patient class action is filed.

Open:

- Regulator and Litigation Support

Actions:

- Apply legal hold to selected evidence
- Restrict operational team access to privileged artifacts
- Flag ClearFlow logs as potentially discoverable

Create decision:

- `Approve litigation evidence hold scope`

### Day 45

Provider cyber insurer issues reservation of rights.

Actions:

- Preserve payment-delay and claims-backlog evidence
- Escalate Board Risk Oversight
- Run Statement Consistency Agent across customer notices, board brief, and insurer packet

Create decision:

- `Approve insurance-facing evidence packet`

### Day 60

Payer/provider conflict appears:

- Northstar asks ClearFlow to pause IDR objections and payment-integrity challenges for crisis-related claims.
- Apex Health Plan asks ClearFlow to maintain normal controls and objections.

Open or reopen:

- Conflict Governance
- IDR Posture

Change ClearFlow role:

- From `recovery_coordinator`
- To `conflict_governed_intermediary`

Create major human decision:

- `Change IDR posture for Northstar crisis-related disputes?`

Options:

- Continue all controls
- Pause crisis-related objections
- Settle high-value disputes
- Route to neutral review

Agent recommendation:

- `route_to_neutral_review`

### Day 90

Regulator/litigation request overlaps prior communications.

Actions:

- Evidence and Access Control reopens
- Statement Consistency Agent flags inconsistent wording
- Privilege and Access Agent recommends scoped production packages
- Executive brief updates

Create decision:

- `Approve scoped evidence production package`

## Data Objects

Implement static data in JSON/TS modules.

### Case

Fields:

- `id`
- `type`
- `name`
- `ownerOrg`
- `triggeringProvider`
- `status`
- `currentGoal`
- `goalHistory`
- `networkRiskScore`
- `currentDay`
- `cashAtRisk`
- `claimsImpacted`
- `idrBacklog`
- `payersImpacted`
- `providersImpacted`
- `childCaseIds`
- `participantIds`
- `evidenceIds`
- `timelineEventIds`
- `decisionIds`

### Child Case

Fields:

- `id`
- `type`
- `title`
- `status`
- `stage`
- `owner`
- `participants`
- `deadline`
- `risk`
- `summary`
- `dependencies`
- `evidenceIds`
- `decisionIds`

Statuses:

- `not_triggered`
- `monitoring`
- `active`
- `blocked`
- `conflict_governed`
- `evidence_hold`
- `closed`

### Participant

Fields:

- `id`
- `name`
- `orgType`
- `currentRole`
- `roleHistory`
- `accessScope`
- `conflictStatus`
- `summary`

### Evidence

Fields:

- `id`
- `title`
- `source`
- `day`
- `classification`
- `privilege`
- `linkedCaseIds`
- `accessScope`
- `summary`
- `confidence`
- `underLegalHold`

### Decision

Fields:

- `id`
- `title`
- `day`
- `status`
- `requiredApprovers`
- `options`
- `agentRecommendation`
- `rationale`
- `linkedCaseIds`

## Agents To Simulate

Agents can be deterministic functions returning rich reasoning text. If LLMs are available, use them only behind these clear interfaces.

1. **Case Manager Agent**
   - Maintains current goal.
   - Recommends child cases.
   - Reopens stages.
   - Detects stale approvals.

2. **Network Flow Anomaly Agent**
   - Explains claim/remittance/IDR anomalies.
   - Estimates shock type and cash at risk.

3. **Business Associate Exposure Agent**
   - Maps PHI-bearing flows.
   - Recommends evidence scope.

4. **Payment Continuity Agent**
   - Prioritizes claims and payer exception requests.

5. **IDR Posture Agent**
   - Recommends continue/pause/settle/neutral review.

6. **Conflict Governance Agent**
   - Detects payer/provider conflict.
   - Recommends approval structure.

7. **Privilege and Access Agent**
   - Classifies evidence and access scopes.

8. **Statement Consistency Agent**
   - Compares statements across packets and flags conflicts.

## Robot Actions To Simulate

Robot actions should create timeline events and visible artifacts.

1. **Network Telemetry Robot**
   - Imports synthetic network data.

2. **Payer Outreach Robot**
   - Generates payer exception packet.

3. **Provider Support Robot**
   - Generates provider recovery report.

4. **IDR Action Packet Robot**
   - Generates neutral-review packet.

5. **Evidence Hold Robot**
   - Marks evidence under legal hold.

6. **Customer Communications Robot**
   - Generates payer/provider notices.

7. **Evidence Production Robot**
   - Generates scoped evidence packet.

8. **Executive Brief Robot**
   - Generates executive/board brief.

## Visual Design Guidance

Style:

- Serious, premium enterprise command center.
- Dense but legible.
- Avoid hero marketing layout.
- Avoid playful colors.
- Use restrained but varied palette: white/near-white surfaces, charcoal text, muted teal, amber, red, blue status colors.
- Use compact cards only for repeated items.
- Avoid giant gradients and decorative blobs.

Expected components:

- KPI strip
- Timeline
- Case board
- Evidence graph/list
- Participant graph
- Decision modal
- Agent recommendation panel
- Generated packet preview
- Executive brief preview

Use icons for:

- Case
- Timeline
- Evidence
- Lock/privilege
- Alert
- Payment
- Hospital/provider
- Payer
- Decision
- Robot/action
- Agent/reasoning

## Acceptance Criteria

The demo must satisfy all of these:

1. ClearFlow owns the parent case.
2. Northstar is only the triggering provider.
3. The first event is network financial telemetry, not SOC detection.
4. The parent case goal changes at least three times.
5. At least five child cases open.
6. IDR Posture reopens on Day 60.
7. ClearFlow role changes to conflict-governed intermediary.
8. Evidence access differs by participant.
9. At least four human decisions appear.
10. At least three robot actions generate artifacts.
11. Executive brief reflects current case state.
12. No real healthcare intermediary, payer, provider, insurer, litigation, or patient names appear.

## Guardrails

- Use no real vendor names in UI, code, screenshots, narration, or sample docs.
- Do not reference real litigation.
- Do not create legal advice. Label all legal outputs as decision-support drafts for counsel review.
- Do not use real patient data.
- Do not submit to real portals.
- Use fictional claim IDs, patient IDs, payer IDs, contract IDs, and case numbers.

## Suggested File Structure

```txt
src/
  app/
  components/
    CommandCenter.*
    ShockwaveTimeline.*
    ChildCaseBoard.*
    ParticipantGraph.*
    EvidenceGraph.*
    AgentWorkspace.*
    DecisionModal.*
    ExecutiveBrief.*
  data/
    initialState.*
    demoEvents.*
    participants.*
    childCases.*
    evidence.*
    decisions.*
  agents/
    caseManager.*
    networkFlowAnomaly.*
    businessAssociateExposure.*
    paymentContinuity.*
    idrPosture.*
    conflictGovernance.*
    privilegeAccess.*
    statementConsistency.*
  robots/
    payerOutreach.*
    providerSupport.*
    idrActionPacket.*
    evidenceHold.*
    customerComms.*
    evidenceProduction.*
    executiveBrief.*
  state/
    caseStore.*
```

## Demo Closing Line

> The malware event happened at one provider. The crisis happened in the network. CascadeCare Network Command gives that shockwave one living case, one evidence graph, evolving participants, agentic reasoning, robot execution, and human judgment.

