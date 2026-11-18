package com.oneonone;

import java.util.*;

/**
 * Step-by-step traces for concepts drawn on the generic board: each step carries "board" panels (array, table,
 * graph, stack, text, vars) that the client draws as they are. Inputs are bounded to teaching sizes.
 */
final class BoardTraces {

  static final Set<String> SUPPORTED = Set.of(
    "union-find", "topological-sort", "kruskal", "bellman-ford", "floyd-warshall",
    "segment-tree", "fenwick", "interval-scheduling", "bits", "kmp", "rabin-karp",
    "monotonic-stack", "monotonic-queue", "knapsack", "lcs", "interval-dp"
  );

  static final int INF = Integer.MAX_VALUE / 4;

  private BoardTraces() {}

  /** One trace: the panels for the next step are set, then step() records them with the narration. */
  static final class Board {

    final TraceEngine.Run run;
    final List<String> code;

    Board(String algorithm, List<String> code) {
      run = new TraceEngine.Run("board", List.of());
      run.algorithm = algorithm;
      this.code = code;
    }

    void step(String text, int line, Map<String, Object> vars, Object... panels) {
      // panels ride inside "visual": the typed trace contract keeps that map and drops unknown fields
      run.extra.put("visual", Map.of("kind", run.algorithm, "board", List.of(panels)));
      run.step(text, line, List.of(), vars);
    }
  }

  // ---- panel builders ----

  static Map<String, Object> array(String title, List<?> values, Map<Integer, String> marks) {
    return panel("array", title, "values", values, "marks", marks(marks));
  }

  static Map<String, Object> labelled(String title, List<?> values, List<?> labels, Map<Integer, String> marks) {
    return panel("array", title, "values", values, "labels", labels, "marks", marks(marks));
  }

  static Map<String, Object> stack(String title, List<?> items) {
    return panel("stack", title, "items", items);
  }

  static Map<String, Object> vars(Map<String, Object> items) {
    return panel("vars", "", "items", items);
  }

  static Map<String, Object> text(String title, String chars, int offset, Map<Integer, String> marks) {
    return panel("text", title, "chars", List.of(chars.split("")), "offset", offset, "marks", marks(marks));
  }

  static Map<String, Object> table(String title, List<?> rows, List<?> cols, List<List<Object>> cells, int[] active, List<int[]> refs) {
    var out = panel("table", title, "rows", rows, "cols", cols, "cells", copy(cells));
    if (active != null) out.put("active", List.of(active[0], active[1]));
    out.put("refs", refs.stream().map(r -> List.of(r[0], r[1])).toList());
    return out;
  }

  /** edges: {from,to,w} maps; marks per vertex; edgeMarks keyed "from-to". */
  static Map<String, Object> graph(String title, int n, boolean directed, List<int[]> edges, Map<String, String> edgeMarks, Map<Integer, String> marks, Map<Integer, String> labels) {
    var list = new ArrayList<Map<String, Object>>();
    for (int k = 0; k < edges.size(); k++) {
      var e = edges.get(k);
      var m = new LinkedHashMap<String, Object>();
      m.put("from", e[0]);
      m.put("to", e[1]);
      if (e.length > 2) m.put("w", e[2]);
      m.put("state", edgeMarks.getOrDefault("#" + k, edgeMarks.getOrDefault(e[0] + "-" + e[1], "idle"))); // "#k" marks one parallel edge
      list.add(m);
    }
    var l = new LinkedHashMap<String, Object>();
    labels.forEach((k, v) -> l.put(k.toString(), v));
    return panel("graph", title, "n", n, "directed", directed, "edges", list, "marks", marks(marks), "labels", l);
  }

  static Map<String, Object> panel(String type, String title, Object... kv) {
    var out = new LinkedHashMap<String, Object>();
    out.put("type", type);
    out.put("title", title);
    for (int i = 0; i < kv.length; i += 2) out.put(kv[i].toString(), kv[i + 1]);
    return out;
  }

  static Map<String, Object> marks(Map<Integer, String> marks) {
    var out = new LinkedHashMap<String, Object>();
    marks.forEach((k, v) -> out.put(k.toString(), v));
    return out;
  }

  static List<List<Object>> copy(List<List<Object>> cells) {
    return cells.stream().map(r -> (List<Object>) new ArrayList<>(r)).toList();
  }

  static Map<Integer, String> mark(Object... kv) {
    var out = new LinkedHashMap<Integer, String>();
    for (int i = 0; i < kv.length; i += 2) if ((int) kv[i] >= 0) out.put((int) kv[i], kv[i + 1].toString());
    return out;
  }

  static Map<String, Object> v(Object... kv) {
    var out = new LinkedHashMap<String, Object>();
    for (int i = 0; i < kv.length; i += 2) out.put(kv[i].toString(), kv[i + 1]);
    return out;
  }

  static String show(int d) {
    return d >= INF / 2 ? "∞" : String.valueOf(d);
  }

  static List<Object> shown(int[] d) {
    var out = new ArrayList<Object>();
    for (int x : d) out.add(show(x));
    return out;
  }

  static List<Integer> range(int n) {
    var out = new ArrayList<Integer>();
    for (int i = 0; i < n; i++) out.add(i);
    return out;
  }

  // ---- input parsing ----

  static List<Integer> numbers(String input, int max, String message) {
    List<Integer> out = input == null || input.isBlank() ? List.of() : new TraceEngine().parse(input);
    if (out.size() > max) throw new IllegalArgumentException(message);
    return out;
  }

  static List<int[]> tuples(List<Integer> values, int size, int n, int maxEdges) {
    if (values.size() % size != 0 || values.size() / size > maxEdges) throw new IllegalArgumentException(
      "Give " + (size == 2 ? "pairs of vertices" : "from,to,weight triples") + ", up to " + maxEdges + " edges."
    );
    var out = new ArrayList<int[]>();
    for (int i = 0; i < values.size(); i += size) {
      int[] t = new int[size];
      for (int j = 0; j < size; j++) t[j] = values.get(i + j);
      if (t[0] < 0 || t[0] >= n || t[1] < 0 || t[1] >= n) throw new IllegalArgumentException("Vertex ids must be 0.." + (n - 1) + ".");
      if (size == 3 && Math.abs(t[2]) > 99) throw new IllegalArgumentException("Keep weights between -99 and 99.");
      out.add(t);
    }
    return out;
  }

  static int vertices(int n) {
    if (n < 1 || n > 8) throw new IllegalArgumentException("Use 1 to 8 vertices.");
    return n;
  }

  static String[] pair(String words) {
    String[] parts = words == null ? new String[0] : words.split("\\|", -1);
    if (parts.length != 2 || parts[0].isEmpty() || parts[1].isEmpty() || parts[0].length() > 24 || parts[1].length() > 12
      || words.chars().anyMatch(c -> c > 127)) throw new IllegalArgumentException(
      "Write two ASCII strings separated by |, up to 24 and 12 characters."
    );
    return parts;
  }

