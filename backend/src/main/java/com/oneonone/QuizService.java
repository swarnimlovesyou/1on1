package com.oneonone;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * Quiz-style mock assessment: a third each of aptitude, reasoning and CS fundamentals, timed. Answers stay in the
 * stored quiz and are only revealed, with explanations, after submitting.
 */
@Service
public class QuizService {

  static final Set<Integer> SIZES = Set.of(15, 30);
  static final Set<Integer> MINUTES = Set.of(20, 40);

  final Store store;
  final DrillService drills;

  public QuizService(Store store, DrillService drills) {
    this.store = store;
    this.drills = drills;
  }

  public Map<String, Object> start(String user, Map<String, Object> body) {
    int size = number(body.get("questions")), minutes = number(body.get("minutes"));
    if (!SIZES.contains(size) || !MINUTES.contains(minutes))
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Choose 15 or 30 questions and 20 or 40 minutes.");
    var r = ThreadLocalRandom.current();
    int each = size / 3;
    var questions = new ArrayList<Map<String, Object>>();
    questions.addAll(drillQuestions("aptitude", "Aptitude", each, r));
    questions.addAll(drillQuestions("reasoning", "Reasoning", each, r));
    questions.addAll(csQuestions(size - 2 * each, r));
    Collections.shuffle(questions, r);
    store.quota(user, "QUIZ", 40);
    // opaque ids: a topic-seed or guide-challenge id would let the public drill and challenge endpoints reveal answers
    for (int i = 0; i < questions.size(); i++) questions.get(i).put("id", "q" + (i + 1));
    String id = "quiz-" + UUID.randomUUID();
    Instant now = Instant.now();
    var doc = new LinkedHashMap<String, Object>();
    doc.put("questions", questions);
    doc.put("minutes", minutes);
    doc.put("startedAt", now.toString());
    doc.put("deadline", now.plus(Duration.ofMinutes(minutes)).toString());
    store.put(id, "quiz", user, doc);
    var out = new LinkedHashMap<String, Object>();
    out.put("id", id);
    out.put("minutes", minutes);
    out.put("deadline", doc.get("deadline"));
    out.put("questions", questions.stream().map(QuizService::publicQuestion).toList());
    return out;
  }

  static Map<String, Object> publicQuestion(Map<String, Object> q) {
    var out = new LinkedHashMap<String, Object>();
    for (String key : List.of("id", "section", "prompt", "options", "unit")) if (q.get(key) != null) out.put(key, q.get(key));
    return out;
  }

  List<Map<String, Object>> drillQuestions(String track, String section, int count, Random r) {
    var topics = DrillService.TOPICS.entrySet().stream().filter(e -> e.getValue().equals(track)).map(Map.Entry::getKey).toList();
    var out = new ArrayList<Map<String, Object>>();
    for (int i = 0; i < count; i++) {
      String topic = topics.get((i + r.nextInt(topics.size())) % topics.size());
      int seed = r.nextInt(0, Integer.MAX_VALUE);
      var d = drills.generate(topic, seed);
      var q = new LinkedHashMap<String, Object>();
      q.put("id", topic + "-" + seed);
      q.put("section", section);
      q.put("prompt", d.prompt());
      if (d.options() != null) q.put("options", d.options());
      if (d.unit() != null) q.put("unit", d.unit());
      q.put("answer", d.answer());
      q.put("explanation", d.explanation());
      out.add(q);
    }
    return out;
  }

  List<Map<String, Object>> csQuestions(int count, Random r) {
    var pool = new ArrayList<Map<String, Object>>();
    for (var g : store.list("guide", "public"))
      if ("cs-fundamentals".equals(g.get("track")) && !Boolean.FALSE.equals(g.get("published")))
        for (var c : Store.items(g.get("challenges")))
          if (c.get("answer") instanceof Number n && c.get("options") != null) {
            var options = Store.strings(c.get("options"));
            var q = new LinkedHashMap<String, Object>();
            q.put("id", c.get("id"));
            q.put("section", "CS fundamentals");
            q.put("prompt", c.get("prompt"));
            q.put("options", options);
            q.put("answer", options.get(n.intValue()));
            q.put("explanation", c.get("explanation"));
            pool.add(q);
          }
    Collections.shuffle(pool, r);
    return pool.subList(0, Math.min(count, pool.size()));
  }

  Map<String, Object> quiz(String user, String id) {
    if (!id.startsWith("quiz-")) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That quiz doesn't exist.");
    try {
      return store.owned(id, user);
    } catch (RuntimeException e) {
      throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That quiz doesn't exist.");
    }
  }

  /** For tests: the stored answer to one question. */
  String answerFor(String quizId, String questionId) {
    return Store.items(quiz(store.db.queryForObject("select owner_id from documents where id=?", String.class, quizId), quizId).get("questions")).stream().filter(q -> questionId.equals(q.get("id"))).findFirst().orElseThrow().get("answer").toString();
  }

  public synchronized Map<String, Object> submit(String user, String id, Map<String, Object> body) {
    var doc = new LinkedHashMap<>(quiz(user, id));
    if (doc.get("result") instanceof Map<?, ?> earlier) return (Map<String, Object>) earlier;
    var given = body.get("answers") instanceof Map<?, ?> m ? m : Map.of();
    var review = new ArrayList<Map<String, Object>>();
    var bySection = new LinkedHashMap<String, int[]>();
    int score = 0;
    for (var q : Store.items(doc.get("questions"))) {
      String answer = given.get(q.get("id")) == null ? "" : given.get(q.get("id")).toString();
      // choices compare by the option's exact text; typed answers use the drill matcher (numbers by value, units allowed)
      boolean correct = !answer.isBlank() && (q.get("options") != null ? answer.equals(q.get("answer")) : DrillService.matches(q.get("answer").toString(), answer));
      if (correct) score++;
      var tally = bySection.computeIfAbsent(q.get("section").toString(), k -> new int[2]);
      tally[1]++;
      if (correct) tally[0]++;
      var row = new LinkedHashMap<String, Object>();
      row.put("id", q.get("id"));
      row.put("section", q.get("section"));
      row.put("prompt", q.get("prompt"));
      row.put("given", answer);
      row.put("expected", q.get("answer"));
      row.put("correct", correct);
      row.put("explanation", q.get("explanation"));
      review.add(row);
    }
    var result = new LinkedHashMap<String, Object>();
    result.put("score", score);
    result.put("total", review.size());
    result.put("late", Instant.now().isAfter(Instant.parse(doc.get("deadline").toString()).plusSeconds(30)));
    result.put("sections", bySection.entrySet().stream().map(e -> (Map<String, Object>) new LinkedHashMap<String, Object>(Map.of("section", e.getKey(), "score", e.getValue()[0], "total", e.getValue()[1]))).toList());
    result.put("review", review);
    doc.put("result", result);
    store.put(id, "quiz", user, doc);
    return result;
  }

  static int number(Object v) {
    try {
      return Integer.parseInt(String.valueOf(v));
    } catch (NumberFormatException e) {
      return -1;
    }
  }
}
