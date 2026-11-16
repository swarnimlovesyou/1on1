import { motion } from "motion/react";
import type { Step } from "../../types";
import {
  CellStrip,
  Model,
  Equation,
  Label,
  Chips,
  cells,
  list,
  object,
  numeric,
  type Timing,
  type Cell,
} from "./LabPrimitives";

export default function FoundationModel({
  step,
  algorithm,
  timing,
}: {
  step: Step;
  algorithm: string;
  timing: Timing;
}) {
  const v = step.visual ?? {},
    f = object(v.focus),
    vars = step.variables;
  if (algorithm === "complexity") {
    const n = numeric(v.n, 0),
      counts = list<number>(v.counts),
      max = Math.max(1, n * n);
    return (
      <Model
        title="Count the work"
        subtitle="Defined loop-body visits · not elapsed time"
        legend="Compare the same input size. The highlighted grid row contributes n pair visits."
      >
        <div className="lab-growth">
          {["Linear scan", "Ordered pairs", "Repeated halving"].map(
            (name, i) => (
              <div className="lab-growth-row" key={name}>
                <span>{name}</span>
                <div>
                  <motion.div
                    initial={false}
                    animate={{ scaleX: (counts[i] ?? 0) / max }}
                    transition={timing}
                  />
                </div>
                <strong>{counts[i] ?? 0}</strong>
              </div>
            ),
          )}
        </div>
        <div
          className="lab-pair-grid"
          style={{ gridTemplateColumns: `repeat(${Math.max(n, 1)},14px)` }}
          aria-label={`${n} by ${n} ordered pairs`}
        >
          {Array.from({ length: n * n }, (_, i) => (
            <span
              key={i}
              className={Math.floor(i / n) <= numeric(v.row) ? "counted" : ""}
            />
          ))}
        </div>
        <Equation>
          n = {n}
          {v.halvingValue !== undefined && (
            <> · current halving value = {String(v.halvingValue)}</>
          )}
        </Equation>
      </Model>
    );
  }
  if (algorithm === "strings" || algorithm === "variable-window") {
    const chars = list<string>(v.characters),
      left = numeric(v.left),
      right = numeric(v.right),
      cursor = numeric(v.cursor);
    const items: Cell[] = chars.map((char, i) => ({
      id: "character-" + i,
      label: char === " " ? "␣" : char,
      index: i,
      state:
        algorithm === "variable-window"
          ? i >= left && i <= right
            ? "active"
            : i < left
              ? "discarded"
              : ""
          : i === cursor
            ? "active"
            : "",
      pointers:
        algorithm === "variable-window"
          ? [...(i === left ? ["L"] : []), ...(i === right ? ["R"] : [])]
          : i === cursor
            ? ["read"]
            : [],
    }));
    return (
      <Model
        title={
          algorithm === "strings"
            ? "Immutable source, growing output"
            : "A frame that restores its invariant"
        }
        subtitle={
          algorithm === "strings"
            ? "Copy characters into a separate buffer."
            : "Shrink until the incoming character is unique."
        }
      >
        <CellStrip
          items={items}
          timing={timing}
          label="Source character positions"
          window={algorithm === "variable-window" ? [left, right] : undefined}
        />
        {algorithm === "strings" ? (
          <>
            <Label>Output buffer</Label>
            <CellStrip
              items={list<string>(v.output).map((char, i) => ({
                id: "output-" + (chars.length - 1 - i),
                label: char === " " ? "␣" : char,
                index: i,
                state: i === list(v.output).length - 1 ? "active" : "resolved",
              }))}
              timing={timing}
              label="Reversed output buffer"
            />
          </>
        ) : (
          <>
            <Label>
              {v.phase === "shrink"
                ? "Membership before adding the incoming character"
                : "Unique members of the restored frame"}
            </Label>
            <Chips items={list(v.members)} label="Window membership" />
            <Equation>
              Best length: {numeric(v.best, 0)}
              {v.incoming !== undefined && (
                <> · incoming “{String(v.incoming)}”</>
              )}
            </Equation>
          </>
        )}
      </Model>
    );
  }
  if (algorithm === "hashing") {
    const entries = list<{
      id: string;
      key: number;
      count: number;
      bucket: number;
    }>(v.entries);
    return (
      <Model
        title="Membership and counts"
        subtitle="Illustrative hash(key) = floorMod(key, 4); exact key equality resolves collisions."
        legend="These four buckets illustrate hashing. They do not represent Java HashMap's actual memory layout."
      >
        <CellStrip items={cells(step)} timing={timing} label="Input keys" />
        <div className="lab-buckets">
          {Array.from({ length: 4 }, (_, bucket) => (
            <div
              key={bucket}
              className={
                "lab-bucket " + (numeric(v.bucket) === bucket ? "active" : "")
              }
            >
              <Label>Bucket {bucket}</Label>
              <AnimateEntries
                entries={entries.filter((e) => e.bucket === bucket)}
                activeKey={numeric(v.key)}
                timing={timing}
              />
              {!entries.some((e) => e.bucket === bucket) && (
                <span className="lab-empty">empty</span>
              )}
            </div>
          ))}
        </div>
        {v.key !== undefined && (
          <Equation>
            key {String(v.key)} · {String(v.phase)}
          </Equation>
        )}
      </Model>
    );
  }
  if (algorithm === "matrices") {
    const rows = numeric(v.rows, 0),
      cols = numeric(v.cols, 0),
      output = list<number | null>(v.output);
    return (
      <Model
        title="Transpose by coordinate"
        subtitle="One source cell becomes one destination cell; rows and columns exchange roles."
      >
        <div className="lab-matrix-pair">
          <Matrix
            values={step.array}
            columns={cols}
            active={numeric(v.source)}
            label={`Input ${rows} × ${cols}`}
            timing={timing}
          />
          <span className="lab-transfer">(r,c) → (c,r)</span>
          <Matrix
            values={output}
            columns={rows}
            active={numeric(v.destination)}
            label={`Output ${cols} × ${rows}`}
            timing={timing}
          />
        </div>
      </Model>
    );
  }
  if (algorithm === "intervals") {
    const source = list<{ id: string; start: number; end: number }>(
        v.intervals,
      ),
      output = list<{ id: string; start: number; end: number }>(v.output),
      min = Math.min(0, ...source.map((x) => x.start)),
      max = Math.max(1, ...source.map((x) => x.end)),
      span = Math.max(1, max - min);
    const rows = (items: typeof source, label: string) => (
      <div className="lab-interval-scroll">
        <div className="lab-interval-rows" role="group" aria-label={label}>
          {items.map((item) => (
            <motion.div
              layout="position"
              className="lab-interval-row"
              key={item.id}
              transition={timing}
            >
              <span>{item.id.replace("interval-", "I")}</span>
              <motion.div
                className={
                  "lab-interval " + (v.current === item.id ? "active" : "")
                }
                initial={false}
                animate={{
                  x: ((item.start - min) / span) * 460,
                  width: Math.max(7, ((item.end - item.start) / span) * 460),
                }}
                transition={timing}
              >
                <small>{item.start}</small>
                <small>{item.end}</small>
              </motion.div>
            </motion.div>
          ))}
          {!items.length && <p className="lab-empty">No intervals yet</p>}
        </div>
      </div>
    );
    return (
      <Model
        title="Merge closed intervals"
        subtitle="Shared horizontal scale · touching endpoints overlap."
      >
        <Label>Input, ordered by start</Label>
        {rows(source, "Input closed intervals")}
        <Label>Merged coverage</Label>
        {rows(output, "Merged closed intervals")}
      </Model>
    );
  }
  const focus = Object.keys(f).length ? f : vars,
    low = numeric(focus.low, 0),
    high = numeric(focus.high, step.array.length - 1),
    left = numeric(vars.left),
    right = numeric(vars.right);
  let items = cells(step).map((cell, i) => ({
    ...cell,
    pointers: [
      ...(i === numeric(focus.left) ? ["L"] : []),
      ...(i === numeric(focus.right) ? ["R"] : []),
      ...(i === numeric(focus.mid) ? ["mid"] : []),
      ...(i === numeric(focus.boundary) ? ["boundary"] : []),
      ...(i === numeric(focus["pivot index"] ?? focus.pivotIndex)
        ? ["pivot"]
        : []),
    ],
  }));
  if (algorithm === "binary-search")
    items = items.map((cell, i) => ({
      ...cell,
      state:
        i < low || i > high
          ? "discarded"
          : i === numeric(focus.mid)
            ? "active"
            : "candidate",
      pointers: [
        ...(i === low ? ["low"] : []),
        ...(i === high ? ["high"] : []),
        ...(i === numeric(focus.mid) ? ["mid"] : []),
      ],
    }));
  if (algorithm === "arrays")
    items = items.map((cell, i) => ({
      ...cell,
      state:
        i === numeric(v.consumed)
          ? "active"
          : i < numeric(v.consumed)
            ? "resolved"
            : cell.state,
    }));
  if (algorithm === "prefix-sums" && v.rightExclusive !== undefined)
    items = items.map((cell, i) => ({
      ...cell,
      state:
        i >= numeric(v.left) && i < numeric(v.rightExclusive) ? "active" : "",
      pointers: [],
    }));
  const isSort = ["merge-sort", "quick-sort", "quickselect"].includes(
    algorithm,
  );
  return (
    <Model
      title={
        algorithm === "prefix-sums"
          ? "Sums live at boundaries"
          : algorithm === "sliding-window"
            ? "Keep the frame and the sum together"
            : algorithm === "two-pointers"
              ? "Two positions, one justified move"
              : algorithm === "binary-search"
                ? "Discard only the impossible interval"
                : isSort
                  ? "Order values through real operations"
                  : "Read a slot, update the result"
      }
      subtitle={
        algorithm === "binary-search"
          ? "Dimmed positions have been ruled out; midpoint and bounds have separate roles."
          : isSort
            ? "Elements retain identity when equal values move."
            : undefined
      }
    >
      {isSort && (
        <div className="lab-bars-scroll">
          <div className="lab-bars">
            {step.entities?.map((entity, i) => (
              <motion.div
                layout="position"
                key={entity.id}
                className={
                  "lab-bar-slot " + (step.active.includes(i) ? "active" : "")
                }
                transition={timing}
              >
                <motion.div
                  className={entity.value < 0 ? "negative" : ""}
                  initial={false}
                  animate={{
                    height: Math.max(
                      8,
                      (Math.abs(entity.value) /
                        Math.max(1, ...step.array.map(Math.abs))) *
                        95,
                    ),
                  }}
                  transition={timing}
                />
                <span>{entity.value}</span>
                <small>{i}</small>
              </motion.div>
            ))}
          </div>
        </div>
      )}
      <CellStrip
        items={items}
        timing={timing}
        label="Algorithm values and pointer positions"
        window={algorithm === "sliding-window" ? [left, right] : undefined}
      />
      {algorithm === "prefix-sums" && (
        <>
          <Label>Prefix boundary table · prefix[0] = 0</Label>
          <CellStrip
            items={Array.from({ length: step.array.length + 1 }, (_, i) => ({
              id: "prefix-" + i,
              label: list<number>(v.prefix)[i] ?? "?",
              index: i,
              state:
                i === numeric(v.left) || i === numeric(v.rightExclusive)
                  ? "active"
                  : i < list(v.prefix).length
                    ? "resolved"
                    : "",
            }))}
            timing={timing}
            label="Exclusive prefix boundaries"
          />
        </>
      )}
      {algorithm === "merge-sort" && (
        <>
          <Label>
            {v.phase === "split" ? "Divide interval" : "Merge buffer"}{" "}
            {list(v.range).join("..")}
          </Label>
          <CellStrip
            items={list<number>(v.buffer).map((value, i) => ({
              id: "buffer-" + i,
              label: value,
              index: i,
              state: "resolved",
            }))}
            timing={timing}
            label="Merge output buffer"
          />
        </>
      )}
      {(v.equation !== undefined ||
        vars.sum !== undefined ||
        vars.total !== undefined) && (
        <Equation>
          {String(
            v.equation ??
              (vars.sum !== undefined
                ? `sum = ${vars.sum}`
                : `total = ${vars.total}`),
          )}
          {vars.best !== undefined && <> · best = {String(vars.best)}</>}
        </Equation>
      )}
    </Model>
  );
}

