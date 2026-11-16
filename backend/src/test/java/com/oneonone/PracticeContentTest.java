package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/** Every core lesson's graded practice, checked through the real grader against the real Java traces. */
class PracticeContentTest {

  Store store;
  ChallengeService challenges;
  final TraceEngine traces = new TraceEngine();
  List<Map<String, Object>> core = new ArrayList<>();
  Set<String> problems = new HashSet<>();

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(
      new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", "")
    );
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    challenges = new ChallengeService(store, traces, new ProgressService(store));
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    Map<String, Map<String, Object>> lessons = new HashMap<>();
    for (var lesson : Store.items(content.get("lessons"))) {
      store.put(lesson.get("id").toString(), "lesson", "public", lesson);
      lessons.put(lesson.get("id").toString(), lesson);
    }
    for (var p : Store.items(content.get("problems"))) problems.add(p.get("id").toString());
    var curriculum = store.decode(new String(getClass().getResourceAsStream("/curriculum.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var concept : Store.items(curriculum.get("concepts"))) core.add(lessons.get(Store.strings(concept.get("lessonIds")).getFirst()));
  }

  Contracts.AttemptResult grade(Map<String, Object> challenge, Object answer) {
    return challenges.attempt(null, challenge.get("id").toString(), new Contracts.AttemptRequest(answer, UUID.randomUUID().toString()));
  }

  @Test
  void everyCoreLessonHasTwoSubstantiveChecksAndAPatternDrillAndLinkedProblems() {
    assertEquals(24, core.size());
    for (var lesson : core) {
      var list = ChallengeService.authored(lesson);
      long substantive = list.stream().filter(c -> List.of("prediction", "dry-run", "manipulation").contains(c.get("kind"))).count();
      long patterns = list.stream().filter(c -> "pattern".equals(c.get("kind"))).count();
      assertTrue(substantive >= 2, lesson.get("id") + " has " + substantive + " substantive checks");
      assertTrue(patterns >= 1, lesson.get("id") + " has no pattern drill");
      assertTrue(list.stream().anyMatch(c -> "dry-run".equals(c.get("kind"))), lesson.get("id") + " has no dry run");
      var linked = Store.strings(lesson.get("linkedProblems"));
      assertFalse(linked.isEmpty(), lesson.get("id") + " links no problems");
      for (String p : linked) assertTrue(problems.contains(p), lesson.get("id") + " links unknown " + p);
      Set<String> ids = new HashSet<>();
      for (var c : list) {
        assertTrue(ids.add(c.get("id").toString()), "duplicate challenge id " + c.get("id"));
        assertFalse(Store.text(c, "hint", "").isBlank(), c.get("id") + " needs a hint");
      }
    }
  }

  @Test
  void everyDryRunPointsAtARealTraceStepAndGradesFromIt() {
    int checked = 0;
    for (var lesson : core) for (var c : ChallengeService.authored(lesson)) {
      if (!"dry-run".equals(c.get("kind"))) continue;
      var steps = Store.items(traces.trace((Map<String, Object>) c.get("scene")).get("steps"));
      int at = ((Number) c.get("traceStep")).intValue();
      assertTrue(at >= 0 && at < steps.size(), c.get("id") + " step " + at + " of " + steps.size());
      var variables = (Map<String, Object>) steps.get(at).get("variables");
      Map<String, Object> right = new LinkedHashMap<>();
      for (var f : Store.items(c.get("fields"))) {
        String key = f.get("key").toString();
        assertTrue(variables.containsKey(key), c.get("id") + " asks for " + key + " but the trace has " + variables.keySet());
        Object v = variables.get(key);
        right.put(key, v instanceof List<?> l ? String.join(",", l.stream().map(String::valueOf).toList()) : String.valueOf(v));
      }
      assertTrue(grade(c, right).correct(), c.get("id") + " should accept the trace's own values " + right);
      var wrong = new LinkedHashMap<>(right);
      String first = wrong.keySet().iterator().next();
      wrong.put(first, "999999");
      assertFalse(grade(c, wrong).correct(), c.get("id") + " accepted a wrong value");
      checked++;
    }
    assertEquals(24, checked, "one dry run per core lesson");
  }

  @Test
  void everyAuthoredChoiceGradesAsAuthoredAndTheOthersFail() {
    for (var lesson : core) for (var c : ChallengeService.authored(lesson)) {
      if (!List.of("prediction", "pattern").contains(c.get("kind"))) continue;
      // the kept checkpoint's answer lives on the lesson; authored challenges carry their own
      Object answer = c.containsKey("answer") ? c.get("answer") : ((Map<?, ?>) lesson.get("checkpoint")).get("answer");
      int options = Store.strings(c.get("options")).size();
      int correct = ((Number) answer).intValue();
      assertTrue(correct >= 0 && correct < options, String.valueOf(c.get("id")));
      for (int i = 0; i < options; i++) assertEquals(i == correct, grade(c, i).correct(), c.get("id") + " option " + i);
    }
  }
}
