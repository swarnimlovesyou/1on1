import { ArrowRight } from "@phosphor-icons/react";
import type { Step, Tree } from "../../types";
export default function LegacyStateView({
  step,
  family,
}: {
  step: Step;
  family: string;
}) {
  if (family === "graph" && step.edges) {
    const n = step.vertexCount ?? 6,
      positions = Array.from({ length: n }, (_, i) => ({
        x: 70 + (i % 4) * 130,
        y: 60 + Math.floor(i / 4) * 135,
      }));
    return (
      <svg
        className="diagram"
        viewBox="0 0 560 270"
        role="img"
        aria-label="Directed graph; highlighted vertex is currently being processed"
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="24"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>
        {step.edges.map((e, i) => (
          <g key={i}>
            <line
              className="graph-edge"
              x1={positions[e.from].x}
              y1={positions[e.from].y}
              x2={positions[e.to].x}
              y2={positions[e.to].y}
              markerEnd="url(#arrow)"
            />
            <text
              className="edge-label"
              x={(positions[e.from].x + positions[e.to].x) / 2}
              y={(positions[e.from].y + positions[e.to].y) / 2 - 10}
            >
              {e.weight}
            </text>
          </g>
        ))}
        {positions.map((p, i) => (
          <g key={i}>
            <circle
              className={
                "graph-node " + (step.active.includes(i) ? "active" : "")
              }
              cx={p.x}
              cy={p.y}
              r={23}
            />
            <text className="node-label" x={p.x} y={p.y + 5}>
              {String.fromCharCode(65 + i)}
            </text>
            {step.array[i] >= 0 && (
              <text className="edge-label" x={p.x} y={p.y + 43}>
                {step.array[i]}
              </text>
            )}
          </g>
        ))}
      </svg>
    );
  }
  if (family === "tree" && step.tree) return <TreeView root={step.tree} />;
  if (family === "heap") {
    const tree = (i: number): Tree | null =>
      i >= step.array.length
        ? null
        : {
            value: step.array[i],
            left: tree(i * 2 + 1),
            right: tree(i * 2 + 2),
          };
    return <TreeView root={tree(0)} />;
  }
  if (family === "trie" && step.words) {
    const root: {
      value: string;
      children: Record<string, any>;
      end?: boolean;
    } = { value: "∅", children: {} };
    step.words.forEach((word) => {
      let node = root;
      for (const char of word) {
        node.children[char] ??= { value: char, children: {} };
        node = node.children[char];
      }
      node.end = true;
    });
    const nodes: {
      x: number;
      y: number;
      value: string;
      end?: boolean;
      parent?: number;
    }[] = [];
    let leaves = 0;
    const walk = (node: any, depth: number, parent?: number) => {
      const idx = nodes.length;
      nodes.push({
        x: 0,
        y: 30 + depth * 43,
        value: node.value,
        end: node.end,
        parent,
      });
      const keys = Object.keys(node.children);
      if (!keys.length) nodes[idx].x = 45 + leaves++ * 65;
      else {
        keys.forEach((k) => walk(node.children[k], depth + 1, idx));
        nodes[idx].x =
          nodes.filter((n) => n.parent === idx).reduce((s, n) => s + n.x, 0) /
          keys.length;
      }
    };
    walk(root, 0);
    return (
      <svg
        className="diagram trie-diagram"
        viewBox={`0 0 ${Math.max(420, leaves * 65 + 50)} 300`}
        role="img"
        aria-label="Trie with shared prefixes and filled word-ending nodes"
      >
        {nodes
          .filter((n) => n.parent !== undefined)
          .map((n, i) => (
            <line
              key={i}
              className="graph-edge"
              x1={n.x}
              y1={n.y}
              x2={nodes[n.parent!].x}
              y2={nodes[n.parent!].y}
            />
          ))}
        {nodes.map((n, i) => (
          <g key={i}>
            <circle
              className={"graph-node " + (n.end ? "active" : "")}
              cx={n.x}
              cy={n.y}
              r={16}
            />
            <text className="node-label" x={n.x} y={n.y + 5}>
              {n.value}
            </text>
          </g>
        ))}
      </svg>
    );
  }
  return (
    <div
      className={
        "array-stage " +
        (family === "stack" || family === "recursion" ? "stack-stage" : "")
      }
    >
      <div className={"array-values " + (family === "dp" ? "dp-values" : "")}>
        {step.array.length ? (
          step.array.map((value, i) => (
            <div className="array-item" key={i}>
              <span
                className={
                  "array-cell " + (step.active.includes(i) ? "active" : "")
                }
              >
                {value}
              </span>
              <span className="array-index">
                {family === "dp" ? `F(${i})` : i}
              </span>
              {family === "linked" && i < step.array.length - 1 && (
                <ArrowRight className="link-arrow" size={18} />
              )}
            </div>
          ))
        ) : (
          <span className="muted">The structure is empty.</span>
        )}
      </div>
      {family === "coverage" && step.topics && (
        <div className="coverage-topics">
          {step.topics.map((t) => (
            <span className="chip" key={t}>
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
function TreeView({ root }: { root: Tree | null }) {
  const nodes: { x: number; y: number; value: number; parent?: number }[] = [];
  function walk(
    n: Tree | null,
    x: number,
    y: number,
    span: number,
    parent?: number,
  ) {
    if (!n) return;
    const idx = nodes.length;
    nodes.push({ x, y, value: n.value, parent });
    walk(n.left, x - span, y + 64, span / 2, idx);
    walk(n.right, x + span, y + 64, span / 2, idx);
  }
  walk(root, 280, 35, 120);
  return (
    <svg
      className="diagram"
      viewBox={`0 0 560 ${Math.max(250, ...nodes.map((n) => n.y + 35))}`}
      role="img"
      aria-label="Tree after the current insertion"
    >
      {nodes
        .filter((n) => n.parent !== undefined)
        .map((n, i) => (
          <line
            className="graph-edge"
            key={i}
            x1={n.x}
            y1={n.y}
            x2={nodes[n.parent!].x}
            y2={nodes[n.parent!].y}
          />
        ))}
      {nodes.map((n, i) => (
        <g key={i}>
          <circle className="graph-node" cx={n.x} cy={n.y} r={21} />
          <text className="node-label" x={n.x} y={n.y + 5}>
            {n.value}
          </text>
        </g>
      ))}
    </svg>
  );
}
