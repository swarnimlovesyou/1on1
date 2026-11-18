package com.oneonone;

import com.oneonone.algorithms.*;
import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class LearningController {

  final Store s;
  final TraceEngine traces;
  final ProgressService progress;
  final ChallengeService challenges;
  final PlanService plans;

  public LearningController(
    Store s,
    TraceEngine t,
    ProgressService progress,
    ChallengeService challenges,
    PlanService plans
  ) {
    this.plans = plans;
    this.progress = progress;
    this.challenges = challenges;
    this.s = s;
    traces = t;
  }

  @PostMapping("/experiments")
  public Contracts.ExecutionTrace trace(@RequestBody Contracts.SceneRequest b) {
    return Contracts.ExecutionTrace.from(traces.trace(b.toMap()));
  }

  @GetMapping("/progress")
  public Map<String, Object> progress(Authentication a) {
    return progress.summary(AuthController.user(a));
  }

  @PostMapping("/progress")
  public Map<String, Object> update(
    Authentication a,
    @RequestBody Map<String, Object> body
  ) {
    String user = AuthController.user(a);
    if (body.get("checkpoint") instanceof Map<?, ?> cp) {
      challenges.attempt(
        user,
        "challenge-" + cp.get("lesson") + "-checkpoint",
        new Contracts.AttemptRequest(
          cp.get("answer"),
          UUID.randomUUID().toString()
        )
      );
    }
    return progress.update(user, body);
  }

  @GetMapping("/notes")
  public List<Map<String, Object>> notes(Authentication a) {
    return s.list("note", AuthController.user(a));
  }

  @PostMapping("/notes")
  public Map<String, Object> note(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a),
      text = Store.text(b, "text", "").strip();
    if (
      text.isEmpty() || text.length() > 20000
    ) throw new IllegalArgumentException(
      "Write a note of up to 20000 characters."
    );
    String id = Store.text(b, "id", "note-" + UUID.randomUUID());
    if (
      !id.matches("note-[a-zA-Z0-9-]{1,80}")
    ) throw new IllegalArgumentException("Choose a valid note identifier.");
    if (s.find(id).isPresent()) s.owned(id, u);
    Map<String, Object> note = new LinkedHashMap<>();
    String problem = Store.text(b, "problem", "");
    if (!problem.isEmpty()) {
      if (!problem.startsWith("problem-") || !s.owned(problem, "public").containsKey("tests")) throw new IllegalArgumentException("Choose a published practice problem.");
      note.put("problem", problem);
    }
    if (b.get("experiment") instanceof Map<?, ?>) {
      var scene = (Map<String, Object>) b.get("experiment");
      traces.trace(scene);
      note.put("experiment", scene);
    }
    note.putAll(
      Map.of(
        "text",
        text,
        "title",
        Store.text(b, "title", "Study note"),
        "lesson",
        Store.text(b, "lesson", ""),
        "createdAt",
        s
          .find(id)
          .map(n -> n.get("createdAt"))
          .orElse(java.time.Instant.now().toString()),
        "reviewed",
        Boolean.TRUE.equals(b.get("reviewed"))
      )
    );
    return s.put(id, "note", u, note);
  }

  @DeleteMapping("/notes/{id}")
  public Map<String, Object> deleteNote(
    Authentication a,
    @PathVariable String id
  ) {
    s.delete(id, AuthController.user(a));
    return Map.of("ok", true);
  }

  @PutMapping("/drafts/{problem}")
  public Map<String, Object> draft(
    Authentication a,
    @PathVariable String problem,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a),
      code = Store.text(b, "code", "");
    if (code.length() > 50000) throw new IllegalArgumentException(
      "Code must be under 50000 characters."
    );
    String language = Store.text(b, "language", "java");
    if (
      !Set.of("java", "python", "cpp").contains(language) ||
      !s.owned(problem, "public").containsKey("tests")
    ) throw new IllegalArgumentException(
      "Choose a published problem and supported language."
    );
    return s.put(
      "draft-" + u + "-" + problem + "-" + Store.text(b, "language", "java"),
      "draft",
      u,
      Map.of(
        "problem",
        problem,
        "language",
        Store.text(b, "language", "java"),
        "code",
        code,
        "codeRevision",
        Contracts.codeRevision(language, code)
      )
    );
  }

  /** {title,topics,difficulty,perDay,startDate?}: set cover picks the problems, then they become dated tasks. */
  @PostMapping("/plans")
  public Map<String, Object> plan(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    return plans.create(AuthController.user(a), b);
  }

  /** {startDate?, perDay?}: completed tasks stay as they are; the rest is re-planned from startDate. */
  @PostMapping("/plans/{id}/regenerate")
  public Map<String, Object> regenerate(
    Authentication a,
    @PathVariable String id,
    @RequestBody Map<String, Object> b
  ) {
    return plans.regenerate(AuthController.user(a), id, b);
  }

  /** {done?: boolean, date?: "YYYY-MM-DD"}: complete, reopen or move one task. */
  @PatchMapping("/plans/{id}/tasks/{task}")
  public Map<String, Object> task(
    Authentication a,
    @PathVariable String id,
    @PathVariable String task,
    @RequestBody Map<String, Object> b
  ) {
    return plans.updateTask(AuthController.user(a), id, task, b);
  }

  @GetMapping("/cohorts")
  public List<Map<String, Object>> cohorts(Authentication a) {
    String u = AuthController.user(a);
    return s
      .all("cohort")
      .stream()
      .filter(c -> Store.strings(c.get("members")).contains(u))
      .map(this::cohortView)
      .toList();
  }

  @PostMapping("/cohorts")
  public Map<String, Object> cohort(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a),
      name = Store.text(b, "name", "").strip();
    if (
      name.isBlank() || name.length() > 100
    ) throw new IllegalArgumentException(
      "Enter a cohort name of up to 100 characters."
    );
    var c = s.put(
      "cohort-" + UUID.randomUUID(),
      "cohort",
      u,
      Map.of(
        "name",
        name,
        "code",
        UUID.randomUUID().toString().substring(0, 8).toUpperCase(Locale.ROOT),
        "members",
        List.of(u)
      )
    );
    return cohortView(c);
  }

  @PostMapping("/cohorts/join")
  public synchronized Map<String, Object> join(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a);
    var c = s
      .all("cohort")
      .stream()
      .filter(x ->
        x
          .get("code")
          .equals(Store.text(b, "code", "").strip().toUpperCase(Locale.ROOT))
      )
      .findFirst()
      .orElseThrow(() ->
        new IllegalArgumentException("That invitation code was not found.")
      );
    var members = new ArrayList<>(Store.strings(c.get("members")));
    if (!members.contains(u)) members.add(u);
    c.put("members", members);
    String owner = s.db.queryForObject(
      "select owner_id from documents where id=?",
      String.class,
      c.get("id")
    );
    return cohortView(s.put(c.get("id").toString(), "cohort", owner, c));
  }

  @GetMapping("/cohorts/summary")
  public List<Map<String, Object>> cohortSummaries(Authentication a) {
    String user = AuthController.user(a);
    Map<String, Integer> weights = new HashMap<>();
    for (var p : s.list("problem", "public"))
      weights.put(
        p.get("id").toString(),
        p.get("difficulty").equals("Hard")
          ? 5
          : p.get("difficulty").equals("Medium")
            ? 3
            : 1
      );
    List<Map<String, Object>> summaries = new ArrayList<>();
    for (var c : s.all("cohort")) {
      var ids = Store.strings(c.get("members"));
      if (!ids.contains(user)) continue;
      int[] scores = ids
        .stream()
        .mapToInt(id ->
          Store.strings(progress.summary(id).get("solved"))
            .stream()
            .distinct()
            .mapToInt(problem -> weights.getOrDefault(problem, 0))
            .sum()
        )
        .toArray();
      summaries.add(
        Map.of(
          "id",
          c.get("id"),
          "name",
          c.get("name"),
          "size",
          scores.length,
          "quartiles",
          scores.length < 5 ? Map.of() : new Quickselect().quartiles(scores, 42)
        )
      );
    }
    return summaries;
  }

  @SuppressWarnings("unchecked")
  Map<String, Object> cohortView(Map<String, Object> c) {
    var out = new LinkedHashMap<>(c);
    List<Map<String, Object>> members = new ArrayList<>();
    Map<String, Integer> weights = new HashMap<>();
    for (var p : s.list("problem", "public"))
      weights.put(
        p.get("id").toString(),
        switch (p.get("difficulty").toString()) {
          case "Hard" -> 5;
          case "Medium" -> 3;
          default -> 1;
        }
      );
    Map<String, Set<String>> solvedBy = new LinkedHashMap<>();
    Map<String, String> nameOf = new HashMap<>();
    for (String u : Store.strings(c.get("members"))) {
      var names = s.db.queryForList(
        "select name from members where id=?",
        String.class,
        u
      );
      if (names.isEmpty()) continue;
      var summary = progress.summary(u);
      var solvedIds = new HashSet<>(Store.strings(summary.get("solved")));
      solvedBy.put(u, solvedIds);
      nameOf.put(u, names.getFirst());
      int score = solvedIds.stream().mapToInt(id -> weights.getOrDefault(id, 0)).sum();
      int week = StudyCircles.thisWeek(summary.get("activity") instanceof Map<?, ?> m ? (Map<String, ?>) m : Map.of(), PlanService.today());
      members.add(Map.of("name", names.getFirst(), "score", score, "id", u, "solved", solvedIds.stream().filter(weights::containsKey).count(), "week", week));
    }
    var published = s.list("problem", "public").stream().filter(p -> !Boolean.FALSE.equals(p.get("published"))).toList();
    var weekly = new LinkedHashMap<>(StudyCircles.weeklyProblem(c.get("id").toString(), PlanService.today(), published, solvedBy));
    if (!weekly.isEmpty()) weekly.put("solvedBy", Store.strings(weekly.get("solvedBy")).stream().map(nameOf::get).toList());
    out.put("weeklyProblem", weekly);
    out.put(
      "members",
      members
        .stream()
        .sorted(
          Comparator.comparingInt(x -> -((Number) x.get("score")).intValue())
        )
        .toList()
    );
    out.put(
      "quartiles",
      members.size() < 5
        ? Map.of()
        : new Quickselect().quartiles(
            members
              .stream()
              .mapToInt(x -> ((Number) x.get("score")).intValue())
              .toArray(),
            42
          )
    );
    return out;
  }
}
