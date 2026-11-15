package com.oneonone;

import java.time.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.http.MediaType;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

/** Provider transport. Hosted credentials are never sent in self-hosted mode. */
public final class JudgeClient {

  final RestClient client;
  private volatile boolean reachable;
  private volatile Map<String, Integer> languages = Map.of();
  private final Set<String> verified = ConcurrentHashMap.newKeySet();
  private volatile String checkedAt = "",
    problem = "not_checked";

  JudgeClient(String url, String mode, String token, String key, String host) {
    var factory = new JdkClientHttpRequestFactory(
      java.net.http.HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(3))
        .build()
    );
    factory.setReadTimeout(Duration.ofSeconds(12));
    var builder = RestClient.builder()
      .requestFactory(factory)
      .baseUrl(url.replaceAll("/+$", ""));
    if (mode.equals("rapidapi")) builder
      .defaultHeader("X-RapidAPI-Key", key)
      .defaultHeader("X-RapidAPI-Host", host);
    else builder.defaultHeader("X-Auth-Token", token);
    client = builder.build();
  }

  synchronized Map<String, Integer> discover() {
    return discover(false);
  }

  synchronized Map<String, Integer> discover(boolean refresh) {
    if (!refresh && reachable && !languages.isEmpty()) return languages;
    try {
      var rows = client.get().uri("/languages").retrieve().body(List.class);
      var found = new LinkedHashMap<String, Integer>();
      for (Object item : rows) {
        var row = (Map<?, ?>) item;
        String name = Objects.toString(row.get("name"), "");
        String language = name.matches("Java[ (].*")
          ? "java"
          : name.matches("Python \\(3.*")
            ? "python"
            : name.startsWith("C++")
              ? "cpp"
              : "";
        if (!language.isEmpty()) found.merge(
          language,
          ((Number) row.get("id")).intValue(),
          Math::max
        );
      }
      if (found.size() != 3) throw new IllegalStateException(
        "Required runtimes are missing."
      );
      languages = Map.copyOf(found);
      reachable = true;
      problem = "";
      return languages;
    } catch (Exception e) {
      reachable = false;
      problem = "language_discovery_failed";
      throw e;
    } finally {
      checkedAt = Instant.now().toString();
    }
  }

  int language(String name) {
    return discover().get(name);
  }

  Map<String, Object> create(Map<String, Object> request) {
    return client
      .post()
      .uri("/submissions?base64_encoded=false&wait=false")
      .contentType(MediaType.APPLICATION_JSON)
      .body(request)
      .retrieve()
      .body(Map.class);
  }

  Map<String, Object> poll(String token) {
    if (!token.matches("[a-zA-Z0-9-]{1,100}")) throw new IllegalStateException(
      "Invalid runner receipt."
    );
    return client
      .get()
      .uri("/submissions/" + token + "?base64_encoded=false")
      .retrieve()
      .body(Map.class);
  }

  void executed(String language) {
    verified.add(language);
    problem = "";
    checkedAt = Instant.now().toString();
  }

  void failed(String reason) {
    problem = reason;
    reachable = false;
    checkedAt = Instant.now().toString();
  }

  Map<String, Object> status() {
    return Map.of(
      "reachable",
      reachable,
      "executionVerified",
      reachable && verified.containsAll(List.of("java", "python", "cpp")),
      "verifiedLanguages",
      new TreeSet<>(verified),
      "languages",
      languages,
      "checkedAt",
      checkedAt,
      "reason",
      problem
    );
  }
}
