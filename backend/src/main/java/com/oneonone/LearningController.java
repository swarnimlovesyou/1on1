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

  public LearningController(
    Store s,
    TraceEngine t,
    ProgressService progress,
    ChallengeService challenges
  ) {
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

  @PostMapping("/plans")
  public Map<String, Object> plan(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a);
    Set<String> goals = new TreeSet<>(Store.strings(b.get("topics")));
    if (
      goals.isEmpty() || goals.size() > 50
    ) throw new IllegalArgumentException("Select between 1 and 50 topics.");
    String difficulty = Store.text(b, "difficulty", "All");
    var state = s.find("state-" + u).orElse(Map.of());
    Set<String> solved = new HashSet<>(
      Store.strings(progress.summary(u).get("solved"))
    );
    var candidates = s
      .list("problem", "public")
      .stream()
      .filter(
        p ->
          !Boolean.FALSE.equals(p.get("published")) &&
          !solved.contains(p.get("id")) &&
          (difficulty.equals("All") || difficulty.equals(p.get("difficulty")))
      )
      .map(p ->
        new SetCover.Candidate(
          p.get("id").toString(),
          new HashSet<>(Store.strings(p.get("topics")))
        )
      )
      .toList();
    var result = new SetCover().select(goals, candidates);
    int perDay = Math.min(
      10,
      Math.max(1, Integer.parseInt(Store.text(b, "perDay", "2")))
    );
    Map<String, Object> data = new LinkedHashMap<>();
    data.put("title", Store.text(b, "title", "My practice plan"));
    data.put("topics", goals);
    data.put("selected", result.selected());
    data.put("uncovered", result.uncovered());
    data.put("perDay", perDay);
    data.put("method", "Greedy set-cover approximation");
    data.put("createdAt", java.time.Instant.now().toString());
    return s.put("plan-" + UUID.randomUUID(), "plan", u, data);
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
    for (String u : Store.strings(c.get("members"))) {
      var names = s.db.queryForList(
        "select name from members where id=?",
        String.class,
        u
      );
      if (names.isEmpty()) continue;
      int score = Store.strings(progress.summary(u).get("solved"))
        .stream()
        .distinct()
        .mapToInt(id -> weights.getOrDefault(id, 0))
        .sum();
      members.add(Map.of("name", names.getFirst(), "score", score, "id", u));
    }
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
