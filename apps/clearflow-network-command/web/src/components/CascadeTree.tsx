import type { ReactNode } from 'react';
import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import {
  LEVEL_LABELS,
  byStartedTimeAsc,
  formatTime,
  getDisplayLabel,
  getExternalId,
  inferCaseLevel,
} from '../caseUtils';
import type { CaseLevel } from '../caseUtils';
import { Panel, PanelError, PanelLoading, StatusChip } from './Panel';

interface CascadeTreeProps {
  instances: CaseInstanceGetResponse[] | null;
  isLoading: boolean;
  error: Error | null;
}

function CaseRow({ instance, depth }: { instance: CaseInstanceGetResponse; depth: number }) {
  const label = getDisplayLabel(instance);
  const externalId = getExternalId(instance);
  const meta = `${externalId} · started ${formatTime(instance.startedTime)}`;
  return (
    <li
      className="flex items-center gap-3 py-2 border-b border-slate-800/60 last:border-b-0"
      style={{ paddingLeft: depth * 24 }}
    >
      {depth > 0 && <span className="text-slate-600 text-xs shrink-0">{'└'}</span>}
      <div className="min-w-0 flex-1">
        <div className="text-sm text-slate-200 truncate" title={label}>{label}</div>
        <div className="text-xs text-slate-500 font-mono truncate" title={meta}>{meta}</div>
      </div>
      <StatusChip status={instance.latestRunStatus} />
    </li>
  );
}

/**
 * Three-level cascade: master crisis (level 0) → stakeholder parents (level 1)
 * → obligation grandchildren (level 2). Levels are inferred from packageId /
 * processKey naming; the tree is rendered by level with indentation.
 */
export function CascadeTree({ instances, isLoading, error }: CascadeTreeProps) {
  let body: ReactNode;

  if (error && !instances) {
    body = <PanelError message={`Failed to load case instances: ${error.message}`} />;
  } else if (isLoading && !instances) {
    body = <PanelLoading label="Loading cascade…" />;
  } else {
    const all = instances ?? [];
    const byLevel: Record<CaseLevel, CaseInstanceGetResponse[]> = { 0: [], 1: [], 2: [] };
    const unclassified: CaseInstanceGetResponse[] = [];
    for (const inst of all) {
      const level = inferCaseLevel(inst);
      if (level === null) unclassified.push(inst);
      else byLevel[level].push(inst);
    }
    ([0, 1, 2] as CaseLevel[]).forEach(l => byLevel[l].sort(byStartedTimeAsc));
    unclassified.sort(byStartedTimeAsc);

    const total = all.length;
    if (total === 0) {
      body = <p className="text-sm text-slate-500 py-6 text-center">No case instances found in the Maestro folder yet.</p>;
    } else {
      body = (
        <div>
          {error && <div className="mb-2"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
          <p className="text-xs text-slate-500 mb-2">
            {byLevel[0].length} master · {byLevel[1].length} stakeholder parents · {byLevel[2].length} obligation grandchildren
          </p>
          <ul>
            {byLevel[0].map(inst => <CaseRow key={inst.instanceId} instance={inst} depth={0} />)}
            {byLevel[1].map(inst => <CaseRow key={inst.instanceId} instance={inst} depth={1} />)}
            {byLevel[2].map(inst => <CaseRow key={inst.instanceId} instance={inst} depth={2} />)}
          </ul>
          {byLevel[2].length === 0 && (
            <p className="text-xs text-slate-600 italic mt-2 pl-12">
              No grandchild cases yet (spawn at Reversal 3)
            </p>
          )}
          {unclassified.length > 0 && (
            <div className="mt-4">
              <h3 className="text-xs font-semibold text-slate-500 uppercase mb-1">Other case instances</h3>
              <ul>
                {unclassified.map(inst => <CaseRow key={inst.instanceId} instance={inst} depth={0} />)}
              </ul>
            </div>
          )}
        </div>
      );
    }
  }

  return (
    <Panel
      title="Cascade Tree"
      subtitle={`${LEVEL_LABELS[0]} → ${LEVEL_LABELS[1]} → ${LEVEL_LABELS[2]}`}
    >
      {body}
    </Panel>
  );
}
