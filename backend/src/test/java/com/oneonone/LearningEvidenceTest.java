package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

class LearningEvidenceTest {

  Store store;
  ProgressService progress;
  ChallengeService challenges;
  final TraceEngine traces = new TraceEngine();

  @BeforeEach
  void setup() throws Exception {
    var db = new JdbcTemplate(
      new DriverManagerDataSource(
        "jdbc:h2:mem:" +
          UUID.randomUUID() +
          ";MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1",
        "sa",
        ""
      )
    );
    for (String migration : List.of(
      "V1__initial.sql",
      "V2__learning_evidence.sql",
      "V3__review_evidence.sql"
    )) {
      var source = new String(
        getClass()
          .getResourceAsStream("/db/migration/" + migration)
          .readAllBytes(),
        StandardCharsets.UTF_8
      );
      for (String sql : source.split(";")) if (!sql.isBlank()) db.execute(sql);
    }
    store = new Store(db);
    progress = new ProgressService(store);
    challenges = new ChallengeService(store, traces, progress);
    var content = store.decode(
      new String(
        getClass().getResourceAsStream("/content.json").readAllBytes(),
        StandardCharsets.UTF_8
      )
    );
    for (var lesson : Store.items(content.get("lessons")))
      store.put(lesson.get("id").toString(), "lesson", "public", lesson);
  }

  @Test
  void autosavesNeverCreateActivityOrAwardSolvedCredit() {
    progress.update(
      "alice",
      Map.of(
        "resumeLesson",
        "lesson-sliding-window",
        "resumeStep",
        3,
        "solved",
        List.of("fake")
      )
    );
    assertEquals(Map.of(), progress.summary("alice").get("activity"));
    assertEquals(List.of(), progress.summary("alice").get("solved"));
    progress.update(
      "alice",
      Map.of("completed", List.of("lesson-sliding-window"))
    );
    progress.update(
      "alice",
      Map.of("completed", List.of("lesson-sliding-window"))
    );
    assertEquals(
      1,
      store.db.queryForObject(
        "select count(*) from learning_events",
        Integer.class
      )
    );
  }

  @Test
  void publicLessonsContainNoAnswerKeysOrGradingRules() {
    for (var lesson : store.list("lesson", "public")) {
      var publicLesson = ChallengeService.publicLesson(lesson);
      assertFalse(
        ((Map<?, ?>) publicLesson.get("checkpoint")).containsKey("answer")
      );
      for (var item : Store.items(publicLesson.get("challenges")))
        for (String privateKey : List.of(
          "answer",
          "rule",
          "explanation",
          "requiredTarget"
        ))
          assertFalse(item.containsKey(privateKey));
    }
  }

  @Test
  void distinctReferencePredictionsAreGradedAndAttemptsAreIdempotent() {
    var result = challenges.attempt(
      "alice",
      "challenge-sliding-window-prediction",
      new Contracts.AttemptRequest(1, "attempt-123456")
    );
    assertTrue(result.correct());
    assertEquals(
      result.id(),
      challenges
        .attempt(
          "alice",
          "challenge-sliding-window-prediction",
          new Contracts.AttemptRequest(1, "attempt-123456")
        )
        .id()
    );
    assertEquals(
      1,
      store.db.queryForObject(
        "select count(*) from challenge_attempts",
        Integer.class
      )
    );
    assertThrows(
      org.springframework.web.server.ResponseStatusException.class,
      () ->
        challenges.attempt(
          "alice",
          "challenge-sliding-window-prediction",
          new Contracts.AttemptRequest(0, "attempt-123456")
        )
    );
  }

  @Test
  void dryRunOracleMatchesIndependentlyWorkedStates() {
    var answers = Map.<String, Map<String, Object>>of(
      "sliding-window",
      Map.of("left", 1, "right", 3, "sum", 7, "best", 8),
      "bst",
      Map.of("inserted", 6, "root", 8, "height", 3),
      "bfs",
      Map.of("visiting", 0, "discovered", 2, "frontier", "1,2"),
      "tabulation",
      Map.of("i", 5, "value", 5)
    );
    for (var answer : answers.entrySet())
      assertTrue(
        challenges
          .attempt(
            "alice",
            "challenge-" + answer.getKey() + "-dry-run",
            new Contracts.AttemptRequest(
              answer.getValue(),
              UUID.randomUUID().toString()
            )
          )
          .correct(),
        answer.getKey()
      );
    assertFalse(
      challenges
        .attempt(
          "alice",
          "challenge-sliding-window-dry-run",
          new Contracts.AttemptRequest(
            Map.of("left", 0, "right", 3, "sum", 7, "best", 8),
            UUID.randomUUID().toString()
          )
        )
        .correct()
    );
  }

