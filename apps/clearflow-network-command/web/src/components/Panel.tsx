import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { statusChipClasses } from '../caseUtils';

interface PanelProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  /** Optional element rendered on the right of the header (counts, controls). */
  action?: ReactNode;
  /** Highlights the panel border/glow (used for the hero cascade panel). */
  accent?: boolean;
  children: ReactNode;
}

/** Glassmorphic mission-control card shared by all dashboard panels. */
export function Panel({ title, subtitle, icon, action, accent, children }: PanelProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className={`relative flex flex-col rounded-xl border bg-ink-850/70 backdrop-blur-xl shadow-panel overflow-hidden ${
        accent ? 'border-accent/40 shadow-glow-sm' : 'border-ink-700/70'
      }`}
    >
      {/* top hairline sheen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/50 to-transparent" />
      <header className="flex items-center gap-3 px-4 py-3 border-b border-ink-700/60 min-w-0">
        {icon && <span className="text-accent shrink-0">{icon}</span>}
        <div className="min-w-0 flex-1">
          <h2 className="text-[13px] font-semibold text-slate-100 uppercase tracking-[0.14em] truncate" title={title}>
            {title}
          </h2>
          {subtitle && <p className="text-xs text-slate-500 truncate" title={subtitle}>{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </header>
      <div className="p-4 flex-1 min-w-0">{children}</div>
    </motion.section>
  );
}

export function PanelLoading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400 py-8 justify-center">
      <span className="w-2 h-2 bg-accent rounded-full animate-pulse-glow" />
      {label}
    </div>
  );
}

export function PanelError({ message }: { message: string }) {
  return (
    <div className="text-sm text-rose-300 bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 break-words">
      {message}
    </div>
  );
}

export function StatusChip({ status }: { status: string | null | undefined }) {
  const label = status || 'Unknown';
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-medium whitespace-nowrap ${statusChipClasses(status)}`}
      title={label}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {label}
    </span>
  );
}
