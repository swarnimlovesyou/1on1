package com.oneonone;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

/**
 * Upcoming contests from Codeforces' official API and AtCoder's public contest page (allowed by its robots.txt),
 * each fetched at most once an hour. A source that fails keeps its last good list and is reported as not ok.
 * LeetCode and CodeChef are linked from the page instead: neither offers a public schedule we may read.
 */
@Service
public class ContestService {

  static final String CODEFORCES = "https://codeforces.com/api/contest.list?gym=false";
  static final String ATCODER = "https://atcoder.jp/contests/?lang=en";
  static final Duration FRESH = Duration.ofHours(1);
  static final Duration RETRY = Duration.ofMinutes(10);

  final Function<String, String> http;
  final Supplier<Instant> clock;
  final ObjectMapper json = new ObjectMapper();
  final Map<String, Source> sources = new LinkedHashMap<>();

  static final class Source {
    final String platform;
    final String url;
    final Function<String, List<Map<String, Object>>> parse;
    List<Map<String, Object>> contests = List.of();
    Instant checkedAt;
    Instant fetchedAt;
    boolean ok;

    Source(String platform, String url, Function<String, List<Map<String, Object>>> parse) {
      this.platform = platform;
      this.url = url;
      this.parse = parse;
    }
  }

  @Autowired
  public ContestService() {
    this(ContestService::get, Instant::now);
  }

  ContestService(Function<String, String> http, Supplier<Instant> clock) {
    this.http = http;
    this.clock = clock;
    sources.put("Codeforces", new Source("Codeforces", CODEFORCES, this::codeforces));
    sources.put("AtCoder", new Source("AtCoder", ATCODER, ContestService::atcoder));
  }

  static String get(String url) {
    try {
      var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(8)).followRedirects(HttpClient.Redirect.NORMAL).build();
      var request = HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(10)).header("User-Agent", "1on1-contests").GET().build();
      var response = client.send(request, HttpResponse.BodyHandlers.ofString());
      if (response.statusCode() != 200) throw new IllegalStateException(url + " answered " + response.statusCode());
      return response.body();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(e);
    } catch (java.io.IOException e) {
      throw new IllegalStateException(e);
    }
  }

  public Map<String, Object> upcoming() {
    Instant now = clock.get();
    // claim due sources under the lock, fetch outside it, so a slow site never makes other requests wait
    var due = new ArrayList<Source>();
    synchronized (this) {
      for (var s : sources.values())
        if (s.checkedAt == null || !now.isBefore(s.checkedAt.plus(s.ok ? FRESH : RETRY))) {
          s.checkedAt = now;
          due.add(s);
        }
    }
    for (var s : due) {
      try {
        var fresh = s.parse.apply(http.apply(s.url));
        synchronized (this) {
          s.contests = fresh;
          s.fetchedAt = now;
          s.ok = true;
        }
      } catch (RuntimeException failure) {
        synchronized (this) {
          s.ok = false; // keep the last good list
        }
      }
    }
    return snapshot(now);
  }

  synchronized Map<String, Object> snapshot(Instant now) {
    var contests = sources.values().stream()
      .flatMap(s -> s.contests.stream())
      .filter(c -> Instant.parse(c.get("start").toString()).plus(Duration.ofMinutes(((Number) c.get("durationMinutes")).longValue())).isAfter(now))
      .sorted(Comparator.comparing((Map<String, Object> c) -> c.get("start").toString()).thenComparing(c -> c.get("title").toString()))
      .toList();
    var status = sources.values().stream().map(s -> {
      var row = new LinkedHashMap<String, Object>();
      row.put("platform", s.platform);
      row.put("ok", s.ok);
      row.put("fetchedAt", s.fetchedAt == null ? null : s.fetchedAt.toString());
      return (Map<String, Object>) row;
    }).toList();
    return Map.of("contests", contests, "sources", status);
  }

  static Map<String, Object> contest(String platform, String title, Instant start, long minutes, String url) {
    var c = new LinkedHashMap<String, Object>();
    c.put("id", platform.toLowerCase() + "-" + url.substring(url.lastIndexOf('/') + 1));
    c.put("platform", platform);
    c.put("title", title);
    c.put("start", start.toString());
    c.put("durationMinutes", (int) minutes);
    c.put("url", url);
    return c;
  }

  List<Map<String, Object>> codeforces(String body) {
    Map<String, Object> data = json.readValue(body, Map.class);
    if (!"OK".equals(data.get("status"))) throw new IllegalStateException("Codeforces: " + data.get("comment"));
    var out = new ArrayList<Map<String, Object>>();
    for (var c : Store.items(data.get("result"))) {
      String phase = String.valueOf(c.get("phase"));
      if (!phase.equals("BEFORE") && !phase.equals("CODING")) continue;
      // one malformed row is skipped rather than taking the whole source down
      if (!(c.get("name") instanceof String name) || !(c.get("startTimeSeconds") instanceof Number start) || !(c.get("durationSeconds") instanceof Number length)) continue;
      out.add(contest("Codeforces", name, Instant.ofEpochSecond(start.longValue()), length.longValue() / 60, "https://codeforces.com/contests/" + c.get("id")));
    }
    return out;
  }

  static final Pattern ROW = Pattern.compile(
    "<time class='fixtime fixtime-full'>([^<]+)</time>.*?<a href=\"/contests/([A-Za-z0-9_-]+)\">([^<]+)</a>.*?<td[^>]*>\\s*(\\d+):(\\d{2})\\s*</td>",
    Pattern.DOTALL
  );
  static final DateTimeFormatter ATCODER_TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ssxx");

  /** Decodes the HTML entities a contest title can carry, so React does not show them literally. */
  static String unescape(String html) {
    var m = Pattern.compile("&#(x?)([0-9A-Fa-f]+);").matcher(html);
    var sb = new StringBuilder();
    while (m.find()) m.appendReplacement(sb, java.util.regex.Matcher.quoteReplacement(new String(Character.toChars(Integer.parseInt(m.group(2), m.group(1).isEmpty() ? 10 : 16)))));
    m.appendTail(sb);
    return sb.toString().replace("&quot;", "\"").replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'").replace("&amp;", "&");
  }

  static List<Map<String, Object>> atcoder(String html) {
    int from = html.indexOf("id=\"contest-table-upcoming\"");
    if (from < 0) throw new IllegalStateException("AtCoder: the upcoming table was not found");
    int to = html.indexOf("</table>", from);
    var section = html.substring(from, to < 0 ? html.length() : to);
    var out = new ArrayList<Map<String, Object>>();
    var m = ROW.matcher(section);
    while (m.find()) {
      var start = OffsetDateTime.parse(m.group(1).trim(), ATCODER_TIME).toInstant();
      long minutes = Long.parseLong(m.group(4)) * 60 + Long.parseLong(m.group(5));
      out.add(contest("AtCoder", unescape(m.group(3).trim()), start, minutes, "https://atcoder.jp/contests/" + m.group(2)));
    }
    return out;
  }
}
