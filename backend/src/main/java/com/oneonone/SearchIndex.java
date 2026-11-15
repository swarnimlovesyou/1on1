package com.oneonone;

import com.oneonone.algorithms.Trie;
import java.util.*;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

@Service
public class SearchIndex {

  private record Snapshot(
    Trie trie,
    Map<String, Map<String, Object>> records
  ) {}

  private final Store store;
  private volatile Snapshot snapshot;

  public SearchIndex(Store store) {
    this.store = store;
  }

  @EventListener(ApplicationReadyEvent.class)
  public synchronized void rebuild() {
    Trie trie = new Trie();
    Map<String, Map<String, Object>> records = new HashMap<>();
    for (String kind : List.of("lesson", "problem"))
      for (var row : store.list(kind, "public")) {
        if (Boolean.FALSE.equals(row.get("published"))) continue;
        String id = row.get("id").toString();
        var publicRow = kind.equals("problem")
          ? ContentController.publicProblem(row)
          : row;
        records.put(id, publicRow);
        trie.insert(row.get("title").toString(), id);
        for (String topic : Store.strings(row.get("topics")))
          trie.insert(topic, id);
        if (row.containsKey("subtitle")) trie.insert(
          row.get("subtitle").toString(),
          id
        );
      }
    snapshot = new Snapshot(trie, Map.copyOf(records));
  }

  public List<Map<String, Object>> search(String prefix) {
    if (snapshot == null) rebuild();
    Snapshot current = snapshot;
    return current.trie
      .search(prefix, 20)
      .stream()
      .map(current.records::get)
      .toList();
  }
}
