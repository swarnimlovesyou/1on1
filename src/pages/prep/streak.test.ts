import { describe, expect, it } from "vitest";
import { nextStreak } from "./streak";

describe("nextStreak", () => {
  it("grows on a correct answer and resets on a wrong one", () => {
    expect(nextStreak(2, true)).toBe(3);
    expect(nextStreak(5, false)).toBe(0);
    expect(nextStreak(0, true)).toBe(1);
  });
});
