package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.time.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Achievements are server-owned; preference/resume writes never create activity. */
@Service
public class ProgressService {

  final Store store;

  public ProgressService(Store store) {
    this.store = store;
  }

  public Map<String, Object> summary(String user) {
    var out = new LinkedHashMap<>(store.find("state-" + user).orElse(Map.of()));
    for (String key : List.of("completed", "solved", "bookmarks"))
      out.putIfAbsent(key, List.of());
    var solved = new LinkedHashSet<>(Store.strings(out.get("solved")));
    solved.addAll(
      store.db.queryForList(
        "select problem_id from solved_credits where member_id=?",
        String.class,
        user
      )
    );
    out.put("solved", List.copyOf(solved));
    if (out.containsKey("activity")) out.put(
      "legacyActivity",
      out.get("activity")
    );
    var activity = new TreeMap<String, Integer>();
    store.db.query(
      "select activity_day,count(*) as total from learning_events where member_id=? group by activity_day",
      rs -> {
        activity.put(rs.getString(1), rs.getInt(2));
      },
      user
    );
    out.put("activity", activity);
    out.put(
      "attempts",
      store.db.query(
        "select id,challenge_id,lesson_id,kind,correct,created_at from challenge_attempts where member_id=? order by created_at desc",
        (rs, n) ->
          Map.of(
            "id",
            rs.getString(1),
            "challengeId",
            rs.getString(2),
            "lessonId",
            rs.getString(3),
            "kind",
            rs.getString(4),
            "correct",
            rs.getBoolean(5),
            "createdAt",
            rs.getTimestamp(6).toInstant().toString()
          ),
        user
      )
    );
    out.put("studyContexts", store.list("study-context", user));
    out.put("notes", store.list("note", user));
    out.put("plans", store.list("plan", user));
    out.put("drafts", store.list("draft", user));
    out.put(
      "submissions",
      store
        .list("submission", user)
        .stream()
        .map(ExecutionService::visible)
        .toList()
    );
    return out;
  }

  @Transactional
  public synchronized Map<String, Object> update(
    String user,
    Map<String, Object> body
  ) {
    var state = new LinkedHashMap<>(
      store.find("state-" + user).orElse(Map.of())
    );
    for (String key : List.of("completed", "bookmarks"))
      if (body.containsKey(key)) {
        var ids = Store.strings(body.get(key));
        if (ids.size() > 500) throw new IllegalArgumentException(
          "Too many saved items."
        );
        var validated = ids
          .stream()
          .distinct()
          .filter(id ->
            store
              .find(id)
              .map(
                item ->
                  !Boolean.FALSE.equals(item.get("published")) &&
                  ("lesson".equals(item.get("kind")) ||
                    (key.equals("bookmarks") &&
                      "problem".equals(item.get("kind"))))
              )
              .orElse(false)
          )
          .toList();
        if (key.equals("completed")) {
          var old = new HashSet<>(Store.strings(state.get(key)));
          for (String id : validated)
            if (id.startsWith("lesson-") && !old.contains(id)) record(
              user,
              "lesson_explored",
              id
            );
        }
        state.put(key, validated);
      }
    for (String key : List.of(
      "level",
      "goal",
      "language",
      "resumeLesson",
      "resumeStep",
      "onboarded"
    ))
      if (body.containsKey(key)) {
        if (
          store.encode(body.get(key)).length() > 300
        ) throw new IllegalArgumentException("Preference value is too long.");
        state.put(key, body.get(key));
      }
    store.put("state-" + user, "state", user, state);
    return summary(user);
  }

  public void record(String user, String kind, String source) {
    String day = LocalDate.now(ZoneOffset.UTC).toString();
    String id = UUID.nameUUIDFromBytes(
      (user + ":" + kind + ":" + source + ":" + day).getBytes(
        StandardCharsets.UTF_8
      )
    ).toString();
    // Synchronization is sufficient for the supported single-Java-process local deployment.
    store.db.update(
      "insert into learning_events(id,member_id,kind,source_id,activity_day) values(?,?,?,?,?) on conflict do nothing",
      id,
      user,
      kind,
      source,
      day
    );
  }

  @Transactional
  public void accepted(String user, String problem, String submission) {
    int added = store.db.update(
      "insert into solved_credits(member_id,problem_id,submission_id) values(?,?,?) on conflict do nothing",
      user,
      problem,
      submission
    );
    if (added > 0) record(user, "problem_accepted", problem);
  }
}
