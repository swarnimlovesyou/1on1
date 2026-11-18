package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.Test;

/** Step-by-step traces for the board-rendered concepts: each ends on the right answer and every step carries panels. */
class BoardTracesTest {

  final TraceEngine engine = new TraceEngine();

  Map<String, Object> run(String algorithm, String input, int target, String words) {
    var body = new LinkedHashMap<String, Object>();
    body.put("algorithm", algorithm);
    if (input != null) body.put("input", input);
    body.put("target", target);
    if (words != null) body.put("words", words);
    return engine.trace(body);
  }

  @SuppressWarnings("unchecked")
  Object answer(Map<String, Object> trace) {
    var steps = Store.items(trace.get("steps"));
    assertTrue(steps.size() >= 3, "a real walk-through, not a jump to the end");
    for (var s : steps) {
      assertFalse(s.get("text").toString().isBlank());
      var panels = Store.items(((Map<String, Object>) s.get("visual")).get("board"));
      assertFalse(panels.isEmpty(), "every step has something to draw");
    }
    return ((Map<String, Object>) steps.getLast().get("variables")).get("answer");
  }

  @Test
  @SuppressWarnings("unchecked")
  void boardPanelsSurviveTheTypedTraceContract() {
    var typed = Contracts.ExecutionTrace.from(run("lcs", null, 0, "ab|b"));
    assertFalse(Store.items(typed.steps().getFirst().visual().get("board")).isEmpty());
  }

  @Test
  @SuppressWarnings("unchecked")
  void graphTraces() {
    assertEquals(2, answer(run("union-find", "0,1,2,3,1,2,4,5", 6, null)));
    assertEquals(List.of(0, 1, 2, 3, 4), answer(run("topological-sort", "0,2,1,2,2,3,3,4,1,4", 5, null)));
    assertEquals(11, answer(run("kruskal", "0,1,4,0,2,1,1,2,2,1,3,5,2,3,8,3,4,3", 5, null)));
    assertEquals(List.of(0, 2, 7, 4), answer(run("bellman-ford", "0,1,6,0,2,7,1,2,8,1,3,5,2,3,-3,3,1,-2", 4, null)));
    assertEquals(6, answer(run("floyd-warshall", "0,1,3,1,2,1,0,2,7,2,3,2", 4, null)), "0 to 3 is 3+1+2");
    assertEquals("cycle", answer(run("topological-sort", "0,1,1,2,2,0", 3, null)));
    assertEquals("negative cycle", answer(run("bellman-ford", "0,1,1,1,2,-2,2,1,1", 3, null)));
    assertEquals("negative cycle", answer(run("floyd-warshall", "0,1,1,1,0,-3", 2, null)));
    var dup = Store.items(run("kruskal", "0,1,5,0,1,2", 2, null).get("steps")).getLast();
    var edges = Store.items(Store.items(((Map<String, Object>) dup.get("visual")).get("board")).getFirst().get("edges"));
    assertEquals(List.of("rejected", "chosen"), edges.stream().map(e -> e.get("state")).toList(), "a parallel edge keeps its own mark");
    assertEquals(3, run("lcs", null, 0, "ab|b").get("revision"), "study position saving accepts this revision");
  }

  @Test
  void arrayAndTreeTraces() {
    assertEquals(13, answer(run("segment-tree", "5,2,7,1,3,6|1,4", 0, null)));
    assertEquals(18, answer(run("fenwick", "5,2,7,1,3,6", 4, null)));
    assertEquals(3, answer(run("interval-scheduling", "1,4,3,5,0,6,5,7,3,9,5,9,6,10,8,11", 0, null)));
    assertEquals(4, answer(run("bits", "4,1,2,1,2", 0, null)));
    assertEquals(List.of(5, 5, 6, -1, 3, -1), answer(run("monotonic-stack", "2,1,5,6,2,3", 0, null)));
    assertEquals(List.of(3, 3, 5, 5, 6, 7), answer(run("monotonic-queue", "1,3,-1,-3,5,3,6,7", 3, null)));
  }

  @Test
  void stringAndTableTraces() {
    assertEquals(6, answer(run("kmp", null, 0, "abxabcabcaby|abcaby")));
    assertEquals(-1, answer(run("kmp", null, 0, "aaaa|ab")));
    assertEquals(4, answer(run("rabin-karp", null, 0, "abracadabra|cad")));
    assertEquals(9, answer(run("knapsack", "1,1,3,4,4,5,5,7", 7, null)));
    assertEquals(3, answer(run("lcs", null, 0, "abcde|ace")));
    assertEquals(4500, answer(run("interval-dp", "10,30,5,60", 0, null)));
  }

  @Test
  void inputsOutsideTheTeachingLimitsAreRejected() {
    assertThrows(IllegalArgumentException.class, () -> run("union-find", "0,9", 3, null));
    assertThrows(IllegalArgumentException.class, () -> run("kruskal", "0,1", 3, null));
    assertThrows(IllegalArgumentException.class, () -> run("knapsack", "1,1", 99, null));
    assertThrows(IllegalArgumentException.class, () -> run("lcs", null, 0, "no-separator"));
    assertThrows(IllegalArgumentException.class, () -> run("segment-tree", "1,2,3|2,9", 0, null));
    assertThrows(IllegalArgumentException.class, () -> run("monotonic-queue", "1,2", 5, null));
  }
}
