package com.oneonone;

import com.oneonone.algorithms.SetCover;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * Practice plans: greedy set cover picks problems that cover the chosen topics, then they become dated
 * tasks (perDay per day). Tasks can be completed or moved; regenerating keeps every completed task
 * exactly as it was and re-plans only the rest from the chosen start date.
 */
@Service
public class PlanService {

  final Store store;
  final ProgressService progress;

  public PlanService(Store store, ProgressService progress) {
    this.store = store;
    this.progress = progress;
  }

  static LocalDate today() {
    return LocalDate.now(ZoneOffset.UTC);
  }

  public Map<String, Object> create(String user, Map<String, Object> body) {
    Set<String> goals = new TreeSet<>(Store.strings(body.get("topics")));
    if (
      goals.isEmpty() || goals.size() > 50
    ) throw new IllegalArgumentException("Select between 1 and 50 topics.");
    String difficulty = Store.text(body, "difficulty", "All");
    int perDay = perDay(body.get("perDay"), 2);
    LocalDate start = date(body.get("startDate"), today());
    Map<String, Object> data = new LinkedHashMap<>();
    data.put("title", Store.text(body, "title", "My practice plan"));
    data.put("topics", List.copyOf(goals));
    data.put("difficulty", difficulty);
    data.put("perDay", perDay);
    data.put("startDate", start.toString());
    data.put("method", "Greedy set-cover approximation");
    data.put("createdAt", java.time.Instant.now().toString());
    schedule(user, data, List.of(), start);
    return store.put("plan-" + UUID.randomUUID(), "plan", user, data);
  }

  /** Keeps completed tasks untouched; re-selects and re-dates everything else from startDate. */
  public Map<String, Object> regenerate(String user, String planId, Map<String, Object> body) {
    var plan = new LinkedHashMap<>(store.owned(planId, user));
    if (body.containsKey("perDay")) plan.put("perDay", perDay(body.get("perDay"), 2));
    LocalDate start = date(body.get("startDate"), today());
    var done = tasks(plan).stream().filter(t -> Boolean.TRUE.equals(t.get("done"))).toList();
    plan.put("startDate", start.toString());
    plan.put("regeneratedAt", java.time.Instant.now().toString());
    schedule(user, plan, done, start);
    return store.put(planId, "plan", user, plan);
  }

  /** {done: true|false} completes or reopens; {date: "YYYY-MM-DD"} moves the task. */
  public Map<String, Object> updateTask(String user, String planId, String taskId, Map<String, Object> body) {
    var plan = new LinkedHashMap<>(store.owned(planId, user));
    var list = new ArrayList<Map<String, Object>>();
    boolean found = false;
    for (var task : tasks(plan)) {
      var t = new LinkedHashMap<>(task);
      if (taskId.equals(t.get("id"))) {
        found = true;
        if (body.get("done") instanceof Boolean done) {
          t.put("done", done);
          t.put("doneAt", done ? java.time.Instant.now().toString() : null);
        }
        if (body.containsKey("date")) {
          LocalDate d = date(body.get("date"), null);
          if (d == null) throw new IllegalArgumentException("Choose a date for this task.");
          t.put("date", d.toString());
        }
      }
      list.add(t);
    }
    if (!found) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "This plan task could not be found.");
    list.sort(Comparator.comparing((Map<String, Object> t) -> t.get("date").toString()));
    plan.put("tasks", list);
    return store.put(planId, "plan", user, plan);
  }

  /** Plans made before tasks existed have only a selection: they read as undated pending work. */
  static List<Map<String, Object>> tasks(Map<String, Object> plan) {
    return Store.items(plan.get("tasks"));
  }

  private void schedule(String user, Map<String, Object> plan, List<Map<String, Object>> done, LocalDate start) {
    Set<String> goals = new TreeSet<>(Store.strings(plan.get("topics")));
    String difficulty = Store.text(plan, "difficulty", "All");
    int perDay = perDay(plan.get("perDay"), 2);
    Set<String> skip = new HashSet<>(Store.strings(progress.summary(user).get("solved")));
    Set<String> covered = new TreeSet<>();
    var problems = store.list("problem", "public");
    for (var t : done) {
      skip.add(t.get("problemId").toString());
      problems.stream().filter(p -> p.get("id").equals(t.get("problemId")))
        .forEach(p -> covered.addAll(Store.strings(p.get("topics"))));
    }
    var candidates = problems
      .stream()
      .filter(p ->
        !Boolean.FALSE.equals(p.get("published")) &&
        !skip.contains(p.get("id").toString()) &&
        (difficulty.equals("All") || difficulty.equals(p.get("difficulty")))
      )
      .map(p -> new SetCover.Candidate(p.get("id").toString(), new HashSet<>(Store.strings(p.get("topics")))))
      .toList();
    Set<String> remaining = new TreeSet<>(goals);
    remaining.removeAll(covered); // topics completed work already covers need no new problems
    var result = new SetCover().select(remaining, candidates);
    var tasks = new ArrayList<Map<String, Object>>(done);
    int i = 0;
    for (var pick : result.selected()) {
      var t = new LinkedHashMap<String, Object>();
      t.put("id", "task-" + UUID.randomUUID().toString().substring(0, 8));
      t.put("kind", "problem");
      t.put("problemId", pick.id());
      t.put("adds", pick.adds());
      t.put("date", start.plusDays(i++ / perDay).toString());
      t.put("done", false);
      t.put("doneAt", null);
      tasks.add(t);
    }
    tasks.sort(Comparator.comparing((Map<String, Object> t) -> t.get("date").toString()));
    plan.put("tasks", tasks);
    var selected = new ArrayList<Map<String, Object>>();
    for (var t : tasks) selected.add(Map.of("id", t.get("problemId"), "adds", t.getOrDefault("adds", List.of())));
    plan.put("selected", selected);
    plan.put("uncovered", result.uncovered());
  }

  static int perDay(Object value, int fallback) {
    try {
      int n = value == null ? fallback : Integer.parseInt(value.toString());
      return Math.min(10, Math.max(1, n));
    } catch (NumberFormatException e) {
      throw new IllegalArgumentException("Choose between 1 and 10 problems per day.");
    }
  }

  /** An ISO date within a year either side of today; null or blank gives the fallback. */
  static LocalDate date(Object value, LocalDate fallback) {
    if (value == null || value.toString().isBlank()) return fallback;
    try {
      LocalDate d = LocalDate.parse(value.toString());
      if (d.isBefore(today().minusYears(1)) || d.isAfter(today().plusYears(1))) throw new IllegalArgumentException(
        "Choose a date within a year of today."
      );
      return d;
    } catch (DateTimeParseException e) {
      throw new IllegalArgumentException("Use a date like 2026-11-20.");
    }
  }
}
