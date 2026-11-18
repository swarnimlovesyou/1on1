package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/** Suggesting a practice plan from the learner's own record, with or without AI. */
class PlanAdvisorTest {

  Store store;
  PlanAdvisor advisor;
  Set<String> problemTopics = new TreeSet<>();

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var l : Store.items(content.get("lessons"))) store.put(l.get("id").toString(), "lesson", "public", l);
    for (var p : Store.items(content.get("problems"))) {
      store.put(p.get("id").toString(), "problem", "public", p);
      problemTopics.addAll(Store.strings(p.get("topics")));
    }
    advisor = new PlanAdvisor(store, new ProgressService(store), null);
  }

  void wrong(String user, String lesson) {
    store.db.update(
      "insert into challenge_attempts(id,member_id,request_id,challenge_id,lesson_id,kind,answer_json,correct,feedback,hint_used,created_at) values(?,?,?,?,?,?,?,?,?,?,?)",
      UUID.randomUUID().toString(), user, UUID.randomUUID().toString(), "c-" + UUID.randomUUID(), lesson, "prediction", "1", false, "", false, Timestamp.from(Instant.now())
    );
  }

  @Test
  void withoutAiTheRulesPutTopicsYouMissedFirstAndSizeThePace() {
    var lesson = store.list("lesson", "public").stream()
      .filter(l -> Store.strings(l.get("topics")).stream().anyMatch(problemTopics::contains)).findFirst().orElseThrow();
    String weak = Store.strings(lesson.get("topics")).stream().filter(problemTopics::contains).findFirst().orElseThrow();
    for (int i = 0; i < 3; i++) wrong("bea", lesson.get("id").toString());

    var s = advisor.suggest("bea", Map.of("goal", "placements", "weeks", 4, "minutesPerDay", 60));
    assertEquals("rules", s.get("source"));
    var topics = Store.strings(s.get("topics"));
    assertEquals(weak, topics.getFirst(), "the topic missed most comes first");
    assertTrue(problemTopics.containsAll(topics), "only topics that have problems");
    assertTrue(topics.size() >= 3 && topics.size() <= 12);
    assertEquals(2, s.get("perDay"), "an hour a day is about two problems");
    assertFalse(Store.strings(s.get("reasons")).isEmpty());
    assertEquals("Easy", advisor.suggest("bea", Map.of("goal", "foundations", "weeks", 2, "minutesPerDay", 30)).get("difficulty"));
  }

  @Test
  void anAiAnswerIsKeptOnlyWithinTheRealTopicsAndLimits() {
    var fallback = advisor.suggest("cal", Map.of("goal", "placements", "weeks", 2, "minutesPerDay", 30));
    String real = problemTopics.iterator().next();
    var ai = PlanAdvisor.fromAi(
      Map.of("title", "Sprint", "topics", List.of(real, "Quantum basket weaving"), "difficulty", "Impossible", "perDay", 40, "reasons", List.of("Because.")),
      problemTopics, fallback);
    assertEquals("ai", ai.get("source"));
    assertEquals(List.of(real), ai.get("topics"));
    assertEquals(fallback.get("difficulty"), ai.get("difficulty"), "an unknown difficulty falls back");
    assertEquals(10, ai.get("perDay"));
    assertEquals(fallback, PlanAdvisor.fromAi(Map.of("topics", List.of("Nope")), problemTopics, fallback), "no real topic means the rules' plan");
  }

  @Test
  void outOfRangeChoicesAreRejected() {
    assertThrows(IllegalArgumentException.class, () -> advisor.suggest("dee", Map.of("weeks", 0, "minutesPerDay", 60)));
    assertThrows(IllegalArgumentException.class, () -> advisor.suggest("dee", Map.of("weeks", 4, "minutesPerDay", 5000)));
  }
}
