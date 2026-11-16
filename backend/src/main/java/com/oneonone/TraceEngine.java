package com.oneonone;

import java.util.*;
import org.springframework.stereotype.Service;

/** Deterministic, bounded educational executions. Every step owns its state snapshot. */
@Service
public class TraceEngine {

  public static final Set<String> LEGACY = Set.of(
    "two-pointers",
    "sliding-window",
    "binary-search",
    "merge-sort",
    "quick-sort",
    "linked-list",
    "stack",
    "queue",
    "recursion",
    "backtracking",
    "bst",
    "avl",
    "tree-traversal",
    "heap",
    "bfs",
    "dfs",
    "dijkstra",
    "max-flow",
    "memoization",
    "tabulation",
    "trie",
    "set-cover",
    "quickselect",
    "bloom-filter"
  );
  public static final Set<String> SUPPORTED = java.util.stream.Stream.concat(
    LEGACY.stream(),
    ConceptTraces.SUPPORTED.stream()
  ).collect(java.util.stream.Collectors.toUnmodifiableSet());

  static final class Run {

    String family;
    final List<Map<String, Object>> steps = new ArrayList<>();
    TraceArray a;
    long seed = 42;
    int nextId;
    String algorithm;
    String pending = "initialize";
    Map<String, Object> extra = new LinkedHashMap<>();

    Run(String f, List<Integer> a) {
      family = f;
      this.a = new TraceArray(a, this);
    }

    void setArray(List<Integer> values) {
      a = new TraceArray(values, this);
      pending = "initialize";
    }

    void swap(int i, int j) {
      Collections.swap(a, i, j);
      Collections.swap(a.ids, i, j);
      pending = "swap";
    }

    void step(
      String text,
      int line,
      List<Integer> active,
      Map<String, Object> vars
    ) {
      if (steps.size() >= 4096) throw new IllegalArgumentException(
        "This example exceeds the 4096-step teaching limit. Use a smaller input."
      );
      var s = new LinkedHashMap<String, Object>();
      s.put("id", "step-" + steps.size());
      s.put("array", List.copyOf(a));
      var entities = new ArrayList<Contracts.Entity>();
      var affected = new ArrayList<String>();
      for (int i = 0; i < a.size(); i++) {
        entities.add(
          new Contracts.Entity(
            a.ids.get(i),
            a.get(i),
            i,
            active.contains(i) ? "active" : "idle"
          )
        );
        if (active.contains(i)) affected.add(a.ids.get(i));
      }
      s.put("entities", entities);
      String kind = steps.isEmpty() ? "initialize" : pending;
      if (algorithm.equals("sliding-window")) kind = vars.containsKey("left")
        ? "move-window"
        : "initialize";
      if (family.equals("tree")) kind = vars.containsKey("inserted")
        ? "insert-node"
        : "visit-node";
      if (family.equals("graph")) kind = vars.containsKey("discovered")
        ? "discover-vertex"
        : "visit-vertex";
      if (family.equals("dp")) kind =
        vars.containsKey("i") || vars.containsKey("n")
          ? "write-cell"
          : "read-result";
      if (steps.isEmpty()) kind = "initialize";
      s.put(
        "operation",
        new Contracts.Operation(
          kind,
          List.copyOf(affected),
          new LinkedHashMap<>(vars)
        )
      );
      s.put("active", List.copyOf(active));
      s.put("variables", new LinkedHashMap<>(vars));
      s.put("text", text);
      s.put("line", line);
      for (var entry : extra.entrySet())
        s.put(entry.getKey(), snapshot(entry.getValue()));
      steps.add(s);
      pending = "compare";
    }
  }

  static Object snapshot(Object value) {
    if (value instanceof Map<?, ?> map) {
      var out = new LinkedHashMap<String, Object>();
      map.forEach((k, v) -> out.put(k.toString(), snapshot(v)));
      return out;
    }
    if (value instanceof Collection<?> list) return list
      .stream()
      .map(TraceEngine::snapshot)
      .toList();
    return value;
  }

  /** Values and identities move together; equal values remain distinct objects. */
  static final class TraceArray extends ArrayList<Integer> {

    final List<String> ids = new ArrayList<>();
    final Run owner;

    TraceArray(List<Integer> values, Run owner) {
      super(values);
      this.owner = owner;
      for (int i = 0; i < values.size(); i++) ids.add(identity(i));
    }

    String identity(int position) {
      return Set.of("dp", "graph", "bitset").contains(owner.family)
        ? "cell-" + position
        : "item-" + owner.nextId++;
    }

    @Override
    public boolean add(Integer value) {
      ids.add(identity(size()));
      owner.pending = "insert";
      return super.add(value);
    }

    @Override
    public void add(int index, Integer value) {
      ids.add(index, identity(size()));
      owner.pending = "insert";
      super.add(index, value);
    }

    @Override
    public Integer remove(int index) {
      ids.remove(index);
      owner.pending = "remove";
      return super.remove(index);
    }

    @Override
    public Integer removeLast() {
      return remove(size() - 1);
    }

    @Override
    public Integer removeFirst() {
      return remove(0);
    }

    @Override
    public Integer set(int index, Integer value) {
      owner.pending = "write";
      return super.set(index, value);
    }

    @Override
    public void sort(Comparator<? super Integer> comparator) {
      var order = new ArrayList<Integer>();
      for (int i = 0; i < size(); i++) order.add(i);
      order.sort((a, b) -> comparator.compare(get(a), get(b)));
      var values = new ArrayList<>(this);
      var identities = new ArrayList<>(ids);
      for (int i = 0; i < size(); i++) {
        super.set(i, values.get(order.get(i)));
        ids.set(i, identities.get(order.get(i)));
      }
      owner.pending = "reorder";
    }
  }

