import { useEffect, useState } from 'react';
import { animate } from 'motion/react';
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import type { CrisisState } from '../caseUtils';
import { Panel } from './Panel';

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

/**
 * Phoenix-style semicircle gauge — % of cases closed (containment). Big centred
 * numeral, 0%…100% end caps, current-posture caption below.
 */
export function PostureGauge({ crisis }: { crisis: CrisisState }) {
  const { counts } = crisis;
  const pct = counts.total > 0 ? Math.round((counts.completed / counts.total) * 100) : 0;
  const n = Math.round(useCountUp(pct));
  const data = [{ name: 'closed', value: pct, fill: '#F26B1D' }];

  return (
    <Panel title="Containment" subtitle="Crisis cases brought to closure">
      <div className="relative">
        <RadialBarChart
          width={260} height={150} cx="50%" cy="95%"
          innerRadius="128%" outerRadius="178%" barSize={16}
          data={data} startAngle={180} endAngle={0}
          className="mx-auto"
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background={{ fill: '#242935' }} dataKey="value" cornerRadius={8} />
        </RadialBarChart>
        <div className="absolute inset-x-0 bottom-1 flex flex-col items-center pointer-events-none">
          <span className="text-4xl font-extrabold tabular-nums text-slate-50">{n}<span className="text-2xl text-accent">%</span></span>
        </div>
        <div className="flex justify-between text-[10px] text-slate-600 px-2 -mt-1">
          <span>0%</span><span>100%</span>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-center">
        <Mini label="Closed" value={counts.completed} />
        <Mini label="Total" value={counts.total} />
        <Mini label="Open" value={Math.max(0, counts.total - counts.completed)} />
      </div>
      <p className="mt-3 text-xs text-slateUI leading-snug border-t border-ink-700/70 pt-3">
        <span className="text-[10px] uppercase tracking-[0.16em] text-slate-600 block mb-1">Current posture</span>
        {crisis.posture}
      </p>
    </Panel>
  );
}

function Mini({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-ink-700/70 bg-ink-900/50 py-2">
      <div className="text-lg font-bold tabular-nums text-slate-100">{value}</div>
      <div className="text-[9px] uppercase tracking-[0.14em] text-slate-600">{label}</div>
    </div>
  );
}
