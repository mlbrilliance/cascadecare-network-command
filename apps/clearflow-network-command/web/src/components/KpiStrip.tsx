import { motion } from 'motion/react';
import { Area, AreaChart, ResponsiveContainer } from 'recharts';
import type { CrisisState } from '../caseUtils';
import { useCountUp } from '../hooks/useCountUp';

interface Tile {
  key: string;
  label: string;
  value: number;
  suffix?: string;
  glyph: string;
}

function KpiTile({ tile, index, spark }: { tile: Tile; index: number; spark?: number[] }) {
  const n = useCountUp(tile.value);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="relative rounded-2xl border border-ink-700 bg-ink-850/80 px-4 py-3.5 overflow-hidden"
    >
      <div className="flex items-center gap-2.5">
        <span className="grid place-items-center w-8 h-8 rounded-xl bg-ink-800 text-accent/90 text-sm shrink-0">
          {tile.glyph}
        </span>
        <div className="min-w-0">
          <div className="text-2xl lg:text-[28px] leading-none font-extrabold tabular-nums text-slate-50">
            {Math.round(n)}
            {tile.suffix && <span className="text-base text-slate-500 ml-0.5">{tile.suffix}</span>}
          </div>
        </div>
      </div>
      <div className="text-[10px] uppercase tracking-[0.14em] text-slate-600 mt-2">{tile.label}</div>
      {spark && spark.length > 1 && (
        <div className="h-8 -mx-4 -mb-3.5 mt-1.5 opacity-90">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={spark.map((v) => ({ v }))} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="kpi-spark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#F26B1D" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#F26B1D" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke="#F26B1D" strokeWidth={2} fill="url(#kpi-spark)" isAnimationActive />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
}

/** Five headline KPI tiles derived from live crisis state. */
export function KpiStrip({ crisis }: { crisis: CrisisState }) {
  const { counts } = crisis;
  // Real cascade-growth series: master → +parents → +grandchildren.
  const spark = [0, counts.masters, counts.masters + counts.parents, counts.total];

  const tiles: Tile[] = [
    { key: 'total', label: 'Total cases', value: counts.total, glyph: '▦' },
    { key: 'stake', label: 'Stakeholder parents', value: counts.parents, glyph: '◆' },
    { key: 'grand', label: 'Obligation grandchildren', value: counts.grandchildren, glyph: '⛓' },
    { key: 'rev', label: 'Reversal reached', value: crisis.reversalN, suffix: '/5', glyph: '↻' },
    { key: 'hitl', label: 'HITL gates', value: counts.hitlGates, glyph: '✋' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {tiles.map((t, i) => (
        <KpiTile key={t.key} tile={t} index={i} spark={t.key === 'total' ? spark : undefined} />
      ))}
    </div>
  );
}
