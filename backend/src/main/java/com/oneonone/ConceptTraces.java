package com.oneonone;

import java.util.*;

/** Bounded authored concept executions, independent of an external judge or AI. */
final class ConceptTraces {

  static final Set<String> SUPPORTED = Set.of(
    "complexity",
    "arrays",
    "strings",
    "hashing",
    "prefix-sums",
    "variable-window",
    "intervals",
    "matrices",
    "graphs"
  );

  static Map<String, Object> trace(Map<String, Object> body) {
    String algorithm = Store.text(body, "algorithm", "");
    int target = new TraceEngine().number(body, "target", 3);
    String input = Store.text(body, "input", "2,1,5");
    String words = Store.text(
      body,
      "words",
      algorithm.equals("strings") ? "cat" : "abca"
    );
    if (
      words.length() > 64 || words.chars().anyMatch(x -> x > 127)
    ) throw new IllegalArgumentException(
      "Use up to 64 ASCII characters in this text model."
    );
    List<Integer> values = Set.of(
      "strings",
      "variable-window",
      "complexity"
    ).contains(algorithm)
      ? List.of()
      : numbers(input);
    String family = switch (algorithm) {
      case "strings", "variable-window" -> "text";
      case "hashing" -> "hash";
      case "intervals" -> "intervals";
      case "matrices" -> "matrix";
      case "graphs" -> "graph";
      case "complexity" -> "growth";
      default -> "array";
    };
    var r = new TraceEngine.Run(family, values);
    r.algorithm = algorithm;
    try {
      r.seed = Long.parseLong(Store.text(body, "seed", "42"));
    } catch (Exception e) {
      throw new IllegalArgumentException("Seed must be an integer.");
    }
    var view = new LinkedHashMap<String, Object>();
    view.put("kind", algorithm);
    r.extra.put("visual", view);
    List<String> code;
    switch (algorithm) {
      case "complexity" -> {
        int n = target;
        if (n < 0 || n > 16) throw new IllegalArgumentException(
          "Compare growth for n from 0 to 16."
        );
        code = List.of(
          "for (i = 0; i < n; i++) linear++;",
          "for (i = 0; i < n; i++) for (j = 0; j < n; j++) pairs++;",
          "for (x = n; x > 0; x /= 2) halving++;"
        );
        view.put("n", n);
        view.put("counts", List.of(0, 0, 0));
        r.step(
          "Choose an operation, then count visits. These are operation counts, not milliseconds.",
          0,
          List.of(),
          Map.of("n", n)
        );
        int linear = 0,
          square = 0,
          halves = 0;
        for (int i = 0; i < n; i++) {
          linear++;
          view.put("counts", List.of(linear, 0, 0));
          view.put("scan", i);
          r.step(
            "Visit scan position " + i + " once.",
            0,
            List.of(),
            Map.of("linear", linear)
          );
        }
        for (int i = 0; i < n; i++) {
          square += n;
          view.put("counts", List.of(linear, square, 0));
          view.put("row", i);
          r.step(
            "Count row " + i + " of n ordered pairs: " + n + " more visits.",
            1,
            List.of(),
            Map.of("pairs", square)
          );
        }
        for (int x = n; x > 0; x /= 2) {
          halves++;
          view.put("counts", List.of(linear, square, halves));
          view.put("halvingValue", x);
          r.step(
            "Halving visits " + x + "; the next scale is " + x / 2 + ".",
            2,
            List.of(),
            Map.of("halving", halves, "x", x)
          );
        }
        r.step(
          "Compare the completed counts at the same input size.",
          2,
          List.of(),
          Map.of("linear", linear, "pairs", square, "halving", halves)
        );
      }
      case "arrays" -> {
        code = List.of(
          "long total = 0;",
          "for (int i = 0; i < a.length; i++) {",
          "  total += a[i];",
          "}"
        );
        long total = 0;
        view.put("consumed", -1);
        view.put("total", 0);
        r.step(
          "Every slot has its own index. The sum starts at zero.",
          0,
          List.of(),
          Map.of("total", 0)
        );
        for (int i = 0; i < values.size(); i++) {
          long previous = total;
          total += values.get(i);
          view.put("consumed", i);
          view.put("total", total);
          view.put(
            "equation",
            previous + " + " + values.get(i) + " = " + total
          );
          r.step(
            "Read slot " +
              i +
              " and add only that value to the consumed prefix.",
            2,
            List.of(i),
            Map.of("i", i, "total", total)
          );
        }
      }
      case "strings" -> {
        code = List.of(
          "StringBuilder out = new StringBuilder();",
          "for (int i = s.length()-1; i >= 0; i--) {",
          "  out.append(s.charAt(i));",
          "}"
        );
        view.put("characters", characters(words));
        view.put("output", List.of());
        r.step(
          "The source string is immutable. Read it backwards into a separate output buffer.",
          0,
          List.of(),
          Map.of("output", "")
        );
        var output = new ArrayList<String>();
        for (int i = words.length() - 1; i >= 0; i--) {
          output.add(String.valueOf(words.charAt(i)));
          view.put("cursor", i);
          view.put("output", List.copyOf(output));
          r.step(
            "Copy character at index " + i + " to the end of the output.",
            2,
            List.of(),
            Map.of("index", i, "output", String.join("", output))
          );
        }
      }
      case "hashing" -> {
        code = List.of(
          "Map<Integer,Integer> counts = new LinkedHashMap<>();",
          "for (int value : a) {",
          "  counts.merge(value, 1, Integer::sum);",
          "}"
        );
        var counts = new LinkedHashMap<Integer, Integer>();
        view.put("entries", List.of());
        view.put("bucketCount", 4);
        r.step(
          "Illustrative bucket rule: floorMod(key,4). Equality distinguishes keys sharing a bucket; these are not JVM memory addresses.",
          0,
          List.of(),
          Map.of("unique", 0)
        );
        for (int i = 0; i < values.size(); i++) {
          int value = values.get(i),
            bucket = Math.floorMod(value, 4);
          boolean repeat = counts.containsKey(value);
          view.put("key", value);
          view.put("bucket", bucket);
          view.put("phase", "lookup");
          r.step(
            "Look for exact key " +
              value +
              " inside illustrative bucket " +
              bucket +
              ".",
            1,
            List.of(i),
            Map.of("key", value, "bucket", bucket)
          );
          counts.merge(value, 1, Integer::sum);
          view.put(
            "entries",
            counts
              .entrySet()
              .stream()
              .map(e ->
                Map.of(
                  "id",
                  "key-" + e.getKey(),
                  "key",
                  e.getKey(),
                  "count",
                  e.getValue(),
                  "bucket",
                  Math.floorMod(e.getKey(), 4)
                )
              )
              .toList()
          );
          view.put("phase", repeat ? "increment" : "insert");
          r.step(
            repeat
              ? "The key already exists: increment its count without creating a second entry."
              : "Insert a new exact key with count one.",
            2,
            List.of(i),
            Map.of(
              "key",
              value,
              "count",
              counts.get(value),
              "unique",
              counts.size()
            )
          );
        }
      }
      case "prefix-sums" -> {
        code = List.of(
          "long[] prefix = new long[a.length+1];",
          "for (int i=0; i<a.length; i++) prefix[i+1]=prefix[i]+a[i];",
          "return prefix[right]-prefix[left]; // [left,right)"
        );
        var prefix = new ArrayList<Long>();
        prefix.add(0L);
        view.put("prefix", prefix);
        view.put("consumed", -1);
        r.step(
          "Boundary zero stores zero: no values have been consumed.",
          0,
          List.of(),
          Map.of("prefix", List.copyOf(prefix))
        );
        long sum = 0;
        for (int i = 0; i < values.size(); i++) {
          sum += values.get(i);
          prefix.add(sum);
          view.put("prefix", prefix);
          view.put("consumed", i);
          r.step(
            "Store the sum before boundary " + (i + 1) + ".",
            1,
            List.of(i),
            Map.of("boundary", i + 1, "sum", sum)
          );
        }
        int left = 0,
          right = values.size();
        if (body.containsKey("words") && !words.isBlank()) {
          var bounds = numbers(words);
          if (bounds.size() != 2) throw new IllegalArgumentException(
            "Enter query boundaries as left,right."
          );
          left = bounds.get(0);
          right = bounds.get(1);
        }
        if (
          left < 0 || left > right || right > values.size()
        ) throw new IllegalArgumentException(
          "Use 0 <= left <= right <= input length."
        );
        long answer = prefix.get(right) - prefix.get(left);
        view.put("left", left);
        view.put("rightExclusive", right);
        view.put(
          "equation",
          prefix.get(right) + " − " + prefix.get(left) + " = " + answer
        );
        r.step(
          "Subtract the sum before the left boundary from the sum before the right boundary.",
          2,
          List.of(),
          Map.of("left", left, "right", right, "result", answer)
        );
      }
      case "variable-window" -> {
        code = List.of(
          "Set<Character> window = new HashSet<>(); int left=0,best=0;",
          "for (int right=0; right<s.length(); right++) {",
          "  while(window.contains(s.charAt(right))) window.remove(s.charAt(left++));",
          "  window.add(s.charAt(right)); best=Math.max(best,right-left+1);",
          "}"
        );
        view.put("characters", characters(words));
        view.put("left", 0);
        view.put("right", -1);
        view.put("members", List.of());
        r.step(
          "Grow a contiguous frame; shrink until no character repeats.",
          0,
          List.of(),
          Map.of("best", 0)
        );
        var set = new LinkedHashSet<Character>();
        int left = 0,
          best = 0;
        for (int right = 0; right < words.length(); right++) {
          char incoming = words.charAt(right);
          view.put("incoming", String.valueOf(incoming));
          view.put("right", right);
          while (set.contains(incoming)) {
            char removed = words.charAt(left++);
            set.remove(removed);
            view.put("left", left);
            view.put("members", set.stream().map(String::valueOf).toList());
            view.put("phase", "shrink");
            r.step(
              "Remove '" +
                removed +
                "' from the left; keep shrinking if the duplicate is still inside.",
              2,
              List.of(),
              Map.of("left", left, "right", right, "best", best)
            );
          }
          set.add(incoming);
          best = Math.max(best, right - left + 1);
          view.put("left", left);
          view.put("best", best);
          view.put("members", set.stream().map(String::valueOf).toList());
          view.put("phase", "extend");
          r.step(
            "The restored frame has distinct characters. Compare its length with best.",
            3,
            List.of(),
            Map.of("left", left, "right", right, "best", best)
          );
        }
      }
      case "intervals" -> {
        code = List.of(
          "sort(intervals, byStart); // closed endpoints",
          "for (Interval next : intervals) {",
          "  if (disjoint) output.add(copy(next));",
          "  else last.end = max(last.end,next.end);",
          "}"
        );
        if (values.size() % 2 != 0) throw new IllegalArgumentException(
          "Enter interval start,end pairs: 1,3,2,6,8,10."
        );
        var intervals = new ArrayList<Map<String, Object>>();
        for (int i = 0; i < values.size(); i += 2) {
          if (
            values.get(i) > values.get(i + 1)
          ) throw new IllegalArgumentException(
            "Each closed interval needs start <= end."
          );
          intervals.add(
            new LinkedHashMap<>(
              Map.of(
                "id",
                "interval-" + i / 2,
                "start",
                values.get(i),
                "end",
                values.get(i + 1)
              )
            )
          );
        }
        view.put("intervals", intervals);
        view.put("output", List.of());
        r.step(
          "Draw each closed interval on the same number line.",
          0,
          List.of(),
          Map.of("intervals", intervals.size())
        );
        intervals.sort(
          Comparator.comparingInt(x -> ((Number) x.get("start")).intValue())
        );
        view.put("intervals", intervals);
        r.step(
          "Order starts before merging. Touching closed endpoints overlap.",
          0,
          List.of(),
          Map.of("phase", "sorted")
        );
        var output = new ArrayList<Map<String, Object>>();
        for (var next : intervals) {
          view.put("current", next.get("id"));
          boolean disjoint =
            output.isEmpty() ||
            ((Number) output.getLast().get("end")).intValue() <
              ((Number) next.get("start")).intValue();
          if (disjoint) output.add(new LinkedHashMap<>(next));
          else output
            .getLast()
            .put(
              "end",
              Math.max(
                ((Number) output.getLast().get("end")).intValue(),
                ((Number) next.get("end")).intValue()
              )
            );
          view.put("output", output);
          r.step(
            disjoint
              ? "Append a separate interval."
              : "Extend the last merged end; the covered range stays continuous.",
            disjoint ? 2 : 3,
            List.of(),
            Map.of("merged", output.size())
          );
        }
      }
      case "matrices" -> {
        code = List.of(
          "int[][] out = new int[cols][rows];",
          "for (int r=0; r<rows; r++) for (int c=0; c<cols; c++) {",
          "  out[c][r] = input[r][c];",
          "}"
        );
        int cols = target;
        if (
          cols < 1 || cols > 8 || values.isEmpty() || values.size() % cols != 0
        ) throw new IllegalArgumentException(
          "Use 1–8 columns and a nonempty value count divisible by the column count."
        );
        int rows = values.size() / cols;
        if (rows > 8) throw new IllegalArgumentException(
          "Use at most eight rows."
        );
        var output = new ArrayList<Object>(
          Collections.nCopies(values.size(), null)
        );
        view.put("rows", rows);
        view.put("cols", cols);
        view.put("output", output);
        r.step(
          "A " +
            rows +
            " × " +
            cols +
            " input becomes a " +
            cols +
            " × " +
            rows +
            " output.",
          0,
          List.of(),
          Map.of("rows", rows, "columns", cols)
        );
        for (int i = 0; i < values.size(); i++) {
          int row = i / cols,
            col = i % cols;
          output.set(col * rows + row, values.get(i));
          view.put("source", i);
          view.put("destination", col * rows + row);
          view.put("output", output);
          r.step(
            "Copy (" + row + "," + col + ") to (" + col + "," + row + ").",
            2,
            List.of(i),
            Map.of(
              "source row",
              row,
              "source column",
              col,
              "output row",
              col,
              "output column",
              row
            )
          );
        }
      }
      case "graphs" -> {
        code = List.of(
          "create one outgoing row per vertex;",
          "for (Edge e : edges) {",
          "  adjacency[e.from].add(e.to); // directed",
          "}"
        );
        int n = target;
        if (
          n < 1 || n > 8 || values.size() % 2 != 0
        ) throw new IllegalArgumentException(
          "Use 1–8 vertices and pairs of directed edge endpoints."
        );
        var adjacency = new ArrayList<List<Integer>>();
        for (int i = 0; i < n; i++) adjacency.add(new ArrayList<>());
        r.setArray(Collections.nCopies(n, -1));
        r.extra.put("vertexCount", n);
        r.extra.put("edges", List.of());
        view.put("adjacency", adjacency);
        r.step(
          "Create a row for every vertex, including isolated ones.",
          0,
          List.of(),
          Map.of("vertices", n)
        );
        var edges = new ArrayList<Map<String, Object>>();
        for (int i = 0; i < values.size(); i += 2) {
          int from = values.get(i),
            to = values.get(i + 1);
          if (
            from < 0 || to < 0 || from >= n || to >= n
          ) throw new IllegalArgumentException(
            "Vertex IDs must be 0..vertex count-1."
          );
          adjacency.get(from).add(to);
          edges.add(Map.of("from", from, "to", to, "weight", 1));
          r.extra.put("edges", edges);
          view.put("adjacency", adjacency);
          view.put("edgeIndex", i / 2);
          r.extra.put("activeEdge", "edge-" + from + "-" + to);
          r.step(
            "Store directed edge " + from + " → " + to + " in its source row.",
            2,
            List.of(from, to),
            Map.of("from", from, "to", to, "edges", edges.size())
          );
        }
      }
      default -> throw new IllegalArgumentException("Unsupported concept.");
    }
    var normalized = new LinkedHashMap<>(body);
    normalized.put("algorithm", algorithm);
    normalized.put("input", input);
    normalized.put("target", target);
    normalized.put("seed", r.seed);
    if (
      Set.of("strings", "variable-window").contains(algorithm)
    ) normalized.put("words", words);
    return Map.of(
      "version",
      2,
      "revision",
      3,
      "algorithm",
      algorithm,
      "family",
      family,
      "input",
      normalized,
      "steps",
      r.steps,
      "result",
      r.steps.getLast(),
      "code",
      code
    );
  }

  static List<Integer> numbers(String input) {
    if (input.isBlank()) return List.of();
    return new TraceEngine().parse(input);
  }

  static List<String> characters(String value) {
    return value
      .chars()
      .mapToObj(c -> String.valueOf((char) c))
      .toList();
  }
}
