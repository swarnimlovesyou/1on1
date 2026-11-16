package com.oneonone;

import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;

/**
 * Spaced review for one concept, replayed from its evidence rather than stored, so it can never drift
 * from what the learner actually did.
 *
 * <ul>
 *   <li>A first success schedules the first review 1 day later; each successful review then waits 3,
 *       then 7 days (7 repeats).
 *   <li>A miss, at any time, brings the review back the next day and restarts the ladder.
 *   <li>A hinted success counts as remembered but does not climb: it repeats the current interval.
 *   <li>A success before the review is due is practice, not a review: it does not move the date, so
 *       cramming cannot skip intervals.
 * </ul>
 *
 * Replaying n events is O(n log n) for the sort, then one pass.
 */
public final class ReviewSchedule {

  static final int[] INTERVALS = { 1, 3, 7 };

  /** One graded piece of evidence: a challenge attempt or an accepted problem. */
  public record Event(LocalDate day, boolean correct, boolean hinted) {}

  /**
   * stage 0: not yet remembered (new, or reset by a miss); 1–3: position on the 1/3/7-day ladder.
   * dueOn is null until the first graded evidence.
   */
  public record State(
    int stage,
    LocalDate dueOn,
    LocalDate lastEvidence,
    String lastOutcome,
    int reviews
  ) {
    public boolean due(LocalDate today) {
      return dueOn != null && !dueOn.isAfter(today);
    }
  }

  private ReviewSchedule() {}

  public static State replay(List<Event> events) {
    int stage = 0, reviews = 0;
    LocalDate due = null, last = null;
    String outcome = "none";
    for (Event e : events
      .stream()
      .sorted(Comparator.comparing(Event::day))
      .toList()) {
      boolean reviewing = due != null && !e.day().isBefore(due);
      if (!e.correct()) {
        stage = 0;
        due = e.day().plusDays(1);
        outcome = "missed";
        if (reviewing) reviews++;
      } else if (due == null) {
        // first success: start the ladder
        stage = e.hinted() ? 0 : 1;
        due = e.day().plusDays(INTERVALS[0]);
        outcome = e.hinted() ? "hinted" : "remembered";
      } else if (reviewing) {
        reviews++;
        if (!e.hinted()) stage = Math.min(stage + 1, INTERVALS.length);
        due = e.day().plusDays(INTERVALS[Math.max(stage, 1) - 1]);
        outcome = e.hinted() ? "hinted" : "remembered";
      } else continue; // practice before the review is due: evidence, but no schedule change
      last = e.day();
    }
    return new State(stage, due, last, outcome, reviews);
  }
}
