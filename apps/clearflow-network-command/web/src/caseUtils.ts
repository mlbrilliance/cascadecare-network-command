import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import { REVERSALS, STAKEHOLDERS } from './narrative';

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

/** Tailwind classes for a status chip (Running=blue, Completed=green, Faulted=red, Paused=amber). */
export function statusChipClasses(status: string | null | undefined): string {
  const s = (status ?? '').toLowerCase();
  if (s.includes('complet')) return 'bg-green-500/15 text-green-300 border-green-500/40';
  if (s.includes('fault') || s.includes('error')) return 'bg-red-500/15 text-red-300 border-red-500/40';
  if (s.includes('paus')) return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
  if (s.includes('run') || s.includes('resum') || s.includes('pend')) return 'bg-blue-500/15 text-blue-300 border-blue-500/40';
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

/** Hex tones for SVG nodes by run status (mirrors statusChipClasses palette). */
export function statusTone(status: string | null | undefined): StatusTone {
  const s = _STATUS_OF(status);
  if (s.includes('complet')) return { fill: '#064e3b', stroke: '#34D399' };
  if (s.includes('fault') || s.includes('error')) return { fill: '#4c0519', stroke: '#F43F5E' };
  if (s.includes('paus')) return { fill: '#451a03', stroke: '#F59E0B' };
  if (s.includes('run') || s.includes('resum') || s.includes('pend')) return { fill: '#082f49', stroke: '#38BDF8' };
  return { fill: '#16273C', stroke: '#64748b' };
}