  public Map<String, Object> trace(Map<String, Object> b) {
    String alg = Store.text(b, "algorithm", "sliding-window");
    if (ConceptTraces.SUPPORTED.contains(alg)) return ConceptTraces.trace(b);
    if (alg.equals("tree-traversal")) return TreeTraces.trace(b);
    if (!SUPPORTED.contains(alg)) throw new IllegalArgumentException(
      "Choose a supported algorithm from the learning library."
    );
    List<Integer> a = parse(Store.text(b, "input", "2, 1, 5, 1, 3, 2"));
    int target = number(b, "target", 3);
    if (target < -10000 || target > 10000) throw new IllegalArgumentException(
      "Target must be between -10000 and 10000."
    );
    if (
      !Set.of("binary-search", "two-pointers").contains(alg) && target < 0
    ) throw new IllegalArgumentException(
      "This experiment needs a nonnegative target."
    );
    if (
      alg.equals("recursion") && target > 10
    ) throw new IllegalArgumentException(
      "The factorial experiment supports n from 0 to 10."
    );
    if (
      Set.of("memoization", "tabulation").contains(alg) && target > 16
    ) throw new IllegalArgumentException(
      "The table experiment supports n from 0 to 16."
    );
    if (
      alg.equals("quickselect") && (target < 1 || target > a.size())
    ) throw new IllegalArgumentException(
      "Choose k from 1 to the input length."
    );
    if (
      Store.text(b, "words", "").length() > 200
    ) throw new IllegalArgumentException(
      "Use at most 200 characters of words."
    );
    Run r = new Run(family(alg), a);
    r.algorithm = alg;
    try {
      r.seed = Long.parseLong(Store.text(b, "seed", "42"));
    } catch (NumberFormatException error) {
      throw new IllegalArgumentException("Seed must be an integer.");
    }
    if (
      Set.of("stack", "queue", "recursion", "backtracking", "heap").contains(
        alg
      )
    ) r.setArray(List.of());
    if (Set.of("memoization", "tabulation").contains(alg)) {
      r.setArray(new ArrayList<>(Collections.nCopies(target + 1, 0)));
      if (target > 0) r.a.set(1, 1);
    }
    if (alg.equals("trie")) r.extra.put("words", List.of());
    if (alg.equals("bloom-filter")) r.setArray(
      new ArrayList<>(Collections.nCopies(16, 0))
    );
    r.step(
      "Start with the input. Predict what will change first.",
      0,
      List.of(),
      Map.of("size", a.size())
    );
    switch (alg) {
      case "sliding-window" -> {
        int k = target;
        if (k < 1 || k > a.size()) throw new IllegalArgumentException(
          "Window size must be between 1 and the input length."
        );
        int sum = 0,
          best = Integer.MIN_VALUE;
        for (int i = 0; i < a.size(); i++) {
          sum += a.get(i);
          if (i >= k) sum -= a.get(i - k);
          if (i >= k - 1) best = Math.max(best, sum);
          r.step(
            i < k - 1
              ? "Expand the window until it contains " + k + " values."
              : "Add the incoming value and remove the outgoing value. Update the best sum.",
            i < k - 1 ? 1 : 3,
            java.util.stream.IntStream.rangeClosed(Math.max(0, i - k + 1), i)
              .boxed()
              .toList(),
            Map.of(
              "left",
              Math.max(0, i - k + 1),
              "right",
              i,
              "sum",
              sum,
              "best",
              best == Integer.MIN_VALUE ? "—" : best
            )
          );
        }
      }
      case "two-pointers" -> {
        r.a.sort(Integer::compare);
        a = r.a;
        r.step(
          "Prepare sorted input before the linear search phase.",
          0,
          List.of(),
          Map.of("preparation", "sort")
        );
        int l = 0,
          h = a.size() - 1;
        boolean pairFound = false;
        while (l < h) {
          int sum = a.get(l) + a.get(h);
          r.step(
            "Compare the endpoint sum with " + target + ".",
            1,
            List.of(l, h),
            Map.of("left", l, "right", h, "sum", sum, "target", target)
          );
          if (sum == target) {
            pairFound = true;
            r.step(
              "A matching pair is found.",
              2,
              List.of(l, h),
              Map.of("result", a.get(l) + " + " + a.get(h))
            );
            break;
          }
          if (sum < target) l++;
          else h--;
        }
        if (!pairFound) r.step(
          "The pointers meet. No matching pair exists.",
          4,
          List.of(l),
          Map.of("result", "not found", "left", l, "right", h)
        );
      }
      case "binary-search" -> {
        r.a.sort(Integer::compare);
        a = r.a;
        r.step(
          "Prepare sorted input before the linear search phase.",
          0,
          List.of(),
          Map.of("preparation", "sort")
        );
        int lo = 0,
          hi = a.size() - 1;
        boolean found = false;
        while (lo <= hi) {
          int mid = lo + (hi - lo) / 2;
          r.step(
            "Inspect the midpoint and discard the half that cannot contain the target.",
            2,
            List.of(mid),
            Map.of("low", lo, "mid", mid, "high", hi, "target", target)
          );
          if (a.get(mid) == target) {
            found = true;
            r.step(
              "The target is at index " + mid + " in the sorted input.",
              3,
              List.of(mid),
              Map.of("result", mid)
            );
            break;
          }
          if (a.get(mid) < target) lo = mid + 1;
          else hi = mid - 1;
        }
        if (!found) r.step(
          "The search interval is empty; the target is absent.",
          5,
          List.of(),
          Map.of("result", -1, "low", lo, "high", hi)
        );
      }
      case "merge-sort" -> merge(r, 0, a.size() - 1);
      case "quick-sort" -> quick(r, 0, a.size() - 1);
      case "quickselect" -> {
        int k = Math.min(Math.max(target, 1), a.size()) - 1;
        select(r, k);
      }
      case "linked-list" -> {
        int[] next = new int[a.size()];
        for (int i = 0; i < next.length; i++) next[i] =
          i + 1 < next.length ? i + 1 : -1;
        var originalIds = List.copyOf(r.a.ids);
        int previous = -1;
        for (int current = 0; current < a.size(); current++) {
          int following = next[current];
          next[current] = previous;
          var links = new ArrayList<Map<String, Object>>();
          for (int i = 0; i < next.length; i++) links.add(
            Map.of(
              "from",
              originalIds.get(i),
              "to",
              next[i] < 0 ? "" : originalIds.get(next[i])
            )
          );
          r.extra.put("links", links);
          r.extra.put("head", originalIds.get(current));
          r.pending = "rewire-link";
          r.step(
            "Save next, reverse the current link, then advance previous and current.",
            2,
            List.of(current),
            Map.of("current", current, "previous", previous, "next", following)
          );
          previous = current;
        }
        for (int i = 0; i < a.size() / 2; i++) r.swap(i, a.size() - 1 - i);
        r.step(
          "The old tail is now the head; every link points toward the previous node.",
          3,
          List.of(0),
          Map.of("reversed", a.size())
        );
      }
      case "stack", "queue" -> {
        r.setArray(List.of());
        for (int value : a) {
          r.a.add(value);
          r.step(
            alg.equals("stack")
              ? "Push a value onto the top."
              : "Enqueue a value at the back.",
            1,
            List.of(r.a.size() - 1),
            Map.of("size", r.a.size())
          );
        }
        while (!r.a.isEmpty()) {
          int value = r.a.remove(alg.equals("stack") ? r.a.size() - 1 : 0);
          r.step(
            alg.equals("stack")
              ? "Pop the most recently added value."
              : "Dequeue the earliest added value.",
            3,
            List.of(),
            Map.of("removed", value, "size", r.a.size())
          );
        }
      }
      case "recursion" -> {
        int n = Math.min(target, 10);
        r.setArray(List.of());
        long fact = 1;
        for (int i = n; i >= 1; i--) {
          r.a.add(i);
          r.step(
            "Suspend this call while factorial(" + (i - 1) + ") is evaluated.",
            1,
            List.of(r.a.size() - 1),
            Map.of("call", "factorial(" + i + ")")
          );
        }
        r.a.add(0);
        r.step(
          "The base case factorial(0) returns 1.",
          0,
          List.of(r.a.size() - 1),
          Map.of("result", 1)
        );
        r.a.removeLast();
        r.step(
          "Pop the base frame and resume the suspended caller.",
          2,
          List.of(),
          Map.of("returned", 1)
        );
        for (int i = 1; i <= n; i++) {
          fact *= i;
          if (!r.a.isEmpty()) r.a.removeLast();
          r.step(
            "Return " + i + " × the smaller result.",
            3,
            List.of(),
            Map.of("returned", fact)
          );
        }
      }
      case "backtracking" -> {
        a = new ArrayList<>(a.subList(0, Math.min(5, a.size())));
        r.setArray(List.of());
        subsets(r, a, 0);
      }
      case "bst", "avl", "tree-traversal" -> {
        Node root = null;
        for (int v : a) {
          var route = new ArrayList<String>();
          Node cursor = root;
          while (cursor != null) {
            route.add(cursor.id);
            r.extra.put("tree", tree(root));
            r.extra.put(
              "visual",
              Map.of(
                "path",
                List.copyOf(route),
                "scope",
                "Whole tree",
                "key",
                v
              )
            );
            r.step(
              "Compare key " +
                v +
                " with " +
                cursor.v +
                "; choose the ordered subtree.",
              1,
              List.of(),
              Map.of("comparing", cursor.v, "key", v)
            );
            if (v == cursor.v) break;
            cursor = v < cursor.v ? cursor.l : cursor.r;
          }
          root = insertTeaching(root, v, alg.equals("avl"), r);
          r.extra.put("tree", tree(root));
          r.extra.put(
            "visual",
            Map.of("path", List.copyOf(route), "scope", "Whole tree", "key", v)
          );
          r.step(
            alg.equals("avl")
              ? "Insert the key and restore the AVL height invariant."
              : "Insert smaller values to the left and larger values to the right.",
            3,
            List.of(),
            Map.of("inserted", v, "root", root.v, "height", root.h)
          );
        }
        if (alg.equals("tree-traversal")) {
          Queue<Node> q = new ArrayDeque<>();
          q.add(root);
          List<Integer> visited = new ArrayList<>();
          while (!q.isEmpty()) {
            Node n = q.remove();
            visited.add(n.v);
            r.step(
              "Visit this level before moving to its children.",
              3,
              List.of(),
              Map.of("visiting", n.v, "order", List.copyOf(visited))
            );
            if (n.l != null) q.add(n.l);
            if (n.r != null) q.add(n.r);
          }
        }
      }
      case "heap" -> {
        r.setArray(List.of());
        for (int v : a) {
          r.a.add(v);
          int i = r.a.size() - 1;
          while (i > 0) {
            int p = (i - 1) / 2;
            r.extra.put(
              "visual",
              Map.of("parent", p, "child", i, "phase", "compare")
            );
            r.step(
              "Compare inserted value with its parent at index " + p + ".",
              1,
              List.of(p, i),
              Map.of("parent", p, "child", i)
            );
            if (r.a.get(p) >= r.a.get(i)) break;
            r.swap(p, i);
            r.extra.put(
              "visual",
              Map.of("parent", p, "child", i, "phase", "swap")
            );
            r.step(
              "Swap this child upward; only this path can violate heap order.",
              2,
              List.of(p, i),
              Map.of("parent", p, "child", i)
            );
            i = p;
          }
          r.step(
            "Bubble the inserted value upward until the max-heap invariant holds.",
            2,
            List.of(i),
            Map.of("inserted", v, "maximum", r.a.getFirst())
          );
        }
      }
      case "bfs", "dfs", "dijkstra", "max-flow" -> graph(r, alg, target);
      case "memoization", "tabulation" -> {
        int n = Math.min(target, 16);
        r.setArray(new ArrayList<>(Collections.nCopies(n + 1, 0)));
        r.a.set(0, 0);
        if (n > 0) r.a.set(1, 1);
        r.extra.put(
          "visual",
          Map.of(
            "known",
            n == 0 ? List.of(0) : List.of(0, 1),
            "dependencies",
            List.of()
          )
        );
        if (alg.equals("memoization")) fibTeaching(r, n, new ArrayList<>());
        else for (int i = 2; i <= n; i++) {
          r.a.set(i, r.a.get(i - 1) + r.a.get(i - 2));
          r.extra.put(
            "visual",
            Map.of(
              "known",
              java.util.stream.IntStream.rangeClosed(0, i).boxed().toList(),
              "destination",
              i,
              "dependencies",
              List.of(i - 2, i - 1)
            )
          );
          r.step(
            "Reuse the two previously computed states.",
            2,
            List.of(i - 2, i - 1, i),
            Map.of("i", i, "value", r.a.get(i))
          );
        }
        r.step(
          "Read the stored answer. Each state is computed once.",
          4,
          List.of(n),
          Map.of("result", r.a.get(n))
        );
      }
      case "trie" -> {
        String words = Store.text(b, "words", "tree, trie, try, track");
        if (words.length() > 200) throw new IllegalArgumentException(
          "Use at most 200 characters of words."
        );
        List<String> inserted = new ArrayList<>();
        r.setArray(List.of());
        for (String word : words.toLowerCase(Locale.ROOT).split("[,\\s]+")) {
          if (word.isBlank()) continue;
          for (int j = 1; j <= word.length(); j++) {
            var displayWords = new ArrayList<>(inserted);
            displayWords.add(word.substring(0, j));
            r.extra.put(
              "visual",
              Map.of(
                "prefix",
                word.substring(0, j),
                "trieWords",
                displayWords,
                "word",
                word
              )
            );
            r.extra.put("words", List.copyOf(inserted));
            r.step(
              "Follow prefix '" +
                word.substring(0, j) +
                "'; create an edge only if it is missing.",
              1,
              List.of(),
              Map.of("word", word, "prefix", word.substring(0, j))
            );
          }
          inserted.add(word);
          r.extra.put("words", List.copyOf(inserted));
          r.step(
            "Follow existing prefix edges; create missing edges, then mark a word boundary.",
            2,
            List.of(),
            Map.of("inserted", word, "words", inserted.size())
          );
        }
      }
      case "set-cover" -> {
        Set<String> remaining = new LinkedHashSet<>(
          List.of("Arrays", "Hashing", "Trees", "Graphs", "DP")
        );
        String goals = Store.text(b, "words", "");
        if (
          !goals.isBlank() && !goals.equals("tree, trie, try, track")
        ) remaining = new LinkedHashSet<>(
          Arrays.stream(goals.split(","))
            .map(String::trim)
            .filter(x -> !x.isEmpty())
            .toList()
        );
        if (
          remaining.size() > 12 || goals.length() > 200
        ) throw new IllegalArgumentException(
          "Use up to 12 goal topics and 200 characters."
        );
        List<Set<String>> sets = List.of(
          Set.of("Arrays", "Hashing"),
          Set.of("Trees", "Graphs"),
          Set.of("DP", "Arrays"),
          Set.of("Trees")
        );
        r.setArray(List.of());
        r.extra.put("topics", List.copyOf(remaining));
        var universe = List.copyOf(remaining);
        var selected = new ArrayList<Integer>();
        r.extra.put(
          "visual",
          Map.of(
            "universe",
            universe,
            "sets",
            sets
              .stream()
              .map(s -> s.stream().sorted().toList())
              .toList(),
            "selected",
            List.of(),
            "remaining",
            universe,
            "candidate",
            -1,
            "gain",
            List.of()
          )
        );
        r.steps.clear();
        r.step(
          "Requested topics form the goal universe; each candidate covers a subset.",
          0,
          List.of(),
          Map.of("goals", universe.size())
        );
        for (int round = 0; !remaining.isEmpty(); round++) {
          int best = -1;
          Set<String> gain = Set.of();
          for (int i = 0; i < sets.size(); i++) {
            Set<String> g = new TreeSet<>(sets.get(i));
            g.retainAll(remaining);
            r.extra.put(
              "visual",
              Map.of(
                "universe",
                universe,
                "sets",
                sets
                  .stream()
                  .map(s -> s.stream().sorted().toList())
                  .toList(),
                "selected",
                List.copyOf(selected),
                "remaining",
                List.copyOf(remaining),
                "candidate",
                i,
                "gain",
                List.copyOf(g)
              )
            );
            r.step(
              "Candidate " +
                (i + 1) +
                " covers " +
                g.size() +
                " currently uncovered goals.",
              1,
              List.of(),
              Map.of("candidate", i + 1, "new coverage", g.size())
            );
            if (g.size() > gain.size()) {
              best = i;
              gain = g;
            }
          }
          if (best < 0) break;
          r.a.add(best + 1);
          selected.add(best);
          remaining.removeAll(gain);
          r.extra.put(
            "visual",
            Map.of(
              "universe",
              universe,
              "sets",
              sets
                .stream()
                .map(s -> s.stream().sorted().toList())
                .toList(),
              "selected",
              List.copyOf(selected),
              "remaining",
              List.copyOf(remaining),
              "candidate",
              best,
              "gain",
              List.copyOf(gain)
            )
          );
          r.step(
            "Choose the practice problem adding the most uncovered topics.",
            2,
            List.of(r.a.size() - 1),
            Map.of(
              "added",
              String.join(", ", gain),
              "remaining",
              String.join(", ", remaining)
            )
          );
        }
        r.step(
          remaining.isEmpty()
            ? "All requested goals are covered; this greedy result is not a proof of minimum size."
            : "No remaining candidate covers these goals: " +
                String.join(", ", remaining) +
                ".",
          4,
          List.of(),
          Map.of(
            "uncovered",
            List.copyOf(remaining),
            "selected",
            List.copyOf(selected)
          )
        );
      }
      case "bloom-filter" -> {
        r.setArray(new ArrayList<>(Collections.nCopies(16, 0)));
        Set<String> exact = new HashSet<>();
        String[] bloomInput = Store.text(b, "words", "tree, graph, heap").split(
          "\\|",
          -1
        );
        if (
          bloomInput.length > 2 ||
          Arrays.stream(bloomInput).mapToInt(String::length).sum() > 200
        ) throw new IllegalArgumentException(
          "Use insert words | one query word, up to 200 characters."
        );
        for (String word : bloomInput[0].split("[,\\s]+")) {
          if (word.isBlank()) continue;
          int h1 = Math.floorMod(word.hashCode(), 16),
            h2 = Math.floorMod(word.hashCode() * 31 + 7, 16);
          r.a.set(h1, 1);
          r.extra.put(
            "visual",
            Map.of(
              "word",
              word,
              "hashes",
              List.of(h1, h2),
              "phase",
              "first hash"
            )
          );
          r.step(
            "Hash '" +
              word +
              "' to bit " +
              h1 +
              ". Existing one-bits stay set.",
            1,
            List.of(h1),
            Map.of("word", word, "hash", h1)
          );
          r.a.set(h2, 1);
          r.extra.put(
            "visual",
            Map.of(
              "word",
              word,
              "hashes",
              List.of(h1, h2),
              "phase",
              "second hash"
            )
          );
          exact.add(word);
          r.step(
            "Set two hash positions. A hit means possibly present; exact membership still needs verification.",
            2,
            List.of(h1, h2),
            Map.of(
              "word",
              word,
              "first hash",
              h1,
              "second hash",
              h2,
              "exact count",
              exact.size()
            )
          );
        }
        if (bloomInput.length == 2 && !bloomInput[1].isBlank()) {
          String query = bloomInput[1].trim();
          int first = Math.floorMod(query.hashCode(), 16),
            second = Math.floorMod(query.hashCode() * 31 + 7, 16);
          boolean possible = r.a.get(first) == 1 && r.a.get(second) == 1;
          r.extra.put(
            "visual",
            Map.of(
              "word",
              query,
              "hashes",
              List.of(first, second),
              "phase",
              "query",
              "possible",
              possible,
              "exact",
              exact.contains(query)
            )
          );
          r.step(
            possible
              ? "Both query bits are set: possibly present. The exact set confirms " +
                  (exact.contains(query)
                    ? "present."
                    : "absent: this is a false positive.")
              : "A query bit is zero: definitely absent from this filter.",
            3,
            List.of(first, second),
            Map.of(
              "possibly present",
              possible,
              "exact membership",
              exact.contains(query)
            )
          );
        }
      }
    }
    var output = new LinkedHashMap<String, Object>(
      Map.of(
        "version",
        2,
        "algorithm",
        alg,
        "family",
        r.family,
        "steps",
        r.steps,
        "result",
        r.steps.getLast(),
        "input",
        normalizedInput(b, alg, a, target, r.seed)
      )
    );
    output.put("revision", 3);
    TracePresentation.enrich(output);
    return output;
  }

