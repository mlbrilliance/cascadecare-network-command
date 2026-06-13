import type { ReactNode } from 'react';
import { motion } from 'motion/react';
import { statusChipClasses } from '../caseUtils';

interface PanelProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  /** Optional element rendered on the right of the header (counts, controls). */
  action?: ReactNode;
  /** Highlights the panel as the hero (subtle accent edge — used sparingly). */
  accent?: boolean;
  /** Optional id for in-page anchor / scroll-spy. */
  id?: string;
  className?: string;
  children: ReactNode;
}

/** Flat charcoal command card shared by all dashboard panels. */
export function Panel({ title, subtitle, icon, action, accent, id, className, children }: PanelProps) {
  return (
    <motion.section
      id={id}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className={`relative flex flex-col rounded-2xl border bg-ink-850/85 shadow-panel overflow-hidden ${
        accent ? 'border-accent/35' : 'border-ink-700'
      } ${className ?? ''}`}
    >
      <header className="flex items-center gap-3 px-5 py-3.5 border-b border-ink-700/70 min-w-0">
        {/* orange tick — the only accent in the header */}
        <span className={`h-3.5 w-[3px] rounded-full shrink-0 ${accent ? 'bg-accent' : 'bg-accent/55'}`} />
        {icon && <span className="text-accent shrink-0">{icon}</span>}
        <div className="min-w-0 flex-1">
          <h2 className="display-heading text-[13px] text-slate-100 uppercase tracking-[0.13em] truncate" title={title}>
            {title}
          </h2>
          {subtitle && <p className="text-xs text-slateUI/80 truncate" title={subtitle}>{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </header>
      <div className="p-5 flex-1 min-w-0">{children}</div>
    </motion.section>
  );
}

export function PanelLoading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slateUI py-8 justify-center">
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
