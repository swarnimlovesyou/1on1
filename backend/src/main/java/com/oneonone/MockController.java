package com.oneonone;

import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** Timed mock assessments for the signed-in learner. */
@RestController
@RequestMapping("/api/v1/mocks")
public class MockController {

  final MockService mocks;

  public MockController(MockService mocks) {
    this.mocks = mocks;
  }

  /** {size: 2|3, minutes: 60|90, style: "mixed" | company name} */
  @PostMapping
  public Map<String, Object> start(Authentication a, @RequestBody Map<String, Object> b) {
    return mocks.start(
      AuthController.user(a),
      b.get("size") instanceof Number n ? n.intValue() : 0,
      b.get("minutes") instanceof Number m ? m.intValue() : 0,
      Store.text(b, "style", "mixed")
    );
  }

  @GetMapping
  public List<Map<String, Object>> list(Authentication a) {
    return mocks.list(AuthController.user(a));
  }

  @GetMapping("/{id}")
  public Map<String, Object> view(Authentication a, @PathVariable String id) {
    return mocks.view(AuthController.user(a), id);
  }

  @PostMapping("/{id}/finish")
  public Map<String, Object> finish(Authentication a, @PathVariable String id) {
    return mocks.finish(AuthController.user(a), id);
  }

  /** {kind: "tab" | "fullscreen"} */
  @PostMapping("/{id}/signals")
  public Map<String, Object> signal(Authentication a, @PathVariable String id, @RequestBody Map<String, Object> b) {
    return mocks.signal(AuthController.user(a), id, Store.text(b, "kind", ""));
  }
}
