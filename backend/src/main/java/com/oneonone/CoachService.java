package com.oneonone;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

/**
 * Guided coding for one problem: the learner's own plan, a hint ladder grounded in their actual runs, and a
 * reflection after acceptance. A study record only: it never writes credit, mastery or attempts. Accepted
 * credit comes solely from ExecutionService grading an official run.
 */
@org.springframework.stereotype.Service
public class CoachService {

  static final Map<String, String> TRANSFER = Map.ofEntries(
    Map.entry("Arrays", "What changes if the values can be negative, or if the array is too large to keep in memory and arrives as a stream?"),
    Map.entry("Strings", "What changes if the text contains Unicode letters, or if upper and lower case must count as the same character?"),
    Map.entry("Sorting", "What changes if the input is already nearly sorted, or if equal values must keep their original order?"),
    Map.entry("Graphs", "What changes if the edges are undirected, or if each edge has a positive weight?"),
    Map.entry("Dynamic programming", "What changes if n grows to a million: which states do you still need to keep?"),
    Map.entry("Hashing", "What changes if you may use only O(1) extra memory?"),
    Map.entry("Trees", "What changes if the tree is very deep: does your approach still work without recursion?"),
    Map.entry("Stacks & queues", "What changes if the operations arrive in a stream and you must answer after each one?"),
    Map.entry("Recursion", "What changes if n is large enough that the call stack overflows?"),
    Map.entry("Heaps", "What changes if you need the k smallest values instead of one?"),
    Map.entry("Sliding window", "What changes if the window size is not fixed but limited by a condition?"),
    Map.entry("Probabilistic structures", "What changes if the input is ten times larger: does your count still fit the type you chose?")
  );
  static final String DEFAULT_TRANSFER = "What changes if the input is ten times larger, or contains the smallest values the constraints allow?";
  static final List<String> STAGES = List.of("plan", "code", "debug", "reflect", "done");

  final Store s;
  final ExecutionService execution;

  public CoachService(Store s, ExecutionService execution) {
    this.s = s;
    this.execution = execution;
  }

  String id(String user, String problem) {
    return "coach-" + UUID.nameUUIDFromBytes((user + ":" + problem).getBytes(StandardCharsets.UTF_8));
  }

  Map<String, Object> problem(String problem) {
    var p = s.owned(problem, "public");
    if (!p.containsKey("tests") || Boolean.FALSE.equals(p.get("published"))) throw new IllegalArgumentException("Choose a published practice problem.");
    return p;
  }

  static String language(String language) {
    if (!Set.of("java", "python", "cpp").contains(language)) throw new IllegalArgumentException("Choose Java, Python or C++.");
    return language;
  }

  Map<String, Object> session(String user, String problem) {
    return new LinkedHashMap<>(s.find(id(user, problem)).orElse(Map.of("problem", problem)));
  }

  boolean accepted(String user, String problem) {
    return s.db.queryForObject("select count(*) from solved_credits where member_id=? and problem_id=?", Integer.class, user, problem) > 0;
  }

  /** The newest official run, with the first failing row (hidden rows carry no input) and whether it is the current code. */
  Map<String, Object> latestRun(String user, String problem, String currentRevision) {
    var run = s.list("submission", user).stream()
      .filter(r -> problem.equals(r.get("problem")) && !Boolean.FALSE.equals(r.get("official")))
      .max(Comparator.comparing(r -> Instant.parse(Store.text(r, "createdAt", "1970-01-01T00:00:00Z"))))
      .orElse(null);
    if (run == null) return null;
    var out = new LinkedHashMap<String, Object>();
    out.put("id", run.get("id"));
    out.put("status", run.get("status"));
    out.put("createdAt", run.get("createdAt"));
    out.put("language", run.get("language"));
    String revision = Contracts.codeRevision(Store.text(run, "language", "java"), Store.text(run, "code", ""));
    out.put("codeRevision", revision);
    out.put("current", revision.equals(currentRevision));
    out.put("finished", !Set.of("QUEUED", "RUNNING").contains(Store.text(run, "status", "")));
    Store.items(run.get("results")).stream()
      .filter(row -> !"PASSED".equals(row.get("status")))
      .findFirst()
      .ifPresent(row -> {
        var failing = new LinkedHashMap<String, Object>();
        for (String k : List.of("index", "status", "public", "input", "expected", "actual", "message")) if (row.containsKey(k)) failing.put(k, row.get(k));
        out.put("failing", failing);
      });
    return out;
  }

