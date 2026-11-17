package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/** Curated sheets from openly licensed lists (sheets.json, built by import_questions.py); ticks are kept per learner. */
@RestController
@RequestMapping("/api/v1/sheets")
public class SheetController {

  final Store store;
  private volatile List<Map<String, Object>> sheets;
  private volatile Set<String> itemIds;

  public SheetController(Store store) {
    this.store = store;
  }

  List<Map<String, Object>> all() {
    if (sheets == null) try (var in = new ClassPathResource("sheets.json").getInputStream()) {
      var loaded = Store.items(store.decode("{\"s\":" + new String(in.readAllBytes(), StandardCharsets.UTF_8) + "}").get("s"));
      Set<String> ids = new HashSet<>();
      for (var s : loaded) for (var item : Store.items(s.get("items"))) ids.add(item.get("id").toString());
      itemIds = ids;
      sheets = loaded;
    } catch (java.io.IOException e) {
      throw new IllegalStateException("sheets.json is missing", e);
    }
    return sheets;
  }

  @GetMapping
  public List<Map<String, Object>> list() {
    return all().stream().map(s -> {
      var row = new LinkedHashMap<String, Object>();
      for (String key : List.of("id", "title", "summary", "credit")) row.put(key, s.get(key));
      row.put("count", Store.items(s.get("items")).size());
      return (Map<String, Object>) row;
    }).toList();
  }

  @GetMapping("/{id}")
  public Map<String, Object> sheet(@PathVariable String id) {
    return all().stream().filter(s -> id.equals(s.get("id"))).findFirst()
      .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "That sheet doesn't exist."));
  }

  @GetMapping("/ticks/mine")
  public Map<String, Object> myTicks(Authentication auth) {
    return ticks(AuthController.user(auth));
  }

  @PutMapping("/ticks/mine/{item}")
  public Map<String, Object> myTick(Authentication auth, @PathVariable String item, @RequestBody Map<String, Object> body) {
    return tick(AuthController.user(auth), item, body);
  }

  Map<String, Object> ticks(String user) {
    var doc = store.find("sheet-ticks-" + user);
    return Map.of("done", doc.map(d -> Store.strings(d.get("done"))).orElse(List.of()));
  }

  synchronized Map<String, Object> tick(String user, String item, Map<String, Object> body) {
    all();
    if (!itemIds.contains(item)) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That question is not on any sheet.");
    if (!(body.get("done") instanceof Boolean done)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Send done: true or false.");
    var list = new ArrayList<>(Store.strings(ticks(user).get("done")));
    list.remove(item);
    if (done) list.add(item);
    store.put("sheet-ticks-" + user, "sheet-ticks", user, Map.of("done", list));
    return Map.of("done", list);
  }
}
