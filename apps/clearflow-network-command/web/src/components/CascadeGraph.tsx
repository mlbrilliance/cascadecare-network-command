import { useMemo } from 'react';
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

const VIEW_W = 1000;
const VIEW_H = 600;
const Y = { master: 70, parent: 300, child: 520 } as const;
const R = { master: 26, parent: 17, child: 11 } as const;
const MARGIN = 70;

interface Node {
  inst: CaseInstanceGetResponse;
  x: number;
  y: number;
  label: string;
  parentX?: number;
  parentY?: number;
}

function spread(count: number, width = VIEW_W): number[] {
  if (count <= 0) return [];
  if (count === 1) return [width / 2];
  const usable = width - MARGIN * 2;
  return Array.from({ length: count }, (_, i) => MARGIN + (usable * i) / (count - 1));
}

function shortName(inst: CaseInstanceGetResponse): string {
  const slug = slugFromInstance(inst);
  const known = slug && STAKEHOLDERS.find((s) => s.slug === slug);
  if (known) return known.displayName;
  const label = getDisplayLabel(inst).replace(/^clearflow[-\s]*/i, '');
  return label.length > 22 ? `${label.slice(0, 20)}…` : label;
}

function edgePath(x1: number, y1: number, x2: number, y2: number): string {
  const dy = (y2 - y1) * 0.5;
  return `M ${x1} ${y1} C ${x1} ${y1 + dy} ${x2} ${y2 - dy} ${x2} ${y2}`;
}

interface Layout {
  master: Node | null;
  parents: Node[];
  children: Node[];
}

function buildLayout(instances: CaseInstanceGetResponse[]): Layout {
  const masters = instances.filter((i) => inferCaseLevel(i) === 0);
  const parentInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 1));
  const childInsts = dedupeByLabel(instances.filter((i) => inferCaseLevel(i) === 2));

  const master: Node | null = masters[0]
    ? { inst: masters[0], x: VIEW_W / 2, y: Y.master, label: 'Master crisis' }
    : null;

  const px = spread(parentInsts.length);
  const parents: Node[] = parentInsts.map((inst, i) => ({
    inst, x: px[i], y: Y.parent, label: shortName(inst),
  }));

  // Place each grandchild under its matching provider parent (by slug); fall
  // back to an even spread when no parent matches.
  const cx = spread(childInsts.length);
  const children: Node[] = childInsts.map((inst, i) => {
    const slug = slugFromInstance(inst);
    const owner = slug ? parents.find((p) => slugFromInstance(p.inst) === slug) : undefined;
    return {
      inst,
      x: owner ? owner.x : cx[i],
      y: Y.child,
      label: slug ?? shortName(inst),
      parentX: owner ? owner.x : master?.x ?? VIEW_W / 2,
      parentY: owner ? owner.y : Y.parent,
    };
  });

  return { master, parents, children };
}

function GraphNode({ node, r, delay }: { node: Node; r: number; delay: number }) {
  const tone = statusTone(node.inst.latestRunStatus);
  const meta = `${getDisplayLabel(node.inst)}\n${getExternalId(node.inst)} · ${node.inst.latestRunStatus ?? 'Unknown'} · started ${formatTime(node.inst.startedTime)}`;
  return (
    <g transform={`translate(${node.x},${node.y})`} style={{ cursor: 'default' }}>
      <title>{meta}</title>
      <motion.g
        initial={{ opacity: 0, scale: 0.35 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 220, damping: 18, delay }}
      >
        <circle r={r + 5} fill={tone.stroke} opacity={0.16} />
        <circle r={r} fill={tone.fill} stroke={tone.stroke} strokeWidth={2.5} />
        <text
          y={r + 16}
          textAnchor="middle"
          className="fill-slate-300"
          style={{ fontSize: r >= R.parent ? 14 : 12, fontWeight: 600 }}
        >
          {node.label}
        </text>
      </motion.g>
    </g>
  );
}

/**
 * The hero: a three-level node-link graph of the case cascade. Master crisis
 * fans to stakeholder parents, which fan to obligation grandchildren — the
 * Reversal-3 spawn moment animates in. Levels inferred from packageId/processKey.
 */
export function CascadeGraph({ instances, isLoading, error }: CascadeGraphProps) {
  const layout = useMemo(() => buildLayout(instances ?? []), [instances]);
  const { master, parents, children } = layout;
  const total = (instances ?? []).length;

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
        <svg viewBox={`0 0 ${VIEW_W} ${VIEW_H}`} className="w-full h-auto" preserveAspectRatio="xMidYMid meet">
          {/* edges: master → parents */}
          {master && parents.map((p, i) => (
            <motion.path
              key={`em-${p.inst.instanceId}`}
              d={edgePath(master.x, master.y + R.master, p.x, p.y - R.parent)}
              fill="none" stroke="#2DD4BF" strokeWidth={1.4} strokeOpacity={0.35}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.45 }}
              transition={{ duration: 0.7, delay: 0.15 + i * 0.05 }}
            />
          ))}
          {/* edges: parent → grandchildren (the R3 fan) */}
          {children.map((c, i) => (
            <motion.path
              key={`ec-${c.inst.instanceId}`}
              d={edgePath(c.parentX ?? c.x, (c.parentY ?? Y.parent) + R.parent, c.x, c.y - R.child)}
              fill="none" stroke="#5EEAD4" strokeWidth={1.4} strokeOpacity={0.4}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.5 }}
              transition={{ duration: 0.6, delay: 0.5 + i * 0.07 }}
            />
          ))}
          {/* nodes */}
          {master && <GraphNode node={master} r={R.master} delay={0} />}
          {parents.map((p, i) => <GraphNode key={p.inst.instanceId} node={p} r={R.parent} delay={0.2 + i * 0.05} />)}
          {children.map((c, i) => <GraphNode key={c.inst.instanceId} node={c} r={R.child} delay={0.55 + i * 0.07} />)}
        </svg>

        <div className="flex items-center justify-between gap-3 mt-2 text-xs text-slate-500">
          <span>
            <span className="text-slate-300 font-semibold">{master ? 1 : 0}</span> master ·{' '}
            <span className="text-slate-300 font-semibold">{parents.length}</span> stakeholders ·{' '}
            <span className="text-slate-300 font-semibold">{children.length}</span> grandchildren
          </span>
          {children.length === 0 && (
            <span className="italic text-slate-600">Grandchildren spawn at Reversal 3</span>
          )}
        </div>
      </div>
    );
  }

  return (
    <Panel
      title="Cascade"
      subtitle="Master crisis → stakeholder parents → obligation grandchildren"
      accent
    >
      {body}
    </Panel>
  );
}
