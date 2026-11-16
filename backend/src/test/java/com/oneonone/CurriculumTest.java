package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.InvocationTargetException;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import javax.tools.ToolProvider;
import org.junit.jupiter.api.Test;

class CurriculumTest {

  final Store reader = new Store(null);

  Map<String, Object> resource(String name) throws Exception {
    return reader.decode(
      new String(
        getClass()
          .getResourceAsStream("/" + name)
          .readAllBytes(),
        java.nio.charset.StandardCharsets.UTF_8
      )
    );
  }

  @Test
  void curriculumHasCompleteAcyclicDependenciesAndCanonicalApplications() throws Exception {
    var data = resource("curriculum.json");
    assertEquals(1, ((Number) data.get("version")).intValue());
    var concepts = Store.items(data.get("concepts"));
    var questions = Store.items(data.get("questions"));
    assertEquals(24, concepts.size());
    assertEquals(47, questions.size());
    var ids = new HashSet<String>();
    var qids = new HashSet<String>();
    for (var q : questions) {
      assertTrue(qids.add(q.get("id").toString()));
      assertEquals(3, Store.strings(q.get("progressiveHints")).size());
      assertFalse(q.get("approachOutline").toString().isBlank());
      if (q.get("kind").equals("external-reference")) assertTrue(
        q
          .get("canonicalUrl")
          .toString()
          .startsWith("https://leetcode.com/problems/")
      );
    }
    int associations = 0;
    for (var c : concepts) {
      // The declared order must be a valid topological order, not merely cycle-free.
      for (var dependency : Store.strings(c.get("prerequisites")))
        assertTrue(ids.contains(dependency), c.get("id") + " → " + dependency);
      assertTrue(ids.add(c.get("id").toString()));
      assertFalse(Store.strings(c.get("objectives")).isEmpty());
      assertFalse(
        Store.items(
          ((Map<?, ?>) c.get("java")).get("lineAnnotations")
        ).isEmpty()
      );
      assertFalse(
        Store.strings(
          ((Map<?, ?>) c.get("visualization")).get("expectedStates")
        ).isEmpty()
      );
      var apps = Store.items(c.get("applications"));
      assertEquals(2, apps.size());
      associations += apps.size();
      for (var app : apps) assertTrue(qids.contains(app.get("questionId")));
    }
    assertEquals(48, associations);
    for (var c : concepts)
      for (var app : Store.items(c.get("applications")))
        for (var prerequisite : Store.strings(
          app.get("additionalPrerequisites")
        ))
          assertTrue(ids.contains(prerequisite));
    for (var q : questions)
      assertTrue(ids.containsAll(Store.strings(q.get("conceptTags"))));
    assertEquals(
      2,
      concepts
        .stream()
        .flatMap(c -> Store.items(c.get("applications")).stream())
        .filter(a -> a.get("questionId").equals("leetcode-206"))
        .count()
    );
  }

