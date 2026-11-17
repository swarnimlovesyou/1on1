import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MagnifyingGlass } from "@phosphor-icons/react";
import { useLessons } from "../pages/Learning";
import { usePrep } from "../pages/prep/usePrep";

type Entry = { title: string; group: string; to: string };

const PAGES: Entry[] = [
  { title: "Home", group: "Page", to: "/home" },
  { title: "Explore concepts", group: "Page", to: "/learn" },
  { title: "Animations", group: "Page", to: "/learn/animations" },
  { title: "Performance lab", group: "Page", to: "/learn/lab" },
  { title: "Practice problems", group: "Page", to: "/practice" },
  { title: "Question bank", group: "Page", to: "/practice?tab=bank" },
  { title: "Companies", group: "Page", to: "/practice?tab=companies" },
  { title: "Mock assessment", group: "Page", to: "/practice?tab=mock" },
  { title: "Blind 75", group: "Sheet", to: "/practice?tab=sheets&sheet=blind-75" },
  { title: "NeetCode 150", group: "Sheet", to: "/practice?tab=sheets&sheet=neetcode-150" },
  { title: "Contests", group: "Page", to: "/contests" },
  { title: "Prep", group: "Page", to: "/prep" },
  { title: "Traffic playground", group: "Prep", to: "/prep/system-design/playground" },
  { title: "My practice plan", group: "Page", to: "/plan" },
  { title: "My notebook", group: "Page", to: "/notebook" },
  { title: "Progress", group: "Page", to: "/progress" },
  { title: "Study together", group: "Page", to: "/cohorts" },
  { title: "Settings", group: "Page", to: "/settings" },
];

/** Exact title first, then titles that start with the query, then any match; shorter titles win ties. */
export function rank(entries: Entry[], query: string, limit = 12) {
  const q = query.trim().toLowerCase();
  if (!q) return entries.slice(0, limit);
  const score = (e: Entry) => {
    const t = e.title.toLowerCase();
    return t === q ? 0 : t.startsWith(q) ? 1 : t.includes(q) ? 2 : e.group.toLowerCase().includes(q) ? 3 : 9;
  };
  return entries
    .map((e, i) => ({ e, i, s: score(e) }))
    .filter((x) => x.s < 9)
    .sort((a, b) => a.s - b.s || a.e.title.length - b.e.title.length || a.i - b.i)
    .slice(0, limit)
    .map((x) => x.e);
}

/** Ctrl/⌘ + K: jump to any page, lesson, Prep track or guide, or sheet by keyboard. */
export default function CommandPalette({ open, setOpen }: { open: boolean; setOpen: (v: boolean) => void }) {
  const navigate = useNavigate();
  const lessons = useLessons();
  const prep = usePrep();
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(!open);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
      requestAnimationFrame(() => input.current?.focus());
    }
  }, [open]);

  const entries = useMemo<Entry[]>(
    () => [
      ...PAGES,
      ...(prep.data?.tracks ?? []).map((t) => ({ title: t.title, group: "Prep track", to: "/prep/" + t.id })),
      ...(lessons.data ?? []).map((l) => ({ title: l.title, group: "Lesson", to: "/learn/" + l.id })),
      ...(prep.data?.guides ?? []).map((g) => ({ title: g.title, group: "Prep guide", to: "/prep/guide/" + g.id })),
    ],
    [lessons.data, prep.data],
  );
  const results = rank(entries, query);

  if (!open) return null;
  function go(entry: Entry | undefined) {
    if (!entry) return;
    setOpen(false);
    navigate(entry.to);
  }
  return (
    <div className="palette-backdrop" onMouseDown={() => setOpen(false)}>
      <div
        className="palette"
        role="dialog"
        aria-modal="true"
        aria-label="Jump to"
        onMouseDown={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === "Escape") setOpen(false);
          else if (e.key === "ArrowDown") {
            e.preventDefault();
            setActive((a) => Math.min(a + 1, results.length - 1));
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setActive((a) => Math.max(a - 1, 0));
          } else if (e.key === "Enter") {
            e.preventDefault();
            go(results[active]);
          }
        }}
      >
        <label className="palette-search">
          <MagnifyingGlass size={18} aria-hidden="true" />
          <input
            ref={input}
            value={query}
            placeholder="Jump to a page, lesson, guide or sheet"
            aria-label="Search pages, lessons, guides and sheets"
            aria-controls="palette-results"
            aria-activedescendant={results[active] ? `palette-${active}` : undefined}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
          />
          <kbd>Esc</kbd>
        </label>
        <ul id="palette-results" role="listbox" aria-label="Results">
          {results.map((r, i) => (
            <li
              key={r.to + r.title}
              id={`palette-${i}`}
              role="option"
              aria-selected={i === active}
              className={i === active ? "active" : ""}
              onMouseEnter={() => setActive(i)}
              onClick={() => go(r)}
            >
              <span>{r.title}</span>
              <small>{r.group}</small>
            </li>
          ))}
          {!results.length && <li className="palette-empty">Nothing matches that yet.</li>}
        </ul>
      </div>
    </div>
  );
}
