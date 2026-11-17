package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Timed mock assessments, scored only from official accepted runs inside the window. */
class MockTest {

  static final String U = "learner";
  Store store;
  MockService mocks;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var p : Store.items(content.get("problems"))) store.put(p.get("id").toString(), "problem", "public", p);
    mocks = new MockService(store, new BankService(store));
  }

  void submit(String problem, String status, boolean official, Instant at) {
    store.put("submission-" + UUID.randomUUID(), "submission", U, Map.of("problem", problem, "official", official, "status", status, "createdAt", at.toString(), "code", "x", "language", "java"));
  }

  @SuppressWarnings("unchecked")
  List<Map<String, Object>> problems(Map<String, Object> view) {
    return (List<Map<String, Object>>) view.get("problems");
  }

  /** Moves the attempt's window so tests can place submissions around it. */
  void window(String id, Instant start, Instant deadline) {
    var doc = new LinkedHashMap<>(store.get(id));
    doc.put("startedAt", start.toString());
    doc.put("deadline", deadline.toString());
    store.put(id, "mock", U, doc);
  }

  @Test
  void aMixedMockPicksOneProblemPerDifficultyWithoutRepeats() {
    var view = mocks.start(U, 3, 60, "mixed");
    var picked = problems(view);
    assertEquals(3, picked.size());
    assertEquals(Set.of("Easy", "Medium", "Hard"), new HashSet<>(picked.stream().map(p -> p.get("difficulty")).toList()));
    assertEquals(3, new HashSet<>(picked.stream().map(p -> p.get("id")).toList()).size());
    assertEquals(false, view.get("finished"));
    assertTrue(((Number) view.get("remainingSeconds")).intValue() > 3500);
    assertThrows(IllegalArgumentException.class, () -> mocks.start(U, 4, 60, "mixed"));
    assertThrows(IllegalArgumentException.class, () -> mocks.start(U, 3, 45, "mixed"));
    assertThrows(IllegalArgumentException.class, () -> mocks.start(U, 3, 60, "No Such Company Inc"));
  }

  @Test
  void onlyOfficialAcceptedRunsInsideTheWindowCount() {
    var view = mocks.start(U, 2, 60, "mixed");
    String id = view.get("id").toString();
    Instant start = Instant.now().minusSeconds(600), deadline = start.plusSeconds(3600);
    window(id, start, deadline);
    var ids = problems(view).stream().map(p -> p.get("id").toString()).toList();
    submit(ids.get(0), "ACCEPTED", true, start.minusSeconds(1));
    submit(ids.get(0), "ACCEPTED", false, start.plusSeconds(60));
    submit(ids.get(0), "WRONG_ANSWER", true, start.plusSeconds(60));
    assertEquals(0, ((Number) mocks.view(U, id).get("score")).intValue());
    submit(ids.get(1), "ACCEPTED", true, start.plusSeconds(120));
    var scored = mocks.view(U, id);
    assertEquals(1, ((Number) scored.get("score")).intValue());
    assertEquals(true, problems(scored).stream().filter(p -> p.get("id").equals(ids.get(1))).findFirst().orElseThrow().get("accepted"));
    assertEquals(0, store.db.queryForObject("select count(*) from solved_credits", Integer.class), "the mock never writes credit");
  }

  @Test
  void finishingOrPassingTheDeadlineLocksTheAttempt() {
    var view = mocks.start(U, 2, 60, "mixed");
    String id = view.get("id").toString();
    var ids = problems(view).stream().map(p -> p.get("id").toString()).toList();
    mocks.signal(U, id, "tab");
    mocks.finish(U, id);
    submit(ids.get(0), "ACCEPTED", true, Instant.now().plusSeconds(5));
    mocks.signal(U, id, "tab");
    var done = mocks.view(U, id);
    assertEquals(true, done.get("finished"));
    assertEquals(0, ((Number) done.get("score")).intValue());
    assertEquals(1, ((Number) ((Map<?, ?>) done.get("signals")).get("tabSwitches")).intValue());

    var other = mocks.start(U, 2, 60, "mixed");
    String late = other.get("id").toString();
    Instant start = Instant.now().minusSeconds(7200);
    window(late, start, start.plusSeconds(3600));
    submit(problems(other).getFirst().get("id").toString(), "ACCEPTED", true, start.plusSeconds(4000));
    var expired = mocks.view(U, late);
    assertEquals(true, expired.get("finished"));
    assertEquals(0, ((Number) expired.get("remainingSeconds")).intValue());
    assertEquals(0, ((Number) expired.get("score")).intValue(), "a run after the deadline does not count");
  }

  @Test
  void problemsOutsideTheMockNeverCountTowardsItsScore() {
    var view = mocks.start(U, 2, 60, "mixed");
    String id = view.get("id").toString();
    var chosen = problems(view).stream().map(p -> p.get("id").toString()).toList();
    String other = store.list("problem", "public").stream().map(p -> p.get("id").toString()).filter(p -> !chosen.contains(p)).findFirst().orElseThrow();
    submit(other, "ACCEPTED", true, Instant.now());
    assertEquals(0, ((Number) mocks.view(U, id).get("score")).intValue());
  }

  @Test
  void mocksAreReadOnlyThroughTheirOwnKind() {
    store.put("submission-x", "submission", U, Map.of("problem", "p", "official", true, "status", "ACCEPTED", "createdAt", Instant.now().toString()));
    var error = assertThrows(ResponseStatusException.class, () -> mocks.view(U, "submission-x"));
    assertEquals(404, error.getStatusCode().value());
  }

  @Test
  void anotherLearnersAttemptIsNotFound() {
    String id = mocks.start(U, 2, 60, "mixed").get("id").toString();
    var error = assertThrows(ResponseStatusException.class, () -> mocks.view("someone-else", id));
    assertEquals(404, error.getStatusCode().value());
  }

  @Test
  void aCompanyStyleMockAlwaysFillsTheRequestedSize() {
    var view = mocks.start(U, 3, 90, "Google");
    assertEquals(3, problems(view).size());
    assertEquals("Google", view.get("style"));
    assertEquals(3, MockService.allocate(Map.of("Easy", 10L, "Medium", 5L), 3).values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(Map.of("Easy", 2, "Medium", 1), MockService.allocate(Map.of("Easy", 10L, "Medium", 5L), 3));
  }
}
