import { describe, expect, it } from "vitest";
import { streak, weekCount, weeks } from "./activity";

const today = new Date("2026-11-18T10:00:00Z");

describe("activity", () => {
  it("counts consecutive active days ending today or yesterday", () => {
    expect(streak({ "2026-11-18": 2, "2026-11-17": 1, "2026-11-16": 4, "2026-11-14": 1 }, today)).toBe(3);
    expect(streak({ "2026-11-17": 1, "2026-11-16": 1 }, today)).toBe(2);
    expect(streak({ "2026-11-15": 1 }, today)).toBe(0);
    expect(streak({}, today)).toBe(0);
  });
  it("sums the last seven days, today included", () => {
    expect(weekCount({ "2026-11-18": 2, "2026-11-12": 3, "2026-11-11": 9 }, today)).toBe(5);
  });
  it("lays out 12 weeks of days ending today, oldest first", () => {
    const grid = weeks({ "2026-11-18": 2 }, today, 12);
    expect(grid).toHaveLength(12);
    expect(grid.every((w) => w.length === 7)).toBe(true);
    expect(grid.at(-1)!.at(-1)).toEqual({ date: "2026-11-18", count: 2 });
    expect(grid[0][0].date).toBe("2026-08-27");
  });
});