  Map<String, Object> normalizedInput(
    Map<String, Object> body,
    String algorithm,
    List<Integer> values,
    int target,
    long seed
  ) {
    var input = new LinkedHashMap<String, Object>();
    input.put("algorithm", algorithm);
    input.put("input", Store.text(body, "input", "2,1,5,1,3,2"));
    input.put("target", target);
    input.put("seed", seed);
    if (body.containsKey("words")) input.put("words", body.get("words"));
    return input;
  }

  public List<Integer> parse(String input) {
    try {
      List<Integer> a = new ArrayList<>(
        Arrays.stream(input.strip().split("[,\\s]+"))
          .filter(s -> !s.isBlank())
          .map(Integer::valueOf)
          .toList()
      );
      if (
        a.isEmpty() ||
        a.size() > 32 ||
        a.stream().anyMatch(x -> Math.abs((long) x) > 10000)
      ) throw new IllegalArgumentException();
      return a;
    } catch (Exception e) {
      throw new IllegalArgumentException(
        "Enter 1–32 comma-separated integers between -10000 and 10000."
      );
    }
  }

  int number(Map<String, Object> b, String k, int d) {
    try {
      return Integer.parseInt(Store.text(b, k, "" + d));
    } catch (Exception e) {
      throw new IllegalArgumentException("Target must be an integer.");
    }
  }

