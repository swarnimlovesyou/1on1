package com.oneonone;

import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** Signed-in quiz-style mock assessment: start one, then submit it once for a graded review. */
@RestController
@RequestMapping("/api/v1/quizzes")
public class QuizController {

  final QuizService quizzes;

  public QuizController(QuizService quizzes) {
    this.quizzes = quizzes;
  }

  @PostMapping
  public Map<String, Object> start(Authentication a, @RequestBody Map<String, Object> body) {
    return quizzes.start(AuthController.user(a), body);
  }

  @PostMapping("/{id}/submit")
  public Map<String, Object> submit(Authentication a, @PathVariable String id, @RequestBody Map<String, Object> body) {
    return quizzes.submit(AuthController.user(a), id, body);
  }
}
