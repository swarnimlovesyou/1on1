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
  traceRevision?: number;
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
  /** Why each prerequisite concept matters here, keyed by concept id. */
  prerequisiteNotes?: Record<string, string>;
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
  interactiveStatus?: "existing-limited" | "specification-only" | "interactive";
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
  problem?: string;
  reviewed: boolean;
  createdAt: string;
}
export interface PlanTask {
  id: string;
  kind: "problem";
  problemId: string;
  adds: string[];
  date: string;
  done: boolean;
  doneAt: string | null;
}
export interface Plan {
  id: string;
  title: string;
  topics: string[];
  selected: { id: string; adds: string[] }[];
  uncovered: string[];
  perDay: number;
  method: string;
  /** Dated tasks; plans made before tasks existed have none until re-planned. */
  tasks?: PlanTask[];
  startDate?: string;
}
export type EvidenceState = "new" | "explored" | "passed" | "accepted";
export interface MapConcept {
  id: string;
  title: string;
  order: number;
  prerequisites: string[];
  lessonIds: string[];
  problemIds: string[];
  state: EvidenceState;
  explored: boolean;
  challenges: { passed: number; total: number };
  problems: { accepted: number; total: number };
  evidence: string[];
  notes: NoteLink[];
  missed?: MissedChallenge;
  review?: { stage: number; dueOn: string | null; due: boolean; lastOutcome: string; reviews: number };
}
export interface ReviewDue {
  conceptId: string;
  title: string;
  dueOn: string;
  overdueDays: number;
  lastOutcome: string;
  lessonId: string | null;
  notes: NoteLink[];
  missed?: MissedChallenge;
}
export interface NoteLink {
  id: string;
  title: string;
}
/** The most recent challenge the learner missed and has not passed since. */
export interface MissedChallenge {
  challengeId: string;
  lessonId: string;
  title: string;
}
export interface NextAction {
  kind: "review" | "task" | "learn" | "practice" | "done";
  title: string;
  reason: string;
  href: string;
  conceptId: string | null;
}
export interface LearningMap {
  today: string;
  concepts: MapConcept[];
  reviewsDue: ReviewDue[];
  nextAction: NextAction;
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
  links?: { from: string; to: string }[];
  head?: string;
  visual?: Record<string, unknown>;
}
export interface Trace {
  version: number;
  algorithm: string;
  family: string;
  steps: Step[];
  result: Step;
  input: Scene;
  revision?: number;
  code?: string[];
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

export interface NotebookSource {
  id: string;
  title: string;
  fileName: string;
  pages: number;
  bytes: number;
  createdAt: string;
}
export interface NotebookPassage {
  sourceId: string;
  title: string;
  page: number;
  text: string;
  score: number;
  n?: number;
}
export interface NotebookAnswer {
  /** true: cited answer; false: the sources don't say; null: passages only (no model). */
  answered: boolean | null;
  text: string;
  citations: NotebookPassage[];
  passages: NotebookPassage[];
  method: "model" | "search";
}
export interface RevisionCard {
  id: string;
  sourceId: string | null;
  sourceTitle: string | null;
  page: number | null;
  front: string;
  back: string;
  draftedBy: "model" | "text";
  recall: "again" | "hard" | "good" | "easy" | null;
  recalledAt: string | null;
  updatedAt: string;
}

export type CoachNudge = {
  at: string;
  stage: string;
  kind: "question" | "evidence" | "hint" | "options" | "solution";
  text: string;
  rung?: number;
  code?: string;
  language?: string;
};
export type CoachRun = {
  id: string;
  status: string;
  createdAt: string;
  current: boolean;
  finished: boolean;
  failing?: { index: number; status: string; public: boolean };
};
export type CoachView = {
  problem: string;
  stage: "plan" | "code" | "debug" | "reflect" | "done";
  steps: { key: string; label: string; done: boolean }[];
  plan?: { approach: string; invariant: string; example: string };
  latestRun?: CoachRun;
  accepted: boolean;
  nudges: CoachNudge[];
  solutionRevealed: boolean;
  reflection?: { complexity: string; transfer: string };
  transfer: string;
  execution: boolean;
};
