import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, type ReactNode } from "react";
import type { Step } from "../../types";

export type Timing = {
  duration: number;
  ease: readonly [number, number, number, number];
};
export type Cell = {
  id: string;
  label: string | number;
  index?: string | number;
  state?: string;
  pointers?: string[];
};
export const list = <T,>(value: unknown): T[] =>
  Array.isArray(value) ? (value as T[]) : [];
export const object = (value: unknown): Record<string, unknown> =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
export const numeric = (value: unknown, fallback = -1) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;
export function cells(step: Step): Cell[] {
  return (
    step.entities ?? step.array.map((value, i) => ({ id: "cell-" + i, value }))
  ).map((e, i) => ({
    id: e.id,
    label: e.value,
    index: i,
    state: step.active.includes(i) ? "active" : "",
  }));
}

export function Model({
  title,
  subtitle,
  children,
  legend,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  legend?: ReactNode;
}) {
  return (
    <div className="lab-model">
      <div className="lab-model-heading">
        <h3>{title}</h3>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {children}
      {legend && <div className="lab-legend">{legend}</div>}
    </div>
  );
}
export function CellStrip({
  items,
  timing,
  label,
  window,
}: {
  items: Cell[];
  timing: Timing;
  label: string;
  window?: [number, number];
}) {
  const scroll = useRef<HTMLDivElement>(null);
  const focus = items.findIndex((c) =>
    c.pointers?.some((p) => ["mid", "R", "read"].includes(p)),
  );
  const active =
    focus >= 0
      ? focus
      : items.findIndex(
          (c) => c.state === "active" || c.state === "destination",
        );
  useEffect(() => {
    const element = scroll.current;
    if (element && active >= 0)
      element.scrollTo({
        left: Math.max(0, active * 64 - element.clientWidth / 2 + 32),
        behavior: "auto",
      });
  }, [active]);
  return (
    <div
      ref={scroll}
      className="lab-strip-scroll"
      role="group"
      aria-label={label}
    >
      <div
        className="lab-strip"
        style={{ minWidth: Math.max(items.length * 64, 150) }}
      >
        {window && window[0] >= 0 && window[1] >= window[0] && (
          <motion.div
            className="lab-window-frame"
            initial={false}
            animate={{
              x: window[0] * 64,
              width: (window[1] - window[0] + 1) * 64 - 6,
            }}
            transition={timing}
          >
            <span>window</span>
          </motion.div>
        )}
        <AnimatePresence initial={false}>
          {items.map((cell) => (
            <motion.div
              layout="position"
              key={cell.id}
              className={"lab-cell " + (cell.state ?? "")}
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.85 }}
              transition={timing}
            >
              <div className="lab-pointers">
                {cell.pointers?.map((p) => (
                  <span key={p}>{p}</span>
                ))}
              </div>
              <strong>{cell.label}</strong>
              {cell.index !== undefined && <small>{cell.index}</small>}
            </motion.div>
          ))}
        </AnimatePresence>
        {!items.length && (
          <p className="lab-empty">Empty · no values to process</p>
        )}
      </div>
    </div>
  );
}
export function Equation({ children }: { children: ReactNode }) {
  return <div className="lab-equation">{children}</div>;
}
export function Label({ children }: { children: ReactNode }) {
  return <p className="lab-row-label">{children}</p>;
}
export function Chips({ items, label }: { items: unknown[]; label: string }) {
  return (
    <div className="lab-chips" aria-label={label}>
      {items.length ? (
        items.map((item, i) => (
          <span key={String(item) + "-" + i}>{String(item)}</span>
        ))
      ) : (
        <span className="lab-empty">empty</span>
      )}
    </div>
  );
}
