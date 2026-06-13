import { useCallback, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { CaseInstanceGetResponse } from '@uipath/uipath-typescript/cases';
import {
  dedupeByLabel,
  formatTime,
  getDisplayLabel,
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

const MARGIN = 90;
const SP = 74; // horizontal spacing per node at full zoom
const Y = { master: 90, parent: 430, child: 760 } as const;
const R = { master: 30, parent: 15, child: 10 } as const;
const BASE_H = 880;
const VIEW_PX_H = 560; // on-screen viewport height
const LABEL_ZOOM = 0.75; // show node labels at/above this zoom
const MIN_Z = 0.06;
const MAX_Z = 6;

interface Node {
  inst: CaseInstanceGetResponse;
  x: number;
  y: number;
  label: string;
  parentX: number;
  parentY: number;
}

function shortLabel(inst: CaseInstanceGetResponse, dense: boolean): string {
  const slug = slugFromInstance(inst);
  if (dense) return slug ?? getExternalId(inst).slice(0, 6);
  const known = slug && STAKEHOLDERS.find((s) => s.slug === slug);
  if (known) return known.displayName;
  const label = getDisplayLabel(inst).replace(/^clearflow[-\s]*/i, '');
  return label.length > 20 ? `${label.slice(0, 18)}…` : label;
}

function edgePath(x1: number, y1: number, x2: number, y2: number): string {
  const dy = (y2 - y1) * 0.5;
  return `M ${x1} ${y1} C ${x1} ${y1 + dy} ${x2} ${y2 - dy} ${x2} ${y2}`;
}

interface Layout {
  master: Node | null;
  parents: Node[];
  children: Node[];
  width: number;
}

function buildLayout(instances: CaseInstanceGetResponse[]): Layout {
  const masters = instances.filter((i) => inferCaseLevel(i) === 0);
  const parentInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 1));
  const childInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 2));
  const dense = parentInsts.length + childInsts.length > 18;

  const maxCount = Math.max(parentInsts.length, childInsts.length, 1);
  const width = MARGIN * 2 + Math.max(0, maxCount - 1) * SP;
  const cx = width / 2;
  const rowX = (count: number, i: number): number =>
    count <= 1 ? cx : MARGIN + ((width - MARGIN * 2) * i) / (count - 1);

  const master: Node | null = masters[0]
    ? { inst: masters[0], x: cx, y: Y.master, label: 'Master crisis', parentX: cx, parentY: Y.master }
    : null;

  const parents: Node[] = parentInsts.map((inst, i) => ({
    inst, x: rowX(parentInsts.length, i), y: Y.parent,
    label: shortLabel(inst, dense), parentX: cx, parentY: Y.master,
  }));

  const children: Node[] = childInsts.map((inst, i) => {
    const slug = slugFromInstance(inst);
    const owner = slug ? parents.find((p) => slugFromInstance(p.inst) === slug) : undefined;
    return {
      inst, x: rowX(childInsts.length, i), y: Y.child,
      label: shortLabel(inst, dense),
      parentX: owner ? owner.x : cx,
      parentY: owner ? owner.y : Y.master,
    };
  });

  return { master, parents, children, width };
}

function GraphNode({ node, r, showLabel, pop, delay }: {
  node: Node; r: number; showLabel: boolean; pop: boolean; delay: number;
}) {
  const tone = statusTone(node.inst.latestRunStatus);
  const meta = `${getDisplayLabel(node.inst)}\n${getExternalId(node.inst)} · ${node.inst.latestRunStatus ?? 'Unknown'} · started ${formatTime(node.inst.startedTime)}`;
  const inner = (
    <>
      <circle r={r + 5} fill={tone.stroke} opacity={0.18} />
      <circle r={r} fill={tone.fill} stroke={tone.stroke} strokeWidth={2.5} />
      {showLabel && (
        <text y={r + 17} textAnchor="middle" className="fill-slate-300"
          style={{ fontSize: r >= R.parent ? 15 : 13, fontWeight: 600 }}>
          {node.label}
        </text>
      )}
    </>
  );
  return (
    <g transform={`translate(${node.x},${node.y})`}>
      <title>{meta}</title>
      {pop ? (
        <motion.g initial={{ opacity: 0, scale: 0.4 }} animate={{ opacity: 1, scale: 1 }}
          transition={{ type: 'spring', stiffness: 220, damping: 18, delay }}>
          {inner}
        </motion.g>
      ) : (
        <g>{inner}</g>
      )}
    </g>
  );
}

