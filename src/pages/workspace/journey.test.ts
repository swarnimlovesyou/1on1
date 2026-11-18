import { describe, expect, it } from "vitest";
import { forecast, frontier, latestPlan } from "./Journey";
import type { MapConcept, Plan } from "../../types";

const c = (id: string, state: MapConcept["state"], prerequisites: string[] = [], order = 0) =>
  ({ id, title: id, order, prerequisites, lessonIds: [], problemIds: [], state, explored: state !== "new" }) as unknown as MapConcept;

describe("journey", () => {
  it("the frontier is unstarted concepts whose prerequisites all have evidence", () => {
    const got = frontier([c("a", "passed"), c("b", "new", ["a"], 2), c("c", "new", ["b"], 3), c("d", "new", [], 1)]);
    expect(got.map((x) => x.id)).toEqual(["d", "b"]);
  });
  it("the latest plan is the newest by creation, not the last by id", () => {
    const plans = [{ id: "plan-z", createdAt: "2026-11-01" }, { id: "plan-a", createdAt: "2026-11-15" }] as unknown as Plan[];
    expect(latestPlan(plans)?.id).toBe("plan-a");
  });
  it("a plan forecast counts what is left, what is late and when it ends", () => {
    const t = (date: string, done: boolean) => ({ id: date, kind: "problem", problemId: "p", adds: [], date, done, doneAt: null });
    const plan = { tasks: [t("2026-11-10", true), t("2026-11-12", false), t("2026-11-20", false)] } as unknown as Plan;
    expect(forecast(plan, "2026-11-18")).toEqual({ done: 1, total: 3, overdue: 1, finish: "2026-11-20" });
  });
});