  String family(String a) {
    return switch (a) {
      case "linked-list" -> "linked";
      case "bloom-filter" -> "bitset";
      case "stack", "queue" -> a;
      case "recursion", "backtracking" -> "recursion";
      case "bst", "avl", "tree-traversal" -> "tree";
      case "heap" -> "heap";
      case "bfs", "dfs", "dijkstra", "max-flow" -> "graph";
      case "memoization", "tabulation" -> "dp";
      case "trie" -> "trie";
      case "set-cover" -> "coverage";
      default -> "array";
    };
  }

  void merge(Run r, int lo, int hi) {
    if (lo >= hi) return;
    int m = (lo + hi) / 2;
    r.extra.put(
      "visual",
      Map.of(
        "range",
        List.of(lo, hi),
        "mid",
        m,
        "buffer",
        List.of(),
        "phase",
        "split"
      )
    );
    r.step(
      "Split this interval into two smaller runs before merging.",
      0,
      List.of(lo, hi),
      Map.of("low", lo, "mid", m, "high", hi)
    );
    merge(r, lo, m);
    merge(r, m + 1, hi);
    List<Integer> out = new ArrayList<>();
    int i = lo,
      j = m + 1;
    List<String> identities = new ArrayList<>();
    while (i <= m || j <= hi) {
      int source = j > hi || (i <= m && r.a.get(i) <= r.a.get(j)) ? i++ : j++;
      out.add(r.a.get(source));
      identities.add(r.a.ids.get(source));
      r.extra.put(
        "visual",
        Map.of(
          "range",
          List.of(lo, hi),
          "mid",
          m,
          "buffer",
          List.copyOf(out),
          "phase",
          "merge",
          "leftCursor",
          i,
          "rightCursor",
          j
        )
      );
      r.step(
        "Copy the smaller unconsumed front into the merge buffer.",
        3,
        List.of(source),
        Map.of("low", lo, "mid", m, "high", hi, "buffer size", out.size())
      );
    }
    for (int k = 0; k < out.size(); k++) {
      r.a.set(lo + k, out.get(k));
      r.a.ids.set(lo + k, identities.get(k));
    }
    r.pending = "merge";
    r.extra.put(
      "visual",
      Map.of(
        "range",
        List.of(lo, hi),
        "mid",
        m,
        "buffer",
        List.copyOf(out),
        "phase",
        "commit"
      )
    );
    r.step(
      "Merge the sorted halves into one ordered interval.",
      3,
      java.util.stream.IntStream.rangeClosed(lo, hi).boxed().toList(),
      Map.of("low", lo, "mid", m, "high", hi)
    );
  }

