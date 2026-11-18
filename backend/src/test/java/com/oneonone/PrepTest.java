package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Prep guides: served without answers, quizzes graded by the existing challenge engine, invisible to DSA evidence. */
class PrepTest {

  Store store;
  ChallengeService challenges;
  PrepController prep;

  static Map<String, Object> question(int n) {
    return new LinkedHashMap<>(Map.of(
      "id", "challenge-test-guide-q" + n, "kind", "prediction", "title", "Question " + n, "prompt", "Pick B",
      "options", List.of("A", "B", "C"), "answer", 1, "explanation", "B is right.", "hint", "Not A."
    ));
  }

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
    var questions = new ArrayList<Map<String, Object>>();
    for (int i = 1; i <= 5; i++) questions.add(question(i));
    store.put("guide-cs-fundamentals-test", "guide", "public", Map.of(
      "kind", "guide", "track", "cs-fundamentals", "subject", "OOP", "title", "Test guide", "order", 1, "summary", "s",
      "sections", List.of(Map.of("title", "One", "text", "t")), "keyPoints", List.of("k"), "challenges", questions
    ));
    challenges = new ChallengeService(store, new TraceEngine(), new ProgressService(store));
    prep = new PrepController(store, new ProgressService(store));
  }

  int attempts() {
    return store.db.queryForObject("select count(*) from challenge_attempts", Integer.class);
  }

  @Test
  void aGuestIsGradedButNothingIsStored() {
    var result = challenges.attempt(null, "challenge-test-guide-q1", new Contracts.AttemptRequest(1, UUID.randomUUID().toString()));
    assertTrue(result.correct());
    assertFalse(challenges.attempt(null, "challenge-test-guide-q1", new Contracts.AttemptRequest(0, UUID.randomUUID().toString())).correct());
    assertEquals(0, attempts());
  }

  @Test
  void aLearnersAttemptIsStoredAgainstTheGuideButNeverReachesTheConceptMap() throws Exception {
    challenges.attempt("learner", "challenge-test-guide-q2", new Contracts.AttemptRequest(1, UUID.randomUUID().toString()));
    assertEquals("guide-cs-fundamentals-test", store.db.queryForObject("select lesson_id from challenge_attempts", String.class));
    var map = new LearningMapService(store).map("learner");
    assertEquals(40, Store.items(map.get("concepts")).size());
    assertTrue(Store.items(map.get("reviewsDue")).isEmpty());
  }

  @Test
  void theGuideIsServedWithoutAnswersAndUnknownIdsAreNotFound() {
    var guide = prep.guide("guide-cs-fundamentals-test");
    for (var c : Store.items(guide.get("challenges"))) assertFalse(c.containsKey("answer"), c.toString());
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> prep.guide("guide-nope")).getStatusCode().value());
    var overview = prep.overview();
    var listed = Store.items(overview.get("guides"));
    assertEquals(1, listed.size());
    assertEquals(5, Store.strings(listed.getFirst().get("challengeIds")).size());
    assertFalse(listed.getFirst().containsKey("sections"), "the overview lists guides without their text");
  }
  @Test
  void aGuideRemovedFromContentIsUnpublishedUnlessAnAdminEditedIt() throws Exception {
    store.put("guide-cs-fundamentals-stale", "guide", "public", Map.of("kind", "guide", "track", "cs-fundamentals", "title", "Stale"));
    store.put("guide-cs-fundamentals-kept", "guide", "public", Map.of("kind", "guide", "track", "cs-fundamentals", "title", "Kept", "edited", true));
    var seed = new ContentSeed(store, new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder());
    seed.adminEmail = "";
    seed.adminPassword = "";
    seed.run();
    assertEquals(false, store.get("guide-cs-fundamentals-stale").get("published"));
    assertNotEquals(false, store.get("guide-cs-fundamentals-kept").get("published"));
    var listed = Store.items(prep.overview().get("guides")).stream().map(g -> g.get("id")).toList();
    assertFalse(listed.contains("guide-cs-fundamentals-stale"));
    assertTrue(listed.contains("guide-cs-fundamentals-kept"));
  }
  @Test
  void theOverviewTellsWhichDrillAGuidePractises() {
    var questions = new ArrayList<Map<String, Object>>();
    for (int i = 1; i <= 5; i++) questions.add(question(i + 10));
    store.put("guide-aptitude-test", "guide", "public", Map.of("kind", "guide", "track", "aptitude", "title", "Percentages", "order", 1,
      "summary", "s", "drill", "percentages", "challenges", questions));
    var row = Store.items(prep.overview().get("guides")).stream().filter(g -> "guide-aptitude-test".equals(g.get("id"))).findFirst().orElseThrow();
    assertEquals("percentages", row.get("drill"));
  }
  void puzzle(String id, String answer) {
    var block = new LinkedHashMap<String, Object>(Map.of("statement", "s", "hints", List.of("a", "b"), "solution", List.of("x", "y")));
    if (answer != null) block.put("answer", answer);
    store.put(id, "guide", "public", Map.of("kind", "guide", "track", "puzzles", "title", "P", "order", 1, "summary", "s", "puzzle", block));
  }

  int puzzleEvents() {
    return store.db.queryForObject("select count(*) from learning_events where kind='puzzle'", Integer.class);
  }

  @Test
  void aPuzzleAnswerIsCheckedOnTheServerAndNeverSentAhead() {
    puzzle("guide-puzzles-coins", "17");
    assertEquals(Map.of("correct", true), prep.check(null, "guide-puzzles-coins", Map.of("answer", " 17 ")));
    assertEquals(Map.of("correct", true), prep.check(null, "guide-puzzles-coins", Map.of("answer", "17.0")));
    assertEquals(Map.of("correct", false), prep.check(null, "guide-puzzles-coins", Map.of("answer", "seventeen")));
    assertEquals(0, puzzleEvents(), "a guest's answer is not recorded");
    prep.check("user-1", "guide-puzzles-coins", Map.of("answer", "16"));
    assertEquals(0, puzzleEvents(), "a wrong answer is not recorded");
    prep.check("user-1", "guide-puzzles-coins", Map.of("answer", "17"));
    assertEquals(1, puzzleEvents());
    var served = (Map<?, ?>) prep.guide("guide-puzzles-coins").get("puzzle");
    assertFalse(served.containsKey("answer"));
    assertEquals(true, served.get("checkable"));
  }

  @Test
  void checkingSomethingThatIsNotACheckablePuzzleSaysWhy() {
    puzzle("guide-puzzles-open", null);
    for (var call : List.<Runnable>of(
      () -> prep.check(null, "guide-puzzles-missing", Map.of("answer", "1")),
      () -> prep.check(null, "guide-cs-fundamentals-test", Map.of("answer", "1"))
    )) assertEquals(404, assertThrows(ResponseStatusException.class, call::run).getStatusCode().value());
    var none = assertThrows(ResponseStatusException.class, () -> prep.check(null, "guide-puzzles-open", Map.of("answer", "1")));
    assertEquals(400, none.getStatusCode().value());
    assertEquals("This puzzle has no single answer to check.", none.getReason());
    puzzle("guide-puzzles-coins", "17");
    assertEquals(400, assertThrows(ResponseStatusException.class, () -> prep.check(null, "guide-puzzles-coins", Map.of("answer", "  "))).getStatusCode().value());
  }
}
