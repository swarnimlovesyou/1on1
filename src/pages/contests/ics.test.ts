import { describe, expect, it } from "vitest";
import { countdown, icsFor } from "./ics";

describe("icsFor", () => {
  it("writes one UTC event with the contest's link, CRLF line endings and escaped text", () => {
    const ics = icsFor({ id: "atcoder-abc485", title: "AtCoder Beginner Contest 485, Div; A", start: "2026-11-21T12:00:00Z", durationMinutes: 100, url: "https://atcoder.jp/contests/abc485", platform: "AtCoder" }, new Date("2026-11-17T00:00:00Z"));
    const lines = ics.split("\r\n");
    expect(lines[0]).toBe("BEGIN:VCALENDAR");
    expect(lines).toContain("DTSTART:20261121T120000Z");
    expect(lines).toContain("DTEND:20261121T134000Z");
    expect(lines).toContain("SUMMARY:AtCoder Beginner Contest 485\\, Div\\; A");
    expect(lines).toContain("URL:https://atcoder.jp/contests/abc485");
    expect(lines).toContain("UID:atcoder-abc485@1on1");
    expect(lines).toContain("DTSTAMP:20261117T000000Z");
    expect(lines.at(-2)).toBe("END:VCALENDAR");
    expect(ics.endsWith("\r\n")).toBe(true);
  });
});

describe("countdown", () => {
  const c = { id: "x", platform: "Codeforces", title: "R", start: "2026-11-21T12:00:00Z", durationMinutes: 120, url: "u" };
  const at = (iso: string) => new Date(iso).getTime();
  it("counts down in days, hours or minutes, then says live, then ended", () => {
    expect(countdown(c, at("2026-11-18T08:00:00Z"))).toBe("in 3 d 4 h");
    expect(countdown(c, at("2026-11-21T09:15:00Z"))).toBe("in 2 h 45 min");
    expect(countdown(c, at("2026-11-21T11:20:00Z"))).toBe("in 40 min");
    expect(countdown(c, at("2026-11-21T13:00:00Z"))).toBe("live now");
    expect(countdown(c, at("2026-11-21T14:00:00Z"))).toBe("ended");
  });
});

describe("calendar polish", () => {
  const long = { id: "atcoder-x", platform: "AtCoder", title: "AtCoder Regular Contest 999 (Sponsored by a Very Long Company Name Incorporated, Div. 1 and Div. 2)", start: "2026-11-21T12:00:00Z", durationMinutes: 100, url: "https://atcoder.jp/contests/x" };
  it("folds lines longer than 75 octets so strict calendar apps accept them", () => {
    const ics = icsFor(long, new Date("2026-11-17T00:00:00Z"));
    for (const line of ics.split("\r\n")) expect(new TextEncoder().encode(line).length).toBeLessThanOrEqual(75);
    const unfolded = ics.replace(/\r\n /g, "");
    expect(unfolded).toContain("SUMMARY:AtCoder Regular Contest 999 (Sponsored by a Very Long Company Name Incorporated\\, Div. 1 and Div. 2)");
  });
  it("says starting now in the last minute instead of in 0 min", () => {
    expect(countdown(long, new Date("2026-11-21T11:59:40Z").getTime())).toBe("starting now");
  });
});
