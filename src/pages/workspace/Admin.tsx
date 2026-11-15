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
function AdminContent() {
  const q = useQuery({
      queryKey: ["admin"],
      queryFn: () => api<Record<string, any>>("/admin/content"),
    }),
    [content, setContent] = useState(""),
    [message, setMessage] = useState("");
  const save = useMutation({
    mutationFn: () => {
      const parsed = JSON.parse(content);
      return api(
        "/admin/" + (Array.isArray(parsed) ? "import" : "content"),
        parsed,
      );
    },
    onSuccess: () => {
      setMessage("Content validated and saved.");
      q.refetch();
    },
  });
  return (
    <>
      <PageHeading
        title="Build a better learning moment."
        description="Author, validate, and publish the content students will actually use."
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
                      onClick={() => {
                        setContent(JSON.stringify(x, null, 2));
                        setMessage("");
                      }}
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
                  const parsed = JSON.parse(await file.text());
                  setContent(JSON.stringify(parsed, null, 2));
                  setMessage("File loaded. Validate and save to import it.");
                } catch {
                  setMessage("That file is not valid JSON.");
                }
              }}
            />
          </label>
          <p className="muted">
            Select an item or paste a new JSON record. Set published to false to
            keep a draft. Import arrays to add multiple records.
          </p>
          <label>
            Lesson, problem, or path JSON
            <textarea
              className="json-editor"
              rows={20}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              spellCheck={false}
            />
          </label>
          <button
            className="button primary small"
            disabled={!content.trim() || save.isPending}
            onClick={() => save.mutate()}
          >
            Validate & save <CheckCircle size={17} />
          </button>
          {save.error && <ErrorState error={save.error} />}
          <p className="success" role="status">
            {message}
          </p>
        </section>
      </div>
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
