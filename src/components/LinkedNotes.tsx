import { Link } from "react-router-dom";
import { useApp } from "../context";

/** The learner's own notes saved from this lesson or problem, so they meet them again in context. */
export default function LinkedNotes({
  lesson,
  problem,
}: {
  lesson?: string;
  problem?: string;
}) {
  const { progress } = useApp();
  const notes = progress.notes
    .filter(
      (n) =>
        (lesson && n.lesson === lesson) || (problem && n.problem === problem),
    )
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  if (!notes.length) return null;
  return (
    <div className="linked-notes">
      <h3>Your notes on this {lesson ? "concept" : "problem"}</h3>
      <ul>
        {notes.slice(0, 5).map((n) => (
          <li key={n.id}>
            <Link to="/notebook">{n.title}</Link>
            <small>{new Date(n.createdAt).toLocaleDateString()}</small>
          </li>
        ))}
      </ul>
      {notes.length > 5 && (
        <Link to="/notebook" className="text-link">
          All {notes.length} in your notebook
        </Link>
      )}
    </div>
  );
}
