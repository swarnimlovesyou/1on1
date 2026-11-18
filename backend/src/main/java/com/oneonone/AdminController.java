package com.oneonone;

import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
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

  /**
   * A one-time reset link for a learner, valid 30 minutes, for installs without email: the admin passes it on by
   * hand. Only the token's hash is stored, as for emailed links.
   */
  @PostMapping("/members/reset-link")
  public Map<String, Object> resetLink(@RequestBody Map<String, Object> b) {
    String email = Store.text(b, "email", "").strip().toLowerCase(Locale.ROOT);
    var ids = s.db.queryForList("select id from members where email=?", String.class, email);
    if (ids.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No account uses that email.");
    String token = UUID.randomUUID() + UUID.randomUUID().toString();
    s.db.update("insert into reset_tokens values(?,?,?)", AuthController.sha256(token), ids.getFirst(),
      java.sql.Timestamp.from(java.time.Instant.now().plusSeconds(1800)));
    return Map.of("path", "/reset-password?token=" + token, "expiresInMinutes", 30);
  }

  /** Every learner report, newest first, with who sent it, so spam can be removed. */
  @GetMapping("/reports")
  public List<Map<String, Object>> reports() {
    var out = new ArrayList<Map<String, Object>>();
    for (var r : s.all("report")) {
      var names = s.db.queryForList("select name from members where id=?", String.class, r.get("user"));
      var row = new LinkedHashMap<String, Object>();
      row.put("id", r.get("id"));
      row.put("questionId", r.get("questionId"));
      row.put("company", r.get("company"));
      row.put("stage", r.get("stage"));
      row.put("member", names.isEmpty() ? "Deleted account" : names.getFirst());
      row.put("createdAt", r.get("createdAt"));
      out.add(row);
    }
    out.sort(Comparator.comparing((Map<String, Object> r) -> String.valueOf(r.get("createdAt"))).reversed());
    return out;
  }

  @DeleteMapping("/reports/{id}")
  public Map<String, Object> deleteReport(@PathVariable String id) {
    if (!id.startsWith("report-") || s.find(id).isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That report doesn't exist.");
    s.db.update("delete from documents where id=? and kind='report'", id);
    return Map.of("ok", true);
  }
}
