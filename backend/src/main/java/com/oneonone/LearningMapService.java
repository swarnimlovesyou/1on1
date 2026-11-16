package com.oneonone;

import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.*;
import java.util.regex.Pattern;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

/**
 * The concept map: the 24 concepts in prerequisite order (Kahn's algorithm, ties by authored order),
 * each with the evidence behind its state, its spaced-review schedule, and one personalised next action.
 *
 * Evidence is kept in three separate grades and never merged: exploring a notebook, passing a
 * server-graded challenge, and having a linked problem accepted by the judge. Nothing is locked; the
 * map only recommends.
 */
@Service
public class LearningMapService {

  private static final Pattern PROBLEM_ID = Pattern.compile("problem-[a-z0-9-]+");

  record Concept(String id, String title, int order, List<String> prerequisites, List<String> lessonIds, Set<String> localProblems) {}

  final Store store;
  private final List<Concept> concepts = new ArrayList<>();

  public LearningMapService(Store store) throws Exception {
    this.store = store;
    var json = new tools.jackson.databind.ObjectMapper();
    Map<String, Object> data = json.readValue(new ClassPathResource("curriculum.json").getInputStream(), Map.class);
    Map<String, String> localProblem = new HashMap<>();
    for (var q : Store.items(data.get("questions"))) if (q.get("localProblemId") != null) localProblem.put(
      q.get("id").toString(),
      q.get("localProblemId").toString()
    );
    for (var c : Store.items(data.get("concepts"))) {
      Set<String> problems = new TreeSet<>();
      for (var app : Store.items(c.get("applications"))) {
        String p = localProblem.get(Store.text(app, "questionId", ""));
        if (p != null) problems.add(p);
      }
      concepts.add(
        new Concept(
          c.get("id").toString(),
          c.get("title").toString(),
          ((Number) c.get("order")).intValue(),
          Store.strings(c.get("prerequisites")),
          Store.strings(c.get("lessonIds")),
          problems
        )
      );
    }
  }

  /** Kahn's algorithm with a priority queue on authored order: O((V + E) log V). Throws on a cycle. */
  static List<String> topologicalOrder(Map<String, List<String>> prerequisites, Map<String, Integer> order) {
    Map<String, Integer> indegree = new HashMap<>();
    Map<String, List<String>> unlocks = new HashMap<>();
    for (var e : prerequisites.entrySet()) {
      indegree.putIfAbsent(e.getKey(), 0);
      for (String before : e.getValue()) {
        if (!prerequisites.containsKey(before)) throw new IllegalStateException("Unknown prerequisite " + before + " of " + e.getKey());
        indegree.merge(e.getKey(), 1, Integer::sum);
        unlocks.computeIfAbsent(before, k -> new ArrayList<>()).add(e.getKey());
      }
    }
    var ready = new PriorityQueue<String>(Comparator.comparing((String id) -> order.getOrDefault(id, 0)).thenComparing(id -> id));
    indegree.forEach((id, n) -> {
      if (n == 0) ready.add(id);
    });
    List<String> out = new ArrayList<>();
    while (!ready.isEmpty()) {
      String id = ready.poll();
      out.add(id);
      for (String next : unlocks.getOrDefault(id, List.of())) if (indegree.merge(next, -1, Integer::sum) == 0) ready.add(next);
    }
    if (out.size() != prerequisites.size()) throw new IllegalStateException("The concept prerequisites contain a cycle.");
    return out;
  }

