import { useReducedMotion } from "motion/react";
import type { Step } from "../../types";
import FoundationModel from "./FoundationModels";
import StructureModel from "./StructureModels";
import GraphModel from "./GraphModel";
import AdvancedModel from "./AdvancedModels";

export default function SceneCanvas({
  step,
  algorithm,
  duration,
  instant,
}: {
  step: Step;
  family?: string;
  algorithm: string;
  duration: number;
  instant: boolean;
}) {
  const reduced = useReducedMotion();
  const timing = {
    duration: instant || reduced ? 0 : Math.min(0.45, duration),
    ease: [0.16, 1, 0.3, 1] as const,
  };
  const props = { step, algorithm, timing };
  if (["bfs", "dfs", "dijkstra", "max-flow", "graphs"].includes(algorithm))
    return <GraphModel {...props} />;
  if (
    [
      "linked-list",
      "stack",
      "queue",
      "recursion",
      "backtracking",
      "bst",
      "avl",
      "tree-traversal",
      "heap",
      "trie",
      "memoization",
      "tabulation",
    ].includes(algorithm)
  )
    return <StructureModel {...props} />;
  if (["bloom-filter", "set-cover"].includes(algorithm))
    return <AdvancedModel {...props} />;
  return <FoundationModel {...props} />;
}
