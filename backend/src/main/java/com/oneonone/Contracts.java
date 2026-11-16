package com.oneonone;

import java.util.*;

/** Shared wire contracts. Algorithm state is computed by Java, never by the renderer. */
public final class Contracts {

  private Contracts() {}

  public static String codeRevision(String language, String code) {
    try {
      return HexFormat.of().formatHex(
        java.security.MessageDigest.getInstance("SHA-256").digest(
          (language + "\n" + code).getBytes(
            java.nio.charset.StandardCharsets.UTF_8
          )
        )
      );
    } catch (java.security.NoSuchAlgorithmException error) {
      throw new IllegalStateException(error);
    }
  }

  @com.fasterxml.jackson.annotation.JsonInclude(
    com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL
  )
  public record SceneRequest(
    String algorithm,
    String input,
    Integer target,
    String words,
    Long seed
  ) {
    public Map<String, Object> toMap() {
      var out = new LinkedHashMap<String, Object>();
      out.put("algorithm", algorithm == null ? "sliding-window" : algorithm);
      out.put("input", input == null ? "2,1,5,1,3,2" : input);
      out.put("target", target == null ? 3 : target);
      if (words != null) out.put("words", words);
      out.put("seed", seed == null ? 42L : seed);
      return out;
    }
  }

  public record Entity(String id, int value, int position, String role) {}

  public record Operation(
    String kind,
    List<String> entityIds,
    Map<String, Object> details
  ) {}

  public record TreeNode(String id, int value, TreeNode left, TreeNode right) {}

  public record GraphEdge(int from, int to, int weight) {}

  public record Link(String from, String to) {}

  @com.fasterxml.jackson.annotation.JsonInclude(
    com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL
  )
  public record TraceStep(
    String id,
    List<Integer> array,
    List<Entity> entities,
    List<Integer> active,
    Map<String, Object> variables,
    String text,
    int line,
    Operation operation,
    TreeNode tree,
    List<String> words,
    List<String> topics,
    Integer vertexCount,
    List<GraphEdge> edges,
    String activeEdge,
    List<Link> links,
    String head,
    Map<String, Object> visual
  ) {}

  public record ExecutionTrace(
    int version,
    String algorithm,
    String family,
    SceneRequest input,
    List<TraceStep> steps,
    TraceStep result,
    Integer revision,
    List<String> code
  ) {
    public static ExecutionTrace from(Map<String, Object> trace) {
      return new tools.jackson.databind.ObjectMapper().convertValue(
        trace,
        ExecutionTrace.class
      );
    }
  }

  public record LessonBlock(
    String id,
    String kind,
    String title,
    String text,
    List<String> lines
  ) {}

  /** hintUsed: the learner opened the hint before answering (optional; a success after a miss is also hinted). */
  public record AttemptRequest(Object answer, String requestId, Boolean hintUsed) {
    public AttemptRequest(Object answer, String requestId) {
      this(answer, requestId, null);
    }
  }

  public record AttemptResult(
    String id,
    String challengeId,
    String kind,
    boolean correct,
    String feedback,
    String explanation,
    boolean saved
  ) {}

  public record StudyContext(
    int version,
    String lesson,
    SceneRequest scene,
    int step,
    String section,
    String codeRevision,
    Integer traceRevision
  ) {
    public StudyContext(
      int version,
      String lesson,
      SceneRequest scene,
      int step,
      String section,
      String codeRevision
    ) {
      this(version, lesson, scene, step, section, codeRevision, null);
    }
  }
}
