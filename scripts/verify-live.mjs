import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { root } from "./project.mjs";

const base = process.env.ONEONONE_API_URL ?? "http://127.0.0.1:8080/api/v1";
if (!["127.0.0.1", "localhost", "[::1]"].includes(new URL(base).hostname))
  throw new Error(
    "Live verification is scoped to a local development application.",
  );
let cookie = "",
  csrf = "";
const report = {
  checkedAt: new Date().toISOString(),
  execution: { status: "not_checked", cases: [] },
  ai: { status: "not_checked" },
  checks: [],
};
async function api(path, body, options = {}) {
  const response = await fetch(base + path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      ...(cookie ? { Cookie: cookie } : {}),
      ...(csrf ? { "X-CSRF-TOKEN": csrf } : {}),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    signal: AbortSignal.timeout(options.timeout ?? 65000),
  });
  for (const item of response.headers.getSetCookie())
    if (item.startsWith("JSESSIONID=")) cookie = item.split(";")[0];
  if (options.stream) return response;
  const data = await response.json();
  if (data.csrf) csrf = data.csrf;
  if (!response.ok)
    throw new Error(`${response.status}: ${data.message ?? "Request failed"}`);
  return data;
}
async function awaitJob(created) {
  let job = created;
  const deadline = Date.now() + 300000;
  while (["QUEUED", "RUNNING"].includes(job.status) && Date.now() < deadline) {
    await new Promise((done) => setTimeout(done, 500));
    job = await api("/submissions/" + created.id);
  }
  return job;
}
try {
  await api("/auth/session");
  await api("/auth/register", {
    name: "Live verification (test account)",
    email: `phase1-${randomUUID()}@example.test`,
    password: randomUUID() + randomUUID(),
  });
  await api("/auth/session");
  const system = await api("/system");
  if (!process.argv.includes("--ai-only")) {
    const runner = await api("/system/check", {});
    if (!runner.reachable)
      report.execution = {
        status: "blocked",
        reason: runner.reason ?? "Runner is not reachable",
        cases: [],
      };
    else {
      const content = JSON.parse(
        readFileSync(
          join(root, "backend/src/main/resources/content.json"),
          "utf8",
        ),
      );
      for (const problem of content.problems.filter(
        (item) => item.referenceJourney,
      ))
        for (const language of ["java", "python", "cpp"]) {
          const job = await awaitJob(
            await api("/submissions", {
              problem: problem.id,
              language,
              code: problem.references[language],
              official: true,
              requestId: randomUUID(),
            }),
          );
          report.execution.cases.push({
            problem: problem.id,
            language,
            status: job.status,
          });
          console.log(`${problem.id} / ${language}: ${job.status}`);
          if (job.status !== "ACCEPTED")
            throw new Error(
              "A reference solution failed live grading. Check the saved verification result.",
            );
          if (
            job.results.some(
              (row) =>
                !row.public &&
                ["input", "expected", "actual"].some((key) => key in row),
            )
          )
            throw new Error("Hidden test information reached the client.");
        }
      for (const language of ["java", "python", "cpp"]) {
        const job = await awaitJob(
          await api("/submissions", {
            problem: "problem-three-window",
            language,
            code: "this is deliberately invalid source ???",
            official: false,
            input: "1",
            requestId: randomUUID(),
          }),
        );
        report.execution.cases.push({
          scenario: "invalid source",
          language,
          status: job.status,
        });
        if (!["COMPILATION_ERROR", "RUNTIME_ERROR"].includes(job.status))
          throw new Error("A failing program was not classified correctly.");
      }
      report.execution.status = "passed";
    }
  }
  if (!process.argv.includes("--judge-only")) {
    if (!system.ai)
      report.ai = {
        status: "blocked",
        reason: "GEMINI_API_KEY is not configured locally",
      };
    else {
      try {
        const answer = await api("/tutor", {
          message:
            "In two short sentences, explain why the selected window sum changes. Do not give a full solution.",
          mode: "explain",
          lesson: "lesson-sliding-window",
          experiment: {
            algorithm: "sliding-window",
            input: "2,1,5,1,3,2",
            target: 3,
          },
          step: 4,
        });
        if (typeof answer.text !== "string" || !answer.text.trim())
          throw new Error("Gemini returned no explanation.");
        const scene = await api("/tutor", {
          message: "Visualize binary search for 7 in 1,3,5,7,9.",
          mode: "visualize",
        });
        if (!scene.scene)
          throw new Error("Gemini returned no structured scene.");
        await api("/experiments", scene.scene);
        const response = await api(
          "/tutor/stream",
          {
            message: "Give one conceptual hint about a queue in BFS.",
            mode: "explain",
            lesson: "lesson-bfs",
          },
          { stream: true },
        );
        const stream = await response.text();
        if (
          !response.ok ||
          (!stream.includes("event:done") && !stream.includes("event: done")) ||
          stream.includes("event:error") ||
          stream.includes("event: error")
        )
          throw new Error("Gemini did not finish a streamed response.");
        report.ai = {
          status: "passed",
          explanation: true,
          validatedScene: true,
          stream: true,
        };
      } catch (error) {
        report.ai = { status: "failed", reason: error.message };
      }
    }
  }
  report.checks.push(
    "Registered an isolated test account; no existing learner record was edited.",
  );
} catch (error) {
  report.error = error.message;
} finally {
  mkdirSync(join(root, ".cache"), { recursive: true });
  writeFileSync(
    join(root, ".cache", "live-verification.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(
    JSON.stringify({
      execution: report.execution.status,
      ai: report.ai.status,
      error: report.error ?? report.ai.reason ?? report.execution.reason ?? "",
    }),
  );
  console.log(
    "Detailed evidence: .cache/live-verification.json (no credentials). Skipped/blocked integrations are not passing checks.",
  );
  if (
    report.error ||
    ["failed", "blocked"].includes(report.ai.status) ||
    ["failed", "blocked"].includes(report.execution.status)
  )
    process.exitCode = 1;
}