  void quick(Run r, int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(r, lo, hi);
    quick(r, lo, p - 1);
    quick(r, p + 1, hi);
  }

  int partition(Run r, int lo, int hi) {
    int pivot = r.a.get(hi),
      p = lo;
    for (int j = lo; j < hi; j++) {
      r.step(
        "Compare this value with pivot " + pivot + ".",
        2,
        List.of(j, hi),
        Map.of(
          "pivot",
          pivot,
          "pivotIndex",
          hi,
          "boundary",
          p,
          "scan",
          j,
          "low",
          lo,
          "high",
          hi
        )
      );
      if (r.a.get(j) <= pivot) {
        if (p != j) {
          r.swap(p, j);
          r.step(
            "Move the value into the partition at the boundary.",
            2,
            List.of(p, j),
            Map.of(
              "pivot",
              pivot,
              "pivotIndex",
              hi,
              "boundary",
              p,
              "scan",
              j,
              "low",
              lo,
              "high",
              hi
            )
          );
        }
        p++;
      }
    }
    r.swap(p, hi);
    r.step(
      "Place the pivot in its final sorted position.",
      3,
      List.of(p),
      Map.of("pivot index", p)
    );
    return p;
  }

  void select(Run r, int k) {
    Random random = new Random(r.seed);
    int lo = 0,
      hi = r.a.size() - 1;
    while (lo <= hi) {
      r.swap(lo + random.nextInt(hi - lo + 1), hi);
      int p = partition(r, lo, hi);
      if (p == k) {
        r.step(
          "The pivot is the requested order statistic; the other side needs no sorting.",
          4,
          List.of(p),
          Map.of("k", k + 1, "result", r.a.get(p))
        );
        return;
      }
      if (p < k) lo = p + 1;
      else hi = p - 1;
    }
  }

