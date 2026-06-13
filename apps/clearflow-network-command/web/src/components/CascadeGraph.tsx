import { useMemo, useState } from 'react';
import { motion } from 'motion/react';
import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import {
  inferCaseLevel,
  rollupStakeholders,
  statusTone,
} from '../caseUtils';
import type { RollupStatus, StakeholderRollup } from '../caseUtils';
import { Panel, PanelError, PanelLoading } from './Panel';

interface CascadeGraphProps {
  instances: CaseInstanceGetResponse[] | null;
  isLoading: boolean;
  error: Error | null;
}

// SVG coordinate space (scaled responsively via viewBox).
const W = 1000;
const TOP = 46;
const PITCH = 60;
const PORT_H = 46;
const PORT_X = 548;
const PORT_W = 300;
const PORT_RIGHT = PORT_X + PORT_W;
const MX = 40;
const MW = 214;
const MH = 124;
const BOLT_X = MX + MW; // cable origin

/** Status → cable + node colour, mirroring the disciplined orange palette. */
const STATUS_COLOR: Record<RollupStatus, string> = {
  running: '#F26B1D',
  faulted: '#F43F5E',
  paused: '#D9963B',
  completed: '#34D399',
  idle: '#3A4150',
};
const ACTIVE: RollupStatus[] = ['running', 'faulted'];

