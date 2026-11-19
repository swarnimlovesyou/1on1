package com.oneonone;

import java.util.*;

/**
 * Translates the tutor's Gemini-shaped requests to Groq's OpenAI-compatible chat format and reads replies back, so
 * every prompt, schema and safety rule stays written once. Gemini-only settings (thinking levels) are dropped.
 */
final class GroqChat {

  static final String URL = "https://api.groq.com/openai/v1/chat/completions";

  private GroqChat() {}

  static Map<String, Object> request(Map<String, Object> gemini, String model, boolean stream) {
    var messages = new ArrayList<Map<String, Object>>();
    var config = gemini.get("generationConfig") instanceof Map<?, ?> m ? m : Map.of();
    boolean json = "application/json".equals(config.get("responseMimeType"));
    String system = gemini.get("systemInstruction") instanceof Map<?, ?> si ? join(si.get("parts")) : "";
    if (json) // JSON mode requires the word JSON in the prompt; the schema keeps the reply in the shape the tutor parses
      system += "\n\nReply with one JSON object only" + (config.get("responseJsonSchema") != null ? ", matching this JSON schema: " + config.get("responseJsonSchema") : ".");
    if (!system.isBlank()) messages.add(Map.of("role", "system", "content", system));
    for (var c : Store.items(gemini.get("contents")))
      messages.add(Map.of("role", "model".equals(c.get("role")) ? "assistant" : "user", "content", join(c.get("parts"))));
    var out = new LinkedHashMap<String, Object>();
    out.put("model", model);
    out.put("messages", messages);
    if (config.get("temperature") != null) out.put("temperature", config.get("temperature"));
    if (config.get("maxOutputTokens") != null) out.put("max_completion_tokens", config.get("maxOutputTokens"));
    if (json && !stream) out.put("response_format", Map.of("type", "json_object"));
    if (stream) out.put("stream", true);
    return out;
  }

  static String join(Object parts) {
    var sb = new StringBuilder();
    for (var p : Store.items(parts)) if (p.get("text") != null) sb.append(p.get("text"));
    return sb.toString();
  }

  @SuppressWarnings("unchecked")
  static String text(Map<String, Object> response) {
    var choices = Store.items(response.get("choices"));
    if (choices.isEmpty() || !(choices.getFirst().get("message") instanceof Map<?, ?> m)) return "";
    return String.valueOf(((Map<String, Object>) m).getOrDefault("content", ""));
  }

  @SuppressWarnings("unchecked")
  static String delta(Map<String, Object> chunk) {
    var choices = Store.items(chunk.get("choices"));
    if (choices.isEmpty() || !(choices.getFirst().get("delta") instanceof Map<?, ?> d)) return "";
    Object content = ((Map<String, Object>) d).get("content");
    return content == null ? "" : content.toString();
  }
}
