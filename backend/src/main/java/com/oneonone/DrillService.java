package com.oneonone;

import java.math.BigDecimal;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * Aptitude and reasoning drills. Each question is a pure function of (topic, seed), so the server regenerates it to
 * grade and the answer never reaches the browser first. Inputs are chosen so every numeric answer is a whole number.
 */
@Service
public class DrillService {

  public record Drill(String prompt, String answer, String explanation, List<String> options, String unit) {
    Drill(String prompt, long answer, String explanation, String unit) {
      this(prompt, Long.toString(answer), explanation, null, unit);
    }
  }

  public static final Map<String, String> TOPICS = new LinkedHashMap<>();

  static {
    for (String t : List.of("percentages", "profit-loss", "ratio-proportion", "averages", "interest", "time-work", "speed-distance", "number-systems"))
      TOPICS.put(t, "aptitude");
    for (String t : List.of("number-series", "letter-series", "coding-decoding", "directions", "syllogisms")) TOPICS.put(t, "reasoning");
  }

  final ProgressService progress;

  public DrillService(ProgressService progress) {
    this.progress = progress;
  }

  public Map<String, Object> next(String topic, String seedText) {
    known(topic);
    int seed = seedText == null || seedText.isBlank() ? ThreadLocalRandom.current().nextInt(0, Integer.MAX_VALUE) : seed(seedText);
    var d = generate(topic, seed);
    var out = new LinkedHashMap<String, Object>();
    out.put("topic", topic);
    out.put("seed", seed);
    out.put("prompt", d.prompt());
    if (d.options() != null) out.put("options", d.options());
    if (d.unit() != null) out.put("unit", d.unit());
    return out;
  }

  public Map<String, Object> answer(String user, String topic, Object seedValue, String given) {
    known(topic);
    if (seedValue == null) throw bad("Send the seed of the question you are answering.");
    int seed = seed(seedValue.toString());
    if (given == null || given.isBlank()) throw bad("Type an answer first.");
    var d = generate(topic, seed);
    if (user != null) progress.record(user, "drill", topic);
    return Map.of("correct", matches(d.answer(), given), "expected", d.answer(), "explanation", d.explanation());
  }

  /** Numbers compare by value after dropping thousands commas; text compares ignoring case. */
  static boolean matches(String expected, String given) {
    String g = given.trim().replaceAll("(?<=\\d),(?=\\d)", "");
    try {
      return new BigDecimal(expected).compareTo(new BigDecimal(g)) == 0;
    } catch (NumberFormatException notNumeric) {
      return expected.trim().equalsIgnoreCase(g);
    }
  }

  public Drill generate(String topic, int seed) {
    known(topic);
    // Neighbouring seeds give near-identical first draws from java.util.Random, so spread them out first.
    var r = new Random(seed * 0x9E3779B97F4A7C15L + topic.hashCode());
    return switch (topic) {
      case "percentages" -> percentages(r);
      case "profit-loss" -> profitLoss(r);
      case "ratio-proportion" -> ratio(r);
      case "averages" -> averages(r);
      case "interest" -> r.nextBoolean() ? simpleInterest(500 * between(r, 1, 20), between(r, 2, 12), between(r, 1, 5))
        : compoundInterest(100 * between(r, 10, 100), r.nextBoolean() ? 10 : 20);
      case "time-work" -> {
        int[] t = WORK[r.nextInt(WORK.length)];
        int m = between(r, 1, 3);
        yield r.nextBoolean() ? timeWork(t[0] * m, t[1] * m) : timeWork(t[1] * m, t[0] * m);
      }
      case "speed-distance" -> {
        int speed = 18 * between(r, 1, 5), seconds = between(r, 5, 30);
        yield trainPole(seconds * speed * 5 / 18, speed);
      }
      case "number-systems" -> numberSystems(r);
      case "number-series" -> numberSeries(r);
      case "letter-series" -> letterSeries(r);
      case "coding-decoding" -> coding(r);
      case "directions" -> directions(r);
      case "syllogisms" -> {
        var nouns = new ArrayList<>(NOUNS);
        Collections.shuffle(nouns, r);
        yield syllogism(between(r, 1, 7), nouns.get(0), nouns.get(1), nouns.get(2));
      }
      default -> throw new IllegalStateException(topic);
    };
  }