  // ---- dispatch ----

  static Map<String, Object> trace(Map<String, Object> body) {
    String algorithm = Store.text(body, "algorithm", "");
    String input = Store.text(body, "input", "");
    String words = Store.text(body, "words", "");
    int target = new TraceEngine().number(body, "target", 0);
    Board b = switch (algorithm) {
      case "union-find" -> unionFind(input, target);
      case "topological-sort" -> topological(input, target);
      case "kruskal" -> kruskal(input, target);
      case "bellman-ford" -> bellmanFord(input, target);
      case "floyd-warshall" -> floyd(input, target);
      case "segment-tree" -> segmentTree(input);
      case "fenwick" -> fenwick(input, target);
      case "interval-scheduling" -> intervals(input);
      case "bits" -> bits(input);
      case "kmp" -> kmp(words);
      case "rabin-karp" -> rabinKarp(words);
      case "monotonic-stack" -> monotonicStack(input);
      case "monotonic-queue" -> monotonicQueue(input, target);
      case "knapsack" -> knapsack(input, target);
      case "lcs" -> lcs(words);
      case "interval-dp" -> matrixChain(input);
      default -> throw new IllegalArgumentException("Unsupported concept.");
    };
    var normalized = new LinkedHashMap<>(body);
    normalized.put("algorithm", algorithm);
    normalized.put("seed", 42);
    var steps = b.run.steps;
    return Map.of("version", 2, "revision", 3, "algorithm", algorithm, "family", "board", "input", normalized,
      "steps", steps, "result", steps.getLast(), "code", b.code);
  }

  // ---- graphs ----

  static int find(int[] parent, int x) {
    while (parent[x] != x) x = parent[x];
    return x;
  }

  static Board unionFind(String input, int target) {
    int n = vertices(target);
    var pairs = tuples(numbers(input, 32, "Up to 16 unions."), 2, n, 16);
    var b = new Board("union-find", List.of(
      "int find(int x) { while (parent[x] != x) x = parent[x]; return x; } // add path compression in production",
      "void union(int a, int b) {",
      "  int ra = find(a), rb = find(b);",
      "  if (ra == rb) return; // already together",
      "  if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }",
      "  parent[rb] = ra; size[ra] += size[rb]; sets--;",
      "}"
    ));
    int[] parent = new int[n], size = new int[n];
    for (int i = 0; i < n; i++) {
      parent[i] = i;
      size[i] = 1;
    }
    int sets = n;
    var links = new ArrayList<int[]>();
    b.step("Every vertex starts as its own set: parent[i] = i, so there are " + n + " sets.", 0, v("sets", sets),
      labelled("parent", toList(parent), range(n), Map.of()), graph("Sets as trees", n, true, links, Map.of(), Map.of(), Map.of()));
    for (var p : pairs) {
      int ra = find(parent, p[0]), rb = find(parent, p[1]);
      b.step("union(" + p[0] + ", " + p[1] + "): follow parents to the roots, " + ra + " and " + rb + ".", 2, v("a", p[0], "b", p[1], "rootA", ra, "rootB", rb),
        labelled("parent", toList(parent), range(n), mark(p[0], "active", p[1], "active", ra, "found", rb, "found")),
        graph("Sets as trees", n, true, links, Map.of(), mark(ra, "found", rb, "found"), Map.of()));
      if (ra == rb) {
        b.step("Same root, so " + p[0] + " and " + p[1] + " are already in one set. Nothing changes.", 3, v("sets", sets),
          labelled("parent", toList(parent), range(n), mark(ra, "found")), graph("Sets as trees", n, true, links, Map.of(), mark(ra, "found"), Map.of()));
        continue;
      }
      if (size[ra] < size[rb]) {
        int t = ra;
        ra = rb;
        rb = t;
      }
      parent[rb] = ra;
      size[ra] += size[rb];
      sets--;
      links.add(new int[] { rb, ra });
      b.step("Hang root " + rb + " under root " + ra + " (the larger set keeps its root). Now " + sets + " sets.", 5, v("sets", sets),
        labelled("parent", toList(parent), range(n), mark(rb, "changed", ra, "found")),
        graph("Sets as trees", n, true, links, Map.of(rb + "-" + ra, "active"), mark(ra, "found", rb, "changed"), Map.of()));
    }
    b.step("All unions done: " + sets + " separate set" + (sets == 1 ? "" : "s") + " remain.", 6, v("sets", sets, "answer", sets),
      labelled("parent", toList(parent), range(n), Map.of()), graph("Sets as trees", n, true, links, Map.of(), Map.of(), Map.of()));
    return b;
  }

  static List<Integer> toList(int[] a) {
    return Arrays.stream(a).boxed().toList();
  }

  static Board topological(String input, int target) {
    int n = vertices(target);
    var edges = tuples(numbers(input, 32, "Up to 16 edges."), 2, n, 16);
    var b = new Board("topological-sort", List.of(
      "count indegree[v] for every edge u → v;",
      "queue every vertex with indegree 0;",
      "while (!queue.isEmpty()) {",
      "  int u = queue.poll(); order.add(u);",
      "  for (int v : out[u]) if (--indegree[v] == 0) queue.add(v);",
      "}",
      "if (order.size() < n) there is a cycle;"
    ));
    int[] in = new int[n];
    for (var e : edges) in[e[1]]++;
    var order = new ArrayList<Integer>();
    var queue = new ArrayDeque<Integer>();
    var done = new LinkedHashMap<Integer, String>();
    b.step("Count incoming edges. A vertex with none has nothing that must come before it.", 0, v("indegree", toList(in)),
      labelled("indegree", toList(in), range(n), Map.of()), graph("Graph", n, true, edges, Map.of(), Map.of(), Map.of()));
    for (int i = 0; i < n; i++) if (in[i] == 0) queue.add(i);
    b.step("Start the queue with every indegree-0 vertex: " + queue + ".", 1, v("queue", List.copyOf(queue)),
      labelled("indegree", toList(in), range(n), Map.of()), stack("Queue (front first)", List.copyOf(queue)), graph("Graph", n, true, edges, Map.of(), Map.of(), Map.of()));
    while (!queue.isEmpty()) {
      int u = queue.poll();
      order.add(u);
      done.put(u, "done");
      var em = new LinkedHashMap<String, String>();
      for (var e : edges) if (e[0] == u) {
        em.put(e[0] + "-" + e[1], "active");
        if (--in[e[1]] == 0) queue.add(e[1]);
      }
      b.step("Take " + u + " and place it next. Remove its outgoing edges; any vertex left with indegree 0 joins the queue.", 4, v("u", u, "order", List.copyOf(order)),
        labelled("indegree", toList(in), range(n), new LinkedHashMap<>(done)), stack("Queue (front first)", List.copyOf(queue)),
        array("Order so far", List.copyOf(order), Map.of()), graph("Graph", n, true, edges, em, new LinkedHashMap<>(done), Map.of()));
    }
    boolean cycle = order.size() < n;
    b.step(cycle ? "Only " + order.size() + " of " + n + " vertices were placed: the rest wait on each other in a cycle, so no order exists."
      : "Every vertex placed: " + order + " respects every edge.", 6, v("answer", cycle ? "cycle" : List.copyOf(order)),
      array("Order", List.copyOf(order), Map.of()), graph("Graph", n, true, edges, Map.of(), new LinkedHashMap<>(done), Map.of()));
    return b;
  }

