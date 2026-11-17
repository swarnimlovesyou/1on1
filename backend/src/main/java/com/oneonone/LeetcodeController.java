package com.oneonone;

import java.time.*;
import java.util.*;
import org.springframework.http.*;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

@RestController
@RequestMapping("/api/v1/connections/leetcode")
public class LeetcodeController {

  final Store s;
  final SheetController sheets;

  public LeetcodeController(Store s, SheetController sheets) {
    this.s = s;
    this.sheets = sheets;
  }

  /** Bank ids for the recent accepted submissions LeetCode returns (at most 20), without duplicates. */
  static List<String> acceptedIds(Map<String, Object> data) {
    var ids = new LinkedHashSet<String>();
    for (var sub : Store.items(data.get("recentAcSubmissionList")))
      if (sub.get("titleSlug") instanceof String slug && !slug.isBlank()) ids.add("lc-" + slug);
    return List.copyOf(ids);
  }

  @GetMapping
  public Map<String, Object> get(Authentication a) {
    return s.find("leetcode-" + AuthController.user(a)).orElse(Map.of());
  }

  @PostMapping
  public Map<String, Object> refresh(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    String u = AuthController.user(a),
      name = Store.text(b, "username", "").strip();
    if (
      !name.matches("[A-Za-z0-9_-]{1,40}")
    ) throw new IllegalArgumentException("Enter a valid LeetCode username.");
    var old = s.find("leetcode-" + u).orElse(Map.of());
    if (
      name.equals(old.get("username")) &&
      old.containsKey("attemptedAt") &&
      Instant.parse(old.get("attemptedAt").toString())
        .plusSeconds(900)
        .isAfter(Instant.now())
    ) throw new IllegalArgumentException(
      "You can refresh this profile every 15 minutes."
    );
    return sync(u, name);
  }

  Map<String, Object> sync(String u, String name) {
    var old = new LinkedHashMap<>(s.find("leetcode-" + u).orElse(Map.of()));
    old.put("username", name);
    old.put("attemptedAt", Instant.now().toString());
    String query =
      "query($username: String!){matchedUser(username:$username){username submitStatsGlobal{acSubmissionNum{difficulty count}} userCalendar{streak totalActiveDays submissionCalendar}} userContestRanking(username:$username){rating attendedContestsCount globalRanking} recentAcSubmissionList(username:$username,limit:20){id title titleSlug timestamp}}";
    try {
      var factory =
        new org.springframework.http.client.JdkClientHttpRequestFactory(
          java.net.http.HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(8))
            .build()
        );
      factory.setReadTimeout(Duration.ofSeconds(12));
      var result = RestClient.builder()
        .requestFactory(factory)
        .build()
        .post()
        .uri("https://leetcode.com/graphql")
        .contentType(MediaType.APPLICATION_JSON)
        .body(Map.of("query", query, "variables", Map.of("username", name)))
        .retrieve()
        .body(Map.class);
      var data = (Map<String, Object>) result.get("data");
      if (
        data == null || data.get("matchedUser") == null
      ) throw new IllegalArgumentException();
      old.put("data", data);
      old.put("syncedAt", Instant.now().toString());
      old.put("status", "synced");
      old.put("sheetTicksAdded", sheets.tickAll(u, acceptedIds(data)));
      old.remove("message");
    } catch (Exception e) {
      old.put("status", "unavailable");
      old.put(
        "message",
        "LeetCode couldn't be reached or this public profile was not found. Cached data is retained; check the username and retry later."
      );
    }
    return s.put("leetcode-" + u, "leetcode", u, old);
  }

  @DeleteMapping
  public Map<String, Object> remove(Authentication a) {
    String u = AuthController.user(a);
    s.delete("leetcode-" + u, u);
    return Map.of("ok", true);
  }

  @Scheduled(fixedDelay = 21600000, initialDelay = 21600000)
  public void scheduled() {
    for (var record : s.all("leetcode")) {
      String id = record.get("id").toString();
      sync(
        id.substring("leetcode-".length()),
        record.get("username").toString()
      );
    }
  }
}
