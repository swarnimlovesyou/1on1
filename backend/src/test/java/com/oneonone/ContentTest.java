package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import javax.tools.ToolProvider;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.ObjectMapper;

class ContentTest {

  @Test
  void allReferenceSolutionsPassAllJudgeFixtures() throws Exception {
    var resource = getClass().getResourceAsStream("/content.json");
    var data = new ObjectMapper().readValue(resource, Map.class);
    var problems = Store.items(data.get("problems"));
    assertEquals(60, problems.size());
    assertEquals(49, Store.items(data.get("lessons")).size());
    Path dir = Files.createTempDirectory("1on1-references");
    List<String> sources = new ArrayList<>();
    for (int i = 0; i < problems.size(); i++) {
      String name = "Reference" + i;
      Path source = dir.resolve(name + ".java");
      Files.writeString(
        source,
        problems
          .get(i)
          .get("reference")
          .toString()
          .replace("public class Main", "public class " + name)
      );
      sources.add(source.toString());
    }
    int compiled = ToolProvider.getSystemJavaCompiler().run(
      null,
      null,
      null,
      sources.toArray(String[]::new)
    );
    assertEquals(0, compiled, "Every authored Java reference must compile");
    InputStream originalIn = System.in;
    PrintStream originalOut = System.out;
    try (var loader = new URLClassLoader(new URL[] { dir.toUri().toURL() })) {
      for (int i = 0; i < problems.size(); i++) {
        var problem = problems.get(i);
        var main = loader
          .loadClass("Reference" + i)
          .getMethod("main", String[].class);
        for (var test : Store.items(problem.get("tests"))) {
          var out = new ByteArrayOutputStream();
          System.setIn(
            new ByteArrayInputStream(
              test
                .get("input")
                .toString()
                .getBytes(java.nio.charset.StandardCharsets.UTF_8)
            )
          );
          System.setOut(
            new PrintStream(out, true, java.nio.charset.StandardCharsets.UTF_8)
          );
          main.invoke(null, (Object) new String[0]);
          assertEquals(
            ExecutionService.normalize(test.get("output").toString()),
            ExecutionService.normalize(
              out.toString(java.nio.charset.StandardCharsets.UTF_8)
            ),
            problem.get("title") + " input " + test.get("input")
          );
        }
      }
    } finally {
      System.setIn(originalIn);
      System.setOut(originalOut);
    }
  }

  @Test
  void everyProblemHasAPythonReferenceSpecificHintsAndAnEditorial() throws Exception {
    var data = new ObjectMapper().readValue(getClass().getResourceAsStream("/content.json"), Map.class);
    Set<String> hintTexts = new HashSet<>();
    for (var problem : Store.items(data.get("problems"))) {
      String id = problem.get("id").toString();
      var references = (Map<?, ?>) problem.get("references");
      assertNotNull(references, id + " has no references");
      assertEquals(problem.get("reference"), references.get("java"), id);
      assertTrue(references.get("python") instanceof String s && !s.isBlank(), id + " has no Python reference");
      var hints = Store.strings(problem.get("hints"));
      assertEquals(3, hints.size(), id);
      // a hint shared with another problem is a generic placeholder, not a hint about this one
      for (String hint : hints) assertTrue(hintTexts.add(hint), id + " reuses the hint: " + hint);
      assertTrue(Store.text(problem, "editorial", "").length() >= 200, id + " editorial is too thin");
      assertTrue(Store.items(problem.get("tests")).stream().anyMatch(t -> Boolean.FALSE.equals(t.get("public"))), id + " has no hidden case");
    }
  }
}
