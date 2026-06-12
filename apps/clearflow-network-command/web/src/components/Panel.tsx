import type { ReactNode } from 'react';
import { statusChipClasses } from '../caseUtils';

interface PanelProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

/** Dark-theme card wrapper shared by all dashboard panels. */
export function Panel({ title, subtitle, children }: PanelProps) {
  return (
    <section className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden flex flex-col">
      <header className="px-4 py-3 border-b border-slate-800 min-w-0">
        <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider truncate" title={title}>
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs text-slate-500 truncate" title={subtitle}>{subtitle}</p>
        )}
      </header>
      <div className="p-4 flex-1 min-w-0">{children}</div>
    </section>
  );
}

export function PanelLoading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400 py-6 justify-center">
      <span className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
      {label}
    </div>
  );
}

export function PanelError({ message }: { message: string }) {
  return (
    <div className="text-sm text-red-300 bg-red-500/10 border border-red-500/30 rounded p-3 break-words">
      {message}
    </div>
  );
}

export function StatusChip({ status }: { status: string | null | undefined }) {
  const label = status || 'Unknown';
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-medium whitespace-nowrap ${statusChipClasses(status)}`}
      title={label}
    >
      {label}
    </span>
  );
}
