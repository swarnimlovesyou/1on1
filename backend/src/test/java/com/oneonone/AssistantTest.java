package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.web.server.ResponseStatusException;

/** Pairing an external assistant: a revocable token that reads one learner's context and notes, and nothing else. */
class AssistantTest {

  Store store;
  AssistantController assistant;

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(new DriverManagerDataSource("jdbc:h2:mem:" + UUID.randomUUID() + ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", ""));
    for (String m : List.of("V1__initial.sql", "V2__learning_evidence.sql", "V3__review_evidence.sql")) {
      var source = new String(getClass().getResourceAsStream("/db/migration/" + m).readAllBytes(), StandardCharsets.UTF_8);
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    var content = store.decode(new String(getClass().getResourceAsStream("/content.json").readAllBytes(), StandardCharsets.UTF_8));
    for (var l : Store.items(content.get("lessons"))) store.put(l.get("id").toString(), "lesson", "public", l);
    db.update("insert into members(id,email,name,password,role) values('ana','ana@example.test','Ana','x','learner')");
    db.update("insert into members(id,email,name,password,role) values('ben','ben@example.test','Ben','x','learner')");
    store.put("note-ben-secret", "note", "ben", Map.of("title", "Ben's private note", "text", "graphs are hard", "lesson", "", "createdAt", "2026-11-01T00:00:00Z", "reviewed", false));
    assistant = new AssistantController(store, new LearningMapService(store), null);
  }

  String bearer(Map<String, Object> created) {
    return "Bearer " + created.get("token");
  }

  @Test
  void aTokenReadsAndWritesOnlyItsOwnersNotesAndIsShownOnce() {
    var created = assistant.create("ana", Map.of("label", "Claude Desktop"));
    assertTrue(created.get("token").toString().startsWith("1on1_"));
    assertFalse(assistant.list("ana").getFirst().containsKey("token"), "the token is shown once, then only its label");
    assistant.saveNote(bearer(created), Map.of("title", "Kadane", "text", "reset the running sum when it goes negative"));
    var notes = assistant.notes(bearer(created), "kadane");
    assertEquals(1, notes.size());
    assertEquals("Kadane", notes.getFirst().get("title"));
    assertTrue(assistant.notes(bearer(created), "graphs").isEmpty(), "never another learner's notes");
    var context = assistant.context(bearer(created));
    assertEquals("Ana", context.get("name"));
    assertNotNull(context.get("nextAction"));
  }

  @Test
  void revokedMissingOrMalformedTokensAreRejected() {
    var created = assistant.create("ana", Map.of("label", "Laptop"));
    assistant.revoke("ana", assistant.list("ana").getFirst().get("id").toString());
    assertEquals(401, assertThrows(ResponseStatusException.class, () -> assistant.context(bearer(created))).getStatusCode().value());
    assertEquals(401, assertThrows(ResponseStatusException.class, () -> assistant.context(null)).getStatusCode().value());
    assertEquals(401, assertThrows(ResponseStatusException.class, () -> assistant.context("Bearer nope")).getStatusCode().value());
    var other = assistant.create("ana", Map.of("label", "Other"));
    assertEquals(404, assertThrows(ResponseStatusException.class, () -> assistant.revoke("ben", assistant.list("ana").getFirst().get("id").toString())).getStatusCode().value(), "only the owner can revoke");
    assertNotNull(assistant.context(bearer(other)));
  }

  @Test
  void aLearnerHasAtMostFivePairings() {
    for (int i = 0; i < 5; i++) assistant.create("ana", Map.of("label", "Device " + i));
    assertThrows(IllegalArgumentException.class, () -> assistant.create("ana", Map.of("label", "One too many")));
  }
}