  void subsets(Run r, List<Integer> a, int i) {
    r.step(
      "Record this subset; explore a choice and then undo it.",
      1,
      List.of(),
      Map.of("depth", i, "subset", List.copyOf(r.a))
    );
    for (int j = i; j < a.size(); j++) {
      r.a.add(a.get(j));
      subsets(r, a, j + 1);
      r.a.removeLast();
      r.step(
        "Undo the last choice and restore the parent path before the next sibling.",
        3,
        List.of(),
        Map.of("depth", i, "subset", List.copyOf(r.a), "removed", a.get(j))
      );
    }
  }

  int fib(Run r, int n) {
    if (n < 2) return n;
    if (r.a.get(n) != 0) return r.a.get(n);
    int x = fib(r, n - 1) + fib(r, n - 2);
    r.a.set(n, x);
    r.step(
      "Memoize this result so repeated calls become lookups.",
      3,
      List.of(n),
      Map.of("n", n, "result", x)
    );
    return x;
  }

  int fibTeaching(Run r, int n, List<Integer> frames) {
    frames.add(n);
    var known = new ArrayList<Integer>();
    for (int i = 0; i < r.a.size(); i++) if (
      i < 2 || r.a.get(i) != 0
    ) known.add(i);
    r.extra.put(
      "visual",
      Map.of(
        "frames",
        List.copyOf(frames),
        "known",
        known,
        "destination",
        n,
        "dependencies",
        n < 2 ? List.of() : List.of(n - 2, n - 1)
      )
    );
    r.step(
      "Enter F(" +
        n +
        "). Check the base cases and cached answer before recursing.",
      0,
      List.of(n),
      Map.of("call", n, "frames", List.copyOf(frames))
    );
    int result;
    if (n < 2) result = n;
    else if (r.a.get(n) != 0) {
      result = r.a.get(n);
      r.step(
        "Cache hit: reuse F(" + n + ") without repeating its descendants.",
        1,
        List.of(n),
        Map.of("cached", n, "value", result)
      );
    } else {
      result = fibTeaching(r, n - 1, frames) + fibTeaching(r, n - 2, frames);
      r.a.set(n, result);
    }
    known = new ArrayList<>();
    for (int i = 0; i < r.a.size(); i++) if (
      i < 2 || r.a.get(i) != 0
    ) known.add(i);
    frames.removeLast();
    r.extra.put(
      "visual",
      Map.of(
        "frames",
        List.copyOf(frames),
        "known",
        known,
        "destination",
        n,
        "dependencies",
        n < 2 ? List.of() : List.of(n - 2, n - 1)
      )
    );
    r.step(
      "Return F(" + n + ") = " + result + " and resume its caller.",
      3,
      List.of(n),
      Map.of("n", n, "result", result)
    );
    return result;
  }

  Node insertTeaching(Node node, int value, boolean avl, Run r) {
    if (node == null) return new Node(value);
    if (value < node.v) node.l = insertTeaching(node.l, value, avl, r);
    else if (value > node.v) node.r = insertTeaching(node.r, value, avl, r);
    else return node;
    update(node);
    if (!avl) return node;
    int balance = height(node.l) - height(node.r);
    if (balance > 1) {
      if (value > node.l.v) node.l = rotateTeaching(node.l, false, r);
      return rotateTeaching(node, true, r);
    }
    if (balance < -1) {
      if (value < node.r.v) node.r = rotateTeaching(node.r, true, r);
      return rotateTeaching(node, false, r);
    }
    return node;
  }

  Node rotateTeaching(Node node, boolean rightRotation, Run r) {
    String name = rightRotation ? "right" : "left";
    r.extra.put("tree", tree(node));
    r.extra.put(
      "visual",
      Map.of(
        "scope",
        "Local AVL subtree · before " + name + " rotation",
        "path",
        List.of(node.id)
      )
    );
    r.step(
      "The balance bound is exceeded here. Rotate this local subtree " +
        name +
        ".",
      2,
      List.of(),
      Map.of("pivot", node.v, "balance", height(node.l) - height(node.r))
    );
    Node root = rightRotation ? right(node) : left(node);
    r.extra.put("tree", tree(root));
    r.extra.put(
      "visual",
      Map.of(
        "scope",
        "Local AVL subtree · after " + name + " rotation",
        "path",
        List.of(root.id, node.id)
      )
    );
    r.pending = "rotate-" + name;
    r.step(
      "Reconnect the middle subtree and update heights. The in-order key order is unchanged.",
      2,
      List.of(),
      Map.of("new local root", root.v)
    );
    return root;
  }

