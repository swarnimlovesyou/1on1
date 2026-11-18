package com.oneonone;

import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** Public quiz-style mock assessment: start one, then submit it once for a graded review. */
@RestController
@RequestMapping("/api/v1/quizzes")
public class QuizController {

  final QuizService quizzes;

  public QuizController(QuizService quizzes) {
    this.quizzes = quizzes;
  }

  @PostMapping
  public Map<String, Object> start(@RequestBody Map<String, Object> body) {
    return quizzes.start(body);
  }

  @PostMapping("/{id}/submit")
  public Map<String, Object> submit(@PathVariable String id, @RequestBody Map<String, Object> body) {
    return quizzes.submit(id, body);
  }
}
