import { useCallback, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { Tasks } from '@uipath/uipath-typescript/tasks';
import type { TaskGetResponse } from '@uipath/uipath-typescript/tasks';
import { useAuth } from '../hooks/useAuth';
import { usePolling } from '../hooks/usePolling';
import { useProcessActions } from '../hooks/useProcessActions';
import { REFRESH_INTERVAL_MS, TABLE_PAGE_SIZE } from '../config';
import { formatTime } from '../caseUtils';
import { Panel, PanelError, PanelLoading, StatusChip } from './Panel';

interface TaskPage {
  items: TaskGetResponse[];
  hasNextPage: boolean;
  totalCount: number | null;
}

function isPending(status: string): boolean {
  const s = status.toLowerCase();
  return !s.includes('complet') && (s.includes('pend') || s.includes('progress') || s.includes('assign') || s.includes('open') || s === 'unassigned');
}

function TaskRow({
  task, onApprove, approving,
}: { task: TaskGetResponse; onApprove: (t: TaskGetResponse) => void; approving: boolean }) {
  const status = String(task.status ?? '');
  return (
    <motion.li
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-3 py-2.5 border-b border-ink-700/50 last:border-b-0"
    >
      <div className="min-w-0 flex-1">
        <span className="text-sm text-slate-200 block truncate" title={task.title}>{task.title}</span>
        <span className="text-xs text-slate-500 block truncate">
          {String(task.type ?? '')} · {formatTime(task.createdTime)}
        </span>
      </div>
      <StatusChip status={status} />
      {isPending(status) && (
        <button
          onClick={() => onApprove(task)}
          disabled={approving}
          className="shrink-0 rounded-lg border border-emerald-500/50 bg-emerald-500/15 px-3 py-1.5 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/25 disabled:opacity-50 transition-all"
        >
          {approving ? '…' : 'Approve'}
        </button>
      )}
    </motion.li>
  );
}

/**
 * Action Center HITL gates (e.g. the Reversal-4 fiduciary approval). Pending
 * gates can be approved inline (Tasks.complete). Offset-paginated at 25/page.
 */
export function HitlGates() {
  const { sdk, isAuthenticated } = useAuth();
  const tasks = useMemo(() => new Tasks(sdk), [sdk]);
  const { state, approveHitl } = useProcessActions();
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
        <p className="text-sm text-slate-500 py-6 text-center">
          {page > 1 ? 'No tasks on this page.' : 'No HITL gates open yet (the fiduciary gate fires at Reversal 4).'}
        </p>
        {page > 1 && (
          <div className="text-center">
            <button onClick={() => setPage(1)} className="text-xs text-accent hover:text-accent-glow">Back to first page</button>
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
        {state.message && state.activeId && (
          <div className={`mb-2 text-xs rounded-lg border px-3 py-2 ${
            state.phase === 'error' ? 'text-rose-300 border-rose-500/30 bg-rose-500/10' : 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10'
          }`}>
            {state.message}
          </div>
        )}
        <ul>
          {data.items.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onApprove={approveHitl}
              approving={state.phase === 'working' && state.activeId === String(task.id)}
            />
          ))}
        </ul>
        <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
          <span>Showing {from}–{to}{data.totalCount !== null ? ` of ${data.totalCount}` : ''}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-2 py-1 rounded border border-ink-600 text-slate-300 disabled:opacity-40 hover:bg-ink-700"
            >
              Prev
            </button>
            <span className="text-slate-400">Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!data.hasNextPage}
              className="px-2 py-1 rounded border border-ink-600 text-slate-300 disabled:opacity-40 hover:bg-ink-700"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Panel title="HITL Gates" subtitle="Action Center tasks — approve human gates inline">
      {body}
    </Panel>
  );
}
