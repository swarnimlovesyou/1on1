import { Link, useParams } from "react-router-dom";
import { ArrowLeft, BookOpenText, CheckCircle, Circle } from "@phosphor-icons/react";
import { useApp } from "../../context";
import { Loading, ErrorState, PageHeading } from "../../components/Shared";
import { usePrep } from "./usePrep";
import { guidePassed } from "./progress";
import { subjectSources } from "./sources";

/** One track's guides, grouped by subject when the track has subjects. */
export default function PrepTrack() {
  const { track = "" } = useParams();
  const prep = usePrep();
  const { progress } = useApp();
  if (prep.isLoading) return <Loading />;
  if (prep.error || !prep.data) return <ErrorState error={prep.error} />;
  const info = prep.data.tracks.find((t) => t.id === track);
  if (!info) return <ErrorState error={new Error("That Prep track doesn't exist.")} />;
  const guides = prep.data.guides.filter((g) => g.track === track);
  const groups = [...new Set(guides.map((g) => g.subject ?? ""))];
  return (
    <>
      <Link className="back-link" to="/prep">
        <ArrowLeft size={16} aria-hidden="true" />
        All of Prep
      </Link>
      <PageHeading title={info.title} description={info.summary} />
      {track === "system-design" && (
        <Link className="prep-feature" to="/prep/system-design/playground">
          <strong>Traffic playground</strong>
          <span>Set the load, servers, cache and database, and see where requests queue up.</span>
        </Link>
      )}
      {!!guides.length && (
        <Link className="prep-feature" to={`/prep/${track}/handbook`}>
          <strong>
            <BookOpenText size={18} aria-hidden="true" /> Open the {info.title} handbook
          </strong>
          <span>All {guides.length} guides' notes and cheat sheets on one page, ready to save as a PDF.</span>
        </Link>
      )}
      {!guides.length && <p className="muted">Guides for this track are on their way.</p>}
      {groups.map((group) => (
        <section key={group} className="prep-group">
          {group && <h2 className="family-heading">{group}</h2>}
          <ol className="prep-guides">
            {guides
              .filter((g) => (g.subject ?? "") === group)
              .map((g) => {
                const passed = guidePassed(g.challengeIds, progress.attempts ?? []);
                return (
                  <li key={g.id}>
                    {passed ? (
                      <CheckCircle size={18} weight="fill" className="success" aria-label="Quiz passed" />
                    ) : (
                      <Circle size={18} aria-hidden="true" />
                    )}
                    <Link to={"/prep/guide/" + g.id}>
                      <strong>{g.title}</strong>
                      <span>{g.summary}</span>
                    </Link>
                    {g.drill && (
                      <Link className="prep-practise" to={"/prep/drill/" + g.drill} aria-label="Practise">
                        Practise
                      </Link>
                    )}
                  </li>
                );
              })}
          </ol>
          {subjectSources(track, group || undefined).length > 0 && (
            <div className="prep-reading">
              <span>Read more{group ? ` on ${group}` : ""}:</span>
              {subjectSources(track, group || undefined).map((s) => (
                <a key={s.url} href={s.url} target="_blank" rel="noopener noreferrer">
                  {s.title}
                </a>
              ))}
            </div>
          )}
        </section>
      ))}
    </>
  );
}
