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
export function Admin() {
  const { user } = useApp();
  return (
    <Gate>
      {user?.role === "ADMIN" ? (
        <AdminContent />
      ) : (
        <div className="empty">
          <ShieldCheck size={36} />
          <h2>This space belongs to content editors.</h2>
          <p>
            Use an administrator account to publish lessons and judge fixtures.
          </p>
        </div>
      )}
    </Gate>
  );
}
type CheckItem = { field: string; message: string };
type Checks = {
  errors: CheckItem[];
  publication: CheckItem[];
  warnings: CheckItem[];
  canSave: boolean;
  canPublish: boolean;
  summary: Record<string, number>;
};

function parse(text: string): { record?: any; error?: string } {
  try {
    return { record: JSON.parse(text) };
  } catch (e) {
    return { error: "This is not valid JSON: " + (e as Error).message };
  }
}

function AdminContent() {
  const q = useQuery({
      queryKey: ["admin"],
      queryFn: () => api<Record<string, any>>("/admin/content"),
    }),
    [content, setContent] = useState(""),
    [checked, setChecked] = useState<{ text: string; checks: Checks }>(),
    [message, setMessage] = useState("");
  const parsed = content.trim() ? parse(content) : {};
  const single =
    parsed.record && !Array.isArray(parsed.record) ? parsed.record : undefined;
  // checks describe one exact text; any edit makes them stale
  const current = checked?.text === content ? checked.checks : undefined;
  const load = (text: string, note = "") => {
    setContent(text);
    setChecked(undefined);
    setMessage(note);
  };
  const check = useMutation({
    mutationFn: () => api<Checks>("/admin/content/check", single),
    onSuccess: (checks) => setChecked({ text: content, checks }),
  });
  const save = useMutation({
    mutationFn: (publish: boolean | undefined) =>
      Array.isArray(parsed.record)
        ? api("/admin/import", parsed.record)
        : api("/admin/content", { ...single, published: publish }),
    onSuccess: (_, publish) => {
      setMessage(
        Array.isArray(parsed.record)
          ? "Records imported."
          : publish
            ? "Published. Learners see this version now."
            : "Saved as a draft. Learners don’t see it yet.",
      );
      if (single) {
        const next = JSON.stringify({ ...single, published: publish }, null, 2);
        setContent(next);
        setChecked(current ? { text: next, checks: current } : undefined);
      }
      q.refetch();
    },
  });
  return (
    <>
      <PageHeading
        title="Build a better learning moment."
        description="Author, check, preview and publish the content students will actually use."
        action={<ShieldCheck size={26} />}
      />
      <div className="admin-layout">
        <section>
          <h2>Content collection</h2>
          {q.isLoading ? (
            <Loading />
          ) : q.error ? (
            <ErrorState error={q.error} />
          ) : (
            ["lessons", "problems", "paths"].map((k) => (
              <details key={k}>
                <summary>
                  {k} <span>{q.data?.[k].length}</span>
                </summary>
                <div className="admin-items">
                  {q.data?.[k].map((x: any) => (
                    <button
                      key={x.id}
                      onClick={() => load(JSON.stringify(x, null, 2))}
                    >
                      {x.title}
                      <span>
                        {x.published === false ? "Draft" : "Published"}
                      </span>
                    </button>
                  ))}
                </div>
              </details>
            ))
          )}
          <button
            className="button secondary small"
            onClick={() => download("1on1-content-export.json", q.data)}
          >
            <Download size={16} />
            Export collection
          </button>
        </section>
        <section>
          <h2>Content editor</h2>
          <label className="content-upload">
            Import a JSON file
            <input
              type="file"
              accept=".json,application/json"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                if (file.size > 5000000) {
                  setMessage("Use a JSON file smaller than 5 MB.");
                  return;
                }
                try {
                  const data = JSON.parse(await file.text());
                  load(
                    JSON.stringify(data, null, 2),
                    "File loaded. Check it before saving.",
                  );
                } catch {
                  setMessage("That file is not valid JSON.");
                }
              }}
            />
          </label>
          <p className="muted">
            Select an item or paste a new record, then check it. Errors block
            saving; publication checks block publishing, but you can still
            save a draft. Arrays import several records at once.
          </p>
          <label>
            Lesson, problem, or path JSON
            <textarea
              className="json-editor"
              rows={20}
              value={content}
              onChange={(e) => {
                setContent(e.target.value);
                setMessage("");
              }}
              spellCheck={false}
            />
          </label>
          {parsed.error && <p className="inline-alert">{parsed.error}</p>}
          <div className="admin-actions">
            {Array.isArray(parsed.record) ? (
              <button
                className="button primary small"
                disabled={save.isPending}
                onClick={() => save.mutate(undefined)}
              >
                Import {parsed.record.length} records{" "}
                <CheckCircle size={17} />
              </button>
            ) : (
              <>
                <button
                  className="button secondary small"
                  disabled={!single || check.isPending}
                  onClick={() => check.mutate()}
                >
                  <Flask size={16} />
                  {current ? "Check again" : "Check"}
                </button>
                <button
                  className="button secondary small"
                  disabled={!current?.canSave || save.isPending}
                  onClick={() => save.mutate(false)}
                >
                  Save draft
                </button>
                <button
                  className="button primary small"
                  disabled={!current?.canPublish || save.isPending}
                  onClick={() => save.mutate(true)}
                >
                  Publish <CheckCircle size={17} />
                </button>
              </>
            )}
          </div>
          {single && checked && !current && (
            <p className="muted">You’ve edited since the last check.</p>
          )}
          {check.error && <ErrorState error={check.error} />}
          {save.error && <ErrorState error={save.error} />}
          <p className="success" role="status">
            {message}
          </p>
          {current && <CheckList checks={current} />}
        </section>
      </div>
      {single && current?.canSave && <AdminPreview record={single} />}
      <section>
        <h2>Service usage</h2>
        <table className="simple-table">
          <thead>
            <tr>
              <th>Date (UTC)</th>
              <th>Service</th>
              <th>Requests</th>
            </tr>
          </thead>
          <tbody>
            {q.data?.usage.map((r: any, i: number) => (
              <tr key={i}>
                <td>{r.usage_day}</td>
                <td>{r.kind}</td>
                <td>{r.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}

function CheckList({ checks }: { checks: Checks }) {
  const groups: [string, string, CheckItem[]][] = [
    ["error", "Fix before saving", checks.errors],
    ["publication", "Needed before publishing", checks.publication],
    ["warning", "Worth a look", checks.warnings],
  ];
  return (
    <div className="admin-checks" aria-live="polite">
      {checks.canPublish ? (
        <p className="success">
          <CheckCircle size={16} /> Ready to publish.
        </p>
      ) : (
        <p>
          {checks.canSave
            ? "You can save this as a draft."
            : "This can’t be saved yet."}
        </p>
      )}
      {groups.map(([kind, title, items]) =>
        items.length ? (
          <div key={kind} className={"admin-check-group " + kind}>
            <h3>{title}</h3>
            <ul>
              {items.map((i, n) => (
                <li key={n}>
                  <code>{i.field}</code> {i.message}
                </li>
              ))}
            </ul>
          </div>
        ) : null,
      )}
    </div>
  );
}

/** What a learner would see, rendered from the unsaved record. */
function AdminPreview({ record }: { record: any }) {
  return (
    <section className="admin-preview">
      <h2>Preview</h2>
      <h3>{record.title}</h3>
      {record.kind === "lesson" ? (
        <>
          <p className="lesson-prose">{record.body}</p>
          {(record.blocks ?? []).map((b: any) => (
            <div className="lesson-block" key={b.id}>
              <h3>{b.title}</h3>
              <p className="lesson-prose">{b.text}</p>
            </div>
          ))}
          {record.experiment && <Experiment scene={record.experiment} />}
          <h3>Challenges</h3>
          <ol>
            {(record.challenges ?? []).map((c: any) => (
              <li key={c.id}>
                <strong>{c.title}</strong> ({c.kind}): {c.prompt}
              </li>
            ))}
          </ol>
        </>
      ) : record.kind === "problem" ? (
        <>
          <p className="preserve-lines">{record.description}</p>
          <p className="muted">{record.constraints}</p>
          <h3>Hints</h3>
          <ol>
            {(record.hints ?? []).map((h: string) => (
              <li key={h}>{h}</li>
            ))}
          </ol>
          <h3>Editorial</h3>
          <p className="preserve-lines">{record.editorial}</p>
          <p className="muted">
            {(record.tests ?? []).length} tests,{" "}
            {(record.tests ?? []).filter((t: any) => t.public === false).length}{" "}
            hidden. References:{" "}
            {Object.keys(record.references ?? { java: 1 }).join(", ")}.
          </p>
        </>
      ) : (
        <p className="muted">Paths have no learner preview.</p>
      )}
    </section>
  );
}