  public Map<String, Object> view(String user, String problem, String language) {
    var p = problem(problem);
    language(language);
    var session = session(user, problem);
    var draft = s.find("draft-" + user + "-" + problem + "-" + language).orElse(null);
    String current = draft == null ? "" : Store.text(draft, "codeRevision", "");
    var run = latestRun(user, problem, current);
    boolean solved = accepted(user, problem);
    var plan = (Map<?, ?>) session.get("plan");
    String stage = solved
      ? (session.containsKey("reflection") ? "done" : "reflect")
      : plan == null
        ? "plan"
        : run != null && Boolean.TRUE.equals(run.get("finished")) && !"ACCEPTED".equals(run.get("status")) ? "debug" : "code";
    var out = new LinkedHashMap<String, Object>();
    out.put("problem", problem);
    out.put("language", language);
    out.put("stage", stage);
    out.put("steps", List.of(
      step("plan", "Plan your approach", plan != null),
      step("code", "Write a first version", draft != null),
      step("run", "Run it on the tests", run != null && Boolean.TRUE.equals(run.get("finished"))),
      step("fix", "Get it accepted", solved),
      step("reflect", "Reflect and transfer", session.containsKey("reflection"))
    ));
    out.put("plan", plan);
    out.put("codeRevision", current);
    out.put("latestRun", run);
    out.put("accepted", solved);
    out.put("nudges", Store.items(session.get("nudges")));
    out.put("solutionRevealed", session.containsKey("solutionRevealedAt"));
    out.put("reflection", session.get("reflection"));
    out.put("transfer", transfer(p));
    var runner = execution.status();
    // cached status only: unknown until the runner is first used, false once it has failed
    out.put("execution", execution.available() && (Boolean.TRUE.equals(runner.get("reachable")) || "not_checked".equals(runner.get("reason"))));
    return out;
  }

  static Map<String, Object> step(String key, String label, boolean done) {
    return Map.of("key", key, "label", label, "done", done);
  }

  static String transfer(Map<String, Object> p) {
    return Store.strings(p.get("topics")).stream().map(TRANSFER::get).filter(Objects::nonNull).findFirst().orElse(DEFAULT_TRANSFER);
  }

  static String bounded(String value, String name, int max) {
    String v = value == null ? "" : value.strip();
    if (v.isEmpty() || v.length() > max) throw new IllegalArgumentException("Write your " + name + " in up to " + max + " characters.");
    return v;
  }

  public Map<String, Object> savePlan(String user, String problem, Map<String, Object> body) {
    problem(problem);
    var session = session(user, problem);
    var plan = new LinkedHashMap<String, Object>();
    plan.put("approach", bounded(Store.text(body, "approach", ""), "approach", 1500));
    plan.put("invariant", bounded(Store.text(body, "invariant", ""), "invariant", 600));
    plan.put("example", bounded(Store.text(body, "example", ""), "worked example", 1000));
    plan.put("savedAt", Instant.now().toString());
    session.put("plan", plan);
    s.put(id(user, problem), "coach", user, session);
    return view(user, problem, language(Store.text(body, "language", "java")));
  }

  public Map<String, Object> saveReflection(String user, String problem, Map<String, Object> body) {
    problem(problem);
    if (!accepted(user, problem)) throw new ResponseStatusException(HttpStatus.CONFLICT, "Reflect once an official run is accepted.");
    var session = session(user, problem);
    session.put("reflection", Map.of(
      "complexity", bounded(Store.text(body, "complexity", ""), "complexity reflection", 800),
      "transfer", bounded(Store.text(body, "transfer", ""), "transfer answer", 1500),
      "savedAt", Instant.now().toString()
    ));
    s.put(id(user, problem), "coach", user, session);
    return view(user, problem, language(Store.text(body, "language", "java")));
  }

