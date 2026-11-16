# Content authoring guide

How lessons, practice challenges and problems are written, checked and shipped. Everything learners see comes from
`backend/src/main/resources/content.json` and `curriculum.json`, both generated. Never edit those files by hand: change
the Python source and regenerate.

## The pipeline

```bash
cd scripts && python generate_content.py
```

`generate_content.py` builds the base lessons, problems and paths, then applies these modules in order. A later module
can overwrite an earlier one, so put a change in the module that owns that part of a record.

| Order | Module | Owns |
| --- | --- | --- |
| 1 | `generate_content.py` | Problem statements, Java references, fixtures, paths, the base lesson list |
| 2 | `reference_content.py` | The four reference journeys (fixed window, BST, BFS, tabulation) and the eight reference problems |
| 3 | `curriculum_content.py` | The 24 concepts: mental model, worked example, invariant, mistake, complexity, Java teaching example with test cases, checkpoint, visual specification. Also writes `curriculum.json` and `docs/CURRICULUM.md` |
| 4 | `visualization_content.py` | Each lesson's experiment scene (input, target) and the pseudocode lines shown beside the animation |
| 5 | `practice_content.py` | Per-algorithm prediction, pattern and dry-run challenges, and linked problems |
| 6 | `problem_content.py` | Python references, three hints, editorials and hidden edge cases, loaded from `problem_batches/batch_*.py` |
| 7 | `lesson_content.py` | Lesson openings, worked/invariant/tradeoff blocks and prerequisite reasons, loaded from `lesson_prose/batch_*.py`; lesson-level teaching overrides (Quicksort, Merge Sort, Memoization) |

On startup `ContentSeed` loads `content.json` into the database, except records an administrator saved
(`edited: true`). Restart the backend after regenerating.

## Writing a lesson

A core lesson needs all of the following before it can be published. The admin checks and `PracticeContentTest`
enforce them.

- **Opening (`body`, 300+ characters):** start from an everyday picture, say what problem the idea solves and what to
  watch in the animation. Don't copy the concept's one-line mental model.
- **Worked example (`blocks[worked]`):** walk the lesson's own experiment input, step by step, as the Java trace
  computes it. Every number must appear in that trace. Don't repeat the code section's `workedExample`, which the page
  already shows.
- **Why it works (`blocks[invariant]`):** what stays true, and why that makes the algorithm correct.
- **Cost (`blocks[tradeoff]`):** why the time and space are what they are, when to choose something else, and the edge
  cases.
- **Prerequisite reasons (`prerequisiteNotes`):** one sentence per prerequisite concept on what this lesson uses from it.
- **Practice:** at least two prediction, dry-run or manipulation challenges, a pattern drill, a dry run on the
  experiment's trace, and at least one linked problem.

Prose batches are checked against the real trace before they are merged:

```bash
python scripts/lesson_prose/check_prose.py <n> <trace-export.json>
```

The export holds each lesson's fields plus its trace steps, fetched from `POST /api/v1/experiments` with the lesson's
`experiment` scene.

### Code sections must match the animation

The "Minimal Java" section comes from the concept (`teaching.java`, `teaching.workedExample`,
`teaching.visualization`). When a lesson's animation runs something different from its concept's example, give that
lesson its own teaching override in `lesson_content.py` (`LESSON_TEACHING`). `CurriculumTest` compiles every concept
example and every lesson override, and runs their documented cases.

## Writing challenges

Challenges are graded on the server by `ChallengeService`. Shapes:

| Kind | Required fields | Graded by |
| --- | --- | --- |
| `prediction`, `pattern` | `prompt`, `options` (2+), `answer` (option index), `explanation`, `hint` | Index equality |
| `dry-run` | `prompt`, `scene`, `traceStep`, `fields [{key,label}]`, `hint` | Each field equals the trace variable `key` at `traceStep` |
| `manipulation` | `prompt`, `scene`, `rule {path, equals}`, optional `requiredTarget` | The learner's own scene, traced in Java, reaches `rule.path == equals` |

For a dry run, pick `traceStep` by reading the trace. The checks reject a step outside the trace or a field the step
doesn't record. Challenge ids must stay stable: attempts and review schedules refer to them.

## Writing a problem

- **Statement, constraints and formats:** stdin and stdout only, with no hidden function signature.
- **Java `reference`:** the judge grades with it. `references.java` must equal it.
- **Python reference:** in `references.python`. C++ is optional until a compiler or Judge0 is available; without it,
  learners using C++ see the Java reference with a note saying so.
- **Hints:** three, progressive and specific to this problem: what to notice, the key state, then the algorithm with
  its tricky edge.
- **Editorial:** the approach, why it is correct, complexity and edge cases.
- **Fixtures:** 5–40, with at least one public and one hidden. Add adversarial cases (ties, negatives, extremes,
  disconnected graphs).

Problem batches are checked before they are merged. The checker runs the Python on every fixture, and requires both the
Java and the Python reference to agree on each new case:

```bash
python scripts/problem_batches/check_batch.py <n>
```

## Editing in the admin page

The admin editor (`/admin`, administrator accounts only) runs the same rules through `POST /api/v1/admin/content/check`:

- **Errors** block any save.
- **Publication checks** block publishing; you can still save a draft (`published: false`).
- **Warnings** are advice.

The preview shows the unsaved record as a learner would see it. References are never executed in the admin page.
Verify them with the commands below. Saved records are marked `edited`, so regenerating content won't overwrite them.

## Before you ship

```bash
cd scripts && python generate_content.py
```

```bash
python scripts/verify-references.py
```

```bash
npm run verify
```

`verify` runs the backend tests (including `ContentTest`, which runs every Java reference on every fixture,
`CurriculumTest`, `PracticeContentTest` and `AdminChecksTest`), the frontend tests and the production build. With the app
running (`npm run dev:core`), `npx playwright test` runs the browser journeys.
