import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Lightbulb } from "@phosphor-icons/react";
import { api } from "../../api";
import type { PrepGuide } from "../../types";
import { Loading, ErrorState } from "../../components/Shared";
import ChallengeCard from "../../components/ChallengeCard";

/** A Prep guide: sections, key points, then its quiz graded on the server. */
export default function GuidePage() {
  const { id = "" } = useParams();
  const guide = useQuery({ queryKey: ["prep-guide", id], queryFn: () => api<PrepGuide>("/prep/guides/" + id) });
  if (guide.isLoading) return <Loading />;
  if (guide.error || !guide.data) return <ErrorState error={guide.error} />;
  const g = guide.data;
  return (
    <article className="prep-guide">
      <Link className="back-link" to={"/prep/" + g.track}>
        <ArrowLeft size={16} aria-hidden="true" />
        Back to {g.subject ?? "the track"}
      </Link>
      {g.subject && <span className="prep-subject">{g.subject}</span>}
      <h1 className="display">{g.title}</h1>
      <p className="prose">{g.summary}</p>
      {g.sections.map((s) => (
        <section key={s.title}>
          <h2>{s.title}</h2>
          <p className="prose preserve-lines">{s.text}</p>
        </section>
      ))}
      <div className="insight">
        <Lightbulb size={22} aria-hidden="true" />
        <ul>
          {g.keyPoints.map((k) => (
            <li key={k}>{k}</li>
          ))}
        </ul>
      </div>
      {!!g.challenges.length && (
        <section className="prep-quiz">
          <h2>Check yourself</h2>
          {g.challenges.map((c) => (
            <ChallengeCard key={c.id} challenge={c} />
          ))}
        </section>
      )}
    </article>
  );
}
