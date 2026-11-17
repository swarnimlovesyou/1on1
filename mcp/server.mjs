#!/usr/bin/env node
// A thin MCP adapter over 1on1's public learning API. It owns no logic: every answer comes from the Java services,
// so grading, traces and data stay authoritative there. It reads public data only; nothing here can see or change
// a learner's account (pairing a session would be a separate, explicit step).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API = (process.env.ONEONONE_API ?? "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

class ApiError extends Error {}

async function call(path, init = {}) {
  const res = await fetch(API + path, init);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(body.message ?? `1on1 answered ${res.status} for ${path}.`);
  return { body, res };
}

const get = async (path) => (await call(path)).body;

// Mutations need the session's CSRF token, sent back with the session cookie.
async function post(path, payload) {
  const { body: session, res } = await call("/auth/session");
  const cookie = (res.headers.getSetCookie?.() ?? [res.headers.get("set-cookie")].filter(Boolean)).map((c) => c.split(";")[0]).join("; ");
  return (await call(path, { method: "POST", headers: { "content-type": "application/json", "x-csrf-token": session.csrf, cookie }, body: JSON.stringify(payload) })).body;
}

const reply = (text) => ({ content: [{ type: "text", text }] });

function tool(name, description, shape, run) {
  server.registerTool(name, { description, inputSchema: shape }, async (args) => {
    try {
      return reply(await run(args));
    } catch (e) {
      return { isError: true, ...reply(e instanceof ApiError ? e.message : `Couldn't reach 1on1 at ${API}: ${e.message}`) };
    }
  });
}

const server = new McpServer({ name: "1on1", version: "0.1.0" });

tool("search_library", "Search 1on1's lessons and original problems by title or topic.", { query: z.string().min(1) }, async ({ query }) => {
  const rows = await get("/search?q=" + encodeURIComponent(query));
  if (!rows.length) return `Nothing in the library matches "${query}".`;
  return rows.slice(0, 15).map((r) => `${r.title} (${r.id}${r.kind ? ", " + r.kind : ""})`).join("\n");
});

tool("get_lesson", "Read one lesson: its idea, invariant, common mistake, complexity and practice questions (answers are never included).", { id: z.string().min(1) }, async ({ id }) => {
  const l = await get("/lessons/" + encodeURIComponent(id));
  const parts = [`# ${l.title}`, l.body, l.invariant && `Invariant: ${l.invariant}`, l.pitfall && `Common mistake: ${l.pitfall}`];
  if (l.timeComplexity) parts.push(`Time ${l.timeComplexity}, space ${l.spaceComplexity}.`);
  for (const c of l.challenges ?? []) parts.push(`Question (${c.kind}): ${c.prompt}${c.options ? "\n  Options: " + c.options.join(" | ") : ""}`);
  return parts.filter(Boolean).join("\n\n");
});

tool(
  "run_trace",
  "Run a lesson's algorithm in 1on1's Java trace engine and return each step's narration.",
  { algorithm: z.string().min(1), input: z.string().min(1).describe("Comma-separated integers, up to 32"), target: z.number().int().optional() },
  async ({ algorithm, input, target }) => {
    const trace = await post("/experiments", { algorithm, input, ...(target === undefined ? {} : { target }) });
    const steps = trace.steps ?? [];
    const lines = steps.slice(0, 60).map((s, i) => `${i + 1}. ${s.narration ?? s.message ?? ""}`);
    return [`${steps.length} steps${trace.result !== undefined ? `, result ${trace.result}` : ""}.`, ...lines, steps.length > 60 ? `… ${steps.length - 60} more steps.` : ""].filter(Boolean).join("\n");
  },
);

tool(
  "search_questions",
  "Search the practice question bank (Codeforces, AtCoder, CSES, LeetCode and 1on1's own) with optional filters. Company data is community-reported and dated May 2022.",
  {
    query: z.string().optional(),
    source: z.enum(["1on1", "Codeforces", "AtCoder", "CSES", "LeetCode"]).optional(),
    difficulty: z.enum(["Easy", "Medium", "Hard"]).optional(),
    company: z.string().optional(),
    sort: z.enum(["easiest", "hardest", "title"]).optional(),
  },
  async ({ query, source, difficulty, company, sort }) => {
    const p = new URLSearchParams({ size: "15" });
    for (const [k, v] of Object.entries({ q: query, source, difficulty, company, sort })) if (v) p.set(k, v);
    const page = await get("/bank?" + p);
    if (!page.items.length) return "No questions match those filters.";
    const rows = page.items.map((q) => {
      const companies = Object.entries(q.companies ?? {}).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([n, c]) => `${n} (${c})`);
      return `${q.title} [${q.source}${q.difficulty ? ", " + q.difficulty : ""}] ${q.url}${companies.length ? "\n  Reported at: " + companies.join(", ") : ""}`;
    });
    return [`${page.total} questions; first ${page.items.length}:`, ...rows].join("\n");
  },
);

tool("upcoming_contests", "List upcoming Codeforces and AtCoder contests (start times in UTC).", {}, async () => {
  const { contests, sources } = await get("/contests");
  const down = sources.filter((s) => !s.ok).map((s) => s.platform);
  const rows = contests.slice(0, 20).map((c) => `${c.start} ${c.platform}: ${c.title} (${c.durationMinutes} min) ${c.url}`);
  return [...(down.length ? [`Not reachable just now: ${down.join(", ")}.`] : []), ...(rows.length ? rows : ["No upcoming contests listed."])].join("\n");
});

tool(
  "measure_growth",
  "Count the steps of 1on1's Java trace for an algorithm at n = 4, 8, 16 and 32, and name the closest growth curve.",
  { algorithm: z.string().min(1).describe("binary-search, two-pointers, sliding-window, merge-sort or quick-sort") },
  async ({ algorithm }) => {
    const m = await get("/lab/" + encodeURIComponent(algorithm));
    return `${algorithm}: steps ${m.sizes.map((n, i) => `n=${n}: ${Number(m.steps[i]).toFixed(1)}`).join(", ")}. Closest growth: ${m.closest}. These are trace steps, not time.`;
  },
);

tool("get_drill", "Get a fresh aptitude or reasoning practice question for a topic (the answer stays on the server).", { topic: z.string().min(1) }, async ({ topic }) => {
  const q = await get(`/drills/${encodeURIComponent(topic)}/next`);
  return `Seed ${q.seed}\n${q.prompt}${q.options ? "\nOptions: " + q.options.join(" | ") : ""}${q.unit ? `\nUnit: ${q.unit}` : ""}`;
});

tool(
  "check_drill",
  "Check an answer to a drill question, identified by its topic and seed.",
  { topic: z.string().min(1), seed: z.number().int().min(0), answer: z.string().min(1) },
  async ({ topic, seed, answer }) => {
    const r = await post(`/drills/${encodeURIComponent(topic)}/answer`, { seed, answer });
    return `${r.correct ? "Correct." : `Not quite; the answer is ${r.expected}.`} ${r.explanation}`;
  },
);

await server.connect(new StdioServerTransport());
