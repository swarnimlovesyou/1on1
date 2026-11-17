package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

/** The authored CS fundamentals guides, graded through the real challenge engine. */
class PrepContentTest {

  Store store;
  ChallengeService challenges;
  Map<String, Object> content;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var g : Store.items(content.get("guides"))) store.put(g.get("id").toString(), "guide", "public", g);
    challenges = new ChallengeService(store, new TraceEngine(), new ProgressService(store));
  }

  @Test
  void thirtyCsFundamentalsGuidesSixPerSubjectWithFiveQuestionsEach() {
    var guides = Store.items(content.get("guides")).stream().filter(g -> "cs-fundamentals".equals(g.get("track"))).toList();
    assertEquals(30, guides.size());
    Map<String, Long> perSubject = new TreeMap<>();
    for (var g : guides) perSubject.merge(g.get("subject").toString(), 1L, Long::sum);
    assertEquals(Map.of("Computer networks", 6L, "DBMS", 6L, "OOP", 6L, "Operating systems", 6L, "SQL", 6L), perSubject);
    Set<String> ids = new HashSet<>();
    for (var g : guides) {
      assertTrue(ids.add(g.get("id").toString()), "duplicate guide " + g.get("id"));
      assertEquals(5, Store.items(g.get("challenges")).size(), g.get("id").toString());
    }
    assertEquals(33, Store.items(content.get("lessons")).size(), "the DSA catalogue is untouched");
  }

  @Test
  void everyQuizQuestionGradesOnlyItsAuthoredAnswer() {
    for (var g : Store.items(content.get("guides"))) for (var c : Store.items(g.get("challenges"))) {
      int answer = ((Number) c.get("answer")).intValue(), options = Store.strings(c.get("options")).size();
      for (int i = 0; i < options; i++) assertEquals(
        i == answer,
        challenges.attempt(null, c.get("id").toString(), new Contracts.AttemptRequest(i, UUID.randomUUID().toString())).correct(),
        c.get("id") + " option " + i
      );
    }
  }
}