  static void known(String topic) {
    if (!TOPICS.containsKey(topic)) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "That drill topic doesn't exist.");
  }

  static int seed(String text) {
    try {
      int seed = Integer.parseInt(text.trim());
      if (seed >= 0) return seed;
    } catch (NumberFormatException ignored) {
      // falls through to the same message
    }
    throw bad("The seed must be a whole number from 0 to 2147483647.");
  }

  static ResponseStatusException bad(String message) {
    return new ResponseStatusException(HttpStatus.BAD_REQUEST, message);
  }

  static int between(Random r, int low, int high) {
    return low + r.nextInt(high - low + 1);
  }

  static <T> T pick(Random r, List<T> items) {
    return items.get(r.nextInt(items.size()));
  }

  static long gcd(long a, long b) {
    return b == 0 ? a : gcd(b, a % b);
  }

  // ---- aptitude ----

  static Drill percentages(Random r) {
    int p = pick(r, List.of(5, 10, 12, 15, 20, 25, 30, 40, 50, 60, 75));
    int step = (int) (100 / gcd(p, 100));
    if (r.nextBoolean()) {
      int n = step * between(r, Math.max(1, 40 / step), 2000 / step);
      return new Drill("What is " + p + "% of " + n + "?", (long) p * n / 100, p + "% of " + n + " = " + n + " × " + p + " ÷ 100 = " + (p * n / 100) + ".", null);
    }
    int whole = step * between(r, Math.max(1, 20 / step), 600 / step), part = p * whole / 100;
    return new Drill(part + " is what percent of " + whole + "?", p, part + " ÷ " + whole + " × 100 = " + p + "%.", "%");
  }

  static Drill profitLoss(Random r) {
    int cost = 100 * between(r, 2, 50), p = pick(r, List.of(5, 10, 15, 20, 25, 30));
    if (r.nextBoolean()) {
      boolean profit = r.nextBoolean();
      int sell = cost * (profit ? 100 + p : 100 - p) / 100;
      return new Drill("An item bought for ₹" + cost + " is sold at a " + p + "% " + (profit ? "profit" : "loss") + ". What is the selling price?", sell,
        "Selling price = " + cost + " × " + (profit ? 100 + p : 100 - p) + " ÷ 100 = ₹" + sell + ".", "₹");
    }
    int sell = cost * (100 + p) / 100;
    return new Drill("An item bought for ₹" + cost + " is sold for ₹" + sell + ". What is the profit percent?", p,
      "Profit = " + sell + " − " + cost + " = " + (sell - cost) + ", and " + (sell - cost) + " ÷ " + cost + " × 100 = " + p + "%.", "%");
  }

  static Drill ratio(Random r) {
    if (r.nextBoolean()) {
      int a = between(r, 1, 9), b = between(r, 1, 9), k = between(r, 5, 60), total = (a + b) * k;
      return new Drill("₹" + total + " is shared between Asha and Ben in the ratio " + a + ":" + b + ". How much does Ben get?", (long) b * k,
        "There are " + a + " + " + b + " = " + (a + b) + " parts of ₹" + k + " each, so Ben gets " + b + " × " + k + " = ₹" + (b * k) + ".", "₹");
    }
    int a = between(r, 1, 7), b = between(r, 1, 7), c = between(r, 1, 7), k = between(r, 5, 40), total = (a + b + c) * k;
    return new Drill("₹" + total + " is shared among Asha, Ben and Chitra in the ratio " + a + ":" + b + ":" + c + ". How much does Chitra get?", (long) c * k,
      "There are " + a + " + " + b + " + " + c + " = " + (a + b + c) + " parts of ₹" + k + " each, so Chitra gets " + c + " × " + k + " = ₹" + (c * k) + ".", "₹");
  }

  static Drill averages(Random r) {
    if (r.nextBoolean()) {
      int n = between(r, 4, 6), mean = between(r, 40, 90), sum = 0;
      var values = new ArrayList<Integer>();
      for (int i = 0; i < n - 1; i++) {
        int v = mean + between(r, -8, 8); // keeps the balancing last value at 0 or more
        values.add(v);
        sum += v;
      }
      values.add(n * mean - sum);
      String list = String.join(", ", values.stream().map(String::valueOf).toList());
      return new Drill("What is the average of " + list + "?", mean, "The total is " + n * mean + ", and " + n * mean + " ÷ " + n + " = " + mean + ".", null);
    }
    int n = between(r, 4, 9), a = between(r, 20, 80), d = between(r, 1, 5) * (r.nextBoolean() ? 1 : -1);
    if (a + (n + 1) * d <= 0) d = -d;
    int b = a + d, added = (n + 1) * b - n * a;
    return new Drill("The average of " + n + " numbers is " + a + ". When one more number is added, the average becomes " + b + ". What number was added?", added,
      "New total " + (n + 1) + " × " + b + " = " + (n + 1) * b + ", old total " + n + " × " + a + " = " + n * a + ", difference " + added + ".", null);
  }

  static Drill simpleInterest(int principal, int rate, int years) {
    long interest = (long) principal * rate * years / 100;
    return new Drill("What is the simple interest on ₹" + principal + " at " + rate + "% a year for " + years + (years == 1 ? " year?" : " years?"), interest,
      "Simple interest = " + principal + " × " + rate + " × " + years + " ÷ 100 = ₹" + interest + ".", "₹");
  }

  static Drill compoundInterest(int principal, int rate) {
    long amount = (long) principal * (100 + rate) * (100 + rate) / 10000, interest = amount - principal;
    return new Drill("What is the compound interest on ₹" + principal + " at " + rate + "% a year for 2 years, compounded yearly?", interest,
      "Amount = " + principal + " × " + (100 + rate) + "/100 × " + (100 + rate) + "/100 = ₹" + amount + ", so the interest is " + amount + " − " + principal + " = ₹" + interest + ".", "₹");
  }

  static final int[][] WORK = { { 3, 6 }, { 4, 12 }, { 6, 12 }, { 10, 15 }, { 12, 24 }, { 20, 30 }, { 12, 36 } };

  static Drill timeWork(int a, int b) {
    if ((a * b) % (a + b) != 0) throw new IllegalArgumentException(a + "," + b);
    int together = a * b / (a + b);
    return new Drill("Asha can finish a job in " + a + " days and Ben can finish it in " + b + " days. Working together, how many days do they take?", together,
      "Together they do 1/" + a + " + 1/" + b + " of the job a day, so they take " + a + " × " + b + " ÷ (" + a + " + " + b + ") = " + together + " days.", "days");
  }

  static Drill trainPole(int metres, int kmh) {
    int seconds = metres * 18 / (5 * kmh);
    return new Drill("A train " + metres + " m long runs at " + kmh + " km/h. How many seconds does it take to pass a pole?", seconds,
      kmh + " km/h = " + kmh + " × 5/18 = " + (kmh * 5 / 18) + " m/s, and " + metres + " ÷ " + (kmh * 5 / 18) + " = " + seconds + " seconds.", "seconds");
  }

  static Drill numberSystems(Random r) {
    int h = pick(r, List.of(2, 3, 4, 5, 6, 8, 9, 12)), x, y;
    do {
      x = between(r, 2, 12);
      y = between(r, 2, 12);
    } while (x == y || gcd(x, y) != 1);
    int a = h * x, b = h * y;
    if (r.nextBoolean())
      return new Drill("What is the HCF of " + a + " and " + b + "?", h, a + " = " + h + " × " + x + " and " + b + " = " + h + " × " + y + ", and " + x + " and " + y + " share no factor, so the HCF is " + h + ".", null);
    long lcm = (long) h * x * y;
    return new Drill("What is the LCM of " + a + " and " + b + "?", lcm, "HCF is " + h + ", so LCM = " + a + " × " + b + " ÷ " + h + " = " + lcm + ".", null);
  }

  // ---- reasoning ----

  static Drill numberSeries(Random r) {
    long[] t = new long[6];
    String rule;
    switch (r.nextInt(4)) {
      case 0 -> {
        int start = between(r, 1, 50), d = between(r, 2, 15);
        for (int i = 0; i < 6; i++) t[i] = start + (long) d * i;
        rule = "Each term is " + d + " more than the one before.";
      }
      case 1 -> {
        int start = between(r, 1, 5), ratio = between(r, 2, 3);
        t[0] = start;
        for (int i = 1; i < 6; i++) t[i] = t[i - 1] * ratio;
        rule = "Each term is multiplied by " + ratio + ".";
      }
      case 2 -> {
        int s = between(r, 1, 8), k = between(r, -3, 10);
        for (int i = 0; i < 6; i++) t[i] = (long) (s + i) * (s + i) + k;
        String plus = k == 0 ? "" : k > 0 ? " + " + k : " − " + -k;
        rule = "The terms are n²" + plus + " for n = " + s + ", " + (s + 1) + ", " + (s + 2) + " and so on, so the next is " + (s + 5) + "²" + plus + ".";
      }
      default -> {
        int a = between(r, 1, 12), b = between(r, 1, 12);
        while (b == a) b = between(r, 1, 12);
        t[0] = between(r, 1, 30);
        for (int i = 1; i < 6; i++) t[i] = t[i - 1] + (i % 2 == 1 ? a : b);
        rule = "The differences alternate between +" + a + " and +" + b + ".";
      }
    }
    String shown = String.join(", ", Arrays.stream(t, 0, 5).mapToObj(Long::toString).toList());
    return new Drill("What comes next: " + shown + ", ?", t[5], rule + " The next term is " + t[5] + ".", null);
  }

  static char letter(int index) {
    return (char) ('A' + Math.floorMod(index, 26));
  }

  static Drill letterSeries(Random r) {
    int start = r.nextInt(26), step = between(r, 1, 5);
    var shown = new ArrayList<String>();
    for (int i = 0; i < 5; i++) shown.add(String.valueOf(letter(start + step * i)));
    String next = String.valueOf(letter(start + step * 5));
    return new Drill("What letter comes next: " + String.join(", ", shown) + ", ?", next,
      "Each letter moves " + step + " place" + (step == 1 ? "" : "s") + " forward in the alphabet" + (start + step * 5 > 25 ? " (after Z, start again at A)" : "") + ", so the next is " + next + ".", null, null);
  }

  static String shift(String word, int k) {
    var out = new StringBuilder();
    for (char c : word.toCharArray()) out.append(letter(c - 'A' + k));
    return out.toString();
  }

  static boolean wraps(String word, int k) {
    for (char c : word.toCharArray()) if (c - 'A' + k < 0 || c - 'A' + k > 25) return true;
    return false;
  }

  static final List<String> WORDS = List.of("CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "BOOK", "FISH", "LAMP", "ROAD", "CLOUD", "PLANT", "RIVER", "STONE", "BREAD", "CHAIR", "GLASS", "TRAIN");

  static Drill coding(Random r) {
    String a = pick(r, WORDS), b;
    do b = pick(r, WORDS); while (b.equals(a));
    int k = between(r, 1, 5) * (r.nextBoolean() ? 1 : -1);
    String coded = shift(b, k);
    return new Drill("If " + a + " is coded as " + shift(a, k) + ", how is " + b + " coded?", coded,
      "Each letter moves " + Math.abs(k) + " place" + (Math.abs(k) == 1 ? "" : "s") + (k > 0 ? " forward" : " back") + " in the alphabet" + (wraps(b, k) ? (k > 0 ? " (after Z, start again at A)" : " (before A, go back to Z)") : "") + ", so " + b + " becomes " + coded + ".", null, null);
  }

  static final String[] COMPASS = { "north", "east", "south", "west" };

  static Drill directions(Random r) {
    String name = pick(r, List.of("Riya", "Arjun", "Meera", "Kabir", "Sara", "Dev"));
    int turn = r.nextInt(4);
    boolean mirror = r.nextBoolean();
    // Legs as (compass index before rotation, metres). Index 0 north, 1 east, 2 south, 3 west.
    var legs = new ArrayList<int[]>();
    long distance;
    String working;
    if (r.nextBoolean()) {
      int m = pick(r, List.of(1, 2, 3, 5, 10)), dx = 3 * m, dy = 4 * m;
      if (r.nextBoolean()) { int s = dx; dx = dy; dy = s; }
      int extra = between(r, 1, 10);
      legs.add(new int[] { 0, dy + extra });
      legs.add(new int[] { 1, dx });
      legs.add(new int[] { 2, extra });
      distance = 5L * m;
      working = "The net move is " + dy + " m one way and " + dx + " m at right angles, so the distance is √(" + dy + "² + " + dx + "²) = " + distance + " m.";
    } else {
      int up = between(r, 2, 20), b = between(r, 1, 15), c = between(r, 1, 15);
      legs.add(new int[] { 0, up });
      legs.add(new int[] { 1, b });
      legs.add(new int[] { 2, up });
      legs.add(new int[] { 1, c });
      distance = b + c;
      working = "The two " + up + " m legs cancel, leaving " + b + " + " + c + " = " + distance + " m in one direction.";
    }
    var parts = new ArrayList<String>();
    for (int[] leg : legs) {
      int dir = mirror && leg[0] % 2 == 1 ? (leg[0] + 2) % 4 : leg[0];
      parts.add(leg[1] + " m " + COMPASS[(dir + turn) % 4]);
    }
    String walk = String.join(", then ", parts);
    return new Drill(name + " walks " + walk + ". How far is " + name + " from the starting point, in a straight line?", distance, working, "m");
  }

  static final List<String> NOUNS = List.of("cats", "dogs", "pens", "books", "trees", "cars", "birds", "chairs", "cups", "lamps", "stones", "boats");
  static final List<String> VERDICTS = List.of("Only I follows", "Only II follows", "Both follow", "Neither follows");

  static Drill syllogism(int template, String a, String b, String c) {
    String all = "All %s are %s.", some = "Some %s are %s.", no = "No %s are %s.", someNot = "Some %s are not %s.";
    String[] t = switch (template) {
      case 1 -> new String[] { all.formatted(a, b), all.formatted(b, c), all.formatted(a, c), some.formatted(c, a), "Both follow",
        "Every one of the " + a + " is one of the " + b + ", so every one is one of the " + c + "; that also means some " + c + " are " + a + "." };
      case 2 -> new String[] { all.formatted(a, b), some.formatted(b, c), some.formatted(a, c), some.formatted(c, b), "Only II follows",
        "The " + b + " that are " + c + " need not include any " + a + ", so I does not follow; II just reverses the second statement." };
      case 3 -> new String[] { no.formatted(a, b), all.formatted(c, b), no.formatted(c, a), some.formatted(a, c), "Only I follows",
        "Every one of the " + c + " is among the " + b + ", and no " + a + " are " + b + ", so no " + c + " are " + a + "; II contradicts that." };
      case 4 -> new String[] { some.formatted(a, b), all.formatted(b, c), some.formatted(a, c), all.formatted(c, a), "Only I follows",
        "The " + a + " that are " + b + " are also " + c + ", so I follows; nothing says every one of the " + c + " is among the " + a + "." };
      case 5 -> new String[] { all.formatted(a, b), no.formatted(b, c), no.formatted(a, c), some.formatted(b, a), "Both follow",
        "The " + a + " sit inside the " + b + ", which share nothing with the " + c + ", so I follows; II reverses part of the first statement." };
      case 6 -> new String[] { some.formatted(a, b), no.formatted(b, c), someNot.formatted(a, c), no.formatted(a, c), "Only I follows",
        "The " + a + " that are " + b + " cannot be " + c + ", so I follows; other " + a + " might still be " + c + ", so II does not." };
      case 7 -> new String[] { all.formatted(a, b), all.formatted(c, b), all.formatted(a, c), some.formatted(a, c), "Neither follows",
        "Both groups sit inside the " + b + ", but they need not overlap at all, so neither conclusion is certain." };
      default -> throw new IllegalArgumentException("template " + template);
    };
    String prompt = "Statements: " + capital(t[0]) + " " + capital(t[1]) + " Conclusions: I. " + capital(t[2]) + " II. " + capital(t[3]) + " Which conclusions follow?";
    return new Drill(prompt, t[4], t[5], VERDICTS, null);
  }

  static String capital(String s) {
    return Character.toUpperCase(s.charAt(0)) + s.substring(1);
  }
}
