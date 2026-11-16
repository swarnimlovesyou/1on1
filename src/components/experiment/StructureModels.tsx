import { motion } from "motion/react";
import { useId } from "react";
import type { Step, Tree } from "../../types";
import {
  Model,
  Label,
  CellStrip,
  Equation,
  Chips,
  cells,
  list,
  object,
  numeric,
  type Timing,
  type Cell,
} from "./LabPrimitives";

export default function StructureModel({
  step,
  algorithm,
  timing,
}: {
  step: Step;
  algorithm: string;
  timing: Timing;
}) {
  const v = step.visual ?? {},
    vars = step.variables;
  if (algorithm === "linked-list")
    return <LinkedList step={step} timing={timing} />;
  if (["bst", "avl", "tree-traversal", "heap"].includes(algorithm))
    return <TreeModel step={step} algorithm={algorithm} timing={timing} />;
  if (algorithm === "trie") return <TrieModel step={step} timing={timing} />;
  if (algorithm === "memoization" || algorithm === "tabulation") {
    const known = list<number>(v.known),
      dependencies = list<number>(v.dependencies),
      destination = numeric(v.destination);
    return (
      <Model
        title={
          algorithm === "memoization"
            ? "Ask, cache, and return"
            : "Compute only after dependencies"
        }
        subtitle="Unknown cells are shown as ?. A stored zero is a known value."
      >
        <Label>Dependency table</Label>
        <CellStrip
          items={cells(step).map((cell, i) => ({
            ...cell,
            label: known.includes(i) || i < 2 ? step.array[i] : "?",
            index: `F(${i})`,
            state:
              i === destination
                ? "destination"
                : dependencies.includes(i)
                  ? "dependency"
                  : known.includes(i)
                    ? "resolved"
                    : "",
          }))}
          timing={timing}
          label="Dynamic programming dependencies"
        />
        {destination >= 2 && (
          <Equation>
            F({destination}) ← F({destination - 1}) + F({destination - 2})
          </Equation>
        )}
        {algorithm === "memoization" && (
          <>
            <Label>Suspended calls · newest frame at the top</Label>
            <Frames
              items={list<number>(v.frames).map((n, i) => ({
                id: "frame-" + i,
                label: `F(${n})`,
                detail:
                  i === list(v.frames).length - 1
                    ? "active call"
                    : "waiting for dependency",
              }))}
              timing={timing}
            />
          </>
        )}
      </Model>
    );
  }
  if (algorithm === "recursion" || algorithm === "backtracking") {
    const frames = step.array.map((value, i) => ({
      id: step.entities?.[i]?.id ?? "frame-" + i,
      label:
        algorithm === "recursion" ? `factorial(${value})` : `choose ${value}`,
      detail:
        algorithm === "recursion"
          ? `waiting to multiply by ${value}`
          : `choice depth ${i + 1}`,
    }));
    return (
      <Model
        title={
          algorithm === "recursion"
            ? "One frame per suspended call"
            : "Choose → explore → undo"
        }
        subtitle={
          algorithm === "recursion"
            ? "Each frame keeps its own argument while a smaller call runs."
            : "The current path is restored before a sibling branch starts."
        }
      >
        {algorithm === "backtracking" && (
          <>
            <Label>Current subset path</Label>
            <CellStrip
              items={cells(step)}
              timing={timing}
              label="Backtracking path"
            />
          </>
        )}
        <Frames items={frames} timing={timing} />
        <Equation>
          {vars.returned !== undefined
            ? `returned ${vars.returned}`
            : vars.result !== undefined
              ? `base result ${vars.result}`
              : algorithm === "backtracking"
                ? `depth ${vars.depth ?? 0}${vars.removed !== undefined ? ` · undo ${vars.removed}` : ""}`
                : "Frames resume as the stack unwinds."}
        </Equation>
      </Model>
    );
  }
  if (algorithm === "stack")
    return (
      <Model
        title="Last in, first out"
        subtitle="Only the top is available for removal."
      >
        <Frames
          items={step.array.map((value, i) => ({
            id: step.entities?.[i]?.id ?? "stack-" + i,
            label: String(value),
            detail:
              i === step.array.length - 1 ? "top · next pop" : `depth ${i}`,
          }))}
          timing={timing}
        />
        {vars.removed !== undefined && (
          <Equation>popped {String(vars.removed)}</Equation>
        )}
      </Model>
    );
  return (
    <Model
      title="First in, first out"
      subtitle="Append at the back. Remove from the front."
    >
      <div className="lab-queue-ends">
        <span>front · next out</span>
        <span>back · next in</span>
      </div>
      <CellStrip
        items={cells(step).map((c, i) => ({
          ...c,
          pointers: [
            ...(i === 0 ? ["front"] : []),
            ...(i === step.array.length - 1 ? ["back"] : []),
          ],
        }))}
        timing={timing}
        label="FIFO queue"
      />
      {vars.removed !== undefined && (
        <Equation>dequeued {String(vars.removed)}</Equation>
      )}
    </Model>
  );
}

