export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}
export interface Scene {
  algorithm: string;
  input: string;
  target: number;
  words?: string;
}
export interface Lesson {
  id: string;
  kind: string;
  order: number;
  title: string;
  subtitle: string;
  topics: string[];
  difficulty: string;
  minutes: number;
  body: string;
  invariant: string;
  pitfall: string;
  timeComplexity: string;
  spaceComplexity: string;
  code: string[];
  experiment: Scene;
  checkpoint: {
    question: string;
    options: string[];
    answer: number;
    explanation: string;
  };
  prerequisites: string[];
}
export interface Problem {
  id: string;
  kind: string;
  order: number;
  title: string;
  topics: string[];
  difficulty: string;
  description: string;
  constraints: string;
  inputFormat: string;
  outputFormat: string;
  samples: { input: string; output: string }[];
  editorial: string;
  reference?: string;
  complexity: string;
  hints: string[];
}
export interface Path {
  id: string;
  title: string;
  description: string;
  lessons: string[];
  color: string;
}
export interface Note {
  experiment?: Scene;
  id: string;
  title: string;
  text: string;
  lesson: string;
  reviewed: boolean;
  createdAt: string;
}
export interface Plan {
  id: string;
  title: string;
  topics: string[];
  selected: { id: string; adds: string[] }[];
  uncovered: string[];
  perDay: number;
  method: string;
}
export interface Submission {
  id: string;
  problem: string;
  code: string;
  language: string;
  official: boolean;
  status: string;
  createdAt: string;
  message?: string;
  results: {
    index: number;
    status: string;
    public: boolean;
    input?: string;
    actual?: string;
    expected?: string;
    message?: string;
    time: string;
    memory: string;
  }[];
}
export interface Progress {
  completed: string[];
  solved: string[];
  bookmarks: string[];
  activity: Record<string, number>;
  checkpoints?: Record<string, { answer: number; correct: boolean }>;
  resumeLesson?: string;
  resumeStep?: number;
  level?: string;
  goal?: string;
  language?: string;
  onboarded?: boolean;
  notes: Note[];
  plans: Plan[];
  drafts: { problem: string; language: string; code: string }[];
  submissions: Submission[];
}
export interface Tree {
  value: number;
  left: Tree | null;
  right: Tree | null;
}
export interface Step {
  id: string;
  array: number[];
  active: number[];
  variables: Record<string, unknown>;
  text: string;
  line: number;
  tree?: Tree;
  words?: string[];
  topics?: string[];
  vertexCount?: number;
  edges?: { from: number; to: number; weight: number }[];
}
export interface Trace {
  version: number;
  algorithm: string;
  family: string;
  steps: Step[];
  result: Step;
  input: Scene;
}
export const emptyProgress: Progress = {
  completed: [],
  solved: [],
  bookmarks: [],
  activity: {},
  notes: [],
  plans: [],
  drafts: [],
  submissions: [],
};
