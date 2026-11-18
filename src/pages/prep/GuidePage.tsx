import { Link, useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, ArrowSquareOut, FilePdf, Lightbulb } from "@phosphor-icons/react";
import { api } from "../../api";
import type { PrepGuide } from "../../types";
import { Loading, ErrorState } from "../../components/Shared";
import ChallengeCard from "../../components/ChallengeCard";
import PuzzleBlock from "./PuzzleBlock";
import { guideSources, type Source } from "./sources";

/** The readable part of a guide: sections, then a cheat sheet of its key points. Shared with the track handbook. */
export function GuideNotes({ guide: g, puzzle = true }: { guide: PrepGuide; puzzle?: boolean }) {
  return (
    <>
      {puzzle && g.puzzle && <PuzzleBlock id={g.id} puzzle={g.puzzle} />}
      {g.sections.map((s) => (
        <section key={s.title}>
          <h2>{s.title}</h2>
          <p className="prose preserve-lines">{s.text}</p>
        </section>
      ))}
      <div className="insight prep-cheatsheet">
        <Lightbulb size={22} aria-hidden="true" />
        <div>
          <h3>Cheat sheet</h3>
          <ul>
            {g.keyPoints.map((k) => (
              <li key={k}>{k}</li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}

export function SourceList({ sources }: { sources: Source[] }) {
  return (
    <ul className="prep-sources">
      {sources.map((s) => (
        <li key={s.url}>
          <a href={s.url} target="_blank" rel="noopener noreferrer">
            <strong>{s.title}</strong>
            <ArrowSquareOut size={14} aria-hidden="true" />
          </a>
          <small>
            {s.by}
            {s.paid ? ", paid" : ""}
          </small>
          <p>{s.note}</p>
        </li>
      ))}
    </ul>
  );
}

const VIEWS = ["notes", "quiz", "sources"] as const;

/** A Prep guide in three parts: notes (printable as a PDF), its quiz graded on the server, and where to read more. */
export default function GuidePage() {
  const { id = "" } = useParams();
  const [params, setParams] = useSearchParams();
  const guide = useQuery({ queryKey: ["prep-guide", id], queryFn: () => api<PrepGuide>("/prep/guides/" + id) });
  if (guide.isLoading) return <Loading />;
  if (guide.error || !guide.data) return <ErrorState error={guide.error} />;
  const g = guide.data;
  const view = VIEWS.find((v) => v === params.get("view")) ?? "notes";
  const sources = guideSources(g.id, g.track, g.subject);
  const show = (v: string) => setParams(v === "notes" ? {} : { view: v }, { replace: true });
  const label = { notes: "Notes", quiz: `Quiz (${g.challenges.length})`, sources: "Sources" };
  return (
    <article className="prep-guide">
      <Link className="back-link" to={"/prep/" + g.track}>
        <ArrowLeft size={16} aria-hidden="true" />
        Back to {g.subject ?? "the track"}
      </Link>
      {g.subject && <span className="prep-subject">{g.subject}</span>}
      <h1 className="display">{g.title}</h1>
      <p className="prose">{g.summary}</p>
      <div className="prep-guide-bar">
        <div className="tabs" role="tablist" aria-label="Guide parts">
          {VIEWS.filter((v) => v !== "quiz" || g.challenges.length).map((v) => (
            <button key={v} role="tab" aria-selected={view === v} className={view === v ? "active" : ""} onClick={() => show(v)}>
              {label[v]}
            </button>
          ))}
        </div>
        <button
          className="button small"
          type="button"
          onClick={() => {
            show("notes");
            window.print(); // the print stylesheet prints the notes whichever part is open
          }}
        >
          <FilePdf size={16} aria-hidden="true" />
          Save as PDF
        </button>
      </div>
      <div className="guide-panel notes" role="tabpanel" hidden={view !== "notes"}>
        <GuideNotes guide={g} />
        <div className="prep-next">
          {g.drill && (
            <Link className="button" to={"/prep/drill/" + g.drill}>
              Practise with unlimited questions
              <ArrowRight size={16} aria-hidden="true" />
            </Link>
          )}
          {!!g.challenges.length && (
            <button className="button primary" type="button" onClick={() => show("quiz")}>
              Check yourself: {g.challenges.length} questions
              <ArrowRight size={16} aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
      {view === "quiz" && (
        <section className="prep-quiz guide-panel" role="tabpanel">
          <h2>Check yourself</h2>
          {g.challenges.map((c) => (
            <ChallengeCard key={c.id} challenge={c} />
          ))}
        </section>
      )}
      {view === "sources" && (
        <section className="guide-panel" role="tabpanel">
          <h2>Read more</h2>
          <p className="muted">Free references unless marked paid. They open on their own sites.</p>
          <SourceList sources={sources} />
        </section>
      )}
    </article>
  );
}
