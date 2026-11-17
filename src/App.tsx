import { useEffect, useState, useRef } from "react";
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
  Code,
  CalendarBlank,
  Notebook,
  ChartBar,
  Users,
  ArrowUpRight,
  MagnifyingGlass,
  Sun,
  Moon,
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
const navigation = [
  ["/home", "Home", House],
  ["/learn", "Explore concepts", Books],
  ["/practice", "Practice", Code],
  ["/plan", "My practice plan", CalendarBlank],
  ["/notebook", "My notebook", Notebook],
  ["/progress", "Progress", ChartBar],
  ["/cohorts", "Study together", Users],
] as const;
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
    [mobile, setMobile] = useState(false),
    [search, setSearch] = useState("");
  const [theme, setTheme] = useState(
    () => localStorage.getItem("1on1-theme") ?? "system",
  );
  const searchRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const focusSearch = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", focusSearch);
    return () => window.removeEventListener("keydown", focusSearch);
  }, []);
  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const apply = () =>
      (document.documentElement.dataset.theme =
        theme === "system" ? (media.matches ? "dark" : "light") : theme);
    apply();
    media.addEventListener("change", apply);
    localStorage.setItem("1on1-theme", theme);
    return () => media.removeEventListener("change", apply);
  }, [theme]);
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
        {navigation.map(([path, label, Icon]) => (
          <NavLink key={path} to={path}>
            <Icon size={20} />
            <span>{label}</span>
            {path === "/learn" && <span className="nav-count">24</span>}
          </NavLink>
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
        theme,
        setTheme,
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
                  {location.pathname.startsWith("/learn/")
                    ? "Study notebook"
                    : (navigation.find(([p]) => p === location.pathname)?.[1] ??
                      "1on1")}
                </strong>
              </span>
              <form
                className="global-search"
                onSubmit={(e) => {
                  e.preventDefault();
                  navigate("/learn?q=" + encodeURIComponent(search));
                }}
              >
                <MagnifyingGlass size={17} />
                <input
                  aria-label="Search concepts and problems"
                  ref={searchRef}
                  placeholder="Find your next lightbulb moment"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <kbd>
                  <Command size={11} /> K
                </kbd>
              </form>
              <button
                className="icon-btn"
                aria-label="Toggle color theme"
                onClick={() =>
                  setTheme(
                    document.documentElement.dataset.theme === "dark"
                      ? "light"
                      : "dark",
                  )
                }
              >
                {theme === "dark" ||
                (theme === "system" &&
                  document.documentElement.dataset.theme === "dark") ? (
                  <Sun size={20} />
                ) : (
                  <Moon size={20} />
                )}
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
                <Route path="/learn/:id" element={<NotebookPage />} />
                <Route path="/practice" element={<Practice />} />
                <Route path="/practice/:id" element={<ProblemPage />} />
                <Route path="/practice/q/:id" element={<SolveExternal />} />
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
