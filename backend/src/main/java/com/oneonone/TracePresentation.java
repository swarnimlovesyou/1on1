package com.oneonone;

import java.util.*;

/** Supplies semantic display metadata, never guessed execution outcomes. */
final class TracePresentation {

  private static final Map<String, List<String>> CODE = loadCode();

  private static Map<String, List<String>> loadCode() {
    try (
      var stream = TracePresentation.class.getResourceAsStream("/content.json")
    ) {
      var data = new tools.jackson.databind.ObjectMapper().readValue(
        stream,
        Map.class
      );
      var out = new HashMap<String, List<String>>();
      for (var lesson : Store.items(data.get("lessons")))
        if (lesson.get("experiment") instanceof Map<?, ?> scene) out.put(
          scene.get("algorithm").toString(),
          Store.strings(lesson.get("code"))
        );
      return Map.copyOf(out);
    } catch (Exception error) {
      throw new IllegalStateException(
        "Teaching code is missing or invalid.",
        error
      );
    }
  }

  static void enrich(Map<String, Object> trace) {
    String algorithm = trace.get("algorithm").toString();
    var steps = Store.items(trace.get("steps"));
    var input = (Map<String, Object>) trace.get("input");
    List<Integer> source = new TraceEngine().parse(
      input.get("input").toString()
    );
    Map<String, Object> lastFocus = new LinkedHashMap<>();
    var initialEntities = steps.isEmpty()
      ? List.of()
      : steps.getFirst().get("entities");
    for (var step : steps) {
      var view = new LinkedHashMap<String, Object>();
      if (step.get("visual") instanceof Map<?, ?> raw) view.putAll(
        (Map<String, Object>) raw
      );
      view.put("kind", algorithm);
      view.put("original", source);
      var vars = (Map<String, Object>) step.get("variables");
      if (
        Set.of(
          "two-pointers",
          "binary-search",
          "quick-sort",
          "quickselect"
        ).contains(algorithm)
      ) {
        if (vars.containsKey("pivotIndex")) lastFocus.remove("pivot index");
        if (vars.containsKey("pivot index")) lastFocus.remove("scan");
        if (Integer.valueOf(-1).equals(vars.get("result"))) lastFocus.remove(
          "mid"
        );
        lastFocus.putAll(vars);
        view.put("focus", new LinkedHashMap<>(lastFocus));
      } else view.put("focus", vars);
      if (algorithm.equals("linked-list")) view.put("nodes", initialEntities);
      step.put("visual", view);
    }
    trace.put("steps", steps);
    trace.put("result", steps.getLast());
    trace.put("code", CODE.get(algorithm));
  }
}
