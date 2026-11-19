package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import org.junit.jupiter.api.Test;

/** Groq speaks the OpenAI chat format; the tutor builds Gemini-shaped requests. This checks the translation. */
class GroqChatTest {

  @Test
  @SuppressWarnings("unchecked")
  void aGeminiRequestBecomesAnOpenAiChatRequest() {
    var gemini = Map.<String, Object>of(
      "systemInstruction", Map.of("parts", List.of(Map.of("text", "Teach gently."))),
      "contents", List.of(
        Map.of("role", "user", "parts", List.of(Map.of("text", "What is a heap?"))),
        Map.of("role", "model", "parts", List.of(Map.of("text", "A tree with an order rule."))),
        Map.of("role", "user", "parts", List.of(Map.of("text", "Show me."), Map.of("text", " Briefly.")))
      ),
      "generationConfig", Map.of("temperature", 0.2, "maxOutputTokens", 900, "responseMimeType", "application/json",
        "responseJsonSchema", Map.of("type", "object"), "thinkingConfig", Map.of("thinkingLevel", "LOW"))
    );
    var chat = GroqChat.request(gemini, "openai/gpt-oss-120b", false);
    assertEquals("openai/gpt-oss-120b", chat.get("model"));
    assertEquals(0.2, chat.get("temperature"));
    assertEquals(900, chat.get("max_completion_tokens"));
    assertEquals(Map.of("type", "json_object"), chat.get("response_format"));
    var messages = (List<Map<String, Object>>) chat.get("messages");
    assertEquals(List.of("system", "user", "assistant", "user"), messages.stream().map(m -> m.get("role")).toList());
    assertTrue(messages.getFirst().get("content").toString().startsWith("Teach gently."));
    assertTrue(messages.getFirst().get("content").toString().contains("JSON"), "json mode needs the word JSON and the schema in the prompt");
    assertEquals("Show me. Briefly.", messages.getLast().get("content"));
    assertFalse(chat.containsKey("stream"));
    assertEquals(true, GroqChat.request(gemini, "m", true).get("stream"));
  }

  @Test
  void repliesAndStreamChunksAreReadBack() {
    assertEquals("{\"text\":\"hi\"}", GroqChat.text(Map.of("choices", List.of(Map.of("message", Map.of("content", "{\"text\":\"hi\"}"))))));
    assertEquals("", GroqChat.text(Map.of("choices", List.of())));
    assertEquals("He", GroqChat.delta(Map.of("choices", List.of(Map.of("delta", Map.of("content", "He"))))));
    assertEquals("", GroqChat.delta(Map.of("choices", List.of(Map.of("delta", Map.of())))));
  }
}
