import { describe, expect, it } from "vitest";
import { toSubmission } from "./browserPython";

describe("browser Python runs", () => {
  it("show output, errors and time limits in the usual result shape, never as graded", () => {
    const ok = toSubmission({ stdout: "5\n", stderr: "", ms: 12, timedOut: false }, "problem-x", "print(5)", "");
    expect(ok.status).toBe("RAN_IN_BROWSER");
    expect(ok.official).toBe(false);
    expect(ok.id.startsWith("browser-")).toBe(true);
    expect(ok.results[0].actual).toBe("5\n");
    expect(toSubmission({ stdout: "", stderr: "ZeroDivisionError", ms: 1, timedOut: false }, "p", "1/0", "").status).toBe("RUNTIME_ERROR");
    expect(toSubmission({ stdout: "", stderr: "", ms: 10000, timedOut: true }, "p", "while True: pass", "").status).toBe("TIME_LIMIT_EXCEEDED");
  });
});
