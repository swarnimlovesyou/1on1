package com.oneonone;

import java.io.IOException;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/** The learner's own PDFs, cited search and answers over them, and revision cards. Signed-in only. */
@RestController
@RequestMapping("/api/v1/notebook")
public class NotebookController {

  final NotebookService notebook;

  public NotebookController(NotebookService notebook) {
    this.notebook = notebook;
  }

  @GetMapping("/sources")
  public List<Map<String, Object>> sources(Authentication a) {
    return notebook.sources(AuthController.user(a));
  }

  @PostMapping(value = "/sources", consumes = "multipart/form-data")
  @ResponseStatus(HttpStatus.CREATED)
  public Map<String, Object> add(Authentication a, @RequestParam("file") MultipartFile file) throws IOException {
    return notebook.ingest(AuthController.user(a), file.getOriginalFilename(), file.getBytes());
  }

  @DeleteMapping("/sources/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void delete(Authentication a, @PathVariable String id) {
    notebook.delete(AuthController.user(a), id);
  }

  /** {query, sourceIds?}: BM25 passages from the selected sources (all of them when none are given). */
  @PostMapping("/search")
  public List<Map<String, Object>> search(Authentication a, @RequestBody Map<String, Object> b) {
    return notebook
      .search(AuthController.user(a), Store.text(b, "query", ""), Store.strings(b.get("sourceIds")), 8)
      .stream()
      .map(NotebookService::view)
      .toList();
  }

  /** {question, sourceIds?}: an answer citing file and page, or a plain "your sources don't say". */
  @PostMapping("/ask")
  public Map<String, Object> ask(Authentication a, @RequestBody Map<String, Object> b) {
    return notebook.ask(AuthController.user(a), Store.text(b, "question", ""), Store.strings(b.get("sourceIds")));
  }

  @GetMapping("/cards")
  public List<Map<String, Object>> cards(Authentication a) {
    return notebook.cards(AuthController.user(a));
  }

  /** {sourceId, page?}: drafts up to six editable cards from that page or the whole source. */
  @PostMapping("/cards/draft")
  public List<Map<String, Object>> draft(Authentication a, @RequestBody Map<String, Object> b) {
    Object page = b.get("page");
    return notebook.draftCards(AuthController.user(a), Store.text(b, "sourceId", ""), page == null ? null : Integer.valueOf(page.toString()));
  }

  @PutMapping("/cards/{id}")
  public Map<String, Object> edit(Authentication a, @PathVariable String id, @RequestBody Map<String, Object> b) {
    return notebook.editCard(AuthController.user(a), id, Store.text(b, "front", ""), Store.text(b, "back", ""));
  }

  /** {rating: again|hard|good|easy}: self-reported, kept apart from graded evidence. */
  @PostMapping("/cards/{id}/recall")
  public Map<String, Object> recall(Authentication a, @PathVariable String id, @RequestBody Map<String, Object> b) {
    return notebook.recall(AuthController.user(a), id, Store.text(b, "rating", ""));
  }

  @DeleteMapping("/cards/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void deleteCard(Authentication a, @PathVariable String id) {
    notebook.deleteCard(AuthController.user(a), id);
  }
}
