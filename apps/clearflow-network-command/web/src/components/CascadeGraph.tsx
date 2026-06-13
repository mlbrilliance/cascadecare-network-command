import { useCallback, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import {
  dedupeByLabel,
  formatTime,
  getExternalId,
  inferCaseLevel,
  slugFromInstance,
  statusTone,
} from '../caseUtils';
import { STAKEHOLDERS } from '../narrative';
import { Panel, PanelError, PanelLoading } from './Panel';

interface CascadeGraphProps {
  instances: CaseInstanceGetResponse[] | null;
  isLoading: boolean;
  error: Error | null;
}

const R = { master: 24, stakeholder: 8.5, grandchild: 6.5 } as const;
const MIN_Z = 0.1;
const MAX_Z = 6;
const VIEW_PX_H = 580;
const START = -Math.PI / 2; // first node at top

/** Best human name for the info strip (real stakeholder name, else tier + seq). */
function niceName(inst: CaseInstanceGetResponse, kind: 'stakeholder' | 'grandchild', seq: number): string {
  const slug = slugFromInstance(inst);
  const known = slug ? STAKEHOLDERS.find((s) => s.slug === slug) : undefined;
  if (known) return known.displayName;
  const title = (inst.caseTitle || inst.instanceDisplayName || '').replace(/^clearflow[-\s]*/i, '').trim();
  if (title && !/^[0-9a-f-]{8,}$/i.test(title)) return title;
  return kind === 'stakeholder' ? `Stakeholder ${seq}` : `Obligation ${seq}`;
}

interface Node {
  inst: CaseInstanceGetResponse;
  x: number;
  y: number;
  r: number;
  name: string;
  /** edge target (parent) — center for stakeholders, owner/center for grandchildren */
  px: number;
  py: number;
}

interface Particle { x: number; y: number; s: number; o: number; c: string; d: number; dur: number }

interface Layout {
  master: CaseInstanceGetResponse | null;
  stakeholders: Node[];
  grandchildren: Node[];
  half: number;
  viewBox: string;
}

/** Seeded RNG so the particle field is stable across re-renders. */
function mulberry32(seed: number): () => number {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function buildLayout(instances: CaseInstanceGetResponse[]): Layout {
  const masters = instances.filter((i) => inferCaseLevel(i) === 0);
  const sInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 1));
  const gInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 2));

  const innerR = Math.max(240, sInsts.length * 6.4);
  const outerR = innerR + 150;
  const half = outerR + 90;

  const ring = (count: number, i: number, radius: number) => {
    const a = START + (count > 0 ? (i / count) * Math.PI * 2 : 0);
    return { x: Math.cos(a) * radius, y: Math.sin(a) * radius };
  };

  const stakeholders: Node[] = sInsts.map((inst, i) => {
    const p = ring(sInsts.length, i, innerR);
    return { inst, x: p.x, y: p.y, r: R.stakeholder, name: niceName(inst, 'stakeholder', i + 1), px: 0, py: 0 };
  });

  const grandchildren: Node[] = gInsts.map((inst, i) => {
    const p = ring(gInsts.length, i, outerR);
    const slug = slugFromInstance(inst);
    const owner = slug ? stakeholders.find((s) => slugFromInstance(s.inst) === slug) : undefined;
    return {
      inst, x: p.x, y: p.y, r: R.grandchild, name: niceName(inst, 'grandchild', i + 1),
      px: owner ? owner.x : 0, py: owner ? owner.y : 0,
    };
  });

  return { master: masters[0] ?? null, stakeholders, grandchildren, half, viewBox: `${-half} ${-half} ${half * 2} ${half * 2}` };
}

function buildParticles(half: number, count: number): Particle[] {
  const rand = mulberry32(Math.round(half) * 131 + count);
  const out: Particle[] = [];
  for (let i = 0; i < 120; i++) {
    const ang = rand() * Math.PI * 2;
    const rad = half * 1.05 * Math.pow(rand(), 1.45); // denser toward centre
    out.push({
      x: Math.cos(ang) * rad,
      y: Math.sin(ang) * rad,
      s: 2 + rand() * 5,
      o: 0.08 + rand() * 0.4,
      c: rand() > 0.62 ? '#F59E0B' : '#2DD4BF',
      d: rand() * 4,
      dur: 2.5 + rand() * 4,
    });
  }
  return out;
}

