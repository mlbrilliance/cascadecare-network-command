/**
 * AuditRecord compliance-ledger data utilities (pure, framework-free).
 *
 * The immutable `AuditRecord` Data Fabric entity holds one survey-ready row per
 * dispositioned obligation grandchild — six rows per master case run, keyed on
 * the run's case reference (e.g. `AUD-CFCS-67730745-northstar`). The dashboard
 * reads every row live and shows the most-recent run's ledger by default, with
 * a selector for prior runs. Nothing here is baked: a fresh run's six rows
 * appear automatically because grouping is purely data-driven.
 *
 * Field-name resilience: Data Fabric stores fields camelCased (`auditRecordId`)
 * but is observed to PascalCase them on some read paths (`AuditRecordId`). The
 * audit-ledger-writer agent guards against both casings; we mirror that here so
 * the table never silently renders blanks if the API casing shifts.
 */
import type { EntityRecord } from '@uipath/uipath-typescript/entities';
import { STAKEHOLDERS } from './narrative';

/** Tenant-scoped Data Fabric entity that holds the immutable audit ledger. */
export const AUDIT_ENTITY_NAME = 'AuditRecord';

/** A normalised ledger row, decoded from a raw Data Fabric EntityRecord. */
export interface AuditRow {
  /** Data Fabric record UUID (the `Id` system field) — stable React key. */
  recordKey: string;
  auditRecordId: string;
  caseRef: string;
  stakeholder: string;
  obligationId: string;
  obligationType: string;
  disposition: string;
  privilegeFlag: string;
  jurisdiction: string;
  requestingParty: string;
  /** Recording timestamp supplied by the writer (ISO-8601 or ''). */
  recordedAt: string;
  auditSummary: string;
  /** Data Fabric system create time — the durable "written at" moment. */
  createdTime: string;
}

/** One run's ledger: all rows sharing a caseRef, plus a sortable timestamp. */
export interface LedgerRun {
  caseRef: string;
  rows: AuditRow[];
  /** Most recent timestamp across the run's rows (for "latest run" ordering). */
  recordedAt: string;
}

/**
 * Read a field from a raw record regardless of camelCase / PascalCase casing.
 * Tries the exact name, then a capitalised-first-letter variant, then a
 * case-insensitive scan — so `auditRecordId` and `AuditRecordId` both resolve.
 */
export function readField(record: EntityRecord, name: string): string {
  const cap = name.charAt(0).toUpperCase() + name.slice(1);
  const direct = record[name] ?? record[cap];
  if (direct != null) return String(direct);
  const lower = name.toLowerCase();
  for (const key of Object.keys(record)) {
    if (key.toLowerCase() === lower) {
      const v = record[key];
      if (v != null) return String(v);
    }
  }
  return '';
}

/** Decode a raw Data Fabric record into a typed, casing-resilient AuditRow. */
export function toAuditRow(record: EntityRecord): AuditRow {
  return {
    recordKey: readField(record, 'id') || readField(record, 'auditRecordId'),
    auditRecordId: readField(record, 'auditRecordId'),
    caseRef: readField(record, 'caseRef'),
    stakeholder: readField(record, 'stakeholder'),
    obligationId: readField(record, 'obligationId'),
    obligationType: readField(record, 'obligationType'),
    disposition: readField(record, 'disposition'),
    privilegeFlag: readField(record, 'privilegeFlag'),
    jurisdiction: readField(record, 'jurisdiction'),
    requestingParty: readField(record, 'requestingParty'),
    recordedAt: readField(record, 'recordedAt'),
    auditSummary: readField(record, 'auditSummary'),
    createdTime: readField(record, 'createTime') || readField(record, 'createdTime'),
  };
}

/** Best available timestamp for a row — the writer's recordedAt, else DF createTime. */
export function rowTimestamp(row: AuditRow): string {
  return row.recordedAt || row.createdTime;
}

function timeValue(iso: string): number {
  const t = new Date(iso).getTime();
  return Number.isNaN(t) ? 0 : t;
}

/**
 * Group decoded rows into runs by caseRef, newest run first. Within a run the
 * rows are ordered by stakeholder for a stable, readable table. A run's sort
 * timestamp is the max row timestamp, so a brand-new run rises to the top with
 * no code change.
 */
export function groupRuns(rows: AuditRow[]): LedgerRun[] {
  const byCase = new Map<string, AuditRow[]>();
  for (const row of rows) {
    const key = row.caseRef || '(unknown)';
    const list = byCase.get(key);
    if (list) list.push(row);
    else byCase.set(key, [row]);
  }

  const runs: LedgerRun[] = [];
  for (const [caseRef, runRows] of byCase) {
    runRows.sort((a, b) => a.stakeholder.localeCompare(b.stakeholder));
    const recordedAt = runRows.reduce(
      (latest, r) => (timeValue(rowTimestamp(r)) > timeValue(latest) ? rowTimestamp(r) : latest),
      '',
    );
    runs.push({ caseRef, rows: runRows, recordedAt });
  }

  runs.sort((a, b) => timeValue(b.recordedAt) - timeValue(a.recordedAt));
  return runs;
}

const DISPLAY_NAME_BY_SLUG: Record<string, string> = Object.fromEntries(
  STAKEHOLDERS.map((s) => [s.slug, s.displayName]),
);

/** Friendly stakeholder label from a slug, falling back to a capitalised slug. */
export function stakeholderLabel(slug: string): string {
  if (!slug) return '—';
  return DISPLAY_NAME_BY_SLUG[slug] ?? slug.charAt(0).toUpperCase() + slug.slice(1);
}

/**
 * Tailwind chip classes for a disposition. "filed" obligations are resolved
 * (green); "withdrawn" is the deliberate compliance-gap the narrative shows
 * (amber); anything else is neutral.
 */
export function dispositionChipClasses(disposition: string): string {
  const d = disposition.toLowerCase();
  if (d.includes('file')) return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40';
  if (d.includes('withdraw')) return 'bg-amber-500/15 text-amber-300 border-amber-500/40';
  return 'bg-slate-500/15 text-slate-300 border-slate-500/40';
}

/**
 * Short, stable content fingerprint for the immutability badge. This is a
 * presentational hash of the row's substantive fields (NOT a cryptographic
 * tamper seal) — it gives each immutable entry a recognisable, monospace
 * "content hash" the way an audit ledger surfaces row integrity. Deterministic
 * for the same content via a DJB2-style fold over the joined fields.
 */
export function contentHash(row: AuditRow): string {
  const material = [
    row.auditRecordId, row.caseRef, row.stakeholder, row.obligationId,
    row.obligationType, row.disposition, row.privilegeFlag, row.jurisdiction,
    row.requestingParty, row.recordedAt,
  ].join('|');
  let h = 5381;
  for (let i = 0; i < material.length; i++) {
    h = ((h << 5) + h + material.charCodeAt(i)) >>> 0;
  }
  return h.toString(16).padStart(8, '0').slice(0, 8);
}
