package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import java.util.regex.Pattern;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/**
 * Learners' own "I was asked this" reports: fresh company data that 1on1 owns, labelled as learner-reported and kept
 * apart from the 2022 community dataset. One report per learner, question and company.
 */
@RestController
@RequestMapping("/api/v1/reports")
public class ReportController {

  static final Pattern COMPANY = Pattern.compile("[A-Za-z0-9][A-Za-z0-9 .&'-]{1,39}");
  static final Set<String> STAGES = Set.of("OA", "Interview");

  final Store store;
  final BankService bank;

  public ReportController(Store store, BankService bank) {
    this.store = store;
    this.bank = bank;
  }

  @PostMapping
  public Map<String, Object> post(Authentication auth, @RequestBody Map<String, Object> body) {
    return report(AuthController.user(auth), body);
  }

  @GetMapping("/recent")
  public List<Map<String, Object>> recent() {
    var groups = new LinkedHashMap<String, List<Map<String, Object>>>();
    for (var r : store.all("report")) groups.computeIfAbsent(r.get("questionId") + "|" + r.get("companyKey"), k -> new ArrayList<>()).add(r);
    return groups.values().stream()
      .map(rows -> {
        rows.sort(Comparator.comparing((Map<String, Object> r) -> r.get("createdAt").toString()).reversed());
        var latest = rows.getFirst();
        var question = question(latest.get("questionId").toString()).orElse(null);
        if (question == null) return null;
        var out = new LinkedHashMap<String, Object>();
        out.put("questionId", latest.get("questionId"));
        out.put("title", question.get("title"));
        out.put("url", question.get("url"));
        out.put("source", question.get("source"));
        out.put("company", latest.get("company"));
        out.put("stage", latest.get("stage"));
        out.put("month", latest.get("createdAt").toString().substring(0, 7));
        out.put("reports", (int) rows.stream().map(r -> r.get("user")).distinct().count());
        out.put("latest", latest.get("createdAt"));
        return (Map<String, Object>) out;
      })
      .filter(Objects::nonNull)
      .sorted(Comparator.comparing((Map<String, Object> r) -> r.get("latest").toString()).reversed())
      .limit(8)
      .map(r -> {
        r.remove("latest");
        return r;
      })
      .toList();
  }

  Optional<Map<String, Object>> question(String id) {
    return bank.external(id).or(() -> bank.own().stream().filter(p -> id.equals(p.get("id"))).findFirst());
  }

  Map<String, Object> report(String user, Map<String, Object> body) {
    String id = String.valueOf(body.get("questionId"));
    if (question(id).isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That question isn't in the bank.");
    String company = String.valueOf(body.getOrDefault("company", "")).strip();
    if (!COMPANY.matcher(company).matches())
      throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Enter the company's name (2 to 40 letters, digits, spaces or . & ' -).");
    String stage = String.valueOf(body.get("stage"));
    if (!STAGES.contains(stage)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Say whether it was an online assessment or an interview.");
    String key = company.toLowerCase(Locale.ROOT);
    String docId = "report-" + UUID.nameUUIDFromBytes((user + "|" + id + "|" + key).getBytes(StandardCharsets.UTF_8));
    var existing = store.find(docId);
    if (existing.isPresent()) return Map.of("saved", true, "repeat", true);
    store.put(docId, "report", user, Map.of(
      "questionId", id, "company", company, "companyKey", key, "stage", stage, "user", user, "createdAt", Instant.now().toString()
    ));
    return Map.of("saved", true, "repeat", false);
  }
}
