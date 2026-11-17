/** Ticks are kept in order without duplicates. */
export function toggle(done: string[], id: string, on: boolean) {
  const rest = done.filter((x) => x !== id);
  return on ? [...rest, id] : rest;
}

// NeetCode pattern names mapped to the 1on1 lesson that teaches the idea; patterns without one get no link.
const LESSONS: Record<string, string> = {
  "Arrays & Hashing": "lesson-hashing",
  "Two Pointers": "lesson-two-pointers",
  "Sliding Window": "lesson-sliding-window",
  Stack: "lesson-stack",
  "Binary Search": "lesson-binary-search",
  "Linked List": "lesson-linked-list",
  Trees: "lesson-tree-traversal",
  Tries: "lesson-trie",
  "Heap / Priority Queue": "lesson-heap",
  Backtracking: "lesson-backtracking",
  Graphs: "lesson-bfs",
  "Advanced Graphs": "lesson-dijkstra",
  "1-D Dynamic Programming": "lesson-memoization",
  "2-D Dynamic Programming": "lesson-tabulation",
  Intervals: "lesson-intervals",
  "Math & Geometry": "lesson-matrices",
};

export function lessonForPattern(pattern: string) {
  return LESSONS[pattern] ?? null;
}
