import { motion } from 'motion/react';
import { AGENTS } from '../narrative';
import type { Agent } from '../narrative';
import { Panel } from './Panel';

/** Claude (BYO-LLM) reasoning agents carry the orange accent; first-party UiPath is neutral. */
function llmBadgeClass(llm: string): string {
  if (llm.startsWith('Claude')) return 'bg-accent/12 text-accent-glow border-accent/40';
  return 'bg-ink-800 text-slateUI border-ink-600';
}

function AgentCard({ agent, index }: { agent: Agent; index: number }) {
  const kindClass =
    agent.kind === 'Coded'
      ? 'bg-ink-800 text-slateUI border-ink-600'
      : 'bg-accent/10 text-accent border-accent/30';
  const dotColor = agent.kind === 'Builder' ? 'bg-accent' : 'bg-slateUI/70';
  return (
    <motion.li
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-start gap-3 py-2.5 border-b border-ink-700/50 last:border-b-0"
    >
      <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${dotColor}`} />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-slate-200 truncate">{agent.displayName}</span>
          <span className={`px-1.5 py-0.5 rounded border text-[10px] font-semibold ${kindClass}`}>{agent.kind}</span>
          <span className={`px-1.5 py-0.5 rounded border text-[10px] font-semibold ${llmBadgeClass(agent.llm)}`}>{agent.llm}</span>
        </div>
        <p className="text-xs text-slate-500 truncate" title={agent.role}>{agent.role}</p>
      </div>
    </motion.li>
  );
}

/** The seven runtime agents — shows the topology and names each one. */
export function AgentRoster() {
  const coded = AGENTS.filter((a) => a.kind === 'Coded').length;
  const builder = AGENTS.filter((a) => a.kind === 'Builder').length;
  return (
    <Panel
      title="Agent Roster"
      subtitle="Coordinated UiPath agents across the crisis"
      action={
        <span className="text-xs text-slate-500 whitespace-nowrap">
          {coded} Coded · {builder} Builder
        </span>
      }
    >
      <ul>
        {AGENTS.map((a, i) => <AgentCard key={a.id} agent={a} index={i} />)}
      </ul>
    </Panel>
  );
}
