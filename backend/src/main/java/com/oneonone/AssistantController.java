package com.oneonone;

import java.time.Instant;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/**
 * Pairing an external assistant (through the MCP adapter) with one learner. The learner makes a token in Settings;
 * it is shown once and stored only as a hash. The assistant sends it as a bearer token and can read that learner's
 * study context, search their notes and notebook sources, and save a note. Nothing else: no grading, no account
 * changes, no other learner's data. Revoking the pairing stops it at once.
 */
@RestController
@RequestMapping("/api/v1")
public class AssistantController {

  static final int MAX_PAIRINGS = 5;

  final Store store;
  final LearningMapService map;
  final NotebookService notebook; // null in tests

  public AssistantController(Store store, LearningMapService map, NotebookService notebook) {
    this.store = store;
    this.map = map;
    this.notebook = notebook;
  }

  // ---- managed by the signed-in learner ----

  @PostMapping("/pairing")
  public Map<String, Object> create(Authentication a, @RequestBody Map<String, Object> body) {
    return create(AuthController.user(a), body);
  }

  @GetMapping("/pairing")
  public List<Map<String, Object>> list(Authentication a) {
    return list(AuthController.user(a));
  }

  @DeleteMapping("/pairing/{id}")
  public Map<String, Object> revoke(Authentication a, @PathVariable String id) {
    return revoke(AuthController.user(a), id);
  }

  public synchronized Map<String, Object> create(String user, Map<String, Object> body) {
    String label = Store.text(body, "label", "").strip();
    if (label.isEmpty() || label.length() > 60) throw new IllegalArgumentException("Name the assistant or device in up to 60 characters.");
    if (store.list("pairing", user).size() >= MAX_PAIRINGS) throw new IllegalArgumentException("Revoke a pairing before adding another; up to five are allowed.");
    String token = "1on1_" + UUID.randomUUID().toString().replace("-", "") + UUID.randomUUID().toString().replace("-", "");
    String id = "pairing-" + UUID.randomUUID();
    store.put(id, "pairing", user, Map.of("label", label, "tokenHash", AuthController.sha256(token), "createdAt", Instant.now().toString()));
    return Map.of("id", id, "label", label, "token", token);
  }

  public List<Map<String, Object>> list(String user) {
    return store.list("pairing", user).stream()
      .map(p -> {
        var out = new LinkedHashMap<String, Object>();
        out.put("id", p.get("id"));
        out.put("label", p.get("label"));
        out.put("createdAt", p.get("createdAt"));
        out.put("lastUsedAt", p.get("lastUsedAt"));
        return (Map<String, Object>) out;
      })
      .toList();
  }

  public Map<String, Object> revoke(String user, String id) {
    if (!id.startsWith("pairing-") || store.list("pairing", user).stream().noneMatch(p -> id.equals(p.get("id"))))
      throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That pairing doesn't exist.");
    store.delete(id, user);
    return Map.of("ok", true);
  }

  // ---- used by the paired assistant ----

  /** The learner a bearer token belongs to, or 401. Records when it was last used. */
  String owner(String authorization) {
    if (authorization == null || !authorization.startsWith("Bearer 1on1_")) throw unauthorized();
    String hash = AuthController.sha256(authorization.substring("Bearer ".length()).strip());
    // shortcut: a scan of pairing documents; fine for a local install, index the hash if pairings reach thousands
    for (var p : store.all("pairing")) if (hash.equals(p.get("tokenHash"))) {
      String user = store.db.queryForObject("select owner_id from documents where id=?", String.class, p.get("id"));
      var used = new LinkedHashMap<>(p);
      used.remove("id");
      used.put("lastUsedAt", Instant.now().toString());
      store.put(p.get("id").toString(), "pairing", user, used);
      return user;
    }
    throw unauthorized();
  }

  static ResponseStatusException unauthorized() {
    return new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Pair this assistant from 1on1's Settings, then use the token it shows.");
  }

  @GetMapping("/assistant/context")
  public Map<String, Object> context(@RequestHeader(value = "Authorization", required = false) String authorization) {
    String user = owner(authorization);
    var m = map.map(user);
    var out = new LinkedHashMap<String, Object>();
    out.put("name", store.db.queryForObject("select name from members where id=?", String.class, user));
    out.put("nextAction", m.get("nextAction"));
    out.put("reviewsDue", Store.items(m.get("reviewsDue")).stream().map(r -> Map.of("title", r.get("title"), "dueOn", r.get("dueOn"))).limit(10).toList());
    var concepts = Store.items(m.get("concepts"));
    out.put("conceptsByState", concepts.stream().collect(java.util.stream.Collectors.groupingBy(c -> String.valueOf(c.get("state")), TreeMap::new, java.util.stream.Collectors.counting())));
    var study = store.list("study-context", user);
    if (!study.isEmpty()) out.put("lastStudied", study.getLast().get("lessonId"));
    return out;
  }

  @GetMapping("/assistant/notes")
  public List<Map<String, Object>> notes(@RequestHeader(value = "Authorization", required = false) String authorization, @RequestParam(defaultValue = "") String q) {
    String user = owner(authorization);
    String query = q.strip().toLowerCase(Locale.ROOT);
    return store.list("note", user).stream()
      .filter(n -> query.isEmpty() || (n.get("title") + " " + n.get("text")).toLowerCase(Locale.ROOT).contains(query))
      .limit(20)
      .map(n -> Map.<String, Object>of("id", n.get("id"), "title", String.valueOf(n.get("title")), "text", clip(String.valueOf(n.get("text")), 1500), "createdAt", String.valueOf(n.get("createdAt"))))
      .toList();
  }

  @PostMapping("/assistant/notes")
  public Map<String, Object> saveNote(@RequestHeader(value = "Authorization", required = false) String authorization, @RequestBody Map<String, Object> body) {
    String user = owner(authorization);
    String text = Store.text(body, "text", "").strip(), title = Store.text(body, "title", "From your assistant").strip();
    if (text.isEmpty() || text.length() > 20000 || title.length() > 120) throw new IllegalArgumentException("Write a note of up to 20000 characters with a title of up to 120.");
    store.quota(user, "ASSISTANT", 100);
    return store.put("note-" + UUID.randomUUID(), "note", user, Map.of("title", title, "text", text, "lesson", "", "createdAt", Instant.now().toString(), "reviewed", false, "source", "assistant"));
  }

  /** Passages from the learner's own uploaded sources, with source and page for citing. */
  @GetMapping("/assistant/notebook")
  public List<Map<String, Object>> notebook(@RequestHeader(value = "Authorization", required = false) String authorization, @RequestParam String q) {
    String user = owner(authorization);
    if (notebook == null || q.isBlank()) return List.of();
    return notebook.search(user, q.strip(), List.of(), 5).stream()
      .map(p -> Map.<String, Object>of("source", p.title(), "page", p.page(), "text", clip(p.text(), 1200)))
      .toList();
  }

  static String clip(String s, int max) {
    return s.length() <= max ? s : s.substring(0, max) + "…";
  }
}