function AnimateEntries({
  entries,
  activeKey,
  timing,
}: {
  entries: { id: string; key: number; count: number }[];
  activeKey: number;
  timing: Timing;
}) {
  return (
    <>
      {entries.map((e) => (
        <motion.div
          layout="position"
          className={"lab-hash-entry " + (activeKey === e.key ? "active" : "")}
          key={e.id}
          transition={timing}
        >
          <strong>{e.key}</strong>
          <span>count {e.count}</span>
        </motion.div>
      ))}
    </>
  );
}
function Matrix({
  values,
  columns,
  active,
  label,
  timing,
}: {
  values: (number | null)[];
  columns: number;
  active: number;
  label: string;
  timing: Timing;
}) {
  return (
    <div className="lab-matrix-wrap">
      <Label>{label}</Label>
      <div className="lab-matrix-scroll">
        <div
          className="lab-matrix"
          style={{
            gridTemplateColumns: `repeat(${Math.max(1, columns)},52px)`,
          }}
          role="group"
          aria-label={label}
        >
          {values.map((value, i) => (
            <motion.div
              className={"lab-matrix-cell " + (active === i ? "active" : "")}
              key={i}
              initial={false}
              animate={{
                backgroundColor:
                  active === i ? "var(--accent-wash)" : "var(--surface)",
              }}
              transition={timing}
            >
              <strong>{value ?? "·"}</strong>
              <small>
                {Math.floor(i / columns)},{i % columns}
              </small>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
