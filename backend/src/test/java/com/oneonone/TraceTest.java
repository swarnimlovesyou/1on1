package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.Test;

class TraceTest {

  final TraceEngine engine = new TraceEngine();

  @Test
  void singleValueAndEmptyStructuresAreHandled() {
    for (String alg : TraceEngine.SUPPORTED)
      assertFalse(
        Store.items(
          engine
            .trace(Map.of("algorithm", alg, "input", "1", "target", 1))
            .get("steps")
        ).isEmpty(),
        alg
      );
  }

  @Test
  void invalidScalarBoundsAreNotSilentlyClamped() {
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(
        Map.of("algorithm", "quickselect", "input", "1", "target", 2)
      )
    );
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(Map.of("algorithm", "recursion", "target", 11))
    );
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(Map.of("algorithm", "tabulation", "target", 17))
    );
  }

  @Test
  void everySceneHasBoundedInterpretableSteps() {
    for (String alg : TraceEngine.SUPPORTED) {
      var result = engine.trace(
        Map.of("algorithm", alg, "input", "4, 2, 7, 1, 3, 6", "target", 3)
      );
      var steps = Store.items(result.get("steps"));
      assertFalse(steps.isEmpty(), alg);
      assertTrue(steps.size() <= 1000);
      assertTrue(
        steps
          .stream()
          .allMatch(
            s ->
              s.containsKey("text") &&
              s.containsKey("array") &&
              s.containsKey("variables")
          )
      );
    }
  }

  @Test
  void invalidInputIsRejected() {
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(Map.of("input", ""))
    );
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(Map.of("input", "a,b"))
    );
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(Map.of("algorithm", "not-supported"))
    );
    assertThrows(IllegalArgumentException.class, () ->
      engine.trace(
        Map.of("algorithm", "sliding-window", "input", "1,2", "target", 3)
      )
    );
  }

  @Test
  void parsesMultipleDigitAndNegativeValues() {
    assertEquals(List.of(12, -3, 100), engine.parse("12, -3, 100"));
  }

  @Test
  void sortingTracesMatchOracle() {
    for (String alg : List.of("merge-sort", "quick-sort")) {
      var r = engine.trace(Map.of("algorithm", alg, "input", "4, -2, 4, 0"));
      assertEquals(
        List.of(-2, 0, 4, 4),
        ((Map<?, ?>) r.get("result")).get("array")
      );
    }
  }

  @Test
  void negativeSlidingWindow() {
    var r = engine.trace(
      Map.of("algorithm", "sliding-window", "input", "-4, -2, -3", "target", 2)
    );
    assertEquals(
      -5,
      ((Map<?, ?>) ((Map<?, ?>) r.get("result")).get("variables")).get("best")
    );
  }

  @Test
  void traceSnapshotsDoNotAlias() {
    var r = engine.trace(Map.of("algorithm", "stack", "input", "1,2,3"));
    var steps = Store.items(r.get("steps"));
    assertEquals(List.of(1), steps.get(1).get("array"));
    assertEquals(List.of(), steps.getLast().get("array"));
  }

  @Test
  void fibonacciModesAgree() {
    for (String alg : List.of("memoization", "tabulation")) {
      var r = engine.trace(Map.of("algorithm", alg, "target", 8));
      assertEquals(
        21,
        ((Map<?, ?>) ((Map<?, ?>) r.get("result")).get("variables")).get(
          "result"
        )
      );
    }
  }

  @Test
  void largestDescendingInputFinishesWithoutSilentTraceTruncation() {
    String input = java.util.stream.IntStream.iterate(32, x -> x - 1)
      .limit(32)
      .mapToObj(String::valueOf)
      .collect(java.util.stream.Collectors.joining(","));
    var trace = engine.trace(Map.of("algorithm", "quick-sort", "input", input));
    assertEquals(
      java.util.stream.IntStream.rangeClosed(1, 32).boxed().toList(),
      ((Map<?, ?>) trace.get("result")).get("array")
    );
    assertTrue(Store.items(trace.get("steps")).size() < 1000);
  }

  @Test
  void dfsFinishesOneBranchBeforeEnteringItsNextSibling() {
    var trace = engine.trace(
      Map.of("algorithm", "dfs", "input", "4,2,7,1,3,6")
    );
    var steps = Store.items(trace.get("steps"));
    var entries = new ArrayList<Integer>();
    var returns = new ArrayList<Integer>();
    for (var step : steps) {
      var vars = (Map<String, Object>) step.get("variables");
      if (step.get("text").toString().startsWith("Enter vertex")) entries.add(
        ((Number) vars.get("visiting")).intValue()
      );
      if (vars.containsKey("returning")) returns.add(
        ((Number) vars.get("returning")).intValue()
      );
    }
    assertEquals(List.of(0, 1, 2, 3, 4, 5), entries);
    assertEquals(List.of(5, 4, 3, 2, 1, 0), returns);
    assertEquals(
      List.of(0, 1, 2, 3, 4, 5),
      ((Map<?, ?>) trace.get("result")).get("array")
    );
  }
}