  @Test
  void javaTeachingExamplesCompileAndPassDocumentedNormalAndBoundaryCases() throws Exception {
    var concepts = Store.items(resource("curriculum.json").get("concepts"));
    Path testRoot = Path.of("target").toAbsolutePath().normalize();
    Path directory = Files.createTempDirectory(testRoot, "curriculum-");
    try {
      var sources = new ArrayList<String>();
      for (int i = 0; i < concepts.size(); i++) {
        var example = (Map<String, Object>) concepts.get(i).get("java");
        String code = example
          .get("source")
          .toString()
          .replace("class CurriculumExample", "public class Teaching" + i);
        var methods = new StringBuilder();
        var cases = Store.items(example.get("cases"));
        assertTrue(cases.size() >= 2);
        for (int j = 0; j < cases.size(); j++) methods.append(
          "\npublic static String case" +
            j +
            "() { return String.valueOf(" +
            cases.get(j).get("expression") +
            "); }\n"
        );
        code = code.substring(0, code.lastIndexOf('}')) + methods + "}";
        Path file = directory.resolve("Teaching" + i + ".java");
        Files.writeString(file, code);
        sources.add(file.toString());
      }
      var args = new ArrayList<>(List.of("--release", "21"));
      args.addAll(sources);
      assertEquals(
        0,
        ToolProvider.getSystemJavaCompiler().run(
          null,
          null,
          null,
          args.toArray(String[]::new)
        ),
        "All 24 complete Java examples must compile"
      );
      try (
        var loader = new URLClassLoader(new URL[] { directory.toUri().toURL() })
      ) {
        for (int i = 0; i < concepts.size(); i++) {
          var example = (Map<String, Object>) concepts.get(i).get("java");
          var cases = Store.items(example.get("cases"));
          for (int j = 0; j < cases.size(); j++) {
            var test = cases.get(j);
            var method = loader.loadClass("Teaching" + i).getMethod("case" + j);
            String label =
              concepts.get(i).get("id") + ": " + test.get("expression");
            if (test.containsKey("expectedException")) {
              var error = assertThrows(
                InvocationTargetException.class,
                () -> method.invoke(null),
                label
              );
              assertEquals(
                test.get("expectedException"),
                error.getCause().getClass().getSimpleName(),
                label
              );
            } else assertEquals(
              test.get("expected"),
              method.invoke(null),
              label
            );
          }
          for (var annotation : Store.items(example.get("lineAnnotations"))) {
            int line = ((Number) annotation.get("line")).intValue();
            assertTrue(
              line > 0 &&
                line <= example.get("implementation").toString().lines().count()
            );
          }
        }
      }
    } finally {
      assertTrue(directory.toRealPath().startsWith(testRoot.toRealPath()));
      try (var files = Files.walk(directory)) {
        for (var file : files.sorted(Comparator.reverseOrder()).toList())
          Files.delete(file);
      }
    }
  }

  @Test
  void publicCurriculumAndLessonsWithholdCheckpointGold() throws Exception {
    var publicData = new CurriculumController().get();
    for (var c : Store.items(publicData.get("concepts"))) {
      assertFalse(((Map<?, ?>) c.get("checkpoint")).containsKey("answer"));
      assertFalse(((Map<?, ?>) c.get("java")).containsKey("cases"));
    }
    for (var lesson : Store.items(resource("content.json").get("lessons"))) {
      var safe = ChallengeService.publicLesson(lesson);
      if (safe.get("teaching") instanceof Map<?, ?> teaching) assertFalse(
        ((Map<?, ?>) teaching.get("checkpoint")).containsKey("answer")
      );
    }
  }

  @Test
  void existingIdsAndAdvancedAlgorithmsRemainAndNewLessonsHaveNoFakeScenes() throws Exception {
    var content = resource("content.json");
    var lessons = Store.items(content.get("lessons"));
    var ids = lessons
      .stream()
      .map(l -> l.get("id").toString())
      .collect(java.util.stream.Collectors.toSet());
    assertEquals(33, ids.size());
    assertEquals(60, Store.items(content.get("problems")).size());
    for (String algorithm : TraceEngine.SUPPORTED)
      assertTrue(ids.contains("lesson-" + algorithm));
    int specs = 0,
      advanced = 0;
    for (var lesson : lessons) {
      assertTrue(ids.containsAll(Store.strings(lesson.get("prerequisites"))));
      if (lesson.get("branch").equals("advanced")) advanced++;
      if ("specification-only".equals(lesson.get("interactiveStatus"))) {
        specs++;
        assertNull(lesson.get("experiment"));
      }
    }
    assertEquals(9, specs);
    assertEquals(7, advanced);
    var pathIds = Store.items(content.get("paths"))
      .stream()
      .map(p -> p.get("id"))
      .toList();
    assertTrue(
      pathIds.containsAll(
        List.of("path-foundations", "path-core", "path-interview")
      )
    );
  }
}
