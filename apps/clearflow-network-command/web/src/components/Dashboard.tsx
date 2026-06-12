import { useCallback, useMemo } from 'react';
import { CaseInstances } from '@uipath/uipath-typescript/cases';
import type {
  CaseInstanceGetAllWithPaginationOptions,
  CaseInstanceGetResponse,
} from '@uipath/uipath-typescript/cases';
import type { PaginatedResponse, PaginationCursor } from '@uipath/uipath-typescript/core';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { MAESTRO_FOLDER_KEY, REFRESH_INTERVAL_MS } from '../config';
import { inferCaseLevel } from '../caseUtils';
import { CascadeTree } from './CascadeTree';
import { MasterCaseStatus } from './MasterCaseStatus';
import { ReversalTimeline } from './ReversalTimeline';
import { HitlGates } from './HitlGates';

interface DashboardProps {
  onLogout: () => void;
}

/** Cursor-loops every page of case instances in the Maestro folder (skill rule 14). */
async function fetchAllCaseInstances(service: CaseInstances): Promise<CaseInstanceGetResponse[]> {
  const all: CaseInstanceGetResponse[] = [];
  let cursor: PaginationCursor | undefined;
  for (;;) {
    const options = {
      folderKey: MAESTRO_FOLDER_KEY,
      pageSize: 100,
      ...(cursor ? { cursor } : {}),
    } as CaseInstanceGetAllWithPaginationOptions;
    // Pagination options are always passed, so the response is paginated.
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

  const fetchCases = useCallback(() => fetchAllCaseInstances(caseInstances), [caseInstances]);

  const { data: instances, isLoading, error, isActive, lastUpdated } = usePolling<CaseInstanceGetResponse[]>({
    fetchFn: fetchCases,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
  });

  // Most recent master crisis instance (level 0, latest startedTime).
  const master = useMemo(() => {
    if (!instances) return null;
    const masters = instances.filter(inst => inferCaseLevel(inst) === 0);
    masters.sort((a, b) => new Date(b.startedTime ?? 0).getTime() - new Date(a.startedTime ?? 0).getTime());
    return masters[0] ?? null;
  }, [instances]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <header className="border-b border-slate-800 bg-slate-900/60">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4 min-w-0">
          <div className="min-w-0 flex-1">
            <h1 className="text-lg font-semibold text-slate-100 truncate" title="ClearFlow Network Command">
              ClearFlow Network Command
            </h1>
            <p className="text-xs text-slate-500 truncate" title="Cyber Crisis Operations — Live Case State">
              Cyber Crisis Operations — Live Case State
            </p>
          </div>
          {isActive && (
            <span className="flex items-center gap-1.5 text-xs text-teal-300 whitespace-nowrap">
              <span className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
              LIVE
            </span>
          )}
          {lastUpdated && (
            <span className="text-xs text-slate-500 whitespace-nowrap hidden sm:inline">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={onLogout}
            className="text-sm text-slate-400 hover:text-slate-100 whitespace-nowrap"
          >
            Sign out
          </button>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="min-w-0">
          <CascadeTree instances={instances} isLoading={isLoading} error={error} />
        </div>
        <div className="space-y-6 min-w-0">
          <MasterCaseStatus master={master} parentLoading={isLoading} />
          <ReversalTimeline />
          <HitlGates />
        </div>
      </main>
    </div>
  );
}
