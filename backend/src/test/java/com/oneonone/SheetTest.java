package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Curated sheets (Blind 75, NeetCode 150): public lists, ticks kept per learner. */
class SheetTest {

  SheetController sheets;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    sheets = new SheetController(new Store(db));
  }

  int status(Runnable call) {
    return assertThrows(ResponseStatusException.class, call::run).getStatusCode().value();
  }

  @Test
  void theListShowsEachSheetWithItsCountAndCredit() {
    var list = sheets.list();
    assertEquals(List.of("blind-75", "neetcode-150"), list.stream().map(s -> s.get("id")).toList());
    assertEquals(75, list.get(0).get("count"));
    assertEquals(150, list.get(1).get("count"));
    assertTrue(list.get(0).get("credit").toString().contains("MIT"));
    assertFalse(list.get(0).containsKey("items"), "the list is light; items come with one sheet");
  }

  @Test
  void oneSheetHasItsItemsAndUnknownSheetsAreNotFound() {
    var blind = sheets.sheet("blind-75");
    var items = Store.items(blind.get("items"));
    assertEquals(75, items.size());
    assertTrue(items.stream().allMatch(i -> i.get("id").toString().startsWith("lc-") && i.get("url").toString().startsWith("https://leetcode.com/problems/")));
    assertEquals(404, status(() -> sheets.sheet("striver-a2z")));
  }

  @Test
  void ticksAreKeptPerLearnerAndOnlyForItemsOnASheet() {
    String id = Store.items(sheets.sheet("neetcode-150").get("items")).get(3).get("id").toString();
    assertEquals(List.of(), sheets.ticks("user-1").get("done"));
    sheets.tick("user-1", id, Map.of("done", true));
    sheets.tick("user-1", id, Map.of("done", true));
    assertEquals(List.of(id), sheets.ticks("user-1").get("done"));
    assertEquals(List.of(), sheets.ticks("user-2").get("done"), "another learner's ticks are separate");
    sheets.tick("user-1", id, Map.of("done", false));
    assertEquals(List.of(), sheets.ticks("user-1").get("done"));
    assertEquals(404, status(() -> sheets.tick("user-1", "lc-not-on-any-sheet", Map.of("done", true))));
    assertEquals(400, status(() -> sheets.tick("user-1", id, Map.of())));
  }
  @Test
  void aLeetCodeSyncTicksAcceptedSheetQuestionsAndIgnoresTheRest() {
    var items = Store.items(sheets.sheet("blind-75").get("items"));
    String a = items.get(0).get("id").toString(), b = items.get(1).get("id").toString();
    sheets.tick("user-1", a, Map.of("done", true));
    assertEquals(1, sheets.tickAll("user-1", List.of(a, b, "lc-not-on-any-sheet")), "only the new sheet question counts");
    assertEquals(List.of(a, b), sheets.ticks("user-1").get("done"), "existing ticks are kept, in order");
    assertEquals(0, sheets.tickAll("user-1", List.of()));
    assertEquals(0, sheets.tickAll("user-2", List.of("lc-not-on-any-sheet")));
    assertEquals(List.of(), sheets.ticks("user-2").get("done"));
  }

  @Test
  void recentAcceptedSubmissionsBecomeBankIds() {
    Map<String, Object> data = Map.of("recentAcSubmissionList", List.of(
      Map.of("titleSlug", "two-sum", "title", "Two Sum"),
      Map.of("titleSlug", "two-sum", "title", "Two Sum"),
      Map.of("title", "No slug")
    ));
    assertEquals(List.of("lc-two-sum"), LeetcodeController.acceptedIds(data));
    assertEquals(List.of(), LeetcodeController.acceptedIds(Map.of()));
  }
}
