import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import { REVERSALS, STAKEHOLDERS } from './narrative';
import type { StakeholderKind } from './narrative';

/** 0 = master crisis, 1 = stakeholder parent, 2 = obligation grandchild. */
export type CaseLevel = 0 | 1 | 2;

export const LEVEL_LABELS: Record<CaseLevel, string> = {
  0: 'Master crisis',
  1: 'Stakeholder parent',
  2: 'Obligation grandchild',
};

/**
 * Infers the cascade level of a case instance from its packageId / processKey
 * naming convention.
 */
export function inferCaseLevel(instance: CaseInstanceGetResponse): CaseLevel | null {
  const haystack = `${instance.packageId ?? ''} ${instance.processKey ?? ''}`.toLowerCase();
  if (haystack.includes('master-crisis')) return 0;
  if (haystack.includes('stakeholder-parent')) return 1;
  if (haystack.includes('obligation-grandchild')) return 2;
  return null;
}

/**
 * Some tenants surface an externalId on case instances; the published type
 * does not declare it, so read it defensively and fall back to instanceId.
 */
export function getExternalId(instance: CaseInstanceGetResponse): string {
  const maybe = (instance as unknown as { externalId?: string | null }).externalId;
  return maybe ?? instance.instanceId;
}

export function getDisplayLabel(instance: CaseInstanceGetResponse): string {
  return instance.caseTitle || instance.instanceDisplayName || instance.packageId || instance.instanceId;
}

/** Tailwind classes for a status chip (Running=orange, Completed=green, Faulted=red, Paused=amber). */
export function statusChipClasses(status: string | null | undefined): string {
  const s = (status ?? '').toLowerCase();
  if (s.includes('complet')) return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40';
  if (s.includes('fault') || s.includes('error')) return 'bg-rose-500/15 text-rose-300 border-rose-500/40';
  if (s.includes('paus')) return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
  if (s.includes('run') || s.includes('resum') || s.includes('pend')) return 'bg-accent/15 text-accent-glow border-accent/40';
  return 'bg-slate-500/15 text-slate-300 border-slate-500/40';
}