function ConstellationNode({ node, kind, hovered, onHover }: {
  node: Node; kind: 'stakeholder' | 'grandchild'; hovered: boolean; onHover: (n: Node | null) => void;
}) {
  const tone = statusTone(node.inst.latestRunStatus);
  const r = hovered ? node.r * 1.5 : node.r;
  return (
    <g
      transform={`translate(${node.x},${node.y})`}
      onMouseEnter={() => onHover(node)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      <circle r={node.r + 14} fill="transparent" />
      <circle r={r + (hovered ? 9 : 5)} fill={tone.stroke} opacity={hovered ? 0.35 : 0.16} />
      <circle r={r} fill={tone.fill} stroke={tone.stroke} strokeWidth={hovered ? 2.5 : 1.8}
        opacity={kind === 'grandchild' ? 0.92 : 1} />
    </g>
  );
}

/** Generalized zoom/pan viewport: wheel-zoom (centre-anchored), drag-pan, fit-on-mount. */
function ZoomPanCanvas({ contentW, contentH, viewBox, onZoom, children }: {
  contentW: number; contentH: number; viewBox: string; onZoom: (z: number) => void; children: React.ReactNode;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(0.3);
  const prevZoom = useRef(0.3);
  const drag = useRef<{ x: number; y: number; sl: number; st: number; moved: boolean } | null>(null);

  const fit = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const z = Math.max(MIN_Z, Math.min(1, Math.min(el.clientWidth / contentW, el.clientHeight / contentH)));
    prevZoom.current = z;
    setZoom(z);
    onZoom(z);
    el.scrollLeft = (contentW * z - el.clientWidth) / 2;
    el.scrollTop = (contentH * z - el.clientHeight) / 2;
  }, [contentW, contentH, onZoom]);

  useLayoutEffect(() => { fit(); }, [fit]);

  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el || prevZoom.current === zoom) return;
    const ratio = zoom / prevZoom.current;
    el.scrollLeft = (el.scrollLeft + el.clientWidth / 2) * ratio - el.clientWidth / 2;
    el.scrollTop = (el.scrollTop + el.clientHeight / 2) * ratio - el.clientHeight / 2;
    prevZoom.current = zoom;
  }, [zoom]);

  const applyZoom = useCallback((factor: number) => {
    setZoom((z) => { const next = Math.max(MIN_Z, Math.min(MAX_Z, z * factor)); onZoom(next); return next; });
  }, [onZoom]);

  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => { e.preventDefault(); applyZoom(e.deltaY < 0 ? 1.15 : 0.87); };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, [applyZoom]);

  const onPointerDown = (e: React.PointerEvent) => {
    const el = containerRef.current; if (!el) return;
    el.setPointerCapture(e.pointerId);
    drag.current = { x: e.clientX, y: e.clientY, sl: el.scrollLeft, st: el.scrollTop, moved: false };
  };
  const onPointerMove = (e: React.PointerEvent) => {
    const el = containerRef.current; if (!el || !drag.current) return;
    el.scrollLeft = drag.current.sl - (e.clientX - drag.current.x);
    el.scrollTop = drag.current.st - (e.clientY - drag.current.y);
  };
  const endDrag = (e: React.PointerEvent) => { containerRef.current?.releasePointerCapture(e.pointerId); drag.current = null; };

  const btn = 'w-8 h-8 flex items-center justify-center rounded-md border border-ink-600 bg-ink-850/80 text-slate-300 hover:border-accent/50 hover:text-accent text-sm font-bold backdrop-blur';

  return (
    <div className="relative">
      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
        <button className={btn} title="Zoom in" onClick={() => applyZoom(1.3)}>+</button>
        <button className={btn} title="Zoom out" onClick={() => applyZoom(0.77)}>−</button>
        <button className={btn} title="Fit to view" onClick={fit}>⤢</button>
      </div>
      <span className="absolute bottom-3 left-3 z-10 text-[10px] text-slate-500 bg-ink-950/60 px-2 py-1 rounded backdrop-blur pointer-events-none">
        scroll to zoom · drag to pan · hover a node for detail
      </span>
      <div
        ref={containerRef}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerLeave={endDrag}
        className="overflow-hidden rounded-lg border border-ink-700/50 bg-[#040810] cursor-grab active:cursor-grabbing"
        style={{ height: VIEW_PX_H, touchAction: 'none' }}
      >
        <svg width={contentW * zoom} height={contentH * zoom} viewBox={viewBox} style={{ display: 'block' }}>
          {children}
        </svg>
      </div>
    </div>
  );
}

/**
 * The hero: a radial constellation of the case cascade. The master crisis is a
 * glowing core; stakeholder parents orbit on an inner ring and obligation
 * grandchildren on an outer ring, each linked by a thin sunburst edge. Glowing
 * nodes carry no inline text (so it never garbles at any density) — hovering a
 * node lights it up and surfaces its real name/status in the info strip below.
 * Levels inferred from packageId/processKey.
 */
