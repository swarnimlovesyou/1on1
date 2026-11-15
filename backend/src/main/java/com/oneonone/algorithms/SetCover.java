package com.oneonone.algorithms;

import java.util.*;

/** Unit-cost greedy set cover. Never claims exact optimality. */
public final class SetCover {

  public record Candidate(String id, Set<String> topics) {}

  public record Choice(String id, Set<String> adds) {}

  public record Result(List<Choice> selected, Set<String> uncovered) {}

  public Result select(Set<String> goals, List<Candidate> candidates) {
    Set<String> remaining = new TreeSet<>(goals);
    List<Choice> chosen = new ArrayList<>();
    Set<String> used = new HashSet<>();
    while (!remaining.isEmpty()) {
      Candidate best = null;
      Set<String> gain = Set.of();
      for (Candidate c : candidates) {
        if (used.contains(c.id())) continue;
        Set<String> add = new TreeSet<>(c.topics());
        add.retainAll(remaining);
        if (
          add.size() > gain.size() ||
          (add.size() == gain.size() &&
            !add.isEmpty() &&
            (best == null || c.id().compareTo(best.id()) < 0))
        ) {
          best = c;
          gain = add;
        }
      }
      if (best == null) break;
      used.add(best.id());
      chosen.add(new Choice(best.id(), Set.copyOf(gain)));
      remaining.removeAll(gain);
    }
    return new Result(List.copyOf(chosen), Set.copyOf(remaining));
  }
}
