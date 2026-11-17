package com.oneonone;

import java.util.Map;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** Public aptitude and reasoning drills; a signed-in answer logs one practice event per topic per day. */
@RestController
@RequestMapping("/api/v1/drills")
public class DrillController {

  final DrillService drills;

  public DrillController(DrillService drills) {
    this.drills = drills;
  }

  @GetMapping("/{topic}/next")
  public Map<String, Object> next(@PathVariable String topic, @RequestParam(required = false) String seed) {
    return drills.next(topic, seed);
  }

  @PostMapping("/{topic}/answer")
  public Map<String, Object> answer(Authentication auth, @PathVariable String topic, @RequestBody Map<String, Object> body) {
    String user = auth == null || auth instanceof AnonymousAuthenticationToken ? null : AuthController.user(auth);
    var answer = body.get("answer");
    return drills.answer(user, topic, body.get("seed"), answer == null ? null : answer.toString());
  }
}
