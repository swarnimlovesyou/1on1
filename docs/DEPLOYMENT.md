# Deployment and operations

## Local application

Use the README's two-terminal setup. The H2 file database is persistent; back up `backend/.data` only after the API has stopped. Local application tests were run with Java 25 compiling for release 21. CI uses Java 21. Node 22 is the supported frontend runtime.

## Full container deployment

1. Copy `.env.example` to the ignored `.env`. Set a strong `POSTGRES_PASSWORD`. For the provided local container setup set `APP_BASE_URL=http://localhost:8088`, `SMTP_HOST=mailpit`, `SMTP_PORT=1025`, and `COOKIE_SECURE=false`. Add external AI/judge credentials locally if using those features.
2. Run `docker compose config --quiet`, then `docker compose up --build -d`.
3. Visit http://localhost:8088 and inspect http://localhost:8025 for local password-reset emails. Create a fresh student account; production does not seed the sample student. Optionally set `ADMIN_EMAIL` and a new `ADMIN_PASSWORD` before the first API start.
4. Confirm `/api/v1/system`, a public lesson, signup/login, a saved note, a practice plan and an experiment. Run a real sandboxed submission and Gemini question only after supplying working credentials.

Nginx serves the built SPA, falls back to `index.html` for app routes and forwards `/api` to Java. PostgreSQL is private to the compose network with a named data volume. The API is not exposed directly to the host. Mailpit's UI is bound only to localhost. Mailpit is for local testing; use real authenticated SMTP for public production.

## Public hosting

Deploy the container application on a Linux host supporting Docker/Java. Configure TLS on the public reverse proxy, use the actual HTTPS `APP_BASE_URL`, and set `COOKIE_SECURE=true`. Inject provider/database/admin secrets using the host's secret store. Disable the local Mailpit service and supply SMTP settings. Use a verified SMTP sender for the deployment domain; adjust the server's reset-message sender if required by the provider.

Back up PostgreSQL with `pg_dump` to an external backup destination. Test restoring a backup before relying on it. Session authentication is in a single API instance, so an API restart requires signing in again; learning records remain in the database. Multi-instance deployments need shared sessions, distributed quotas and a durable execution queue before adding replicas.

Daily usage limits are server enforced and visible to administrators. Judge0 and Gemini can independently reject requests because of free-tier limits, provider quotas or account settings. The frontend surfaces these errors and retains saved work. Do not route execution through a general Java subprocess fallback: only the isolated judge should run student code.

## Logs and verification

Use `docker compose logs --tail=100 api web` for startup issues. Logs deliberately avoid provider response bodies and secrets. Verify that production cookies are secure, the browser receives no service keys, hidden tests remain absent from public responses, and the administrator UI rejects a normal student.

The repository's CI verifies unit/reference fixtures, production frontend build, real HTTP checks and browser journeys. External-service calls require separate live smoke checks. Container definitions may be inspected even on a workstation whose Docker daemon is not running; do not treat that as a successful container rollout.

## Updates and recovery

Back up the database, pull the next commit, build and run `docker compose up --build -d`. Flyway applies checked-in schema migrations. Do not edit an applied migration. Built-in unedited content follows the seed catalog; administrator-edited records are preserved. Never delete a data volume to resolve an ordinary application error. To roll back application code, use a compatible prior commit; schema rollback requires a separately tested migration/restore plan.
