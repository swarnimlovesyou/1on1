import { expect, it } from "vitest";
import { clock, remainingFrom, timeUsed } from "./mockTime";

it("counts down from the server's remaining time, not the browser's clock", () => {
  // received with 120 s left; 30 s later on this machine, whatever its clock says about the deadline
  expect(remainingFrom(120, 1_000_000, 1_030_000)).toBe(90);
  expect(remainingFrom(120, 1_000_000, 1_200_000)).toBe(0);
});

it("reports time used up to the finish, capped at the deadline", () => {
  const startedAt = "2026-11-17T10:00:00Z", deadline = "2026-11-17T11:00:00Z";
  expect(timeUsed({ startedAt, deadline, finishedAt: "2026-11-17T10:42:30Z" })).toBe("42:30");
  expect(timeUsed({ startedAt, deadline })).toBe("60:00");
  expect(clock(61)).toBe("1:01");
});
