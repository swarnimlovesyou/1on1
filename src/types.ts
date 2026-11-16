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
  seed?: number;
}
export interface LessonBlock {
  id: string;
  kind: "explanation" | "code";
  title: string;
  text: string;
  lines: string[];
}
export interface Challenge {
  id: string;
  kind: "prediction" | "pattern" | "manipulation" | "dry-run";
  title: string;
  prompt: string;
  options?: string[];
  fields?: { key: string; label: string }[];
  scene?: Scene;
  traceStep?: number;
  hint?: string;
}
export interface AttemptResult {
  id: string;
  challengeId: string;
  kind: Challenge["kind"];
  correct: boolean;
  feedback: string;
  explanation: string;
  saved: boolean;
}
export interface StudyContext {
  version: 1;
  lesson: string;
  scene?: Scene;
  step: number;
  section: string;
  codeRevision: string;
  updatedAt?: string;
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
  blocks?: LessonBlock[];
  challenges: Challenge[];
  referenceJourney?: boolean;
  linkedProblems?: string[];
  invariant: string;
  pitfall: string;
  timeComplexity: string;
  spaceComplexity: string;
  code: string[];
  experiment?: Scene;
  teaching?: CurriculumConcept;
  conceptId?: string;
  branch?: "core" | "advanced";
  interactiveStatus?: "existing-limited" | "specification-only";
  checkpoint: {
    question: string;
    options: string[];
    id: string;
  };
  prerequisites: string[];
}
export interface CurriculumApplication {
  questionId: string;
  role: "introduction" | "transfer";
  connection: string;
  additionalPrerequisites: string[];
  perspective: string;
}
export interface CurriculumConcept {
  id: string;
  title: string;
  order: number;
  prerequisites: string[];
  lessonIds: string[];
  objectives: string[];
  mentalModel: string;
  workedExample: string;
  invariant: string;
  commonMistake: string;
  complexity: { time: string; space: string; assumptions: string };
  java: {
    language: "java";
    implementation: string;
    source: string;
    lineAnnotations: { line: number; explanation: string }[];
  };
  visualization: {
    exampleInput: string;
    expectedStates: string[];
    manipulation: string;
    limits: string;
    interactiveStatus: string;
    gaps: string[];
    scene?: Scene;
  };
  applications: CurriculumApplication[];
  contentStatus: "authored";
  practiceStatus: "planned-phase-2";
}
export interface QuestionReference {
  id: string;
  title: string;
  kind: "external-reference" | "original-exercise" | "local-problem-reference";
  canonicalUrl: string | null;
  localProblemId?: string | null;
  conceptTags: string[];
  progressiveHints: string[];
  approachOutline: string;
  provenance: { sourceIds: string[]; selectionBasis: string };
}
export interface CurriculumManifest {
  version: 1;
  title: string;
  conceptCount: number;
  flow: string[];
  concepts: CurriculumConcept[];
  questions: QuestionReference[];
  sources: {
    id: string;
    url?: string | null;
    retrievedAt: string;
    revision?: string | null;
    snapshotDate?: string | null;
    use: string;
  }[];
  advancedBranch: {
    lessonId: string;
    title: string;
    prerequisites: string[];
  }[];
  delivery: { skillTreeUi: string; practice: string; uiUx: string };
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
  references?: Record<string, string>;
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
  drafts: {
    problem: string;
    language: string;
    code: string;
    codeRevision?: string;
  }[];
  submissions: Submission[];
  studyContexts?: StudyContext[];
  attempts?: {
    id: string;
    challengeId: string;
    lessonId: string;
    kind: string;
    correct: boolean;
    createdAt: string;
  }[];
}
export interface Tree {
  id?: string;
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
  entities?: {
    id: string;
    value: number;
    position: number;
    role: "active" | "idle";
  }[];
  operation?: {
    kind: string;
    entityIds: string[];
    details: Record<string, unknown>;
  };
  activeEdge?: string;
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
