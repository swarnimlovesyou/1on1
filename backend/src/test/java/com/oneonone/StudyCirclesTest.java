package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.time.LocalDate;
import java.util.*;
import org.junit.jupiter.api.Test;

/** The circle's problem of the week and each member's week. */
class StudyCirclesTest {

  final List<Map<String, Object>> problems = List.of(
    Map.of("id", "p1", "title", "One", "difficulty", "Easy"),
    Map.of("id", "p2", "title", "Two", "difficulty", "Medium"),
    Map.of("id", "p3", "title", "Three", "difficulty", "Hard")
  );

  @Test
  void theWeeklyProblemIsOneFewestMembersSolvedAndStaysPutForTheWeek() {
    var solved = Map.of("ann", Set.of("p1", "p2"), "ben", Set.of("p1"));
    var monday = LocalDate.of(2026, 11, 16);
    var pick = StudyCircles.weeklyProblem("cohort-a", monday, problems, solved);
    assertEquals("p3", pick.get("id"), "nobody has solved p3");
    assertEquals(List.of(), pick.get("solvedBy"));
    assertEquals(pick, StudyCircles.weeklyProblem("cohort-a", monday.plusDays(6), problems, solved), "same pick all week");
    var everyone = Map.of("ann", Set.of("p1", "p2", "p3"), "ben", Set.of("p1", "p2", "p3"));
    assertEquals(List.of("ann", "ben"), StudyCircles.weeklyProblem("cohort-a", monday, problems, everyone).get("solvedBy"));
  }

  @Test
  void aStoredPickHoldsAllWeekEvenAfterSomeoneSolvesIt() {
    var monday = LocalDate.of(2026, 11, 16);
    var first = StudyCircles.weekly(Map.of(), "cohort-a", monday, problems, Map.of("ann", Set.of("p1", "p2")));
    assertEquals(Map.of("week", "2026-11-16", "id", "p3"), first);
    var later = StudyCircles.weekly(first, "cohort-a", monday.plusDays(3), problems, Map.of("ann", Set.of("p1", "p2", "p3")));
    assertEquals(first, later, "solving it does not move this week's problem");
    assertEquals(List.of("ann"), StudyCircles.solvedBy("p3", Map.of("ann", Set.of("p3"), "ben", Set.of())));
    assertNotEquals("2026-11-16", StudyCircles.weekly(first, "cohort-a", monday.plusDays(7), problems, Map.of()).get("week"), "a new week picks again");
  }

  @Test
  void aWeekCountsActivityFromMondayToToday() {
    var activity = Map.of("2026-11-15", 4, "2026-11-16", 2, "2026-11-18", 3);
    assertEquals(5, StudyCircles.thisWeek(activity, LocalDate.of(2026, 11, 18)));
  }
}