  static Board kruskal(String input, int target) {
    int n = vertices(target);
    var edges = tuples(numbers(input, 48, "Up to 16 edges."), 3, n, 16);
    if (edges.isEmpty()) throw new IllegalArgumentException("Give at least one weighted edge.");
    var b = new Board("kruskal", List.of(
      "sort edges by weight;",
      "for (Edge e : edges) {",
      "  if (find(e.u) != find(e.v)) { union(e.u, e.v); tree.add(e); total += e.w; }",
      "  // else: e would close a cycle, skip it",
      "}"
    ));
    var sorted = new ArrayList<>(edges);
    sorted.sort(Comparator.comparingInt((int[] e) -> e[2]).thenComparingInt(e -> e[0]).thenComparingInt(e -> e[1]));
    int[] parent = new int[n];
    for (int i = 0; i < n; i++) parent[i] = i;
    var em = new LinkedHashMap<String, String>();
    int total = 0;
    b.step("Sort the edges by weight: the cheapest edges are considered first.", 0, v("edges", sorted.size()),
      array("Edge weights, sorted", sorted.stream().map(e -> e[0] + "–" + e[1] + ": " + e[2]).toList(), Map.of()),
      graph("Graph", n, false, edges, em, Map.of(), Map.of()));
    for (int i = 0; i < sorted.size(); i++) {
      var e = sorted.get(i);
      int ra = find(parent, e[0]), rb = find(parent, e[1]);
      String key = "#" + edges.indexOf(e);
      if (ra != rb) {
        parent[rb] = ra;
        total += e[2];
        em.put(key, "chosen");
        b.step("Edge " + e[0] + "–" + e[1] + " (" + e[2] + ") joins two different trees, so take it. Total " + total + ".", 2, v("edge", e[0] + "-" + e[1], "total", total),
          array("Edge weights, sorted", sorted.stream().map(x -> x[0] + "–" + x[1] + ": " + x[2]).toList(), mark(i, "found")),
          graph("Graph", n, false, edges, new LinkedHashMap<>(em), mark(e[0], "active", e[1], "active"), Map.of()));
      } else {
        em.put(key, "rejected");
        b.step("Edge " + e[0] + "–" + e[1] + " (" + e[2] + ") connects vertices already in one tree; it would make a cycle, so skip it.", 3, v("edge", e[0] + "-" + e[1], "total", total),
          array("Edge weights, sorted", sorted.stream().map(x -> x[0] + "–" + x[1] + ": " + x[2]).toList(), mark(i, "muted")),
          graph("Graph", n, false, edges, new LinkedHashMap<>(em), mark(e[0], "active", e[1], "active"), Map.of()));
      }
    }
    b.step("Every edge considered. The chosen edges form a minimum spanning forest of total weight " + total + ".", 4, v("answer", total),
      graph("Minimum spanning tree", n, false, edges, new LinkedHashMap<>(em), Map.of(), Map.of()));
    return b;
  }

  static Board bellmanFord(String input, int target) {
    int n = vertices(target);
    var edges = tuples(numbers(input, 48, "Up to 16 edges."), 3, n, 16);
    var b = new Board("bellman-ford", List.of(
      "dist[source] = 0; every other dist = ∞;",
      "repeat n - 1 times:",
      "  for (Edge e : edges) if (dist[e.u] + e.w < dist[e.v]) dist[e.v] = dist[e.u] + e.w;",
      "for (Edge e : edges) if (dist[e.u] + e.w < dist[e.v]) negative cycle;"
    ));
    int[] d = new int[n];
    Arrays.fill(d, INF);
    d[0] = 0;
    b.step("Start from vertex 0: its distance is 0, every other distance is unknown (∞).", 0, v("dist", shown(d)),
      labelled("dist", shown(d), range(n), mark(0, "found")), graph("Graph", n, true, edges, Map.of(), mark(0, "found"), labels(d)));
    for (int round = 1; round < n; round++) {
      boolean changed = false;
      for (var e : edges) {
        if (d[e[0]] >= INF / 2) continue;
        if (d[e[0]] + e[2] < d[e[1]]) {
          int before = d[e[1]];
          d[e[1]] = d[e[0]] + e[2];
          changed = true;
          b.step("Round " + round + ": edge " + e[0] + "→" + e[1] + " (" + e[2] + ") improves dist[" + e[1] + "] from " + show(before) + " to " + d[e[1]] + ".", 2,
            v("round", round, "dist", shown(d)), labelled("dist", shown(d), range(n), mark(e[1], "changed", e[0], "active")),
            graph("Graph", n, true, edges, Map.of(e[0] + "-" + e[1], "active"), mark(e[1], "changed"), labels(d)));
        }
      }
      if (!changed) {
        b.step("Round " + round + " changed nothing, so the distances are final already.", 1, v("round", round),
          labelled("dist", shown(d), range(n), Map.of()), graph("Graph", n, true, edges, Map.of(), Map.of(), labels(d)));
        break;
      }
    }
    for (var e : edges) if (d[e[0]] < INF / 2 && d[e[0]] + e[2] < d[e[1]]) {
      b.step("One more pass still improves " + e[0] + "→" + e[1] + ": a negative cycle is reachable, so shortest paths are undefined.", 3, v("answer", "negative cycle"),
        labelled("dist", shown(d), range(n), mark(e[1], "changed")), graph("Graph", n, true, edges, Map.of(e[0] + "-" + e[1], "rejected"), Map.of(), labels(d)));
      return b;
    }
    b.step("A final pass improves nothing, so there is no negative cycle. Shortest distances from 0: " + shown(d) + ".", 3, v("answer", toList(d).stream().map(x -> x >= INF / 2 ? null : x).toList()),
      labelled("dist", shown(d), range(n), Map.of()), graph("Graph", n, true, edges, Map.of(), Map.of(), labels(d)));
    return b;
  }

  static Map<Integer, String> labels(int[] d) {
    var out = new LinkedHashMap<Integer, String>();
    for (int i = 0; i < d.length; i++) out.put(i, show(d[i]));
    return out;
  }

