/**
 * Static narrative single-source for the ClearFlow Network Command dashboard.
 *
 * Ported from the backend data tables (apps/.../backend/dashboard.py) and the
 * agent topology in CLAUDE.md so the React app owns the rich narrative content
 * without a backend round-trip. Data-table idiom — extend by adding a row.
 *
 * All organisation names are committed fictional names (see CLAUDE.md naming
 * conventions); nothing here is IP-sensitive.
 */

export type StakeholderKind = 'provider' | 'payer' | 'vendor';

export interface Stakeholder {
  slug: string;
  displayName: string;
  kind: StakeholderKind;
  stage: string;
}

/** Nine parent stakeholders: 6 providers, 2 active payers, 1 vendor vector. */
export const STAKEHOLDERS: Stakeholder[] = [
  { slug: 'northstar', displayName: 'Northstar Regional Health', kind: 'provider', stage: 'Contain' },
  { slug: 'alpha', displayName: 'Provider Alpha', kind: 'provider', stage: 'Contain' },
  { slug: 'beta', displayName: 'Provider Beta', kind: 'provider', stage: 'Contain' },
  { slug: 'gamma', displayName: 'Provider Gamma', kind: 'provider', stage: 'Contain' },
  { slug: 'delta', displayName: 'Provider Delta', kind: 'provider', stage: 'Contain' },
  { slug: 'epsilon', displayName: 'Provider Epsilon', kind: 'provider', stage: 'Contain' },
  { slug: 'apex', displayName: 'Apex Health Plan', kind: 'payer', stage: 'Notify' },
  { slug: 'summitblue', displayName: 'SummitBlue Medicare Advantage', kind: 'payer', stage: 'Notify' },
  { slug: 'nimbus', displayName: 'Nimbus Patient Engagement Platform', kind: 'vendor', stage: 'Investigate' },
];

/** Provider slugs that receive a TN-DOI grandchild case at Reversal 3. */
export const PROVIDER_SLUGS = STAKEHOLDERS.filter((s) => s.kind === 'provider').map((s) => s.slug);

export interface Reversal {
  n: number;
  name: string;
  day: number;
  wallClockS: number;
  goalFrom: string;
  goalTo: string;
  hero?: boolean;
}

/** Five master-level goal shifts across the 90-day simulated crisis. */
export const REVERSALS: Reversal[] = [
  {
    n: 1, name: 'Multi-customer correlation', day: 1, wallClockS: 20,
    goalFrom: 'Assist isolated customers',
    goalTo: 'Determine if ClearFlow is the vector',
  },
  {
    n: 2, name: 'ClearFlow cleared, Nimbus identified', day: 5, wallClockS: 70,
    goalFrom: 'Determine if ClearFlow is the vector',
    goalTo: 'Bystander posture: strategic decision required',
  },
  {
    n: 3, name: 'State DOI subpoena collision', day: 30, wallClockS: 150,
    goalFrom: 'Bystander posture: strategic decision required',
    goalTo: 'Three-level nesting active: 6 grandchild obligation cases open',
    hero: true,
  },
  {
    n: 4, name: 'Payer demands vs BAAs', day: 45, wallClockS: 200,
    goalFrom: 'Regulatory response in progress',
    goalTo: 'Fiduciary conflict: tri-party HITL gate required',
  },
  {
    n: 5, name: 'Litigation cascade', day: 90, wallClockS: 260,
    goalFrom: 'Fiduciary conflict resolution in progress',
    goalTo: 'Bystander becomes co-defendant: privilege reshuffles',
  },
];

export type AgentKind = 'Coded' | 'Builder';

export interface Agent {
  id: string;
  displayName: string;
  kind: AgentKind;
  llm: string;
  role: string;
}

