import { useCallback, useMemo, useState } from 'react';
import { Processes } from '@uipath/uipath-typescript/processes';
import { Tasks, TaskType } from '@uipath/uipath-typescript/tasks';
import type { TaskGetResponse } from '@uipath/uipath-typescript/tasks';
import { useAuth } from './useAuth';
import { MAESTRO_FOLDER_KEY } from '../config';
import type { OverrideAction } from '../narrative';

export type ActionPhase = 'idle' | 'working' | 'done' | 'error';

export interface ActionState {
  phase: ActionPhase;
  message: string | null;
  /** id of the action currently/last touched, for per-button UI feedback. */
  activeId: string | null;
}

const SCOPE_HINT =
  'Action blocked — this app needs the OR.Execution.Create / OR.Tasks.Edit scopes granted in the tenant.';

function describeError(err: unknown): string {
  const msg = err instanceof Error ? err.message : String(err);
  if (/scope|forbidden|unauthor|permission|403/i.test(msg)) return SCOPE_HINT;
  return msg;
}

/**
 * Operator-console write actions over the browser SDK:
 *   fireReversal — starts the reversal's process with the Demo Driver payload
 *                  (Processes.start; needs OR.Execution.Create).
 *   approveHitl  — completes an Action Center App task / HITL gate
 *                  (Tasks.complete; needs OR.Tasks.Edit).
 * Single shared ActionState drives toasts + per-button spinners.
 */
export function useProcessActions() {
  const { sdk } = useAuth();
  const processes = useMemo(() => new Processes(sdk), [sdk]);
  const tasks = useMemo(() => new Tasks(sdk), [sdk]);
  const [state, setState] = useState<ActionState>({ phase: 'idle', message: null, activeId: null });

  const fireReversal = useCallback(
    async (override: OverrideAction) => {
      setState({ phase: 'working', message: `Firing ${override.label}…`, activeId: override.id });
      try {
        const started = await processes.start(
          { processName: override.processName, inputArguments: JSON.stringify(override.payload) },
          { folderKey: MAESTRO_FOLDER_KEY },
        );
        const jobKey = started?.[0]?.key;
        setState({
          phase: 'done',
          message: `${override.label} fired${jobKey ? ` · job ${String(jobKey).slice(0, 8)}` : ''}`,
          activeId: override.id,
        });
      } catch (err) {
        setState({ phase: 'error', message: describeError(err), activeId: override.id });
      }
    },
    [processes],
  );

  const approveHitl = useCallback(
    async (task: TaskGetResponse, action = 'Approve') => {
      const id = String(task.id);
      setState({ phase: 'working', message: `Approving “${task.title}”…`, activeId: id });
      try {
        const orgUnitId = (task as unknown as { organizationUnitId?: number }).organizationUnitId;
        const folderId = Number(task.folderId ?? orgUnitId ?? 0);
        await tasks.complete({ type: TaskType.App, taskId: Number(task.id), action, data: {} }, folderId);
        setState({ phase: 'done', message: `Approved “${task.title}”`, activeId: id });
      } catch (err) {
        setState({ phase: 'error', message: describeError(err), activeId: id });
      }
    },
    [tasks],
  );

  const reset = useCallback(
    () => setState({ phase: 'idle', message: null, activeId: null }),
    [],
  );

  return { state, fireReversal, approveHitl, reset };
}