  static Board floyd(String input, int target) {
    int n = vertices(target);
    if (n > 5) throw new IllegalArgumentException("Use up to 5 vertices so the table stays readable.");
    var edges = tuples(numbers(input, 48, "Up to 16 edges."), 3, n, 16);
    var b = new Board("floyd-warshall", List.of(
      "dist[i][j] = weight of i → j, 0 on the diagonal, ∞ otherwise;",
      "for (int k = 0; k < n; k++)",
      "  for (int i = 0; i < n; i++) for (int j = 0; j < n; j++)",
      "    if (dist[i][k] + dist[k][j] < dist[i][j]) dist[i][j] = dist[i][k] + dist[k][j];"
    ));
    int[][] d = new int[n][n];
    for (int i = 0; i < n; i++) {
      Arrays.fill(d[i], INF);
      d[i][i] = 0;
    }
    for (var e : edges) d[e[0]][e[1]] = Math.min(d[e[0]][e[1]], e[2]);
    b.step("Fill the table with direct edges only: 0 on the diagonal, ∞ where there is no edge.", 0, v(),
      table("dist[i][j]", range(n), range(n), cells(d), null, List.of()), graph("Graph", n, true, edges, Map.of(), Map.of(), Map.of()));
    for (int k = 0; k < n; k++) {
      b.step("Now allow paths through vertex " + k + " as a stopover.", 1, v("k", k),
        table("dist[i][j]", range(n), range(n), cells(d), null, List.of()), graph("Graph", n, true, edges, Map.of(), mark(k, "found"), Map.of()));
      for (int i = 0; i < n; i++) for (int j = 0; j < n; j++)
        if (d[i][k] < INF / 2 && d[k][j] < INF / 2 && d[i][k] + d[k][j] < d[i][j]) {
          int before = d[i][j];
          d[i][j] = d[i][k] + d[k][j];
          b.step("Going " + i + "→" + k + "→" + j + " costs " + d[i][k] + " + " + d[k][j] + " = " + d[i][j] + ", better than " + show(before) + ".", 3, v("k", k, "i", i, "j", j),
            table("dist[i][j]", range(n), range(n), cells(d), new int[] { i, j }, List.of(new int[] { i, k }, new int[] { k, j })),
            graph("Graph", n, true, edges, Map.of(), mark(i, "active", k, "found", j, "active"), Map.of()));
        }
    }
    for (int i = 0; i < n; i++) if (d[i][i] < 0) {
      b.step("dist[" + i + "][" + i + "] is " + d[i][i] + ": going round a cycle lowers the cost forever, so there is a negative cycle and shortest paths through it are undefined.", 3,
        v("answer", "negative cycle"), table("dist[i][j]", range(n), range(n), cells(d), new int[] { i, i }, List.of()));
      return b;
    }
    b.step("Every vertex has been tried as a stopover, so each cell holds the shortest distance. dist[0][" + (n - 1) + "] = " + show(d[0][n - 1]) + ".", 3,
      v("answer", d[0][n - 1] >= INF / 2 ? null : d[0][n - 1]), table("dist[i][j]", range(n), range(n), cells(d), new int[] { 0, n - 1 }, List.of()));
    return b;
  }

  static List<List<Object>> cells(int[][] d) {
    var out = new ArrayList<List<Object>>();
    for (int[] row : d) out.add(new ArrayList<>(shown(row)));
    return out;
  }

  // ---- arrays and trees ----

  static Board segmentTree(String input) {
    String[] parts = input.split("\\|");
    var values = numbers(parts[0], 8, "Use up to 8 values.");
    var q = parts.length > 1 ? numbers(parts[1], 2, "Give the query as l,r.") : List.of(0, values.size() - 1);
    int n = values.size();
    if (n == 0 || q.size() != 2 || q.get(0) < 0 || q.get(1) >= n || q.get(0) > q.get(1)) throw new IllegalArgumentException(
      "Give 1 to 8 values, then | and a range l,r inside them."
    );
    var b = new Board("segment-tree", List.of(
      "build(node, lo, hi): leaf stores a[lo]; inner node stores left sum + right sum;",
      "query(node, lo, hi, l, r) {",
      "  if (r < lo || hi < l) return 0;          // no overlap",
      "  if (l <= lo && hi <= r) return tree[node]; // full overlap",
      "  return query(left) + query(right);        // partial: split",
      "}"
    ));
    int size = 1;
    while (size < n) size *= 2;
    int[] tree = new int[2 * size];
    var labels = new ArrayList<Object>();
    for (int i = 0; i < 2 * size; i++) labels.add(i);
    for (int i = 0; i < n; i++) tree[size + i] = values.get(i);
    b.step("Place the values in the leaves (positions " + size + " onwards).", 0, v(), array("Values", values, Map.of()),
      labelled("Tree (node 1 is the root)", toList(tree).subList(1, 2 * size), labels.subList(1, 2 * size), Map.of()));
    for (int i = size - 1; i >= 1; i--) {
      tree[i] = tree[2 * i] + tree[2 * i + 1];
      b.step("Node " + i + " stores the sum of its children " + (2 * i) + " and " + (2 * i + 1) + ": " + tree[i] + ".", 0, v("node", i),
        labelled("Tree (node 1 is the root)", toList(tree).subList(1, 2 * size), labels.subList(1, 2 * size), mark(i - 1, "changed", 2 * i - 1, "active", 2 * i, "active")));
    }
    int l = q.get(0), r = q.get(1);
    var used = new LinkedHashMap<Integer, String>();
    int sum = query(b, tree, size, 1, 0, size - 1, l, r, used, labels);
    b.step("Range [" + l + ", " + r + "] is covered by " + used.size() + " stored node" + (used.size() == 1 ? "" : "s") + ", so the sum is " + sum + ".", 4,
      v("answer", sum), array("Values", values, rangeMarks(l, r)), labelled("Tree (node 1 is the root)", toList(tree).subList(1, 2 * size), labels.subList(1, 2 * size), shift(used)));
    return b;
  }

  static Map<Integer, String> shift(Map<Integer, String> m) {
    var out = new LinkedHashMap<Integer, String>();
    m.forEach((k, v) -> out.put(k - 1, v));
    return out;
  }

  static Map<Integer, String> rangeMarks(int l, int r) {
    var out = new LinkedHashMap<Integer, String>();
    for (int i = l; i <= r; i++) out.put(i, "found");
    return out;
  }

