import { describe, expect, it } from "vitest";
import { familyOfLesson, familyOfProblem, familyVar, FAMILIES } from "./families";

describe("algorithm families", () => {
  it("maps every core concept to its family", () => {
    const expected: Record<string, string[]> = {
      foundations: ["complexity", "arrays", "strings", "hashing"],
      searching: ["sorting", "prefix-sums", "two-pointers", "fixed-window", "variable-window", "binary-search", "intervals"],
      linear: ["matrices", "linked-lists", "stacks", "queues"],
      recursion: ["recursion", "backtracking", "dynamic-programming"],
      trees: ["binary-trees", "bst", "heaps"],
      graphs: ["graphs", "bfs", "dfs"],
    };
    for (const [family, concepts] of Object.entries(expected))
      for (const c of concepts)
        expect(familyOfLesson({ id: "lesson-x", conceptId: "concept-" + c }), c).toBe(family);
  });

  it("maps the advanced lessons that have no concept", () => {
    expect(familyOfLesson({ id: "lesson-avl" })).toBe("trees");
    expect(familyOfLesson({ id: "lesson-trie" })).toBe("trees");
    expect(familyOfLesson({ id: "lesson-dijkstra" })).toBe("graphs");
    expect(familyOfLesson({ id: "lesson-max-flow" })).toBe("graphs");
    expect(familyOfLesson({ id: "lesson-quickselect" })).toBe("searching");
    expect(familyOfLesson({ id: "lesson-bloom-filter" })).toBe("foundations");
    expect(familyOfLesson({ id: "lesson-set-cover" })).toBe("foundations");
  });

  it("gives a problem the family of its first topic that maps", () => {
    expect(familyOfProblem(["Arrays", "Two pointers"])).toBe("foundations");
    expect(familyOfProblem(["Two pointers", "Arrays"])).toBe("searching");
    expect(familyOfProblem(["Stacks & queues"])).toBe("linear");
    expect(familyOfProblem(["Dynamic programming"])).toBe("recursion");
    expect(familyOfProblem(["Heaps"])).toBe("trees");
    expect(familyOfProblem(["Graphs"])).toBe("graphs");
    for (const t of ["Strings", "Hashing", "Probabilistic structures", "Greedy algorithms"]) expect(familyOfProblem([t]), t).toBe("foundations");
    for (const t of ["Sorting", "Search", "Sliding window", "Two pointers", "Randomization"]) expect(familyOfProblem([t]), t).toBe("searching");
    expect(familyOfProblem(["Recursion"])).toBe("recursion");
    expect(familyOfProblem(["Trees"])).toBe("trees");
    expect(familyOfProblem(["Text search"])).toBe("trees");
  });

  it("falls back to foundations for unknown or missing topics", () => {
    expect(familyOfProblem(["Quantum"])).toBe("foundations");
    expect(familyOfProblem([])).toBe("foundations");
  });

  it("names the CSS colour and labels every family", () => {
    expect(familyVar("graphs")).toBe("var(--family-graphs)");
    expect(FAMILIES.searching.label).toBe("Searching and sorting");
    expect(Object.keys(FAMILIES)).toEqual(["foundations", "searching", "linear", "recursion", "trees", "graphs"]);
  });
});
