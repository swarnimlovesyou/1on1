package com.oneonone;

import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class ContentSeed implements CommandLineRunner {

  final Store s;
  final PasswordEncoder p;

  @Value("${app.seed-demo}")
  boolean demo;

  @Value("${app.admin-email}")
  String adminEmail;

  @Value("${app.admin-password}")
  String adminPassword;

  public ContentSeed(Store s, PasswordEncoder p) {
    this.s = s;
    this.p = p;
  }

  @Override
  public void run(String... args) throws Exception {
    var data = s.decode(
      new String(
        new ClassPathResource("content.json").getInputStream().readAllBytes(),
        java.nio.charset.StandardCharsets.UTF_8
      )
    );
    Set<String> seeded = new HashSet<>();
    for (String key : List.of("lessons", "problems", "paths"))
      for (var row : Store.items(data.get(key))) {
        String id = row.get("id").toString();
        seeded.add(id);
        if (
          s.find(id).isEmpty() || !Boolean.TRUE.equals(s.get(id).get("edited"))
        ) s.put(id, row.get("kind").toString(), "public", row);
      }
    for (var existing : s.list("problem", "public"))
      if (
        !seeded.contains(existing.get("id")) &&
        !Boolean.TRUE.equals(existing.get("edited"))
      ) {
        existing.put("published", false);
        s.put(existing.get("id").toString(), "problem", "public", existing);
      }
    if (
      !adminEmail.isBlank() &&
      adminPassword.length() >= 12 &&
      s.db
        .queryForList(
          "select id from members where email=?",
          adminEmail.toLowerCase(Locale.ROOT)
        )
        .isEmpty()
    ) {
      s.db.update(
        "insert into members(id,email,name,password,role) values(?,?,?,?,?)",
        UUID.randomUUID().toString(),
        adminEmail.toLowerCase(Locale.ROOT),
        "Content Editor",
        p.encode(adminPassword),
        "ADMIN"
      );
    }
    if (
      demo &&
      s.db
        .queryForList("select id from members where email='demo@1on1.local'")
        .isEmpty()
    ) s.db.update(
      "insert into members(id,email,name,password,role) values(?,?,?,?,?)",
      "demo-student",
      "demo@1on1.local",
      "Alex Morgan",
      p.encode("learnwith1on1"),
      "STUDENT"
    );
  }
}
