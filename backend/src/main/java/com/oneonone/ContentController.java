package com.oneonone;

import com.oneonone.algorithms.Trie;
import java.util.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ContentController {

  final Store store;
  final SearchIndex index;

  public ContentController(Store s, SearchIndex index) {
    store = s;
    this.index = index;
  }

  static Map<String, Object> publicProblem(Map<String, Object> p) {
    var out = new LinkedHashMap<>(p);
    out.remove("tests");
    out.remove("reference");
    out.remove("references");
    return out;
  }

  @GetMapping("/lessons")
  public List<Map<String, Object>> lessons() {
    return store
      .list("lesson", "public")
      .stream()
      .filter(x -> !Boolean.FALSE.equals(x.get("published")))
      .sorted(
        Comparator.comparingInt(x ->
          ((Number) x.getOrDefault("order", 999)).intValue()
        )
      )
      .map(ChallengeService::publicLesson)
      .toList();
  }

  @GetMapping("/lessons/{id}")
  public Map<String, Object> lesson(@PathVariable String id) {
    return lessons()
      .stream()
      .filter(x -> x.get("id").equals(id))
      .findFirst()
      .orElseThrow(() -> new IllegalArgumentException("Lesson not found."));
  }

  @GetMapping("/problems")
  public List<Map<String, Object>> problems() {
    return store
      .list("problem", "public")
      .stream()
      .filter(x -> !Boolean.FALSE.equals(x.get("published")))
      .sorted(
        Comparator.comparingInt(x ->
          ((Number) x.getOrDefault("order", 999)).intValue()
        )
      )
      .map(ContentController::publicProblem)
      .toList();
  }

  @GetMapping("/problems/{id}")
  public Map<String, Object> problem(@PathVariable String id) {
    var p = store.get(id);
    if (
      !p.containsKey("tests") || Boolean.FALSE.equals(p.get("published"))
    ) throw new IllegalArgumentException("Problem not found.");
    return publicProblem(p);
  }

  @GetMapping("/paths")
  public List<Map<String, Object>> paths() {
    return store.list("path", "public");
  }

  @GetMapping("/search")
  public List<Map<String, Object>> search(
    @RequestParam(defaultValue = "") String q
  ) {
    if (q.length() > 100) throw new IllegalArgumentException(
      "Search using at most 100 characters."
    );
    return index.search(q);
  }

  @GetMapping("/problems/{id}/editorial")
  public Map<String, Object> editorial(@PathVariable String id) {
    var p = store.get(id);
    if (
      !p.containsKey("tests") || Boolean.FALSE.equals(p.get("published"))
    ) throw new org.springframework.web.server.ResponseStatusException(
      org.springframework.http.HttpStatus.NOT_FOUND,
      "Problem not found."
    );
    return Map.of(
      "editorial",
      p.get("editorial"),
      "reference",
      p.get("reference"),
      "references",
      p.getOrDefault("references", Map.of("java", p.get("reference")))
    );
  }
}
