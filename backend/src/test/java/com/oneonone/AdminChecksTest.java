package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import tools.jackson.databind.ObjectMapper;

/** The editor's validation and publication checks, against the real catalogue and deliberately broken copies. */
class AdminChecksTest {

  Store store;
  AdminController admin;
  Map<String, Map<String, Object>> lessons = new LinkedHashMap<>(), problems = new LinkedHashMap<>();

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    admin = new AdminController(store, new TraceEngine(), new SearchIndex(store));
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var l : Store.items(content.get("lessons"))) {
      lessons.put(l.get("id").toString(), l);
      store.put(l.get("id").toString(), "lesson", "public", l);
    }
    for (var p : Store.items(content.get("problems"))) {
      problems.put(p.get("id").toString(), p);
      store.put(p.get("id").toString(), "problem", "public", p);
    }
  }

  /** A deep copy, so a test can break one record without touching the others. */
  Map<String, Object> copy(Map<String, Object> value) {
    var json = new ObjectMapper();
    return json.readValue(json.writeValueAsString(value), Map.class);
  }

  static List<String> messages(Map<String, Object> checks, String list) {
    return Store.items(checks.get(list)).stream().map(i -> i.get("field") + ": " + i.get("message")).toList();
  }

  @Test
  void theWholeCatalogueSavesAndEveryCoreLessonAndProblemIsPublishable() {
    for (var l : lessons.values()) {
      var checks = admin.check(l);
      assertEquals(List.of(), messages(checks, "errors"), l.get("id").toString());
      if ("core".equals(l.get("branch"))) assertEquals(List.of(), messages(checks, "publication"), l.get("id").toString());
    }
    for (var p : problems.values()) {
      var checks = admin.check(p);
      assertEquals(List.of(), messages(checks, "errors"), p.get("id").toString());
      assertEquals(List.of(), messages(checks, "publication"), p.get("id").toString());
    }
  }

  @Test
  @SuppressWarnings("unchecked")
  void brokenChallengesAreCaughtTheWayTheGraderWouldFailThem() {
    var lesson = copy(lessons.get("lesson-sliding-window"));
    var challenges = (List<Map<String, Object>>) lesson.get("challenges");
    var dry = challenges.stream().filter(c -> "dry-run".equals(c.get("kind"))).findFirst().orElseThrow();
    dry.put("fields", List.of(Map.of("key", "nonsense", "label", "Nonsense")));
    var pattern = challenges.stream().filter(c -> "pattern".equals(c.get("kind"))).findFirst().orElseThrow();
    pattern.put("answer", 9);
    challenges.add(new LinkedHashMap<>(challenges.getFirst()));

    var errors = String.join("\n", messages(admin.check(lesson), "errors"));
    assertTrue(errors.contains("has no variable “nonsense”"), errors);
    assertTrue(errors.contains("index of one option"), errors);
    assertTrue(errors.contains("unique id"), errors);
    var refused = assertThrows(IllegalArgumentException.class, () -> admin.save(lesson));
    assertTrue(refused.getMessage().startsWith("Fix before saving"), refused.getMessage());

    var outOfRange = copy(lessons.get("lesson-sliding-window"));
    ((List<Map<String, Object>>) outOfRange.get("challenges")).stream().filter(c -> "dry-run".equals(c.get("kind"))).findFirst().orElseThrow().put("traceStep", 999);
    assertTrue(String.join(" ", messages(admin.check(outOfRange), "errors")).contains("traceStep must be between 0 and"));
  }

  @Test
  void anUnfinishedCoreLessonSavesAsADraftButCannotBePublished() {
    var lesson = copy(lessons.get("lesson-stack"));
    lesson.put("blocks", Store.items(lesson.get("blocks")).subList(0, 1));
    var checks = admin.check(lesson);
    assertEquals(true, checks.get("canSave"));
    assertEquals(false, checks.get("canPublish"));
    assertTrue(String.join(" ", messages(checks, "publication")).contains("worked, invariant and tradeoff"));

    var refused = assertThrows(IllegalArgumentException.class, () -> admin.save(lesson));
    assertTrue(refused.getMessage().startsWith("Not ready to publish"), refused.getMessage());
    lesson.put("published", false);
    assertEquals(false, admin.save(lesson).get("published"));
    assertEquals(true, store.get("lesson-stack").get("edited"));

    // the same gap on an advanced lesson is advice, not a block
    var advanced = copy(lessons.get("lesson-avl"));
    advanced.put("blocks", Store.items(advanced.get("blocks")).subList(0, 1));
    var advice = admin.check(advanced);
    assertEquals(true, advice.get("canPublish"));
    assertTrue(String.join(" ", messages(advice, "warnings")).contains("worked, invariant and tradeoff"));
  }

  @Test
  @SuppressWarnings("unchecked")
  void problemsNeedMatchingReferencesSpecificHintsAndAHiddenCaseToPublish() {
    var problem = copy(problems.get("problem-trapped-rain"));
    ((Map<String, Object>) problem.get("references")).remove("python");
    problem.put("hints", List.of("Think.", "Try harder."));
    var checks = admin.check(problem);
    var publication = String.join(" ", messages(checks, "publication"));
    assertTrue(publication.contains("Python reference") && publication.contains("three specific hints"), publication);
    assertEquals(true, checks.get("canSave"));

    ((Map<String, Object>) problem.get("references")).put("java", "class Main {}");
    assertTrue(String.join(" ", messages(admin.check(problem), "errors")).contains("references.java must equal reference"));

    var allPublic = copy(problems.get("problem-trapped-rain"));
    for (var t : (List<Map<String, Object>>) allPublic.get("tests")) t.put("public", true);
    assertTrue(String.join(" ", messages(admin.check(allPublic), "publication")).contains("hidden test"));
  }
}
