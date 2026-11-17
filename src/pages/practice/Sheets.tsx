import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowSquareOut, BookOpen, Code } from "@phosphor-icons/react";
import { api } from "../../api";
import { useApp } from "../../context";
import { Loading, ErrorState } from "../../components/Shared";
import { lessonForPattern, toggle } from "./sheetTicks";

type SheetSummary = { id: string; title: string; summary: string; credit: string; count: number };
type Item = { id: string; title: string; difficulty: string; pattern: string; url: string };
type Sheet = SheetSummary & { items: Item[] };

const LOCAL = "1on1-sheet-ticks";

function readLocal(): string[] {
  try {
    return JSON.parse(localStorage.getItem(LOCAL) ?? "[]");
  } catch {
    return [];
  }
}

/** Ticks live on the account when signed in, and in this browser for guests. */
function useTicks() {
  const { user } = useApp();
  const client = useQueryClient();
  const [local, setLocal] = useState<string[]>(readLocal);
  const server = useQuery({
    queryKey: ["sheet-ticks"],
    queryFn: () => api<{ done: string[] }>("/sheets/ticks/mine"),
    enabled: !!user,
  });
  const save = useMutation({
    mutationFn: ({ id, done }: { id: string; done: boolean }) => api<{ done: string[] }>(`/sheets/ticks/mine/${id}`, { done }, "PUT"),
    onSuccess: (data) => client.setQueryData(["sheet-ticks"], data),
  });
  const done = user ? server.data?.done ?? [] : local;
  function set(id: string, on: boolean) {
    if (user) return save.mutate({ id, done: on });
    const next = toggle(local, id, on);
    setLocal(next);
    try {
      localStorage.setItem(LOCAL, JSON.stringify(next));
    } catch {
      // private mode: ticks last for this visit only
    }
  }
  return { done: new Set(done), set, error: save.error };
}

export default function Sheets() {
  const [params, setParams] = useSearchParams();
  const id = params.get("sheet");
  const list = useQuery({ queryKey: ["sheets"], queryFn: () => api<SheetSummary[]>("/sheets") });
  const ticks = useTicks();
  if (id) return <SheetView id={id} ticks={ticks} back={() => setParams({ tab: "sheets" })} />;
  if (list.isLoading) return <Loading />;
  if (list.error || !list.data) return <ErrorState error={list.error} retry={() => list.refetch()} />;
  return (
    <section className="sheets">
      <div className="sheet-cards">
        {list.data.map((s) => (
          <article key={s.id} className="sheet-card">
            <h2>
              <Link to={`/practice?tab=sheets&sheet=${s.id}`}>{s.title}</Link>
            </h2>
            <p>{s.summary}</p>
            <p className="sheet-count">
              <strong>{s.count}</strong> questions
            </p>
            <small className="muted">{s.credit}</small>
          </article>
        ))}
      </div>
      <p className="muted sheet-note">
        Striver&apos;s SDE and A2Z sheets are not copied here because their terms do not allow it. Open them on{" "}
        <a href="https://takeuforward.org/" target="_blank" rel="noreferrer">
          takeuforward.org
        </a>{" "}
        and use the question bank&apos;s &ldquo;Solve here&rdquo; for any LeetCode question on them.
      </p>
    </section>
  );
}

function SheetView({ id, ticks, back }: { id: string; ticks: ReturnType<typeof useTicks>; back: () => void }) {
  const sheet = useQuery({ queryKey: ["sheet", id], queryFn: () => api<Sheet>(`/sheets/${id}`) });
  if (sheet.isLoading) return <Loading />;
  if (sheet.error || !sheet.data) return <ErrorState error={sheet.error} retry={() => sheet.refetch()} />;
  const s = sheet.data;
  const patterns = [...new Set(s.items.map((i) => i.pattern))];
  const done = s.items.filter((i) => ticks.done.has(i.id)).length;
  return (
    <section className="sheets">
      <button className="back-link" type="button" onClick={back}>
        <ArrowLeft size={16} aria-hidden="true" />
        All sheets
      </button>
      <h2 className="display">{s.title}</h2>
      <p className="sheet-progress" role="status">
        {done} of {s.items.length} done
        <progress max={s.items.length} value={done} aria-hidden="true" />
      </p>
      {ticks.error && (
        <p className="inline-alert" role="alert">
          {ticks.error.message}
        </p>
      )}
      {patterns.map((pattern) => {
        const lesson = lessonForPattern(pattern);
        return (
          <section key={pattern} className="sheet-group">
            <h3 className="family-heading">{pattern}</h3>
            <ul className="sheet-list">
              {s.items
                .filter((i) => i.pattern === pattern)
                .map((item) => (
                  <li key={item.id} className="sheet-row">
                    <input
                      type="checkbox"
                      aria-label={`Mark ${item.title} done`}
                      checked={ticks.done.has(item.id)}
                      onChange={(e) => ticks.set(item.id, e.target.checked)}
                    />
                    <a className="sheet-title" href={item.url} target="_blank" rel="noreferrer">
                      {item.title}
                      <ArrowSquareOut size={14} aria-hidden="true" />
                      <span className="sr-only"> on LeetCode</span>
                    </a>
                    <span className={"difficulty " + item.difficulty.toLowerCase()}>{item.difficulty}</span>
                    <Link className="sheet-action" to={`/practice/q/${item.id}`}>
                      <Code size={15} aria-hidden="true" /> Solve here
                    </Link>
                    {lesson && (
                      <Link className="sheet-action" to={`/learn/${lesson}`}>
                        <BookOpen size={15} aria-hidden="true" /> Learn
                      </Link>
                    )}
                  </li>
                ))}
            </ul>
          </section>
        );
      })}
      <small className="muted">{s.credit}</small>
    </section>
  );
}
