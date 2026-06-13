import { motion, AnimatePresence } from 'motion/react';
import { OVERRIDES } from '../narrative';
import type { OverrideAction } from '../narrative';
import { useProcessActions } from '../hooks/useProcessActions';
import type { ActionState } from '../hooks/useProcessActions';
import { Panel } from './Panel';

function Spinner() {
  return <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />;
}

function StatusLine({ state }: { state: ActionState }) {
  if (state.phase === 'idle' || !state.message) return null;
  const tone =
    state.phase === 'error'
      ? 'text-rose-300 bg-rose-500/10 border-rose-500/30'
      : state.phase === 'done'
        ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30'
        : 'text-accent bg-accent/10 border-accent/30';
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={state.message}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        className={`mt-3 text-xs rounded-lg border px-3 py-2 break-words ${tone}`}
      >
        {state.message}
      </motion.div>
    </AnimatePresence>
  );
}

function FireButton({
  override, working, onFire,
}: { override: OverrideAction; working: boolean; onFire: (o: OverrideAction) => void }) {
  if (override.hero) {
    return (
      <button
        onClick={() => onFire(override)}
        disabled={working}
        title={override.tooltip}
        className="col-span-2 group relative flex items-center justify-center gap-2 rounded-xl border border-accent/60 bg-accent/15 px-4 py-3.5 font-semibold text-accent shadow-glow-sm hover:bg-accent/25 disabled:opacity-50 transition-all animate-pulse-glow"
      >
        {working ? <Spinner /> : <span className="text-lg leading-none">⚡</span>}
        Fire Reversal 3 ★
        <span className="absolute -top-2 right-3 text-[9px] uppercase tracking-wider bg-accent text-ink-950 px-1.5 py-0.5 rounded-full font-bold">
          Hero
        </span>
      </button>
    );
  }
  return (
    <button
      onClick={() => onFire(override)}
      disabled={working}
      title={override.tooltip}
      className="flex items-center justify-center gap-2 rounded-lg border border-ink-600 bg-ink-800/60 px-3 py-2.5 text-sm font-medium text-slate-200 hover:border-accent/50 hover:bg-ink-700/60 disabled:opacity-50 transition-all"
    >
      {working ? <Spinner /> : <span className="text-accent">▸</span>}
      {override.label}
    </button>
  );
}

/**
 * Demo operator console — fires each reversal live by starting its process with
 * the Demo Driver payload. R1 opens a fresh master crisis; R2–R5 drive it.
 */
export function OperatorConsole() {
  const { state, fireReversal } = useProcessActions();
  const working = state.phase === 'working';

  return (
    <Panel
      title="Operator Console"
      subtitle="Fire reversals out of timeline order — live Maestro triggers"
      icon={<span className="text-base leading-none">⚡</span>}
    >
      <div className="grid grid-cols-2 gap-2.5">
        {OVERRIDES.map((o) => (
          <FireButton
            key={o.id}
            override={o}
            working={working && state.activeId === o.id}
            onFire={fireReversal}
          />
        ))}
      </div>
      <StatusLine state={state} />
      <p className="mt-3 text-[11px] text-slate-600 leading-snug">
        Reversal 1 starts a fresh master crisis case; Reversals 2–5 fire the driving event into
        the running case. The Reversal-4 fiduciary gate is approved from the HITL panel below.
      </p>
    </Panel>
  );
}