function truncate(s: string, n: number): string {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

/** Smooth horizontal cable from the master bolt to a port. */
function cablePath(x1: number, y1: number, x2: number, y2: number): string {
  const mid = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`;
}

function cableWeight(rawCount: number): number {
  return Math.max(2.5, Math.min(11, 2.5 + rawCount * 0.7));
}

function StatusDot({ status, cx, cy }: { status: RollupStatus; cx: number; cy: number }) {
  const c = STATUS_COLOR[status];
  const live = ACTIVE.includes(status);
  return (
    <g>
      {live && <circle cx={cx} cy={cy} r={9} fill={c} opacity={0.22} className="animate-pulse" />}
      <circle cx={cx} cy={cy} r={4.5} fill={c} />
    </g>
  );
}

function PortCard({ port, y, hovered, onHover }: {
  port: StakeholderRollup; y: number; hovered: boolean; onHover: (slug: string | null) => void;
}) {
  const c = STATUS_COLOR[port.status];
  const cy = y + PORT_H / 2;
  const active = ACTIVE.includes(port.status);
  const kindLabel = port.kind === 'other' ? 'UNMAPPED' : port.kind.toUpperCase();
  return (
    <g
      onMouseEnter={() => onHover(port.slug)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      <rect
        x={PORT_X} y={y} width={PORT_W} height={PORT_H} rx={11}
        fill={hovered ? '#1B1F27' : '#15181E'}
        stroke={hovered || active ? c : '#242935'}
        strokeOpacity={hovered ? 0.9 : active ? 0.55 : 1}
        strokeWidth={hovered ? 1.8 : 1.2}
      />
      <StatusDot status={port.status} cx={PORT_X + 22} cy={cy} />
      <text x={PORT_X + 40} y={cy - 5} className="fill-slate-100" style={{ fontSize: 14, fontWeight: 600 }}>
        {truncate(port.displayName, 24)}
      </text>
      <text x={PORT_X + 40} y={cy + 12} style={{ fontSize: 9.5, fontWeight: 600, letterSpacing: 1 }} className="fill-slateUI">
        {kindLabel}
      </text>
      {/* right: instance count + obligation chip */}
      <text x={PORT_RIGHT - 78} y={cy + 5} textAnchor="end" className="fill-slate-200" style={{ fontSize: 16, fontWeight: 700 }}>
        {port.rawCount}
      </text>
      <text x={PORT_RIGHT - 74} y={cy + 5} style={{ fontSize: 9, fill: '#8A929E' }}>inst</text>
      {port.grandchildren.length > 0 && (
        <g>
          <rect x={PORT_RIGHT - 46} y={cy - 9} width={38} height={18} rx={9}
            fill={active ? 'rgba(242,107,29,0.16)' : 'rgba(138,146,158,0.12)'}
            stroke={active ? 'rgba(242,107,29,0.5)' : 'rgba(138,146,158,0.3)'} strokeWidth={1} />
          <text x={PORT_RIGHT - 27} y={cy + 3.5} textAnchor="middle"
            style={{ fontSize: 10, fontWeight: 700 }} className={active ? 'fill-accent-glow' : 'fill-slateUI'}>
            ▸{port.openObligations || port.grandchildren.length}
          </text>
        </g>
      )}
    </g>
  );
}

/** Hovered port's obligation grandchildren as a small right-side sub-fan. */
function SubFan({ port, y }: { port: StakeholderRollup; y: number }) {
  const cy = y + PORT_H / 2;
  const kids = port.grandchildren.slice(0, 7);
  const fanX = PORT_RIGHT + 70;
  const spread = Math.min(160, kids.length * 26);
  return (
    <g>
      {kids.map((g, i) => {
        const gy = cy - spread / 2 + (kids.length > 1 ? (i / (kids.length - 1)) * spread : 0);
        const tone = statusTone(g.latestRunStatus);
        return (
          <g key={g.instanceId}>
            <path d={cablePath(PORT_RIGHT, cy, fanX, gy)} fill="none" stroke={tone.stroke} strokeWidth={1.2} strokeOpacity={0.5} />
            <circle cx={fanX} cy={gy} r={5} fill={tone.fill} stroke={tone.stroke} strokeWidth={1.6}>
              <title>{`Obligation grandchild · ${g.latestRunStatus ?? 'Unknown'}`}</title>
            </circle>
          </g>
        );
      })}
      {port.grandchildren.length > kids.length && (
        <text x={fanX + 12} y={cy} style={{ fontSize: 10 }} className="fill-slateUI">
          +{port.grandchildren.length - kids.length}
        </text>
      )}
    </g>
  );
}

function MasterCore({ cy, status, activePorts }: { cy: number; status: RollupStatus; activePorts: number }) {
  const c = STATUS_COLOR[status === 'idle' ? 'running' : status];
  const top = cy - MH / 2;
  return (
    <g>
      <rect x={MX} y={top} width={MW} height={MH} rx={14} fill="#15181E" stroke="#242935" strokeWidth={1.2} />
      <rect x={MX} y={top} width={4} height={MH} rx={2} fill={c} />
      <text x={MX + 22} y={top + 34} style={{ fontSize: 10, fontWeight: 700, letterSpacing: 2 }} className="fill-slateUI">
        CLEARFLOW · CFCS
      </text>
      <text x={MX + 22} y={top + 60} className="fill-slate-50 display-heading" style={{ fontSize: 21 }}>MASTER</text>
      <text x={MX + 22} y={top + 84} className="fill-slate-50 display-heading" style={{ fontSize: 21 }}>CRISIS</text>
      <text x={MX + 22} y={top + 108} style={{ fontSize: 10.5 }} className="fill-slateUI">
        {activePorts} stakeholder{activePorts === 1 ? '' : 's'} live
      </text>
      {/* glowing bolt — the cable origin */}
      <circle cx={BOLT_X} cy={cy} r={26} fill={c} opacity={0.18} className="animate-pulse" style={{ animationDuration: '2.6s' }} />
      <circle cx={BOLT_X} cy={cy} r={17} fill={c} filter="url(#cf-glow)" />
      <path
        d={`M ${BOLT_X + 2} ${cy - 9} L ${BOLT_X - 5} ${cy + 1} L ${BOLT_X + 1} ${cy + 1} L ${BOLT_X - 2} ${cy + 9} L ${BOLT_X + 6} ${cy - 2} L ${BOLT_X} ${cy - 2} Z`}
        fill="#0C0E12"
      />
    </g>
  );
}

export function CascadeGraph({ instances, isLoading, error }: CascadeGraphProps) {
  const ports = useMemo(() => rollupStakeholders(instances), [instances]);
  const [hover, setHover] = useState<string | null>(null);

  const all = instances ?? [];
  const masters = all.filter((i) => inferCaseLevel(i) === 0);
  const stakeholderInsts = all.filter((i) => inferCaseLevel(i) === 1).length;
  const grandchildInsts = all.filter((i) => inferCaseLevel(i) === 2).length;
  const total = all.length;

  const masterStatus: RollupStatus = ports.some((p) => p.status === 'faulted')
    ? 'faulted'
    : ports.some((p) => p.status === 'running')
      ? 'running'
      : masters.length > 0 ? 'running' : 'idle';
  const activePorts = ports.filter((p) => p.rawCount > 0).length;

  const H = TOP + ports.length * PITCH + 24;
  const cy = H / 2;
  const hoveredPort = ports.find((p) => p.slug === hover) ?? null;

  let body;
  if (error && !instances) {
    body = <PanelError message={`Failed to load case instances: ${error.message}`} />;
  } else if (isLoading && !instances) {
    body = <PanelLoading label="Loading energy flow…" />;
  } else if (total === 0) {
    body = (
      <p className="text-sm text-slateUI py-16 text-center">
        Awaiting first signal — fire <span className="text-accent font-semibold">Reversal 1</span> to open the master crisis case.
      </p>
    );
  } else {
    body = (
      <div>
        {error && <div className="mb-3"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
        <div className="rounded-xl border border-ink-700/70 bg-[#0a0c10] bg-dots [background-size:18px_18px] p-2">
          <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ display: 'block', maxHeight: 560 }} preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="cf-glow" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur stdDeviation="3.2" result="b" />
                <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </defs>

            {/* cables: master → each port */}
            {ports.map((p, i) => {
              const py = TOP + i * PITCH + PORT_H / 2;
              const c = STATUS_COLOR[p.status];
              const live = ACTIVE.includes(p.status);
              const on = hover === p.slug;
              const idle = p.rawCount === 0;
              const d = cablePath(BOLT_X, cy, PORT_X, py);
              return (
                <g key={`cable-${p.slug}`}>
                  <path
                    d={d} fill="none" stroke={idle ? '#2A303C' : c}
                    strokeWidth={idle ? 2 : cableWeight(p.rawCount)}
                    strokeOpacity={on ? 0.95 : idle ? 0.5 : 0.7}
                    strokeLinecap="round"
                  />
                  {live && (
                    <path
                      d={d} fill="none" stroke="#FFD9B8" strokeWidth={2}
                      strokeDasharray="2 14" strokeLinecap="round"
                      className="animate-flow-dash" strokeOpacity={0.9}
                    />
                  )}
                </g>
              );
            })}

            {hoveredPort && hoveredPort.grandchildren.length > 0 && (
              <SubFan port={hoveredPort} y={TOP + ports.indexOf(hoveredPort) * PITCH} />
            )}

            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
              {ports.map((p, i) => (
                <PortCard key={p.slug} port={p} y={TOP + i * PITCH} hovered={hover === p.slug} onHover={setHover} />
              ))}
              <MasterCore cy={cy} status={masterStatus} activePorts={activePorts} />
            </motion.g>
          </svg>
        </div>

        {/* info strip — crisp HTML */}
        <div className="flex items-center justify-between gap-3 mt-3 text-xs min-h-[20px]">
          {hoveredPort ? (
            <span className="flex items-center gap-2 min-w-0">
              <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: STATUS_COLOR[hoveredPort.status] }} />
              <span className="text-slate-200 font-medium truncate">{hoveredPort.displayName}</span>
              <span className="text-slateUI truncate hidden sm:inline">
                · {hoveredPort.status} · {hoveredPort.rawCount} instances · {hoveredPort.grandchildren.length} obligations
              </span>
            </span>
          ) : (
            <span className="text-slateUI">
              <span className="text-slate-200 font-semibold">{masters.length}</span> master ·{' '}
              <span className="text-slate-200 font-semibold">{stakeholderInsts}</span> stakeholder ·{' '}
              <span className="text-slate-200 font-semibold">{grandchildInsts}</span> obligation instances
            </span>
          )}
          <span className="hidden md:flex items-center gap-3 shrink-0">
            <Legend color={STATUS_COLOR.running} label="Live" />
            <Legend color={STATUS_COLOR.completed} label="Closed" />
            <Legend color={STATUS_COLOR.paused} label="Paused" />
            <Legend color={STATUS_COLOR.faulted} label="Faulted" />
          </span>
        </div>
        <p className="text-[11px] text-slate-600 mt-1">Hover a port to trace its obligation grandchildren.</p>
      </div>
    );
  }

  return (
    <Panel id="cascade" title="Energy Flow — Crisis Cascade" subtitle="Master crisis → stakeholder ports → obligation grandchildren" accent className="h-full">
      {body}
    </Panel>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-slateUI">
      <span className="w-2 h-2 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
