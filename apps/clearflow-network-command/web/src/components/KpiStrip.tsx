import { useEffect, useState } from 'react';
import { motion, animate } from 'motion/react';
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import type { CrisisState } from '../caseUtils';

/** Eases a number from 0 → value once on mount / when value changes. */
function useCountUp(value: number, duration = 0.9): number {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const controls = animate(0, value, {
      duration,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(v),
    });
    return () => controls.stop();
  }, [value, duration]);
  return display;
}

interface TileProps {
  label: string;
  value: number;
  suffix?: string;
  accent?: 'teal' | 'amber' | 'sky' | 'rose' | 'emerald';
  index: number;
}

const ACCENT: Record<NonNullable<TileProps['accent']>, string> = {
  teal: 'text-accent',
  amber: 'text-amber-400',
  sky: 'text-sky-400',
  rose: 'text-rose-400',
  emerald: 'text-emerald-400',
};

function KpiTile({ label, value, suffix, accent = 'teal', index }: TileProps) {
  const n = useCountUp(value);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="relative rounded-xl border border-ink-700/70 bg-ink-850/60 backdrop-blur-md px-4 py-3 overflow-hidden"
    >
      <div className="pointer-events-none absolute -right-6 -top-6 w-16 h-16 rounded-full bg-accent/5 blur-xl" />
      <div className={`text-2xl lg:text-3xl font-bold tabular-nums ${ACCENT[accent]}`}>
        {Math.round(n)}
        {suffix && <span className="text-base text-slate-500 ml-0.5">{suffix}</span>}
      </div>
      <div className="text-[10px] uppercase tracking-[0.14em] text-slate-500 mt-0.5">{label}</div>
    </motion.div>
  );
}

function ClosedGauge({ pct, index }: { pct: number; index: number }) {
  const n = useCountUp(pct);
  const data = [{ name: 'closed', value: pct, fill: '#2DD4BF' }];
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="relative rounded-xl border border-ink-700/70 bg-ink-850/60 backdrop-blur-md px-4 py-3 flex items-center gap-3 overflow-hidden"
    >
      <div className="relative w-[58px] h-[58px] shrink-0">
        <RadialBarChart
          width={58}
          height={58}
          cx="50%"
          cy="50%"
          innerRadius="72%"
          outerRadius="100%"
          barSize={6}
          data={data}
          startAngle={90}
          endAngle={-270}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background={{ fill: '#16273C' }} dataKey="value" cornerRadius={6} />
        </RadialBarChart>
        <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-accent tabular-nums">
          {Math.round(n)}%
        </span>
      </div>
      <div className="text-[10px] uppercase tracking-[0.14em] text-slate-500 leading-tight">
        Cases<br />closed
      </div>
    </motion.div>
  );
}

/** Six headline KPI tiles derived from live crisis state. */
export function KpiStrip({ crisis }: { crisis: CrisisState }) {
  const { counts } = crisis;
  const pctClosed = counts.total > 0 ? Math.round((counts.completed / counts.total) * 100) : 0;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <KpiTile index={0} label="Total cases" value={counts.total} accent="teal" />
      <ClosedGauge index={1} pct={pctClosed} />
      <KpiTile index={2} label="Stakeholders" value={counts.parents} accent="sky" />
      <KpiTile index={3} label="Grandchildren" value={counts.grandchildren} accent="emerald" />
      <KpiTile index={4} label="Reversal" value={crisis.reversalN} suffix="/5" accent="amber" />
      <KpiTile index={5} label="HITL gates" value={counts.hitlGates} accent="rose" />
    </div>
  );
}