  static class Node {

    int v,
      h = 1;
    Node l, r;
    String id;

    Node(int v) {
      this.v = v;
      this.id = "node-" + v;
    }
  }

  int height(Node n) {
    return n == null ? 0 : n.h;
  }

  void update(Node n) {
    n.h = 1 + Math.max(height(n.l), height(n.r));
  }

  Node right(Node y) {
    Node x = y.l;
    y.l = x.r;
    x.r = y;
    update(y);
    update(x);
    return x;
  }

  Node left(Node x) {
    Node y = x.r;
    x.r = y.l;
    y.l = x;
    update(x);
    update(y);
    return y;
  }

  Node insert(Node n, int v, boolean avl) {
    if (n == null) return new Node(v);
    if (v < n.v) n.l = insert(n.l, v, avl);
    else if (v > n.v) n.r = insert(n.r, v, avl);
    else return n;
    update(n);
    if (avl) {
      int b = height(n.l) - height(n.r);
      if (b > 1) {
        if (v > n.l.v) n.l = left(n.l);
        return right(n);
      }
      if (b < -1) {
        if (v < n.r.v) n.r = right(n.r);
        return left(n);
      }
    }
    return n;
  }

  Object tree(Node n) {
    if (n == null) return null;
    Map<String, Object> m = new LinkedHashMap<>();
    m.put("id", n.id);
    m.put("value", n.v);
    m.put("left", tree(n.l));
    m.put("right", tree(n.r));
    return m;
  }

  void graph(Run r, String alg, int target) {
    int n = Math.min(8, Math.max(3, r.a.size()));
    List<Map<String, Object>> edges = new ArrayList<>();
    int[][] g = new int[n][n];
    for (int i = 0; i < n - 1; i++) {
      g[i][i + 1] = 1 + Math.abs(r.a.get(i % r.a.size()) % 8);
      edges.add(Map.of("from", i, "to", i + 1, "weight", g[i][i + 1]));
      if (i + 2 < n) {
        g[i][i + 2] = 2 + Math.abs(r.a.get(i % r.a.size()) % 5);
        edges.add(Map.of("from", i, "to", i + 2, "weight", g[i][i + 2]));
      }
    }
    r.extra.put("edges", edges);
    r.extra.put("vertexCount", n);
    r.setArray(new ArrayList<>(Collections.nCopies(n, -1)));
    r.steps.clear();
    r.step(
      alg.equals("dfs")
        ? "Start at vertex 0. The call stack will hold the path of vertices whose neighbours are still being explored."
        : "Start at vertex 0. A frontier holds discovered vertices waiting for work.",
      0,
      List.of(0),
      Map.of("visiting", 0, "frontier", List.of(0))
    );
    if (alg.equals("max-flow")) {
      int[][] capacity = new int[n][];
      for (int i = 0; i < n; i++) capacity[i] = g[i].clone();
      int total = 0;
      while (true) {
        int[] p = new int[n];
        Arrays.fill(p, -1);
        p[0] = 0;
        Queue<Integer> q = new ArrayDeque<>();
        q.add(0);
        while (!q.isEmpty() && p[n - 1] < 0) {
          int u = q.remove();
          for (int v = 0; v < n; v++) if (p[v] < 0 && g[u][v] > 0) {
            p[v] = u;
            q.add(v);
          }
        }
        if (p[n - 1] < 0) break;
        int add = Integer.MAX_VALUE;
        for (int v = n - 1; v != 0; v = p[v]) add = Math.min(add, g[p[v]][v]);
        List<Integer> path = new ArrayList<>();
        for (int v = n - 1; v != 0; v = p[v]) {
          g[p[v]][v] -= add;
          g[v][p[v]] += add;
          path.add(v);
        }
        path.add(0);
        Collections.reverse(path);
        total += add;
        r.extra.put("visual", flowView(capacity, g, path, total, List.of()));
        r.step(
          "Augment a residual path and add reverse capacity.",
          3,
          path,
          Map.of("added flow", add, "total flow", total)
        );
      }
      var reachable = new ArrayList<Integer>();
      boolean[] cutSeen = new boolean[n];
      var cutQueue = new ArrayDeque<Integer>();
      cutQueue.add(0);
      cutSeen[0] = true;
      while (!cutQueue.isEmpty()) {
        int u = cutQueue.remove();
        reachable.add(u);
        for (int v = 0; v < n; v++) if (g[u][v] > 0 && !cutSeen[v]) {
          cutSeen[v] = true;
          cutQueue.add(v);
        }
      }
      r.extra.put("visual", flowView(capacity, g, List.of(), total, reachable));
      r.step(
        "No augmenting path remains: maximum flow equals the minimum cut capacity.",
        4,
        List.of(),
        Map.of("maximum flow", total)
      );
      return;
    }
    if (alg.equals("dijkstra")) {
      int[] d = new int[n];
      Arrays.fill(d, 999999);
      d[0] = 0;
      boolean[] used = new boolean[n];
      int[] parent = new int[n];
      Arrays.fill(parent, -1);
      for (int t = 0; t < n; t++) {
        int u = -1;
        for (int i = 0; i < n; i++) if (!used[i] && (u < 0 || d[i] < d[u])) u =
          i;
        if (u < 0 || d[u] == 999999) break;
        used[u] = true;
        for (int v = 0; v < n; v++) if (g[u][v] > 0 && d[u] + g[u][v] < d[v]) {
          int old = d[v];
          d[v] = d[u] + g[u][v];
          parent[v] = u;
          r.extra.put("activeEdge", "edge-" + u + "-" + v);
          r.extra.put(
            "visual",
            Map.of(
              "distances",
              Arrays.stream(d)
                .map(x -> x == 999999 ? -1 : x)
                .boxed()
                .toList(),
              "parents",
              Arrays.stream(parent).boxed().toList(),
              "settled",
              java.util.stream.IntStream.range(0, n)
                .filter(i -> used[i])
                .boxed()
                .toList(),
              "equation",
              d[u] +
                " + " +
                g[u][v] +
                " = " +
                d[v] +
                " (was " +
                (old == 999999 ? "∞" : old) +
                ")"
            )
          );
          r.step(
            "Relax edge " + u + " → " + v + " with a shorter known route.",
            2,
            List.of(u, v),
            Map.of("from", u, "to", v, "distance", d[v])
          );
        }
        r.setArray(
          Arrays.stream(d)
            .map(x -> x == 999999 ? -1 : x)
            .boxed()
            .toList()
        );
        r.extra.put("activeEdge", "");
        r.extra.put(
          "visual",
          Map.of(
            "distances",
            Arrays.stream(d)
              .map(x -> x == 999999 ? -1 : x)
              .boxed()
              .toList(),
            "parents",
            Arrays.stream(parent).boxed().toList(),
            "settled",
            java.util.stream.IntStream.range(0, n)
              .filter(i -> used[i])
              .boxed()
              .toList(),
            "equation",
            "Finalize vertex " + u + " at distance " + d[u]
          )
        );
        r.step(
          "Finalize the nearest unvisited vertex and relax its outgoing edges.",
          2,
          List.of(u),
          Map.of("vertex", u, "distance", d[u])
        );
      }
      return;
    }
    if (alg.equals("dfs")) {
      var seen = new boolean[n];
      var frames = new ArrayList<Integer>();
      int[] count = { 0 };
      depthFirst(r, g, 0, seen, frames, count);
      r.extra.put("activeEdge", "");
      r.step(
        "Return from the source: every reachable vertex was explored.",
        4,
        List.of(),
        Map.of("visited", count[0], "frontier", List.of(), "mode", "dfs")
      );
      return;
    }
    boolean[] seen = new boolean[n];
    int[] distance = new int[n];
    Arrays.fill(distance, -1);
    distance[0] = 0;
    Deque<Integer> q = new ArrayDeque<>();
    q.add(0);
    seen[0] = true;
    int order = 0;
    while (!q.isEmpty()) {
      int u = alg.equals("dfs") ? q.removeLast() : q.removeFirst();
      r.extra.put("activeEdge", "");
      r.a.set(u, order++);
      r.extra.put(
        "visual",
        Map.of("distances", Arrays.stream(distance).boxed().toList())
      );
      r.step(
        alg.equals("dfs")
          ? "Explore the newest pending vertex first."
          : "Explore vertices in discovery order.",
        2,
        List.of(u),
        Map.of("visiting", u, "frontier", List.copyOf(q))
      );
      for (int v = 0; v < n; v++) if (g[u][v] > 0 && !seen[v]) {
        seen[v] = true;
        distance[v] = distance[u] + 1;
        q.addLast(v);
        r.extra.put("activeEdge", "edge-" + u + "-" + v);
        r.extra.put(
          "visual",
          Map.of("distances", Arrays.stream(distance).boxed().toList())
        );
        r.step(
          "Discover vertex " + v + " and add it to the frontier exactly once.",
          3,
          List.of(u, v),
          Map.of("visiting", u, "discovered", v, "frontier", List.copyOf(q))
        );
      }
    }
    r.extra.put("activeEdge", "");
    r.step(
      "Every reachable vertex has been processed.",
      4,
      List.of(),
      Map.of("visited", order, "frontier", List.of())
    );
  }

