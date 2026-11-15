package com.oneonone;

import jakarta.annotation.PreDestroy;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/** Durable, bounded jobs. One Java process owns the local execution queue. */
@Service
public class ExecutionService {

  final Store s;
  final ProgressService progress;

  @Value("${app.judge-url}")
  String url;

  @Value("${app.judge-key}")
  String key = "";

  @Value("${app.judge-host}")
  String host = "";

  @Value("${app.judge-mode:self-hosted}")
  String mode = "self-hosted";

  @Value("${app.judge-auth-token:}")
  String token = "";

  final ExecutorService jobs = new ThreadPoolExecutor(
    2,
    2,
    0,
    TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(20),
    new ThreadPoolExecutor.AbortPolicy()
  );
  final Set<String> active = ConcurrentHashMap.newKeySet();
  private volatile boolean stopping;
  private JudgeClient transport;
  private String transportConfig = "";

  public ExecutionService(Store s, ProgressService progress) {
    this.s = s;
    this.progress = progress;
  }

  public boolean available() {
    return (
      url != null &&
      !url.isBlank() &&
      (mode.equals("rapidapi")
        ? !key.isBlank() && !host.isBlank()
        : mode.equals("self-hosted") && !token.isBlank())
    );
  }

  synchronized JudgeClient judge() {
    String config = url + mode + token + key + host;
    if (transport == null || !config.equals(transportConfig)) {
      transport = new JudgeClient(url, mode, token, key, host);
      transportConfig = config;
    }
    return transport;
  }

  public Map<String, Object> status() {
    var out = new LinkedHashMap<String, Object>();
    out.put("configured", available());
    out.put("mode", mode);
    out.putAll(
      available()
        ? judge().status()
        : Map.of(
            "reachable",
            false,
            "executionVerified",
            false,
            "verifiedLanguages",
            List.of(),
            "reason",
            "not_configured"
          )
    );
    return out;
  }

  public Map<String, Object> probe() {
    if (available()) {
      try {
        judge().discover(true);
      } catch (Exception ignored) {}
    }
    return status();
  }

  public static Map<String, Object> visible(Map<String, Object> data) {
    var out = new LinkedHashMap<String, Object>();
    for (String name : List.of(
      "id",
      "problem",
      "code",
      "language",
      "official",
      "input",
      "status",
      "createdAt",
      "finishedAt",
      "message",
      "results",
      "requestId"
    ))
      if (data.containsKey(name)) out.put(name, data.get(name));
    return out;
  }

  public synchronized Map<String, Object> submit(
    String user,
    Map<String, Object> body
  ) {
    if (!available()) throw new ResponseStatusException(
      HttpStatus.SERVICE_UNAVAILABLE,
      "Configure the local Judge0 token or explicit hosted mode. Your saved draft remains available."
    );
    String problem = Store.text(body, "problem", ""),
      language = Store.text(body, "language", "java"),
      code = Store.text(body, "code", ""),
      input = Store.text(body, "input", "");
    if (
      !Set.of("java", "python", "cpp").contains(language) ||
      code.isBlank() ||
      code.length() > 50000 ||
      input.length() > 10000
    ) throw new IllegalArgumentException(
      "Choose a supported language, code under 50000 characters, and input under 10000 characters."
    );
    var content = s.owned(problem, "public");
    if (
      !content.containsKey("tests") ||
      Boolean.FALSE.equals(content.get("published"))
    ) throw new IllegalArgumentException(
      "Choose a published practice problem."
    );
    String requestId = Store.text(
      body,
      "requestId",
      UUID.randomUUID().toString()
    );
    if (
      !requestId.matches("[A-Za-z0-9_-]{8,128}")
    ) throw new IllegalArgumentException(
      "Supply a valid submission request identifier."
    );
    boolean official = !Boolean.FALSE.equals(body.get("official"));
    for (var old : s.list("submission", user))
      if (requestId.equals(old.get("requestId"))) {
        if (
          !Objects.equals(problem, old.get("problem")) ||
          !Objects.equals(code, old.get("code")) ||
          !Objects.equals(language, old.get("language")) ||
          !Objects.equals(official, old.get("official")) ||
          !Objects.equals(input, old.get("input"))
        ) throw new ResponseStatusException(
          HttpStatus.CONFLICT,
          "This request identifier belongs to another submission."
        );
        return visible(old);
      }
    s.quota(user, "execution", 50);
    String id = "submission-" + UUID.randomUUID();
    var data = new LinkedHashMap<String, Object>();
    data.put("problem", problem);
    data.put("language", language);
    data.put("code", code);
    data.put("input", input);
    data.put("official", official);
    data.put("requestId", requestId);
    data.put("status", "QUEUED");
    data.put("createdAt", Instant.now().toString());
    data.put("deadlineAt", Instant.now().plusSeconds(300).toString());
    data.put("results", List.of());
    data.put("tokens", Map.of());
    data.put("dispatching", -1);
    data.put(
      "fixtures",
      official
        ? content.get("tests")
        : List.of(Map.of("input", input, "output", "", "public", true))
    );
    s.put(id, "submission", user, data);
    schedule(user, id, false);
    return visible(s.get(id));
  }

