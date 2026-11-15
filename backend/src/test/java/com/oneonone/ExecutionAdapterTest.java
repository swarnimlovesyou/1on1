package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.HttpServer;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class ExecutionAdapterTest {

  Store store;
  ExecutionService execution;
  HttpServer judge;
  List<Map<String, Object>> requests;
  volatile int replyStatus = 3;
  String receivedToken, receivedRapidKey;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(
      new DriverManagerDataSource(
        "jdbc:h2:mem:" +
          UUID.randomUUID() +
          ";MODE=PostgreSQL;DB_CLOSE_DELAY=-1",
        "sa",
        ""
      )
    );
    for (String sql : new String(
      getClass()
        .getResourceAsStream("/db/migration/V1__initial.sql")
        .readAllBytes()
    ).split(";"))
      if (!sql.isBlank()) db.execute(sql);
    for (String sql : new String(
      getClass()
        .getResourceAsStream("/db/migration/V2__learning_evidence.sql")
        .readAllBytes()
    ).split(";"))
      if (!sql.isBlank()) db.execute(sql);
    store = new Store(db);
    execution = new ExecutionService(store, new ProgressService(store));
    execution.mode = "rapidapi";
    requests = Collections.synchronizedList(new ArrayList<>());
    judge = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
    judge.createContext("/submissions", exchange -> {
      String body;
      if (exchange.getRequestMethod().equals("POST")) {
        requests.add(
          store.decode(
            new String(
              exchange.getRequestBody().readAllBytes(),
              StandardCharsets.UTF_8
            )
          )
        );
        receivedToken = exchange.getRequestHeaders().getFirst("X-Auth-Token");
        receivedRapidKey = exchange
          .getRequestHeaders()
          .getFirst("X-RapidAPI-Key");
        body = "{\"token\":\"fixture-token\"}";
      } else body =
        "{\"status\":{\"id\":" +
        replyStatus +
        "},\"stdout\":\"42\\n\",\"time\":\"0.01\",\"memory\":1000}";
      byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
      exchange.getResponseHeaders().add("Content-Type", "application/json");
      exchange.sendResponseHeaders(200, bytes.length);
      exchange.getResponseBody().write(bytes);
      exchange.close();
    });
    judge.createContext("/languages", exchange -> {
      byte[] bytes =
        "[{\"id\":62,\"name\":\"Java (OpenJDK)\"},{\"id\":71,\"name\":\"Python (3.8)\"},{\"id\":54,\"name\":\"C++ (GCC)\"}]".getBytes(
          StandardCharsets.UTF_8
        );
      exchange.getResponseHeaders().add("Content-Type", "application/json");
      exchange.sendResponseHeaders(200, bytes.length);
      exchange.getResponseBody().write(bytes);
      exchange.close();
    });
    judge.start();
    execution.url = "http://127.0.0.1:" + judge.getAddress().getPort();
    execution.key = "test-adapter-key";
    execution.host = "local-contract-test";
    store.put(
      "problem-fixture",
      "problem",
      "public",
      Map.of(
        "tests",
        List.of(
          Map.of("input", "private input", "output", "42\n", "public", false)
        )
      )
    );
  }

  @AfterEach
  void cleanup() {
    judge.stop(0);
    execution.jobs.shutdownNow();
  }

  @Test
  void acceptedCreditAndHiddenInputsStayPrivate() throws Exception {
    var created = execution.submit(
      "alice",
      Map.of(
        "problem",
        "problem-fixture",
        "code",
        "trusted fixture source",
        "language",
        "java",
        "official",
        true
      )
    );
    Map<String, Object> finished = await(created);
    assertEquals("ACCEPTED", finished.get("status"));
    assertEquals(
      List.of("problem-fixture"),
      new ProgressService(store).summary("alice").get("solved")
    );
    var result = Store.items(finished.get("results")).getFirst();
    assertFalse(result.containsKey("input"));
    assertFalse(result.containsKey("expected"));
    assertEquals(false, requests.getFirst().get("enable_network"));
  }

  @Test
  void customRunsNeverAwardCredit() throws Exception {
    var created = execution.submit(
      "alice",
      Map.of(
        "problem",
        "problem-fixture",
        "code",
        "trusted fixture source",
        "language",
        "python",
        "official",
        false,
        "input",
        "custom"
      )
    );
    assertEquals("FINISHED", await(created).get("status"));
    assertTrue(store.find("state-alice").isEmpty());
    assertEquals(71, requests.getFirst().get("language_id"));
  }

  @Test
  void wrongAnswersDoNotAwardCredit() throws Exception {
    store.put(
      "problem-fixture",
      "problem",
      "public",
      Map.of(
        "tests",
        List.of(Map.of("input", "public", "output", "43\n", "public", true))
      )
    );
    var created = execution.submit(
      "alice",
      Map.of(
        "problem",
        "problem-fixture",
        "code",
        "trusted fixture source",
        "language",
        "cpp",
        "official",
        true
      )
    );
    assertEquals("WRONG_ANSWER", await(created).get("status"));
    assertTrue(store.find("state-alice").isEmpty());
    assertEquals(54, requests.getFirst().get("language_id"));
  }

  @Test
  void missingConfigurationNeverPretendsToGrade() {
    execution.key = "";
    assertThrows(
      org.springframework.web.server.ResponseStatusException.class,
      () -> execution.submit("alice", Map.of())
    );
  }

  @Test
  void ownershipChecksAndOutputNormalization() {
    store.put("note-private", "note", "alice", Map.of("text", "private"));
    assertThrows(
      org.springframework.web.server.ResponseStatusException.class,
      () -> store.owned("note-private", "bob")
    );
    assertEquals("42\n7", ExecutionService.normalize("42  \r\n7\n"));
  }

  @Test
  void selfHostedAuthenticationDoesNotSendHostedCredentials() throws Exception {
    execution.mode = "self-hosted";
    execution.token = "local-token";
    var created = execution.submit(
      "alice",
      Map.of(
        "problem",
        "problem-fixture",
        "language",
        "java",
        "code",
        "trusted fixture",
        "official",
        false
      )
    );
    assertEquals("FINISHED", await(created).get("status"));
    assertEquals("local-token", receivedToken);
    assertNull(receivedRapidKey);
  }

  @Test
  void retriesReturnTheSameJobAndRejectAChangedPayload() throws Exception {
    var body = Map.<String, Object>of(
      "problem",
      "problem-fixture",
      "language",
      "java",
      "code",
      "trusted fixture",
      "requestId",
      "same-request-123"
    );
    var first = execution.submit("alice", body);
    var second = execution.submit("alice", body);
    assertEquals(first.get("id"), second.get("id"));
    await(first);
    assertEquals(1, requests.size());
    var changed = new HashMap<>(body);
    changed.put("code", "different");
    assertThrows(
      org.springframework.web.server.ResponseStatusException.class,
      () -> execution.submit("alice", changed)
    );
  }

  @Test
  void recoveryPollsSavedReceiptsWithoutDispatchingAgain() throws Exception {
    var data = durable("known-receipt");
    data.put("tokens", Map.of("0", "fixture-token"));
    store.put("submission-recover", "submission", "alice", data);
    execution.recover();
    assertEquals(
      "ACCEPTED",
      await(Map.of("id", "submission-recover")).get("status")
    );
    assertTrue(requests.isEmpty());
  }

  @Test
  void uncertainDispatchIsInterruptedRatherThanDuplicated() throws Exception {
    var data = durable("uncertain-dispatch");
    data.put("dispatching", 0);
    store.put("submission-uncertain", "submission", "alice", data);
    execution.recover();
    assertEquals(
      "INTERRUPTED",
      await(Map.of("id", "submission-uncertain")).get("status")
    );
    assertTrue(requests.isEmpty());
  }

  @Test
  void expiredJobsDoNotExecute() throws Exception {
    var data = durable("expired-job");
    data.put("deadlineAt", java.time.Instant.now().minusSeconds(1).toString());
    store.put("submission-expired", "submission", "alice", data);
    execution.recover();
    assertEquals(
      "INTERRUPTED",
      await(Map.of("id", "submission-expired")).get("status")
    );
    assertTrue(requests.isEmpty());
  }

  @Test
  void customCompilationErrorsAreNotReportedAsFinished() throws Exception {
    replyStatus = 6;
    var job = execution.submit(
      "alice",
      Map.of(
        "problem",
        "problem-fixture",
        "language",
        "cpp",
        "code",
        "invalid fixture",
        "official",
        false
      )
    );
    assertEquals("COMPILATION_ERROR", await(job).get("status"));
    assertEquals(
      List.of(),
      new ProgressService(store).summary("alice").get("solved")
    );
  }

  @Test
  void configurationAndLanguageDiscoveryDoNotClaimExecutionVerification() {
    assertTrue(execution.available());
    assertEquals(false, execution.probe().get("executionVerified"));
    assertEquals(true, execution.status().get("reachable"));
  }

  Map<String, Object> durable(String request) {
    var data = new LinkedHashMap<String, Object>();
    data.put("problem", "problem-fixture");
    data.put("code", "trusted fixture");
    data.put("language", "java");
    data.put("official", true);
    data.put("status", "RUNNING");
    data.put("createdAt", java.time.Instant.now().toString());
    data.put("deadlineAt", java.time.Instant.now().plusSeconds(60).toString());
    data.put("requestId", request);
    data.put("tokens", Map.of());
    data.put("results", List.of());
    data.put("dispatching", -1);
    data.put(
      "fixtures",
      List.of(
        Map.of("input", "private input", "output", "42\n", "public", false)
      )
    );
    return data;
  }

  Map<String, Object> await(Map<String, Object> created) throws Exception {
    String id = created.get("id").toString();
    for (int i = 0; i < 100; i++) {
      var data = store.get(id);
      if (
        !Set.of("QUEUED", "RUNNING").contains(data.get("status"))
      ) return data;
      Thread.sleep(50);
    }
    throw new AssertionError("Adapter did not finish");
  }
}
