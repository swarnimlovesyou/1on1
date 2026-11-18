package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** The quiz-style mock assessment: aptitude, reasoning and CS questions, timed, graded on the server. */
class QuizTest {

  Store store;
  QuizService quizzes;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var g : Store.items(content.get("guides"))) store.put(g.get("id").toString(), "guide", "public", g);
    quizzes = new QuizService(store, new DrillService(new ProgressService(store)));
  }

  @Test
  void aQuizMixesTheSectionsAndNeverSendsAnswers() {
    var quiz = quizzes.start("ann", Map.of("questions", 15, "minutes", 20));
    var questions = Store.items(quiz.get("questions"));
    assertEquals(15, questions.size());
    assertEquals(Set.of("Aptitude", "Reasoning", "CS fundamentals"), questions.stream().map(q -> q.get("section")).collect(java.util.stream.Collectors.toSet()));
    for (var q : questions) {
      assertFalse(q.containsKey("answer"));
      assertFalse(q.containsKey("explanation"));
      assertFalse(q.get("prompt").toString().isBlank());
    }
    assertNotNull(quiz.get("deadline"));
    assertEquals(questions.size(), questions.stream().map(q -> q.get("id")).distinct().count(), "no question twice");
    for (var q : questions) assertTrue(q.get("id").toString().matches("q[0-9]+"), "ids reveal no topic, seed or guide challenge");
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> quizzes.submit("bob", quiz.get("id").toString(), Map.of("answers", Map.of()))).getStatusCode().value(), "only its owner can submit");
  }

  @Test
  void submittingGradesEverySectionAndExplainsEachQuestion() {
    var quiz = quizzes.start("ann", Map.of("questions", 15, "minutes", 20));
    String id = quiz.get("id").toString();
    var answers = new LinkedHashMap<String, Object>();
    for (var q : Store.items(quiz.get("questions"))) answers.put(q.get("id").toString(), quizzes.answerFor(id, q.get("id").toString()));
    var result = quizzes.submit("ann", id, Map.of("answers", answers));
    assertEquals(15, result.get("score"));
    assertEquals(15, result.get("total"));
    var review = Store.items(result.get("review"));
    assertTrue(review.stream().allMatch(r -> Boolean.TRUE.equals(r.get("correct")) && !r.get("explanation").toString().isBlank()));
    var sections = Store.items(result.get("sections"));
    assertEquals(3, sections.size());
    assertEquals(result, quizzes.submit("ann", id, Map.of("answers", Map.of())), "a second submit returns the first result");
  }

  @Test
  void blankAnswersScoreZeroAndUnknownQuizzesAreNotFound() {
    var quiz = quizzes.start("ann", Map.of("questions", 15, "minutes", 20));
    var result = quizzes.submit("ann", quiz.get("id").toString(), Map.of("answers", Map.of()));
    assertEquals(0, result.get("score"));
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> quizzes.submit("ann", "quiz-nope", Map.of("answers", Map.of()))).getStatusCode().value());
    assertEquals(400, assertThrows(ResponseStatusException.class, () -> quizzes.start("ann", Map.of("questions", 7, "minutes", 20))).getStatusCode().value());
  }
}
