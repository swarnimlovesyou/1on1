package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import com.oneonone.algorithms.*;
import java.util.*;
import org.junit.jupiter.api.Test;

class AlgorithmsTest {

  @Test
  void trieEmptyAndMissing() {
    Trie t = new Trie();
    assertTrue(t.search("", 10).isEmpty());
    t.insert("tree", "1");
    assertTrue(t.search("graph", 10).isEmpty());
  }

  @Test
  void trieNormalization() {
    Trie t = new Trie();
    t.insert("  Trees", "1");
    assertEquals(List.of("1"), t.search(" TrE ", 10));
  }

  @Test
  void triePrefixAndLimit() {
    Trie t = new Trie();
    t.insert("trie", "1");
    t.insert("tree", "2");
    t.insert("graph", "3");
    assertEquals(List.of("2", "1"), t.search("tr", 10));
    assertEquals(1, t.search("tr", 1).size());
    assertTrue(t.search("tr", 0).isEmpty());
  }

  @Test
  void trieUniquePostings() {
    Trie t = new Trie();
    t.insert("tree", "1");
    t.insert("trees", "1");
    t.insert("tree", "1");
    assertEquals(List.of("1"), t.search("tr", 10));
  }

  @Test
  void trieInvalidLimits() {
    Trie t = new Trie();
    assertThrows(IllegalArgumentException.class, () -> t.search("a", -1));
    assertThrows(IllegalArgumentException.class, () -> t.search("a", 101));
  }

  @Test
  void coverEmptyGoals() {
    assertTrue(new SetCover().select(Set.of(), List.of()).selected().isEmpty());
  }

  @Test
  void coverImpossible() {
    var r = new SetCover().select(
      Set.of("a", "b"),
      List.of(new SetCover.Candidate("1", Set.of("a")))
    );
    assertEquals(Set.of("b"), r.uncovered());
  }

  @Test
  void coverTiesAndNoReuse() {
    var r = new SetCover().select(
      Set.of("a", "b"),
      List.of(
        new SetCover.Candidate("z", Set.of("a", "b")),
        new SetCover.Candidate("a", Set.of("a", "b"))
      )
    );
    assertEquals("a", r.selected().getFirst().id());
    assertEquals(1, r.selected().size());
  }

  @Test
  void coverGainsAreNew() {
    var r = new SetCover().select(
      Set.of("a", "b", "c"),
      List.of(
        new SetCover.Candidate("1", Set.of("a", "b")),
        new SetCover.Candidate("2", Set.of("b", "c"))
      )
    );
    assertEquals(Set.of("a", "b"), r.selected().getFirst().adds());
    assertEquals(Set.of("c"), r.selected().getLast().adds());
    assertTrue(r.uncovered().isEmpty());
  }

  @Test
  void coverAgainstExhaustiveSmallCases() {
    Random random = new Random(42);
    for (int trial = 0; trial < 100; trial++) {
      Set<String> goals = Set.of("a", "b", "c", "d");
      List<SetCover.Candidate> c = new ArrayList<>();
      for (int i = 0; i < 7; i++) {
        Set<String> tags = new HashSet<>();
        for (String g : goals) if (random.nextBoolean()) tags.add(g);
        c.add(new SetCover.Candidate("" + i, tags));
      }
      int optimum = 99;
      for (int mask = 0; mask < 1 << c.size(); mask++) {
        Set<String> covered = new HashSet<>();
        for (int j = 0; j < c.size(); j++) if (
          (mask & (1 << j)) != 0
        ) covered.addAll(c.get(j).topics());
        if (covered.containsAll(goals)) optimum = Math.min(
          optimum,
          Integer.bitCount(mask)
        );
      }
      var greedy = new SetCover().select(goals, c);
      if (optimum < 99) {
        assertTrue(greedy.uncovered().isEmpty());
        assertTrue(greedy.selected().size() >= optimum);
        assertTrue(
          greedy.selected().size() <=
            Math.ceil(optimum * (1 + .5 + 1.0 / 3 + .25))
        );
      }
    }
  }

  @Test
  void selectBoundary() {
    assertEquals(7, new Quickselect().select(new int[] { 7 }, 0, 42));
  }

  @Test
  void selectInvalid() {
    assertThrows(IllegalArgumentException.class, () ->
      new Quickselect().select(new int[] {}, 0, 1)
    );
    assertThrows(IllegalArgumentException.class, () ->
      new Quickselect().select(new int[] { 1 }, 1, 1)
    );
    assertThrows(IllegalArgumentException.class, () ->
      new Quickselect().select(new int[] { 1 }, -1, 1)
    );
  }

  @Test
  void selectDuplicates() {
    assertEquals(4, new Quickselect().select(new int[] { 4, 4, 4, 4 }, 2, 42));
  }

  @Test
  void selectOrderedAndNegative() {
    assertEquals(
      -2,
      new Quickselect().select(new int[] { -3, -2, -1, 0 }, 1, 2)
    );
    assertEquals(2, new Quickselect().select(new int[] { 4, 3, 2, 1 }, 1, 2));
  }

  @Test
  void selectMatchesSortingAndPreservesInput() {
    Random r = new Random(42);
    for (int n = 1; n < 100; n++) {
      int[] a = r.ints(n, -20, 21).toArray(),
        original = a.clone(),
        sorted = a.clone();
      Arrays.sort(sorted);
      for (int k = 0; k < n; k++) assertEquals(
        sorted[k],
        new Quickselect().select(a, k, k)
      );
      assertArrayEquals(original, a);
    }
  }

  @Test
  void quartilesUseNearestRank() {
    assertEquals(
      Map.of("q1", 1, "median", 2, "q3", 3),
      new Quickselect().quartiles(new int[] { 4, 3, 2, 1 }, 42)
    );
  }
}
