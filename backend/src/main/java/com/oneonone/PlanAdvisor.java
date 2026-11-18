package com.oneonone;

import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * Suggests what a practice plan should cover, from the learner's own record: checks they missed, problems
 * they have and haven't solved, their goal and the time they have. Gemini writes the suggestion when a key is
 * set, but only real topics and in-range values survive; without a key, or if the call fails, a fixed rule
 * does. The learner reviews the suggestion and the set-cover planner turns it into dated tasks.
 */
@RestController
@RequestMapping("/api/v1/plans")
public class PlanAdvisor {

  static final List<String> DIFFICULTIES = List.of("All", "Easy", "Medium", "Hard");

  final Store store;
  final ProgressService progress;
  final TutorService tutor; // null in tests: rules only

  public PlanAdvisor(Store store, ProgressService progress, TutorService tutor) {
    this.store = store;
    this.progress = progress;
    this.tutor = tutor;
  }

  /** {goal: "placements"|"foundations", weeks: 1-12, minutesPerDay: 15-240}. */
  @PostMapping("/suggest")
  public Map<String, Object> suggest(Authentication a, @RequestBody Map<String, Object> body) {
    return suggest(AuthController.user(a), body);
  }

  record TopicStat(String topic, int total, int solved, int missed) {}

  public Map<String, Object> suggest(String user, Map<String, Object> body) {
    int weeks = bounded(body.get("weeks"), 1, 12, "Choose between 1 and 12 weeks.");
    int minutes = bounded(body.get("minutesPerDay"), 15, 240, "Choose between 15 and 240 minutes a day.");
    String goal = "foundations".equals(body.get("goal")) ? "foundations" : "placements";
    var stats = stats(user);
    var rules = rules(stats, goal, weeks, minutes);
    if (tutor == null || !tutor.aiConfigured()) return rules;
    try {
      var raw = tutor.generateJson(
        user,
        "You plan coding-interview practice. From the learner's record, choose the topics to practise next (only from the given list, most important first), a difficulty (All, Easy, Medium or Hard), problems per day, a short plan title and up to four one-sentence reasons that cite the record.",
        store.encode(Map.of("goal", goal, "weeks", weeks, "minutesPerDay", minutes, "topics", stats.stream().map(t -> Map.of("topic", t.topic(), "problems", t.total(), "solved", t.solved(), "missedChecks", t.missed())).toList())),
        Map.of(
          "title", Map.of("type", "string"),
          "topics", Map.of("type", "array", "items", Map.of("type", "string")),
          "difficulty", Map.of("type", "string", "enum", DIFFICULTIES),
          "perDay", Map.of("type", "integer"),
          "reasons", Map.of("type", "array", "items", Map.of("type", "string"))
        )
      );
      return fromAi(raw, new HashSet<>(stats.stream().map(TopicStat::topic).toList()), rules);
    } catch (Exception e) {
      var out = new LinkedHashMap<>(rules);
      out.put("note", "The AI planner was unavailable, so this plan comes from your record by a fixed rule.");
      return out;
    }
  }

  /** Per problem topic: how many problems, how many solved, how many lesson checks missed on it. */
  List<TopicStat> stats(String user) {
    Set<String> solved = new HashSet<>(Store.strings(progress.summary(user).get("solved")));
    var lessonTopics = new HashMap<String, List<String>>();
    for (var l : store.list("lesson", "public")) lessonTopics.put(l.get("id").toString(), Store.strings(l.get("topics")));
    var missed = new HashMap<String, Integer>();
    store.db.query(
      "select lesson_id, count(*) from challenge_attempts where member_id=? and correct=false and lesson_id is not null group by lesson_id",
      rs -> {
        for (String t : lessonTopics.getOrDefault(rs.getString(1), List.of())) missed.merge(t, rs.getInt(2), Integer::sum);
      },
      user
    );
    var total = new TreeMap<String, int[]>();
    for (var p : store.list("problem", "public")) {
      if (Boolean.FALSE.equals(p.get("published"))) continue;
      for (String t : Store.strings(p.get("topics"))) {
        var n = total.computeIfAbsent(t, k -> new int[2]);
        n[0]++;
        if (solved.contains(p.get("id").toString())) n[1]++;
      }
    }
    return total.entrySet().stream().map(e -> new TopicStat(e.getKey(), e.getValue()[0], e.getValue()[1], missed.getOrDefault(e.getKey(), 0))).toList();
  }

  static Map<String, Object> rules(List<TopicStat> stats, String goal, int weeks, int minutes) {
    var ranked = stats.stream()
      .filter(t -> t.solved() < t.total())
      .sorted(Comparator.comparingInt(TopicStat::missed).reversed()
        .thenComparingDouble(t -> (double) t.solved() / t.total())
        .thenComparing(Comparator.comparingInt(TopicStat::total).reversed())
        .thenComparing(TopicStat::topic))
      .limit(Math.max(3, Math.min(12, weeks * 2 + 1)))
      .toList();
    var reasons = new ArrayList<String>();
    for (var t : ranked.subList(0, Math.min(4, ranked.size())))
      reasons.add(t.missed() > 0
        ? t.topic() + ": you missed " + t.missed() + " check" + (t.missed() == 1 ? "" : "s") + " on it."
        : t.topic() + ": " + t.solved() + " of " + t.total() + " problems solved so far.");
    var out = new LinkedHashMap<String, Object>();
    out.put("source", "rules");
    out.put("title", (goal.equals("foundations") ? "Foundations, " : "Placement sprint, ") + weeks + (weeks == 1 ? " week" : " weeks"));
    out.put("topics", ranked.stream().map(TopicStat::topic).toList());
    out.put("difficulty", goal.equals("foundations") ? "Easy" : "All");
    out.put("perDay", Math.max(1, Math.min(10, Math.round(minutes / 30f))));
    out.put("reasons", reasons);
    return out;
  }

  /** Keeps only real topics and in-range values from an AI answer; with no real topic left, the rules win. */
  static Map<String, Object> fromAi(Map<String, Object> raw, Set<String> known, Map<String, Object> fallback) {
    var topics = Store.strings(raw.get("topics")).stream().filter(known::contains).distinct().limit(12).toList();
    if (topics.isEmpty()) return fallback;
    var out = new LinkedHashMap<String, Object>();
    out.put("source", "ai");
    String title = Store.text(raw, "title", "").strip();
    out.put("title", title.isEmpty() || title.length() > 60 ? fallback.get("title") : title);
    out.put("topics", topics);
    out.put("difficulty", DIFFICULTIES.contains(raw.get("difficulty")) ? raw.get("difficulty") : fallback.get("difficulty"));
    int perDay;
    try {
      perDay = Integer.parseInt(String.valueOf(raw.get("perDay")));
    } catch (NumberFormatException e) {
      perDay = (int) fallback.get("perDay");
    }
    out.put("perDay", Math.max(1, Math.min(10, perDay)));
    var reasons = Store.strings(raw.get("reasons")).stream().map(String::strip).filter(r -> !r.isEmpty() && r.length() <= 240).limit(4).toList();
    out.put("reasons", reasons.isEmpty() ? fallback.get("reasons") : reasons);
    return out;
  }

  static int bounded(Object v, int min, int max, String message) {
    try {
      int n = Integer.parseInt(String.valueOf(v));
      if (n < min || n > max) throw new IllegalArgumentException(message);
      return n;
    } catch (NumberFormatException e) {
      throw new IllegalArgumentException(message);
    }
  }
}
