package com.oneonone;

import jakarta.servlet.http.*;
import java.security.*;
import java.time.*;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

  final Store store;
  final PasswordEncoder encoder;
  final JavaMailSender mail;

  @Value("${app.admin-email}")
  String admin;

  @Value("${app.base-url}")
  String base;

  public AuthController(Store s, PasswordEncoder p, JavaMailSender m) {
    store = s;
    encoder = p;
    mail = m;
  }

  static String user(Authentication a) {
    if (
      a == null || !a.isAuthenticated() || a.getName().equals("anonymousUser")
    ) throw new ResponseStatusException(
      HttpStatus.UNAUTHORIZED,
      "Sign in to continue."
    );
    return a.getName();
  }

  Map<String, Object> member(String id) {
    return store.db.queryForMap(
      "select id,email,name,role from members where id=?",
      id
    );
  }

  @GetMapping("/session")
  public Map<String, Object> session(Authentication a, HttpServletRequest req) {
    CsrfToken token = (CsrfToken) req.getAttribute(CsrfToken.class.getName());
    var r = new LinkedHashMap<String, Object>();
    r.put("csrf", token.getToken());
    r.put(
      "user",
      a == null || a.getName().equals("anonymousUser")
        ? null
        : member(a.getName())
    );
    return r;
  }

  @PostMapping("/register")
  public Map<String, Object> register(
    @RequestBody Map<String, Object> b,
    HttpServletRequest q,
    HttpServletResponse r
  ) {
    String email = Store.text(b, "email", "").strip().toLowerCase(Locale.ROOT),
      name = Store.text(b, "name", "").strip(),
      password = Store.text(b, "password", "");
    if (
      !email.matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$") ||
      email.length() > 254 ||
      name.isBlank() ||
      name.length() > 100 ||
      password.length() < 8 ||
      password.length() > 72
    ) throw new IllegalArgumentException(
      "Use a name, valid email, and password of 8–72 characters."
    );
    if (
      !store.db
        .queryForList("select id from members where email=?", email)
        .isEmpty()
    ) throw new IllegalArgumentException(
      "An account with this email already exists."
    );
    String id = UUID.randomUUID().toString(),
      role = "STUDENT";
    store.db.update(
      "insert into members(id,email,name,password,role) values(?,?,?,?,?)",
      id,
      email,
      name,
      encoder.encode(password),
      role
    );
    loginAs(id, role, q, r);
    return member(id);
  }

  @PostMapping("/login")
  public Map<String, Object> login(
    @RequestBody Map<String, Object> b,
    HttpServletRequest q,
    HttpServletResponse r
  ) {
    String email = Store.text(b, "email", "").strip().toLowerCase(Locale.ROOT);
    var users = store.db.queryForList(
      "select * from members where email=?",
      email
    );
    if (
      users.isEmpty() ||
      !encoder.matches(
        Store.text(b, "password", ""),
        users.getFirst().get("password").toString()
      )
    ) throw new ResponseStatusException(
      HttpStatus.UNAUTHORIZED,
      "Email or password is incorrect."
    );
    var u = users.getFirst();
    loginAs(u.get("id").toString(), u.get("role").toString(), q, r);
    return member(u.get("id").toString());
  }

  void loginAs(
    String id,
    String role,
    HttpServletRequest q,
    HttpServletResponse r
  ) {
    if (q.getSession(false) != null) q.changeSessionId();
    var context = SecurityContextHolder.createEmptyContext();
    context.setAuthentication(
      new UsernamePasswordAuthenticationToken(
        id,
        null,
        List.of(new SimpleGrantedAuthority("ROLE_" + role))
      )
    );
    SecurityContextHolder.setContext(context);
    new HttpSessionSecurityContextRepository().saveContext(context, q, r);
  }

  @PostMapping("/logout")
  public Map<String, Object> logout(HttpServletRequest q) {
    q.getSession().invalidate();
    SecurityContextHolder.clearContext();
    return Map.of("ok", true);
  }

  @PostMapping("/request-reset")
  public Map<String, Object> requestReset(@RequestBody Map<String, Object> b) {
    var users = store.db.queryForList(
      "select id,email from members where email=?",
      Store.text(b, "email", "").strip().toLowerCase(Locale.ROOT)
    );
    if (!users.isEmpty()) {
      String token = UUID.randomUUID() + UUID.randomUUID().toString();
      var u = users.getFirst();
      store.db.update(
        "insert into reset_tokens values(?,?,?)",
        hash(token),
        u.get("id"),
        java.sql.Timestamp.from(Instant.now().plusSeconds(1800))
      );
      try {
        var msg = new SimpleMailMessage();
        msg.setTo(u.get("email").toString());
        msg.setFrom("noreply@1on1.app");
        msg.setSubject("Reset your 1on1 password");
        msg.setText(
          "Reset your password within 30 minutes: " +
            base +
            "/reset-password?token=" +
            token
        );
        mail.send(msg);
      } catch (Exception ignored) {
        store.db.update(
          "delete from reset_tokens where token_hash=?",
          hash(token)
        );
      }
    }
    return Map.of(
      "message",
      "If that account exists and email is available, a reset link will arrive shortly."
    );
  }

  @Transactional
  @PostMapping("/reset-password")
  public Map<String, Object> reset(@RequestBody Map<String, Object> b) {
    String password = Store.text(b, "password", "");
    if (
      password.length() < 8 || password.length() > 72
    ) throw new IllegalArgumentException("Use 8–72 characters.");
    var rows = store.db.queryForList(
      "select member_id from reset_tokens where token_hash=? and expires_at>CURRENT_TIMESTAMP",
      hash(Store.text(b, "token", ""))
    );
    if (rows.isEmpty()) throw new IllegalArgumentException(
      "This reset link has expired. Request another."
    );
    store.db.update(
      "update members set password=? where id=?",
      encoder.encode(password),
      rows.getFirst().get("member_id")
    );
    store.db.update(
      "delete from reset_tokens where member_id=?",
      rows.getFirst().get("member_id")
    );
    return Map.of("ok", true);
  }

  String hash(String value) {
    try {
      return HexFormat.of().formatHex(
        MessageDigest.getInstance("SHA-256").digest(
          value.getBytes(java.nio.charset.StandardCharsets.UTF_8)
        )
      );
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
  }
}
