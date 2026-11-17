package com.oneonone;

import java.util.*;
import org.springframework.web.bind.annotation.*;

/** Public, read-only question bank. External questions are metadata and links; they open on their own site. */
@RestController
@RequestMapping("/api/v1/bank")
public class BankController {

  final BankService bank;

  public BankController(BankService bank) {
    this.bank = bank;
  }

  @GetMapping
  public Map<String, Object> search(
    @RequestParam(defaultValue = "") String q,
    @RequestParam(defaultValue = "") String source,
    @RequestParam(defaultValue = "") String difficulty,
    @RequestParam(defaultValue = "") String topic,
    @RequestParam(defaultValue = "") String company,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "25") int size,
    @RequestParam(defaultValue = "relevance") String sort
  ) {
    return bank.search(q, source, difficulty, topic, company, page, size, sort);
  }

  @GetMapping("/item/{id}")
  public Map<String, Object> item(@PathVariable String id) {
    return bank.external(id).orElseThrow(() -> new org.springframework.web.server.ResponseStatusException(org.springframework.http.HttpStatus.NOT_FOUND));
  }

  @GetMapping("/topics")
  public List<String> topics() {
    return bank.topics();
  }

  @GetMapping("/companies")
  public List<Map<String, Object>> companies() {
    return bank.companies();
  }
}
