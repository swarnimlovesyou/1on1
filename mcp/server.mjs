#!/usr/bin/env node
// A thin MCP adapter over 1on1's learning API. It owns no logic: every answer comes from the Java services, so
// grading, traces and data stay authoritative there. Without a token it reads public data only. With ONEONONE_TOKEN
// (made under Settings > Connect an assistant) it can also read that one learner's study context, notes and
// notebook sources, and save a note; the learner can revoke it at any time.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API = (process.env.ONEONONE_API ?? "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");
const TOKEN = process.env.ONEONONE_TOKEN ?? "";

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

// The paired-learner API authenticates by bearer token, so it needs no session or CSRF token.
const mine = (path, payload) =>
  call(path, {
    method: payload ? "POST" : "GET",
    headers: { authorization: "Bearer " + TOKEN, ...(payload ? { "content-type": "application/json" } : {}) },
    ...(payload ? { body: JSON.stringify(payload) } : {}),
  }).then((r) => r.body);

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
  {
    algorithm: z.string().min(1),
    input: z.string().optional().describe("Comma-separated integers, up to 32"),
    target: z.number().int().optional(),
    words: z.string().optional().describe("Text input, e.g. 'text|pattern' for kmp, rabin-karp and lcs"),
  },
  async ({ algorithm, input, target, words }) => {
    const trace = await post("/experiments", { algorithm, ...(input === undefined ? {} : { input }), ...(target === undefined ? {} : { target }), ...(words === undefined ? {} : { words }) });
    const steps = trace.steps ?? [];
    const lines = steps.slice(0, 60).map((s, i) => `${i + 1}. ${s.text ?? s.narration ?? ""}`);
    return [`${steps.length} steps.`, ...lines, steps.length > 60 ? `… ${steps.length - 60} more steps.` : ""].filter(Boolean).join("\n");
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

if (TOKEN) {
  tool("my_context", "The paired learner's study context: their next step, reviews due and how far each concept has got.", {}, async () => {
    const c = await mine("/assistant/context");
    const states = Object.entries(c.conceptsByState ?? {}).map(([k, v]) => `${k} ${v}`).join(", ");
    const reviews = (c.reviewsDue ?? []).map((r) => `- ${r.title} (due ${r.dueOn})`);
    return [`Learner: ${c.name}`, `Next step: ${c.nextAction?.title} (${c.nextAction?.reason})`, states && `Concepts: ${states}`, c.lastStudied && `Last studied: ${c.lastStudied}`, reviews.length ? "Reviews due:\n" + reviews.join("\n") : "No reviews due."]
      .filter(Boolean)
      .join("\n");
  });

  tool("search_my_notes", "Search the paired learner's own notes.", { query: z.string().optional() }, async ({ query }) => {
    const notes = await mine("/assistant/notes?q=" + encodeURIComponent(query ?? ""));
    return notes.length ? notes.map((n) => `## ${n.title} (${n.createdAt.slice(0, 10)})\n${n.text}`).join("\n\n") : "No notes match.";
  });

  tool("save_note", "Save a note to the paired learner's notebook (they can edit or delete it in 1on1).", { title: z.string().min(1).max(120), text: z.string().min(1).max(20000) }, async ({ title, text }) => {
    await mine("/assistant/notes", { title, text });
    return `Saved "${title}" to the learner's notes.`;
  });

  tool("search_my_sources", "Search the PDFs the paired learner uploaded to their notebook; cite each passage by source and page.", { query: z.string().min(1) }, async ({ query }) => {
    const passages = await mine("/assistant/notebook?q=" + encodeURIComponent(query));
    return passages.length ? passages.map((p) => `[${p.source}, p. ${p.page}] ${p.text}`).join("\n\n") : "Nothing in the learner's sources matches.";
  });
}

await server.connect(new StdioServerTransport());
