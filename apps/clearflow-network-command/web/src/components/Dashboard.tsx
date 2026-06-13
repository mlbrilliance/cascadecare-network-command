import { useCallback, useMemo } from 'react';
import { CaseInstances } from '@uipath/uipath-typescript/cases';
import type {
  CaseInstanceGetAllWithPaginationOptions,
  CaseInstanceGetResponse,
} from '@uipath/uipath-typescript/cases';
import { Tasks } from '@uipath/uipath-typescript/tasks';
import type { PaginatedResponse, PaginationCursor } from '@uipath/uipath-typescript/core';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { MAESTRO_FOLDER_KEY, REFRESH_INTERVAL_MS } from '../config';
import { deriveCrisisState } from '../caseUtils';
import { CommandHeader } from './CommandHeader';
import { KpiStrip } from './KpiStrip';
import { CascadeGraph } from './CascadeGraph';
import { ReversalTimeline } from './ReversalTimeline';
import { AgentRoster } from './AgentRoster';
import { OperatorConsole } from './OperatorConsole';
import { HitlGates } from './HitlGates';

interface DashboardProps {
  onLogout: () => void;
}

/** Cursor-loops every page of case instances in the Maestro folder. */
async function fetchAllCaseInstances(service: CaseInstances): Promise<CaseInstanceGetResponse[]> {
  const all: CaseInstanceGetResponse[] = [];
  let cursor: PaginationCursor | undefined;
  for (;;) {
    const options = {
      folderKey: MAESTRO_FOLDER_KEY,
      pageSize: 100,
      ...(cursor ? { cursor } : {}),
    } as CaseInstanceGetAllWithPaginationOptions;
    const page = (await service.getAll(options)) as PaginatedResponse<CaseInstanceGetResponse>;
    all.push(...page.items);
    if (!page.hasNextPage || !page.nextCursor) break;
    cursor = page.nextCursor;
  }
  return all;
}

export function Dashboard({ onLogout }: DashboardProps) {
  const { sdk, isAuthenticated } = useAuth();
  const caseInstances = useMemo(() => new CaseInstances(sdk), [sdk]);
  const tasks = useMemo(() => new Tasks(sdk), [sdk]);

  const fetchCases = useCallback(() => fetchAllCaseInstances(caseInstances), [caseInstances]);
  const fetchHitlCount = useCallback(async () => {
    const r = await tasks.getAll({ pageSize: 100, jumpToPage: 1 });
    return r.totalCount ?? r.items.length;
  }, [tasks]);

  const { data: instances, isLoading, error, isActive, lastUpdated } = usePolling<CaseInstanceGetResponse[]>({
    fetchFn: fetchCases,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
  });

  const { data: hitlCount } = usePolling<number>({
    fetchFn: fetchHitlCount,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
  });

  const crisis = useMemo(() => deriveCrisisState(instances, hitlCount ?? 0), [instances, hitlCount]);

  return (
    <div className="min-h-screen bg-radial-command">
      <CommandHeader crisis={crisis} isActive={isActive} lastUpdated={lastUpdated} onLogout={onLogout} />
      <main className="max-w-[1500px] mx-auto px-5 lg:px-8 py-6 space-y-6">
        <KpiStrip crisis={crisis} />
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
          <div className="xl:col-span-2 space-y-6 min-w-0">
            <CascadeGraph instances={instances} isLoading={isLoading} error={error} />
            <ReversalTimeline currentReversal={crisis.reversalN} />
          </div>
          <div className="space-y-6 min-w-0">
            <OperatorConsole />
            <AgentRoster />
            <HitlGates />
          </div>
        </div>
      </main>
    </div>
  );
}
