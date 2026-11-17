package com.oneonone;

import java.time.Duration;
import java.time.Instant;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

/**
 * Timed mock online assessments over 1on1's own judged problems. The server owns the window; the score is read from
 * official ACCEPTED submissions made inside it, so a mock never writes credit. Integrity signals are client-reported
 * counts, not proctoring.
 */
@org.springframework.stereotype.Service
public class MockService {

  static final List<String> LEVELS = List.of("Easy", "Medium", "Hard");
  final Store s;
  final BankService bank;
  final Random random = new Random();

  public MockService(Store s, BankService bank) {
    this.s = s;
    this.bank = bank;
  }

  /** Splits `size` across difficulties in proportion to `mix`, by largest remainder; zero shares are left out. */
  static Map<String, Integer> allocate(Map<String, Long> mix, int size) {
    long total = mix.values().stream().mapToLong(Long::longValue).sum();
    Map<String, Integer> out = new LinkedHashMap<>();
    if (total == 0) return out;
    Map<String, Double> remainder = new HashMap<>();
    int given = 0;
    for (String level : LEVELS) {
      double exact = mix.getOrDefault(level, 0L) * (double) size / total;
      out.put(level, (int) Math.floor(exact));
      remainder.put(level, exact - Math.floor(exact));
      given += (int) Math.floor(exact);
    }
    var byRemainder = new ArrayList<>(LEVELS);
    byRemainder.sort(Comparator.comparingDouble((String l) -> remainder.get(l)).reversed());
    for (int i = 0; given < size; i++, given++) out.merge(byRemainder.get(i % 3), 1, Integer::sum);
    out.values().removeIf(v -> v == 0);
    return out;
  }

  static List<String> nearest(String level) {
    return switch (level) {
      case "Easy" -> List.of("Easy", "Medium", "Hard");
      case "Hard" -> List.of("Hard", "Medium", "Easy");
      default -> List.of("Medium", "Easy", "Hard");
    };
  }

  public Map<String, Object> start(String user, int size, int minutes, String style) {
    if (size != 2 && size != 3) throw new IllegalArgumentException("Choose 2 or 3 problems.");
    if (minutes != 60 && minutes != 90) throw new IllegalArgumentException("Choose 60 or 90 minutes.");
    String chosenStyle = style == null || style.isBlank() ? "mixed" : style.strip();
    Map<String, Integer> plan;
    if (chosenStyle.equals("mixed")) plan = size == 3 ? Map.of("Easy", 1, "Medium", 1, "Hard", 1) : Map.of("Easy", 1, "Medium", 1);
    else {
      if (bank.companies().stream().noneMatch(c -> chosenStyle.equals(c.get("name")))) throw new IllegalArgumentException("Choose a company from the list.");
      plan = allocate(bank.difficultyMix(chosenStyle), size);
      if (plan.isEmpty()) plan = Map.of("Medium", size);
    }
    Map<String, List<String>> pool = new HashMap<>();
    for (var p : s.list("problem", "public")) if (!Boolean.FALSE.equals(p.get("published")))
      pool.computeIfAbsent(Store.text(p, "difficulty", "Medium"), k -> new ArrayList<>()).add(p.get("id").toString());
    pool.values().forEach(list -> Collections.shuffle(list, random));
    List<String> picked = new ArrayList<>();
    for (String level : LEVELS) for (int i = 0; i < plan.getOrDefault(level, 0); i++)
      // a difficulty that runs out borrows from its nearest neighbour, so the mock always has `size` problems
      for (String from : nearest(level)) {
        var list = pool.getOrDefault(from, new ArrayList<>());
        if (!list.isEmpty()) {
          picked.add(list.removeFirst());
          break;
        }
      }
    if (picked.size() != size) throw new IllegalStateException("Not enough published problems for a mock.");
    Instant now = Instant.now();
    String id = "mock-" + UUID.randomUUID();
    var doc = new LinkedHashMap<String, Object>();
    doc.put("problems", picked);
    doc.put("style", chosenStyle);
    doc.put("minutes", minutes);
    doc.put("startedAt", now.toString());
    doc.put("deadline", now.plus(Duration.ofMinutes(minutes)).toString());
    doc.put("signals", Map.of("tabSwitches", 0, "fullscreenExits", 0));
    s.put(id, "mock", user, doc);
    return view(user, id);
  }

