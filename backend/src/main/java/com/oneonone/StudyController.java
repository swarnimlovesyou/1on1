package com.oneonone;

import static com.oneonone.Contracts.*;

import java.time.Instant;
import java.util.*;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class StudyController {

  final Store store;
  final TraceEngine traces;
  final ChallengeService challenges;
  final ProgressService progress;

  public StudyController(
    Store store,
    TraceEngine traces,
    ChallengeService challenges,
    ProgressService progress
  ) {
    this.store = store;
    this.traces = traces;
    this.challenges = challenges;
    this.progress = progress;
  }

  @PostMapping("/challenges/{id}/attempts")
  public AttemptResult attempt(
    Authentication auth,
    @PathVariable String id,
    @RequestBody AttemptRequest body
  ) {
    String user =
      auth == null || auth instanceof AnonymousAuthenticationToken
        ? null
        : AuthController.user(auth);
    return challenges.attempt(user, id, body);
  }

  @PutMapping("/study-context/{lesson}")
  public synchronized Map<String, Object> save(
    Authentication auth,
    @PathVariable String lesson,
    @RequestBody StudyContext context
  ) {
    String user = AuthController.user(auth);
    if (
      context.traceRevision() != null &&
      context.traceRevision() != 2 &&
      context.traceRevision() != 3
    ) throw new IllegalArgumentException(
      "Choose a supported visualization revision."
    );
    var source = store.owned(lesson, "public");
    if (
      !lesson.equals(context.lesson()) ||
      context.version() != 1 ||
      (context.scene() != null &&
        !lesson.equals("lesson-" + context.scene().algorithm()))
    ) throw new IllegalArgumentException(
      "Save a matching lesson and experiment."
    );
    if (context.scene() == null) {
      if (
        source.get("experiment") != null || context.step() != 0
      ) throw new IllegalArgumentException(
        "Save an experiment for interactive lessons; reading-only lessons use step zero."
      );
    } else {
      var trace = traces.trace(context.scene().toMap());
      if (
        context.step() < 0 ||
        context.step() >= Store.items(trace.get("steps")).size()
      ) throw new IllegalArgumentException("Choose a step in this experiment.");
    }
    if (
      context.section() == null ||
      !context.section().matches("[a-zA-Z0-9_-]{1,80}") ||
      (context.codeRevision() != null && context.codeRevision().length() > 128)
    ) throw new IllegalArgumentException("Invalid saved study location.");
    var data = new LinkedHashMap<String, Object>();
    var previous = store.find("study-" + user + "-" + lesson);
    if (
      previous.isPresent() &&
      previous.get().get("scene") != null &&
      !Integer.valueOf(3).equals(previous.get().get("traceRevision"))
    ) data.put(
      "legacyPosition",
      Map.of(
        "step",
        previous.get().getOrDefault("step", 0),
        "section",
        previous.get().getOrDefault("section", "idea"),
        "revision",
        2
      )
    );
    else if (
      previous.isPresent() && previous.get().containsKey("legacyPosition")
    ) data.put("legacyPosition", previous.get().get("legacyPosition"));
    data.put("version", 1);
    data.put(
      "traceRevision",
      context.traceRevision() == null ? 2 : context.traceRevision()
    );
    data.put("lesson", lesson);
    if (context.scene() != null) data.put("scene", context.scene().toMap());
    data.put("step", context.step());
    data.put("section", context.section());
    data.put("codeRevision", Objects.toString(context.codeRevision(), ""));
    data.put("updatedAt", Instant.now().toString());
    var saved = store.put(
      "study-" + user + "-" + lesson,
      "study-context",
      user,
      data
    );
    progress.update(
      user,
      Map.of("resumeLesson", lesson, "resumeStep", context.step())
    );
    return saved;
  }

  @GetMapping("/study-context/{lesson}")
  public Map<String, Object> get(
    Authentication auth,
    @PathVariable String lesson
  ) {
    return store.owned(
      "study-" + AuthController.user(auth) + "-" + lesson,
      AuthController.user(auth)
    );
  }
}