/** Seven runtime agents — 3 Coded (Python SDK), 4 Agent Builder (BYO Claude). */
export const AGENTS: Agent[] = [
  { id: 'claim-flow-anomaly-detector', displayName: 'Claim Flow Anomaly Detector', kind: 'Coded', llm: 'UiPath', role: 'Classifies anomaly score on claim telemetry' },
  { id: 'multi-customer-pattern-detector', displayName: 'Multi-Customer Pattern Detector', kind: 'Coded', llm: 'UiPath', role: 'Cross-provider correlation; emits cascade signal' },
  { id: 'forensic-self-exam-agent', displayName: 'Forensic Self-Exam Agent', kind: 'Coded', llm: 'UiPath', role: 'Coordinates other agents; routing' },
  { id: 'vector-hypothesis-agent', displayName: 'Vector Hypothesis Agent', kind: 'Builder', llm: 'Claude', role: 'Determines attack vector (ClearFlow vs Nimbus)' },
  { id: 'baa-boundary-reasoner', displayName: 'BAA Boundary Reasoner', kind: 'Builder', llm: 'Claude + Context Grounding', role: 'Analyzes BAA terms; cross-BAA conflicts' },
  { id: 'fiduciary-conflict-detector', displayName: 'Fiduciary Conflict Detector', kind: 'Builder', llm: 'Claude', role: 'Multi-party obligation conflicts; HITL payload' },
  { id: 'negligent-monitoring-risk-agent', displayName: 'Negligent Monitoring Risk Agent', kind: 'Builder', llm: 'Claude', role: 'Co-defendant exposure for Reversal 5' },
];

export interface OverrideAction {
  id: string;
  label: string;
  reversalN: number;
  /** Deployed process name to start (resolved to a key at runtime by name). */
  processName: string;
  /** Input arguments mirrored from the Demo Driver fire-node payloads. */
  payload: Record<string, unknown>;
  tooltip: string;
  hero?: boolean;
}

/**
 * Operator-console actions. Each fires one reversal by starting the matching
 * deployed process with the exact payload the Demo Driver flow uses.
 * R1 starts the master crisis case; R2–R5 start the driving API workflow.
 */
export const OVERRIDES: OverrideAction[] = [
  {
    id: 'fire_r1', label: 'Fire Reversal 1', reversalN: 1,
    processName: 'clearflow-master-crisis',
    payload: {},
    tooltip: 'Starts a fresh master crisis case (Day 1). Multi-customer correlation kicks off.',
  },
  {
    id: 'fire_r2', label: 'Fire Reversal 2', reversalN: 2,
    processName: 'vendor-nimbus',
    payload: {
      event_type: 'vendor-attribution', simulated_day: 5, evidence_signal_strength: 'strong',
      connected_provider_ids: ['northstar', 'alpha', 'beta', 'gamma', 'delta', 'epsilon'],
      clearflow_cleared: true, vector_hypothesis_confidence: 0.87, drives_reversal: 2,
    },
    tooltip: 'ClearFlow cleared; Nimbus identified as the vector (Day 5).',
  },
  {
    id: 'fire_r3', label: 'Fire Reversal 3', reversalN: 3,
    processName: 'regulator-tn-doi',
    payload: {
      event_type: 'regulatory-subpoena', simulated_day: 30, scope: 'all_providers',
      named_provider_ids: ['northstar', 'alpha', 'beta', 'gamma', 'delta', 'epsilon'],
      response_deadline_days: 14, template_id: 'tn-doi-subpoena-2026',
      legal_basis: 'state_market_conduct_exam', drives_reversal: 3,
    },
    tooltip: 'TN DOI subpoena — spawns 6 grandchild obligation cases simultaneously (Day 30).',
    hero: true,
  },
  {
    id: 'fire_r4', label: 'Fire Reversal 4', reversalN: 4,
    processName: 'payer-apex',
    payload: {
      event_type: 'payer-demand', simulated_day: 45, demand_type: 'data_access',
      target_provider_ids: ['northstar', 'alpha', 'beta', 'gamma', 'delta', 'epsilon'],
      contractual_basis: 'audit_rights_clause',
      conflicts_with_baa_ids: ['baa-northstar', 'baa-alpha', 'baa-beta', 'baa-gamma', 'baa-delta', 'baa-epsilon'],
      drives_reversal: 4,
    },
    tooltip: 'Payer demand conflicts with BAAs — opens the tri-party fiduciary HITL gate (Day 45).',
  },
  {
    id: 'fire_r5', label: 'Fire Reversal 5', reversalN: 5,
    processName: 'regulator-tn-doi',
    payload: {
      event_type: 'litigation-event', simulated_day: 90, event_subtype: 'co_defendant_named',
      named_parties: ['ClearFlow Health Network', 'Nimbus Patient Engagement Platform'],
      clearflow_named_co_defendant: true, theory: 'negligent_monitoring',
      privilege_reshuffle_required: true, drives_reversal: 5,
    },
    tooltip: 'Litigation cascade — bystander becomes co-defendant; privilege reshuffles (Day 90).',
  },
];
