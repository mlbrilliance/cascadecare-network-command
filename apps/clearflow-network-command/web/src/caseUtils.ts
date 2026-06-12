import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';

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
