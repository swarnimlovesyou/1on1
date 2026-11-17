package com.oneonone;

import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** Public list of upcoming programming contests. */
@RestController
@RequestMapping("/api/v1/contests")
public class ContestController {

  final ContestService contests;

  public ContestController(ContestService contests) {
    this.contests = contests;
  }

  @GetMapping
  public Map<String, Object> upcoming() {
    return contests.upcoming();
  }
}
