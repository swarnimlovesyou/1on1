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
export function Settings() {
  return (
    <Gate>
      <SettingsContent />
    </Gate>
  );
}
function SettingsContent() {
  const { user, theme, setTheme, progress, reload, notify } = useApp(),
    qc = useQueryClient();
  const [username, setUsername] = useState(""),
    [goal, setGoal] = useState(progress.goal ?? "Understand the fundamentals");
  const q = useQuery({
    queryKey: ["leetcode"],
    queryFn: () => api<Record<string, any>>("/connections/leetcode"),
  });
  const system = useQuery({
    queryKey: ["system"],
    queryFn: () =>
      api<{
        ai: boolean;
        aiStatus: { verified: boolean; reason: string };
        executionStatus: {
          configured: boolean;
          reachable: boolean;
          executionVerified: boolean;
        };
        execution: boolean;
        aiProvider: string;
        aiModel: string;
      }>("/system"),
  });
  const checkRunner = useMutation({
    mutationFn: () => api("/system/check", {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["system"] }),
  });
  const sync = useMutation({
    mutationFn: () =>
      api<{ status?: string; message?: string; sheetTicksAdded?: number }>("/connections/leetcode", { username: username || q.data?.username }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["leetcode"] });
      qc.invalidateQueries({ queryKey: ["sheet-ticks"] });
      // a refresh that could not reach LeetCode ticked nothing, whatever an older record says
      if (data?.status !== "synced") return notify(data?.message ?? "LeetCode couldn't be reached, so nothing changed.");
      const ticked = data.sheetTicksAdded ?? 0;
      notify(ticked ? `Profile refreshed. ${ticked} sheet question${ticked === 1 ? "" : "s"} ticked from your recent solves.` : "Profile refresh finished");
    },
  });
  const stats = q.data?.data?.matchedUser?.submitStatsGlobal
    ?.acSubmissionNum as { difficulty: string; count: number }[] | undefined;
  return (
    <>
      <PageHeading
        title="Make yourself at home."
        description="Your account, your learning preferences, and your connection to LeetCode."
      />
      <div className="settings-sections">
        <section>
          <h2>Your learning space</h2>
          <div className="account-row">
            <span className="avatar large">{user?.name[0]}</span>
            <div>
              <strong>{user?.name}</strong>
              <p>{user?.email}</p>
            </div>
            <Link className="text-link" to="/forgot-password">
              Reset password <ArrowUpRight size={15} />
            </Link>
          </div>
          <label>
            Your learning goal
            <input value={goal} onChange={(e) => setGoal(e.target.value)} />
          </label>
          <button
            className="button secondary small"
            onClick={async () => {
              try {
                await api("/progress", { goal });
                reload();
                notify("Learning goal saved");
              } catch (e) {
                notify((e as Error).message);
              }
            }}
          >
            Save preference <Check size={16} />
          </button>
        </section>
        <section>
          <h2>Set the atmosphere</h2>
          <p className="muted">
            Choose the theme that feels right for your study session.
          </p>
          <div className="theme-options">
            {["light", "dark", "system"].map((t) => (
              <button
                className={theme === t ? "active" : ""}
                key={t}
                onClick={() => setTheme(t)}
              >
                <span className={"theme-preview " + t}>
                  <i />
                  <i />
                  <i />
                </span>
                {t[0].toUpperCase() + t.slice(1)}
                {theme === t && <CheckCircle size={16} />}
              </button>
            ))}
          </div>
        </section>
        <section>
          <div className="section-heading">
            <h2>LeetCode, alongside your notebook.</h2>
            <Plugs size={22} />
          </div>
          <p className="muted">
            Connect a public username. No LeetCode password or session cookie is
            needed. These external statistics are separate from work judged in
            1on1.
          </p>
          <form
            className="inline-form"
            onSubmit={(e) => {
              e.preventDefault();
              sync.mutate();
            }}
          >
            <label>
              LeetCode username
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={q.data?.username ?? "Your public username"}
                required={!q.data?.username}
              />
            </label>
            <button className="button primary small" disabled={sync.isPending}>
              <ArrowClockwise size={16} />
              {sync.isPending
                ? "Refreshing…"
                : q.data?.username
                  ? "Refresh profile"
                  : "Connect profile"}
            </button>
          </form>
          {sync.error && <ErrorState error={sync.error} />}{" "}
          {q.data?.status === "unavailable" && (
            <p className="inline-alert">{q.data.message}</p>
          )}
          {stats && (
            <>
              <div className="leetcode-stats">
                {stats.map((s) => (
                  <div key={s.difficulty}>
                    <strong>{s.count}</strong>
                    <span>{s.difficulty} solved</span>
                  </div>
                ))}
              </div>
              <p className="muted small-text">
                Last successful refresh:{" "}
                {new Date(q.data?.syncedAt).toLocaleString()}. Automatic refresh
                runs every six hours; manual refresh has a 15-minute cooldown.
              </p>
              <h3>Recent accepted problems</h3>
              <div className="leetcode-recent">
                {q.data?.data?.recentAcSubmissionList?.map((p: any) => (
                  <a
                    href={"https://leetcode.com/problems/" + p.titleSlug + "/"}
                    target="_blank"
                    rel="noreferrer"
                    key={p.id}
                  >
                    {p.title}
                    <ArrowUpRight size={15} />
                  </a>
                ))}
              </div>
            </>
          )}
          {q.data?.username && (
            <button
              className="text-link danger"
              onClick={async () => {
                await api("/connections/leetcode", undefined, "DELETE");
                qc.invalidateQueries({ queryKey: ["leetcode"] });
                notify("LeetCode disconnected");
              }}
            >
              Disconnect profile
            </button>
          )}
          <p className="form-note">
            The public connector may be unavailable when LeetCode changes or
            rate-limits its endpoint. Recent activity is not a complete
            historical solved list.
          </p>
        </section>
        <section>
          <h2>Your learning tools</h2>
          <div className="service-row">
            <span>Gemini tutor</span>
            <span
              className={system.data?.aiStatus?.verified ? "success" : "muted"}
            >
              {system.data?.aiStatus?.verified
                ? "Verified this session"
                : system.data?.ai
                  ? "Configured; no verified response yet"
                  : "Awaiting local configuration"}
            </span>
          </div>
          <div className="service-row">
            <span>Isolated code execution</span>
            <span
              className={
                system.data?.executionStatus?.executionVerified
                  ? "success"
                  : "muted"
              }
            >
              {system.data?.executionStatus?.executionVerified
                ? "All three languages verified"
                : system.data?.executionStatus?.reachable
                  ? "Reachable; execution not verified"
                  : system.data?.execution
                    ? "Configured; connection not verified"
                    : "Awaiting Judge0 configuration"}
            </span>
          </div>
          <p className="form-note">
            Keys stay on the Java server. The setup instructions in the
            repository explain local configuration. Free-tier AI limits may
            temporarily pause tutoring.
          </p>
        </section>
      </div>
    </>
  );
}
