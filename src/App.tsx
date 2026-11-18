import { useCallback, useEffect, useState } from "react";
import {
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as Dialog from "@radix-ui/react-dialog";
import {
  House,
  Books,
  Exam,
  Code,
  CalendarBlank,
  Notebook,
  ChartBar,
  Users,
  ArrowUpRight,
  MagnifyingGlass,
  PlayCircle,
  ListChecks,
  Trophy,
  SidebarSimple,
  SignOut,
  ArrowRight,
  Command,
  Plugs,
  Flask,
  ShieldCheck,
  X,
} from "@phosphor-icons/react";
import { api, resetCsrf } from "./api";
import { AppContext } from "./context";
import { emptyProgress } from "./types";
import type { Progress, User } from "./types";
import { Home, Library, NotebookPage, Landing } from "./pages/Learning";
import { Practice, ProblemPage } from "./pages/Practice";
import SolveExternal from "./pages/practice/SolveExternal";
import PrepHome from "./pages/prep/PrepHome";
import PrepTrack from "./pages/prep/PrepTrack";
import GuidePage from "./pages/prep/GuidePage";
import DrillPage from "./pages/prep/DrillPage";
import Animations from "./pages/Animations";
import Contests from "./pages/contests/Contests";
import CommandPalette from "./components/CommandPalette";
import { SHORTCUTS, keyFor, useShortcuts } from "./shortcuts";
import PlaygroundPage from "./pages/prep/PlaygroundPage";
import {
  Planner,
  Notes,
  Analytics,
  Cohorts,
  Settings,
  Evidence,
  Admin,
  Auth,
  Onboarding,
} from "./pages/Workspace";
const navigation: [string, [string, string, typeof House][]][] = [
  [
    "Learn",
    [
      ["/home", "Home", House],
      ["/learn", "Explore concepts", Books],
      ["/learn/animations", "Animations", PlayCircle],
    ],
  ],
  [
    "Practise",
    [
      ["/practice", "Practice", Code],
      ["/practice?tab=sheets", "Sheets", ListChecks],
      ["/contests", "Contests", Trophy],
      ["/prep", "Prep", Exam],
    ],
  ],
  [
    "Your work",
    [
      ["/plan", "My practice plan", CalendarBlank],
      ["/notebook", "My notebook", Notebook],
      ["/progress", "Progress", ChartBar],
      ["/cohorts", "Study together", Users],
    ],
  ],
];

/** Which sidebar link is the current page; sheets and animations live under their parents' paths. */
function isCurrent(to: string, pathname: string, search: string) {
  const sheets = pathname === "/practice" && new URLSearchParams(search).get("tab") === "sheets";
  if (to === "/practice?tab=sheets") return sheets;
  if (to === "/practice") return pathname.startsWith("/practice") && !sheets;
  if (to === "/learn/animations") return pathname === to;
  if (to === "/learn") return pathname.startsWith("/learn") && pathname !== "/learn/animations";
  return pathname === to || pathname.startsWith(to + "/");
}
function Brand() {
  return (
    <Link to="/home" className="brand" aria-label="1on1 home">
      <span className="brand-mark">
        1<span>:</span>1
      </span>
      <span>
        1on1<span className="brand-dot">.</span>
      </span>
    </Link>
  );
}
export default function App() {
  const qc = useQueryClient(),
    location = useLocation(),
    navigate = useNavigate();
  const session = useQuery({
    queryKey: ["session"],
    queryFn: () => api<{ user: User | null; csrf: string }>("/auth/session"),
  });
  const user = session.data?.user ?? null;
  const [palette, setPalette] = useState(false);
  const [keys, setKeys] = useState(false);
  useShortcuts(
    useCallback((path: string) => navigate(path), [navigate]),
    useCallback(() => setKeys(true), []),
  );
  // fetched once for the whole app (the tutor reads it to say up front when AI is unavailable)
  useQuery({
    queryKey: ["system"],
    queryFn: () => api<{ ai: boolean }>("/system"),
    staleTime: 60_000,
  });
  const pq = useQuery({
    queryKey: ["progress", user?.id],
    queryFn: () => api<Progress>("/progress"),
    enabled: !!user,
  });
  const progress = { ...emptyProgress, ...pq.data };
  const [notice, setNotice] = useState(""),
    [mobile, setMobile] = useState(false);
  // light only, like datalis; clear any older saved choice
  useEffect(() => {
    document.documentElement.dataset.theme = "light";
    localStorage.removeItem("1on1-theme");
  }, []);
  useEffect(() => {
    if (!notice) return;
    const t = setTimeout(() => setNotice(""), 4500);
    return () => clearTimeout(t);
  }, [notice]);
  useEffect(() => {
    setMobile(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  const reload = () => {
    qc.invalidateQueries({ queryKey: ["progress"] });
    qc.invalidateQueries({ queryKey: ["session"] });
  };
  const sidebar = (
    <>
      <Brand />
      <div className="sidebar-intro">A space to figure it out.</div>
      <nav aria-label="Main navigation">
        {navigation.map(([group, links]) => (
          <div key={group} className="nav-group">
            <p className="nav-group-label">{group}</p>
            {links.map(([path, label, Icon]) => {
              const current = isCurrent(path, location.pathname, location.search);
              return (
                <Link key={path} to={path} className={current ? "active" : undefined} aria-current={current ? "page" : undefined}>
                  <Icon size={20} />
                  <span>{label}</span>
                  {path === "/learn" && <span className="nav-count">24</span>}
                  {keyFor(path) && (
                    <kbd className="nav-key" aria-hidden="true">
                      {keyFor(path)}
                    </kbd>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <NavLink to="/settings">
          <Plugs size={19} />
          LeetCode & settings
        </NavLink>
        <NavLink to="/evidence">
          <Flask size={19} />
          Algorithm evidence
        </NavLink>
        {user?.role === "ADMIN" && (
          <NavLink to="/admin">
            <ShieldCheck size={19} />
            Content studio
          </NavLink>
        )}
        <div className="sidebar-tip">
          <span className="tip-dot" />
          Small steps. Real understanding.
        </div>
        <Link className="user-profile" to={user ? "/settings" : "/login"}>
          <span className="avatar">
            {user
              ? user.name
                  .split(" ")
                  .map((s) => s[0])
                  .slice(0, 2)
                  .join("")
              : "You"}
          </span>
          <span>
            <strong>{user?.name ?? "Your learning space"}</strong>
            <small>
              {user ? "Personal workspace" : "Sign in to save your progress"}
            </small>
          </span>
          <ArrowUpRight size={16} />
        </Link>
      </div>
    </>
  );
  const authPage = [
    "/login",
    "/signup",
    "/forgot-password",
    "/reset-password",
    "/onboarding",
  ].includes(location.pathname);
  return (
    <AppContext
      value={{
        user,
        progress,
        progressReady: pq.isSuccess || !user,
        notify: setNotice,
        reload,
      }}
    >
      {location.pathname === "/" ? (
        <Landing />
      ) : authPage ? (
        <Routes>
          <Route path="/login" element={<Auth />} />
          <Route path="/signup" element={<Auth />} />
          <Route path="/forgot-password" element={<Auth />} />
          <Route path="/reset-password" element={<Auth />} />
          <Route path="/onboarding" element={<Onboarding />} />
        </Routes>
      ) : (
        <div className="app-shell">
          <aside className="sidebar">{sidebar}</aside>
          <CommandPalette open={palette} setOpen={setPalette} />
          <Dialog.Root open={keys} onOpenChange={setKeys}>
            <Dialog.Portal>
              <Dialog.Overlay className="palette-backdrop" />
              <Dialog.Content className="palette keys-dialog" aria-describedby={undefined}>
                <Dialog.Title>Keyboard shortcuts</Dialog.Title>
                <dl>
                  {SHORTCUTS.map(([key, , label]) => (
                    <div key={key}>
                      <dt>
                        <kbd>{key}</kbd>
                      </dt>
                      <dd>{label}</dd>
                    </div>
                  ))}
                  <div>
                    <dt>
                      <kbd>Ctrl K</kbd>
                    </dt>
                    <dd>Jump to anything</dd>
                  </div>
                  <div>
                    <dt>
                      <kbd>?</kbd>
                    </dt>
                    <dd>This list</dd>
                  </div>
                </dl>
              </Dialog.Content>
            </Dialog.Portal>
          </Dialog.Root>
          <div className="key-strip" aria-hidden="true">
            {SHORTCUTS.map(([key, , label]) => (
              <span key={key}>
                <kbd>{key}</kbd> {label}
              </span>
            ))}
            <span>
              <kbd>Ctrl K</kbd> Jump to
            </span>
            <span>
              <kbd>?</kbd> Keys
            </span>
          </div>
          <Dialog.Root open={mobile} onOpenChange={setMobile}>
            <Dialog.Portal>
              <Dialog.Overlay className="overlay" />
              <Dialog.Content className="mobile-nav">
                <Dialog.Title className="sr-only">Navigation</Dialog.Title>
                <Dialog.Description className="sr-only">
                  Move between your learning tools.
                </Dialog.Description>
                <Dialog.Close
                  className="icon-btn close"
                  aria-label="Close navigation"
                >
                  <X size={20} />
                </Dialog.Close>
                {sidebar}
              </Dialog.Content>
            </Dialog.Portal>
          </Dialog.Root>
          <div className="app-main">
            <header className="topbar">
              <button
                className="icon-btn mobile-toggle"
                aria-label="Open navigation"
                onClick={() => setMobile(true)}
              >
                <SidebarSimple size={22} />
              </button>
              <span className="breadcrumb">
                Your workspace <span>/</span>{" "}
                <strong>
                  {location.pathname === "/learn/animations"
                    ? "Animations"
                    : location.pathname.startsWith("/learn/")
                      ? "Study notebook"
                      : (navigation
                          .flatMap(([, links]) => links)
                          .find(([p]) => isCurrent(p, location.pathname, location.search))?.[1] ?? "1on1")}
                </strong>
              </span>
              <button
                type="button"
                className="global-search"
                aria-label="Jump to anything (Ctrl K)"
                onClick={() => setPalette(true)}
              >
                <MagnifyingGlass size={17} aria-hidden="true" />
                <span>Find your next lightbulb moment</span>
                <kbd>
                  <Command size={11} /> K
                </kbd>
              </button>
              {user ? (
                <button
                  className="icon-btn"
                  aria-label="Sign out"
                  onClick={async () => {
                    await api("/auth/logout", {});
                    resetCsrf();
                    qc.clear();
                    navigate("/login");
                  }}
                >
                  <SignOut size={20} />
                </button>
              ) : (
                <Link className="button small primary" to="/login">
                  Sign in <ArrowRight size={15} />
                </Link>
              )}
            </header>
            <main id="main-content" className="page">
              <Routes>
                <Route path="/home" element={<Home />} />
                <Route path="/learn" element={<Library />} />
                <Route path="/learn/animations" element={<Animations />} />
                <Route path="/learn/:id" element={<NotebookPage />} />
                <Route path="/practice" element={<Practice />} />
                <Route path="/practice/:id" element={<ProblemPage />} />
                <Route path="/practice/q/:id" element={<SolveExternal />} />
                <Route path="/contests" element={<Contests />} />
                <Route path="/prep" element={<PrepHome />} />
                <Route path="/prep/:track" element={<PrepTrack />} />
                <Route path="/prep/guide/:id" element={<GuidePage />} />
                <Route path="/prep/system-design/playground" element={<PlaygroundPage />} />
                <Route path="/prep/drill/:topic" element={<DrillPage />} />
                <Route path="/plan" element={<Planner />} />
                <Route path="/notebook" element={<Notes />} />
                <Route path="/progress" element={<Analytics />} />
                <Route path="/cohorts" element={<Cohorts />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/evidence" element={<Evidence />} />
                <Route path="/admin" element={<Admin />} />
                <Route
                  path="*"
                  element={
                    <div className="empty">
                      <h1>That page took a different path.</h1>
                      <Link className="button primary" to="/home">
                        Back to your workspace
                      </Link>
                    </div>
                  }
                />
              </Routes>
              <footer className="app-footer">
                <span>1on1 — understanding takes practice.</span>
                <Link to="/learn">
                  Keep exploring <ArrowUpRight size={14} />
                </Link>
              </footer>
            </main>
          </div>
        </div>
      )}
      {notice && (
        <div className="toast" role="status">
          {notice}
          <button
            aria-label="Dismiss notification"
            onClick={() => setNotice("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </AppContext>
  );
}
