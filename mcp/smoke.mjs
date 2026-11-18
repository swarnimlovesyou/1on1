// Manual smoke check against a running 1on1 (npm run dev:core): node smoke.mjs
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
const client = new Client({ name: "smoke", version: "1.0.0" });
await client.connect(new StdioClientTransport({ command: process.execPath, args: ["server.mjs"] }));
for (const [name, args] of [["search_questions", { query: "two sum", source: "LeetCode" }], ["upcoming_contests", {}], ["get_drill", { topic: "percentages" }]]) {
  const r = await client.callTool({ name, arguments: args });
  console.log(`--- ${name}${r.isError ? " (error)" : ""}\n` + r.content.map((c) => c.text).join("\n").split("\n").slice(0, 4).join("\n"));
}
await client.close();
