import { motion, AnimatePresence } from 'motion/react';
import type { CrisisState } from '../caseUtils';
import logoUrl from '../assets/clearflow-logo.svg';

interface CommandHeaderProps {
  crisis: CrisisState;
  isActive: boolean;
  lastUpdated: Date | null;
  onLogout: () => void;
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-right leading-tight hidden md:block">
      <div className="text-sm font-semibold text-slate-100 tabular-nums">{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-slate-500">{label}</div>
    </div>
  );
}

/** Sticky command bar: brand, live status, day/reversal, and crisis posture. */
export function CommandHeader({ crisis, isActive, lastUpdated, onLogout }: CommandHeaderProps) {
  const dayLabel = crisis.reversalN > 0 ? `Day ${crisis.simulatedDay}` : 'Pre-crisis';
  const reversalLabel = crisis.reversalN > 0 ? `${crisis.reversalN} / 5` : '—';

  return (
    <header className="sticky top-0 z-30 border-b border-ink-700/70 bg-ink-950/80 backdrop-blur-xl">
      <div className="relative max-w-[1500px] mx-auto px-5 lg:px-8">
        <div className="flex items-center gap-4 py-3 min-w-0">
          <img src={logoUrl} alt="" className="w-9 h-9 shrink-0 animate-float" />
          <div className="min-w-0 flex-1">
            <h1 className="text-base lg:text-lg font-bold tracking-tight text-slate-50 truncate">
              ClearFlow <span className="text-accent text-glow">Network Command</span>
            </h1>
            <p className="text-[11px] text-slate-500 truncate">Cyber Crisis Operations · Live Case State</p>
          </div>

          <Stat label="Sim day" value={dayLabel} />
          <Stat label="Reversal" value={reversalLabel} />

          <span
            className={`flex items-center gap-1.5 text-xs font-semibold whitespace-nowrap px-2.5 py-1 rounded-full border ${
              isActive
                ? 'text-accent border-accent/40 bg-accent/5'
                : 'text-slate-500 border-ink-700 bg-ink-800/40'
            }`}
            title={lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : undefined}
          >
            <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-accent animate-pulse-glow' : 'bg-slate-600'}`} />
            {isActive ? 'LIVE' : 'IDLE'}
          </span>

          <button
            onClick={onLogout}
            className="text-sm text-slate-400 hover:text-slate-100 transition-colors whitespace-nowrap"
          >
            Sign out
          </button>
        </div>

        {/* Crisis posture banner */}
        <div className="flex items-center gap-3 pb-3 min-w-0">
          <span className="text-[10px] uppercase tracking-[0.18em] text-slate-500 shrink-0">Current goal</span>
          <div className="h-px flex-1 bg-gradient-to-r from-accent/40 to-transparent" />
          <AnimatePresence mode="wait">
            <motion.span
              key={crisis.posture}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.4 }}
              className="text-sm font-medium text-slate-200 text-right max-w-[70%] truncate"
              title={crisis.posture}
            >
              {crisis.posture}
            </motion.span>
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
