package com.oneonone;

import java.util.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/admin")
public class AdminController {

  final Store s;
  final TraceEngine traces;
  final SearchIndex index;

  public AdminController(Store s, TraceEngine t, SearchIndex index) {
    this.s = s;
    traces = t;
    this.index = index;
  }

  @GetMapping("/content")
  public Map<String, Object> list() {
    return Map.of(
      "lessons",
      s.list("lesson", "public"),
      "problems",
      s.list("problem", "public"),
      "paths",
      s.list("path", "public"),
      "usage",
      s.db.queryForList(
        "select usage_day,kind,sum(count) as total from daily_usage group by usage_day,kind order by usage_day desc"
      )
    );
  }

  @PostMapping("/content")
  public Map<String, Object> save(@RequestBody Map<String, Object> b) {
    String kind = Store.text(b, "kind", ""),
      id = Store.text(b, "id", "");
    if (
      !Set.of("lesson", "problem", "path").contains(kind) ||
      !id.matches(kind + "-[a-z0-9-]{1,80}")
    ) throw new IllegalArgumentException(
      "Choose a lesson, problem or path with a matching stable identifier."
    );
    if (
      Store.text(b, "title", "").isBlank()
    ) throw new IllegalArgumentException("A title is required.");
    if (kind.equals("lesson")) {
      if (
        Store.text(b, "body", "").isBlank() || !b.containsKey("checkpoint")
      ) throw new IllegalArgumentException(
        "Lessons require body text and a checkpoint."
      );
      traces.trace((Map<String, Object>) b.get("experiment"));
    }
    if (kind.equals("problem")) {
      if (
        Store.items(b.get("tests")).size() < 5 ||
        Store.items(b.get("tests")).size() > 20 ||
        Store.text(b, "editorial", "").isBlank() ||
        Store.text(b, "reference", "").isBlank()
      ) throw new IllegalArgumentException(
        "Problems need 5–20 tests, an editorial and a reference solution."
      );
    }
    b.put("edited", true);
    var result = s.put(id, kind, "public", b);
    index.rebuild();
    return result;
  }

  @PostMapping("/import")
  public Map<String, Object> importData(
    @RequestBody List<Map<String, Object>> rows
  ) {
    if (rows.size() > 100) throw new IllegalArgumentException(
      "Import at most 100 records at once."
    );
    List<String> ids = new ArrayList<>();
    for (var row : rows) ids.add(save(row).get("id").toString());
    return Map.of("imported", ids);
  }
}
