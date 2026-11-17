import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Play } from "@phosphor-icons/react";
import Experiment from "../components/Experiment";
import FamilyMark from "../components/FamilyMark";
import { Loading, ErrorState, PageHeading } from "../components/Shared";
import { FAMILIES, familyOfLesson, familyStyle, type FamilyId } from "../families";
import type { Lesson } from "../types";
import { useLessons } from "./Learning";

/** Every lesson's animation in one place. Each one runs its Java trace only when the learner presses play. */
export default function Animations() {
  const lessons = useLessons();
  if (lessons.isLoading) return <Loading />;
  if (lessons.error || !lessons.data) return <ErrorState error={lessons.error} retry={() => lessons.refetch()} />;
  const withScene = lessons.data.filter((l) => l.experiment);
  return (
    <>
      <Link className="back-link" to="/learn">
        <ArrowLeft size={16} aria-hidden="true" />
        Back to the library
      </Link>
      <PageHeading
        title="Every animation, in one place."
        description="Each one runs the real algorithm in Java and lets you play, step and scrub through it. Open the lesson when you want the why."
      />
      {(Object.keys(FAMILIES) as FamilyId[]).map((family) => {
        const members = withScene.filter((l) => familyOfLesson(l) === family);
        return members.length ? (
          <section key={family} className="family-group">
            <h2 className="family-heading">
              <FamilyMark family={family} label />
            </h2>
            <div className="animation-grid">
              {members.map((l) => (
                <AnimationCard key={l.id} lesson={l} family={family} />
              ))}
            </div>
          </section>
        ) : null;
      })}
    </>
  );
}

function AnimationCard({ lesson, family }: { lesson: Lesson; family: FamilyId }) {
  const [open, setOpen] = useState(false);
  return (
    <article className="animation-card has-family" style={familyStyle(family)}>
      <h3>{lesson.title}</h3>
      {lesson.invariant && <p className="muted">{lesson.invariant}</p>}
      {open ? (
        <Experiment scene={lesson.experiment!} compact />
      ) : (
        <button className="button" type="button" onClick={() => setOpen(true)} aria-label={`Play this animation: ${lesson.title}`}>
          <Play size={16} aria-hidden="true" />
          Play this animation
        </button>
      )}
      <Link className="animation-lesson" to={"/learn/" + lesson.id}>
        Open the lesson<span className="sr-only">: {lesson.title}</span>
      </Link>
    </article>
  );
}
