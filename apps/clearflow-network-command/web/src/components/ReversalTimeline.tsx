import { motion } from 'motion/react';
import { REVERSALS } from '../narrative';
import { Panel } from './Panel';

/** Horizontal animated timeline of the five master reversals. */
export function ReversalTimeline({ currentReversal }: { currentReversal: number }) {
  const reached = Math.max(0, Math.min(currentReversal, REVERSALS.length));
  const progressPct = REVERSALS.length > 1 ? ((reached - 1) / (REVERSALS.length - 1)) * 100 : 0;

  return (
    <Panel title="Reversal Timeline" subtitle="Five master goal shifts across the 90-day crisis">
      <div className="relative pt-2 pb-1">
        {/* rail */}
        <div className="absolute left-[8%] right-[8%] top-[18px] h-0.5 bg-ink-700 rounded-full" />
        <motion.div
          className="absolute left-[8%] top-[18px] h-0.5 bg-accent rounded-full shadow-glow-sm"
          initial={{ width: 0 }}
          animate={{ width: `${(progressPct / 100) * 84}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        />
        <div className="relative grid grid-cols-5">
          {REVERSALS.map((r, i) => {
            const done = r.n < reached;
            const active = r.n === reached;
            const state = active ? 'active' : done ? 'done' : 'future';
            const dot =
              state === 'active'
                ? 'bg-accent border-accent text-ink-950 animate-pulse-glow'
                : state === 'done'
                  ? 'bg-accent/80 border-accent text-ink-950'
                  : 'bg-ink-800 border-ink-600 text-slate-500';
            return (
              <motion.div
                key={r.n}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex flex-col items-center text-center px-1"
                title={`${r.goalFrom} → ${r.goalTo}`}
              >
                <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center text-sm font-bold ${dot}`}>
                  {r.n}
                </div>
                <div className="mt-2 text-[11px] font-semibold text-slate-300 leading-tight line-clamp-2">
                  {r.name}
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">Day {r.day}</div>
                {r.hero && <div className="text-[10px] text-accent font-semibold mt-0.5">★ Hero</div>}
              </motion.div>
            );
          })}
        </div>
      </div>
    </Panel>
  );
}
