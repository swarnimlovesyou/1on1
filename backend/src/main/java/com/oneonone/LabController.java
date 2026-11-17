package com.oneonone;

import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** Public performance lab: step counts of the Java teaching traces over growing inputs. */
@RestController
@RequestMapping("/api/v1/lab")
public class LabController {

  final LabService lab;

  public LabController(LabService lab) {
    this.lab = lab;
  }

  @GetMapping("/{algorithm}")
  public Map<String, Object> measure(@PathVariable String algorithm) {
    return lab.measure(algorithm);
  }
}