export function formatTime(value: string | null | undefined): string {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

/** Ascending sort by startedTime (spawn order). */
export function byStartedTimeAsc(a: CaseInstanceGetResponse, b: CaseInstanceGetResponse): number {
  return new Date(a.startedTime ?? 0).getTime() - new Date(b.startedTime ?? 0).getTime();
}

const _STATUS_OF = (s: string | null | undefined): string => (s ?? '').toLowerCase();

export function isCompleted(inst: CaseInstanceGetResponse): boolean {
  return _STATUS_OF(inst.latestRunStatus).includes('complet');
}

/**
 * Best-effort stakeholder slug for an instance, matched from its label/keys
 * against the known stakeholder slugs. Returns null when none match.
 */
export function slugFromInstance(instance: CaseInstanceGetResponse): string | null {
  const hay = `${getDisplayLabel(instance)} ${instance.packageId ?? ''} ${instance.processKey ?? ''}`.toLowerCase();
  // Longest slug first so 'summitblue' wins before a hypothetical 'blue'.
  for (const slug of [...STAKEHOLDERS.map((s) => s.slug)].sort((a, b) => b.length - a.length)) {
    if (hay.includes(slug)) return slug;
  }
  return null;
}

/**
 * Collapse duplicate spawns to one node per display label, keeping the most
 * recently started. The platform double-delivers spawn messages (12 children
 * from 6 spawn tasks — see docs/DEFERRED-FIXES.md); this keeps the graph clean.
 */
export function dedupeByLabel(instances: CaseInstanceGetResponse[]): CaseInstanceGetResponse[] {
  const best = new Map<string, CaseInstanceGetResponse>();
  for (const inst of instances) {
    const key = getDisplayLabel(inst);
    const prev = best.get(key);
    if (!prev || byStartedTimeAsc(prev, inst) < 0) best.set(key, inst);
  }
  return [...best.values()].sort(byStartedTimeAsc);
}

export interface CrisisCounts {
  total: number;
  completed: number;
  masters: number;
  parents: number;
  grandchildren: number;
  hitlGates: number;
}

export interface CrisisState {
  /** 0 = pre-crisis, 1–5 = furthest reversal reached (inferred from cascade shape). */
  reversalN: number;
  posture: string;
  simulatedDay: number;
  counts: CrisisCounts;
  allComplete: boolean;
}

/**
 * Derive headline crisis state from the live case instances. The reversal is
 * inferred from cascade shape (grandchildren ⇒ R3+, all-complete ⇒ resolved at
 * R5); posture/day come from the static REVERSALS table. hitlGates is supplied
 * by the caller (Action Center tasks live in a separate service).
 */
export function deriveCrisisState(
  instances: CaseInstanceGetResponse[] | null,
  hitlGates = 0,
): CrisisState {
  const all = instances ?? [];
  const masters = all.filter((i) => inferCaseLevel(i) === 0);
  const parents = dedupeByLabel(all.filter((i) => inferCaseLevel(i) === 1));
  const grandchildren = dedupeByLabel(all.filter((i) => inferCaseLevel(i) === 2));
  const completed = all.filter(isCompleted).length;
  const allComplete = all.length > 0 && completed === all.length;

  let reversalN = 0;
  if (grandchildren.length > 0) reversalN = allComplete ? 5 : 4;
  else if (parents.length > 0) reversalN = 2;
  else if (masters.length > 0) reversalN = 1;

  const reversal = REVERSALS.find((r) => r.n === reversalN);
  return {
    reversalN,
    posture: reversal ? reversal.goalTo : 'Awaiting first signal — no active crisis',
    simulatedDay: reversal ? reversal.day : 0,
    counts: {
      total: all.length,
      completed,
      masters: masters.length,
      parents: parents.length,
      grandchildren: grandchildren.length,
      hitlGates,
    },
    allComplete,
  };
}

export interface StatusTone {
  /** Node fill colour for SVG. */
  fill: string;
  /** Node stroke / glow colour for SVG. */
  stroke: string;
}

/**
 * Hex tones for SVG nodes by run status. Disciplined palette: orange = the live
 * crisis energy (running), green = closed, red = faulted, amber = paused, grey =
 * idle/unknown. Green/red are used sparingly — only for discrete terminal states.
 */
export function statusTone(status: string | null | undefined): StatusTone {
  const s = _STATUS_OF(status);
  if (s.includes('complet')) return { fill: '#0E2A1C', stroke: '#34D399' };
  if (s.includes('fault') || s.includes('error')) return { fill: '#2E0F14', stroke: '#F43F5E' };
  if (s.includes('paus')) return { fill: '#2A1C08', stroke: '#D9963B' };
  if (s.includes('run') || s.includes('resum') || s.includes('pend')) return { fill: '#2A1206', stroke: '#F26B1D' };
  return { fill: '#1B1F27', stroke: '#8A929E' };
}

export type RollupStatus = 'running' | 'faulted' | 'paused' | 'completed' | 'idle';

export interface StakeholderRollup {
  /** Canonical slug, or 'other' for instances that matched no known stakeholder. */
  slug: string;
  displayName: string;
  kind: StakeholderKind | 'other';
  /** Aggregate live status across this port's instances. */
  status: RollupStatus;
  /** Raw level-1 parent instances mapped to this stakeholder. */
  parentInstances: CaseInstanceGetResponse[];
  /** Deduped obligation grandchildren under this stakeholder (for the sub-fan). */
  grandchildren: CaseInstanceGetResponse[];
  /** Raw count of every instance (parents + grandchildren) rolled into this port. */
  rawCount: number;
  /** Open (not-completed) obligation grandchildren — drives the ▸N badge. */
  openObligations: number;
}

/** Worst-of aggregate status for a port (faulted ≻ running ≻ paused ≻ completed ≻ idle). */
function aggregateStatus(insts: CaseInstanceGetResponse[]): RollupStatus {
  if (insts.length === 0) return 'idle';
  let running = false;
  let paused = false;
  let anyOpen = false;
  for (const i of insts) {
    const s = _STATUS_OF(i.latestRunStatus);
    if (s.includes('fault') || s.includes('error')) return 'faulted';
    if (s.includes('run') || s.includes('resum') || s.includes('pend')) running = true;
    if (s.includes('paus')) paused = true;
    if (!s.includes('complet')) anyOpen = true;
  }
  if (running) return 'running';
  if (paused) return 'paused';
  return anyOpen ? 'idle' : 'completed';
}

/**
 * Roll up every live instance into the canonical stakeholder ports for the
 * Energy-Flow cascade. Always emits all 9 known stakeholders (idle ports render
 * as inactive), plus an "Other" port when instances matched no known slug — so
 * the ~71 raw + ~34 grandchild instances are fully reconciled, never truncated.
 */
export function rollupStakeholders(
  instances: CaseInstanceGetResponse[] | null,
): StakeholderRollup[] {
  const all = instances ?? [];
  const parents = all.filter((i) => inferCaseLevel(i) === 1);
  const grandchildren = all.filter((i) => inferCaseLevel(i) === 2);

  const build = (
    slug: string,
    displayName: string,
    kind: StakeholderKind | 'other',
    matchedParents: CaseInstanceGetResponse[],
    matchedGrand: CaseInstanceGetResponse[],
  ): StakeholderRollup => {
    const dedupGrand = dedupeByLabel(matchedGrand);
    return {
      slug,
      displayName,
      kind,
      status: aggregateStatus([...matchedParents, ...matchedGrand]),
      parentInstances: matchedParents,
      grandchildren: dedupGrand,
      rawCount: matchedParents.length + matchedGrand.length,
      openObligations: dedupGrand.filter((g) => !isCompleted(g)).length,
    };
  };

  const ports: StakeholderRollup[] = STAKEHOLDERS.map((s) =>
    build(
      s.slug,
      s.displayName,
      s.kind,
      parents.filter((p) => slugFromInstance(p) === s.slug),
      grandchildren.filter((g) => slugFromInstance(g) === s.slug),
    ),
  );

  const unmatchedParents = parents.filter((p) => slugFromInstance(p) === null);
  const unmatchedGrand = grandchildren.filter((g) => slugFromInstance(g) === null);
  if (unmatchedParents.length + unmatchedGrand.length > 0) {
    ports.push(build('other', 'Other instances', 'other', unmatchedParents, unmatchedGrand));
  }

  return ports;
}
