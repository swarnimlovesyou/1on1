package com.oneonone;

import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** The guided coding coach for one problem. Study records only; credit stays with official runs. */
@RestController
@RequestMapping("/api/v1/coach")
public class CoachController {

  final CoachService coach;

  public CoachController(CoachService coach) {
    this.coach = coach;
  }

  @GetMapping("/{problem}")
  public Map<String, Object> view(Authentication a, @PathVariable String problem, @RequestParam(defaultValue = "java") String language) {
    return coach.view(AuthController.user(a), problem, language);
  }

  /** {language, approach, invariant, example} */
  @PutMapping("/{problem}/plan")
  public Map<String, Object> plan(Authentication a, @PathVariable String problem, @RequestBody Map<String, Object> body) {
    return coach.savePlan(AuthController.user(a), problem, body);
  }

  /** {language, want?: "solution", confirm?: true} */
  @PostMapping("/{problem}/nudge")
  public Map<String, Object> nudge(Authentication a, @PathVariable String problem, @RequestBody Map<String, Object> body) {
    return coach.nudge(AuthController.user(a), problem, body);
  }

  /** {language, complexity, transfer}; only after an accepted official run */
  @PutMapping("/{problem}/reflection")
  public Map<String, Object> reflection(Authentication a, @PathVariable String problem, @RequestBody Map<String, Object> body) {
    return coach.saveReflection(AuthController.user(a), problem, body);
  }
}
