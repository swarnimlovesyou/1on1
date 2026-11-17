package com.oneonone;

import java.util.*;
import java.util.function.DoubleUnaryOperator;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * Performance lab (Phase 3): counts the steps of the real Java teaching traces on random inputs of growing size and
 * compares the growth with reference curves. Steps are the trace's operations, not wall-clock time.
 */
@Service
public class LabService {

  static final List<String> SUPPORTED = List.of("binary-search", "two-pointers", "sliding-window", "merge-sort", "quick-sort");
  static final List<Integer> SIZES = List.of(4, 8, 16, 32); // the trace engine's teaching inputs hold at most 32 values
  static final int RUNS = 3;
  static final Map<String, DoubleUnaryOperator> CURVES = new LinkedHashMap<>();

  static {
    CURVES.put("log n", n -> Math.log(n) / Math.log(2));
    CURVES.put("n", n -> n);
    CURVES.put("n log n", n -> n * Math.log(n) / Math.log(2));
    CURVES.put("n²", n -> n * n);
  }

  final TraceEngine traces;

  public LabService(TraceEngine traces) {
    this.traces = traces;
  }

  /** Inputs chosen so each algorithm does its full work: absent targets for the searches, random values for the sorts. */
  Map<String, Object> scene(String algorithm, int n, Random r) {
    var values = new ArrayList<Integer>();
    while (values.size() < n) {
      int v = r.nextInt(9000) + 1;
      if (!values.contains(v)) values.add(v);
    }
    int target = switch (algorithm) {
      case "binary-search" -> 10000;
      case "two-pointers" -> -1;
      case "sliding-window" -> Math.max(1, n / 4);
      default -> 3;
    };
    return Map.of("algorithm", algorithm, "input", String.join(",", values.stream().map(String::valueOf).toList()), "target", target, "seed", 42);
  }

  public Map<String, Object> measure(String algorithm) {
    if (!SUPPORTED.contains(algorithm))
      throw new ResponseStatusException(HttpStatus.NOT_FOUND, "The lab measures " + String.join(", ", SUPPORTED) + ".");
    var steps = new ArrayList<Double>();
    for (int n : SIZES) {
      double total = 0;
      for (int run = 0; run < RUNS; run++) {
        var trace = traces.trace(scene(algorithm, n, new Random(n * 1009L + run)));
        total += Store.items(trace.get("steps")).size();
      }
      steps.add(total / RUNS);
    }
    double lastN = SIZES.getLast(), lastSteps = steps.getLast();
    var curves = new LinkedHashMap<String, Object>();
    String closest = null;
    double best = Double.MAX_VALUE;
    for (var e : CURVES.entrySet()) {
      double scale = lastSteps / e.getValue().applyAsDouble(lastN);
      var points = SIZES.stream().map(n -> scale * e.getValue().applyAsDouble(n)).toList();
      curves.put(e.getKey(), points);
      double error = 0;
      for (int i = 0; i < SIZES.size(); i++) error += Math.pow(Math.log(steps.get(i)) - Math.log(points.get(i)), 2);
      if (error < best) {
        best = error;
        closest = e.getKey();
      }
    }
    var out = new LinkedHashMap<String, Object>();
    out.put("algorithm", algorithm);
    out.put("sizes", SIZES);
    out.put("steps", steps);
    out.put("curves", curves);
    out.put("closest", closest);
    return out;
  }
}
