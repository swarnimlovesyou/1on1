package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/** The question bank over the generated external metadata and 1on1's own problems. */
class BankTest {

  BankService bank;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    var source = new String(getClass().getResourceAsStream("/db/migration/V1__initial.sql").readAllBytes(), StandardCharsets.UTF_8);
    for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    var store = new Store(db);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var p : Store.items(content.get("problems"))) store.put(p.get("id").toString(), "problem", "public", p);
    bank = new BankService(store);
  }

  static List<Map<String, Object>> items(Map<String, Object> page) {
    return Store.items(page.get("items"));
  }

  @Test
  void ownProblemsComeFirstAboveElevenThousandExternalOnes() {
    var page = bank.search("", "", "", "", "", 0, 25);
    assertTrue(((Number) page.get("total")).intValue() >= 11000, page.get("total").toString());
    assertEquals("1on1", items(page).getFirst().get("source"));
    assertTrue(items(page).getFirst().get("url").toString().startsWith("/practice/problem-"));
  }

  @Test
  void filtersBySourceAndDifficulty() {
    var page = bank.search("", "codeforces", "hard", "", "", 0, 50);
    assertFalse(items(page).isEmpty());
    for (var r : items(page)) {
      assertEquals("Codeforces", r.get("source"));
      assertEquals("Hard", r.get("difficulty"));
    }
  }

  @Test
  void aCompanyFilterKeepsThatCompanysQuestionsMostReportedFirst() {
    var rows = items(bank.search("", "", "", "", "Google", 0, 100));
    assertFalse(rows.isEmpty());
    int last = Integer.MAX_VALUE;
    for (var r : rows) {
      int count = ((Number) ((Map<?, ?>) r.get("companies")).get("Google")).intValue();
      assertTrue(count <= last, "sorted by report count");
      last = count;
    }
  }

  @Test
  void noMatchOrAPagePastTheEndIsAnEmptyPageNotAnError() {
    var none = bank.search("zzzz-no-such-title", "", "", "", "", 0, 25);
    assertEquals(0, ((Number) none.get("total")).intValue());
    assertTrue(items(none).isEmpty());
    var beyond = bank.search("", "", "", "", "", 9999, 25);
    assertTrue(items(beyond).isEmpty());
    assertTrue(((Number) beyond.get("total")).intValue() > 0);
    assertEquals(100, ((Number) bank.search("", "", "", "", "", 0, 1000).get("size")).intValue());
  }

  @Test
  void topicsAreOfferedAndCompanyFiltersIgnoreCase() {
    var topics = bank.topics();
    assertTrue(topics.contains("greedy") && topics.contains("Arrays"), topics.toString());
    for (var r : items(bank.search("", "", "", "greedy", "", 0, 20))) assertTrue(Store.strings(r.get("tags")).contains("greedy"));
    assertEquals(bank.search("", "", "", "", "Google", 0, 1).get("total"), bank.search("", "", "", "", "google", 0, 1).get("total"));
  }

  @Test
  void companiesAreListedWithCountsAndAMixPerDifficulty() {
    var companies = bank.companies();
    assertFalse(companies.isEmpty());
    var google = companies.stream().filter(c -> "Google".equals(c.get("name"))).findFirst().orElseThrow();
    assertTrue(((Number) google.get("count")).intValue() > 0);
    var mix = bank.difficultyMix("Google");
    // a few source rows have no difficulty; the mix counts only rated ones
    long rated = mix.values().stream().mapToLong(Long::longValue).sum();
    assertTrue(rated > 0 && rated <= ((Number) google.get("count")).longValue(), mix.toString());
    assertTrue(mix.keySet().stream().allMatch(Set.of("Easy", "Medium", "Hard")::contains), mix.toString());
  }
  static int score(Map<String, Object> r) {
    return BankService.difficultyScore(r);
  }

  @Test
  void sortingByDifficultyPutsUnratedLastAndStaysStableAcrossPages() {
    var all = items(bank.search("", "", "", "", "", 0, 100, "easiest"));
    for (int i = 1; i < all.size(); i++) assertTrue(score(all.get(i - 1)) <= score(all.get(i)), "easiest first at " + i);
    var hardest = items(bank.search("", "", "", "", "", 0, 100, "hardest"));
    assertTrue(score(hardest.get(0)) >= score(hardest.get(1)));
    int total = ((Number) bank.search("", "", "", "", "", 0, 1, "hardest").get("total")).intValue();
    var tail = items(bank.search("", "", "", "", "", (total - 1) / 100, 100, "hardest"));
    assertEquals(Integer.MAX_VALUE, score(tail.getLast()), "unrated questions come last under hardest too");
    var ratedFirst = items(bank.search("", "", "", "", "", 0, 100, "hardest"));
    for (int i = 1; i < ratedFirst.size(); i++) assertTrue(score(ratedFirst.get(i - 1)) >= score(ratedFirst.get(i)), "hardest first at " + i);
    var first = items(bank.search("", "Codeforces", "", "", "", 0, 30, "easiest"));
    var second = items(bank.search("", "Codeforces", "", "", "", 1, 30, "easiest"));
    var both = items(bank.search("", "Codeforces", "", "", "", 0, 60, "easiest"));
    var joined = new ArrayList<>(first);
    joined.addAll(second);
    assertEquals(both.stream().map(r -> r.get("id")).toList(), joined.stream().map(r -> r.get("id")).toList(), "pages join without gaps or repeats");
  }

  @Test
  void sortingByTitleIsAlphabeticalAndAnUnknownSortFallsBackToRelevance() {
    var titles = items(bank.search("", "LeetCode", "", "", "", 0, 50, "title")).stream().map(r -> r.get("title").toString()).toList();
    var sorted = new ArrayList<>(titles);
    sorted.sort(String.CASE_INSENSITIVE_ORDER);
    assertEquals(sorted, titles);
    assertEquals(items(bank.search("", "", "", "", "", 0, 25)).stream().map(r -> r.get("id")).toList(),
      items(bank.search("", "", "", "", "", 0, 25, "nonsense")).stream().map(r -> r.get("id")).toList());
  }
}
