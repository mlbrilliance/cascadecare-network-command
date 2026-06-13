import type { ReactNode } from 'react';
import type { CrisisState } from '../caseUtils';
import { formatTime } from '../caseUtils';
import { Panel } from './Panel';

interface Spec {
  label: string;
  value: string;
  glyph: ReactNode;
}

/** Phoenix-style spec-grid: paired label/value cells with a tiny glyph. */
export function DetailsGrid({ crisis, lastUpdated }: { crisis: CrisisState; lastUpdated: Date | null }) {
  const specs: Spec[] = [
    { label: 'Posture', value: crisis.reversalN > 0 ? `Reversal ${crisis.reversalN}` : 'Pre-crisis', glyph: '◆' },
    { label: 'Sim day', value: crisis.reversalN > 0 ? `Day ${crisis.simulatedDay}` : '—', glyph: '☰' },
    { label: 'Total cases', value: String(crisis.counts.total), glyph: '▦' },
    { label: 'Closed', value: String(crisis.counts.completed), glyph: '✓' },
    { label: 'Reversal', value: crisis.reversalN > 0 ? `${crisis.reversalN} / 5` : '0 / 5', glyph: '↻' },
    { label: 'Updated', value: lastUpdated ? lastUpdated.toLocaleTimeString() : formatTime(null), glyph: '◷' },
  ];
  return (
    <Panel title="Details" subtitle="Live crisis telemetry">
      <div className="grid grid-cols-2 gap-x-3 gap-y-px">
        {specs.map((s) => (
          <div key={s.label} className="flex items-center gap-2.5 py-2.5 border-b border-ink-700/50">
            <span className="grid place-items-center w-7 h-7 rounded-lg bg-ink-800 text-accent/80 text-xs shrink-0">
              {s.glyph}
            </span>
            <div className="min-w-0">
              <div className="text-[9px] uppercase tracking-[0.16em] text-slate-600">{s.label}</div>
              <div className="text-sm font-semibold text-slate-100 tabular-nums truncate" title={s.value}>{s.value}</div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
