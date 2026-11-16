import { useId } from "react";
import { motion } from "motion/react";
import type { Step } from "../../types";
import {
  Model,
  Label,
  CellStrip,
  Equation,
  list,
  numeric,
  type Timing,
} from "./LabPrimitives";
import { Frames } from "./StructureModels";

type Edge = {
  from: number;
  to: number;
  weight?: number;
  flow?: number;
  capacity?: number;
};
export default function GraphModel({
  step,
  algorithm,
  timing,
}: {
  step: Step;
  algorithm: string;
  timing: Timing;
}) {
  const marker = useId().replaceAll(":", ""),
    v = step.visual ?? {},
    count = step.vertexCount ?? 0;
  const positions = Array.from({ length: count }, (_, i) => ({
    x: 275 + 190 * Math.cos(Math.PI + (i * 2 * Math.PI) / Math.max(count, 1)),
    y: 195 + 145 * Math.sin(Math.PI + (i * 2 * Math.PI) / Math.max(count, 1)),
  }));
  const flows = list<Edge>(v.flowEdges),
    edges: Edge[] = flows.length ? flows : (step.edges ?? []),
    reverse = list<Edge>(v.residualEdges),
    path = list<number>(v.path),
    queue = list<number>(step.variables.frontier),
    settled = list<number>(v.settled),
    distance = list<number>(v.distances),
    reachable = list<number>(v.reachable),
    isFlow = algorithm === "max-flow",
    isDijkstra = algorithm === "dijkstra",
    isDfs = algorithm === "dfs",
    isBuild = algorithm === "graphs";
  const activePath = (e: Edge) =>
    path.some((node, i) => node === e.from && path[i + 1] === e.to);
  const drawEdge = (edge: Edge, index: number, residual = false) => {
    const a = positions[edge.from],
      b = positions[edge.to];
    if (!a || !b) return null;
    const angle = Math.atan2(b.y - a.y, b.x - a.x),
      loop = edge.from === edge.to,
      parallel = edges
        .slice(0, index)
        .some((e) => e.from === edge.from && e.to === edge.to),
      bend = residual ? -38 : parallel ? 35 : 0;
    const sx = a.x + 26 * Math.cos(angle),
      sy = a.y + 26 * Math.sin(angle),
      ex = b.x - 31 * Math.cos(angle),
      ey = b.y - 31 * Math.sin(angle),
      cx = (sx + ex) / 2 - bend * Math.sin(angle),
      cy = (sy + ey) / 2 + bend * Math.cos(angle);
    const d = loop
      ? `M${a.x - 14},${a.y - 21} C${a.x - 65},${a.y - 100} ${a.x + 65},${a.y - 100} ${a.x + 15},${a.y - 26}`
      : `M${sx},${sy} Q${cx},${cy} ${ex},${ey}`;
    const active =
        activePath(edge) || step.activeEdge === `edge-${edge.from}-${edge.to}`,
      cut =
        reachable.length > 0 &&
        reachable.includes(edge.from) &&
        !reachable.includes(edge.to) &&
        !residual;
    return (
      <g
        key={`${residual ? "residual" : "edge"}-${edge.from}-${edge.to}-${index}`}
        className={
          "lab-graph-edge " +
          (residual ? "residual " : "") +
          (active ? "active " : "") +
          (cut ? "cut" : "")
        }
      >
        <motion.path
          d={d}
          markerEnd={`url(#${marker})`}
          initial={false}
          animate={{ opacity: residual ? 0.7 : 1 }}
          transition={timing}
        />
        {(isFlow || isDijkstra) && (
          <text
            x={loop ? a.x : cx}
            y={(loop ? a.y - 67 : cy) - 9}
            textAnchor="middle"
            className="lab-edge-label"
          >
            {isFlow && !residual
              ? `${edge.flow ?? 0}/${edge.capacity ?? edge.weight}`
              : residual
                ? `r:${edge.weight}`
                : edge.weight}
          </text>
        )}
      </g>
    );
  };
  return (
    <Model
      title={
        isBuild
          ? "An edge belongs in its source row"
          : isFlow
            ? "Flow, residual paths, and the cut"
            : isDijkstra
              ? "Finalize the smallest tentative cost"
              : isDfs
                ? "Follow the active call path"
                : "Explore one distance layer at a time"
      }
      subtitle={
        isFlow
          ? "Solid labels show flow/capacity. Dashed arrows are residual reverse capacity."
          : isDijkstra
            ? "This bounded teaching graph uses a minimum scan, O(V²), rather than pretending to execute a heap."
            : isBuild
              ? "Directed endpoints are numeric IDs. Isolated rows remain visible."
              : "Edge weights do not affect this unweighted traversal."
      }
    >
      <div className="lab-graph-layout">
        <div className="lab-svg-scroll">
          <svg
            width={550}
            height={400}
            role="img"
            aria-label={`${algorithm} directed graph state`}
          >
            <defs>
              <marker
                id={marker}
                markerWidth="7"
                markerHeight="7"
                refX="6"
                refY="3"
                orient="auto"
              >
                <path d="M0,0 L6,3 L0,6" className="lab-arrow-tip" />
              </marker>
            </defs>
            {edges.map((e, i) => drawEdge(e, i))}
            {reverse.map((e, i) => drawEdge(e, i, true))}
            {positions.map((p, i) => {
              const current =
                  i ===
                  numeric(step.variables.visiting ?? step.variables.vertex),
                discovered = i === numeric(step.variables.discovered),
                done = isDijkstra
                  ? settled.includes(i)
                  : (step.array[i] ?? -1) >= 0;
              const state = current
                ? "active"
                : queue.includes(i)
                  ? "pending"
                  : done
                    ? "resolved"
                    : "";
              return (
                <g key={i} transform={`translate(${p.x},${p.y})`}>
                  <circle
                    r={26}
                    className={
                      "lab-node " +
                      state +
                      (reachable.length
                        ? reachable.includes(i)
                          ? " cut-source"
                          : " cut-sink"
                        : "")
                    }
                  />
                  <text
                    textAnchor="middle"
                    dy=".35em"
                    className="lab-node-text"
                  >
                    {i}
                  </text>
                  <text textAnchor="middle" y={47} className="lab-svg-note">
                    {isBuild
                      ? "vertex"
                      : isFlow
                        ? i === 0
                          ? "source"
                          : i === count - 1
                            ? "sink"
                            : reachable.length
                              ? reachable.includes(i)
                                ? "S side"
                                : "T side"
                              : ""
                        : discovered
                          ? "discovered"
                          : current
                            ? "current"
                            : isDfs && queue.includes(i)
                              ? "on path"
                              : queue.includes(i)
                                ? "queued"
                                : done
                                  ? "processed"
                                  : "unseen"}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        {isBuild ? (
          <div className="lab-adjacency">
            <Label>Adjacency list · outgoing neighbours</Label>
            {list<number[]>(v.adjacency).map((row, i) => (
              <div key={i} className={step.active.includes(i) ? "active" : ""}>
                <strong>{i}</strong>
                <span>→ {row.length ? row.join(", ") : "empty"}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="lab-graph-side">
            {isDfs ? (
              <>
                <Label>Active frames · deepest first</Label>
                <Frames
                  items={queue.map((vertex, i) => ({
                    id: "vertex-" + vertex,
                    label: `dfs(${vertex})`,
                    detail:
                      i === queue.length - 1
                        ? "exploring"
                        : "waiting for return",
                  }))}
                  timing={timing}
                />
              </>
            ) : !isFlow && !isDijkstra ? (
              <>
                <Label>FIFO queue · front first</Label>
                <CellStrip
                  items={queue.map((vertex, i) => ({
                    id: "queued-" + vertex,
                    label: vertex,
                    index: i,
                    state: i === 0 ? "active" : "",
                  }))}
                  timing={timing}
                  label="BFS frontier"
                />
              </>
            ) : null}
            {!isDfs && !isFlow && (
              <>
                <Label>
                  {isDijkstra ? "Tentative costs" : "Minimum edge distances"}
                </Label>
                <div className="lab-distance-table">
                  {positions.map((_, i) => (
                    <div
                      key={i}
                      className={step.active.includes(i) ? "active" : ""}
                    >
                      <span>vertex {i}</span>
                      <strong>
                        {(distance[i] ?? -1) < 0 ? "∞" : distance[i]}
                      </strong>
                      {isDijkstra && (
                        <small>
                          {settled.includes(i) ? "final" : "tentative"}
                        </small>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
      {v.equation !== undefined && <Equation>{String(v.equation)}</Equation>}
      {isFlow && (
        <Equation>
          Total flow: {numeric(v.total, 0)}
          {reachable.length > 0 && (
            <>
              {" "}
              · cut capacity: {numeric(v.cutCapacity, 0)} · S = {"{"}
              {reachable.join(", ")}
              {"}"}
            </>
          )}
        </Equation>
      )}
      <div className="lab-state-key">
        <span>current / selected</span>
        <span>pending / on path</span>
        <span>processed</span>
        {isFlow && <span>cut edges</span>}
      </div>
    </Model>
  );
}
