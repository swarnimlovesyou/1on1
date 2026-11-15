package com.oneonone;

import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;
import tools.jackson.databind.ObjectMapper;

@Component
public class Store {

  public final JdbcTemplate db;
  public final ObjectMapper json = new ObjectMapper();

  public Store(JdbcTemplate db) {
    this.db = db;
  }

  public String encode(Object value) {
    return json.writeValueAsString(value);
  }

  @SuppressWarnings("unchecked")
  public Map<String, Object> decode(String value) {
    return json.readValue(value, LinkedHashMap.class);
  }

  public List<Map<String, Object>> list(String kind, String owner) {
    return db.query(
      "select body from documents where kind=? and owner_id=? order by id",
      (r, i) -> decode(r.getString(1)),
      kind,
      owner
    );
  }

  public List<Map<String, Object>> all(String kind) {
    return db.query(
      "select body from documents where kind=? order by id",
      (r, i) -> decode(r.getString(1)),
      kind
    );
  }

  public Optional<Map<String, Object>> find(String id) {
    return db
      .query(
        "select body from documents where id=?",
        (r, i) -> decode(r.getString(1)),
        id
      )
      .stream()
      .findFirst();
  }

  public Map<String, Object> get(String id) {
    return find(id).orElseThrow(() ->
      new ResponseStatusException(
        HttpStatus.NOT_FOUND,
        "This item could not be found."
      )
    );
  }

  public synchronized Map<String, Object> put(
    String id,
    String kind,
    String owner,
    Map<String, Object> value
  ) {
    var data = new LinkedHashMap<>(value);
    data.put("id", id);
    int updated = db.update(
      "update documents set body=?,updated_at=CURRENT_TIMESTAMP where id=? and owner_id=?",
      encode(data),
      id,
      owner
    );
    if (updated == 0) {
      if (find(id).isPresent()) throw new ResponseStatusException(
        HttpStatus.FORBIDDEN
      );
      db.update(
        "insert into documents(id,kind,owner_id,body) values(?,?,?,?)",
        id,
        kind,
        owner,
        encode(data)
      );
    }
    return data;
  }

  public void delete(String id, String owner) {
    db.update("delete from documents where id=? and owner_id=?", id, owner);
  }

  public Map<String, Object> owned(String id, String owner) {
    return db
      .query(
        "select body from documents where id=? and owner_id=?",
        (r, i) -> decode(r.getString(1)),
        id,
        owner
      )
      .stream()
      .findFirst()
      .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
  }

  public synchronized void quota(String user, String kind, int max) {
    String day = java.time.LocalDate.now(java.time.ZoneOffset.UTC).toString();
    Integer global = db.queryForObject(
      "select coalesce(sum(count),0) from daily_usage where usage_day=? and kind=?",
      Integer.class,
      day,
      kind
    );
    int ceiling = kind.equals("AI") ? 300 : 2000;
    if (global != null && global >= ceiling) throw new ResponseStatusException(
      HttpStatus.TOO_MANY_REQUESTS,
      "Today's shared service limit has been reached. Your saved work remains available."
    );
    var rows = db.queryForList(
      "select count from daily_usage where member_id=? and usage_day=? and kind=?",
      Integer.class,
      user,
      day,
      kind
    );
    int count = rows.isEmpty() ? 0 : rows.getFirst();
    if (count >= max) throw new ResponseStatusException(
      HttpStatus.TOO_MANY_REQUESTS,
      "Your daily " + kind + " limit is reached. Try again tomorrow."
    );
    if (rows.isEmpty()) db.update(
      "insert into daily_usage values(?,?,?,1)",
      user,
      day,
      kind
    );
    else db.update(
      "update daily_usage set count=count+1 where member_id=? and usage_day=? and kind=?",
      user,
      day,
      kind
    );
  }

  public static String text(Map<String, Object> m, String k, String fallback) {
    Object v = m.get(k);
    return v == null ? fallback : String.valueOf(v);
  }

  @SuppressWarnings("unchecked")
  public static List<Map<String, Object>> items(Object v) {
    return v instanceof List<?> ? (List<Map<String, Object>>) v : List.of();
  }

  @SuppressWarnings("unchecked")
  public static List<String> strings(Object v) {
    return v instanceof List<?> l
      ? l.stream().map(String::valueOf).toList()
      : List.of();
  }
}
