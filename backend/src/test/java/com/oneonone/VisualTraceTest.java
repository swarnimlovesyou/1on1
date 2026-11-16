package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.Test;

class VisualTraceTest {

  final TraceEngine engine = new TraceEngine();

  Map<String, Object> run(
    String algorithm,
    String input,
    int target,
    String words
  ) {
    return engine.trace(
      Map.of(
        "algorithm",
        algorithm,
        "input",
        input,
        "target",
        target,
        "words",
        words,
        "seed",
        42
      )
    );
  }

  Map<String, Object> result(Map<String, Object> trace) {
    return (Map<String, Object>) trace.get("result");
  }

  Map<String, Object> view(Map<String, Object> trace) {
    return (Map<String, Object>) result(trace).get("visual");
  }

  @Test
  void everyNotebookHasARealBoundedSceneAndSynchronizedGuide() throws Exception {
    var data = new Store(null).decode(
      new String(
        getClass().getResourceAsStream("/content.json").readAllBytes(),
        java.nio.charset.StandardCharsets.UTF_8
      )
    );
    var algorithms = new HashSet<String>();
    for (var lesson : Store.items(data.get("lessons"))) {
      var trace = engine.trace((Map<String, Object>) lesson.get("experiment"));
      var typed = Contracts.ExecutionTrace.from(trace);
      algorithms.add(typed.algorithm());
      assertEquals(3, typed.revision());
      assertNotNull(typed.code());
      assertFalse(typed.code().isEmpty());
      assertTrue(typed.steps().size() <= 4096);
      for (var step : typed.steps()) {
        assertEquals(typed.algorithm(), step.visual().get("kind"));
        assertTrue(
          step.line() >= 0 && step.line() < typed.code().size(),
          typed.algorithm() + " line " + step.line()
        );
        assertEquals(
          step.entities().size(),
          step.entities().stream().map(Contracts.Entity::id).distinct().count()
        );
      }
    }
    assertEquals(TraceEngine.SUPPORTED, algorithms);
  }

  @Test
  void foundationModelsHaveIndependentNumericalOracles() {
    assertEquals(
      List.of(8, 64, 4),
      view(run("complexity", "8", 8, "")).get("counts")
    );
    assertEquals(
      8L,
      (
        (Number) (
          (Map<?, ?>) result(run("arrays", "2,1,5", 0, "")).get("variables")
        ).get("total")
      ).longValue()
    );
    assertEquals(
      List.of("t", "a", "c"),
      view(run("strings", "", 0, "cat")).get("output")
    );
    var prefix = run("prefix-sums", "2,1,5", 0, "1,3");
    assertEquals(
      6L,
      (
        (Number) ((Map<?, ?>) result(prefix).get("variables")).get("result")
      ).longValue()
    );
    var hash = view(run("hashing", "2,6,2", 0, ""));
    var entries = Store.items(hash.get("entries"));
    assertEquals(2, entries.size());
    assertEquals(2, entries.getFirst().get("count"));
    assertEquals(
      entries.getFirst().get("bucket"),
      entries.getLast().get("bucket")
    );
  }

  @Test
  void variableWindowAgreesWithBruteForceIncludingRepeatedShrinking() {
    var random = new Random(16);
    for (int repeat = 0; repeat < 60; repeat++) {
      var text = new StringBuilder();
      for (int i = 0; i < random.nextInt(16); i++) text.append(
        (char) ('a' + random.nextInt(4))
      );
      int best = 0;
      for (int left = 0; left < text.length(); left++) {
        var seen = new HashSet<Character>();
        for (int right = left; right < text.length(); right++) {
          if (!seen.add(text.charAt(right))) break;
          best = Math.max(best, right - left + 1);
        }
      }
      var trace = run("variable-window", "", 0, text.toString());
      var vars = (Map<?, ?>) result(trace).get("variables");
      assertEquals(best, vars.get("best"), text.toString());
    }
    var steps = Store.items(run("variable-window", "", 0, "abba").get("steps"));
    assertEquals(
      2,
      steps
        .stream()
        .filter(s -> s.get("text").toString().startsWith("Remove"))
        .count()
    );
  }

  @Test
  void transposeAndAdjacencySnapshotsDoNotAliasAndHandleStructure() {
    var matrix = run("matrices", "1,2,3,4,5,6", 3, "");
    assertEquals(List.of(1, 4, 2, 5, 3, 6), view(matrix).get("output"));
    var first = (Map<?, ?>) Store.items(matrix.get("steps"))
      .getFirst()
      .get("visual");
    assertTrue(
      ((List<?>) first.get("output")).stream().allMatch(Objects::isNull)
    );
    var graph = run("graphs", "0,0,0,1,0,1", 3, "");
    assertEquals(
      List.of(List.of(0, 1, 1), List.of(), List.of()),
      view(graph).get("adjacency")
    );
    assertEquals(
      List.of(List.of(), List.of(), List.of()),
      (
        (Map<?, ?>) Store.items(graph.get("steps")).getFirst().get("visual")
      ).get("adjacency")
    );
  }

  @Test
  void closedIntervalsMergeTouchingAndNestedRanges() {
    var output = Store.items(
      view(run("intervals", "1,2,2,3,6,6", 0, "")).get("output")
    );
    assertEquals(2, output.size());
    assertEquals(1, output.getFirst().get("start"));
    assertEquals(3, output.getFirst().get("end"));
    assertEquals(
      1,
      Store.items(
        view(run("intervals", "1,9,2,3,4,5", 0, "")).get("output")
      ).size()
    );
  }

