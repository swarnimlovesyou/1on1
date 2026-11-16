package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

class PlanAndMapTest {

  Store store;
  ProgressService progress;
  PlanService plans;
  LearningMapService map;
  final LocalDate today = PlanService.today();

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(
      new DriverManagerDataSource(
        "jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1",
        "sa",
        ""
      )
    );
    for (String migration : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + migration).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    progress = new ProgressService(store);
    plans = new PlanService(store, progress);
    map = new LearningMapService(store);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (String kind : List.of("lessons", "problems")) for (var item : Store.items(content.get(kind))) store.put(
      item.get("id").toString(),
      kind.equals("lessons") ? "lesson" : "problem",
      "public",
      item
    );
  }

  void attempt(String user, String challenge, String lesson, boolean correct, boolean hintUsed, LocalDate day) {
    store.db.update(
      "insert into challenge_attempts(id,member_id,request_id,challenge_id,lesson_id,kind,answer_json,correct,feedback,hint_used,created_at) values(?,?,?,?,?,?,?,?,?,?,?)",
      UUID.randomUUID().toString(), user, UUID.randomUUID().toString(), challenge, lesson, "prediction", "1", correct, "", hintUsed,
      Timestamp.from(day.atTime(12, 0).toInstant(ZoneOffset.UTC))
    );
  }

  Map<String, Object> concept(Map<String, Object> m, String id) {
    return Store.items(m.get("concepts")).stream().filter(c -> id.equals(c.get("id"))).findFirst().orElseThrow();
  }

  @Test
  void planTasksAreDatedCompletedMovedAndSurviveRegeneration() {
    LocalDate start = today.plusDays(2);
    var plan = plans.create("alice", Map.of("title", "Graphs and more", "topics", List.of("Arrays", "Graphs", "Trees", "Strings"),
      "perDay", 1, "startDate", start.toString()));
    var tasks = PlanService.tasks(plan);
    assertTrue(tasks.size() >= 2, "several problems are needed to cover four topics");
    for (int i = 0; i < tasks.size(); i++) assertEquals(start.plusDays(i).toString(), tasks.get(i).get("date"), "one per day");
    String id = plan.get("id").toString();
    var first = tasks.getFirst();
    var second = tasks.get(1);

    plans.updateTask("alice", id, first.get("id").toString(), Map.of("done", true));
    plans.updateTask("alice", id, second.get("id").toString(), Map.of("date", today.plusDays(9).toString()));
    assertThrows(IllegalArgumentException.class, () -> plans.updateTask("alice", id, second.get("id").toString(), Map.of("date", "next week")));
    assertThrows(ResponseStatusException.class, () -> plans.updateTask("bob", id, first.get("id").toString(), Map.of("done", true)), "only the owner");
    assertThrows(ResponseStatusException.class, () -> plans.updateTask("alice", id, "task-nope", Map.of("done", true)));

    var regenerated = plans.regenerate("alice", id, Map.of("startDate", today.plusDays(5).toString(), "perDay", 2));
    var after = PlanService.tasks(regenerated);
    var kept = after.stream().filter(t -> t.get("id").equals(first.get("id"))).findFirst().orElseThrow();
    assertEquals(true, kept.get("done"));
    assertEquals(first.get("date"), kept.get("date"), "completed work keeps its date");
    assertEquals(1, after.stream().filter(t -> t.get("problemId").equals(first.get("problemId"))).count(), "a completed problem is not planned again");
    for (var t : after) if (!Boolean.TRUE.equals(t.get("done"))) assertFalse(
      LocalDate.parse(t.get("date").toString()).isBefore(today.plusDays(5)),
      "pending work starts at the new start date"
    );
    assertEquals(regenerated.get("selected").toString().contains(first.get("problemId").toString()), true);
  }

  @Test
  void conceptsComeInPrerequisiteOrderAndAGuestStartsAtTheBeginning() {
    var m = map.map(null);
    var concepts = Store.items(m.get("concepts"));
    assertEquals(24, concepts.size());
    Map<String, Integer> position = new HashMap<>();
    for (int i = 0; i < concepts.size(); i++) position.put(concepts.get(i).get("id").toString(), i);
    for (var c : concepts) for (String p : Store.strings(c.get("prerequisites"))) assertTrue(
      position.get(p) < position.get(c.get("id").toString()),
      p + " before " + c.get("id")
    );
    assertTrue(concepts.stream().allMatch(c -> c.get("state").equals("new")));
    var next = (Map<?, ?>) m.get("nextAction");
    assertEquals("learn", next.get("kind"));
    assertEquals("concept-complexity", next.get("conceptId"));
  }

  @Test
  void evidenceGradesStaySeparateAndADueReviewComesFirst() {
    progress.update("alice", Map.of("completed", List.of("lesson-arrays")));
    assertEquals("explored", concept(map.map("alice"), "concept-arrays").get("state"));

    // a success three days ago: its 1-day review is now due
    attempt("alice", "challenge-sliding-window-prediction", "lesson-sliding-window", true, false, today.minusDays(3));
    var m = map.map("alice");
    var window = concept(m, "concept-fixed-window");
    assertEquals("passed", window.get("state"));
    assertEquals(true, ((Map<?, ?>) window.get("review")).get("due"));
    var next = (Map<?, ?>) m.get("nextAction");
    assertEquals("review", next.get("kind"));
    assertEquals("concept-fixed-window", next.get("conceptId"));
    assertTrue(next.get("reason").toString().contains("2 days ago"));

    // reviewing it today without the hint moves it 3 days out; it is no longer due
    attempt("alice", "challenge-sliding-window-pattern", "lesson-sliding-window", true, false, today);
    window = concept(map.map("alice"), "concept-fixed-window");
    assertEquals(today.plusDays(3).toString(), ((Map<?, ?>) window.get("review")).get("dueOn"));
    assertNotEquals("review", ((Map<?, ?>) map.map("alice").get("nextAction")).get("kind"));

    // a miss after the hint was shown, then a success: hinted, so the interval does not climb
    attempt("alice", "challenge-sliding-window-pattern", "lesson-sliding-window", false, false, today.plusDays(0));
    window = concept(map.map("alice"), "concept-fixed-window");
    assertEquals(today.plusDays(1).toString(), ((Map<?, ?>) window.get("review")).get("dueOn"), "a miss returns tomorrow");

    // an accepted linked problem is the strongest grade, kept apart from challenges
    store.db.update("insert into solved_credits(member_id,problem_id,submission_id) values(?,?,?)", "alice", "problem-three-window", "s1");
    window = concept(map.map("alice"), "concept-fixed-window");
    assertEquals("accepted", window.get("state"));
    assertTrue(Store.strings(window.get("evidence")).stream().anyMatch(e -> e.contains("accepted by the judge")));
    assertEquals("new", concept(map.map("bob"), "concept-fixed-window").get("state"), "evidence is per learner");
  }

  @Test
  void aDueReviewLinksBackToTheMissedChallengeAndTheLearnersNotes() {
    attempt("alice", "challenge-sliding-window-pattern", "lesson-sliding-window", false, false, today.minusDays(2));
    store.put("note-lesson", "note", "alice", Map.of("title", "Window sums", "lesson", "lesson-sliding-window", "createdAt", "2026-11-01T00:00:00Z"));
    store.put("note-problem", "note", "alice", Map.of("title", "Three-window bug", "lesson", "", "problem", "problem-three-window", "createdAt", "2026-11-02T00:00:00Z"));
    store.put("note-other", "note", "alice", Map.of("title", "Graphs", "lesson", "lesson-graphs", "createdAt", "2026-11-03T00:00:00Z"));

    var review = Store.items(map.map("alice").get("reviewsDue")).stream().filter(r -> "concept-fixed-window".equals(r.get("conceptId"))).findFirst().orElseThrow();
    var missed = (Map<?, ?>) review.get("missed");
    assertEquals("challenge-sliding-window-pattern", missed.get("challengeId"));
    assertEquals("lesson-sliding-window", missed.get("lessonId"));
    assertNotEquals("a challenge", missed.get("title"), "the authored title, not a placeholder");
    assertEquals(List.of("note-problem", "note-lesson"), Store.items(review.get("notes")).stream().map(n -> n.get("id")).toList(), "this concept's notes, newest first");

    // passing it later resolves the miss; another learner sees none of this
    attempt("alice", "challenge-sliding-window-pattern", "lesson-sliding-window", true, false, today.minusDays(1));
    assertNull(concept(map.map("alice"), "concept-fixed-window").get("missed"));
    assertEquals(List.of(), concept(map.map("bob"), "concept-fixed-window").get("notes"));
  }

  @Test
  void aCycleInPrerequisitesIsRejected() {
    var order = Map.of("a", 1, "b", 2);
    assertEquals(List.of("a", "b"), LearningMapService.topologicalOrder(new LinkedHashMap<>(Map.of("a", List.of(), "b", List.of("a"))), order));
    assertThrows(IllegalStateException.class, () ->
      LearningMapService.topologicalOrder(new LinkedHashMap<>(Map.of("a", List.of("b"), "b", List.of("a"))), order));
    assertThrows(IllegalStateException.class, () -> LearningMapService.topologicalOrder(new LinkedHashMap<>(Map.of("a", List.of("z"))), order));
  }
}
