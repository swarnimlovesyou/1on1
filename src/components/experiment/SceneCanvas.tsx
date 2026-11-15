import { motion, useReducedMotion } from "motion/react";
import type { Step, Tree } from "../../types";
import LegacyStateView from "./LegacyStateView";

type Props = { step: Step; family: string; duration: number; instant: boolean };
export default function SceneCanvas({
  step,
  family,
  duration,
  instant,
}: Props) {
  const reduced = useReducedMotion();
  const transition = {
    duration: instant || reduced ? 0 : duration,
    ease: [0.16, 1, 0.3, 1] as const,
  };
  if (family === "tree")
    return (
      <TreeCanvas
        root={step.tree ?? null}
        inserted={step.variables.inserted}
        transition={transition}
      />
    );
  if (family === "graph") {
    const count = step.vertexCount ?? 0;
    const positions = Array.from({ length: count }, (_, i) => ({
      x: 66 + (i % 4) * 132,
      y: 55 + Math.floor(i / 4) * 132,
    }));
    return (
      <svg
        className="diagram trace-graph"
        viewBox="0 0 530 250"
        role="img"
        aria-label="Directed graph with the current vertex and discovered frontier"
      >
        {(step.edges ?? []).map((edge) => {
          const a = positions[edge.from],
            b = positions[edge.to];
          if (!a || !b) return null;
          const active = step.activeEdge === `edge-${edge.from}-${edge.to}`;
          const angle = Math.atan2(b.y - a.y, b.x - a.x),
            endX = b.x - 27 * Math.cos(angle),
            endY = b.y - 27 * Math.sin(angle);
          return (
            <g
              key={`${edge.from}-${edge.to}`}
              className={active ? "trace-edge is-active" : "trace-edge"}
            >
              <motion.line
                initial={false}
                animate={{ x1: a.x, y1: a.y, x2: endX, y2: endY }}
                transition={transition}
              />
              <path
                d={`M ${endX - 9 * Math.cos(angle - 0.45)} ${endY - 9 * Math.sin(angle - 0.45)} L ${endX} ${endY} L ${endX - 9 * Math.cos(angle + 0.45)} ${endY - 9 * Math.sin(angle + 0.45)}`}
              />
              <text
                x={(a.x + b.x) / 2}
                y={(a.y + b.y) / 2 - 10}
                className="edge-label"
              >
                {edge.weight}
              </text>
            </g>
          );
        })}
        {positions.map((p, i) => {
          const frontier =
            Array.isArray(step.variables.frontier) &&
            step.variables.frontier.includes(i);
          const active = step.active.includes(i),
            visited = (step.array[i] ?? -1) >= 0;
          return (
            <motion.g
              key={`vertex-${i}`}
              initial={false}
              animate={{ x: p.x, y: p.y }}
              transition={transition}
              className={
                "trace-vertex " +
                (active
                  ? "is-active"
                  : frontier
                    ? "in-frontier"
                    : visited
                      ? "is-visited"
                      : "")
              }
            >
              <circle r={24} />
              <text textAnchor="middle" dy=".35em">
                {i}
              </text>
              <text className="vertex-state" y={44} textAnchor="middle">
                {i === Number(step.variables.discovered)
                  ? "discovered"
                  : i === Number(step.variables.visiting)
                    ? "current"
                    : frontier
                      ? "queued"
                      : visited
                        ? "visited"
                        : "unseen"}
              </text>
            </motion.g>
          );
        })}
      </svg>
    );
  }
  if (
    !["array", "dp", "stack", "queue", "recursion", "bitset"].includes(family)
  )
    return <LegacyStateView step={step} family={family} />;
  const entities =
    step.entities ??
    step.array.map((value, position) => ({
      id: `legacy-${position}`,
      value,
      position,
      role: step.active.includes(position)
        ? ("active" as const)
        : ("idle" as const),
    }));
  const left = Number(step.variables.left),
    right = Number(step.variables.right);
  const window = Number.isInteger(left) && Number.isInteger(right);
  const cellWidth = 58;
  return (
    <div
      className={"trace-array-viewport " + (family === "dp" ? "trace-dp" : "")}
    >
      <div
        className="trace-array-track"
        style={{ width: Math.max(entities.length * cellWidth, 190) }}
      >
        {window && (
          <motion.div
            className="trace-window"
            initial={false}
            animate={{
              x: left * cellWidth,
              width: (right - left + 1) * cellWidth - 8,
            }}
            transition={transition}
          >
            <span>current window</span>
          </motion.div>
        )}
        {entities.map((entity, i) => (
          <motion.div
            key={entity.id}
            className={
              "trace-cell " +
              (step.active.includes(i) ? "is-active " : "") +
              (family === "dp" &&
              i === Number(step.variables.i ?? step.variables.n)
                ? "is-destination"
                : "")
            }
            initial={false}
            animate={{
              x: i * cellWidth,
              backgroundColor: step.active.includes(i)
                ? "var(--accent-wash)"
                : "var(--surface)",
            }}
            transition={transition}
          >
            <span className="trace-cell-value">{entity.value}</span>
            <span className="trace-cell-index">
              {family === "dp" ? `F(${i})` : i}
            </span>
          </motion.div>
        ))}
        {!entities.length && (
          <span className="trace-empty">The structure is empty.</span>
        )}
      </div>
      {family === "dp" && (
        <p className="trace-legend">
          Highlighted cells supply the next value. The outlined cell stores it.
        </p>
      )}
    </div>
  );
}

type Transition = {
  duration: number;
  ease: readonly [number, number, number, number];
};
function TreeCanvas({
  root,
  inserted,
  transition,
}: {
  root: Tree | null;
  inserted: unknown;
  transition: Transition;
}) {
  const nodes: {
    id: string;
    value: number;
    x: number;
    y: number;
    parent?: string;
  }[] = [];
  const walk = (
    node: Tree | null,
    x: number,
    y: number,
    span: number,
    parent?: string,
  ) => {
    if (!node) return;
    const id = node.id ?? `node-${node.value}`;
    nodes.push({ id, value: node.value, x, y, parent });
    walk(node.left, x - span, y + 74, span / 2, id);
    walk(node.right, x + span, y + 74, span / 2, id);
  };
  walk(root, 280, 36, 125);
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return (
    <svg
      className="diagram trace-tree"
      viewBox={`0 0 560 ${Math.max(220, ...nodes.map((node) => node.y + 48))}`}
      role="img"
      aria-label="Binary search tree after the current insertion"
    >
      {nodes
        .filter((node) => node.parent)
        .map((node) => {
          const parent = byId.get(node.parent!)!;
          return (
            <motion.line
              key={`${parent.id}-${node.id}`}
              className="graph-edge"
              initial={false}
              animate={{ x1: parent.x, y1: parent.y, x2: node.x, y2: node.y }}
              transition={transition}
            />
          );
        })}
      {nodes.map((node) => (
        <motion.g
          key={node.id}
          initial={false}
          animate={{ x: node.x, y: node.y }}
          transition={transition}
          className={
            "trace-vertex " + (node.value === inserted ? "is-active" : "")
          }
        >
          <circle r={23} />
          <text textAnchor="middle" dy=".35em">
            {node.value}
          </text>
        </motion.g>
      ))}
      {!root && (
        <text x={280} y={105} textAnchor="middle" className="trace-empty">
          An empty tree. Insert the first key.
        </text>
      )}
    </svg>
  );
}