  void depthFirst(
    Run r,
    int[][] graph,
    int u,
    boolean[] seen,
    List<Integer> frames,
    int[] count
  ) {
    seen[u] = true;
    r.a.set(u, count[0]++);
    frames.add(u);
    r.step(
      "Enter vertex " + u + "; keep its frame while exploring descendants.",
      0,
      List.of(u),
      Map.of("visiting", u, "frontier", List.copyOf(frames), "mode", "dfs")
    );
    for (int v = 0; v < graph.length; v++) if (graph[u][v] > 0 && !seen[v]) {
      r.extra.put("activeEdge", "edge-" + u + "-" + v);
      r.step(
        "Descend to neighbour " +
          v +
          " before trying another neighbour of " +
          u +
          ".",
        2,
        List.of(u, v),
        Map.of(
          "visiting",
          u,
          "discovered",
          v,
          "frontier",
          List.copyOf(frames),
          "mode",
          "dfs"
        )
      );
      depthFirst(r, graph, v, seen, frames, count);
    }
    frames.removeLast();
    r.extra.put("activeEdge", "");
    r.step(
      "Finish vertex " + u + " and return to its parent frame.",
      4,
      List.of(u),
      Map.of("returning", u, "frontier", List.copyOf(frames), "mode", "dfs")
    );
  }

  Map<String, Object> flowView(
    int[][] capacity,
    int[][] residual,
    List<Integer> path,
    int total,
    List<Integer> reachable
  ) {
    var flows = new ArrayList<Map<String, Object>>();
    var reverse = new ArrayList<Map<String, Object>>();
    int cut = 0;
    for (int u = 0; u < capacity.length; u++) for (
      int v = 0;
      v < capacity.length;
      v++
    ) {
      if (capacity[u][v] > 0) {
        flows.add(
          Map.of(
            "from",
            u,
            "to",
            v,
            "capacity",
            capacity[u][v],
            "flow",
            capacity[u][v] - residual[u][v]
          )
        );
        if (reachable.contains(u) && !reachable.contains(v)) cut += capacity[u][
          v
        ];
      } else if (residual[u][v] > 0) reverse.add(
        Map.of("from", u, "to", v, "weight", residual[u][v])
      );
    }
    return Map.of(
      "flowEdges",
      flows,
      "residualEdges",
      reverse,
      "path",
      List.copyOf(path),
      "total",
      total,
      "reachable",
      List.copyOf(reachable),
      "cutCapacity",
      cut
    );
  }
}
