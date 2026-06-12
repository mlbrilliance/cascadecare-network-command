import { Panel } from './Panel';

interface Reversal {
  n: number;
  name: string;
  day: number;
  shift: string;
  hero?: boolean;
}

const REVERSALS: Reversal[] = [
  { n: 1, day: 1, name: 'Multi-customer correlation', shift: '"Assist isolated customers" → "Determine if ClearFlow is the vector"' },
  { n: 2, day: 5, name: 'ClearFlow cleared + Nimbus identified', shift: '"Am I the cause?" → "Visible bystander with strategic posture decision"' },
  { n: 3, day: 30, name: 'State DOI subpoena collision', shift: 'Three-level nesting goes live; 6 grandchild cases spawn', hero: true },
  { n: 4, day: 45, name: 'Payer demands vs BAAs', shift: 'Fiduciary Conflict Detector fires; tri-party HITL gate' },
  { n: 5, day: 90, name: 'Litigation cascade', shift: 'Bystander → co-defendant; privilege reshuffles' },
];

/** Static narrative timeline of the five master-level reversals. */
export function ReversalTimeline() {
  return (
    <Panel title="Reversal Timeline" subtitle="Five master goal shifts across the 90-day simulated crisis">
      <table className="w-full table-fixed text-sm">
        <thead>
          <tr className="text-left text-xs text-slate-500 uppercase tracking-wider">
            <th className="w-8 pb-2">#</th>
            <th className="w-16 pb-2">Day</th>
            <th className="w-2/5 pb-2">Reversal</th>
            <th className="pb-2">Master goal shift</th>
          </tr>
        </thead>
        <tbody>
          {REVERSALS.map(r => (
            <tr key={r.n} className={`border-t border-slate-800/60 ${r.hero ? 'bg-teal-500/5' : ''}`}>
              <td className="py-2 text-slate-400 align-top">{r.n}</td>
              <td className="py-2 text-slate-400 align-top whitespace-nowrap">Day {r.day}</td>
              <td className="py-2 align-top max-w-0">
                <span className="text-slate-200 block truncate" title={r.name}>{r.name}</span>
                {r.hero && <span className="text-xs text-teal-400">★ Hero moment</span>}
              </td>
              <td className="py-2 text-slate-400 align-top max-w-0">
                <span className="block truncate" title={r.shift}>{r.shift}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}