  @Test
  void generalTreesPreserveDuplicateIdentitiesAndEveryTraversal() {
    var inorder = run("tree-traversal", "1,1,1", 0, "inorder");
    var typed = Contracts.ExecutionTrace.from(inorder);
    var root = typed.result().tree();
    assertNotEquals(root.id(), root.left().id());
    assertNotEquals(root.left().id(), root.right().id());
    assertEquals(List.of(1, 1, 1), view(inorder).get("output"));
    assertEquals(
      List.of(4, 2, 1, 3, 7, 6),
      view(run("tree-traversal", "4,2,7,1,3,6", 0, "preorder")).get("output")
    );
    assertEquals(
      List.of(1, 3, 2, 6, 7, 4),
      view(run("tree-traversal", "4,2,7,1,3,6", 0, "postorder")).get("output")
    );
    assertEquals(
      List.of(4, 2, 7, 1, 3, 6),
      view(run("tree-traversal", "4,2,7,1,3,6", 0, "levelorder")).get("output")
    );
  }

  int balanced(Contracts.TreeNode n) {
    if (n == null) return 0;
    int left = balanced(n.left()),
      right = balanced(n.right());
    assertTrue(Math.abs(left - right) <= 1);
    return 1 + Math.max(left, right);
  }

  @Test
  void avlRotationsAreVisibleAndPreserveTheBalanceInvariant() {
    for (String input : List.of(
      "30,20,10",
      "10,20,30",
      "30,10,20",
      "10,30,20"
    )) {
      var trace = Contracts.ExecutionTrace.from(run("avl", input, 0, ""));
      balanced(trace.result().tree());
      assertTrue(
        trace
          .steps()
          .stream()
          .anyMatch(s -> s.text().contains("Reconnect the middle subtree"))
      );
      assertEquals(20, trace.result().tree().value());
    }
  }

  @Test
  void graphDistancesAndFlowCutHaveIndependentOracles() {
    assertEquals(
      List.of(0, 1, 1, 2, 2, 3),
      view(run("bfs", "4,2,7,1,3,6", 0, "")).get("distances")
    );
    var dijkstra = run("dijkstra", "4,2,7,1,3,6", 0, "");
    var edges = Store.items(result(dijkstra).get("edges"));
    int n = 6;
    int[] distance = { 0, 999999, 999999, 999999, 999999, 999999 };
    for (int pass = 0; pass < n; pass++) for (var edge : edges) {
      int u = ((Number) edge.get("from")).intValue(),
        v = ((Number) edge.get("to")).intValue(),
        w = ((Number) edge.get("weight")).intValue();
      distance[v] = Math.min(distance[v], distance[u] + w);
    }
    assertEquals(
      Arrays.stream(distance).boxed().toList(),
      view(dijkstra).get("distances")
    );
    for (String input : List.of("4,2,7,1,3,6", "7,1,6,2,5,3")) {
      var trace = run("max-flow", input, 0, "");
      var flows = Store.items(view(trace).get("flowEdges"));
      int minimum = Integer.MAX_VALUE;
      for (int mask = 1; mask < 1 << n; mask += 2) {
        if ((mask & (1 << (n - 1))) != 0) continue;
        int capacity = 0;
        for (var edge : flows) {
          int u = ((Number) edge.get("from")).intValue(),
            v = ((Number) edge.get("to")).intValue();
          if ((mask & (1 << u)) != 0 && (mask & (1 << v)) == 0) capacity += (
            (Number) edge.get("capacity")
          ).intValue();
        }
        minimum = Math.min(minimum, capacity);
      }
      assertEquals(minimum, view(trace).get("total"));
      assertEquals(minimum, view(trace).get("cutCapacity"));
      int[] balance = new int[n];
      for (var edge : flows) {
        int flow = ((Number) edge.get("flow")).intValue(),
          capacity = ((Number) edge.get("capacity")).intValue();
        assertTrue(flow >= 0 && flow <= capacity);
        balance[((Number) edge.get("from")).intValue()] -= flow;
        balance[((Number) edge.get("to")).intValue()] += flow;
      }
      for (int i = 1; i < n - 1; i++) assertEquals(0, balance[i]);
    }
  }

  @Test
  void bloomQueryCanDemonstrateAnActualFalsePositiveAndCoverReportsInfeasibility() {
    var bloom = view(run("bloom-filter", "1", 0, "a | q"));
    assertEquals(true, bloom.get("possible"));
    assertEquals(false, bloom.get("exact"));
    var cover = run("set-cover", "1", 0, "Arrays,Unknown");
    assertEquals(
      List.of("Unknown"),
      ((Map<?, ?>) result(cover).get("variables")).get("uncovered")
    );
  }

  @Test
  void malformedInputsNeverProduceAVisualSuccess() {
    assertThrows(IllegalArgumentException.class, () ->
      run("matrices", "1,2,3", 2, "")
    );
    assertThrows(IllegalArgumentException.class, () ->
      run("intervals", "3,1", 0, "")
    );
    assertThrows(IllegalArgumentException.class, () ->
      run("graphs", "0,9", 3, "")
    );
    assertThrows(IllegalArgumentException.class, () ->
      run("tree-traversal", "1,null,2,3", 0, "inorder")
    );
    assertThrows(IllegalArgumentException.class, () ->
      run("prefix-sums", "1,2", 0, "2,1")
    );
  }
}