  boolean finished(Map<String, Object> doc, Instant now) {
    return doc.get("finishedAt") != null || !now.isBefore(Instant.parse(doc.get("deadline").toString()));
  }

  public Map<String, Object> view(String user, String id) {
    var doc = s.owned(id, user);
    Instant now = Instant.now(), start = Instant.parse(doc.get("startedAt").toString()), deadline = Instant.parse(doc.get("deadline").toString());
    Instant end = doc.get("finishedAt") == null ? deadline : Instant.parse(doc.get("finishedAt").toString());
    if (end.isAfter(deadline)) end = deadline;
    Map<String, Instant> acceptedAt = new HashMap<>();
    for (var sub : s.list("submission", user)) {
      if (!Boolean.TRUE.equals(sub.get("official")) || !"ACCEPTED".equals(sub.get("status"))) continue;
      Instant at = Instant.parse(Store.text(sub, "createdAt", "1970-01-01T00:00:00Z"));
      if (at.isBefore(start) || at.isAfter(end)) continue;
      acceptedAt.merge(Store.text(sub, "problem", ""), at, (a, b) -> a.isBefore(b) ? a : b);
    }
    var problems = new ArrayList<Map<String, Object>>();
    for (String pid : Store.strings(doc.get("problems"))) {
      var p = s.find(pid).orElse(Map.of());
      var row = new LinkedHashMap<String, Object>();
      row.put("id", pid);
      row.put("title", Store.text(p, "title", pid));
      row.put("difficulty", Store.text(p, "difficulty", ""));
      row.put("accepted", acceptedAt.containsKey(pid));
      if (acceptedAt.containsKey(pid)) row.put("acceptedAt", acceptedAt.get(pid).toString());
      problems.add(row);
    }
    boolean done = finished(doc, now);
    var out = new LinkedHashMap<String, Object>();
    out.put("id", id);
    out.put("style", doc.get("style"));
    out.put("minutes", doc.get("minutes"));
    out.put("problems", problems);
    out.put("startedAt", doc.get("startedAt"));
    out.put("deadline", doc.get("deadline"));
    out.put("finishedAt", doc.get("finishedAt"));
    out.put("finished", done);
    out.put("remainingSeconds", done ? 0 : Duration.between(now, deadline).toSeconds());
    out.put("score", acceptedAt.size());
    out.put("signals", doc.get("signals"));
    return out;
  }

  public Map<String, Object> finish(String user, String id) {
    var doc = new LinkedHashMap<>(s.owned(id, user));
    if (doc.get("finishedAt") == null) {
      Instant now = Instant.now(), deadline = Instant.parse(doc.get("deadline").toString());
      doc.put("finishedAt", (now.isAfter(deadline) ? deadline : now).toString());
      s.put(id, "mock", user, doc);
    }
    return view(user, id);
  }

  public Map<String, Object> signal(String user, String id, String kind) {
    String key = switch (kind) {
      case "tab" -> "tabSwitches";
      case "fullscreen" -> "fullscreenExits";
      default -> throw new IllegalArgumentException("Report tab or fullscreen.");
    };
    var doc = new LinkedHashMap<>(s.owned(id, user));
    if (!finished(doc, Instant.now())) {
      var signals = new LinkedHashMap<String, Object>((Map<String, Object>) doc.get("signals"));
      signals.merge(key, 1, (a, b) -> ((Number) a).intValue() + 1);
      doc.put("signals", signals);
      s.put(id, "mock", user, doc);
    }
    return view(user, id);
  }

  public List<Map<String, Object>> list(String user) {
    return s.list("mock", user).stream()
      .sorted(Comparator.comparing((Map<String, Object> d) -> Instant.parse(d.get("startedAt").toString())).reversed())
      .map(d -> view(user, d.get("id").toString()))
      .toList();
  }
}
