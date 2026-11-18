import { motion } from "motion/react";
import type { Step } from "../../types";
import { list, object, type Timing } from "./LabPrimitives";

/** Panels a board trace sends with each step; drawn as they are, so new concepts need no new renderer. */
type Panel = {
  type: "array" | "stack" | "text" | "table" | "graph" | "vars";
  title: string;
} & Record<string, unknown>;

const stateOf = (marks: unknown, i: number) =>
  String(object(marks)[String(i)] ?? "");

function ArrayPanel({ p, timing }: { p: Panel; timing: Timing }) {
  const labels = list<unknown>(p.labels);
  return (
    <ol className="board-array">
      {list<unknown>(p.values).map((v, i) => (
        <motion.li
          key={i}
          layout
          className={"board-cell " + stateOf(p.marks, i)}
          transition={timing}
        >
          <span>{String(v)}</span>
          <small>{labels.length ? String(labels[i]) : i}</small>
        </motion.li>
      ))}
    </ol>
  );
}

function TextPanel({ p }: { p: Panel }) {
  const offset = Number(p.offset ?? 0);
  return (
    <ol
      className="board-array text"
      style={{ paddingLeft: `calc(${offset} * var(--board-cell))` }}
    >
      {list<string>(p.chars).map((c, i) => (
        <li key={i} className={"board-cell " + stateOf(p.marks, i)}>
          <span>{c}</span>
          <small>{offset + i}</small>
        </li>
      ))}
    </ol>
  );
}

function StackPanel({ p, timing }: { p: Panel; timing: Timing }) {
  const items = list<unknown>(p.items);
  return items.length ? (
    <ol className="board-stack">
      {items.map((v, i) => (
        <motion.li
          key={String(v)}
          layout
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={timing}
        >
          {String(v)}
        </motion.li>
      ))}
    </ol>
  ) : (
    <p className="board-empty">empty</p>
  );
}

function TablePanel({ p }: { p: Panel }) {
  const active = list<number>(p.active);
  const refs = list<number[]>(p.refs);
  const isRef = (r: number, c: number) =>
    refs.some((x) => x[0] === r && x[1] === c);
  return (
    <div className="board-table-wrap">
      <table className="board-table">
        <thead>
          <tr>
            <th />
            {list<unknown>(p.cols).map((c, j) => (
              <th key={j} scope="col">
                {String(c)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {list<unknown[]>(p.cells).map((row, r) => (
            <tr key={r}>
              <th scope="row">{String(list<unknown>(p.rows)[r])}</th>
              {row.map((v, c) => (
                <td
                  key={c}
                  className={
                    active[0] === r && active[1] === c
                      ? "active"
                      : isRef(r, c)
                        ? "ref"
                        : v === null
                          ? "empty"
                          : ""
                  }
                >
                  {v === null ? "·" : String(v)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GraphPanel({ p }: { p: Panel }) {
  const n = Number(p.n ?? 0);
  const size = 260,
    c = size / 2,
    radius = n > 1 ? 96 : 0;
  const at = (i: number) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / Math.max(1, n);
    return { x: c + radius * Math.cos(a), y: c + radius * Math.sin(a) };
  };
  const labels = object(p.labels);
  const directed = Boolean(p.directed);
  return (
    <svg
      className="board-graph"
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={p.title || "Graph"}
    >
      <defs>
        <marker
          id="board-arrow"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
        </marker>
      </defs>
      {list<Record<string, unknown>>(p.edges).map((e, k) => {
        const a = at(Number(e.from)),
          b = at(Number(e.to));
        const dx = b.x - a.x,
          dy = b.y - a.y,
          len = Math.hypot(dx, dy) || 1;
        const r = 17; // stop at the node's edge
        const x1 = a.x + (dx / len) * r,
          y1 = a.y + (dy / len) * r,
          x2 = b.x - (dx / len) * r,
          y2 = b.y - (dy / len) * r;
        return (
          <g key={k} className={"board-edge " + String(e.state ?? "")}>
            {e.from === e.to ? (
              <circle cx={a.x} cy={a.y - 22} r={8} fill="none" />
            ) : (
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                markerEnd={directed ? "url(#board-arrow)" : undefined}
              />
            )}
            {e.w !== undefined && (
              <text
                x={(a.x + b.x) / 2 + (dy / len) * 9}
                y={e.from === e.to ? a.y - 38 : (a.y + b.y) / 2 - (dx / len) * 9}
                textAnchor="middle"
                dominantBaseline="middle"
              >
                {String(e.w)}
              </text>
            )}
          </g>
        );
      })}
      {Array.from({ length: n }, (_, i) => {
        const { x, y } = at(i);
        return (
          <g key={i} className={"board-node " + stateOf(p.marks, i)}>
            <circle cx={x} cy={y} r={15} />
            <text x={x} y={y} textAnchor="middle" dominantBaseline="central">
              {i}
            </text>
            {labels[String(i)] !== undefined && (
              <text
                className="board-node-label"
                x={x}
                y={y + (y > c ? 28 : -26)}
                textAnchor="middle"
                dominantBaseline="central"
              >
                {String(labels[String(i)])}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

function VarsPanel({ p }: { p: Panel }) {
  return (
    <dl className="board-vars">
      {Object.entries(object(p.items)).map(([k, v]) => (
        <div key={k}>
          <dt>{k}</dt>
          <dd>{Array.isArray(v) ? v.join(", ") : String(v)}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function BoardModel({
  step,
  timing,
}: {
  step: Step;
  timing: Timing;
}) {
  const panels = list<Panel>((step as unknown as { board?: unknown }).board);
  return (
    <div className="board">
      {panels.map((p, i) => (
        <section key={i} className={"board-panel " + p.type}>
          {p.title && <h4>{p.title}</h4>}
          {p.type === "array" && <ArrayPanel p={p} timing={timing} />}
          {p.type === "text" && <TextPanel p={p} />}
          {p.type === "stack" && <StackPanel p={p} timing={timing} />}
          {p.type === "table" && <TablePanel p={p} />}
          {p.type === "graph" && <GraphPanel p={p} />}
          {p.type === "vars" && <VarsPanel p={p} />}
        </section>
      ))}
    </div>
  );
}
