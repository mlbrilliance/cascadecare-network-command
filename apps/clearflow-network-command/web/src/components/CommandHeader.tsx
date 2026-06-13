import { motion, AnimatePresence } from 'motion/react';
import type { CrisisState } from '../caseUtils';
import logoUrl from '../assets/clearflow-logo.svg';

interface CommandHeaderProps {
  crisis: CrisisState;
  isActive: boolean;
  lastUpdated: Date | null;
  onLogout: () => void;
}

/** Slim sticky command bar: day/reversal, live status, crisis posture. */
export function CommandHeader({ crisis, isActive, lastUpdated, onLogout }: CommandHeaderProps) {
  const dayLabel = crisis.reversalN > 0 ? `Day ${crisis.simulatedDay}` : 'Pre-crisis';
  const reversalLabel = crisis.reversalN > 0 ? `${crisis.reversalN} / 5` : '—';

  return (
    <header className="sticky top-0 z-30 border-b border-ink-700/70 bg-ink-950/85 backdrop-blur-xl">
      <div className="flex items-center gap-4 px-5 lg:px-7 py-3 min-w-0">
        {/* brand shown only when the sidebar is hidden (mobile) */}
        <div className="flex items-center gap-2.5 lg:hidden min-w-0">
          <img src={logoUrl} alt="" className="w-7 h-7 shrink-0" />
          <span className="text-sm font-bold text-slate-50 truncate">ClearFlow Command</span>
        </div>

        <div className="hidden lg:flex items-center gap-2 min-w-0">
          <span className="text-[10px] uppercase tracking-[0.2em] text-slate-600">Cyber Crisis Operations</span>
        </div>

        <div className="flex-1 min-w-0 flex items-center gap-3 justify-end">
          <Pill label="Sim day" value={dayLabel} />
          <Pill label="Reversal" value={reversalLabel} />

          <span
            className={`flex items-center gap-1.5 text-xs font-semibold whitespace-nowrap px-2.5 py-1 rounded-full border ${
              isActive ? 'text-accent border-accent/40 bg-accent/10' : 'text-slate-500 border-ink-700 bg-ink-800/40'
            }`}
            title={lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : undefined}
          >
            <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-accent animate-pulse-glow' : 'bg-slate-600'}`} />
            {isActive ? 'LIVE' : 'IDLE'}
          </span>

          <button
            onClick={onLogout}
            className="text-sm text-slateUI hover:text-slate-100 transition-colors whitespace-nowrap"
          >
            Sign out
          </button>
        </div>
      </div>

      {/* crisis posture banner */}
      <div className="flex items-center gap-3 px-5 lg:px-7 pb-2.5 min-w-0">
        <span className="text-[10px] uppercase tracking-[0.18em] text-slate-600 shrink-0">Current goal</span>
        <div className="h-px flex-1 bg-gradient-to-r from-accent/40 to-transparent" />
        <AnimatePresence mode="wait">
          <motion.span
            key={crisis.posture}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.4 }}
            className="text-sm font-medium text-slate-200 text-right max-w-[72%] truncate"
            title={crisis.posture}
          >
            {crisis.posture}
          </motion.span>
        </AnimatePresence>
      </div>
    </header>
  );
}

function Pill({ label, value }: { label: string; value: string }) {
  return (
    <span className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full border border-ink-700 bg-ink-850/70 whitespace-nowrap">
      <span className="text-[10px] uppercase tracking-wider text-slate-600">{label}</span>
      <span className="text-sm font-semibold text-slate-100 tabular-nums">{value}</span>
    </span>
  );
}
