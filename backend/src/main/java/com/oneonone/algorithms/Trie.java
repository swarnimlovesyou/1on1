package com.oneonone.algorithms;

import java.util.*;

/** Prefix index. Each posting is unique; enumeration is lexicographic and bounded. */
public final class Trie {

  private static final class Node {

    final NavigableMap<Character, Node> children = new TreeMap<>();
    final Set<String> ids = new TreeSet<>();
  }

  private final Node root = new Node();

  private static String normalized(String s) {
    return Objects.requireNonNull(s, "Text is required")
      .strip()
      .toLowerCase(Locale.ROOT);
  }

  public void insert(String term, String id) {
    Node n = root;
    for (char c : normalized(term).toCharArray())
      n = n.children.computeIfAbsent(c, k -> new Node());
    n.ids.add(Objects.requireNonNull(id));
  }

  public List<String> search(String prefix, int limit) {
    if (limit < 0 || limit > 100) throw new IllegalArgumentException(
      "Limit must be between 0 and 100"
    );
    Node n = root;
    for (char c : normalized(prefix).toCharArray()) {
      n = n.children.get(c);
      if (n == null) return List.of();
    }
    Set<String> seen = new LinkedHashSet<>();
    visit(n, limit, seen);
    return List.copyOf(seen);
  }

  private void visit(Node n, int limit, Set<String> out) {
    if (out.size() >= limit) return;
    for (String id : n.ids) {
      out.add(id);
      if (out.size() >= limit) return;
    }
    for (Node child : n.children.values()) {
      visit(child, limit, out);
      if (out.size() >= limit) return;
    }
  }
}