export function CascadeGraph({ instances, isLoading, error }: CascadeGraphProps) {
  const layout = useMemo(() => buildLayout(instances ?? []), [instances]);
  const particles = useMemo(() => buildParticles(layout.half, (instances ?? []).length), [layout.half, instances]);
  const [, setZoom] = useState(0.3);
  const [hover, setHover] = useState<Node | null>(null);
  const { master, stakeholders, grandchildren, half, viewBox } = layout;
  const total = (instances ?? []).length;
  const side = half * 2;
  const masterTone = master ? statusTone(master.latestRunStatus) : statusTone(null);
  const hoveredId = hover?.inst.instanceId;

  let body;
  if (error && !instances) {
    body = <PanelError message={`Failed to load case instances: ${error.message}`} />;
  } else if (isLoading && !instances) {
    body = <PanelLoading label="Loading cascade…" />;
  } else if (total === 0) {
    body = (
      <p className="text-sm text-slate-500 py-12 text-center">
        Awaiting first signal — fire <span className="text-accent font-semibold">Reversal 1</span> to open the master crisis case.
      </p>
    );
  } else {
    body = (
      <div>
        {error && <div className="mb-3"><PanelError message={`Refresh failed: ${error.message}`} /></div>}
        <ZoomPanCanvas contentW={side} contentH={side} viewBox={viewBox} onZoom={setZoom}>
          {/* ambiance: faint guide rings */}
          <circle r={half * 0.62} fill="none" stroke="#2DD4BF" strokeOpacity={0.06} />
          <circle r={half * 0.86} fill="none" stroke="#2DD4BF" strokeOpacity={0.05} />
          {/* stardust */}
          {particles.map((p, i) => (
            <rect key={`p${i}`} x={p.x} y={p.y} width={p.s} height={p.s} fill={p.c} opacity={p.o}
              className="animate-pulse" style={{ animationDelay: `${p.d}s`, animationDuration: `${p.dur}s` }} />
          ))}

          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }}>
            {/* edges: centre → stakeholders */}
            {master && stakeholders.map((s) => {
              const on = hoveredId === s.inst.instanceId;
              return <line key={`es${s.inst.instanceId}`} x1={0} y1={0} x2={s.x} y2={s.y}
                stroke="#2DD4BF" strokeWidth={on ? 1.8 : 0.9} strokeOpacity={on ? 0.85 : 0.22} />;
            })}
            {/* edges: grandchild → owner (or centre) */}
            {grandchildren.map((g) => {
              const on = hoveredId === g.inst.instanceId;
              return <line key={`eg${g.inst.instanceId}`} x1={g.px} y1={g.py} x2={g.x} y2={g.y}
                stroke="#5EEAD4" strokeWidth={on ? 1.8 : 0.8} strokeOpacity={on ? 0.85 : 0.2} />;
            })}

            {/* nodes */}
            {grandchildren.map((g) => (
              <ConstellationNode key={g.inst.instanceId} node={g} kind="grandchild" hovered={hoveredId === g.inst.instanceId} onHover={setHover} />
            ))}
            {stakeholders.map((s) => (
              <ConstellationNode key={s.inst.instanceId} node={s} kind="stakeholder" hovered={hoveredId === s.inst.instanceId} onHover={setHover} />
            ))}

            {/* master core */}
            {master && (
              <g>
                <circle r={R.master + 16} fill={masterTone.stroke} opacity={0.12} className="animate-pulse" style={{ animationDuration: '3s' }} />
                <circle r={R.master + 7} fill={masterTone.stroke} opacity={0.2} />
                <circle r={R.master} fill={masterTone.fill} stroke={masterTone.stroke} strokeWidth={3} />
                <text y={5} textAnchor="middle" className="fill-slate-100" style={{ fontSize: 13, fontWeight: 700, letterSpacing: 1 }}>CFCS</text>
                <text y={R.master + 22} textAnchor="middle" className="fill-slate-400" style={{ fontSize: 12, fontWeight: 600, letterSpacing: 2 }}>MASTER CRISIS</text>
              </g>
            )}
          </motion.g>
        </ZoomPanCanvas>

        {/* info strip — crisp HTML, updates on hover (no canvas text → no garble) */}
        <div className="flex items-center justify-between gap-3 mt-2 text-xs min-h-[34px]">
          {hover ? (
            <div className="flex items-center gap-2 min-w-0">
              <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: statusTone(hover.inst.latestRunStatus).stroke }} />
              <span className="text-slate-200 font-medium truncate">{hover.name}</span>
              <span className="text-slate-500 truncate hidden sm:inline">
                · {hover.inst.latestRunStatus ?? 'Unknown'} · {getExternalId(hover.inst).slice(0, 8)} · started {formatTime(hover.inst.startedTime)}
              </span>
            </div>
          ) : (
            <span className="text-slate-500">
              <span className="text-slate-300 font-semibold">{master ? 1 : 0}</span> master ·{' '}
              <span className="text-slate-300 font-semibold">{stakeholders.length}</span> stakeholders ·{' '}
              <span className="text-slate-300 font-semibold">{grandchildren.length}</span> grandchildren
            </span>
          )}
          <span className="flex items-center gap-3 shrink-0">
            <Legend color="#34D399" label="Completed" />
            <Legend color="#38BDF8" label="Running" />
            <Legend color="#F59E0B" label="Paused" />
            <Legend color="#F43F5E" label="Faulted" />
          </span>
        </div>
        {grandchildren.length === 0 && <p className="text-xs italic text-slate-600 mt-1">Grandchildren spawn at Reversal 3</p>}
      </div>
    );
  }

  return (
    <Panel title="Cascade" subtitle="Master crisis → stakeholder parents → obligation grandchildren" accent>
      {body}
    </Panel>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-slate-500">
      <span className="w-2 h-2 rounded-full" style={{ background: color }} />
      <span className="hidden md:inline">{label}</span>
    </span>
  );
}
