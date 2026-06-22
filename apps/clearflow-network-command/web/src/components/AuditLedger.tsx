import { useCallback, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { Entities } from '@uipath/uipath-typescript/entities';
import type { EntityGetResponse, EntityRecord } from '@uipath/uipath-typescript/entities';
import type { PaginatedResponse } from '@uipath/uipath-typescript/core';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { REFRESH_INTERVAL_MS } from '../config';
import { formatTime } from '../caseUtils';
import { Panel, PanelError, PanelLoading } from './Panel';
import {
  AUDIT_ENTITY_ID,
  AUDIT_ENTITY_NAME,
  contentHash,
  dispositionChipClasses,
  groupRuns,
  rowTimestamp,
  stakeholderLabel,
  toAuditRow,
} from '../auditLedger';
import type { AuditRow, LedgerRun } from '../auditLedger';

/** A function that returns one page of EntityRecords given an optional cursor. */
type PageFetcher = (cursor?: PaginatedResponse<EntityRecord>['nextCursor']) => Promise<PaginatedResponse<EntityRecord>>;

/** Cursor-loop a paginated record source into a flat array (6 rows per run). */
async function pageAll(fetchPage: PageFetcher): Promise<EntityRecord[]> {
  const records: EntityRecord[] = [];
  let cursor: PaginatedResponse<EntityRecord>['nextCursor'] | undefined;
  for (;;) {
    const page = await fetchPage(cursor);
    records.push(...page.items);
    if (!page.hasNextPage || !page.nextCursor) break;
    cursor = page.nextCursor;
  }
  return records;
}

/**
 * Read every record of the tenant-scoped AuditRecord entity. The entity lives at
 * the tenant level (FolderId all-zeros), so NO folderKey is passed — mirroring
 * the audit-ledger-writer agent's read path.
 *
 * PRIMARY path reads records DIRECTLY by the known entity id
 * (`entities.getAllRecords(AUDIT_ENTITY_ID, …)`) — this needs only the granted
 * `DataFabric.Data.Read` user scope and AVOIDS the list-entities call
 * (`entities.getAll()`), which can require a schema/list scope the app does not
 * have. The by-name resolution is kept ONLY as a defensive fallback for the
 * unlikely case the entity id ever changes (id read 404s) yet records remain
 * readable by name. A genuine missing-scope failure on the id read propagates to
 * the panel as an error rather than being masked.
 */
async function fetchAuditRows(entities: Entities): Promise<AuditRow[]> {
  const records = await pageAll((cursor) =>
    entities.getAllRecords(AUDIT_ENTITY_ID, {
      pageSize: 200,
      ...(cursor ? { cursor } : {}),
    }) as Promise<PaginatedResponse<EntityRecord>>,
  ).catch(async (idErr) => {
    // The known id failed (e.g. entity recreated with a new id). Try resolving
    // the entity by name as a last resort; if that ALSO fails, surface the
    // original id-read error so a real scope problem isn't hidden.
    try {
      const all = await entities.getAll();
      const entity = all.find((e: EntityGetResponse) => e.name === AUDIT_ENTITY_NAME);
      if (!entity) throw idErr;
      return pageAll((cursor) =>
        entity.getAllRecords({
          pageSize: 200,
          ...(cursor ? { cursor } : {}),
        }) as Promise<PaginatedResponse<EntityRecord>>,
      );
    } catch {
      throw idErr;
    }
  });
  return records.map(toAuditRow);
}

function ImmutableBadge({ hash }: { hash: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent-glow"
      title="Immutable ledger entry — content fingerprint of this row"
    >
      <span className="text-accent">⛓</span>
      <span className="font-mono tracking-tight">{hash}</span>
    </span>
  );
}

function LedgerRow({ row, index }: { row: AuditRow; index: number }) {
  return (
    <motion.tr
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.04, 0.3) }}
      className="border-b border-ink-700/50 last:border-b-0 align-top hover:bg-ink-800/40 transition-colors"
    >
      <td className="py-2.5 pr-3">
        <span className="block font-mono text-[11px] text-slate-300 break-all" title={row.auditRecordId}>
          {row.auditRecordId || '—'}
        </span>
        <span className="block text-[10px] text-slate-600 font-mono">{row.obligationId}</span>
      </td>
      <td className="py-2.5 pr-3">
        <span className="block text-sm text-slate-200 truncate" title={stakeholderLabel(row.stakeholder)}>
          {stakeholderLabel(row.stakeholder)}
        </span>
        <span className="block text-[11px] text-slate-500 truncate" title={row.obligationType}>
          {row.obligationType || '—'}
        </span>
      </td>
      <td className="py-2.5 pr-3 whitespace-nowrap">
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${dispositionChipClasses(row.disposition)}`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
          {row.disposition || 'unknown'}
        </span>
        <span className="mt-1 block text-[10px] uppercase tracking-[0.1em] text-slate-600">
          {row.privilegeFlag || 'no privilege'} · {row.requestingParty || '—'}
        </span>
      </td>
      <td className="py-2.5 pr-3 max-w-[20rem]">
        <p className="text-xs text-slateUI leading-snug line-clamp-2" title={row.auditSummary}>
          {row.auditSummary || '—'}
        </p>
        <span className="text-[10px] text-slate-600">{row.jurisdiction}</span>
      </td>
      <td className="py-2.5 pr-3 whitespace-nowrap text-[11px] text-slate-500 tabular-nums">
        {formatTime(rowTimestamp(row))}
      </td>
      <td className="py-2.5 whitespace-nowrap">
        <ImmutableBadge hash={contentHash(row)} />
      </td>
    </motion.tr>
  );
}

function LedgerTable({ run }: { run: LedgerRun }) {
  return (
    <div className="overflow-x-auto -mx-1 px-1">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="border-b border-ink-700 text-[10px] uppercase tracking-[0.12em] text-slate-500">
            <th className="py-2 pr-3 font-semibold">Record · Obligation</th>
            <th className="py-2 pr-3 font-semibold">Stakeholder · Type</th>
            <th className="py-2 pr-3 font-semibold">Disposition</th>
            <th className="py-2 pr-3 font-semibold">Audit narrative</th>
            <th className="py-2 pr-3 font-semibold">Recorded</th>
            <th className="py-2 font-semibold">Integrity</th>
          </tr>
        </thead>
        <tbody>
          {run.rows.map((row, i) => (
            <LedgerRow key={row.recordKey || row.auditRecordId} row={row} index={i} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Run picker — lets a reviewer page back through prior runs' ledgers. */
function RunSelector({
  runs, selected, onSelect,
}: { runs: LedgerRun[]; selected: string; onSelect: (caseRef: string) => void }) {
  if (runs.length <= 1) return null;
  return (
    <label className="flex items-center gap-2 text-xs text-slate-500">
      <span className="hidden sm:inline">Run</span>
      <select
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        className="rounded-lg border border-ink-600 bg-ink-900/70 px-2.5 py-1 text-xs text-slate-200 focus:border-accent/50 focus:outline-none"
      >
        {runs.map((run, i) => (
          <option key={run.caseRef} value={run.caseRef}>
            {run.caseRef}{i === 0 ? ' · latest' : ''} ({run.rows.length})
          </option>
        ))}
      </select>
    </label>
  );
}

/**
 * Compliance Ledger — live view of the immutable AuditRecord Data Fabric entity.
 *
 * Reads every ledger row through the browser SDK's Entities service (same auth
 * + token the rest of the dashboard uses). The read needs the Data Fabric user
 * scope `DataFabric.Data.Read` (resource `DataFabricOpenApi`) — granted on the
 * external-app registration and requested in VITE_UIPATH_SCOPE. NOTE: the tenant
 * exposes Data Fabric ONLY as `DataFabric.Data.Read`; there is no `DataService.*`
 * scope here, so requesting `DataService.Data.Read` fails sign-in with
 * invalid_scope. Rows are grouped by case reference into runs; the most-recent
 * run shows by default and a selector exposes prior runs. A fresh master run's
 * six rows appear automatically — no code change — because grouping is data-driven.
 */
export function AuditLedger() {
  const { sdk, isAuthenticated } = useAuth();
  const entities = useMemo(() => new Entities(sdk), [sdk]);
  const [selectedCaseRef, setSelectedCaseRef] = useState<string | null>(null);

  const fetchRows = useCallback(() => fetchAuditRows(entities), [entities]);

  const { data: rows, isLoading, error, lastUpdated } = usePolling<AuditRow[]>({
    fetchFn: fetchRows,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
  });

  const runs = useMemo(() => groupRuns(rows ?? []), [rows]);
  const activeRun = useMemo(() => {
    if (runs.length === 0) return null;
    return runs.find((r) => r.caseRef === selectedCaseRef) ?? runs[0];
  }, [runs, selectedCaseRef]);

  const totalRows = rows?.length ?? 0;

  let body: ReactNode;
  if (error && !rows) {
    body = <PanelError message={`Failed to load audit ledger: ${error.message}`} />;
  } else if (isLoading && !rows) {
    body = <PanelLoading label="Loading compliance ledger…" />;
  } else if (!activeRun || activeRun.rows.length === 0) {
    body = (
      <p className="py-8 text-center text-sm text-slate-500">
        No ledger rows for the latest run yet — six immutable rows are written when the master case
        reaches its Closed stage.
      </p>
    );
  } else {
    body = (
      <div className="space-y-3">
        {error && <PanelError message={`Refresh failed: ${error.message}`} />}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-500">
            Run{' '}
            <span className="font-mono text-slate-300">{activeRun.caseRef}</span>{' '}
            · {activeRun.rows.length} immutable rows · written {formatTime(activeRun.recordedAt)}
          </div>
          <RunSelector
            runs={runs}
            selected={activeRun.caseRef}
            onSelect={setSelectedCaseRef}
          />
        </div>
        <LedgerTable run={activeRun} />
      </div>
    );
  }

  const subtitle = lastUpdated
    ? `Immutable AuditRecord entity · ${runs.length} run${runs.length === 1 ? '' : 's'} · ${totalRows} rows`
    : 'Immutable AuditRecord Data Fabric entity';

  return (
    <Panel
      id="ledger"
      title="Compliance Ledger"
      subtitle={subtitle}
      action={
        <span className="text-xs text-slate-500 whitespace-nowrap">Data Fabric · live</span>
      }
    >
      {body}
    </Panel>
  );
}