  @Test
  void manipulationChecksComputedStateAndFixedWindowSize() {
    assertTrue(
      challenges
        .attempt(
          "alice",
          "challenge-sliding-window-manipulation",
          new Contracts.AttemptRequest(
            Map.of(
              "algorithm",
              "sliding-window",
              "input",
              "4,4,4",
              "target",
              3
            ),
            UUID.randomUUID().toString()
          )
        )
        .correct()
    );
    assertFalse(
      challenges
        .attempt(
          "alice",
          "challenge-sliding-window-manipulation",
          new Contracts.AttemptRequest(
            Map.of(
              "algorithm",
              "sliding-window",
              "input",
              "6,6,0",
              "target",
              2
            ),
            UUID.randomUUID().toString()
          )
        )
        .correct()
    );
  }

  @Test
  void guestsCanPractiseWithoutCreatingLearningRecords() {
    var result = challenges.attempt(
      null,
      "challenge-bfs-prediction",
      new Contracts.AttemptRequest(0, UUID.randomUUID().toString())
    );
    assertTrue(result.correct());
    assertFalse(result.saved());
    assertEquals(
      0,
      store.db.queryForObject(
        "select count(*) from challenge_attempts",
        Integer.class
      )
    );
  }

  @Test
  void sortingPreservesDistinctIdentitiesForDuplicateValues() {
    var trace = traces.trace(
      Map.of("algorithm", "quick-sort", "input", "2,1,2")
    );
    var steps = Store.items(trace.get("steps"));
    var initial = (List<Contracts.Entity>) steps.getFirst().get("entities");
    var last = (List<Contracts.Entity>) steps.getLast().get("entities");
    assertEquals(3, last.stream().map(Contracts.Entity::id).distinct().count());
    assertEquals(
      new HashSet<>(initial.stream().map(Contracts.Entity::id).toList()),
      new HashSet<>(last.stream().map(Contracts.Entity::id).toList())
    );
    for (var entity : last)
      assertEquals(
        entity.value(),
        initial
          .stream()
          .filter(old -> old.id().equals(entity.id()))
          .findFirst()
          .orElseThrow()
          .value()
      );
  }

  @Test
  void acceptedCreditIsAwardedOnceAndPreservesExistingNotes() {
    store.put("note-keep", "note", "alice", Map.of("text", "My explanation"));
    progress.accepted("alice", "problem-three-window", "submission-one");
    progress.accepted("alice", "problem-three-window", "submission-two");
    assertEquals(
      1,
      store.db.queryForObject(
        "select count(*) from solved_credits",
        Integer.class
      )
    );
    assertEquals(
      1,
      store.db.queryForObject(
        "select count(*) from learning_events",
        Integer.class
      )
    );
    assertEquals(
      "My explanation",
      store.owned("note-keep", "alice").get("text")
    );
  }

  @Test
  void everyAlgorithmCanBeExpressedByThePublicVersionedContract() {
    for (String algorithm : TraceEngine.LEGACY) {
      var typed = Contracts.ExecutionTrace.from(
        traces.trace(
          Map.of("algorithm", algorithm, "input", "4,2,7,1,3,6", "target", 3)
        )
      );
      assertEquals(2, typed.version());
      assertFalse(typed.steps().isEmpty());
      assertTrue(
        typed
          .steps()
          .stream()
          .allMatch(step -> step.operation() != null && step.entities() != null)
      );
    }
  }

  @Test
  void reversedLinksKeepTheOriginalNodeIdentities() {
    var trace = Contracts.ExecutionTrace.from(
      traces.trace(Map.of("algorithm", "linked-list", "input", "2,1,2"))
    );
    var initial = trace.steps().getFirst().entities();
    var last = trace.result();
    assertEquals(initial.get(2).id(), last.entities().getFirst().id());
    assertEquals(initial.get(0).id(), last.entities().getLast().id());
    assertEquals(initial.size(), last.links().size());
  }