/** Zoom/pan viewport: wheel to zoom (center-anchored), drag to pan, fit on mount. */
function ZoomPanCanvas({ width, children, onZoom }: {
  width: number; children: React.ReactNode; onZoom: (z: number) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(0.2);
  const fitRef = useRef(0.2);
  const prevZoom = useRef(0.2);
  const drag = useRef<{ x: number; y: number; sl: number; st: number } | null>(null);

  const fit = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const z = Math.max(MIN_Z, Math.min(1, el.clientWidth / width));
    fitRef.current = z;
    prevZoom.current = z;
    setZoom(z);
    onZoom(z);
    el.scrollLeft = (width * z - el.clientWidth) / 2;
    el.scrollTop = 0;
  }, [width, onZoom]);

  useLayoutEffect(() => { fit(); }, [fit]);

  // Keep the viewport centre stable across zoom changes.
  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el || prevZoom.current === zoom) return;
    const ratio = zoom / prevZoom.current;
    el.scrollLeft = (el.scrollLeft + el.clientWidth / 2) * ratio - el.clientWidth / 2;
    el.scrollTop = (el.scrollTop + el.clientHeight / 2) * ratio - el.clientHeight / 2;
    prevZoom.current = zoom;
  }, [zoom]);

  const applyZoom = useCallback((factor: number) => {
    setZoom((z) => {
      const next = Math.max(MIN_Z, Math.min(MAX_Z, z * factor));
      onZoom(next);
      return next;
    });
  }, [onZoom]);

  // Native non-passive wheel listener so preventDefault() actually suppresses
  // page scroll (React's synthetic onWheel is passive and would warn).
  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      applyZoom(e.deltaY < 0 ? 1.15 : 0.87);
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, [applyZoom]);

  const onPointerDown = (e: React.PointerEvent) => {
    const el = containerRef.current;
    if (!el) return;
    el.setPointerCapture(e.pointerId);
    drag.current = { x: e.clientX, y: e.clientY, sl: el.scrollLeft, st: el.scrollTop };
  };
  const onPointerMove = (e: React.PointerEvent) => {
    const el = containerRef.current;
    if (!el || !drag.current) return;
    el.scrollLeft = drag.current.sl - (e.clientX - drag.current.x);
    el.scrollTop = drag.current.st - (e.clientY - drag.current.y);
  };
  const endDrag = (e: React.PointerEvent) => {
    containerRef.current?.releasePointerCapture(e.pointerId);
    drag.current = null;
  };

  const btnClass =
    'w-8 h-8 flex items-center justify-center rounded-md border border-ink-600 bg-ink-850/80 text-slate-300 hover:border-accent/50 hover:text-accent text-sm font-bold backdrop-blur';

  return (
    <div className="relative">
      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
        <button className={btnClass} title="Zoom in" onClick={() => applyZoom(1.3)}>+</button>
        <button className={btnClass} title="Zoom out" onClick={() => applyZoom(0.77)}>−</button>
        <button className={btnClass} title="Fit to view" onClick={fit}>⤢</button>
      </div>
      <span className="absolute bottom-3 left-3 z-10 text-[10px] text-slate-500 bg-ink-950/60 px-2 py-1 rounded backdrop-blur pointer-events-none">
        scroll to zoom · drag to pan · {Math.round(zoom * 100)}%
      </span>
      <div
        ref={containerRef}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerLeave={endDrag}
        className="overflow-auto rounded-lg border border-ink-700/50 bg-ink-950/40 cursor-grab active:cursor-grabbing"
        style={{ height: VIEW_PX_H, touchAction: 'none' }}
      >
        <svg
          width={width * zoom}
          height={BASE_H * zoom}
          viewBox={`0 0 ${width} ${BASE_H}`}
          style={{ display: 'block' }}
        >
          {children}
        </svg>
      </div>
    </div>
  );
}

/**
 * The hero: a zoomable/pannable three-level node-link graph of the case cascade.
 * Master crisis fans to every stakeholder parent, which fan to obligation
 * grandchildren. Scales to any node count — fit-to-view by default, zoom to
 * read labels. Levels inferred from packageId/processKey.
 */
export function CascadeGraph({ instances, isLoading, error }: CascadeGraphProps) {
  const layout = useMemo(() => buildLayout(instances ?? []), [instances]);
  const [zoom, setZoom] = useState(0.2);
  const { master, parents, children, width } = layout;
  const total = (instances ?? []).length;
  const nodeCount = (master ? 1 : 0) + parents.length + children.length;
  const pop = nodeCount <= 36; // spring-pop only when the graph is small enough
  const showLabels = zoom >= LABEL_ZOOM || nodeCount <= 16;
  const capDelay = (i: number) => Math.min(i * 0.02, 0.9);

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
        <ZoomPanCanvas width={width} onZoom={setZoom}>
          <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
            {/* edges: master → parents (dense teal fan) */}
            {master && parents.map((p) => (
              <path key={`em-${p.inst.instanceId}`}
                d={edgePath(master.x, master.y + R.master, p.x, p.y - R.parent)}
                fill="none" stroke="#2DD4BF" strokeWidth={1.2} strokeOpacity={0.3} />
            ))}
            {/* edges: parent → grandchildren */}
            {children.map((c) => (
              <path key={`ec-${c.inst.instanceId}`}
                d={edgePath(c.parentX, c.parentY + R.parent, c.x, c.y - R.child)}
                fill="none" stroke="#5EEAD4" strokeWidth={1.2} strokeOpacity={0.32} />
            ))}
            {/* nodes */}
            {master && <GraphNode node={master} r={R.master} showLabel pop={pop} delay={0} />}
            {parents.map((p, i) => <GraphNode key={p.inst.instanceId} node={p} r={R.parent} showLabel={showLabels} pop={pop} delay={capDelay(i)} />)}
            {children.map((c, i) => <GraphNode key={c.inst.instanceId} node={c} r={R.child} showLabel={showLabels} pop={pop} delay={capDelay(parents.length + i)} />)}
          </motion.g>
        </ZoomPanCanvas>

        <div className="flex items-center justify-between gap-3 mt-2 text-xs text-slate-500 flex-wrap">
          <span>
            <span className="text-slate-300 font-semibold">{master ? 1 : 0}</span> master ·{' '}
            <span className="text-slate-300 font-semibold">{parents.length}</span> stakeholders ·{' '}
            <span className="text-slate-300 font-semibold">{children.length}</span> grandchildren
          </span>
          <span className="flex items-center gap-3">
            <Legend color="#34D399" label="Completed" />
            <Legend color="#38BDF8" label="Running" />
            <Legend color="#F59E0B" label="Paused" />
            <Legend color="#F43F5E" label="Faulted" />
          </span>
          {children.length === 0 && <span className="italic text-slate-600 w-full">Grandchildren spawn at Reversal 3</span>}
        </div>
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
    <span className="inline-flex items-center gap-1.5">
      <span className="w-2 h-2 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