  static int query(Board b, int[] tree, int size, int node, int lo, int hi, int l, int r, Map<Integer, String> used, List<Object> labels) {
    var tv = toList(tree).subList(1, 2 * size);
    var lv = labels.subList(1, 2 * size);
    if (r < lo || hi < l) return 0;
    if (l <= lo && hi <= r) {
      used.put(node, "found");
      b.step("Node " + node + " covers [" + lo + ", " + hi + "], entirely inside the query: use its sum " + tree[node] + " without going deeper.", 3,
        v("node", node, "lo", lo, "hi", hi), labelled("Tree (node 1 is the root)", tv, lv, shift(new LinkedHashMap<>(used))));
      return tree[node];
    }
    var marks = new LinkedHashMap<>(used);
    marks.put(node, "active");
    b.step("Node " + node + " covers [" + lo + ", " + hi + "], only partly inside [" + l + ", " + r + "]: ask both children.", 4,
      v("node", node, "lo", lo, "hi", hi), labelled("Tree (node 1 is the root)", tv, lv, shift(marks)));
    int mid = (lo + hi) / 2;
    return query(b, tree, size, 2 * node, lo, mid, l, r, used, labels) + query(b, tree, size, 2 * node + 1, mid + 1, hi, l, r, used, labels);
  }

  static Board fenwick(String input, int target) {
    var values = numbers(input, 10, "Use up to 10 values.");
    int n = values.size();
    if (n == 0 || target < 0 || target >= n) throw new IllegalArgumentException("Give 1 to 10 values and a prefix end inside them.");
    var b = new Board("fenwick", List.of(
      "void add(int i, int delta) { for (i++; i <= n; i += i & -i) bit[i] += delta; }",
      "int prefix(int i) { int s = 0; for (i++; i > 0; i -= i & -i) s += bit[i]; return s; }"
    ));
    int[] bit = new int[n + 1];
    var labels = range(n + 1);
    b.step("Start with an empty tree. bit[i] will hold the sum of a block of values ending at position i (1-based).", 0, v(),
      array("Values", values, Map.of()), labelled("bit", toList(bit), labels, Map.of()));
    for (int i = 0; i < n; i++) {
      var touched = new LinkedHashMap<Integer, String>();
      for (int j = i + 1; j <= n; j += j & -j) {
        bit[j] += values.get(i);
        touched.put(j, "changed");
      }
      b.step("add(" + i + ", " + values.get(i) + "): update bit at " + touched.keySet() + ", jumping by the lowest set bit each time.", 0, v("i", i),
        array("Values", values, mark(i, "active")), labelled("bit", toList(bit), labels, touched));
    }
    int s = 0;
    var read = new LinkedHashMap<Integer, String>();
    for (int j = target + 1; j > 0; j -= j & -j) {
      s += bit[j];
      read.put(j, "found");
      b.step("prefix(" + target + "): add bit[" + j + "] = " + bit[j] + ", running total " + s + ". Then drop the lowest set bit.", 1, v("j", j, "sum", s),
        array("Values", values, rangeMarks(0, target)), labelled("bit", toList(bit), labels, new LinkedHashMap<>(read)));
    }
    b.step("The sum of values 0.." + target + " is " + s + ", read from only " + read.size() + " cells.", 1, v("answer", s),
      array("Values", values, rangeMarks(0, target)), labelled("bit", toList(bit), labels, read));
    return b;
  }

  static Board intervals(String input) {
    var values = numbers(input, 20, "Use up to 10 intervals.");
    if (values.isEmpty() || values.size() % 2 != 0) throw new IllegalArgumentException("Give start,end pairs.");
    var list = new ArrayList<int[]>();
    for (int i = 0; i < values.size(); i += 2) {
      if (values.get(i) >= values.get(i + 1)) throw new IllegalArgumentException("Each interval must end after it starts.");
      list.add(new int[] { values.get(i), values.get(i + 1) });
    }
    list.sort(Comparator.comparingInt((int[] x) -> x[1]).thenComparingInt(x -> x[0]));
    var names = list.stream().map(x -> "[" + x[0] + ", " + x[1] + ")").toList();
    var b = new Board("interval-scheduling", List.of(
      "sort intervals by end time;",
      "int end = -∞;",
      "for (Interval x : sorted) if (x.start >= end) { take x; end = x.end; }"
    ));
    b.step("Sort by end time. Finishing early leaves the most room for what comes after.", 0, v(), array("Intervals by end", names, Map.of()));
    int end = Integer.MIN_VALUE, count = 0;
    var marks = new LinkedHashMap<Integer, String>();
    for (int i = 0; i < list.size(); i++) {
      var x = list.get(i);
      if (x[0] >= end) {
        end = x[1];
        count++;
        marks.put(i, "found");
        b.step(names.get(i) + " starts at or after the last chosen end, so take it. Chosen: " + count + ".", 2, v("end", end, "count", count),
          array("Intervals by end", names, new LinkedHashMap<>(marks)));
      } else {
        marks.put(i, "muted");
        b.step(names.get(i) + " starts at " + x[0] + ", before the last chosen end " + end + ": it overlaps, skip it.", 2, v("end", end, "count", count),
          array("Intervals by end", names, new LinkedHashMap<>(marks)));
      }
    }
    b.step("At most " + count + " intervals can be chosen without overlap.", 2, v("answer", count), array("Intervals by end", names, marks));
    return b;
  }

  static String binary(int x) {
    String s = Integer.toBinaryString(x & 0xFF);
    return "0".repeat(8 - s.length()) + s;
  }

  static Board bits(String input) {
    var values = numbers(input, 9, "Use up to 9 values.");
    if (values.isEmpty() || values.stream().anyMatch(x -> x < 0 || x > 255)) throw new IllegalArgumentException("Use 1 to 9 values from 0 to 255.");
    var b = new Board("bits", List.of(
      "int x = 0;",
      "for (int v : values) x ^= v; // pairs cancel: a ^ a = 0",
      "while (y != 0) { y &= y - 1; count++; } // clear the lowest set bit"
    ));
    int x = 0;
    var rows = new ArrayList<Object>();
    b.step("XOR every value into x. Equal values cancel out, because a ^ a = 0 and a ^ 0 = a.", 0, v("x", 0), array("x in binary", List.of(binary(0).split("")), Map.of()));
    for (int i = 0; i < values.size(); i++) {
      int before = x;
      x ^= values.get(i);
      rows.add(values.get(i));
      var changed = new LinkedHashMap<Integer, String>();
      for (int k = 0; k < 8; k++) if (((before ^ x) >> (7 - k) & 1) == 1) changed.put(k, "changed");
      b.step(binary(before) + " ^ " + binary(values.get(i)) + " = " + binary(x) + "  (x = " + x + ")", 1, v("value", values.get(i), "x", x),
        array("Values", values, mark(i, "active")), array("x in binary", List.of(binary(x).split("")), changed));
    }
    int y = x, count = 0;
    while (y != 0) {
      int before = y;
      y &= y - 1;
      count++;
      var cleared = new LinkedHashMap<Integer, String>();
      for (int k = 0; k < 8; k++) if (((before ^ y) >> (7 - k) & 1) == 1) cleared.put(k, "muted");
      b.step("y & (y - 1) clears the lowest set bit: " + binary(before) + " → " + binary(y) + ". Set bits counted: " + count + ".", 2, v("y", y, "bits", count),
        array("y in binary", List.of(binary(y).split("")), cleared));
    }
    b.step("If every other value appears exactly twice, the one without a partner is " + x + ". It has " + count + " set bit" + (count == 1 ? "" : "s") + ".", 1, v("answer", x, "bits", count),
      array("x in binary", List.of(binary(x).split("")), Map.of()));
    return b;
  }

