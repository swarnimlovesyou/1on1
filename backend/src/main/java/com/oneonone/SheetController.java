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
  final BankService bank;
  private volatile List<Map<String, Object>> sheets;
  private volatile Set<String> itemIds;

  SheetController(Store store) {
    this(store, null);
  }

  @org.springframework.beans.factory.annotation.Autowired
  public SheetController(Store store, BankService bank) {
    this.store = store;
    this.bank = bank;
  }

  /** The five companies that reported a question most often, from the bank's community data. */
  List<Map<String, Object>> topCompanies(String id) {
    if (bank == null) return List.of();
    return bank.external(id)
      .map(r -> r.get("companies") instanceof Map<?, ?> m ? m : Map.of())
      .orElse(Map.of())
      .entrySet()
      .stream()
      .filter(e -> e.getValue() instanceof Number)
      .sorted((a, b) -> Integer.compare(((Number) b.getValue()).intValue(), ((Number) a.getValue()).intValue()))
      .limit(5)
      .map(e -> (Map<String, Object>) new LinkedHashMap<String, Object>(Map.of("name", e.getKey().toString(), "count", e.getValue())))
      .toList();
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
    var sheet = all().stream().filter(s -> id.equals(s.get("id"))).findFirst()
      .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "That sheet doesn't exist."));
    if (bank == null) return sheet;
    var out = new LinkedHashMap<>(sheet);
    out.put("items", Store.items(sheet.get("items")).stream().map(item -> {
      var row = new LinkedHashMap<>(item);
      var companies = topCompanies(item.get("id").toString());
      if (!companies.isEmpty()) row.put("companies", companies);
      return (Map<String, Object>) row;
    }).toList());
    return out;
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

  /** Adds every id that is on a sheet and not yet ticked; returns how many were added. */
  synchronized int tickAll(String user, Collection<String> ids) {
    all();
    var list = new ArrayList<>(Store.strings(ticks(user).get("done")));
    int added = 0;
    for (String id : ids) if (itemIds.contains(id) && !list.contains(id)) {
      list.add(id);
      added++;
    }
    if (added > 0) store.put("sheet-ticks-" + user, "sheet-ticks", user, Map.of("done", list));
    return added;
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
