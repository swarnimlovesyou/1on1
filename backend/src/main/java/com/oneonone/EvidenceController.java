package com.oneonone;

import com.oneonone.algorithms.*;
import java.util.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/evidence")
public class EvidenceController {

  @PostMapping
  public Map<String, Object> benchmark(@RequestBody Map<String, Object> b) {
    String method = Store.text(b, "method", "quickselect");
    if (
      !Set.of("quickselect", "trie", "set-cover").contains(method)
    ) throw new IllegalArgumentException(
      "Choose Quickselect, trie or set cover."
    );
    List<Map<String, Object>> rows = new ArrayList<>();
    for (int n : method.equals("set-cover")
      ? new int[] { 100, 1000, 10000 }
      : new int[] { 1000, 10000, 100000 }) {
      double custom = 0,
        baseline = 0;
      for (int run = -2; run < 5; run++) {
        Random random = new Random(42);
        long start;
        double c, t;
        if (method.equals("quickselect")) {
          int[] data = random.ints(n, 0, 1000000).toArray();
          start = System.nanoTime();
          new Quickselect().select(data, n / 2, 42);
          c = (System.nanoTime() - start) / 1e6;
          start = System.nanoTime();
          int[] copy = data.clone();
          Arrays.sort(copy);
          int ignored = copy[n / 2];
          t = (System.nanoTime() - start) / 1e6;
        } else if (method.equals("trie")) {
          Trie index = new Trie();
          List<String> terms = new ArrayList<>();
          for (int i = 0; i < n; i++) {
            String term = "topic-" + i;
            terms.add(term);
            index.insert(term, term);
          }
          start = System.nanoTime();
          index.search("topic-999", 20);
          c = (System.nanoTime() - start) / 1e6;
          start = System.nanoTime();
          terms
            .stream()
            .filter(x -> x.startsWith("topic-999"))
            .limit(20)
            .toList();
          t = (System.nanoTime() - start) / 1e6;
        } else {
          Set<String> goals = new HashSet<>();
          for (int i = 0; i < 30; i++) goals.add("t" + i);
          List<SetCover.Candidate> cand = new ArrayList<>();
          for (int i = 0; i < n; i++) {
            Set<String> topics = new HashSet<>();
            for (int j = 0; j < 4; j++) topics.add("t" + random.nextInt(30));
            cand.add(new SetCover.Candidate("p" + i, topics));
          }
          start = System.nanoTime();
          var result = new SetCover().select(goals, cand);
          c = (System.nanoTime() - start) / 1e6;
          start = System.nanoTime();
          Set<String> left = new HashSet<>(goals);
          int picked = 0;
          for (var candidate : cand) {
            Set<String> gain = new HashSet<>(candidate.topics());
            gain.retainAll(left);
            if (!gain.isEmpty()) {
              picked++;
              left.removeAll(gain);
            }
            if (left.isEmpty()) break;
          }
          t = (System.nanoTime() - start) / 1e6;
          if (run == 4) rows.add(
            Map.of(
              "size",
              n,
              "selected",
              result.selected().size(),
              "baselineSelected",
              picked,
              "uncovered",
              result.uncovered().size()
            )
          );
        }
        if (run >= 0) {
          custom += c;
          baseline += t;
        }
      }
      Map<String, Object> row = new LinkedHashMap<>();
      row.putAll(
        Map.of("size", n, "algorithmMs", custom / 5, "baselineMs", baseline / 5)
      );
      if (method.equals("set-cover")) {
        var quality = rows.removeLast();
        row.putAll(quality);
      }
      rows.add(row);
    }
    return Map.of(
      "method",
      method,
      "rows",
      rows,
      "seed",
      42,
      "warmups",
      2,
      "repetitions",
      5,
      "java",
      System.getProperty("java.version"),
      "os",
      System.getProperty("os.name"),
      "processors",
      Runtime.getRuntime().availableProcessors(),
      "note",
      "In-process measurements exclude HTTP, database, and network latency. Trie index construction is excluded. Set cover compares quality as well as speed against first-useful selection. Results depend on dataset and hardware."
    );
  }
}
