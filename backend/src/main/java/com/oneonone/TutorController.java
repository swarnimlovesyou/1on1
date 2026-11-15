package com.oneonone;

import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/v1")
public class TutorController {

  final TutorService tutor;
  final ExecutionService execution;

  public TutorController(TutorService tutor, ExecutionService execution) {
    this.tutor = tutor;
    this.execution = execution;
  }

  @GetMapping("/system")
  public Map<String, Object> system() {
    return tutor.system();
  }

  @PostMapping("/system/check")
  public Map<String, Object> check() {
    return execution.probe();
  }

  @PostMapping("/tutor")
  public Map<String, Object> tutor(
    Authentication auth,
    @RequestBody Map<String, Object> body
  ) {
    return tutor.tutor(auth, body);
  }

  @PostMapping(value = "/tutor/stream", produces = "text/event-stream")
  public SseEmitter stream(
    Authentication auth,
    @RequestBody Map<String, Object> body
  ) {
    return tutor.stream(auth, body);
  }
}
