# 1on1

**Make it click.** A visual DSA learning platform built with React, TypeScript, Java, Spring Boot, and persistent storage.

Explore interactive notebooks, change algorithm inputs, answer prediction checkpoints, save your own explanations, and practise in an integrated Java/Python/C++ editor. Gemini supplies contextual help; Java computes visual execution traces and grades runner output.

![1on1 learning workspace](docs/screenshots/home.png)

The screenshot shows the actual local application with an empty guest learning record. [View an interactive notebook](docs/screenshots/notebook.png).

## Run locally

Prerequisites: Java 21 or newer, Maven 3.9+, Node 22.14+ and npm. Python 3 is needed only to regenerate authored content or run the HTTP verification script.

```powershell
git clone https://github.com/swarnimlovesyou/1on1.git
cd 1on1
npm ci
Copy-Item .env.example .env
```

Use two terminals from the repository root:

```powershell
# Terminal 1
cd backend
mvn spring-boot:run
```

```powershell
# Terminal 2
npm run dev
```

Open **http://127.0.0.1:5173/**. Vite proxies `/api` to Java on port 8080. Local development uses an H2 database persisted under `backend/.data`; no Docker or database account is required. PostgreSQL is the production database.

The development-only student account is `demo@1on1.local` with password `learnwith1on1`. It has no fabricated achievements. This account is not seeded in the production profile.

## Configure real services

Edit the ignored root `.env` locally and restart Java. Never paste keys into chat, commit them, or put them in `VITE_` variables. Rotate any credential that has already been shared publicly.

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Your Google AI Studio key. Use a replacement if a previous key was exposed. |
| `GEMINI_MODEL` | Defaults to `gemini-2.5-flash`; change to an available structured-output model in your Google project. Free-tier quotas depend on the project/model. |
| `JUDGE0_API_KEY` | Hosted Judge0/RapidAPI credential for real sandboxed execution. |
| `JUDGE0_URL`, `JUDGE0_RAPIDAPI_HOST` | Hosted judge URL/host. Java never executes student code on its own host. |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Optional initial content-editor account. Use a new email and a password of at least 12 characters. Public registration always creates students. Existing accounts are never silently promoted. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_TLS` | Password-reset email. Use Mailpit locally or configure authenticated SMTP. |
| `APP_BASE_URL` | Public frontend URL used in reset links. |
| `DATABASE_URL`, `DATABASE_USERNAME`, `DATABASE_PASSWORD` | Optional local PostgreSQL / required production PostgreSQL settings. |
| `POSTGRES_PASSWORD` | Password for the PostgreSQL container in the provided compose setup. It does not change the local H2 connection. |

With no AI key, authored notebooks and deterministic experiments work, and the tutor reports that configuration is missing. With no Judge0 key, the editor and draft saving work, while Run/Submit report unavailability. No fake AI responses or accepted submissions are generated. Keys are never sent to the browser.

Initial usage limits are 30 AI requests and 50 execution actions per user per UTC day, plus shared daily ceilings of 300 AI and 2,000 execution actions. A hosted judge action can execute several tests and consume multiple provider requests. Provider limits may be lower. Usage is visible to administrators.

## What is implemented

- 24 authored lessons, twelve reusable visual families, three connected learning paths.
- 60 original problems across arrays, strings, hashing, sliding windows, sorting, recursion, trees, heaps, graphs, and DP; 420 public/hidden judge fixtures.
- Play/pause, step controls, editable inputs, speed, structured state, synchronized pseudocode, and readable trace transcripts.
- Contextual Gemini tutoring, progressive authored hints, code feedback, validated AI-created experiments, saved explanations and experiments.
- Java/Python/C++ Monaco editor, local editor workers, persistent drafts, real asynchronous Judge0 adapter, deterministic output comparison and private hidden cases.
- Accounts, onboarding, reset-email flow, private notes, bookmarks, revision queue, practice plans, progress, opt-in study cohorts.
- Public LeetCode profile connector with cached snapshots, recent accepted problems, manual refresh cooldown, six-hour scheduled refresh, and explicit stale/unavailable states.
- Administrator content editing, JSON import/export, draft/publication controls, and usage overview.
- Algorithm evidence view with seeded comparative benchmarks and JSON export.
- Responsive light/dark/system themes, keyboard navigation, focus states, text alternatives, and reduced-motion styles.

## Algorithms assessed

All three are original Java implementations under `backend/src/main/java/com/oneonone/algorithms`:

| Technique | Application use | Analysis |
| --- | --- | --- |
| Trie (Unit 4) | A cached, immutable title/topic prefix index rebuilt after content changes. | Prefix traversal plus bounded output; indexing cost and memory are separate. |
| Greedy set cover (Unit 5) | Compact practice sets covering selected topics, excluding solved problems. | Unit-cost approximation; infeasible coverage is reported. Daily grouping is separate. |
| Randomized Quickselect (Unit 6 / CO5) | Cohort activity-score quartile thresholds without complete sorting. | Expected O(n), worst O(n²); three-way partitioning handles duplicates; inputs are copied. |

The full explanation, pseudocode, test matrix, and performance methodology are in [the technical report](docs/TECHNICAL_REPORT.md). Use `/evidence` after signing in to generate machine-specific measurements. Benchmarks are not invented marketing claims.

## Verify

```powershell
# Java algorithms, traces, all reference solutions, and runner adapter contracts
mvn -f backend/pom.xml test