  public Map<String, Object> map(String user) {
    LocalDate today = PlanService.today();
    var lessons = store
      .list("lesson", "public")
      .stream()
      .filter(l -> !Boolean.FALSE.equals(l.get("published")))
      .toList();
    Set<String> publishedProblems = new HashSet<>();
    Map<String, String> problemTitles = new HashMap<>();
    for (var p : store.list("problem", "public")) if (!Boolean.FALSE.equals(p.get("published"))) {
      publishedProblems.add(p.get("id").toString());
      problemTitles.put(p.get("id").toString(), Store.text(p, "title", p.get("id").toString()));
    }

    // evidence, empty for a guest
    Set<String> explored = new HashSet<>();
    List<Map<String, Object>> attempts = List.of();
    Map<String, LocalDate> accepted = new HashMap<>();
    List<Map<String, Object>> plans = List.of();
    if (user != null) {
      explored.addAll(Store.strings(store.find("state-" + user).orElse(Map.of()).get("completed")));
      attempts = store.db.queryForList(
        "select challenge_id,lesson_id,correct,hint_used,created_at from challenge_attempts where member_id=? order by created_at",
        user
      );
      store.db.query(
        "select problem_id,created_at from solved_credits where member_id=?",
        rs -> {
          accepted.put(rs.getString(1), day(rs.getTimestamp(2)));
        },
        user
      );
      plans = store.list("plan", user);
    }

    Map<String, List<String>> prereqs = new LinkedHashMap<>();
    Map<String, Integer> order = new HashMap<>();
    Map<String, Concept> byId = new HashMap<>();
    for (var c : concepts) {
      prereqs.put(c.id(), c.prerequisites());
      order.put(c.id(), c.order());
      byId.put(c.id(), c);
    }
    List<String> sorted = topologicalOrder(prereqs, order);

    Map<String, Map<String, Object>> views = new LinkedHashMap<>();
    Map<String, String> states = new HashMap<>();
    List<Map<String, Object>> reviewsDue = new ArrayList<>();
    for (String id : sorted) {
      Concept c = byId.get(id);
      Set<String> lessonIds = new LinkedHashSet<>(c.lessonIds());
      for (var l : lessons) if (id.equals(l.get("conceptId"))) lessonIds.add(l.get("id").toString());
      Set<String> problems = new TreeSet<>(c.localProblems());
      int challengeTotal = 0;
      for (var l : lessons) if (lessonIds.contains(l.get("id").toString())) {
        challengeTotal += ChallengeService.authored(l).size();
        var m = PROBLEM_ID.matcher(store.encode(l));
        while (m.find()) problems.add(m.group());
      }
      problems.retainAll(publishedProblems);

      // challenge evidence; a success after a miss on the same challenge the same day saw the hint in the feedback
      Set<String> passed = new TreeSet<>();
      List<ReviewSchedule.Event> events = new ArrayList<>();
      Map<String, LocalDate> missedOn = new HashMap<>();
      for (var a : attempts) {
        if (!lessonIds.contains(a.get("lesson_id").toString())) continue;
        String challenge = a.get("challenge_id").toString();
        boolean correct = Boolean.TRUE.equals(a.get("correct"));
        LocalDate d = day((Timestamp) a.get("created_at"));
        boolean hinted = Boolean.TRUE.equals(a.get("hint_used")) || (correct && d.equals(missedOn.get(challenge)));
        if (correct) passed.add(challenge);
        else missedOn.put(challenge, d);
        events.add(new ReviewSchedule.Event(d, correct, hinted));
      }
      List<String> acceptedHere = new ArrayList<>();
      for (String p : problems) if (accepted.containsKey(p)) {
        acceptedHere.add(p);
        events.add(new ReviewSchedule.Event(accepted.get(p), true, false));
      }
      boolean wasExplored = lessonIds.stream().anyMatch(explored::contains);
      String state = !acceptedHere.isEmpty() ? "accepted" : !passed.isEmpty() ? "passed" : wasExplored ? "explored" : "new";
      states.put(id, state);

      List<String> evidence = new ArrayList<>();
      if (wasExplored) evidence.add("You explored the notebook. Exploring alone is not mastery.");
      if (challengeTotal > 0) evidence.add(
        "Passed " + passed.size() + " of " + challengeTotal + " server-graded challenge" + (challengeTotal == 1 ? "" : "s") + "."
      );
      if (!problems.isEmpty()) evidence.add(
        acceptedHere.size() + " of " + problems.size() + " linked problem" + (problems.size() == 1 ? "" : "s") + " accepted by the judge."
      );
      if (state.equals("new")) evidence.add("No evidence yet. Open it any time; nothing is locked.");

      var view = new LinkedHashMap<String, Object>();
      view.put("id", id);
      view.put("title", c.title());
      view.put("order", c.order());
      view.put("prerequisites", c.prerequisites());
      view.put("lessonIds", List.copyOf(lessonIds));
      view.put("problemIds", List.copyOf(problems));
      view.put("state", state);
      view.put("explored", wasExplored);
      view.put("challenges", Map.of("passed", passed.size(), "total", challengeTotal));
      view.put("problems", Map.of("accepted", acceptedHere.size(), "total", problems.size()));
      view.put("evidence", evidence);
      if (!events.isEmpty()) {
        var r = ReviewSchedule.replay(events);
        var review = new LinkedHashMap<String, Object>();
        review.put("stage", r.stage());
        review.put("dueOn", r.dueOn() == null ? null : r.dueOn().toString());
        review.put("due", r.due(today));
        review.put("lastOutcome", r.lastOutcome());
        review.put("reviews", r.reviews());
        view.put("review", review);
        if (r.due(today)) {
          var item = new LinkedHashMap<String, Object>();
          item.put("conceptId", id);
          item.put("title", c.title());
          item.put("dueOn", r.dueOn().toString());
          item.put("overdueDays", r.dueOn().until(today).getDays());
          item.put("lastOutcome", r.lastOutcome());
          item.put("lessonId", lessonIds.isEmpty() ? null : lessonIds.iterator().next());
          reviewsDue.add(item);
        }
      }
      views.put(id, view);
    }
    reviewsDue.sort(Comparator.comparing((Map<String, Object> r) -> r.get("dueOn").toString()));

    var out = new LinkedHashMap<String, Object>();
    out.put("today", today.toString());
    out.put("concepts", List.copyOf(views.values()));
    out.put("reviewsDue", reviewsDue);
    out.put("nextAction", next(user, sorted, byId, views, states, reviewsDue, plans, accepted.keySet(), problemTitles, today));
    return out;
  }

