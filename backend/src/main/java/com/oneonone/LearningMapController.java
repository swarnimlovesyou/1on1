package com.oneonone;

import java.util.Map;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** The concept map, due reviews and next action; guests get the map without evidence. */
@RestController
@RequestMapping("/api/v1")
public class LearningMapController {

  final LearningMapService map;

  public LearningMapController(LearningMapService map) {
    this.map = map;
  }

  @GetMapping("/learning-map")
  public Map<String, Object> get(Authentication auth) {
    return map.map(auth == null || auth instanceof AnonymousAuthenticationToken ? null : AuthController.user(auth));
  }
}