  /**
   * The next rung for the learner's current stage: one focused question, then the concrete evidence (the failing
   * case or the constraints), then the three authored hints, then honest options. A new run starts a new ladder,
   * so a learner is never asked the same question twice in a row. want=solution reveals the reference explicitly.
   */
  public Map<String, Object> nudge(String user, String problem, Map<String, Object> body) {
    var p = problem(problem);
    String language = language(Store.text(body, "language", "java"));
    var view = view(user, problem, language);
    var session = session(user, problem);
    var nudges = new ArrayList<>(Store.items(session.get("nudges")));
    String stage = view.get("stage").toString();
    var run = (Map<String, Object>) view.get("latestRun");
    var entry = new LinkedHashMap<String, Object>();
    entry.put("at", Instant.now().toString());
    entry.put("stage", stage);
    entry.put("codeRevision", view.get("codeRevision"));
    if ("solution".equals(Store.text(body, "want", ""))) {
      if (!Boolean.TRUE.equals(body.get("confirm"))) throw new IllegalArgumentException("Confirm that you want the worked solution.");
      var references = (Map<?, ?>) p.getOrDefault("references", Map.of("java", p.get("reference")));
      String shown = references.containsKey(language) ? language : "java";
      entry.put("kind", "solution");
      entry.put("language", shown);
      entry.put("code", references.get(shown));
      entry.put("text", "Here is a worked reference. Read it against your plan rather than copying it: find the line that keeps your invariant true. It does not mark the problem solved; only an accepted official run does. Then try the transfer question: " + transfer(p));
      session.put("solutionRevealedAt", entry.get("at"));
    } else {
      String key = stage + (run != null && "debug".equals(stage) ? ":" + run.get("id") : "");
      int rung = (int) nudges.stream().filter(n -> key.equals(n.get("key"))).count();
      entry.put("key", key);
      entry.put("rung", rung);
      var hints = Store.strings(p.get("hints"));
      List<String[]> ladder = new ArrayList<>(); // {kind, text}
      ladder.add(new String[] { "question", question(stage, (Map<?, ?>) view.get("plan"), run, Boolean.TRUE.equals(view.get("execution"))) });
      ladder.add(new String[] { "evidence", evidence(stage, run, p) });
      if (!stage.equals("reflect") && !stage.equals("done")) for (int i = 0; i < hints.size(); i++) ladder.add(new String[] { "hint", hints.get(i) });
      ladder.add(new String[] { "options", stage.equals("reflect") || stage.equals("done")
        ? "That's the whole reflection ladder. Save your answers below; they stay with this problem for review."
        : "You've seen every hint for this step. You could run your code for concrete evidence, ask the Blob about one specific line, or reveal the worked solution. Revealing it won't mark the problem solved; only an accepted run does." });
      var chosen = ladder.get(Math.min(rung, ladder.size() - 1));
      entry.put("kind", chosen[0]);
      entry.put("text", chosen[1]);
      if (run != null) entry.put("runId", run.get("id"));
    }
    nudges.add(entry);
    session.put("nudges", nudges.subList(Math.max(0, nudges.size() - 60), nudges.size()));
    s.put(id(user, problem), "coach", user, session);
    return view(user, problem, language);
  }

  static String quote(Object value) {
    return "“" + value.toString().strip().replaceAll("[.]+$", "") + "”";
  }

  static String question(String stage, Map<?, ?> plan, Map<String, Object> run, boolean execution) {
    String noRunner = execution ? "" : " Runs aren't available right now, so this hand check is your evidence for the moment.";
    return switch (stage) {
      case "plan" -> "Before any code: after you have handled the first few values, what must be true about what you have kept? Write that as your invariant in the plan below; your loop's job is to keep it true.";
      case "code" -> plan == null
        ? "Pick a tiny input and trace your code by hand for two steps. Which variables change, and why?" + noRunner
        : "Trace your example " + quote(plan.get("example")) + " through your code by hand for the first two steps. Write down every variable. Does your invariant " + quote(plan.get("invariant")) + " still hold after each step?" + noRunner;
      case "debug" -> run != null && run.get("failing") instanceof Map<?, ?> f && "COMPILATION_ERROR".equals(f.get("status"))
        ? "Your latest run didn't compile. Read only the first error: which line does it name, and what did the compiler expect there?"
        : "Before changing anything: on the failing case, at which step does " + (plan == null ? "your plan" : "your invariant " + quote(plan.get("invariant"))) + " first stop holding?";
      default -> "How many times can each loop variable or pointer move in the worst case? That count is your time complexity. Could any step repeat work an earlier step already did?";
    };
  }

  static String evidence(String stage, Map<String, Object> run, Map<String, Object> p) {
    if (stage.equals("reflect") || stage.equals("done")) return "Transfer question: " + transfer(p);
    if (run != null && run.get("failing") instanceof Map<?, ?> f) {
      String stale = Boolean.TRUE.equals(run.get("current")) ? "" : " You have edited your code since that run, so run it again before trusting this.";
      String status = Objects.toString(f.get("status"), "");
      if (status.equals("COMPILATION_ERROR")) return "The compiler said: " + Objects.toString(f.get("message"), "compilation failed") + "." + stale;
      if (Boolean.TRUE.equals(f.get("public"))) return "Case " + f.get("index") + " failed (" + status.toLowerCase(Locale.ROOT).replace('_', ' ') + "). Input " + quote(f.get("input")) + ", expected " + quote(Objects.toString(f.get("expected"), "")) + ", your program printed " + quote(Objects.toString(f.get("actual"), "")) + ". Trace exactly this input; the first line where your trace disagrees with your plan is the place to look." + stale;
      if (status.equals("TIME_LIMIT")) return "Hidden case " + f.get("index") + " ran out of time. The constraints allow " + quote(p.get("constraints")) + ": how many steps does your code take at that size?" + stale;
      return "Your visible cases pass, but hidden case " + f.get("index") + " fails (" + status.toLowerCase(Locale.ROOT).replace('_', ' ') + "). Hidden cases test the edges of " + quote(p.get("constraints")) + ". Which of those edge inputs does your plan not handle yet?" + stale;
    }
    return "Check your plan against the constraints " + quote(p.get("constraints")) + ". Which smallest or most extreme input would break it? Try that by hand before writing more code.";
  }
}
