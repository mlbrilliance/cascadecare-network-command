import { useEffect, useState } from 'react';
import type { CrisisState } from '../caseUtils';
import logoUrl from '../assets/clearflow-logo.svg';

interface NavItem { id: string; label: string; glyph: string }

const NAV: NavItem[] = [
  { id: 'cascade', label: 'Energy Flow', glyph: '⚡' },
  { id: 'overview', label: 'Overview', glyph: '▦' },
  { id: 'reversals', label: 'Reversals', glyph: '↻' },
  { id: 'console', label: 'Console', glyph: '◉' },
  { id: 'agents', label: 'Agents', glyph: '◆' },
];

function useScrollSpy(ids: string[]): string {
  const [active, setActive] = useState(ids[0]);
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: [0, 0.25, 0.5, 1] },
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [ids]);
  return active;
}

export function Sidebar({ crisis, isActive }: { crisis: CrisisState; isActive: boolean }) {
  const active = useScrollSpy(NAV.map((n) => n.id));

  const go = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0 sticky top-0 h-screen border-r border-ink-700/70 bg-ink-900/60 backdrop-blur-xl">
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-ink-700/60">
        <img src={logoUrl} alt="" className="w-8 h-8 shrink-0" />
        <div className="leading-tight min-w-0">
          <div className="text-sm font-bold text-slate-50 truncate">ClearFlow</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-accent">Network Command</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map((item) => {
          const on = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => go(item.id)}
              className={`group flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm transition-all ${
                on
                  ? 'bg-accent/12 text-accent border border-accent/30'
                  : 'text-slateUI border border-transparent hover:bg-ink-800/60 hover:text-slate-200'
              }`}
            >
              <span className={`w-5 text-center ${on ? 'text-accent' : 'text-slate-600 group-hover:text-slateUI'}`}>{item.glyph}</span>
              <span className="font-medium">{item.label}</span>
              {on && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-accent" />}
            </button>
          );
        })}
      </nav>

      {/* crisis-posture status card */}
      <div className="m-3 rounded-xl border border-ink-700 bg-ink-850/80 p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[10px] uppercase tracking-[0.18em] text-slate-600">Status</span>
          <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
            isActive ? 'text-accent border-accent/40 bg-accent/10' : 'text-slate-500 border-ink-700'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-accent animate-pulse-glow' : 'bg-slate-600'}`} />
            {isActive ? 'LIVE' : 'IDLE'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mb-3">
          <Stat label="Sim day" value={crisis.reversalN > 0 ? `${crisis.simulatedDay}` : '—'} />
          <Stat label="Reversal" value={crisis.reversalN > 0 ? `${crisis.reversalN}/5` : '0/5'} />
        </div>
        <p className="text-[11px] text-slateUI leading-snug line-clamp-3" title={crisis.posture}>{crisis.posture}</p>
      </div>
    </aside>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-ink-900/60 border border-ink-700/60 px-2.5 py-1.5">
      <div className="text-base font-bold tabular-nums text-slate-100">{value}</div>
      <div className="text-[9px] uppercase tracking-[0.12em] text-slate-600">{label}</div>
    </div>
  );
}
