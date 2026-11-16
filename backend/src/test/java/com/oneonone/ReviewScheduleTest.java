package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import com.oneonone.ReviewSchedule.Event;
import java.time.LocalDate;
import java.util.*;
import org.junit.jupiter.api.Test;

class ReviewScheduleTest {

  static final LocalDate D = LocalDate.of(2026, 11, 1);

  static Event ok(int day) {
    return new Event(D.plusDays(day), true, false);
  }

  static Event hinted(int day) {
    return new Event(D.plusDays(day), true, true);
  }

  static Event miss(int day) {
    return new Event(D.plusDays(day), false, false);
  }

  @Test
  void successfulReviewsWaitOneThenThreeThenSevenDays() {
    assertEquals(D.plusDays(1), ReviewSchedule.replay(List.of(ok(0))).dueOn());
    assertEquals(D.plusDays(4), ReviewSchedule.replay(List.of(ok(0), ok(1))).dueOn());
    var s = ReviewSchedule.replay(List.of(ok(0), ok(1), ok(4)));
    assertEquals(D.plusDays(11), s.dueOn());
    assertEquals(3, s.stage());
    assertEquals(D.plusDays(18), ReviewSchedule.replay(List.of(ok(0), ok(1), ok(4), ok(11))).dueOn(), "7 days repeats");
    assertEquals(3, ReviewSchedule.replay(List.of(ok(0), ok(1), ok(4), ok(11))).reviews());
  }

  @Test
  void aMissReturnsTheNextDayAndRestartsTheLadder() {
    var s = ReviewSchedule.replay(List.of(ok(0), ok(1), ok(4), miss(11)));
    assertEquals(D.plusDays(12), s.dueOn());
    assertEquals(0, s.stage());
    assertEquals("missed", s.lastOutcome());
    assertEquals(D.plusDays(13), ReviewSchedule.replay(List.of(ok(0), ok(1), ok(4), miss(11), ok(12))).dueOn(), "back to 1 day");
    assertEquals(D.plusDays(3), ReviewSchedule.replay(List.of(ok(0), miss(2))).dueOn(), "a miss before the due date also counts");
  }

  @Test
  void aHintedSuccessRepeatsTheIntervalInsteadOfClimbing() {
    var s = ReviewSchedule.replay(List.of(ok(0), ok(1), hinted(4)));
    assertEquals(2, s.stage());
    assertEquals(D.plusDays(7), s.dueOn(), "3 days again, not 7");
    assertEquals("hinted", s.lastOutcome());
    assertEquals(0, ReviewSchedule.replay(List.of(hinted(0))).stage(), "a hinted first success is not yet remembered");
  }

  @Test
  void practiceBeforeTheDueDateCannotSkipIntervals() {
    var crammed = ReviewSchedule.replay(List.of(ok(0), ok(0), ok(0), ok(0)));
    assertEquals(D.plusDays(1), crammed.dueOn());
    assertEquals(1, crammed.stage());
    var s = ReviewSchedule.replay(List.of(ok(0), ok(1), ok(2)));
    assertEquals(D.plusDays(4), s.dueOn(), "day 2 is before the 3-day review");
    assertEquals(D.plusDays(1), s.lastEvidence());
  }

  @Test
  void eventsAreReplayedInDayOrderAndDueIsInclusive() {
    var s = ReviewSchedule.replay(List.of(ok(1), ok(0)));
    assertEquals(D.plusDays(4), s.dueOn());
    assertTrue(s.due(D.plusDays(4)));
    assertFalse(s.due(D.plusDays(3)));
    assertNull(ReviewSchedule.replay(List.of()).dueOn());
    assertFalse(ReviewSchedule.replay(List.of()).due(D));
  }
}
