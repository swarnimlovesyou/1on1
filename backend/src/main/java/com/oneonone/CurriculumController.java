package com.oneonone;

import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.web.bind.annotation.*;

/** Authored curriculum metadata; progress and executable grading remain separate. */
@RestController
@RequestMapping("/api/v1/curriculum")
public class CurriculumController {

  private final Map<String, Object> curriculum;

  public CurriculumController() throws Exception {
    var json = new tools.jackson.databind.ObjectMapper();
    var data = json.readValue(
      new ClassPathResource("curriculum.json").getInputStream(),
      Map.class
    );
    curriculum = new LinkedHashMap<>(data);
    curriculum.put(
      "concepts",
      Store.items(data.get("concepts"))
        .stream()
        .map(CurriculumController::publicConcept)
        .toList()
    );
  }

  static Map<String, Object> publicConcept(Map<String, Object> source) {
    var out = new LinkedHashMap<>(source);
    if (source.get("checkpoint") instanceof Map<?, ?> raw) {
      var checkpoint = new LinkedHashMap<String, Object>(
        (Map<String, Object>) raw
      );
      checkpoint.remove("answer");
      checkpoint.remove("explanation");
      out.put("checkpoint", checkpoint);
    }
    if (source.get("java") instanceof Map<?, ?> raw) {
      var java = new LinkedHashMap<String, Object>((Map<String, Object>) raw);
      java.remove("cases");
      out.put("java", java);
    }
    return out;
  }

  @GetMapping
  public Map<String, Object> get() {
    return curriculum;
  }
}
