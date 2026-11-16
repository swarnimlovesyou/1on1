import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Cards, FilePdf, MagnifyingGlass, PencilSimple, Trash, UploadSimple } from "@phosphor-icons/react";
import { api, upload } from "../../api";
import { useApp } from "../../context";
import type { NotebookAnswer, NotebookSource, RevisionCard } from "../../types";
import { ErrorState, Loading } from "../../components/Shared";

const kb = (n: number) => (n < 1024 * 1024 ? Math.round(n / 1024) + " KB" : (n / 1024 / 1024).toFixed(1) + " MB");

/** The learner's own PDFs: add, choose which to search, ask with page citations, draft cards. */
export function Sources() {
  const { notify } = useApp(),
    client = useQueryClient(),
    file = useRef<HTMLInputElement>(null),
    [selected, setSelected] = useState<string[]>([]),
    [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState<NotebookAnswer>();
  const sources = useQuery({ queryKey: ["notebook-sources"], queryFn: () => api<NotebookSource[]>("/notebook/sources") });
  const refresh = () => client.invalidateQueries({ queryKey: ["notebook-sources"] });
  const add = useMutation({
    mutationFn: (f: File) => upload<NotebookSource>("/notebook/sources", f),
    onSuccess: (s) => {
      refresh();
      notify(`${s.title} added: ${s.pages} page${s.pages === 1 ? "" : "s"}`);
    },
  });
  const remove = useMutation({
    mutationFn: (s: NotebookSource) => api(`/notebook/sources/${s.id}`, undefined, "DELETE"),
    onSuccess: () => {
      refresh();
      client.invalidateQueries({ queryKey: ["notebook-cards"] });
      notify("Source removed; cards made from it are kept");
    },
  });
  const ask = useMutation({
    mutationFn: () => api<NotebookAnswer>("/notebook/ask", { question, sourceIds: selected }),
    onSuccess: setAnswer,
  });
  const draft = useMutation({
    mutationFn: (s: NotebookSource) => api<RevisionCard[]>("/notebook/cards/draft", { sourceId: s.id }),
    onSuccess: (cards) => {
      client.invalidateQueries({ queryKey: ["notebook-cards"] });
      notify(cards.length ? `${cards.length} cards drafted: edit them under Revision cards` : "No definitions found to draft from on these pages");
    },
  });
  if (sources.isLoading) return <Loading />;
  if (sources.error) return <ErrorState error={sources.error} retry={() => sources.refetch()} />;
  const list = sources.data ?? [];
  return (
    <div className="doc-notebook">
      <section className="doc-sources">
        <div className="section-heading">
          <h2>Your sources</h2>
          <button className="button small" disabled={add.isPending} onClick={() => file.current?.click()}>
            <UploadSimple size={16} /> {add.isPending ? "Reading…" : "Add a PDF"}
          </button>
          <input
            ref={file}
            type="file"
            accept="application/pdf,.pdf"
            hidden
            onChange={(e) => {
              const f = e.target.files?.[0];
              e.target.value = "";
              if (f) add.mutate(f);
            }}
          />
        </div>
        <p className="form-note">
          Text PDFs up to 10 MB and 100 pages; slides can be exported to PDF. Scans and password-protected files can't be read.
          Only the text of each page is kept, and only you can search it.
        </p>
        {add.error && <ErrorState error={add.error} />}
        {list.map((s) => (
          <div key={s.id} className="doc-source">
            <input
              type="checkbox"
              checked={selected.includes(s.id)}
              aria-label={"Search only selected sources: " + s.title}
              onChange={() => setSelected((v) => (v.includes(s.id) ? v.filter((x) => x !== s.id) : [...v, s.id]))}
            />
            <FilePdf size={20} />
            <span>
              <strong>{s.title}</strong>
              <small>
                {s.pages} page{s.pages === 1 ? "" : "s"} · {kb(s.bytes)}
              </small>
            </span>
            <button className="text-link" disabled={draft.isPending} onClick={() => draft.mutate(s)}>
              <Cards size={15} /> Make cards
            </button>
            <button
              className="icon-btn"
              aria-label={"Remove " + s.title}
              disabled={remove.isPending}
              onClick={() => window.confirm(`Remove ${s.title}? Its text is deleted; cards made from it stay.`) && remove.mutate(s)}
            >
              <Trash size={16} />
            </button>
          </div>
        ))}
        {!list.length && <p className="empty-line">No sources yet. Add your lecture notes or a chapter as a PDF.</p>}
        {draft.error && <ErrorState error={draft.error} />}
      </section>

      <section className="doc-ask">
        <h2>Ask your sources</h2>
        <form
          className="doc-ask-form"
          onSubmit={(e) => {
            e.preventDefault();
            if (question.trim()) ask.mutate();
          }}
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does my lecture say about…"
            aria-label="Question for your sources"
            disabled={!list.length}
          />
          <button className="button primary small" disabled={!question.trim() || ask.isPending || !list.length}>
            <MagnifyingGlass size={16} /> {ask.isPending ? "Searching…" : "Ask"}
          </button>
        </form>
        <p className="form-note">
          {selected.length ? `Searching ${selected.length} selected source${selected.length === 1 ? "" : "s"}.` : "Searching all your sources."} Answers
          cite the file and page; if your sources don't cover it, you'll be told.
        </p>
        {ask.error && <ErrorState error={ask.error} />}
        {answer && (
          <div className={"doc-answer" + (answer.answered === false ? " silent" : "")}>
            <p>{answer.text}</p>
            {(answer.citations.length ? answer.citations : answer.passages).map((p, i) => (
              <blockquote key={p.sourceId + p.page + i}>
                <cite>
                  {p.n ? `[${p.n}] ` : ""}
                  {p.title}, page {p.page}
                </cite>
                <span>{p.text.length > 420 ? p.text.slice(0, 420) + "…" : p.text}</span>
              </blockquote>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

const RATINGS = ["again", "hard", "good", "easy"] as const;

/** Editable revision cards; the self-rating is the learner's own and never counts as graded progress. */
export function RevisionCards() {
  const client = useQueryClient(),
    cards = useQuery({ queryKey: ["notebook-cards"], queryFn: () => api<RevisionCard[]>("/notebook/cards") });
  if (cards.isLoading) return <Loading />;
  if (cards.error) return <ErrorState error={cards.error} retry={() => cards.refetch()} />;
  const list = cards.data ?? [];
  return (
    <div className="revision-cards">
      <p className="form-note">
        Drafted from your sources, then yours to edit. How well you remembered is your own rating; it isn't counted as graded progress.
      </p>
      {list.map((c) => (
        <CardItem key={c.id} card={c} onChange={() => client.invalidateQueries({ queryKey: ["notebook-cards"] })} />
      ))}
      {!list.length && <p className="empty-line">No cards yet. Use “Make cards” on one of your sources.</p>}
    </div>
  );
}

function CardItem({ card, onChange }: { card: RevisionCard; onChange: () => void }) {
  const [editing, setEditing] = useState(false),
    [front, setFront] = useState(card.front),
    [back, setBack] = useState(card.back),
    [shown, setShown] = useState(false);
  const save = useMutation({
    mutationFn: () => api(`/notebook/cards/${card.id}`, { front, back }, "PUT"),
    onSuccess: () => {
      setEditing(false);
      onChange();
    },
  });
  const rate = useMutation({ mutationFn: (rating: string) => api(`/notebook/cards/${card.id}/recall`, { rating }), onSuccess: onChange });
  const remove = useMutation({ mutationFn: () => api(`/notebook/cards/${card.id}`, undefined, "DELETE"), onSuccess: onChange });
  return (
    <article className="revision-card">
      <div className="note-meta">
        <span>
          {card.sourceTitle ? `${card.sourceTitle}, page ${card.page}` : "Source removed"} · {card.draftedBy === "model" ? "drafted by AI" : "taken from the text"}
        </span>
        <span>
          <button className="icon-btn" aria-label="Edit card" onClick={() => setEditing(!editing)}>
            <PencilSimple size={16} />
          </button>
          <button className="icon-btn" aria-label="Delete card" disabled={remove.isPending} onClick={() => remove.mutate()}>
            <Trash size={16} />
          </button>
        </span>
      </div>
      {editing ? (
        <form
          className="card-edit"
          onSubmit={(e) => {
            e.preventDefault();
            save.mutate();
          }}
        >
          <label>
            Front
            <textarea rows={2} value={front} onChange={(e) => setFront(e.target.value)} />
          </label>
          <label>
            Back
            <textarea rows={3} value={back} onChange={(e) => setBack(e.target.value)} />
          </label>
          <button className="button primary small" disabled={!front.trim() || !back.trim() || save.isPending}>
            Save card
          </button>
          {save.error && <ErrorState error={save.error} />}
        </form>
      ) : (
        <>
          <h2>{card.front}</h2>
          {shown ? (
            <>
              <p>{card.back}</p>
              <div className="recall" role="group" aria-label="How well did you remember?">
                {RATINGS.map((r) => (
                  <button key={r} className={card.recall === r ? "active" : ""} disabled={rate.isPending} onClick={() => rate.mutate(r)}>
                    {r[0].toUpperCase() + r.slice(1)}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <button className="text-link" onClick={() => setShown(true)}>
              Show the answer
            </button>
          )}
        </>
      )}
    </article>
  );
}
