package com.oneonone;

import java.util.*;

/**
 * Validation and publication checks for an authored lesson or problem, in the shape the grader, the trace
 * engine and the pages rely on. Errors block any save; publication checks block publishing but allow a draft.
 * Reference solutions are never executed here: they are verified at build time and by the isolated runner.
 */
public class ContentChecks {

  static final Set<String> CHALLENGE_KINDS = Set.of("prediction", "pattern", "manipulation", "dry-run");
  static final List<String> PROSE_BLOCKS = List.of("worked", "invariant", "tradeoff");

  final List<Map<String, String>> errors = new ArrayList<>(), publication = new ArrayList<>(), warnings = new ArrayList<>();
  final Map<String, Object> summary = new LinkedHashMap<>();

  void error(String field, String message) {
    errors.add(Map.of("field", field, "message", message));
  }

  void publish(String field, String message) {
    publication.add(Map.of("field", field, "message", message));
  }

  void warn(String field, String message) {
    warnings.add(Map.of("field", field, "message", message));
  }

  Map<String, Object> result() {
    var out = new LinkedHashMap<String, Object>();
    out.put("errors", errors);
    out.put("publication", publication);
    out.put("warnings", warnings);
    out.put("canSave", errors.isEmpty());
    out.put("canPublish", errors.isEmpty() && publication.isEmpty());
    out.put("summary", summary);
    return out;
  }

  /** Runs the checks for one record; `problems` resolves linked problem ids. */
  static Map<String, Object> check(Map<String, Object> b, TraceEngine traces, java.util.function.Function<String, Optional<Map<String, Object>>> find) {
    var c = new ContentChecks();
    String kind = Store.text(b, "kind", ""), id = Store.text(b, "id", "");
    if (!Set.of("lesson", "problem", "path").contains(kind) || !id.matches(kind + "-[a-z0-9-]{1,80}"))
      c.error("id", "Choose a lesson, problem or path with a matching stable identifier.");
    if (Store.text(b, "title", "").isBlank()) c.error("title", "A title is required.");
    if (kind.equals("lesson")) c.lesson(b, traces, find);
    if (kind.equals("problem")) c.problem(b);
    return c.result();
  }

