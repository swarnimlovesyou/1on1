# 1on1 MCP adapter

A thin [Model Context Protocol](https://modelcontextprotocol.io) server over 1on1's public learning API, so an assistant
such as Claude Desktop can use the library, traces, question bank, contests, the performance lab and drills.

It owns no logic. Every answer comes from the Java services, so traces and grading stay authoritative there. It reads
public data only: nothing here can see or change a learner's account (pairing a signed-in session is a separate step that
is not built).

## Tools

| Tool | What it does |
| --- | --- |
| `search_library` | Search lessons and 1on1's own problems |
| `get_lesson` | Read a lesson's idea, invariant, common mistake, complexity and questions (no answers) |
| `run_trace` | Run an algorithm in the Java trace engine and return each step's narration |
| `search_questions` | Search the question bank with source, difficulty, company and sort filters |
| `upcoming_contests` | Upcoming Codeforces and AtCoder contests |
| `measure_growth` | The performance lab's step counts and closest growth curve |
| `get_drill` / `check_drill` | A generated aptitude or reasoning question, and checking an answer |

## Run

```bash
cd mcp && npm install
```

Start 1on1 (`npm run dev:core` from the repo root), then add this to Claude Desktop's `claude_desktop_config.json`,
with the path to this folder:

```json
{
  "mcpServers": {
    "1on1": { "command": "node", "args": ["C:/path/to/1on1-final/mcp/server.mjs"] }
  }
}
```

Set `ONEONONE_API` to point at another instance (default `http://127.0.0.1:8080/api/v1`).

## Check

- `npm test`: drives the server through the MCP client against a stub API (tool list, filters, CSRF on traces, errors).
- `node smoke.mjs`: calls four tools against a running 1on1.

Only the stdio transport and Claude Desktop-style clients are covered; Codex and ChatGPT were not tried.
