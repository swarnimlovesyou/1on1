import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Circle, Timer } from "@phosphor-icons/react";
import { api } from "../../api";
import type { MockView } from "../../types";
import { useApp } from "../../context";
import { Loading, ErrorState } from "../../components/Shared";

export function clock(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

/** Counts down from the server's deadline; the server, not this clock, decides what counts. */
export function useCountdown(deadline?: string) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);
  return deadline ? Math.max(0, (new Date(deadline).getTime() - now) / 1000) : 0;
}

/** Timed assessments over 1on1's own judged problems. */
export default function MockOA() {
  const { user, notify } = useApp();
  const qc = useQueryClient();
  const mocks = useQuery({ queryKey: ["mocks"], queryFn: () => api<MockView[]>("/mocks"), enabled: !!user });
  const companies = useQuery({
    queryKey: ["bank-companies"],
    queryFn: () => api<{ name: string; count: number }[]>("/bank/companies"),
    staleTime: Infinity,
  });
  const [size, setSize] = useState("3"),
    [minutes, setMinutes] = useState("60"),
    [style, setStyle] = useState("mixed");
  const refresh = () => qc.invalidateQueries({ queryKey: ["mocks"] });
  const start = useMutation({
    mutationFn: () => api<MockView>("/mocks", { size: Number(size), minutes: Number(minutes), style }),
    onSuccess: refresh,
    onError: (e) => notify(e.message),
  });
  const active = mocks.data?.find((m) => !m.finished);
  const remaining = useCountdown(active?.deadline);
  const finish = useMutation({
    mutationFn: (id: string) => api<MockView>(`/mocks/${id}/finish`, {}),
    onSuccess: refresh,
  });
  // integrity signals are counts the learner can see in the report; they are not proctoring
  useEffect(() => {
    if (!active) return;
    const report = (kind: string) => api(`/mocks/${active.id}/signals`, { kind }).catch(() => {});
    const onHidden = () => document.visibilityState === "hidden" && report("tab");
    const onFullscreen = () => !document.fullscreenElement && report("fullscreen");
    document.addEventListener("visibilitychange", onHidden);
    document.addEventListener("fullscreenchange", onFullscreen);
    return () => {
      document.removeEventListener("visibilitychange", onHidden);
      document.removeEventListener("fullscreenchange", onFullscreen);
    };
  }, [active?.id]);
  useEffect(() => {
    if (active && remaining <= 0 && !finish.isPending) finish.mutate(active.id);
  }, [active?.id, remaining <= 0]);

  if (!user)
    return (
      <div className="empty">
        <h2>Sign in to take a mock assessment.</h2>
        <p>Your attempts and scores are saved to your account.</p>
        <Link className="button primary small" to="/login">
          Sign in
        </Link>
      </div>
    );
  if (mocks.isLoading) return <Loading />;
  if (mocks.error) return <ErrorState error={mocks.error} />;
  const past = mocks.data!.filter((m) => m.finished);
  return (
    <div className="mock-oa">
      {active ? (
        <section className="mock-active">
          <div className="mock-timer" role="timer" aria-live="off">
            <Timer size={20} /> {clock(remaining)} left
          </div>
          <p className="muted">
            Solve each problem and submit it. Only official accepted submissions made before the timer ends count.
          </p>
          <ol className="mock-problems">
            {active.problems.map((p) => (
              <li key={p.id}>
                {p.accepted ? <CheckCircle size={18} weight="fill" className="success" /> : <Circle size={18} />}
                <Link to={`/practice/${p.id}?mock=${active.id}`}>{p.title}</Link>
                <span className={"difficulty " + p.difficulty.toLowerCase()}>{p.difficulty}</span>
              </li>
            ))}
          </ol>
          <button className="button secondary small" disabled={finish.isPending} onClick={() => finish.mutate(active.id)}>
            Finish now
          </button>
        </section>
      ) : (
        <section className="mock-start">
          <h2>Take a timed assessment.</h2>
          <p className="muted">
            Problems come from 1on1's own judged set. A company style mirrors that company's mix of difficulties from
            the community-reported lists.
          </p>
          <div className="practice-filters">
            <label>
              Problems
              <select value={size} onChange={(e) => setSize(e.target.value)}>
                <option>2</option>
                <option>3</option>
              </select>
            </label>
            <label>
              Time
              <select value={minutes} onChange={(e) => setMinutes(e.target.value)}>
                <option value="60">60 minutes</option>
                <option value="90">90 minutes</option>
              </select>
            </label>
            <label>
              Style
              <select value={style} onChange={(e) => setStyle(e.target.value)}>
                <option value="mixed">Mixed difficulty</option>
                {companies.data?.slice(0, 60).map((c) => (
                  <option key={c.name} value={c.name}>
                    {c.name} style
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button className="button primary small" disabled={start.isPending} onClick={() => start.mutate()}>
            Start mock
          </button>
        </section>
      )}
      {!!past.length && (
        <section className="mock-history">
          <h2>Your reports</h2>
          {past.map((m) => (
            <div key={m.id} className="mock-report">
              <strong>
                {m.score} of {m.problems.length} solved
              </strong>
              <span className="muted">
                {m.style === "mixed" ? "Mixed" : m.style + " style"} · {m.minutes} min ·{" "}
                {new Date(m.startedAt).toLocaleString()}
              </span>
              <ul>
                {m.problems.map((p) => (
                  <li key={p.id}>
                    {p.accepted ? "Accepted" : "Not solved"}: {p.title}
                  </li>
                ))}
              </ul>
              <small className="muted">
                Integrity signals: {m.signals.tabSwitches} tab switches, {m.signals.fullscreenExits} fullscreen exits.
              </small>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