  @Test
  void readingOnlyContextIsOwnedAndDoesNotInventAnExperimentOrActivity() {
    var custom = new LinkedHashMap<>(store.get("lesson-arrays"));
    custom.remove("experiment");
    custom.put("edited", true);
    store.put("lesson-arrays", "lesson", "public", custom);
    var study = new StudyController(store, traces, challenges, progress);
    var auth =
      new org.springframework.security.authentication.UsernamePasswordAuthenticationToken(
        "alice",
        "unused",
        List.of()
      );
    var saved = study.save(
      auth,
      "lesson-arrays",
      new Contracts.StudyContext(1, "lesson-arrays", null, 0, "code", "")
    );
    assertFalse(saved.containsKey("scene"));
    assertEquals("code", study.get(auth, "lesson-arrays").get("section"));
    assertEquals(Map.of(), progress.summary("alice").get("activity"));
    assertThrows(IllegalArgumentException.class, () ->
      study.save(
        auth,
        "lesson-bfs",
        new Contracts.StudyContext(1, "lesson-bfs", null, 0, "idea", "")
      )
    );
    var bob =
      new org.springframework.security.authentication.UsernamePasswordAuthenticationToken(
        "bob",
        "unused",
        List.of()
      );
    assertThrows(
      org.springframework.web.server.ResponseStatusException.class,
      () -> study.get(bob, "lesson-arrays")
    );
  }

  @Test
  void curriculumSeedUpdatePreservesEditedLessonsAndPrivateLearningRecords() throws Exception {
    var lesson = new LinkedHashMap<>(store.get("lesson-two-pointers"));
    lesson.put("edited", true);
    lesson.put("title", "My edited lesson");
    store.put("lesson-two-pointers", "lesson", "public", lesson);
    store.put(
      "note-retained",
      "note",
      "alice",
      Map.of("text", "My own explanation")
    );
    store.put(
      "draft-retained",
      "draft",
      "alice",
      Map.of("code", "// saved draft")
    );
    progress.update(
      "alice",
      Map.of("completed", List.of("lesson-two-pointers"))
    );
    progress.accepted("alice", "problem-three-window", "submission-retained");
    var context = store.put(
      "study-retained",
      "study-context",
      "alice",
      Map.of(
        "version",
        1,
        "lesson",
        "lesson-bfs",
        "step",
        3,
        "scene",
        Map.of(
          "algorithm",
          "bfs",
          "input",
          "4,2,7,1,3,6",
          "target",
          3,
          "seed",
          42
        )
      )
    );
    var seed = new ContentSeed(
      store,
      new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder()
    );
    seed.demo = false;
    seed.adminEmail = "";
    seed.adminPassword = "";
    seed.run();
    assertEquals(
      "My edited lesson",
      store.get("lesson-two-pointers").get("title")
    );
    assertEquals(
      "My own explanation",
      store.owned("note-retained", "alice").get("text")
    );
    assertEquals(
      "// saved draft",
      store.owned("draft-retained", "alice").get("code")
    );
    assertEquals(
      List.of("lesson-two-pointers"),
      progress.summary("alice").get("completed")
    );
    assertEquals(33, store.list("lesson", "public").size());
    assertEquals(context, store.owned("study-retained", "alice"));
    assertEquals(
      List.of("problem-three-window"),
      progress.summary("alice").get("solved")
    );
  }

  @Test
  void upgradedTraceKeepsLegacyPositionAndFullExperimentInput() {
    var old=Map.<String,Object>of("version",1,"lesson","lesson-sliding-window","scene",Map.of("algorithm","sliding-window","input","4,4,4,1","target",3,"seed",42),"step",3,"section","experiment");
    store.put("study-alice-lesson-sliding-window","study-context","alice",old);
    var study=new StudyController(store,traces,challenges,progress);
    var auth=new org.springframework.security.authentication.UsernamePasswordAuthenticationToken("alice","unused",List.of());
    var saved=study.save(auth,"lesson-sliding-window",new Contracts.StudyContext(1,"lesson-sliding-window",new Contracts.SceneRequest("sliding-window","4,4,4,1",3,"",42L),0,"experiment","",3));
    assertEquals(3,saved.get("traceRevision"));assertEquals(3,((Map<?,?>)saved.get("legacyPosition")).get("step"));
    assertEquals("4,4,4,1",((Map<?,?>)saved.get("scene")).get("input"));
    assertEquals(Map.of(),progress.summary("alice").get("activity"));
  }
}
