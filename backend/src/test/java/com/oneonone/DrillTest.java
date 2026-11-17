package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Generated aptitude and reasoning drills: deterministic per seed, graded on the server, answers never sent early. */
class DrillTest {

  Store store;
  DrillService drills;
  static final Set<String> TEXT_TOPICS = Set.of("letter-series", "coding-decoding", "syllogisms");

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    drills = new DrillService(new ProgressService(store));
  }

  int events() {
    return store.db.queryForObject("select count(*) from learning_events where kind='drill'", Integer.class);
  }

  HttpStatus status(Runnable call) {
    var e = assertThrows(ResponseStatusException.class, call::run);
    assertNotNull(e.getReason(), "errors carry a sentence");
    return HttpStatus.valueOf(e.getStatusCode().value());
  }

  @Test
  void thereAreEightAptitudeAndFiveReasoningTopics() {
    assertEquals(List.of("percentages", "profit-loss", "ratio-proportion", "averages", "interest", "time-work", "speed-distance",
      "number-systems", "number-series", "letter-series", "coding-decoding", "directions", "syllogisms"), List.copyOf(DrillService.TOPICS.keySet()));
    assertEquals(8, DrillService.TOPICS.values().stream().filter("aptitude"::equals).count());
    assertEquals(5, DrillService.TOPICS.values().stream().filter("reasoning"::equals).count());
  }

  @Test
  void everyTopicIsDeterministicAndSelfConsistent() {
    for (String topic : DrillService.TOPICS.keySet()) {
      Set<String> prompts = new HashSet<>();
      for (int seed = 0; seed < 300; seed++) {
        var d = drills.generate(topic, seed);
        assertEquals(d, drills.generate(topic, seed), topic + " " + seed);
        assertFalse(d.prompt().isBlank());
        assertFalse(d.explanation().isBlank());
        assertTrue(DrillService.matches(d.answer(), d.answer()));
        if (d.options() != null) {
          assertEquals(4, new HashSet<>(d.options()).size(), topic + " " + seed);
          assertTrue(d.options().contains(d.answer()));
        }
        if (!TEXT_TOPICS.contains(topic)) assertTrue(Integer.parseInt(d.answer()) >= 0, topic + " " + seed + ": " + d.answer());
        prompts.add(d.prompt());
      }
      assertTrue(prompts.size() >= 15, topic + " varies with the seed: " + prompts.size());
    }
  }

  @Test
  void gradingAcceptsFormatButNotWrongValues() {
    assertTrue(DrillService.matches("1200", " 1,200 "));
    assertTrue(DrillService.matches("40", "40.0"));
    assertTrue(DrillService.matches("ECV", "ecv"));
    assertTrue(DrillService.matches("Only I follows", " only i follows"));
    assertFalse(DrillService.matches("40", "41"));
    assertFalse(DrillService.matches("40", "forty"));
    assertFalse(DrillService.matches("ECV", "ECW"));
  }

  @Test
  void aNumberTypedWithItsUnitIsStillRight() {
    assertTrue(DrillService.matches("15", "15%"));
    assertTrue(DrillService.matches("15", "15 %"));
    assertTrue(DrillService.matches("1200", "₹1,200"));
    assertTrue(DrillService.matches("1200", "Rs 1200"));
    assertTrue(DrillService.matches("1200", "rs. 1200"));
    assertTrue(DrillService.matches("12", "12 days"));
    assertTrue(DrillService.matches("10", "10 seconds"));
    assertTrue(DrillService.matches("5", "5 m"));
    assertFalse(DrillService.matches("40", "41%"));
    assertFalse(DrillService.matches("40", "forty"));
    assertFalse(DrillService.matches("40", "%"));
  }

  @Test
  void knownValues() {
    assertEquals("8", DrillService.timeWork(12, 24).answer());
    assertEquals("10", DrillService.trainPole(150, 54).answer());
    assertEquals("210", DrillService.compoundInterest(1000, 10).answer());
    assertEquals("ECV", DrillService.shift("CAT", 2));
    assertEquals("YZR", DrillService.shift("BCU", -3));
    var s3 = DrillService.syllogism(3, "cats", "dogs", "birds");
    assertEquals("Only I follows", s3.answer());
    assertTrue(s3.prompt().contains("No cats are dogs."), s3.prompt());
    assertEquals("Neither follows", DrillService.syllogism(7, "cats", "dogs", "birds").answer());
    assertEquals("Both follow", DrillService.syllogism(1, "cats", "dogs", "birds").answer());
  }

  @Test
  void nextHidesTheAnswerAndAnswerGradesIt() {
    var next = drills.next("percentages", "42");
    assertEquals(42, next.get("seed"));
    assertEquals("percentages", next.get("topic"));
    assertFalse(next.containsKey("answer"));
    assertFalse(next.containsKey("explanation"));
    var expected = drills.generate("percentages", 42).answer();
    assertEquals(true, drills.answer(null, "percentages", 42, expected).get("correct"));
    var wrong = drills.answer(null, "percentages", 42, expected + "1");
    assertEquals(false, wrong.get("correct"));
    assertEquals(expected, wrong.get("expected"));
    assertNotNull(drills.next("syllogisms", null).get("seed"), "a missing seed gets a random one");
  }

  @Test
  void badRequestsAreRejectedWithASentence() {
    assertEquals(HttpStatus.NOT_FOUND, status(() -> drills.next("calculus", "1")));
    assertEquals(HttpStatus.NOT_FOUND, status(() -> drills.answer(null, "calculus", 1, "3")));
    for (String seed : List.of("abc", "-1", "99999999999", "1.5"))
      assertEquals(HttpStatus.BAD_REQUEST, status(() -> drills.next("averages", seed)), seed);
    assertEquals(HttpStatus.BAD_REQUEST, status(() -> drills.answer(null, "averages", null, "3")));
    assertEquals(HttpStatus.BAD_REQUEST, status(() -> drills.answer(null, "averages", 1, "  ")));
    assertEquals(HttpStatus.BAD_REQUEST, status(() -> drills.answer(null, "averages", 1, null)));
  }

  @Test
  void aGuestIsGradedAndNothingIsRecorded() {
    drills.answer(null, "directions", 7, "5");
    assertEquals(0, events());
  }

  @Test
  void aLearnerLogsOneDrillEventPerTopicPerDay() {
    drills.answer("user-1", "directions", 7, "5");
    drills.answer("user-1", "directions", 8, "5");
    assertEquals(1, events());
    drills.answer("user-1", "averages", 8, "5");
    assertEquals(2, events());
  }
}
