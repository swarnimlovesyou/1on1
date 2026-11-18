import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api";
import { ErrorState } from "../../components/Shared";

type Report = { id: string; questionId: string; company: string; stage: string; member: string; createdAt: string };

/** Learner reports, removable when they are spam; shown publicly only once trusted, so removal is rare. */
export function ReportModeration() {
  const qc = useQueryClient();
  const reports = useQuery({ queryKey: ["admin-reports"], queryFn: () => api<Report[]>("/admin/reports") });
  const remove = useMutation({
    mutationFn: (id: string) => api(`/admin/reports/${id}`, undefined, "DELETE"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-reports"] }),
  });
  return (
    <section className="admin-reports">
      <h2>Learner reports</h2>
      {reports.error && <ErrorState error={reports.error} />}
      {reports.data && !reports.data.length && <p className="muted">No learner has reported a question yet.</p>}
      {!!reports.data?.length && (
        <div className="table-scroll">
          <table className="simple-table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Company</th>
                <th>Stage</th>
                <th>From</th>
                <th>Date</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {reports.data.map((r) => (
                <tr key={r.id}>
                  <td>{r.questionId}</td>
                  <td>{r.company}</td>
                  <td>{r.stage}</td>
                  <td>{r.member}</td>
                  <td>{r.createdAt.slice(0, 10)}</td>
                  <td>
                    <button className="button small" type="button" disabled={remove.isPending} onClick={() => remove.mutate(r.id)} aria-label={`Remove ${r.company} report on ${r.questionId}`}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

/** A one-time reset link for a learner who lost their password, for installs without email. */
export function ResetLink() {
  const [email, setEmail] = useState("");
  const make = useMutation({ mutationFn: () => api<{ path: string; expiresInMinutes: number }>("/admin/members/reset-link", { email }) });
  const link = make.data && window.location.origin + make.data.path;
  return (
    <section className="admin-reset">
      <h2>Account recovery</h2>
      <p className="muted">Without email set up, make a reset link here and pass it to the learner yourself. It works once, for 30 minutes.</p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          make.mutate();
        }}
      >
        <label>
          Learner's email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <button className="button primary small" disabled={make.isPending}>
          Make a reset link
        </button>
      </form>
      {make.error && <ErrorState error={make.error} />}
      {link && (
        <p className="admin-reset-link">
          <input readOnly aria-label="Reset link" value={link} onFocus={(e) => e.target.select()} />
          <button className="button small" type="button" onClick={() => navigator.clipboard?.writeText(link)}>
            Copy
          </button>
        </p>
      )}
    </section>
  );
}
