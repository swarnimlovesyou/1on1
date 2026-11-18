package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Admin tools for a local install without email: hand-delivered reset links and removing learner reports. */
class AdminToolsTest {

  Store store;
  AdminController admin;
  ReportController reports;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    db.update("insert into members(id,email,name,password,role) values('m1','ana@example.test','Ana','x','learner')");
    admin = new AdminController(store, null, null);
    reports = new ReportController(store, new BankService(store));
  }

  @Test
  void anAdminCanIssueAOneTimeResetLinkForAKnownEmailOnly() {
    var out = admin.resetLink(Map.of("email", " ANA@example.test "));
    String link = out.get("path").toString();
    assertTrue(link.startsWith("/reset-password?token="));
    String token = link.substring(link.indexOf('=') + 1);
    assertEquals(1, store.db.queryForObject("select count(*) from reset_tokens where token_hash=? and member_id='m1'", Integer.class, AuthController.sha256(token)));
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> admin.resetLink(Map.of("email", "nobody@example.test"))).getStatusCode().value());
  }

  @Test
  void anAdminCanListAndRemoveLearnerReports() {
    reports.report("m1", Map.of("questionId", "lc-two-sum", "company", "Google", "stage", "OA"));
    var listed = admin.reports();
    assertEquals(1, listed.size());
    assertEquals("Ana", listed.getFirst().get("member"));
    admin.deleteReport(listed.getFirst().get("id").toString());
    assertTrue(admin.reports().isEmpty());
    assertTrue(reports.recent().isEmpty());
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> admin.deleteReport("lesson-arrays")).getStatusCode().value(), "only reports can be removed here");
  }
}