export function Frames({
  items,
  timing,
}: {
  items: { id: string; label: string; detail?: string }[];
  timing: Timing;
}) {
  return (
    <div className="lab-frames" aria-label="Stack frames newest first">
      {[...items].reverse().map((frame, i) => (
        <motion.div
          layout="position"
          key={frame.id}
          initial={false}
          transition={timing}
          className={"lab-frame " + (i === 0 ? "active" : "")}
        >
          <strong>{frame.label}</strong>
          <span>{frame.detail}</span>
        </motion.div>
      ))}
      {!items.length && (
        <p className="lab-empty">Stack empty · no suspended frames</p>
      )}
    </div>
  );
}

function LinkedList({ step, timing }: { step: Step; timing: Timing }) {
  const marker = useId().replaceAll(":", ""),
    v = step.visual ?? {},
    nodes = list<{ id: string; value: number }>(v.nodes),
    width = Math.max(500, nodes.length * 115 + 40),
    byId = new Map(
      nodes.map((node, i) => [node.id, { ...node, x: 60 + i * 115 }]),
    );
  const links =
    step.links ??
    nodes.map((node, i) => ({ from: node.id, to: nodes[i + 1]?.id ?? "" }));
  return (
    <Model
      title="Reverse references, keep the nodes"
      subtitle="Fixed node identities make every changed arrow visible. Values are not swapped."
    >
      <div className="lab-svg-scroll">
        <svg
          width={width}
          height={210}
          role="img"
          aria-label="Singly linked list with actual next references"
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
          {links
            .filter((link) => link.to)
            .map((link) => {
              const a = byId.get(link.from),
                b = byId.get(link.to);
              if (!a || !b) return null;
              const forward = a.x < b.x;
              return (
                <motion.path
                  key={link.from}
                  d={`M${a.x + (forward ? 27 : -27)},90 Q${(a.x + b.x) / 2},${forward ? 90 : 24} ${b.x + (forward ? -28 : 28)},90`}
                  className={"lab-link " + (!forward ? "reversed" : "")}
                  markerEnd={`url(#${marker})`}
                  initial={false}
                  transition={timing}
                />
              );
            })}
          {nodes.map((node, i) => (
            <g key={node.id} transform={`translate(${60 + i * 115},90)`}>
              <rect
                x={-27}
                y={-24}
                width={54}
                height={48}
                rx={9}
                className={
                  step.active.some(
                    (position) => step.entities?.[position]?.id === node.id,
                  )
                    ? "lab-node active"
                    : "lab-node"
                }
              />
              <text textAnchor="middle" dy=".35em" className="lab-node-text">
                {node.value}
              </text>
              <text textAnchor="middle" y={49} className="lab-svg-note">
                {node.id}
              </text>
              {(step.head ?? nodes[0]?.id) === node.id && (
                <text textAnchor="middle" y={-40} className="lab-svg-focus">
                  head
                </text>
              )}
              {!links.find((link) => link.from === node.id)?.to && (
                <text textAnchor="middle" y={76} className="lab-svg-note">
                  next = null
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>
      <Equation>
        {Object.entries(step.variables)
          .filter(([key]) => ["current", "previous", "next"].includes(key))
          .map(
            ([key, value]) =>
              `${key}: ${numeric(value) < 0 ? "null" : `original node ${value}`}`,
          )
          .join(" · ") || "Follow next references from the current head."}
      </Equation>
    </Model>
  );
}

type Placed = {
  id: string;
  value: number;
  x: number;
  y: number;
  parent?: string;
};
function TreeModel({
  step,
  algorithm,
  timing,
}: {
  step: Step;
  algorithm: string;
  timing: Timing;
}) {
  const v = step.visual ?? {},
    placed: Placed[] = [];
  let slot = 0;
  const place = (node: Tree | null, depth: number, parent?: string) => {
    if (!node) return;
    const id = node.id ?? "node-" + node.value;
    place(node.left, depth + 1, id);
    const x = 45 + slot++ * 72;
    placed.push({ id, value: node.value, x, y: 48 + depth * 88, parent });
    place(node.right, depth + 1, id);
  };
  if (algorithm === "heap") {
    step.array.forEach((value, i) => {
      const level = Math.floor(Math.log2(i + 1)),
        first = 2 ** level - 1;
      placed.push({
        id: step.entities?.[i]?.id ?? "heap-" + i,
        value,
        x:
          40 +
          ((i - first + 0.5) *
            (Math.max(
              520,
              2 ** Math.floor(Math.log2(Math.max(1, step.array.length))) * 65,
            ) -
              80)) /
            2 ** level,
        y: 48 + level * 88,
        parent:
          i > 0 ? step.entities?.[Math.floor((i - 1) / 2)]?.id : undefined,
      });
    });
  } else place(step.tree ?? null, 0);
  const marker = useId().replaceAll(":", ""),
    byId = new Map(placed.map((node) => [node.id, node])),
    path = list<string>(v.path),
    visited = list<string>(v.visited),
    frames = list<string>(v.frames),
    width = Math.max(520, ...placed.map((node) => node.x + 48)),
    height = Math.max(220, ...placed.map((node) => node.y + 70));
  const focused = (node: Placed) =>
    algorithm === "heap"
      ? step.active.includes(
          step.entities?.findIndex((e) => e.id === node.id) ?? -1,
        )
      : v.current === node.id ||
        node.value === step.variables.inserted ||
        path.includes(node.id);
  return (
    <Model
      title={
        algorithm === "heap"
          ? "A max-heap is a tree and an array"
          : algorithm === "avl"
            ? "Rebalance without changing key order"
            : algorithm === "bst"
              ? "A comparison chooses the subtree"
              : `${String(v.mode ?? "inorder")} traversal`
      }
      subtitle={String(
        v.scope ??
          (algorithm === "heap"
            ? "Parent(i) = floor((i−1)/2). Siblings do not need to be sorted."
            : "Every node keeps its identity through structural changes."),
      )}
    >
      <div className="lab-svg-scroll">
        <svg
          width={width}
          height={height}
          role="img"
          aria-label={
            algorithm === "heap"
              ? "Max heap parent and child relationships"
              : "Tree structure with current comparisons and visit order"
          }
        >
          <defs>
            <marker
              id={marker}
              markerWidth="6"
              markerHeight="6"
              refX="5"
              refY="3"
              orient="auto"
            >
              <path d="M0,0 L5,3 L0,6" className="lab-arrow-tip" />
            </marker>
          </defs>
          {placed
            .filter((n) => n.parent)
            .map((node) => {
              const parent = byId.get(node.parent!);
              return (
                parent && (
                  <motion.line
                    key={"edge-" + node.id}
                    className={
                      "lab-tree-edge " + (focused(node) ? "active" : "")
                    }
                    initial={false}
                    animate={{
                      x1: parent.x,
                      y1: parent.y + 24,
                      x2: node.x,
                      y2: node.y - 28,
                    }}
                    transition={timing}
                    markerEnd={`url(#${marker})`}
                  />
                )
              );
            })}
          {placed.map((node) => (
            <motion.g
              key={node.id}
              initial={false}
              animate={{ x: node.x, y: node.y }}
              transition={timing}
            >
              <circle
                r={25}
                className={
                  "lab-node " +
                  (focused(node)
                    ? "active"
                    : visited.includes(node.id)
                      ? "resolved"
                      : frames.includes(node.id)
                        ? "pending"
                        : "")
                }
              />
              <text textAnchor="middle" dy=".35em" className="lab-node-text">
                {node.value}
              </text>
              {algorithm === "heap" && (
                <text textAnchor="middle" y={44} className="lab-svg-note">
                  index {step.entities?.findIndex((e) => e.id === node.id)}
                </text>
              )}
            </motion.g>
          ))}
          {!placed.length && (
            <text x={35} y={85} className="lab-svg-note">
              Empty tree · no nodes yet
            </text>
          )}
        </svg>
      </div>
      {algorithm === "heap" && (
        <CellStrip
          items={cells(step)}
          timing={timing}
          label="Heap array indices"
        />
      )}
      {!!path.length && (
        <>
          <Label>Comparison path</Label>
          <Chips
            items={path.map((id) => byId.get(id)?.value ?? id)}
            label="Compared keys"
          />
        </>
      )}
      {Array.isArray(v.output) && (
        <>
          <Label>Emitted values, in order</Label>
          <CellStrip
            items={list<number>(v.output).map((value, i) => ({
              id: "visit-" + i,
              label: value,
              index: i,
              state: "resolved",
            }))}
            timing={timing}
            label="Traversal output"
          />
        </>
      )}
      {!!frames.length && (
        <>
          <Label>
            {v.mode === "levelorder" ? "Pending queue" : "Active frame IDs"}
          </Label>
          <Chips
            items={frames.map((id) => byId.get(id)?.value ?? id)}
            label="Traversal pending nodes"
          />
        </>
      )}
    </Model>
  );
}

function TrieModel({ step, timing }: { step: Step; timing: Timing }) {
  const v = step.visual ?? {},
    words = list<string>(v.trieWords).length
      ? list<string>(v.trieWords)
      : (step.words ?? []),
    terminals = new Set(step.words ?? []),
    prefix = String(v.prefix ?? "");
  type Node = {
    id: string;
    label: string;
    parent?: string;
    children: Node[];
    x: number;
    y: number;
  };
  const root: Node = { id: "", label: "root", children: [], x: 0, y: 40 },
    map = new Map<string, Node>([["", root]]);
  for (const word of words)
    for (let i = 1; i <= word.length; i++) {
      const id = word.slice(0, i);
      if (!map.has(id)) {
        const parent = map.get(id.slice(0, -1))!;
        const node: Node = {
          id,
          label: word[i - 1],
          parent: parent.id,
          children: [],
          x: 0,
          y: 40 + i * 70,
        };
        map.set(id, node);
        parent.children.push(node);
      }
    }
  let leaf = 0;
  const layout = (node: Node) => {
    node.children.sort((a, b) => a.label.localeCompare(b.label));
    node.children.forEach(layout);
    node.x = node.children.length
      ? node.children.reduce((s, n) => s + n.x, 0) / node.children.length
      : 40 + leaf++ * 76;
  };
  layout(root);
  const nodes = [...map.values()],
    width = Math.max(520, leaf * 76 + 50),
    height = Math.max(200, ...nodes.map((n) => n.y + 55));
  return (
    <Model
      title="Share prefixes, mark complete words"
      subtitle="A node is identified by its full prefix. A filled endpoint marks a complete inserted word."
    >
      <div className="lab-svg-scroll">
        <svg
          width={width}
          height={height}
          role="img"
          aria-label="Trie prefix edges and word boundaries"
        >
          {nodes
            .filter((n) => n.parent !== undefined)
            .map((node) => {
              const parent = map.get(node.parent!)!;
              return (
                <motion.line
                  key={"edge-" + node.id}
                  className={
                    "lab-tree-edge " +
                    (prefix.startsWith(node.id) ? "active" : "")
                  }
                  initial={false}
                  animate={{
                    x1: parent.x,
                    y1: parent.y + 22,
                    x2: node.x,
                    y2: node.y - 23,
                  }}
                  transition={timing}
                />
              );
            })}
          {nodes.map((node) => (
            <motion.g
              key={node.id}
              initial={false}
              animate={{ x: node.x, y: node.y }}
              transition={timing}
            >
              <circle
                r={node.id ? 22 : 26}
                className={
                  "lab-node " +
                  (node.id === prefix
                    ? "active"
                    : terminals.has(node.id)
                      ? "resolved"
                      : "")
                }
              />
              {terminals.has(node.id) && (
                <circle r={16} className="lab-terminal-ring" />
              )}
              <text textAnchor="middle" dy=".35em" className="lab-node-text">
                {node.label}
              </text>
            </motion.g>
          ))}
        </svg>
      </div>
      <Equation>
        current prefix: {prefix || "empty"}
        {v.word !== undefined && <> · inserting “{String(v.word)}”</>}
      </Equation>
      <Chips items={step.words ?? []} label="Completed inserted words" />
    </Model>
  );
}
