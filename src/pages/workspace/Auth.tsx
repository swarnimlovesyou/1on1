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
export function Auth() {
  const loc = useLocation(),
    navigate = useNavigate(),
    qc = useQueryClient(),
    { reload } = useApp(),
    [params] = useSearchParams();
  const signup = loc.pathname === "/signup",
    forgot = loc.pathname === "/forgot-password",
    reset = loc.pathname === "/reset-password";
  const [name, setName] = useState(""),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState("");
  const q = useMutation({
    mutationFn: () =>
      api<Record<string, any>>(
        "/auth/" +
          (signup
            ? "register"
            : forgot
              ? "request-reset"
              : reset
                ? "reset-password"
                : "login"),
        { name, email, password, token: params.get("token") },
      ),
    onSuccess: () => {
      if (!forgot && !reset) {
        resetCsrf();
        qc.invalidateQueries({ queryKey: ["session"] });
        reload();
        navigate(signup ? "/onboarding" : "/home");
      }
    },
  });
  return (
    <div className="auth-page">
      <Link className="brand" to="/">
        <span className="brand-mark">1:1</span>1on1
        <span className="brand-dot">.</span>
      </Link>
      <div className="auth-layout">
        <section className="auth-story">
          <h1>
            A space for
            <br /> your next
            <br /> <span>“I get it.”</span>
          </h1>
          <p>
            Learn it visually. Try it yourself.
            <br /> Make a little progress, every day.
          </p>
          <div className="auth-diagram">
            {[2, 1, 5, 1, 3, 2].map((n, i) => (
              <span key={i} className={i > 1 && i < 5 ? "active" : ""}>
                {n}
              </span>
            ))}
            <small>
              Sometimes, a different way of seeing changes everything.
            </small>
          </div>
        </section>
        <section className="auth-form">
          <h2>
            {signup
              ? "Start your learning story."
              : forgot
                ? "Let’s get you back in."
                : reset
                  ? "A fresh start."
                  : "Welcome back."}
          </h2>
          <p>
            {signup
              ? "Your curiosity is all you need to bring."
              : forgot
                ? "We’ll email a password reset link if your account exists."
                : reset
                  ? "Choose a new password for your workspace."
                  : "Your notebook is right where you left it."}
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              q.mutate();
            }}
          >
            {signup && (
              <label>
                Your name
                <input
                  autoComplete="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength={100}
                  placeholder="What should we call you?"
                />
              </label>
            )}
            {!reset && (
              <label>
                Email address
                <input
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="you@example.com"
                />
              </label>
            )}
            {!forgot && (
              <label>
                Password
                <input
                  type="password"
                  autoComplete={
                    signup || reset ? "new-password" : "current-password"
                  }
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  maxLength={72}
                  placeholder="At least 8 characters"
                />
              </label>
            )}
            {!signup && !forgot && !reset && (
              <Link className="forgot-link" to="/forgot-password">
                Forgot your password?
              </Link>
            )}
            <button className="button primary full" disabled={q.isPending}>
              {q.isPending
                ? "One moment…"
                : signup
                  ? "Create your account"
                  : forgot
                    ? "Send reset link"
                    : reset
                      ? "Update password"
                      : "Back to learning"}
              <ArrowRight size={18} />
            </button>
            {q.error && <ErrorState error={q.error} />}{" "}
            {q.isSuccess && forgot && (
              <p className="success" role="status">
                {q.data.message}
              </p>
            )}
            {q.isSuccess && reset && (
              <p className="success">
                Password updated. <Link to="/login">Sign in</Link>
              </p>
            )}
          </form>
          <p className="auth-switch">
            {signup ? "Already have a notebook?" : "New around here?"}{" "}
            <Link to={signup ? "/login" : "/signup"}>
              {signup ? "Sign in" : "Make yourself at home"}
            </Link>
          </p>
          <Link to="/learn" className="back-link">
            <ArrowLeft size={15} />
            Explore without an account
          </Link>
        </section>
      </div>
    </div>
  );
}