  static Board monotonicStack(String input) {
    var a = numbers(input, 12, "Use up to 12 values.");
    if (a.isEmpty()) throw new IllegalArgumentException("Give at least one value.");
    var b = new Board("monotonic-stack", List.of(
      "for (int i = 0; i < n; i++) {",
      "  while (!stack.isEmpty() && a[stack.peek()] < a[i]) next[stack.pop()] = a[i];",
      "  stack.push(i); // indices waiting for something larger",
      "}",
      "anything left on the stack has no greater element: -1"
    ));
    int[] next = new int[a.size()];
    Arrays.fill(next, Integer.MIN_VALUE);
    var stack = new ArrayDeque<Integer>();
    b.step("Walk left to right. The stack keeps indices still waiting for a larger value; their values only decrease from bottom to top.", 0, v(),
      array("Values", a, Map.of()), stack("Stack (bottom first)", List.of()), array("Next greater", answerList(next), Map.of()));
    for (int i = 0; i < a.size(); i++) {
      while (!stack.isEmpty() && a.get(stack.peek()) < a.get(i)) {
        int j = stack.pop();
        next[j] = a.get(i);
        b.step(a.get(i) + " is larger than " + a.get(j) + " at index " + j + ", so " + a.get(i) + " is its next greater element. Pop it.", 1, v("i", i, "popped", j),
          array("Values", a, mark(i, "active", j, "found")), stack("Stack (bottom first)", stackView(stack, a)), array("Next greater", answerList(next), mark(j, "changed")));
      }
      stack.push(i);
      b.step("Push index " + i + " (" + a.get(i) + "); it waits for something larger.", 2, v("i", i),
        array("Values", a, mark(i, "active")), stack("Stack (bottom first)", stackView(stack, a)), array("Next greater", answerList(next), Map.of()));
    }
    for (int j : stack) next[j] = -1;
    b.step("Indices still on the stack never met a larger value, so they get -1. Each index was pushed and popped at most once: O(n).", 4,
      v("answer", toList(next)), array("Values", a, Map.of()), stack("Stack (bottom first)", List.of()), array("Next greater", toList(next), Map.of()));
    return b;
  }

  static List<Object> answerList(int[] next) {
    return Arrays.stream(next).mapToObj(x -> x == Integer.MIN_VALUE ? (Object) "?" : x).toList();
  }

  static List<String> stackView(Deque<Integer> stack, List<Integer> a) {
    var out = new ArrayList<String>();
    stack.descendingIterator().forEachRemaining(i -> out.add(i + ": " + a.get(i)));
    return out;
  }

  static Board monotonicQueue(String input, int k) {
    var a = numbers(input, 12, "Use up to 12 values.");
    if (k < 1 || k > a.size()) throw new IllegalArgumentException("The window size must be between 1 and the number of values.");
    var b = new Board("monotonic-queue", List.of(
      "for (int i = 0; i < n; i++) {",
      "  while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast(); // smaller ones can never win",
      "  dq.addLast(i);",
      "  if (dq.peekFirst() <= i - k) dq.pollFirst(); // left the window",
      "  if (i >= k - 1) max.add(a[dq.peekFirst()]);",
      "}"
    ));
    var dq = new ArrayDeque<Integer>();
    var max = new ArrayList<Integer>();
    b.step("Slide a window of " + k + ". The deque holds indices whose values decrease from front to back, so the front is always the window's maximum.", 0, v("k", k),
      array("Values", a, Map.of()), stack("Deque (front first)", List.of()), array("Window maxima", List.of(), Map.of()));
    for (int i = 0; i < a.size(); i++) {
      while (!dq.isEmpty() && a.get(dq.peekLast()) <= a.get(i)) {
        int j = dq.pollLast();
        b.step(a.get(i) + " arrives, at least as large as " + a.get(j) + " (index " + j + "), which can never be a maximum again. Drop it from the back.", 1, v("i", i, "dropped", j),
          array("Values", a, window(i, k, i, j)), stack("Deque (front first)", queueView(dq, a)), array("Window maxima", List.copyOf(max), Map.of()));
      }
      dq.addLast(i);
      if (dq.peekFirst() <= i - k) {
        int j = dq.pollFirst();
        b.step("Index " + j + " has slid out of the window; remove it from the front.", 3, v("i", i, "expired", j),
          array("Values", a, window(i, k, i, j)), stack("Deque (front first)", queueView(dq, a)), array("Window maxima", List.copyOf(max), Map.of()));
      }
      if (i >= k - 1) {
        max.add(a.get(dq.peekFirst()));
        b.step("Window [" + (i - k + 1) + ", " + i + "]: the front of the deque, " + a.get(dq.peekFirst()) + ", is its maximum.", 4, v("i", i, "max", a.get(dq.peekFirst())),
          array("Values", a, window(i, k, dq.peekFirst(), -1)), stack("Deque (front first)", queueView(dq, a)), array("Window maxima", List.copyOf(max), mark(max.size() - 1, "changed")));
      } else {
        b.step("Add index " + i + " (" + a.get(i) + ") at the back. The window is not full yet.", 2, v("i", i),
          array("Values", a, window(i, k, i, -1)), stack("Deque (front first)", queueView(dq, a)), array("Window maxima", List.copyOf(max), Map.of()));
      }
    }
    b.step("Every window has its maximum, and each index entered and left the deque at most once: O(n).", 5, v("answer", List.copyOf(max)),
      array("Values", a, Map.of()), array("Window maxima", List.copyOf(max), Map.of()));
    return b;
  }

  static Map<Integer, String> window(int i, int k, int active, int other) {
    var out = new LinkedHashMap<Integer, String>();
    for (int j = Math.max(0, i - k + 1); j <= i; j++) out.put(j, "window");
    if (other >= 0) out.put(other, "muted");
    out.put(active, "active");
    return out;
  }

  static List<String> queueView(Deque<Integer> dq, List<Integer> a) {
    return dq.stream().map(i -> i + ": " + a.get(i)).toList();
  }

  // ---- strings ----

