package com.oneonone;

import static com.oneonone.Contracts.*;

import java.math.BigDecimal;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ChallengeService {

  final Store store;
  final TraceEngine traces;
  final ProgressService progress;

  public ChallengeService(
    Store store,
    TraceEngine traces,
    ProgressService progress
  ) {
    this.store = store;
    this.traces = traces;
    this.progress = progress;
  }

  public static List<Map<String, Object>> authored(Map<String, Object> lesson) {
    var out = new ArrayList<>(Store.items(lesson.get("challenges")));
    if (out.isEmpty() && lesson.get("checkpoint") instanceof Map<?, ?> raw) {
      var cp = new LinkedHashMap<String, Object>((Map<String, Object>) raw);
      cp.put("id", "challenge-" + lesson.get("id") + "-checkpoint");
      cp.put("kind", "prediction");
      cp.put("title", "Check your intuition");
      cp.put("prompt", cp.get("question"));
      out.add(cp);
    }
    return out;
  }

  public static Map<String, Object> publicLesson(Map<String, Object> lesson) {
    var out = new LinkedHashMap<>(lesson);
    if (lesson.get("teaching") instanceof Map<?, ?> teaching) out.put(
      "teaching",
      CurriculumController.publicConcept((Map<String, Object>) teaching)
    );
    var publicChallenges = authored(lesson)
      .stream()
      .map(challenge -> {
        var item = new LinkedHashMap<String, Object>();
        for (String key : List.of(
          "id",
          "kind",
          "title",
          "prompt",
          "options",
          "fields",
          "scene",
          "traceStep",
          "hint"
        ))
          if (challenge.containsKey(key)) item.put(key, challenge.get(key));
        return item;
      })
      .toList();
    out.put("challenges", publicChallenges);
    if (out.get("checkpoint") instanceof Map<?, ?> raw) {
      var cp = new LinkedHashMap<String, Object>((Map<String, Object>) raw);
      cp.remove("answer");
      cp.remove("explanation");
      cp.put("id", "challenge-" + lesson.get("id") + "-checkpoint");
      out.put("checkpoint", cp);
    }
    return out;
  }

  @Transactional
  public synchronized AttemptResult attempt(
    String user,
    String challengeId,
    AttemptRequest request
  ) {
    if (
      request.answer() == null ||
      store.encode(request.answer()).length() > 12000
    ) throw new IllegalArgumentException("Supply a bounded answer.");
    if (
      request.requestId() == null ||
      !request.requestId().matches("[A-Za-z0-9_-]{8,128}")
    ) throw new IllegalArgumentException("Supply a unique request identifier.");
    String answerJson = store.encode(request.answer());
    if (user != null) {
      var previous = store.db.queryForList(
        "select id,challenge_id,kind,answer_json,correct,feedback from challenge_attempts where member_id=? and request_id=?",
        user,
        request.requestId()
      );
      if (!previous.isEmpty()) {
        var row = previous.getFirst();
        if (
          !challengeId.equals(row.get("challenge_id")) ||
          !answerJson.equals(row.get("answer_json"))
        ) throw new ResponseStatusException(
          HttpStatus.CONFLICT,
          "This request identifier was already used for another answer."
        );
        var found = find(challengeId);
        boolean correct = Boolean.TRUE.equals(row.get("correct"));
        return new AttemptResult(
          row.get("id").toString(),
          challengeId,
          row.get("kind").toString(),
          correct,
          row.get("feedback").toString(),
          correct ? Store.text(found.challenge(), "explanation", "") : "",
          true
        );
      }
    }
    var found = find(challengeId);
    var challenge = found.challenge();
    String kind = Store.text(challenge, "kind", "prediction");
    boolean correct;
    String feedback =
      "Try again. " +
      Store.text(
        challenge,
        "hint",
        "Look at the invariant and the state before this operation."
      );
    if (kind.equals("dry-run")) {
      if (
        !(request.answer() instanceof Map<?, ?> answer)
      ) throw new IllegalArgumentException("Fill in the state-table fields.");
      var trace = traces.trace((Map<String, Object>) challenge.get("scene"));
      var steps = Store.items(trace.get("steps"));
      int index = ((Number) challenge.get("traceStep")).intValue();
      if (
        index < 0 || index >= steps.size()
      ) throw new IllegalArgumentException(
        "This authored exercise points outside its trace."
      );
      var variables = (Map<String, Object>) steps.get(index).get("variables");
      correct = true;
      for (var field : Store.items(challenge.get("fields"))) {
        String key = field.get("key").toString();
        if (
          !variables.containsKey(key) ||
          !same(variables.get(key), answer.get(key))
        ) {
          correct = false;
          feedback =
            "Check “" +
            field.get("label") +
            "”. " +
            Store.text(
              challenge,
              "hint",
              "Follow the operation one step at a time."
            );
          break;
        }
      }
    } else if (kind.equals("manipulation")) {
      if (
        !(request.answer() instanceof Map<?, ?> scene)
      ) throw new IllegalArgumentException(
        "Run an experiment, then submit its input."
      );
      if (
        !Objects.equals(
          ((Map<?, ?>) challenge.get("scene")).get("algorithm"),
          scene.get("algorithm")
        )
      ) throw new IllegalArgumentException("Use this lesson's algorithm.");
      var trace = traces.trace((Map<String, Object>) scene);
      var result = (Map<String, Object>) trace.get("result");
      var rule = (Map<String, Object>) challenge.get("rule");
      Object actual = result;
      for (String part : rule.get("path").toString().split("\\."))
        actual = actual instanceof Map<?, ?> map ? map.get(part) : null;
      correct = same(actual, rule.get("equals"));
      if (challenge.containsKey("requiredTarget")) correct &= same(
        scene.get("target"),
        challenge.get("requiredTarget")
      );
    } else correct = same(challenge.get("answer"), request.answer());
    if (correct) feedback = kind.equals("dry-run")
      ? "Your state table matches the Java execution."
      : "That’s it. You connected the state to the idea.";
    String id = UUID.randomUUID().toString();
    if (user != null) {
      int inserted = store.db.update(
        "insert into challenge_attempts(id,member_id,request_id,challenge_id,lesson_id,kind,answer_json,correct,feedback,hint_used) values(?,?,?,?,?,?,?,?,?,?) on conflict do nothing",
        id,
        user,
        request.requestId(),
        challengeId,
        found.lesson(),
        kind,
        answerJson,
        correct,
        feedback,
        Boolean.TRUE.equals(request.hintUsed())
      );
      if (inserted == 0) {
        var row = store.db.queryForMap(
          "select id,challenge_id,kind,answer_json,correct,feedback from challenge_attempts where member_id=? and request_id=?",
          user,
          request.requestId()
        );
        if (
          !challengeId.equals(row.get("challenge_id")) ||
          !answerJson.equals(row.get("answer_json"))
        ) throw new ResponseStatusException(
          HttpStatus.CONFLICT,
          "This request identifier belongs to another answer."
        );
        boolean savedCorrect = Boolean.TRUE.equals(row.get("correct"));
        return new AttemptResult(
          row.get("id").toString(),
          challengeId,
          row.get("kind").toString(),
          savedCorrect,
          row.get("feedback").toString(),
          savedCorrect ? Store.text(challenge, "explanation", "") : "",
          true
        );
      }
      progress.record(
        user,
        correct ? "challenge_passed" : "challenge_attempted",
        challengeId
      );
    }
    return new AttemptResult(
      id,
      challengeId,
      kind,
      correct,
      feedback,
      correct ? Store.text(challenge, "explanation", "") : "",
      user != null
    );
  }

  private record Found(String lesson, Map<String, Object> challenge) {}

  private Found find(String id) {
    for (var lesson : store.list("lesson", "public"))
      if (!Boolean.FALSE.equals(lesson.get("published"))) {
        if (
          id.equals("challenge-" + lesson.get("id") + "-checkpoint") &&
          lesson.get("checkpoint") instanceof Map<?, ?> cp
        ) return new Found(
          lesson.get("id").toString(),
          (Map<String, Object>) cp
        );
        for (var challenge : authored(lesson))
          if (id.equals(challenge.get("id"))) return new Found(
            lesson.get("id").toString(),
            challenge
          );
      }
    // Prep guide quizzes are graded the same way; their attempts record the guide id
    for (var guide : store.list("guide", "public"))
      if (!Boolean.FALSE.equals(guide.get("published")))
        for (var challenge : authored(guide))
          if (id.equals(challenge.get("id"))) return new Found(guide.get("id").toString(), challenge);
    throw new ResponseStatusException(
      HttpStatus.NOT_FOUND,
      "This learning challenge could not be found."
    );
  }

  static boolean same(Object expected, Object actual) {
    if (expected == null || actual == null) return false;
    if (
      expected instanceof List<?> list && actual instanceof String text
    ) return same(
      list,
      Arrays.stream(text.replaceAll("[\\[\\]]", "").split("[,\\s]+", -1))
        .filter(x -> !x.isBlank())
        .toList()
    );
    if (expected instanceof List<?> a && actual instanceof List<?> b) {
      if (a.size() != b.size()) return false;
      for (int i = 0; i < a.size(); i++) if (
        !same(a.get(i), b.get(i))
      ) return false;
      return true;
    }
    try {
      return (
        new BigDecimal(expected.toString().strip()).compareTo(
          new BigDecimal(actual.toString().strip())
        ) == 0
      );
    } catch (NumberFormatException ignored) {
      return expected
        .toString()
        .strip()
        .equalsIgnoreCase(actual.toString().strip());
    }
  }
}
