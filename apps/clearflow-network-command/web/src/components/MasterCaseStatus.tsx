import { useCallback, useMemo } from 'react';
import { CaseInstances } from '@uipath/uipath-typescript/cases';
import type { CaseGetStageResponse, CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { REFRESH_INTERVAL_MS } from '../config';
import { formatTime, getDisplayLabel, getExternalId } from '../caseUtils';
import { Panel, PanelError, PanelLoading, StatusChip } from './Panel';

interface MasterCaseStatusProps {
  master: CaseInstanceGetResponse | null;
  parentLoading: boolean;
}

function StageList({ master }: { master: CaseInstanceGetResponse }) {
  const { sdk, isAuthenticated } = useAuth();
  const caseInstances = useMemo(() => new CaseInstances(sdk), [sdk]);

  const fetchStages = useCallback(
    () => caseInstances.getStages(master.instanceId, master.folderKey),
    [caseInstances, master.instanceId, master.folderKey],
  );

  const { data: stages, isLoading, error } = usePolling<CaseGetStageResponse[]>({
    fetchFn: fetchStages,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
    deps: [master.instanceId],
  });

  if (error && !stages) return <PanelError message={`Failed to load stages: ${error.message}`} />;
  if (isLoading && !stages) return <PanelLoading label="Loading stages…" />;
  if (!stages || stages.length === 0) {
    return <p className="text-sm text-slate-500">No stage data available.</p>;
  }

  return (
    <div>
      {error && <div className="mb-2"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
      <ul>
        {stages.map(stage => (
          <li key={stage.id} className="flex items-center gap-3 py-2 border-b border-slate-800/60 last:border-b-0">
            <div className="min-w-0 flex-1">
              <span className="text-sm text-slate-200 block truncate" title={stage.name}>{stage.name}</span>
            </div>
            <StatusChip status={stage.status} />
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Latest master crisis instance: run status + stage progression. */
export function MasterCaseStatus({ master, parentLoading }: MasterCaseStatusProps) {
  return (
    <Panel title="Master Case Status" subtitle="clearflow-master-crisis — most recent instance">
      {!master ? (
        parentLoading
          ? <PanelLoading label="Loading master case…" />
          : <p className="text-sm text-slate-500 py-4 text-center">No master crisis case instance found.</p>
      ) : (
        <div>
          <div className="flex items-center gap-3 mb-3 min-w-0">
            <div className="min-w-0 flex-1">
              <div className="text-sm text-slate-200 truncate" title={getDisplayLabel(master)}>
                {getDisplayLabel(master)}
              </div>
              <div
                className="text-xs text-slate-500 font-mono truncate"
                title={`${getExternalId(master)} · started ${formatTime(master.startedTime)}`}
              >
                {getExternalId(master)} · started {formatTime(master.startedTime)}
              </div>
            </div>
            <StatusChip status={master.latestRunStatus} />
          </div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Stages</h3>
          <StageList master={master} />
        </div>
      )}
    </Panel>
  );
}