  static Board kmp(String words) {
    String[] p = pair(words);
    String text = p[0], pat = p[1];
    var b = new Board("kmp", List.of(
      "lps[i] = length of the longest proper prefix of pat[0..i] that is also its suffix;",
      "for (int i = 0, j = 0; i < text.length(); ) {",
      "  if (text[i] == pat[j]) { i++; j++; if (j == m) return i - m; }",
      "  else if (j > 0) j = lps[j - 1]; // reuse what already matched",
      "  else i++;",
      "}"
    ));
    int m = pat.length();
    int[] lps = new int[m];
    for (int i = 1, len = 0; i < m; ) {
      if (pat.charAt(i) == pat.charAt(len)) lps[i++] = ++len;
      else if (len > 0) len = lps[len - 1];
      else lps[i++] = 0;
    }
    b.step("First the failure table: lps[i] is how much of the pattern can be kept after a mismatch at i + 1.", 0, v("lps", toList(lps)),
      labelled("lps", toList(lps), List.of(pat.split("")), Map.of()), text("Text", text, 0, Map.of()), text("Pattern", pat, 0, Map.of()));
    int i = 0, j = 0;
    while (i < text.length()) {
      if (text.charAt(i) == pat.charAt(j)) {
        b.step("text[" + i + "] = '" + text.charAt(i) + "' matches pattern[" + j + "]. Advance both.", 2, v("i", i, "j", j),
          labelled("lps", toList(lps), List.of(pat.split("")), Map.of()), text("Text", text, 0, matched(i - j, i, "found")), text("Pattern", pat, i - j, matched(0, j, "found")));
        i++;
        j++;
        if (j == m) {
          b.step("All " + m + " characters matched: the pattern starts at index " + (i - m) + ".", 2, v("answer", i - m),
            text("Text", text, 0, matched(i - m, i - 1, "found")), text("Pattern", pat, i - m, matched(0, m - 1, "found")));
          return b;
        }
      } else if (j > 0) {
        b.step("Mismatch at text[" + i + "]. Keep the " + lps[j - 1] + " character" + (lps[j - 1] == 1 ? "" : "s") + " lps says are still matched; slide the pattern without moving i.", 3,
          v("i", i, "j", j, "keep", lps[j - 1]), labelled("lps", toList(lps), List.of(pat.split("")), mark(j - 1, "found")),
          text("Text", text, 0, mark(i, "changed")), text("Pattern", pat, i - j, mark(j, "changed")));
        j = lps[j - 1];
      } else {
        b.step("Mismatch at the pattern's first character: move on to text[" + (i + 1) + "].", 4, v("i", i, "j", j),
          text("Text", text, 0, mark(i, "muted")), text("Pattern", pat, i, mark(0, "muted")));
        i++;
      }
    }
    b.step("The text ran out: the pattern does not occur.", 5, v("answer", -1), text("Text", text, 0, Map.of()));
    return b;
  }

  static Map<Integer, String> matched(int from, int to, String state) {
    var out = new LinkedHashMap<Integer, String>();
    for (int k = from; k <= to; k++) out.put(k, state);
    return out;
  }

  static Board rabinKarp(String words) {
    String[] p = pair(words);
    String text = p[0], pat = p[1];
    int m = pat.length(), base = 31, mod = 101;
    if (m > text.length()) throw new IllegalArgumentException("The pattern must not be longer than the text.");
    var b = new Board("rabin-karp", List.of(
      "hash(s) = (s[0]·31^(m-1) + ... + s[m-1]) mod 101;",
      "h = hash(text[0..m)); target = hash(pat);",
      "for each window: if (h == target && text.substring(i, i + m).equals(pat)) return i;",
      "  h = ((h - text[i]·31^(m-1)) · 31 + text[i + m]) mod 101; // roll in O(1)"
    ));
    int high = 1;
    for (int k = 1; k < m; k++) high = high * base % mod;
    int target = 0, h = 0;
    for (int k = 0; k < m; k++) {
      target = (target * base + pat.charAt(k)) % mod;
      h = (h * base + text.charAt(k)) % mod;
    }
    b.step("Hash the pattern once: " + target + ". Hash the first window of the text the same way: " + h + ".", 1, v("target", target, "hash", h),
      text("Text", text, 0, matched(0, m - 1, "window")), text("Pattern", pat, 0, Map.of()));
    for (int i = 0; i + m <= text.length(); i++) {
      if (h == target) {
        boolean same = text.startsWith(pat, i);
        b.step("Window at " + i + " has hash " + h + ", equal to the pattern's. Check the characters: " + (same ? "a real match." : "a collision, keep going."), 2,
          v("i", i, "hash", h, "target", target), text("Text", text, 0, matched(i, i + m - 1, same ? "found" : "changed")), text("Pattern", pat, i, Map.of()));
        if (same) {
          b.step("The pattern starts at index " + i + ".", 2, v("answer", i), text("Text", text, 0, matched(i, i + m - 1, "found")));
          return b;
        }
      } else {
        b.step("Window at " + i + " has hash " + h + " ≠ " + target + ": no need to compare characters.", 2, v("i", i, "hash", h, "target", target),
          text("Text", text, 0, matched(i, i + m - 1, "window")), text("Pattern", pat, i, Map.of()));
      }
      if (i + m < text.length()) h = Math.floorMod((h - text.charAt(i) * high % mod) * base + text.charAt(i + m), mod);
    }
    b.step("No window matched: the pattern does not occur.", 2, v("answer", -1), text("Text", text, 0, Map.of()));
    return b;
  }

  static Board lcs(String words) {
    String[] p = pair(words);
    String a = p[0], c = p[1];
    if (a.length() > 10) throw new IllegalArgumentException("Keep the first string to 10 characters and the second to 12 so the table fits.");
    var b = new Board("lcs", List.of(
      "dp[i][j] = LCS length of a[0..i) and b[0..j); row 0 and column 0 are 0;",
      "if (a[i-1] == b[j-1]) dp[i][j] = dp[i-1][j-1] + 1;",
      "else dp[i][j] = max(dp[i-1][j], dp[i][j-1]);"
    ));
    int[][] dp = new int[a.length() + 1][c.length() + 1];
    var rows = new ArrayList<Object>(List.of("∅"));
    for (char ch : a.toCharArray()) rows.add(String.valueOf(ch));
    var cols = new ArrayList<Object>(List.of("∅"));
    for (char ch : c.toCharArray()) cols.add(String.valueOf(ch));
    var cells = new ArrayList<List<Object>>();
    for (int i = 0; i <= a.length(); i++) {
      var row = new ArrayList<Object>();
      for (int j = 0; j <= c.length(); j++) row.add(i == 0 || j == 0 ? 0 : null);
      cells.add(row);
    }
    b.step("An empty prefix shares nothing, so the first row and column are 0.", 0, v(), table("dp", rows, cols, cells, null, List.of()));
    for (int i = 1; i <= a.length(); i++) for (int j = 1; j <= c.length(); j++) {
      boolean same = a.charAt(i - 1) == c.charAt(j - 1);
      dp[i][j] = same ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
      cells.get(i).set(j, dp[i][j]);
      b.step(same ? "'" + a.charAt(i - 1) + "' = '" + c.charAt(j - 1) + "': extend the diagonal, " + dp[i - 1][j - 1] + " + 1 = " + dp[i][j] + "."
        : "'" + a.charAt(i - 1) + "' ≠ '" + c.charAt(j - 1) + "': take the better of dropping one character, max(" + dp[i - 1][j] + ", " + dp[i][j - 1] + ") = " + dp[i][j] + ".",
        same ? 1 : 2, v("i", i, "j", j, "value", dp[i][j]),
        table("dp", rows, cols, cells, new int[] { i, j }, same ? List.of(new int[] { i - 1, j - 1 }) : List.of(new int[] { i - 1, j }, new int[] { i, j - 1 })));
    }
    int ans = dp[a.length()][c.length()];
    b.step("The bottom-right cell is the answer: the longest common subsequence has length " + ans + ".", 2, v("answer", ans),
      table("dp", rows, cols, cells, new int[] { a.length(), c.length() }, List.of()));
    return b;
  }

