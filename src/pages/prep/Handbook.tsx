import { Link, useParams } from "react-router-dom";
import { useQueries } from "@tanstack/react-query";
import { ArrowLeft, FilePdf } from "@phosphor-icons/react";
import { api } from "../../api";
import type { PrepGuide } from "../../types";
import { Loading, ErrorState, PageHeading } from "../../components/Shared";
import { usePrep } from "./usePrep";
import { GuideNotes, SourceList } from "./GuidePage";
import { subjectSources } from "./sources";

/** Every guide's notes for one track on a single page, laid out to print as one PDF. */
export default function Handbook() {
  const { track = "" } = useParams();
  const prep = usePrep();
  const summaries = (prep.data?.guides ?? []).filter((g) => g.track === track).sort((a, b) => a.order - b.order);
  const guides = useQueries({
    queries: summaries.map((g) => ({ queryKey: ["prep-guide", g.id], queryFn: () => api<PrepGuide>("/prep/guides/" + g.id) })),
  });
  if (prep.isLoading || guides.some((q) => q.isLoading)) return <Loading />;
  const failed = prep.error ?? guides.find((q) => q.error)?.error;
  if (failed) return <ErrorState error={failed} />;
  const info = prep.data?.tracks.find((t) => t.id === track);
  if (!info) return <ErrorState error={new Error("That Prep track doesn't exist.")} />;
  const loaded = guides.map((q) => q.data!).filter(Boolean);
  const subjects = [...new Set(loaded.map((g) => g.subject ?? ""))];
  return (
    <div className="prep-handbook">
      <Link className="back-link" to={"/prep/" + track}>
        <ArrowLeft size={16} aria-hidden="true" />
        Back to {info.title}
      </Link>
      <PageHeading
        title={info.title + " handbook"}
        description={`All ${loaded.length} guides' notes and cheat sheets in one place, for revision or printing.`}
        action={
          <button className="button primary" type="button" onClick={() => window.print()}>
            <FilePdf size={16} aria-hidden="true" />
            Save as PDF
          </button>
        }
      />
      <nav className="handbook-contents" aria-label="Contents">
        <ol>
          {loaded.map((g) => (
            <li key={g.id}>
              <a href={"#" + g.id}>{g.title}</a>
            </li>
          ))}
        </ol>
      </nav>
      {loaded.map((g) => (
        <article key={g.id} id={g.id} className="prep-guide">
          {g.subject && <span className="prep-subject">{g.subject}</span>}
          <h2 className="handbook-title">{g.title}</h2>
          <p className="prose">{g.summary}</p>
          <GuideNotes guide={g} puzzle={false} />
          {g.puzzle && (
            <section>
              <h2>The puzzle</h2>
              <p className="prose preserve-lines">{g.puzzle.statement}</p>
              <p className="muted">Work it out, then check your answer on the guide page.</p>
            </section>
          )}
        </article>
      ))}
      <section className="handbook-sources">
        <h2>Read more</h2>
        {subjects.map((s) => (
          <div key={s}>
            {s && <h3>{s}</h3>}
            <SourceList sources={subjectSources(track, s || undefined)} />
          </div>
        ))}
      </section>
    </div>
  );
}
