import { spawn, spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  readdirSync,
  copyFileSync,
} from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { randomBytes, timingSafeEqual } from "node:crypto";
import { createServer, request } from "node:http";
import { createConnection } from "node:net";

export const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cache = join(root, ".cache");
const windows = process.platform === "win32";
const command = process.argv[2] ?? "doctor";
const flags = new Set(process.argv.slice(3));
mkdirSync(cache, { recursive: true });

export function readEnv(path) {
  if (!existsSync(path)) return {};
  return Object.fromEntries(
    readFileSync(path, "utf8")
      .split(/\r?\n/)
      .flatMap((line) => {
        const match = line.match(/^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$/);
        return match
          ? [[match[1], match[2].replace(/^(['"])(.*)\1$/, "$2")]]
          : [];
      }),
  );
}

function native(executable, args) {
  if (windows && /\.(cmd|bat)$/i.test(executable)) {
    const quoted = [executable, ...args]
      .map((value) => '"' + value.replaceAll('"', '""') + '"')
      .join(" ");
    return ["cmd.exe", ["/d", "/s", "/c", '"' + quoted + '"']];
  }
  return [executable, args];
}
function run(executable, args = [], options = {}) {
  const [file, parameters] = native(executable, args);
  return spawnSync(file, parameters, {
    cwd: root,
    windowsHide: true,
    windowsVerbatimArguments: windows && file === "cmd.exe",
    encoding: "utf8",
    ...options,
  });
}
function findCommand(name) {
  const result = run(windows ? "where.exe" : "which", [name]);
  return result.status === 0
    ? result.stdout.trim().split(/\r?\n/)[0]
    : undefined;
}
function javaHome() {
  const candidates = [process.env.JAVA_HOME];
  if (windows) {
    for (const base of ["Java", "Eclipse Adoptium", "Microsoft"]) {
      const path = join(process.env.ProgramFiles ?? "C:\\Program Files", base);
      if (existsSync(path))
        for (const item of readdirSync(path).reverse())
          candidates.push(join(path, item));
    }
  }
  for (const candidate of candidates.filter(Boolean)) {
    const executable = join(candidate, "bin", windows ? "java.exe" : "java");
    if (existsSync(executable)) {
      const result = run(executable, ["-version"]);
      const major = Number(
        (result.stderr + result.stdout).match(/version "(\d+)/)?.[1],
      );
      if (result.status === 0 && major >= 21) return candidate;
    }
  }
  return undefined;
}
function environment() {
  const env = { ...process.env, ...readEnv(join(root, ".env")) };
  const home = javaHome();
  if (home) env.JAVA_HOME = home;
  env.JUDGE0_MODE ||= "self-hosted";
  if (env.JUDGE0_MODE === "self-hosted") {
    const local = readEnv(join(cache, "local.env"));
    env.JUDGE0_URL =
      env.JUDGE0_URL && !env.JUDGE0_URL.includes("rapidapi.com")
        ? env.JUDGE0_URL
        : "http://127.0.0.1:2358";
    env.JUDGE0_AUTH_TOKEN ||= local.LOCAL_JUDGE_AUTH_TOKEN ?? "";
  }
  return env;
}
function initLocal() {
  if (!existsSync(join(root, ".env")))
    copyFileSync(join(root, ".env.example"), join(root, ".env"));
  const path = join(cache, "local.env");
  const local = readEnv(path);
  for (const key of [
    "LOCAL_JUDGE_AUTH_TOKEN",
    "LOCAL_JUDGE_DB_PASSWORD",
    "LOCAL_JUDGE_REDIS_PASSWORD",
  ])
    local[key] ||= randomBytes(32).toString("hex");
  writeFileSync(
    path,
    Object.entries(local)
      .map(([key, value]) => `${key}=${value}`)
      .join("\n") + "\n",
    { mode: 0o600 },
  );
  const conf = {
    JUDGE0_TELEMETRY_ENABLE: "false",
    AUTHN_TOKEN: local.LOCAL_JUDGE_AUTH_TOKEN,
    POSTGRES_HOST: "judge-db",
    POSTGRES_DB: "judge0",
    POSTGRES_USER: "judge0",
    POSTGRES_PASSWORD: local.LOCAL_JUDGE_DB_PASSWORD,
    REDIS_HOST: "judge-redis",
    REDIS_PASSWORD: local.LOCAL_JUDGE_REDIS_PASSWORD,
    COUNT: "2",
    MAX_QUEUE_SIZE: "40",
    ENABLE_NETWORK: "false",
    ALLOW_ENABLE_NETWORK: "false",
    ENABLE_CALLBACKS: "false",
    ENABLE_ADDITIONAL_FILES: "false",
    ENABLE_SUBMISSION_DELETE: "false",
    MAX_CPU_TIME_LIMIT: "10",
    MAX_WALL_TIME_LIMIT: "20",
    MAX_MEMORY_LIMIT: "512000",
    MAX_MAX_FILE_SIZE: "2048",
  };
  writeFileSync(
    join(cache, "judge0.conf"),
    Object.entries(conf)
      .map(([key, value]) => `${key}=${value}`)
      .join("\n") + "\n",
    { mode: 0o600 },
  );
}
function compose(args, options = {}) {
  return run(
    "docker",
    [
      "compose",
      "--env-file",
      join(cache, "local.env"),
      "-f",
      join(root, "infra", "local.compose.yaml"),
      ...args,
    ],
    { stdio: "inherit", ...options },
  );
}
function requireSuccess(result, label) {
  if (result.error || result.status !== 0)
    throw new Error(
      `${label} failed${result.error ? ": " + result.error.message : ""}.`,
    );
}
async function portOpen(port) {
  return new Promise((done) => {
    const socket = createConnection({ host: "127.0.0.1", port });
    socket.setTimeout(800);
    socket.once("connect", () => {
      socket.destroy();
      done(true);
    });
    socket.once("error", () => {
      socket.destroy();
      done(false);
    });
    socket.once("timeout", () => {
      socket.destroy();
      done(false);
    });
  });
}
async function doctor() {
  const env = environment();
  const [nodeMajor, nodeMinor] = process.versions.node.split(".").map(Number);
  const nodeReady = nodeMajor > 22 || (nodeMajor === 22 && nodeMinor >= 14);
  const maven = findCommand(windows ? "mvn.cmd" : "mvn");
  const java = run(
    env.JAVA_HOME
      ? join(env.JAVA_HOME, "bin", windows ? "java.exe" : "java")
      : "java",
    ["-version"],
  );
  const javaVersion = (java.stderr + java.stdout).match(
    /version "([^\"]+)/,
  )?.[1];
  const docker = run(
    "docker",
    ["info", "--format", "{{.ServerVersion}} cgroup={{.CgroupVersion}}"],
    { timeout: 12000 },
  );
  const checks = {
    Node: `${process.version} ${nodeReady ? "OK" : "NEEDS 22.14+"}`,
    Java:
      java.status === 0
        ? `${javaVersion} ${Number(javaVersion?.split(".")[0]) >= 21 ? "OK" : "NEEDS 21+"}`
        : "UNAVAILABLE",
    Maven: maven ? "AVAILABLE" : "UNAVAILABLE",
    Python:
      run("python", ["--version"]).status === 0
        ? "AVAILABLE (content/HTTP verification)"
        : "UNAVAILABLE (content/HTTP verification)",
    Docker:
      docker.status === 0
        ? docker.stdout.trim()
        : "UNAVAILABLE: start Docker Desktop Linux engine",
    Gemini: env.GEMINI_API_KEY
      ? "CONFIGURED; live verification still required"
      : "NOT CONFIGURED; authored lessons remain usable",
    Judge: `${env.JUDGE0_MODE}; configuration does not prove execution`,
  };
  for (const [key, value] of Object.entries(checks))
    console.log(`${key}: ${value}`);
  for (const port of [5173, 8080, 2358, 8025])
    console.log(`Port ${port}: ${(await portOpen(port)) ? "in use" : "free"}`);
  console.log(
    "Secrets are never printed. Local configuration and persistent data are preserved.",
  );
  return (
    nodeReady &&
    java.status === 0 &&
    Number(javaVersion?.split(".")[0]) >= 21 &&
    Boolean(maven)
  );
}
function launch(executable, args, options = {}) {
  const [file, parameters] = native(executable, args);
  return spawn(file, parameters, {
    cwd: root,
    windowsHide: true,
    windowsVerbatimArguments: windows && file === "cmd.exe",
    stdio: "inherit",
    ...options,
  });
}
async function dev() {
  initLocal();
  for (const port of [5173, 8080])
    if (await portOpen(port))
      throw new Error(
        `Port ${port} is already in use. Stop the existing preview first; no unrelated process was killed.`,
      );
  const env = environment();
  if (!findCommand(windows ? "mvn.cmd" : "mvn"))
    throw new Error("Install Maven 3.9+ and run npm run doctor.");
  if (!flags.has("--without-services"))
    requireSuccess(compose(["up", "-d"]), "Local services");
  else
    console.log(
      "Local services skipped explicitly. Grading/email require separately running services.",
    );
  const children = [];
  let closing = false;
  const stop = () => {
    if (closing) return;
    closing = true;
    for (const child of children) {
      if (windows) run("taskkill.exe", ["/PID", String(child.pid), "/T", "/F"]);
      else {
        try {
          process.kill(-child.pid, "SIGTERM");
        } catch {}
      }
    }
    server.close();
    process.exitCode = 0;
  };
  const token = randomBytes(32).toString("hex");
  const server = createServer((req, res) => {
    const received = Buffer.from(req.headers.authorization ?? "");
    const expected = Buffer.from("Bearer " + token);
    if (
      req.method !== "POST" ||
      req.url !== "/stop" ||
      received.length !== expected.length ||
      !timingSafeEqual(received, expected)
    ) {
      res.writeHead(403).end();
      return;
    }
    res.end("Stopping owned development processes.");
    setTimeout(stop, 50);
  });
  await new Promise((done) => server.listen(0, "127.0.0.1", done));
  writeFileSync(
    join(cache, "dev-control.json"),
    JSON.stringify({ port: server.address().port, token }),
    { mode: 0o600 },
  );
  children.push(
    launch(
      findCommand(windows ? "mvn.cmd" : "mvn"),
      ["-B", "spring-boot:run"],
      { cwd: join(root, "backend"), env, detached: !windows },
    ),
  );
  children.push(
    launch(
      process.execPath,
      [
        join(root, "node_modules", "vite", "bin", "vite.js"),
        "--host",
        "127.0.0.1",
        "--strictPort",
      ],
      { env, detached: !windows },
    ),
  );
  for (const child of children) {
    child.on("error", (error) => {
      console.error(error.message);
      stop();
    });
    child.on("exit", (code) => {
      if (!closing) {
        console.error(`A development service exited (${code}).`);
        stop();
      }
    });
  }
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);
  console.log(
    "1on1: http://127.0.0.1:5173/home | Mailpit: http://127.0.0.1:8025",
  );
}
async function stopDev() {
  const path = join(cache, "dev-control.json");
  if (existsSync(path)) {
    const { port, token } = JSON.parse(readFileSync(path, "utf8"));
    await new Promise((done, reject) => {
      const req = request(
        {
          hostname: "127.0.0.1",
          port,
          path: "/stop",
          method: "POST",
          headers: { Authorization: "Bearer " + token },
        },
        (res) => {
          res.resume();
          res.on("end", () =>
            res.statusCode === 200
              ? done()
              : reject(
                  new Error(
                    "Development supervisor rejected the stop request.",
                  ),
                ),
          );
        },
      );
      req.on("error", () => {
        console.log("No active development supervisor; no process was killed.");
        done();
      });
      req.setTimeout(2000, () => req.destroy());
      req.end();
    });
  }
  if (!flags.has("--without-services") && existsSync(join(cache, "local.env")))
    requireSuccess(compose(["stop"]), "Stopping local services");
  console.log("Persistent data and Docker volumes were retained.");
}
async function main() {
  if (command === "doctor") {
    if (!(await doctor())) process.exitCode = 1;
  } else if (command === "setup") {
    initLocal();
    if (!(await doctor()))
      throw new Error(
        "Resolve the prerequisite failures above, then rerun setup.",
      );
    requireSuccess(
      run(findCommand(windows ? "npm.cmd" : "npm") ?? "npm", ["ci"], {
        stdio: "inherit",
      }),
      "Frontend dependencies",
    );
    requireSuccess(
      run(
        findCommand(windows ? "mvn.cmd" : "mvn"),
        ["-B", "-f", "backend/pom.xml", "-DskipTests", "compile"],
        { env: environment(), stdio: "inherit" },
      ),
      "Java dependencies/compilation",
    );
    console.log(
      "Setup complete. Configure Gemini locally, then npm run dev. No existing data or credentials were overwritten.",
    );
  } else if (command === "dev") await dev();
  else if (command === "stop") await stopDev();
  else if (command === "services") {
    initLocal();
    requireSuccess(compose(["up", "-d"]), "Local services");
  } else if (command === "verify") {
    const env = environment();
    requireSuccess(
      run(
        findCommand(windows ? "mvn.cmd" : "mvn") ?? "mvn",
        ["-B", "-f", "backend/pom.xml", "test"],
        { env, stdio: "inherit" },
      ),
      "Java checks",
    );
    requireSuccess(
      run(findCommand(windows ? "npm.cmd" : "npm") ?? "npm", ["test"], {
        stdio: "inherit",
      }),
      "Frontend checks",
    );
    requireSuccess(
      run(findCommand(windows ? "npm.cmd" : "npm") ?? "npm", ["run", "build"], {
        stdio: "inherit",
      }),
      "Production build",
    );
    if (flags.has("--browser"))
      requireSuccess(
        run(
          findCommand(windows ? "npm.cmd" : "npm") ?? "npm",
          ["run", "test:e2e"],
          {
            stdio: "inherit",
          },
        ),
        "Browser checks (requires running app)",
      );
    console.log(
      "Local automated checks passed. Live Gemini/Judge0 verification is separate; run npm run verify:live with the app running.",
    );
  } else if (command === "backup") {
    if (await portOpen(8080))
      throw new Error(
        "Stop Java first so its H2 data files can be copied consistently.",
      );
    const source = join(root, "backend", ".data");
    if (!existsSync(source))
      throw new Error(
        "No local H2 database exists yet. PostgreSQL backups must use pg_dump; this command never guesses database credentials.",
      );
    const destination = join(
      cache,
      "backups",
      new Date().toISOString().replaceAll(":", "-"),
    );
    mkdirSync(destination, { recursive: true });
    for (const name of readdirSync(source))
      if (name.endsWith(".mv.db"))
        copyFileSync(join(source, name), join(destination, name));
    writeFileSync(
      join(destination, "README.txt"),
      "With Java stopped, restore the .mv.db file into backend/.data. Preserve a copy of the previous file first. No credentials are included.\n",
    );
    console.log(`Local database backup: ${destination}`);
  } else throw new Error(`Unknown command: ${command}`);
}

if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
)
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
