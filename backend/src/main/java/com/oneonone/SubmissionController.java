package com.oneonone;

import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/submissions")
public class SubmissionController {

  final ExecutionService e;
  final Store s;

  public SubmissionController(ExecutionService e, Store s) {
    this.e = e;
    this.s = s;
  }

  @PostMapping
  public Map<String, Object> submit(
    Authentication a,
    @RequestBody Map<String, Object> b
  ) {
    return e.submit(AuthController.user(a), b);
  }

  @GetMapping("/{id}")
  public Map<String, Object> get(Authentication a, @PathVariable String id) {
    return ExecutionService.visible(s.owned(id, AuthController.user(a)));
  }
}
