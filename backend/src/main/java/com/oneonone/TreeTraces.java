package com.oneonone;

import java.util.*;

/** General binary trees use explicit level-order slots; equal keys have different IDs. */
final class TreeTraces {

  static Map<String, Object> trace(Map<String, Object> body) {
    String input = Store.text(body, "input", "4,2,7,1,3,6");
    String mode = Store.text(body, "words", "inorder")
      .trim()
      .toLowerCase(Locale.ROOT);
    if (mode.equals("tree, trie, try, track") || mode.isBlank()) mode =
      "inorder";
    if (
      !Set.of("inorder", "preorder", "postorder", "levelorder").contains(mode)
    ) throw new IllegalArgumentException(
      "Choose inorder, preorder, postorder or levelorder traversal."
    );
    String[] tokens = input.isBlank()
      ? new String[0]
      : input.trim().split("[,\\s]+");
    if (tokens.length > 31) throw new IllegalArgumentException(
      "Use at most 31 level-order slots, with null for missing children."
    );
    var nodes = new TraceEngine.Node[tokens.length];
    var values = new ArrayList<Integer>();
    for (int i = 0; i < tokens.length; i++) {
      if (tokens[i].equalsIgnoreCase("null")) continue;
      int value;
      try {
        value = Integer.parseInt(tokens[i]);
      } catch (Exception error) {
        throw new IllegalArgumentException("Use integer keys or null slots.");
      }
      if (Math.abs((long) value) > 10000) throw new IllegalArgumentException(
        "Keys must be between -10000 and 10000."
      );
      nodes[i] = new TraceEngine.Node(value);
      nodes[i].id = "node-slot-" + i;
      values.add(value);
      if (
        i > 0 && nodes[(i - 1) / 2] == null
      ) throw new IllegalArgumentException(
        "A non-null node cannot have a null parent slot."
      );
      if (i > 0) {
        if (i % 2 == 1) nodes[(i - 1) / 2].l = nodes[i];
        else nodes[(i - 1) / 2].r = nodes[i];
      }
    }
    var engine = new TraceEngine();
    var r = new TraceEngine.Run("tree", values);
    r.algorithm = "tree-traversal";
    var view = new LinkedHashMap<String, Object>();
    view.put("kind", "tree-traversal");
    view.put("mode", mode);
    view.put("visited", List.of());
    view.put("frames", List.of());
    r.extra.put("visual", view);
    r.extra.put("tree", engine.tree(nodes.length == 0 ? null : nodes[0]));
    r.step(
      "Build the actual binary tree from level-order slots. No BST ordering is assumed.",
      0,
      List.of(),
      Map.of("traversal", mode)
    );
    var output = new ArrayList<Integer>();
    var visited = new ArrayList<String>();
    TraceEngine.Node root = nodes.length == 0 ? null : nodes[0];
    if (mode.equals("levelorder")) {
      var queue = new ArrayDeque<TraceEngine.Node>();
      if (root != null) queue.add(root);
      while (!queue.isEmpty()) {
        var node = queue.remove();
        output.add(node.v);
        visited.add(node.id);
        view.put("current", node.id);
        view.put("visited", visited);
        view.put("output", output);
        if (node.l != null) queue.add(node.l);
        if (node.r != null) queue.add(node.r);
        view.put(
          "frames",
          queue
            .stream()
            .map(n -> n.id)
            .toList()
        );
        r.step(
          "Visit " + node.v + " and enqueue its children for later levels.",
          2,
          List.of(),
          Map.of("visiting", node.v, "output", List.copyOf(output))
        );
      }
    } else walk(r, root, mode, view, new ArrayList<>(), output, visited);
    view.put("current", "");
    view.put("frames", List.of());
    r.step(
      "Traversal complete. Link shape, not sorted order, determined the visits.",
      4,
      List.of(),
      Map.of("output", List.copyOf(output))
    );
    var normalized = new LinkedHashMap<>(body);
    normalized.put("algorithm", "tree-traversal");
    normalized.put("input", input);
    normalized.put("words", mode);
    normalized.putIfAbsent("target", 0);
    normalized.putIfAbsent("seed", 42);
    return Map.of(
      "version",
      2,
      "revision",
      3,
      "algorithm",
      "tree-traversal",
      "family",
      "tree",
      "input",
      normalized,
      "steps",
      r.steps,
      "result",
      r.steps.getLast(),
      "code",
      List.of(
        "visit(node): if null, return;",
        "  recurse left/right according to traversal mode;",
        "  emit node at its preorder/inorder/postorder position;",
        "  finish the remaining child;",
        "return to parent; // levelorder uses a FIFO queue"
      )
    );
  }

  static void walk(
    TraceEngine.Run r,
    TraceEngine.Node node,
    String mode,
    Map<String, Object> view,
    List<String> frames,
    List<Integer> output,
    List<String> visited
  ) {
    if (node == null) return;
    frames.add(node.id);
    view.put("current", node.id);
    view.put("frames", frames);
    r.step(
      "Enter frame for node " + node.v + ".",
      0,
      List.of(),
      Map.of("frame", node.v)
    );
    if (mode.equals("preorder")) emit(r, node, view, output, visited);
    walk(r, node.l, mode, view, frames, output, visited);
    if (mode.equals("inorder")) emit(r, node, view, output, visited);
    walk(r, node.r, mode, view, frames, output, visited);
    if (mode.equals("postorder")) emit(r, node, view, output, visited);
    frames.removeLast();
    view.put("frames", frames);
    view.put("current", frames.isEmpty() ? "" : frames.getLast());
    r.step(
      "Return from node " + node.v + " to its caller.",
      4,
      List.of(),
      Map.of("returned", node.v)
    );
  }

  static void emit(
    TraceEngine.Run r,
    TraceEngine.Node node,
    Map<String, Object> view,
    List<Integer> output,
    List<String> visited
  ) {
    output.add(node.v);
    visited.add(node.id);
    view.put("current", node.id);
    view.put("visited", visited);
    view.put("output", output);
    r.step(
      "Emit " + node.v + " at this traversal's visit position.",
      2,
      List.of(),
      Map.of("visiting", node.v, "output", List.copyOf(output))
    );
  }
}
