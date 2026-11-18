package com.oneonone;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.TemporalAdjusters;
import java.util.*;

/** Weekly rhythm for a study circle: one shared problem, and how much each member did this week. */
final class StudyCircles {

  private StudyCircles() {}

  static LocalDate monday(LocalDate day) {
    return day.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
  }

  /** Among the problems the fewest members have solved, one picked by the circle and week, so it holds all week. */
  static Map<String, Object> weeklyProblem(String cohortId, LocalDate day, List<Map<String, Object>> problems, Map<String, Set<String>> solved) {
    if (problems.isEmpty()) return Map.of();
    Comparator<Map<String, Object>> fewest = Comparator.comparingLong(p -> solved.values().stream().filter(s -> s.contains(p.get("id").toString())).count());
    var sorted = problems.stream().sorted(fewest.thenComparing(p -> p.get("id").toString())).toList();
    long least = solved.values().stream().filter(s -> s.contains(sorted.getFirst().get("id").toString())).count();
    var tied = sorted.stream().filter(p -> solved.values().stream().filter(s -> s.contains(p.get("id").toString())).count() == least).toList();
    var pick = tied.get(Math.floorMod((cohortId + monday(day)).hashCode(), tied.size()));
    var by = solved.entrySet().stream().filter(e -> e.getValue().contains(pick.get("id").toString())).map(Map.Entry::getKey).sorted().toList();
    return Map.of("id", pick.get("id"), "title", pick.get("title"), "difficulty", pick.get("difficulty"), "solvedBy", by);
  }

  /** This week's {week, id}: the stored pick while it is still this week's and still published, else a fresh one. */
  static Map<String, Object> weekly(Map<?, ?> stored, String cohortId, LocalDate day, List<Map<String, Object>> problems, Map<String, Set<String>> solved) {
    String week = monday(day).toString();
    if (week.equals(stored.get("week")) && problems.stream().anyMatch(p -> p.get("id").equals(stored.get("id"))))
      return Map.of("week", week, "id", stored.get("id"));
    var pick = weeklyProblem(cohortId, day, problems, solved);
    return pick.isEmpty() ? Map.of() : Map.of("week", week, "id", pick.get("id"));
  }

  static List<String> solvedBy(Object id, Map<String, Set<String>> solved) {
    return solved.entrySet().stream().filter(e -> e.getValue().contains(String.valueOf(id))).map(Map.Entry::getKey).sorted().toList();
  }

  /** Learning actions from this week's Monday through today. */
  static int thisWeek(Map<String, ?> activity, LocalDate today) {
    String from = monday(today).toString(), to = today.toString();
    return activity.entrySet().stream()
      .filter(e -> e.getKey().compareTo(from) >= 0 && e.getKey().compareTo(to) <= 0)
      .mapToInt(e -> ((Number) e.getValue()).intValue())
      .sum();
  }
}