  private void schedule(String user, String id, boolean recovery) {
    if (!active.add(id)) return;
    try {
      jobs.submit(() -> {
        try {
          run(user, id, recovery);
        } finally {
          active.remove(id);
        }
      });
    } catch (RejectedExecutionException error) {
      active.remove(id);
      var data = new LinkedHashMap<>(s.get(id));
      data.put("status", "UNAVAILABLE");
      data.put(
        "message",
        "The execution queue is full. Your submission was saved."
      );
      s.put(id, "submission", user, data);
    }
  }

  @EventListener(ApplicationReadyEvent.class)
  public void recover() {
    for (var row : s.db.queryForList(
      "select owner_id,body from documents where kind='submission'"
    )) {
      var data = s.decode(row.get("body").toString());
      if (Set.of("QUEUED", "RUNNING").contains(data.get("status"))) schedule(
        row.get("owner_id").toString(),
        data.get("id").toString(),
        true
      );
    }
  }

  void run(String user, String id, boolean recovery) {
    var data = new LinkedHashMap<>(s.get(id));
    var results = new ArrayList<>(Store.items(data.get("results")));
    var tokens = new LinkedHashMap<String, Object>(
      (Map<String, Object>) data.getOrDefault("tokens", Map.of())
    );
    try {
      if (
        !data.containsKey("fixtures") || !data.containsKey("deadlineAt")
      ) throw new InterruptedJob(
        "This older job has no durable execution snapshot. Submit it again."
      );
      Instant deadline = Instant.parse(data.get("deadlineAt").toString());
      if (Instant.now().isAfter(deadline)) throw new InterruptedJob(
        "This saved execution expired. Submit it again."
      );
      data.put("status", "RUNNING");
      data.remove("message");
      s.put(id, "submission", user, data);
      String language = data.get("language").toString();
      boolean official = Boolean.TRUE.equals(data.get("official"));
      var fixtures = Store.items(data.get("fixtures"));
      if (fixtures.isEmpty()) throw new IllegalStateException(
        "No grading fixtures."
      );
      int languageId = judge().language(language);
      for (int index = results.size(); index < fixtures.size(); index++) {
        if (Instant.now().isAfter(deadline)) throw new InterruptedJob(
          "The execution deadline was reached. Your submission is saved."
        );
        var fixture = fixtures.get(index);
        String receipt = Objects.toString(tokens.get("" + index), "");
        if (receipt.isBlank()) {
          if (
            recovery &&
            ((Number) data.getOrDefault("dispatching", -1)).intValue() == index
          ) throw new InterruptedJob(
            "The app stopped before the runner receipt was saved. It will not duplicate an uncertain execution; submit again."
          );
          data.put("dispatching", index);
          s.put(id, "submission", user, data);
          var request = new LinkedHashMap<String, Object>();
          request.put("source_code", data.get("code"));
          request.put("language_id", languageId);
          request.put("stdin", fixture.get("input"));
          request.put("cpu_time_limit", language.equals("java") ? 5 : 2);
          request.put("wall_time_limit", 10);
          request.put(
            "memory_limit",
            language.equals("java") ? 512000 : 256000
          );
          request.put("max_file_size", 128);
          request.put("enable_network", false);
          receipt = Objects.toString(judge().create(request).get("token"), "");
          if (receipt.isBlank()) throw new IllegalStateException(
            "No runner receipt."
          );
          tokens.put("" + index, receipt);
          data.put("tokens", tokens);
          data.put("dispatching", -1);
          s.put(id, "submission", user, data);
        }
        var result = waitFor(receipt, deadline);
        int status = (
          (Number) ((Map<?, ?>) result.get("status")).get("id")
        ).intValue();
        if (status == 13 || status == 14) throw new IllegalStateException(
          "Runner infrastructure failed."
        );
        String actual = Objects.toString(result.get("stdout"), ""),
          expected = Objects.toString(fixture.get("output"), "");
        boolean passed =
          status == 3 &&
          (!official || normalize(actual).equals(normalize(expected)));
        String verdict = passed
          ? "PASSED"
          : status == 3
            ? "WRONG_ANSWER"
            : status == 6
              ? "COMPILATION_ERROR"
              : status == 5
                ? "TIME_LIMIT"
                : "RUNTIME_ERROR";
        if (status == 3) judge().executed(language);
        boolean isPublic = Boolean.TRUE.equals(fixture.get("public"));
        var row = new LinkedHashMap<String, Object>();
        row.put("index", index + 1);
        row.put("status", verdict);
        row.put("public", isPublic);
        row.put("time", Objects.toString(result.get("time"), ""));
        row.put("memory", Objects.toString(result.get("memory"), ""));
        if (isPublic) {
          row.put("input", fixture.get("input"));
          row.put("actual", bounded(actual));
          if (official) row.put("expected", expected);
        }
        if (status == 6) row.put(
          "message",
          bounded(
            Objects.toString(
              result.get("compile_output"),
              "Compilation failed."
            )
          )
        );
        if (!official && status != 3 && status != 6) row.put(
          "message",
          bounded(
            Objects.toString(
              result.get("stderr"),
              "The program did not finish normally."
            )
          )
        );
        results.add(row);
        data.put("results", results);
        s.put(id, "submission", user, data);
        if (status == 6) break;
      }
      String outcome = results
        .stream()
        .map(row -> row.get("status").toString())
        .filter(value -> !value.equals("PASSED"))
        .findFirst()
        .orElse(official ? "ACCEPTED" : "FINISHED");
      data.put("status", outcome);
      if (official && outcome.equals("ACCEPTED")) progress.accepted(
        user,
        data.get("problem").toString(),
        id
      );
      data.put("finishedAt", Instant.now().toString());
    } catch (InterruptedException error) {
      Thread.currentThread().interrupt();
      data.put("status", "QUEUED");
      data.put("message", "Execution will resume on the next backend start.");
    } catch (InterruptedJob error) {
      data.put("status", "INTERRUPTED");
      data.put("message", error.getMessage());
    } catch (Exception error) {
      if (stopping || Thread.currentThread().isInterrupted()) {
        data.put("status", "QUEUED");
        data.put("message", "Execution will resume on the next backend start.");
      } else {
        data.put("status", "UNAVAILABLE");
        data.put(
          "message",
          "The local runner could not finish. Your submission is saved. Check runner readiness before retrying."
        );
        judge().failed("execution_failed");
      }
    }
    data.put("results", results);
    s.put(id, "submission", user, data);
  }

  Map<String, Object> waitFor(
    String receipt,
    Instant jobDeadline
  ) throws InterruptedException {
    Instant deadline = Instant.now().plusSeconds(60);
    if (jobDeadline.isBefore(deadline)) deadline = jobDeadline;
    long delay = 150;
    while (Instant.now().isBefore(deadline)) {
      var result = judge().poll(receipt);
      int status = (
        (Number) ((Map<?, ?>) result.get("status")).get("id")
      ).intValue();
      if (status > 2) return result;
      Thread.sleep(delay);
      delay = Math.min(1000, delay * 2);
    }
    throw new InterruptedJob(
      "The runner did not return a result before the polling deadline."
    );
  }

  private static String bounded(String text) {
    return text.substring(0, Math.min(text.length(), 8000));
  }

  private static final class InterruptedJob extends RuntimeException {

    InterruptedJob(String message) {
      super(message);
    }
  }

  @PreDestroy
  public void close() {
    stopping = true;
    jobs.shutdownNow();
  }

  static String normalize(String value) {
    return value
      .replace("\r\n", "\n")
      .replaceAll("[ \\t]+(?=\\n|$)", "")
      .stripTrailing();
  }
}
