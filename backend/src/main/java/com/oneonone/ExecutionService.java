package com.oneonone;

import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ExecutionService {

  final Store s;

  @Value("${app.judge-url}")
  String url;

  @Value("${app.judge-key}")
  String key;

  @Value("${app.judge-host}")
  String host;

  final ExecutorService jobs = new ThreadPoolExecutor(
    2,
    2,
    0,
    TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(20),
    new ThreadPoolExecutor.AbortPolicy()
  );

  public ExecutionService(Store s) {
    this.s = s;
  }

  public boolean available() {
    return key != null && !key.isBlank();
  }

  public static Map<String, Object> visible(Map<String, Object> b) {
    var out = new LinkedHashMap<>(b);
    out.remove("tokens");
    out.remove("owner");
    return out;
  }

  public Map<String, Object> submit(String user, Map<String, Object> b) {
    if (!available()) throw new ResponseStatusException(
      HttpStatus.SERVICE_UNAVAILABLE,
      "Code execution needs a Judge0 API key. Your editor and saved drafts still work."
    );
    String problem = Store.text(b, "problem", ""),
      lang = Store.text(b, "language", "java"),
      code = Store.text(b, "code", "");
    if (
      !Set.of("java", "python", "cpp").contains(lang) ||
      code.isBlank() ||
      code.length() > 50000
    ) throw new IllegalArgumentException(
      "Choose Java, Python or C++ and supply up to 50000 characters of code."
    );
    var p = s.get(problem);
    if (!p.containsKey("tests")) throw new IllegalArgumentException(
      "Choose a practice problem."
    );
    s.quota(user, "execution", 50);
    boolean official = !Boolean.FALSE.equals(b.get("official"));
    String input = Store.text(b, "input", "");
    if (input.length() > 10000) throw new IllegalArgumentException(
      "Custom input must be under 10000 characters."
    );
    var data = new LinkedHashMap<String, Object>();
    String id = "submission-" + UUID.randomUUID();
    data.putAll(
      Map.of(
        "problem",
        problem,
        "language",
        lang,
        "code",
        code,
        "official",
        official,
        "status",
        "QUEUED",
        "createdAt",
        Instant.now().toString(),
        "results",
        List.of()
      )
    );
    s.put(id, "submission", user, data);
    try {
      jobs.submit(() -> run(user, id, p, lang, code, official, input));
    } catch (RejectedExecutionException e) {
      data.put("status", "UNAVAILABLE");
      data.put("message", "The execution queue is full. Try again shortly.");
      s.put(id, "submission", user, data);
    }
    return visible(s.get(id));
  }

  void run(
    String user,
    String id,
    Map<String, Object> p,
    String lang,
    String code,
    boolean official,
    String input
  ) {
    var data = new LinkedHashMap<>(s.get(id));
    data.put("status", "RUNNING");
    s.put(id, "submission", user, data);
    List<Map<String, Object>> results = new ArrayList<>();
    try {
      List<Map<String, Object>> tests = official
        ? Store.items(p.get("tests"))
        : List.of(Map.of("input", input, "output", "", "public", true));
      int index = 0;
      String overall = "ACCEPTED";
      for (var test : tests) {
        var req = new LinkedHashMap<String, Object>();
        req.putAll(
          Map.of(
            "source_code",
            code,
            "language_id",
            lang.equals("java") ? 62 : lang.equals("python") ? 71 : 54,
            "stdin",
            test.get("input"),
            "cpu_time_limit",
            lang.equals("java") ? 5 : 2,
            "wall_time_limit",
            10,
            "memory_limit",
            256000,
            "max_file_size",
            128,
            "enable_network",
            false
          )
        );
        var factory =
          new org.springframework.http.client.JdkClientHttpRequestFactory(
            java.net.http.HttpClient.newBuilder()
              .connectTimeout(Duration.ofSeconds(10))
              .build()
          );
        factory.setReadTimeout(Duration.ofSeconds(15));
        RestClient client = RestClient.builder()
          .requestFactory(factory)
          .baseUrl(url)
          .defaultHeader("X-RapidAPI-Key", key)
          .defaultHeader("X-RapidAPI-Host", host)
          .build();
        Map<String, Object> created = client
          .post()
          .uri("/submissions?base64_encoded=false&wait=false")
          .contentType(MediaType.APPLICATION_JSON)
          .body(req)
          .retrieve()
          .body(Map.class);
        String token = created.get("token").toString();
        Map<String, Object> res = null;
        for (int attempt = 0; attempt < 40; attempt++) {
          Thread.sleep(500);
          res = client
            .get()
            .uri("/submissions/" + token + "?base64_encoded=false")
            .retrieve()
            .body(Map.class);
          int status = (
            (Number) ((Map<?, ?>) res.get("status")).get("id")
          ).intValue();
          if (status > 2) break;
        }
        int status = (
          (Number) ((Map<?, ?>) res.get("status")).get("id")
        ).intValue();
        if (status <= 2) throw new IllegalStateException("Timed out");
        String actual = Objects.toString(res.get("stdout"), ""),
          expected = Objects.toString(test.get("output"), "");
        boolean pass =
          status == 3 &&
          (!official || normalize(actual).equals(normalize(expected)));
        String verdict = pass
          ? "PASSED"
          : status == 3
            ? "WRONG_ANSWER"
            : status == 6
              ? "COMPILATION_ERROR"
              : status == 5
                ? "TIME_LIMIT"
                : "RUNTIME_ERROR";
        boolean pub = Boolean.TRUE.equals(test.get("public"));
        Map<String, Object> row = new LinkedHashMap<>();
        row.putAll(
          Map.of(
            "index",
            ++index,
            "status",
            verdict,
            "public",
            pub,
            "time",
            Objects.toString(res.get("time"), ""),
            "memory",
            Objects.toString(res.get("memory"), "")
          )
        );
        if (pub) {
          row.put("input", test.get("input"));
          row.put(
            "actual",
            actual.substring(0, Math.min(actual.length(), 8000))
          );
          if (official) row.put("expected", expected);
        }
        if (status == 6) row.put(
          "message",
          Objects.toString(res.get("compile_output"), "Compilation failed.")
        );
        results.add(row);
        if (!pass && overall.equals("ACCEPTED")) overall = verdict;
        if (status == 6) break;
      }
      data.put("status", official ? overall : "FINISHED");
      if (official && overall.equals("ACCEPTED")) {
        synchronized (s) {
          var state = new LinkedHashMap<>(
            s.find("state-" + user).orElse(Map.of())
          );
          Set<String> solved = new LinkedHashSet<>(
            Store.strings(state.get("solved"))
          );
          solved.add(p.get("id").toString());
          state.put("solved", solved);
          s.put("state-" + user, "state", user, state);
        }
      }
    } catch (Exception e) {
      data.put("status", "UNAVAILABLE");
      data.put(
        "message",
        "The code runner could not finish. Your submission is saved; try again."
      );
    }
    data.put("results", results);
    s.put(id, "submission", user, data);
  }

  static String normalize(String s) {
    return s
      .replace("\r\n", "\n")
      .replaceAll("[ \\t]+(?=\\n|$)", "")
      .stripTrailing();
  }
}
