# 1on1 MCP adapter

A thin [Model Context Protocol](https://modelcontextprotocol.io) server over 1on1's learning API, so an assistant such
as Claude Desktop can use the library, traces, question bank, contests and drills, and, once a learner pairs it, that
learner's study context and notes.

It owns no logic. Every answer comes from the Java services, so traces and grading stay authoritative there.

## Tools

Public (always available):

| Tool | What it does |
| --- | --- |
| `search_library` | Search lessons and 1on1's own problems |
| `get_lesson` | Read a lesson's idea, invariant, common mistake, complexity and questions (no answers) |
| `run_trace` | Run an algorithm in the Java trace engine and return each step's narration (`words` takes `text\|pattern` for `kmp`, `rabin-karp`, `lcs`) |
| `search_questions` | Search the question bank with source, difficulty, company and sort filters |
| `upcoming_contests` | Upcoming Codeforces and AtCoder contests |
| `get_drill` / `check_drill` | A generated aptitude or reasoning question, and checking an answer |

Paired (only with `ONEONONE_TOKEN`):

| Tool | What it does |
| --- | --- |
| `my_context` | The learner's next step, reviews due, concept progress and last lesson |
| `search_my_notes` | Search the learner's notes |
| `save_note` | Save a note to the learner's notebook |
| `search_my_sources` | Search the PDFs the learner uploaded, with source and page for citing |

## Pairing

In 1on1, open **Settings → Connect an assistant**, name the device and press **Make a token**. The token is shown once
and stored only as a hash. It lets the assistant read that learner's context and notes and save notes; it cannot grade,
change the account or see other learners. **Revoke** stops it immediately. Up to five pairings per learner.

## Run

```bash
cd mcp && npm install
```

Start 1on1 (`npm run dev:core` from the repo root), then add this to Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "1on1": {
      "command": "node",
      "args": ["C:/path/to/1on1-final/mcp/server.mjs"],
      "env": { "ONEONONE_TOKEN": "1on1_… (optional, from Settings)" }
    }
  }
}
```

Set `ONEONONE_API` to point at another instance (default `http://127.0.0.1:8080/api/v1`).

## Skills

`skills/` holds three teaching skills in the standard `SKILL.md` format, written to use these tools and 1on1's teaching
policy (mental model first, one question at a time, never invent a trace or a grade):

- `concept-coach`: teach a concept from the lesson, its invariant and a real trace.
- `exam-practice`: drills graded by 1on1 and bank questions by topic or company, links only.
- `debugging-guide`: find a bug from the smallest failing input and the reference trace.

For Claude Desktop or Claude Code, copy a skill folder into your skills directory. Other clients can use the
`SKILL.md` body as a system prompt.

## Check

- `npm test`: drives the server through the MCP client against a stub API (tool lists with and without a token,
  filters, CSRF on traces, bearer token on paired calls, errors).
- `node smoke.mjs`: calls four tools against a running 1on1.

Only the stdio transport and Claude Desktop-style clients are covered; Codex and ChatGPT were not tried, and the skills
have not been run in a live assistant.
