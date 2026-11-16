/** Six algorithm families. Each gives its lessons and problems one colour and mark across the app. */
export type FamilyId = "foundations" | "searching" | "linear" | "recursion" | "trees" | "graphs";

export const FAMILIES: Record<FamilyId, { label: string }> = {
  foundations: { label: "Foundations" },
  searching: { label: "Searching and sorting" },
  linear: { label: "Linear structures" },
  recursion: { label: "Recursion and DP" },
  trees: { label: "Trees and heaps" },
  graphs: { label: "Graphs" },
};

const CONCEPTS: Record<string, FamilyId> = {
  complexity: "foundations", arrays: "foundations", strings: "foundations", hashing: "foundations",
  sorting: "searching", "prefix-sums": "searching", "two-pointers": "searching", "fixed-window": "searching",
  "variable-window": "searching", "binary-search": "searching", intervals: "searching",
  matrices: "linear", "linked-lists": "linear", stacks: "linear", queues: "linear",
  recursion: "recursion", backtracking: "recursion", "dynamic-programming": "recursion",
  "binary-trees": "trees", bst: "trees", heaps: "trees",
  graphs: "graphs", bfs: "graphs", dfs: "graphs",
};

// advanced lessons have no concept; a trie is a tree, quickselect partitions, Bloom filters and set cover build on sets
const LESSONS: Record<string, FamilyId> = {
  "lesson-avl": "trees", "lesson-trie": "trees", "lesson-dijkstra": "graphs", "lesson-max-flow": "graphs",
  "lesson-quickselect": "searching", "lesson-bloom-filter": "foundations", "lesson-set-cover": "foundations",
};

const TOPICS: Record<string, FamilyId> = {
  Arrays: "foundations", Strings: "foundations", Hashing: "foundations",
  "Probabilistic structures": "foundations", "Greedy algorithms": "foundations",
  Sorting: "searching", Search: "searching", "Sliding window": "searching", "Two pointers": "searching", Randomization: "searching",
  "Stacks & queues": "linear",
  Recursion: "recursion", "Dynamic programming": "recursion",
  Trees: "trees", Heaps: "trees", "Text search": "trees",
  Graphs: "graphs",
};

export function familyOfLesson(lesson: { id: string; conceptId?: string }): FamilyId {
  return CONCEPTS[lesson.conceptId?.replace("concept-", "") ?? ""] ?? LESSONS[lesson.id] ?? "foundations";
}

export function familyOfProblem(topics: string[]): FamilyId {
  return topics.map((t) => TOPICS[t]).find(Boolean) ?? "foundations";
}

export function familyVar(id: FamilyId): string {
  return `var(--family-${id})`;
}

/** Inline style that gives a page root its family colour; `.has-family` descendants (the experiment) read it. */
export function familyStyle(id: FamilyId): Record<string, string> {
  return { "--family": familyVar(id), "--family-wash": `var(--family-${id}-wash)` };
}
