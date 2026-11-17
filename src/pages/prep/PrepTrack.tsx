import { Link, useParams } from "react-router-dom";
import { ArrowLeft, CheckCircle, Circle } from "@phosphor-icons/react";
import { useApp } from "../../context";
import { Loading, ErrorState, PageHeading } from "../../components/Shared";
import { usePrep } from "./usePrep";
import { guidePassed } from "./progress";

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
        </section>
      ))}
    </>
  );
}
