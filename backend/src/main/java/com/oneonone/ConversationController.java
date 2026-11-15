package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.util.*;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/** Private tutor transcripts are study records, never learning achievements. */
@RestController
@RequestMapping("/api/v1/conversations")
public class ConversationController {

  final Store store;
  final TraceEngine traces;

  public ConversationController(Store store, TraceEngine traces) {
    this.store = store;
    this.traces = traces;
  }

  private String id(String user, String context) {
    if (
      !context.matches("[A-Za-z0-9_-]{1,128}")
    ) throw new IllegalArgumentException("Choose a valid study context.");
    return (
      "conversation-" +
      UUID.nameUUIDFromBytes(
        (user + ":" + context).getBytes(StandardCharsets.UTF_8)
      )
    );
  }

  @GetMapping("/{context}")
  public Map<String, Object> get(
    Authentication auth,
    @PathVariable String context
  ) {
    return store
      .find(id(AuthController.user(auth), context))
      .orElse(Map.of("context", context, "messages", List.of()));
  }

  @PutMapping("/{context}")
  public Map<String, Object> save(
    Authentication auth,
    @PathVariable String context,
    @RequestBody Map<String, Object> body
  ) {
    String user = AuthController.user(auth);
    var messages = Store.items(body.get("messages"));
    if (
      messages.size() > 20 || store.encode(messages).length() > 120000
    ) throw new IllegalArgumentException(
      "Keep at most 20 bounded messages in this conversation."
    );
    var clean = new ArrayList<Map<String, Object>>();
    for (var message : messages) {
      String role = Store.text(message, "role", ""),
        text = Store.text(message, "text", "");
      if (
        !Set.of("you", "tutor").contains(role) || text.length() > 16000
      ) throw new IllegalArgumentException("Invalid conversation message.");
      var item = new LinkedHashMap<String, Object>();
      item.put("role", role);
      item.put("text", text);
      if (message.get("scene") instanceof Map<?, ?> scene) {
        traces.trace((Map<String, Object>) scene);
        item.put("scene", scene);
      }
      clean.add(item);
    }
    return store.put(
      id(user, context),
      "conversation",
      user,
      Map.of("context", context, "messages", clean)
    );
  }
}
