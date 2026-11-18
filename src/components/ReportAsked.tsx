import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import { useApp } from "../context";

/** "I was asked this": learners report where a question came up, building fresh company data 1on1 owns. */
export default function ReportAsked({ questionId }: { questionId: string }) {
  const { user } = useApp();
  const client = useQueryClient();
  const [company, setCompany] = useState("");
  const [stage, setStage] = useState<"OA" | "Interview">("Interview");
  const report = useMutation({
    mutationFn: () => api<{ saved: boolean; repeat: boolean }>("/reports", { questionId, company: company.trim(), stage }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["reports-recent"] }),
  });
  if (!user)
    return (
      <p className="report-asked muted">
        Were you asked this in an assessment or interview? <Link to="/login">Sign in to report it</Link> so others can see it.
      </p>
    );
  function submit(e: FormEvent) {
    e.preventDefault();
    if (company.trim()) report.mutate();
  }
  return (
    <form className="report-asked" aria-label="I was asked this" onSubmit={submit}>
      <strong>I was asked this</strong>
      <input aria-label="Company" placeholder="Company" value={company} maxLength={40} onChange={(e) => (report.reset(), setCompany(e.target.value))} />
      <fieldset>
        <legend className="sr-only">Where</legend>
        {(["OA", "Interview"] as const).map((s) => (
          <label key={s}>
            <input type="radio" name="stage" value={s} checked={stage === s} onChange={() => setStage(s)} />
            {s === "OA" ? "Online assessment" : "Interview"}
          </label>
        ))}
      </fieldset>
      <button className="button small" type="submit" disabled={!company.trim() || report.isPending}>
        Report
      </button>
      {report.error && (
        <p className="inline-alert" role="alert">
          {report.error.message}
        </p>
      )}
      {report.data && (
        <p className="muted" role="status">
          {report.data.repeat ? "Thanks, you had already reported this one." : "Thanks. It now shows in recently asked."}
        </p>
      )}
    </form>
  );
}
