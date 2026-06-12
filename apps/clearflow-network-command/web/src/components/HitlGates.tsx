import { useCallback, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { Tasks } from '@uipath/uipath-typescript/tasks';
import type { TaskGetResponse } from '@uipath/uipath-typescript/tasks';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { REFRESH_INTERVAL_MS, TABLE_PAGE_SIZE } from '../config';
import { formatTime } from '../caseUtils';
import { Panel, PanelError, PanelLoading, StatusChip } from './Panel';

interface TaskPage {
  items: TaskGetResponse[];
  hasNextPage: boolean;
  totalCount: number | null;
}

/**
 * Action Center tasks (HITL gates, e.g. the Reversal-4 fiduciary approval).
 * Tasks is an offset-based service, so pagination uses jumpToPage at 25
 * rows per page (skill rule 15).
 */
export function HitlGates() {
  const { sdk, isAuthenticated } = useAuth();
  const tasks = useMemo(() => new Tasks(sdk), [sdk]);
  const [page, setPage] = useState(1);

  const fetchTasks = useCallback(async (): Promise<TaskPage> => {
    const result = await tasks.getAll({ pageSize: TABLE_PAGE_SIZE, jumpToPage: page });
    return {
      items: result.items,
      hasNextPage: 'hasNextPage' in result ? result.hasNextPage : false,
      totalCount: result.totalCount ?? null,
    };
  }, [tasks, page]);

  const { data, isLoading, error } = usePolling<TaskPage>({
    fetchFn: fetchTasks,
    interval: REFRESH_INTERVAL_MS,
    enabled: isAuthenticated,
    deps: [page],
  });

  let body: ReactNode;
  if (error && !data) {
    body = <PanelError message={`Failed to load tasks: ${error.message}`} />;
  } else if (isLoading && !data) {
    body = <PanelLoading label="Loading HITL gates…" />;
  } else if (!data || data.items.length === 0) {
    body = (
      <div>
        {error && <div className="mb-2"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
        <p className="text-sm text-slate-500 py-4 text-center">
          {page > 1 ? 'No tasks on this page.' : 'No HITL gates open yet (the fiduciary gate fires at Reversal 4).'}
        </p>
        {page > 1 && (
          <div className="text-center">
            <button
              onClick={() => setPage(1)}
              className="text-xs text-teal-400 hover:text-teal-300"
            >
              Back to first page
            </button>
          </div>
        )}
      </div>
    );
  } else {
    const from = (page - 1) * TABLE_PAGE_SIZE + 1;
    const to = from + data.items.length - 1;
    body = (
      <div>
        {error && <div className="mb-2"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
        <table className="w-full table-fixed text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-500 uppercase tracking-wider">
              <th className="pb-2 w-1/2">Title</th>
              <th className="pb-2 w-24">Status</th>
              <th className="pb-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(task => (
              <tr key={task.id} className="border-t border-slate-800/60">
                <td className="py-2 max-w-0">
                  <span className="text-slate-200 block truncate" title={task.title}>{task.title}</span>
                  <span className="text-xs text-slate-500 block truncate" title={String(task.type ?? '')}>
                    {String(task.type ?? '')}
                  </span>
                </td>
                <td className="py-2"><StatusChip status={String(task.status ?? '')} /></td>
                <td className="py-2 text-slate-400 max-w-0">
                  <span className="block truncate" title={formatTime(task.createdTime)}>
                    {formatTime(task.createdTime)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
          <span>
            Showing {from}–{to}{data.totalCount !== null ? ` of ${data.totalCount}` : ''}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2 py-1 rounded border border-slate-700 text-slate-300 disabled:opacity-40 hover:bg-slate-800"
            >
              Prev
            </button>
            <span className="text-slate-400">Page {page}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={!data.hasNextPage}
              className="px-2 py-1 rounded border border-slate-700 text-slate-300 disabled:opacity-40 hover:bg-slate-800"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Panel title="HITL Gates" subtitle="Action Center tasks — human approvals across the crisis">
      {body}
    </Panel>
  );
}
