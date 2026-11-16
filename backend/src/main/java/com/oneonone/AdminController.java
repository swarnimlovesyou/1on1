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

  /** Validation and publication checks without saving, for the editor's preview. */
  @PostMapping("/content/check")
  public Map<String, Object> check(@RequestBody Map<String, Object> b) {
    return ContentChecks.check(b, traces, s::find);
  }

  @PostMapping("/content")
  public Map<String, Object> save(@RequestBody Map<String, Object> b) {
    var checks = check(b);
    var errors = Store.items(checks.get("errors"));
    if (!errors.isEmpty()) throw new IllegalArgumentException(messages("Fix before saving", errors));
    var publication = Store.items(checks.get("publication"));
    if (!Boolean.FALSE.equals(b.get("published")) && !publication.isEmpty()) throw new IllegalArgumentException(
      messages("Not ready to publish; save it as a draft (\"published\": false) or fix", publication)
    );
    b.put("edited", true);
    var result = s.put(Store.text(b, "id", ""), Store.text(b, "kind", ""), "public", b);
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

  static String messages(String lead, List<Map<String, Object>> items) {
    var parts = items.stream().limit(5).map(i -> i.get("field") + ": " + i.get("message")).toList();
    return lead + ": " + String.join(" ", parts) + (items.size() > 5 ? " (+" + (items.size() - 5) + " more)" : "");
  }
}
