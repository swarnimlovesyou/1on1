import { Link } from "react-router-dom";
import { useApp } from "../../context";
import { Loading, ErrorState, PageHeading } from "../../components/Shared";
import { usePrep } from "./usePrep";
import { trackProgress } from "./progress";

/** The five Prep tracks, each with how many of its guides the learner has passed. */
export default function PrepHome() {
  const prep = usePrep();
  const { progress } = useApp();
  if (prep.isLoading) return <Loading />;
  if (prep.error || !prep.data) return <ErrorState error={prep.error} />;
  const counts = trackProgress(prep.data.guides, progress.attempts ?? []);
  return (
    <>
      <PageHeading title="Prepare beyond the algorithms." description="Aptitude, reasoning, puzzles, CS fundamentals and system design, each at your own pace." />
      <div className="prep-tracks">
        {prep.data.tracks.map((t) => (
          <Link key={t.id} to={"/prep/" + t.id} className="prep-track">
            <h2>{t.title}</h2>
            <p>{t.summary}</p>
            <small>
              {t.guides
                ? `${counts[t.id]?.passed ?? 0} of ${t.guides} guides passed`
                : "Coming soon"}
            </small>
          </Link>
        ))}
      </div>
    </>
  );
}