  @SuppressWarnings("unchecked")
  void lesson(Map<String, Object> b, TraceEngine traces, java.util.function.Function<String, Optional<Map<String, Object>>> find) {
    boolean core = "core".equals(b.get("branch"));
    if (Store.text(b, "body", "").isBlank()) error("body", "Lessons require body text.");
    if (!b.containsKey("checkpoint")) error("checkpoint", "Lessons require a checkpoint.");
    if (b.get("experiment") instanceof Map<?, ?> scene) {
      try {
        summary.put("experimentSteps", Store.items(traces.trace((Map<String, Object>) scene).get("steps")).size());
      } catch (RuntimeException e) {
        error("experiment", "The experiment does not trace: " + e.getMessage());
      }
    } else if (
      !(b.get("teaching") instanceof Map<?, ?> teaching) ||
      !"specification-only".equals(b.get("interactiveStatus")) ||
      !(teaching.get("java") instanceof Map<?, ?>) ||
      !(teaching.get("visualization") instanceof Map<?, ?>)
    ) error("experiment", "A lesson needs a supported experiment or an explicit visual specification and Java teaching example.");

    // challenges, exactly as the grader reads them
    var challenges = ChallengeService.authored(b);
    Set<String> ids = new HashSet<>();
    int substantive = 0, patterns = 0, dryRuns = 0;
    for (int i = 0; i < challenges.size(); i++) {
      var ch = challenges.get(i);
      String field = "challenges[" + i + "]", chKind = Store.text(ch, "kind", "");
      String chId = Store.text(ch, "id", "");
      if (chId.isBlank() || !ids.add(chId)) error(field + ".id", "Each challenge needs a unique id.");
      if (!CHALLENGE_KINDS.contains(chKind)) {
        error(field + ".kind", "Use prediction, pattern, manipulation or dry-run.");
        continue;
      }
      if (Store.text(ch, "prompt", Store.text(ch, "question", "")).isBlank()) error(field + ".prompt", "A challenge needs a prompt.");
      if (Store.text(ch, "hint", "").isBlank()) warn(field + ".hint", "Without a hint the learner gets a generic one.");
      if (chKind.equals("pattern")) patterns++;
      else substantive++;
      switch (chKind) {
        case "prediction", "pattern" -> {
          int options = Store.strings(ch.get("options")).size();
          Object answer = ch.containsKey("answer") ? ch.get("answer") : b.get("checkpoint") instanceof Map<?, ?> cp ? cp.get("answer") : null;
          if (options < 2) error(field + ".options", "Give at least two options.");
          if (!(answer instanceof Number n) || n.intValue() < 0 || n.intValue() >= options) error(field + ".answer", "The answer must be the index of one option.");
        }
        case "dry-run" -> {
          dryRuns++;
          try {
            var steps = Store.items(traces.trace((Map<String, Object>) ch.get("scene")).get("steps"));
            int at = ch.get("traceStep") instanceof Number n ? n.intValue() : -1;
            if (at < 0 || at >= steps.size()) error(field + ".traceStep", "traceStep must be between 0 and " + (steps.size() - 1) + ".");
            else {
              var variables = (Map<String, Object>) steps.get(at).get("variables");
              var fields = Store.items(ch.get("fields"));
              if (fields.isEmpty()) error(field + ".fields", "A dry run needs at least one field.");
              for (var f : fields) if (!variables.containsKey(Store.text(f, "key", ""))) error(
                field + ".fields",
                "Step " + at + " has no variable “" + Store.text(f, "key", "") + "”; it has " + variables.keySet() + "."
              );
            }
          } catch (RuntimeException e) {
            error(field + ".scene", "The dry run's scene does not trace: " + e.getMessage());
          }
        }
        case "manipulation" -> {
          if (!(ch.get("scene") instanceof Map<?, ?>) || !(ch.get("rule") instanceof Map<?, ?> rule) || Store.text((Map<String, Object>) rule, "path", "").isBlank())
            error(field + ".rule", "A manipulation needs a scene and a rule with a result path.");
        }
        default -> {}
      }
    }
    summary.put("challenges", challenges.size());

    // prose sections render as titled blocks
    var blocks = Store.items(b.get("blocks"));
    for (int i = 0; i < blocks.size(); i++) if (Store.text(blocks.get(i), "title", "").isBlank() || Store.text(blocks.get(i), "text", "").isBlank())
      error("blocks[" + i + "]", "Each block needs a title and text.");
    var blockIds = blocks.stream().map(x -> Store.text(x, "id", "")).toList();

    for (String p : Store.strings(b.get("linkedProblems"))) {
      var problem = find.apply(p);
      if (problem.isEmpty()) error("linkedProblems", "Unknown problem " + p + ".");
      else if (Boolean.FALSE.equals(problem.get().get("published"))) warn("linkedProblems", p + " is still a draft.");
    }
    var prerequisites = b.get("teaching") instanceof Map<?, ?> t ? Store.strings(t.get("prerequisites")) : List.<String>of();
    var notes = b.get("prerequisiteNotes") instanceof Map<?, ?> m ? m.keySet() : Set.of();
    for (Object key : notes) if (!prerequisites.contains(key.toString())) error("prerequisiteNotes", key + " is not one of this lesson's prerequisites.");

    // what a core lesson must have before learners see it; advanced lessons get advice only
    List<String[]> ready = new ArrayList<>();
    if (Store.text(b, "body", "").length() < 300) ready.add(new String[] { "body", "Write an opening of at least 300 characters." });
    if (!blockIds.containsAll(PROSE_BLOCKS)) ready.add(new String[] { "blocks", "Add worked, invariant and tradeoff blocks." });
    if (substantive < 2) ready.add(new String[] { "challenges", "Add at least two prediction, dry-run or manipulation challenges." });
    if (patterns < 1) ready.add(new String[] { "challenges", "Add a pattern drill." });
    if (dryRuns < 1 && b.get("experiment") instanceof Map<?, ?>) ready.add(new String[] { "challenges", "Add a dry run on the experiment's trace." });
    if (Store.strings(b.get("linkedProblems")).isEmpty()) ready.add(new String[] { "linkedProblems", "Link at least one practice problem." });
    if (!notes.containsAll(prerequisites)) ready.add(new String[] { "prerequisiteNotes", "Say why each prerequisite is needed." });
    for (String[] r : ready) if (core) publish(r[0], r[1]);
    else warn(r[0], r[1]);
  }

  void problem(Map<String, Object> b) {
    var tests = Store.items(b.get("tests"));
    if (tests.size() < 5 || tests.size() > 40) error("tests", "Problems need 5–40 tests.");
    for (int i = 0; i < tests.size(); i++) if (!(tests.get(i).get("input") instanceof String) || !(tests.get(i).get("output") instanceof String))
      error("tests[" + i + "]", "Each test needs input and output text.");
    long hidden = tests.stream().filter(t -> Boolean.FALSE.equals(t.get("public"))).count();
    summary.put("tests", tests.size());
    summary.put("hiddenTests", hidden);
    if (Store.text(b, "editorial", "").isBlank()) error("editorial", "An editorial is required.");
    if (Store.text(b, "reference", "").isBlank()) error("reference", "A Java reference solution is required.");
    var references = b.get("references") instanceof Map<?, ?> r ? r : Map.of();
    if (references.containsKey("java") && !Objects.equals(references.get("java"), b.get("reference")))
      error("references.java", "references.java must equal reference; the judge grades with reference.");

    var hints = Store.strings(b.get("hints"));
    if (hints.size() != 3 || hints.stream().anyMatch(h -> h.strip().length() < 25)) publish("hints", "Write three specific hints of at least 25 characters.");
    if (Store.text(b, "editorial", "").length() < 200) publish("editorial", "Write an editorial of at least 200 characters.");
    if (hidden == 0) publish("tests", "Add at least one hidden test.");
    if (hidden == tests.size()) publish("tests", "Keep at least one public test so learners see the format.");
    if (!(references.get("python") instanceof String py) || py.isBlank()) publish("references.python", "Add a Python reference.");
    if (!(references.get("cpp") instanceof String cpp) || cpp.isBlank()) warn("references.cpp", "No C++ reference; learners using C++ see the Java one.");
    warn("references", "References are not executed here. Run scripts/verify-references.py and the content tests before release.");
  }
}
