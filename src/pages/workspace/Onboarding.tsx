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
export function Onboarding() {
  const { reload, notify } = useApp(),
    navigate = useNavigate();
  const [level, setLevel] = useState("Finding my feet"),
    [goal, setGoal] = useState("Understand the fundamentals"),
    [language, setLanguage] = useState("java");
  return (
    <div className="onboarding">
      <Link className="brand" to="/home">
        <span className="brand-mark">1:1</span>1on1.
      </Link>
      <div>
        <Lightbulb size={34} />
        <h1>Let’s begin where you are.</h1>
        <p>There’s no wrong starting point. This is your space.</p>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            try {
              await api("/progress", {
                level,
                goal,
                language,
                onboarded: true,
              });
              reload();
              navigate("/home");
            } catch (e) {
              notify((e as Error).message);
            }
          }}
        >
          <label>
            How does DSA feel right now?
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              {[
                "Finding my feet",
                "Connecting the dots",
                "Sharpening my skills",
              ].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label>
            What are you working towards?
            <select value={goal} onChange={(e) => setGoal(e.target.value)}>
              {[
                "Understand the fundamentals",
                "Prepare for interviews",
                "Build stronger problem-solving habits",
              ].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label>
            Your preferred coding language
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="java">Java</option>
              <option value="python">Python</option>
              <option value="cpp">C++</option>
            </select>
          </label>
          <button className="button primary full">
            Find my first lightbulb moment <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
