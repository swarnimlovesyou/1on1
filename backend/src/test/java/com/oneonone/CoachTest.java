package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** The Phase 2 coaching journey, with runs recorded as the runner records them (no Judge0 needed). */
class CoachTest {

  static final String P = "problem-trapped-rain", U = "learner";
  Store store;
  ProgressService progress;
  CoachService coach;
  int runs;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    progress = new ProgressService(store);
    coach = new CoachService(store, new ExecutionService(store, progress));
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var p : Store.items(content.get("problems"))) store.put(p.get("id").toString(), "problem", "public", p);
  }

  void draft(String code) {
    store.put("draft-" + U + "-" + P + "-python", "draft", U, Map.of("problem", P, "language", "python", "code", code, "codeRevision", Contracts.codeRevision("python", code)));
  }

  String run(String code, String status, Map<String, Object> failing) {
    String id = "submission-" + UUID.randomUUID();
    var results = new ArrayList<Map<String, Object>>();
    results.add(Map.of("index", 1, "status", "PASSED", "public", true));
    if (failing != null) results.add(failing);
    store.put(id, "submission", U, Map.of("problem", P, "language", "python", "code", code, "official", true, "status", status, "createdAt", Instant.parse("2026-11-16T10:00:00Z").plusSeconds(runs++).toString(), "results", results));
    return id;
  }

  Map<String, Object> nudge() {
    return coach.nudge(U, P, Map.of("language", "python"));
  }

  static Map<String, Object> last(Map<String, Object> view) {
    return Store.items(view.get("nudges")).getLast();
  }

  int count(String table) {
    return store.db.queryForObject("select count(*) from " + table, Integer.class);
  }

  @Test
  void conceptToPlanToFailingRunToCorrectionToAcceptanceToReflectionAndResume() {
    assertEquals("plan", coach.view(U, P, "python").get("stage"));
    var view = coach.savePlan(U, P, Map.of("language", "python", "approach", "Two pointers from both ends", "invariant", "the lower side's best wall bounds its water", "example", "2 0 2 holds 2"));
    assertEquals("code", view.get("stage"));
    // the first question is about the learner's own example and invariant, and is honest about the missing runner
    String q = last(nudge()).get("text").toString();
    assertTrue(q.contains("2 0 2 holds 2") && q.contains("lower side's best wall"), q);
    assertTrue(q.contains("Runs aren't available"), q);

    draft("partial");
    run("partial", "WRONG_ANSWER", Map.of("index", 2, "status", "WRONG_ANSWER", "public", true, "input", "2 1 5 1 3 2\n", "expected", "3\n", "actual", "1\n"));
    view = coach.view(U, P, "python");
    assertEquals("debug", view.get("stage"));
    var latest = (Map<?, ?>) view.get("latestRun");
    assertEquals(true, latest.get("current"));

    // a fresh ladder for this run: question, the actual failing case, three authored hints, then honest options
    List<String> kinds = new ArrayList<>();
    for (int i = 0; i < 7; i++) kinds.add(last(nudge()).get("kind").toString());
    assertEquals(List.of("question", "evidence", "hint", "hint", "hint", "options", "options"), kinds);
    var nudges = Store.items(coach.view(U, P, "python").get("nudges"));
    String evidence = nudges.stream().filter(n -> "evidence".equals(n.get("kind"))).findFirst().orElseThrow().get("text").toString();
    assertTrue(evidence.contains("2 1 5 1 3 2") && evidence.contains("expected “3”") && evidence.contains("printed “1”"), evidence);
    assertFalse(evidence.contains("edited"), "the run is of the current code");
    var hints = Store.strings(store.get(P).get("hints"));
    assertTrue(nudges.stream().anyMatch(n -> n.get("text").toString().endsWith(hints.get(2))));

    // editing makes the old run stale evidence, and says so
    draft("corrected");
    view = coach.view(U, P, "python");
    assertEquals(false, ((Map<?, ?>) view.get("latestRun")).get("current"));
    // a new run restarts the ladder rather than repeating the exhausted one
    run("corrected", "WRONG_ANSWER", Map.of("index", 7, "status", "WRONG_ANSWER", "public", false));
    assertEquals(0, last(nudge()).get("rung"));
    String hidden = last(nudge()).get("text").toString();
    assertTrue(hidden.contains("hidden case 7") && hidden.contains("-10000 and 10000"), hidden);

    String accepted = run("corrected", "ACCEPTED", null);
    progress.accepted(U, P, accepted); // what ExecutionService does for an accepted official run
    assertEquals("reflect", coach.view(U, P, "python").get("stage"));
    assertTrue(last(nudge()).get("text").toString().contains("worst case"));
    assertTrue(last(nudge()).get("text").toString().startsWith("Transfer question"));
    view = coach.saveReflection(U, P, Map.of("language", "python", "complexity", "Each pointer moves at most n times: O(n).", "transfer", "Negative heights clamp to zero, so nothing changes."));
    assertEquals("done", view.get("stage"));
    assertTrue(Store.items(view.get("steps")).stream().allMatch(s -> Boolean.TRUE.equals(s.get("done"))));

    // reload/resume: a fresh service sees the same plan, history and reflection
    var resumed = new CoachService(store, new ExecutionService(store, progress)).view(U, P, "python");
    assertEquals(view.get("nudges"), resumed.get("nudges"));
    assertEquals(view.get("plan"), resumed.get("plan"));
    assertEquals("done", resumed.get("stage"));
  }

  @Test
  void coachingAndRevealingTheSolutionNeverCreateCredit() {
    coach.savePlan(U, P, Map.of("approach", "guess", "invariant", "none", "example", "1"));
    for (int i = 0; i < 8; i++) nudge();
    assertThrows(IllegalArgumentException.class, () -> coach.nudge(U, P, Map.of("language", "python", "want", "solution")));
    var view = coach.nudge(U, P, Map.of("language", "python", "want", "solution", "confirm", true));
    var shown = last(view);
    assertEquals("python", shown.get("language"));
    assertTrue(shown.get("code").toString().contains("left_max"), "the Python reference, in the learner's language");
    assertEquals(true, view.get("solutionRevealed"));
    assertEquals(false, view.get("accepted"));
    var conflict = assertThrows(ResponseStatusException.class, () -> coach.saveReflection(U, P, Map.of("complexity", "O(n)", "transfer", "same")));
    assertEquals(409, conflict.getStatusCode().value());
    assertEquals(0, count("solved_credits"));
    assertEquals(0, count("learning_events"));
    assertEquals(0, count("challenge_attempts"));
    assertFalse(Store.strings(progress.summary(U).get("solved")).contains(P));
  }

  @Test
  void plansAreValidatedAndSessionsArePrivate() {
    assertThrows(IllegalArgumentException.class, () -> coach.savePlan(U, P, Map.of("approach", " ", "invariant", "x", "example", "y")));
    assertThrows(IllegalArgumentException.class, () -> coach.savePlan(U, P, Map.of("approach", "x".repeat(1501), "invariant", "x", "example", "y")));
    assertThrows(IllegalArgumentException.class, () -> coach.view(U, P, "rust"));
    coach.savePlan(U, P, Map.of("approach", "mine", "invariant", "x", "example", "y"));
    assertNull(coach.view("someone-else", P, "java").get("plan"));
    assertEquals("plan", coach.view("someone-else", P, "java").get("stage"));
  }
}
