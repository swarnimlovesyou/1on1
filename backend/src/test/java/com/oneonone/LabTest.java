package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.web.server.ResponseStatusException;

/** The performance lab: step counts of the real Java traces over growing inputs, compared with reference curves. */
class LabTest {

  LabService lab = new LabService(new TraceEngine());

  @Test
  void eachSupportedAlgorithmFitsItsTextbookGrowth() {
    Map<String, String> expected = Map.of(
      "binary-search", "log n",
      "two-pointers", "n",
      "sliding-window", "n",
      "merge-sort", "n log n",
      "quick-sort", "n log n"
    );
    for (var e : expected.entrySet()) {
      var r = lab.measure(e.getKey());
      assertEquals(List.of(4, 8, 16, 32), r.get("sizes"), e.getKey());
      var steps = (List<?>) r.get("steps");
      assertEquals(4, steps.size());
      for (int i = 1; i < steps.size(); i++)
        assertTrue(((Number) steps.get(i)).doubleValue() >= ((Number) steps.get(i - 1)).doubleValue(), e.getKey() + " never shrinks");
      assertEquals(e.getValue(), r.get("closest"), e.getKey() + " steps " + steps);
    }
  }

  @Test
  void measurementsAreRepeatableAndCurvesMatchTheLargestSize() {
    assertEquals(lab.measure("merge-sort"), lab.measure("merge-sort"));
    var r = lab.measure("two-pointers");
    var curves = (Map<?, ?>) r.get("curves");
    assertEquals(Set.of("log n", "n", "n log n", "n²"), curves.keySet());
    double last = ((Number) ((List<?>) r.get("steps")).get(3)).doubleValue();
    for (var c : curves.values()) assertEquals(last, ((Number) ((List<?>) c).get(3)).doubleValue(), 1e-6, "each curve is scaled to the measured value at n = 32");
  }

  @Test
  void anUnsupportedAlgorithmIsNotFound() {
    var e = assertThrows(ResponseStatusException.class, () -> lab.measure("max-flow"));
    assertEquals(404, e.getStatusCode().value());
    assertEquals(List.of("binary-search", "two-pointers", "sliding-window", "merge-sort", "quick-sort"), LabService.SUPPORTED);
  }
}