  // ---- tables ----

  static Board knapsack(String input, int capacity) {
    var values = numbers(input, 12, "Use up to 6 items.");
    if (values.isEmpty() || values.size() % 2 != 0 || capacity < 1 || capacity > 12) throw new IllegalArgumentException(
      "Give weight,value pairs (up to 6 items) and a capacity from 1 to 12."
    );
    int n = values.size() / 2;
    var b = new Board("knapsack", List.of(
      "dp[i][c] = best value using the first i items with capacity c;",
      "dp[i][c] = dp[i-1][c];                                  // skip item i",
      "if (w[i] <= c) dp[i][c] = max(dp[i][c], dp[i-1][c - w[i]] + v[i]); // take it"
    ));
    var rows = new ArrayList<Object>(List.of("none"));
    for (int i = 0; i < n; i++) rows.add("w" + values.get(2 * i) + " v" + values.get(2 * i + 1));
    var cols = new ArrayList<Object>(range(capacity + 1));
    int[][] dp = new int[n + 1][capacity + 1];
    var cells = new ArrayList<List<Object>>();
    for (int i = 0; i <= n; i++) {
      var row = new ArrayList<Object>();
      for (int c = 0; c <= capacity; c++) row.add(i == 0 ? 0 : null);
      cells.add(row);
    }
    b.step("With no items the best value is 0 for every capacity.", 0, v(), table("dp[item][capacity]", rows, cols, cells, null, List.of()));
    for (int i = 1; i <= n; i++) {
      int w = values.get(2 * i - 2), val = values.get(2 * i - 1);
      if (w < 1 || val < 0) throw new IllegalArgumentException("Weights must be positive and values not negative.");
      for (int c = 0; c <= capacity; c++) {
        int skip = dp[i - 1][c];
        int take = w <= c ? dp[i - 1][c - w] + val : -1;
        dp[i][c] = Math.max(skip, take);
        cells.get(i).set(c, dp[i][c]);
        if (c == 0 || (w > c && c != w - 1 && c != capacity)) continue; // narrate the informative cells; the rest are copies
        b.step(w > c ? "Capacity " + c + " is too small for weight " + w + ": copy the row above, " + skip + "."
          : "Capacity " + c + ": skip gives " + skip + ", take gives " + dp[i - 1][c - w] + " + " + val + " = " + take + ". Keep " + dp[i][c] + ".",
          w > c ? 1 : 2, v("item", i, "capacity", c, "value", dp[i][c]),
          table("dp[item][capacity]", rows, cols, cells, new int[] { i, c }, w > c ? List.of(new int[] { i - 1, c }) : List.of(new int[] { i - 1, c }, new int[] { i - 1, c - w })));
      }
    }
    b.step("The best value within capacity " + capacity + " is " + dp[n][capacity] + ".", 2, v("answer", dp[n][capacity]),
      table("dp[item][capacity]", rows, cols, cells, new int[] { n, capacity }, List.of()));
    return b;
  }

  static Board matrixChain(String input) {
    var d = numbers(input, 6, "Use up to 6 dimensions (5 matrices).");
    if (d.size() < 3 || d.stream().anyMatch(x -> x < 1 || x > 99)) throw new IllegalArgumentException("Give 3 to 6 dimensions from 1 to 99.");
    int n = d.size() - 1;
    var b = new Board("interval-dp", List.of(
      "cost[i][i] = 0; // one matrix needs no multiplication",
      "for (len = 2..n) for (i = 0; i + len - 1 < n; i++) { j = i + len - 1;",
      "  cost[i][j] = min over k in [i, j) of cost[i][k] + cost[k+1][j] + d[i]·d[k+1]·d[j+1];",
      "}"
    ));
    var labels = new ArrayList<Object>();
    for (int i = 0; i < n; i++) labels.add("M" + i + " (" + d.get(i) + "×" + d.get(i + 1) + ")");
    int[][] cost = new int[n][n];
    var cells = new ArrayList<List<Object>>();
    for (int i = 0; i < n; i++) {
      var row = new ArrayList<Object>();
      for (int j = 0; j < n; j++) row.add(i == j ? 0 : null);
      cells.add(row);
    }
    b.step("A single matrix costs nothing, so the diagonal is 0. Longer intervals build on shorter ones.", 0, v(), table("cost[i][j]", labels, labels, cells, null, List.of()));
    for (int len = 2; len <= n; len++) for (int i = 0; i + len - 1 < n; i++) {
      int j = i + len - 1, best = Integer.MAX_VALUE, bestK = i;
      for (int k = i; k < j; k++) {
        int c = cost[i][k] + cost[k + 1][j] + d.get(i) * d.get(k + 1) * d.get(j + 1);
        if (c < best) {
          best = c;
          bestK = k;
        }
      }
      cost[i][j] = best;
      cells.get(i).set(j, best);
      b.step("M" + i + "..M" + j + ": the best split is after M" + bestK + ", costing " + cost[i][bestK] + " + " + cost[bestK + 1][j] + " + " + d.get(i) + "·" + d.get(bestK + 1) + "·" + d.get(j + 1) + " = " + best + ".", 2,
        v("i", i, "j", j, "split", bestK, "cost", best), table("cost[i][j]", labels, labels, cells, new int[] { i, j }, List.of(new int[] { i, bestK }, new int[] { bestK + 1, j })));
    }
    b.step("The whole chain costs at least " + cost[0][n - 1] + " scalar multiplications with the best bracketing.", 2, v("answer", cost[0][n - 1]),
      table("cost[i][j]", labels, labels, cells, new int[] { 0, n - 1 }, List.of()));
    return b;
  }
}
