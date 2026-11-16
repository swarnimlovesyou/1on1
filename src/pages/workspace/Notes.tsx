import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Plus,
  Check,
  CheckCircle,
  Trash,
  BookmarkSimple,
  Notebook,
  CalendarBlank,
  ChartBar,
  Users,
  Plugs,
  ArrowClockwise,
  Download,
  Flask,
  ShieldCheck,
  ArrowLeft,
  Code,
  Lightbulb,
} from "@phosphor-icons/react";
import { api, download, resetCsrf } from "../../api";
import { useApp } from "../../context";
import type { Note, Plan, User } from "../../types";
import { useLessons, useProblems } from "../Learning";
import {
  Loading,
  ErrorState,
  PageHeading,
  Gate,
} from "../../components/Shared";
import Experiment from "../../components/Experiment";
import { RevisionCards, Sources } from "./DocumentNotebook";
export function Notes() {
  return (
    <Gate>
      <NotesContent />
    </Gate>
  );
}
function NotesContent() {
  const { progress, reload, notify } = useApp(),
    lessons = useLessons(),
    problems = useProblems();
  const [tab, setTab] = useState("My thoughts"),
    [text, setText] = useState(""),
    [title, setTitle] = useState(""),
    [adding, setAdding] = useState(false),
    [search, setSearch] = useState("");
  const save = useMutation({
    mutationFn: () =>
      api("/notes", { title: title || "A thought worth keeping", text }),
    onSuccess: () => {
      setText("");
      setTitle("");
      setAdding(false);
      reload();
      notify("Thought saved");
    },
  });
  const bookmarked = [...(lessons.data ?? []), ...(problems.data ?? [])].filter(
    (x) => progress.bookmarks.includes(x.id),
  );
  const rows = progress.notes.filter(
    (n) =>
      (tab !== "To revisit" || !n.reviewed) &&
      (n.text + " " + n.title).toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <>
      <PageHeading
        title="Your own words. Your own understanding."
        description="A home for the explanations, questions, and small discoveries worth keeping."
        action={
          <button
            className="button primary small"
            onClick={() => setAdding(!adding)}
          >
            <Plus size={17} />
            Capture a thought
          </button>
        }
      />
      <div className="library-toolbar">
        <div className="tabs">
          {["My thoughts", "My sources", "Revision cards", "Saved for later", "To revisit"].map((t) => (
            <button
              className={tab === t ? "active" : ""}
              key={t}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <input
          className="compact-search"
          aria-label="Search your notes"
          placeholder="Find a thought…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {adding && (
        <form
          className="note-compose"
          onSubmit={(e) => {
            e.preventDefault();
            save.mutate();
          }}
        >
          <label>
            A name for this thought
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What finally clicked"
            />
          </label>
          <label>
            In your own words
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              placeholder="I used to think… Now I understand…"
            />
          </label>
          <div className="note-actions">
            <button
              type="button"
              className="text-link"
              onClick={() => setAdding(false)}
            >
              Cancel
            </button>
            <button
              className="button primary small"
              disabled={!text.trim() || save.isPending}
            >
              Save to notebook <Check size={16} />
            </button>
          </div>
          {save.error && <ErrorState error={save.error} />}
        </form>
      )}
      {tab === "My sources" ? (
        <Sources />
      ) : tab === "Revision cards" ? (
        <RevisionCards />
      ) : tab === "Saved for later" ? (
        <div className="lesson-rows">
          {bookmarked.map((b) => (
            <Link
              key={b.id}
              className="lesson-row"
              to={(b.kind === "lesson" ? "/learn/" : "/practice/") + b.id}
            >
              <BookmarkSimple size={20} />
              <span>
                <strong>{b.title}</strong>
                <small>{b.topics.join(" · ")}</small>
              </span>
              <ArrowUpRight size={17} />
            </Link>
          ))}
          {!bookmarked.length && <NotesEmpty />}
        </div>
      ) : (
        <div className="notes-grid">
          {rows.map((n) => (
            <article className="personal-note" key={n.id}>
              <div className="note-meta">
                <span>
                  {new Date(n.createdAt).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                  })}
                </span>
                <button
                  className="icon-btn"
                  aria-label={"Delete " + n.title}
                  onClick={async () => {
                    try {
                      await api("/notes/" + n.id, undefined, "DELETE");
                      reload();
                    } catch (e) {
                      notify((e as Error).message);
                    }
                  }}
                >
                  <Trash size={16} />
                </button>
              </div>
              <h2>{n.title}</h2>
              <p>{n.text}</p>
              {n.experiment && (
                <details className="saved-experiment">
                  <summary>Reopen saved experiment</summary>
                  <Experiment scene={n.experiment} />
                </details>
              )}
              <div className="note-bottom">
                {n.lesson ? (
                  <Link to={"/learn/" + n.lesson}>
                    Back to concept <ArrowUpRight size={14} />
                  </Link>
                ) : (
                  <span>Personal thought</span>
                )}
                <button
                  className={"review-button " + (n.reviewed ? "success" : "")}
                  onClick={async () => {
                    try {
                      await api("/notes", { ...n, reviewed: !n.reviewed });
                      reload();
                    } catch (e) {
                      notify((e as Error).message);
                    }
                  }}
                >
                  <CheckCircle size={15} />
                  {n.reviewed ? "Revisited" : "Mark revisited"}
                </button>
              </div>
            </article>
          ))}
          {!rows.length && <NotesEmpty />}
        </div>
      )}
    </>
  );
}
function NotesEmpty() {
  return (
    <div className="empty">
      <Notebook size={42} />
      <h2>A blank page is a good beginning.</h2>
      <p>
        Save a thought, bookmark a concept, or keep a useful explanation from
        your tutor.
      </p>
      <Link to="/learn" className="text-link">
        Find something that clicks <ArrowRight size={16} />
      </Link>
    </div>
  );
}
