package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/** Prep: aptitude, reasoning, puzzles, CS fundamentals and system design guides. Public, read-only, answers stripped. */
@RestController
@RequestMapping("/api/v1/prep")
public class PrepController {

  final Store store;
  private volatile List<Map<String, Object>> tracks;

  public PrepController(Store store) {
    this.store = store;
  }

  List<Map<String, Object>> tracks() {
    if (tracks == null) try (var in = new ClassPathResource("content.json").getInputStream()) {
      tracks = Store.items(store.decode(new String(in.readAllBytes(), StandardCharsets.UTF_8)).get("prepTracks"));
    } catch (java.io.IOException e) {
      throw new IllegalStateException("content.json is missing", e);
    }
    return tracks;
  }

  List<Map<String, Object>> guides() {
    return store.list("guide", "public").stream()
      .filter(g -> !Boolean.FALSE.equals(g.get("published")))
      .sorted(Comparator.comparing((Map<String, Object> g) -> Store.text(g, "track", ""))
        .thenComparing(g -> Store.text(g, "subject", ""))
        .thenComparingInt(g -> ((Number) g.getOrDefault("order", 999)).intValue()))
      .toList();
  }

  @GetMapping
  public Map<String, Object> overview() {
    var guides = guides();
    var listed = guides.stream().map(g -> {
      var row = new LinkedHashMap<String, Object>();
      for (String key : List.of("id", "track", "subject", "title", "order", "summary", "drill")) if (g.containsKey(key)) row.put(key, g.get(key));
      row.put("challengeIds", ChallengeService.authored(g).stream().map(c -> c.get("id")).toList());
      row.put("puzzle", g.containsKey("puzzle"));
      return (Map<String, Object>) row;
    }).toList();
    var trackRows = tracks().stream().map(t -> {
      var row = new LinkedHashMap<String, Object>(t);
      row.put("guides", guides.stream().filter(g -> t.get("id").equals(g.get("track"))).count());
      return (Map<String, Object>) row;
    }).toList();
    return Map.of("tracks", trackRows, "guides", listed);
  }

  @GetMapping("/guides/{id}")
  public Map<String, Object> guide(@PathVariable String id) {
    var guide = store.find(id).filter(g -> id.startsWith("guide-") && !Boolean.FALSE.equals(g.get("published")))
      .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    var out = new LinkedHashMap<>(ChallengeService.publicLesson(guide));
    // a puzzle's answer is checked on the server, never sent ahead
    if (out.get("puzzle") instanceof Map<?, ?> puzzle) {
      var safe = new LinkedHashMap<String, Object>((Map<String, Object>) puzzle);
      safe.put("checkable", safe.remove("answer") != null);
      out.put("puzzle", safe);
    }
    return out;
  }
}
