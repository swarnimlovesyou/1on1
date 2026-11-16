import type { Scene } from "../../types";
type Preset = {
  label: string;
  input?: string;
  target?: number;
  words?: string;
  seed?: number;
};
const examples: Record<string, Preset[]> = {
  complexity: [
    { label: "Double the input", target: 16 },
    { label: "Zero work", target: 0 },
  ],
  arrays: [
    { label: "Negative and repeated values", input: "-2,4,-2,0" },
    { label: "Empty array", input: "" },
  ],
  strings: [
    { label: "Repeated characters", words: "aab" },
    { label: "Empty string", words: "" },
  ],
  hashing: [
    { label: "Collision without equality", input: "2,6,10,2" },
    { label: "Empty set", input: "" },
  ],
  "prefix-sums": [
    { label: "Negative values", input: "-2,3,-1,4", words: "1,4" },
    { label: "Empty range", input: "2,1,5", words: "1,1" },
  ],
  "variable-window": [
    { label: "Shrink more than once", words: "abba" },
    { label: "Repeated single character", words: "aaaa" },
  ],
  intervals: [
    { label: "Touching closed endpoints", input: "1,2,2,3,6,6" },
    { label: "Nested intervals", input: "1,9,2,3,4,5" },
  ],
  matrices: [
    { label: "Rectangular transpose", input: "1,2,3,4,5,6", target: 3 },
    { label: "Single row", input: "1,2,3,4", target: 4 },
  ],
  graphs: [
    { label: "Isolated vertices", input: "0,1", target: 4 },
    { label: "Loops and parallel edges", input: "0,0,0,1,0,1", target: 3 },
  ],
  "two-pointers": [
    { label: "Repeated values form a pair", input: "2,2,3,6", target: 4 },
    { label: "No matching pair", input: "1,3,5", target: 20 },
  ],
  "sliding-window": [
    { label: "All negative values", input: "-4,-2,-3", target: 2 },
    { label: "Entire input is one window", input: "2,1,5", target: 3 },
  ],
  "binary-search": [
    { label: "Target absent", input: "1,3,5,7", target: 4 },
    { label: "Duplicate keys", input: "1,2,2,2,4", target: 2 },
  ],
  "merge-sort": [
    { label: "Negative and equal values", input: "4,-2,4,0,1" },
    { label: "Already ordered", input: "1,2,3,4" },
  ],
  "quick-sort": [
    { label: "Reverse ordered", input: "7,6,5,4,3,2,1" },
    { label: "Equal keys", input: "3,3,3,3" },
  ],
  quickselect: [
    {
      label: "Same values, a new pivot seed",
      input: "4,2,7,1,3,6",
      target: 3,
      seed: 81,
    },
    {
      label: "Repeated order statistic",
      input: "2,2,2,4,5",
      target: 2,
      seed: 42,
    },
  ],
  "linked-list": [
    { label: "Equal values, different nodes", input: "2,1,2" },
    { label: "One node", input: "7" },
  ],
  stack: [
    { label: "A short LIFO example", input: "1,2,3" },
    { label: "Repeated values", input: "2,2,1" },
  ],
  queue: [
    { label: "Compare with the stack", input: "1,2,3" },
    { label: "One queued value", input: "7" },
  ],
  recursion: [
    { label: "Base case only", target: 0 },
    { label: "Watch five suspended calls", target: 5 },
  ],
  backtracking: [
    { label: "Two choices", input: "1,2" },
    { label: "Three choices", input: "1,2,3" },
  ],
  bst: [
    { label: "Sorted insertion creates a chain", input: "1,2,3,4,5" },
    { label: "Duplicate keys are ignored", input: "8,3,8,3,10" },
  ],
  avl: [
    { label: "Left-right rotation", input: "30,10,20" },
    { label: "Right-left rotation", input: "10,30,20" },
  ],
  "tree-traversal": [
    {
      label: "General tree with equal values",
      input: "1,1,1",
      words: "inorder",
    },
    { label: "Missing child slots", input: "4,2,7,null,3,6", words: "inorder" },
  ],
  heap: [
    { label: "Bubble a new maximum", input: "2,1,3,9" },
    { label: "Duplicate priorities", input: "4,4,2,4" },
  ],
  bfs: [
    { label: "Three-vertex frontier", input: "1,2,3" },
    { label: "Eight-vertex layers", input: "1,2,3,4,5,6,7,8" },
  ],
  dfs: [
    { label: "Compare this graph with BFS", input: "1,2,3,4,5,6" },
    { label: "A short recursive path", input: "1,2,3" },
  ],
  dijkstra: [
    { label: "Different nonnegative costs", input: "7,1,6,2,5,3" },
    { label: "Small weighted graph", input: "1,2,3,4" },
  ],
  "max-flow": [
    { label: "Inspect residual capacity", input: "7,1,6,2,5,3" },
    { label: "Small flow network", input: "1,2,3,4" },
  ],
  memoization: [
    { label: "Cache reused by repeated calls", target: 8 },
    { label: "Known zero base case", target: 0 },
  ],
  tabulation: [
    { label: "Base cells only", target: 1 },
    { label: "Build F(8)", target: 8 },
  ],
  trie: [
    { label: "Shared prefix and word boundary", words: "a,an,ant,all" },
    { label: "One word prefixes another", words: "tree,trees,trie" },
  ],
  "set-cover": [
    { label: "An infeasible goal", words: "Arrays,Unknown" },
    { label: "Overlapping topic goals", words: "Arrays,Hashing,DP" },
  ],
  "bloom-filter": [
    { label: "An actual false positive", words: "a | q" },
    { label: "Confirm an inserted word", words: "tree,graph | tree" },
  ],
};
export function presets(scene: Scene) {
  return (examples[scene.algorithm] ?? []).map(({ label, ...overrides }) => ({
    label,
    scene: { ...scene, ...overrides },
  }));
}