  private static Map<String, Object> next(
    String user,
    List<String> sorted,
    Map<String, Concept> byId,
    Map<String, Map<String, Object>> views,
    Map<String, String> states,
    List<Map<String, Object>> reviewsDue,
    List<Map<String, Object>> plans,
    Set<String> accepted,
    Map<String, String> problemTitles,
    LocalDate today
  ) {
    if (!reviewsDue.isEmpty()) {
      var r = reviewsDue.getFirst();
      int overdue = ((Number) r.get("overdueDays")).intValue();
      return action(
        "review",
        "Review " + r.get("title"),
        (overdue > 0 ? "Due " + overdue + " day" + (overdue == 1 ? "" : "s") + " ago" : "Due today") +
        ". Answer one of its challenges without the hint to move it further out.",
        "/learn/" + r.get("lessonId"),
        r.get("conceptId").toString()
      );
    }
    for (var plan : plans) for (var t : PlanService.tasks(plan)) if (
      !Boolean.TRUE.equals(t.get("done")) &&
      !accepted.contains(t.get("problemId").toString()) &&
      !LocalDate.parse(t.get("date").toString()).isAfter(today)
    ) return action(
      "task",
      "Solve " + problemTitles.getOrDefault(t.get("problemId").toString(), t.get("problemId").toString()),
      "Planned for " + t.get("date") + " in " + Store.text(plan, "title", "your plan") + ".",
      "/practice/" + t.get("problemId"),
      null
    );
    for (String id : sorted) {
      String state = states.get(id);
      if (state.equals("passed") || state.equals("accepted")) continue;
      boolean ready = byId.get(id).prerequisites().stream().allMatch(p -> !states.get(p).equals("new") && !states.get(p).equals("explored"));
      if (!ready && user != null) continue;
      var lessonIds = Store.strings(views.get(id).get("lessonIds"));
      return action(
        "learn",
        (state.equals("explored") ? "Pass a challenge in " : "Learn ") + byId.get(id).title(),
        user == null
          ? "The first concept in prerequisite order. Sign in to keep your evidence."
          : byId.get(id).prerequisites().isEmpty()
            ? "It needs nothing before it."
            : "You have evidence for everything it builds on.",
        lessonIds.isEmpty() ? "/learn" : "/learn/" + lessonIds.getFirst(),
        id
      );
    }
    for (String id : sorted) for (String p : Store.strings(views.get(id).get("problemIds"))) if (!accepted.contains(p)) return action(
      "practice",
      "Solve " + problemTitles.getOrDefault(p, p),
      "You passed " + byId.get(id).title() + "'s challenges; an accepted problem is the strongest evidence.",
      "/practice/" + p,
      id
    );
    return action("done", "You're caught up", "No reviews are due and every concept has evidence. Explore anything.", "/learn", null);
  }

  private static Map<String, Object> action(String kind, String title, String reason, String href, String conceptId) {
    var out = new LinkedHashMap<String, Object>();
    out.put("kind", kind);
    out.put("title", title);
    out.put("reason", reason);
    out.put("href", href);
    out.put("conceptId", conceptId);
    return out;
  }

  private static LocalDate day(Timestamp t) {
    return t.toInstant().atZone(ZoneOffset.UTC).toLocalDate();
  }
}
