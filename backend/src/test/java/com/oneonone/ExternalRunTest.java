package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/** External bank questions run on the learner's own input only; they are never judged here. */
class ExternalRunTest {

  Store store;
  BankService bank;
  ExecutionService execution;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    bank = new BankService(store);
    execution = new ExecutionService(store, new ProgressService(store));
    // configured but unreachable: submit stores the job, and the background run later marks it unavailable
    execution.url = "http://127.0.0.1:1";
    execution.mode = "rapidapi";
    execution.key = "test";
    execution.host = "test";
    execution.bank = bank;
  }

  Map<String, Object> run(boolean official) {
    var body = new HashMap<String, Object>();
    body.put("problem", "cf-1000A");
    body.put("language", "python");
    body.put("code", "print(input())");
    body.put("input", "hello");
    body.put("official", official);
    body.put("requestId", "request-" + UUID.randomUUID());
    return execution.submit("learner", body);
  }

  @Test
  void bankQuestionsAreLookedUpById() {
    assertTrue(bank.external("cf-1000A").isPresent());
    assertEquals("Codeforces", bank.external("cf-1000A").get().get("source"));
    assertTrue(bank.external("cf-nope").isEmpty());
  }

  @Test
  void anExternalQuestionRunsOnTheLearnersInputButIsNeverJudged() {
    var refused = assertThrows(IllegalArgumentException.class, () -> run(true));
    assertEquals("External questions run on your own input; they are judged on their own site.", refused.getMessage());
    assertEquals(0, store.list("submission", "learner").size(), "a refused official run stores nothing");

    var job = run(false);
    var stored = store.get(job.get("id").toString());
    assertEquals(false, stored.get("official"));
    assertEquals("cf-1000A", stored.get("problem"));
    var fixtures = Store.items(stored.get("fixtures"));
    assertEquals(1, fixtures.size());
    assertEquals("hello", fixtures.getFirst().get("input"));
  }
}
