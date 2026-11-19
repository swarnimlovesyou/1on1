# Deployment and operations

For the assessment's local-demo allowance, Judge0/free-tier details, Vercel split hosting and laptop execution dependencies, read [the handoff guide](HANDOFF.md) first. A locally running website does not automatically include a locally running Judge0 service.

## Local application

Use the README's `npm run setup`, `doctor` and combined `dev` commands; do not start a second Java server. The H2 file database is persistent; back up `backend/.data` only after the API has stopped. Local application tests were run with Java 25 compiling for release 21. CI uses Java 21. Node 22 is the supported frontend runtime.

The primary service definition is `infra/local.compose.yaml`, managed by `npm run services`/`dev`/`stop`. It runs only Judge0, its private PostgreSQL/Redis, and Mailpit. Authentication/configuration is generated under ignored `.cache`; the application itself uses native H2. Bindings are localhost only. Judge0 uses its upstream privileged worker requirement; the downloaded image has not yet been proven compatible with this Docker Desktop engine.

On 16 November, the official image pull failed with unexpected EOF, followed by an unresponsive Docker daemon. Docker backend logs recorded SCSI virtual-device I/O errors. No volumes were deleted, no WSL VM was substituted, and no hosted judge fallback was enabled. Read [the exact blocker and recovery sequence](PHASE1_HANDOFF.md) before attempting grading.

`npm run backup` refuses while Java's port is open and copies native H2 files only. Restore with Java stopped, retaining a copy of the previous file first. This is separate from PostgreSQL `pg_dump` and does not export credentials.

## Full container deployment

This older optional topology remains unverified and is not the primary setup. Its API container cannot reach the host runner through `127.0.0.1`; explicitly configure an authenticated reachable judge URL/mode and container networking before testing it. It does not contain a Judge0 service. Do not run it alongside the native service definition because Mailpit ports overlap.

1. Copy `.env.example` to the ignored `.env`. Set a strong `POSTGRES_PASSWORD`. For the provided local container setup set `APP_BASE_URL=http://localhost:8088`, `SMTP_HOST=mailpit`, `SMTP_PORT=1025`, and `COOKIE_SECURE=false`. Add external AI/judge credentials locally if using those features.
2. Run `docker compose config --quiet`, then `docker compose up --build -d`.
3. Visit http://localhost:8088 and inspect http://localhost:8025 for local password-reset emails. Create a fresh student account; production does not seed the sample student. Optionally set `ADMIN_EMAIL` and a new `ADMIN_PASSWORD` before the first API start.
4. Confirm `/api/v1/system`, a public lesson, signup/login, a saved note, a practice plan and an experiment. Run a real sandboxed submission and Gemini question only after supplying working credentials.

Nginx serves the built SPA, falls back to `index.html` for app routes and forwards `/api` to Java. PostgreSQL is private to the compose network with a named data volume. The API is not exposed directly to the host. Mailpit's UI is bound only to localhost. Mailpit is for local testing; use real authenticated SMTP for public production.

## Free hosting: Vercel, Render and Neon (no local Docker needed)

The hosts build the images themselves, so this machine needs no Docker. The frontend is static on Vercel and proxies
`/api` to the Java API on Render, so the browser sees one origin and the session cookie works unchanged. Not yet
rehearsed live.

1. **Database (Neon, free):** create a project and copy its connection details. Use
   `jdbc:postgresql://<host>/<database>?sslmode=require` as `DATABASE_URL`, plus the user and password. Flyway creates
   the tables on first start.
2. **API (Render, free):** New → Blueprint → this repository. `render.yaml` builds `backend/Dockerfile` and asks for
   the secrets: the Neon details, `APP_BASE_URL` (the Vercel URL from step 3), `GROQ_API_KEY` (free at
   console.groq.com), `ADMIN_EMAIL`/`ADMIN_PASSWORD`, and optionally `JUDGE0_API_KEY` (Judge0's free RapidAPI plan,
   50 runs a day) to run code. If the service is not named `oneonone-api`, note its URL.
3. **Frontend (Vercel, free):** import the repository; `vercel.json` sets the build. If the Render URL differs from
   `https://oneonone-api.onrender.com`, edit the `/api` rewrite in `vercel.json` first.
4. Set `APP_BASE_URL` on Render to the Vercel URL and redeploy. Check `/api/v1/system`, sign up, open a lesson and
   play an animation, start a quiz, and ask the tutor a question.

Known limits of the free plans: Render sleeps after 15 minutes idle and the first request then takes about a minute
(open the site a few minutes before a demo); sessions live in the API's memory, so a sleep or redeploy signs everyone
out (learning records stay in Neon); Render's free instance has 512 MB, which a Spring Boot app fits but not
comfortably; streamed tutor answers pass through Vercel's proxy and may arrive in one piece instead of word by word.
Without SMTP, use the admin page's reset links. Production does not seed the demo account.

## Public hosting

Deploy the container application on a Linux host supporting Docker/Java. Configure TLS on the public reverse proxy, use the actual HTTPS `APP_BASE_URL`, and set `COOKIE_SECURE=true`. Inject provider/database/admin secrets using the host's secret store. Disable the local Mailpit service and supply SMTP settings. Use a verified SMTP sender for the deployment domain; adjust the server's reset-message sender if required by the provider.

Back up PostgreSQL with `pg_dump` to an external backup destination. Test restoring a backup before relying on it. Session authentication is in a single API instance, so an API restart requires signing in again; learning records remain in the database. Multi-instance deployments need shared sessions, distributed quotas and a durable execution queue before adding replicas.

Daily usage limits are server enforced and visible to administrators. Judge0 and Gemini can independently reject requests because of free-tier limits, provider quotas or account settings. The frontend surfaces these errors and retains saved work. Do not route execution through a general Java subprocess fallback: only the isolated judge should run student code.

## Logs and verification

Use `docker compose logs --tail=100 api web` for startup issues. Logs deliberately avoid provider response bodies and secrets. Verify that production cookies are secure, the browser receives no service keys, hidden tests remain absent from public responses, and the administrator UI rejects a normal student.

The repository's CI verifies unit/reference fixtures, production frontend build, real HTTP checks and browser journeys. External-service calls require separate live smoke checks. Container definitions may be inspected even on a workstation whose Docker daemon is not running; do not treat that as a successful container rollout.

## Updates and recovery

Back up the database, pull the next commit, build and run `docker compose up --build -d`. Flyway applies checked-in schema migrations. Do not edit an applied migration. Built-in unedited content follows the seed catalog; administrator-edited records are preserved. Never delete a data volume to resolve an ordinary application error. To roll back application code, use a compatible prior commit; schema rollback requires a separately tested migration/restore plan.
