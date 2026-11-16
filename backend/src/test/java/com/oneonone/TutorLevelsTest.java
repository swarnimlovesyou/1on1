package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.server.ResponseStatusException;

/** Graduated help is a bounded ladder, checked before any provider call. */
class TutorLevelsTest {

  final TutorService tutor = new TutorService(new Store(null), new TraceEngine(), null, null);
  final UsernamePasswordAuthenticationToken learner = new UsernamePasswordAuthenticationToken("learner", null, List.of());

  @Test
  void eachLevelAsksForMoreHelpThanTheLastAndNoneGivesTheSolutionUnasked() {
    assertEquals("", TutorService.helpLevel(0));
    Set<String> seen = new HashSet<>();
    for (int level = 1; level <= 4; level++) {
      String text = TutorService.helpLevel(level);
      assertTrue(text.startsWith("Help level " + level + " of 4"), text);
      assertTrue(seen.add(text));
    }
    assertTrue(TutorService.helpLevel(1).contains("Give no hint or answer yet"));
    assertTrue(TutorService.helpLevel(4).contains("only if they explicitly ask"));
  }

  @Test
  void anOutOfRangeLevelIsRejectedAndAMissingKeyIsReportedHonestly() {
    tutor.key = "";
    tutor.model = "gemini-3.1-flash-lite";
    var offline = assertThrows(ResponseStatusException.class, () -> tutor.tutor(learner, Map.of("message", "help", "level", 1)));
    assertEquals(503, offline.getStatusCode().value());
    tutor.key = "configured-but-never-called";
    assertThrows(IllegalArgumentException.class, () -> tutor.tutor(learner, Map.of("message", "help", "level", 7)));
    assertThrows(IllegalArgumentException.class, () -> tutor.tutor(learner, Map.of("message", "help", "level", -1)));
  }
}
