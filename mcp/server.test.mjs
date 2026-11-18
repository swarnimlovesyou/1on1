import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// A stub of the 1on1 API, so the adapter is tested without the app running.
const seen = [];
const api = http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    seen.push({ method: req.method, url: req.url, headers: req.headers, body });
    const send = (status, json, headers = {}) => {
      res.writeHead(status, { "content-type": "application/json", ...headers });
      res.end(JSON.stringify(json));
    };
    if (req.url.startsWith("/api/v1/auth/session")) return send(200, { user: null, csrf: "token-1" }, { "set-cookie": "JSESSIONID=abc; Path=/" });
    if (req.url.startsWith("/api/v1/bank?")) return send(200, { total: 1, items: [{ id: "lc-two-sum", title: "Two Sum", source: "LeetCode", difficulty: "Easy", url: "https://leetcode.com/problems/two-sum/", companies: { Amazon: 117, Google: 44 } }] });
    if (req.url === "/api/v1/experiments") return send(200, { steps: [{ text: "Start." }, { text: "Done." }], result: "9" });
    if (req.url.startsWith("/api/v1/assistant/")) {
      if (req.headers.authorization !== "Bearer 1on1_test") return send(401, { message: "Pair this assistant from 1on1's Settings." });
      if (req.url === "/api/v1/assistant/context")
        return send(200, { name: "Ana", nextAction: { title: "Binary Search", reason: "Its prerequisites are done." }, reviewsDue: [{ title: "Arrays", dueOn: "2026-11-18" }], conceptsByState: { new: 30, passed: 10 } });
      if (req.url.startsWith("/api/v1/assistant/notes") && req.method === "POST") return send(200, { id: "note-1" });
      if (req.url.startsWith("/api/v1/assistant/notes")) return send(200, [{ id: "note-1", title: "Kadane", text: "reset when negative", createdAt: "2026-11-17T10:00:00Z" }]);
    }
    send(404, { message: "Not found." });
  });
});

let client, paired;
before(async () => {
  await new Promise((r) => api.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${api.address().port}/api/v1`;
  const env = { ...process.env, ONEONONE_API: base };
  delete env.ONEONONE_TOKEN;
  client = new Client({ name: "test", version: "1.0.0" });
  await client.connect(new StdioClientTransport({ command: process.execPath, args: ["server.mjs"], env }));
  paired = new Client({ name: "paired", version: "1.0.0" });
  await paired.connect(new StdioClientTransport({ command: process.execPath, args: ["server.mjs"], env: { ...env, ONEONONE_TOKEN: "1on1_test" } }));
});
after(async () => {
  await client?.close();
  await paired?.close();
  api.close();
});

const text = (result) => result.content.map((c) => c.text).join("\n");

test("lists the learning tools and nothing that touches a learner's private data", async () => {
  const names = (await client.listTools()).tools.map((t) => t.name).sort();
  assert.deepEqual(names, ["check_drill", "get_drill", "get_lesson", "run_trace", "search_library", "search_questions", "upcoming_contests"]);
});

test("question search passes filters and reports companies", async () => {
  const result = await client.callTool({ name: "search_questions", arguments: { query: "two", company: "Google", sort: "easiest" } });
  const call = seen.findLast((s) => s.url.startsWith("/api/v1/bank?"));
  const params = new URL(call.url, "http://x").searchParams;
  assert.equal(params.get("q"), "two");
  assert.equal(params.get("company"), "Google");
  assert.equal(params.get("sort"), "easiest");
  assert.match(text(result), /Two Sum/);
  assert.match(text(result), /Amazon \(117\)/);
});

test("a trace posts the scene with the session's CSRF token and cookie", async () => {
  const result = await client.callTool({ name: "run_trace", arguments: { algorithm: "two-pointers", input: "1, 2, 7", target: 9 } });
  const post = seen.findLast((s) => s.url === "/api/v1/experiments");
  assert.equal(post.method, "POST");
  assert.equal(post.headers["x-csrf-token"], "token-1");
  assert.match(post.headers.cookie, /JSESSIONID=abc/);
  assert.deepEqual(JSON.parse(post.body), { algorithm: "two-pointers", input: "1, 2, 7", target: 9 });
  assert.match(text(result), /2 steps/);
  assert.match(text(result), /1\. Start\./);
});

test("an API error comes back as a tool error with the API's own sentence", async () => {
  const result = await client.callTool({ name: "get_drill", arguments: { topic: "nonsense" } });
  assert.equal(result.isError, true);
  assert.match(text(result), /Not found/);
});

test("a paired adapter adds the learner's own tools and sends the token as a bearer", async () => {
  const names = (await paired.listTools()).tools.map((t) => t.name);
  for (const n of ["my_context", "search_my_notes", "save_note", "search_my_sources"]) assert.ok(names.includes(n), n);
  const context = text(await paired.callTool({ name: "my_context", arguments: {} }));
  assert.match(context, /Learner: Ana/);
  assert.match(context, /Next step: Binary Search/);
  assert.match(context, /Arrays \(due 2026-11-18\)/);
  const saved = await paired.callTool({ name: "save_note", arguments: { title: "Kadane", text: "reset when negative" } });
  assert.match(text(saved), /Saved "Kadane"/);
  const call = seen.findLast((s) => s.url === "/api/v1/assistant/notes" && s.method === "POST");
  assert.equal(call.headers.authorization, "Bearer 1on1_test");
  assert.equal(call.headers["x-csrf-token"], undefined, "bearer calls need no session");
  assert.match(text(await paired.callTool({ name: "search_my_notes", arguments: { query: "kad" } })), /Kadane/);
});