# TypeScript production build and API-boundary unit tests
npm run build
npm test

# Real HTTP integration checks, with Java running
python scripts/verify_api.py

# Browser flows and responsive screenshots, with both servers running
npx playwright install chromium
npm run test:e2e
```

The judge adapter contract tests use a clearly isolated local fixture server; they do not claim that the paid/hosted provider was contacted. Live Gemini, hosted execution, SMTP delivery and LeetCode availability must be checked with working credentials/network access. Browser tests capture desktop/mobile evidence under the ignored `.impeccable/review` directory.

Regenerate deterministic authored content with `python scripts/generate_content.py`. Content seeds update unedited built-in records on startup; changes saved through the admin UI are marked as edited and preserved. Retired, unedited built-ins are archived, not deleted. Take database backups before content or schema upgrades.

## Team development

One Java service owns business logic. Frontend API contracts are in `src/types.ts` and documented in [API.md](docs/API.md).

- **Frontend/notebooks:** `src`, tokens in `src/styles.css`, browser tests.
- **Java/algorithms/data:** backend modules, SQL migrations, JUnit tests, benchmarks.
- **AI/execution/integrations:** Gemini/LeetCode/Judge0 adapters, content tooling, and service error handling.

Share content and review responsibilities. Each student should commit their own work and record actual contributions in the proposal/report. The initial implementation was assisted by Codex; do not represent it as independently authored student work. Understand and be prepared to explain the Java implementations during the viva.

## Container deployment

The complete Java architecture is packaged for a Java/container host. It is not a frontend-only static deployment.

```powershell
# Configure the ignored .env first; set a strong DATABASE_PASSWORD
docker compose up --build -d
```

Open http://localhost:8088. Nginx serves the frontend and proxies Java; PostgreSQL uses a named volume. Mailpit is available locally on http://localhost:8025 for reset emails when the compose SMTP default is used. See [deployment instructions](docs/DEPLOYMENT.md) before exposing this to the internet.

Do not use `docker compose down -v` unless you intend to delete stored data. Set `COOKIE_SECURE=true`, a real `APP_BASE_URL`, proper SMTP, and TLS on the public reverse proxy for production. Back up PostgreSQL and keep service keys only in the hosting secret store.

## Academic package

- [Project proposal](docs/PROPOSAL.md)
- [Technical report](docs/TECHNICAL_REPORT.md)
- [API and data contracts](docs/API.md)
- [Demonstration script and requirement mapping](docs/DEMO.md)
- [Validation record](docs/VALIDATION.md)

Add the actual two/three team members' names, IDs, and individual contributions before submission. Faculty determines project acceptance and the final assessment.
