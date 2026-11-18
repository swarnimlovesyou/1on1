package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Learners' own "I was asked this" reports: fresh, owned company data, kept apart from the 2022 dataset. */
class ReportTest {

  ReportController reports;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    var store = new Store(db);
    reports = new ReportController(store, new BankService(store));
  }

  int status(Runnable call) {
    return assertThrows(ResponseStatusException.class, call::run).getStatusCode().value();
  }

  @Test
  void reportsAreAggregatedNewestFirstAndRepeatsCountOnce() {
    reports.report("u1", Map.of("questionId", "lc-two-sum", "company", "Google", "stage", "Interview"));
    reports.report("u1", Map.of("questionId", "lc-two-sum", "company", "google", "stage", "Interview"));
    reports.report("u2", Map.of("questionId", "lc-two-sum", "company", "Google", "stage", "OA"));
    reports.report("u2", Map.of("questionId", "cf-1000A", "company", "Flipkart", "stage", "OA"));
    reports.report("u3", Map.of("questionId", "lc-two-sum", "company", "Qqzx Spam", "stage", "OA"));
    var recent = reports.recent();
    assertEquals(2, recent.size(), "an unknown company reported by one learner stays hidden");
    var twoSum = recent.stream().filter(r -> "lc-two-sum".equals(r.get("questionId"))).findFirst().orElseThrow();
    assertEquals("Two Sum", twoSum.get("title"));
    assertEquals("Google", twoSum.get("company"));
    assertEquals(2, twoSum.get("reports"), "two learners, the repeat by u1 counts once");
    assertEquals("LeetCode", twoSum.get("source"));
    assertTrue(twoSum.get("month").toString().matches("[0-9]{4}-[0-9]{2}"));
  }

  @Test
  void badReportsAreRejectedWithASentence() {
    assertEquals(404, status(() -> reports.report("u1", Map.of("questionId", "lc-not-real", "company", "Google", "stage", "OA"))));
    for (String company : List.of("", "x", "<script>", "A".repeat(41)))
      assertEquals(400, status(() -> reports.report("u1", Map.of("questionId", "lc-two-sum", "company", company, "stage", "OA"))), company);
    assertEquals(400, status(() -> reports.report("u1", Map.of("questionId", "lc-two-sum", "company", "Google", "stage", "Coffee"))));
    assertTrue(reports.recent().isEmpty());
  }
}
