package com.oneonone;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.*;

/** Upcoming contests from Codeforces' official API and AtCoder's contest page, cached, failing honestly. */
class ContestTest {

  static final String CF = """
    {"status":"OK","result":[
      {"id":2290,"name":"Codeforces Round 1100 (Div. 2)","phase":"BEFORE","durationSeconds":7200,"startTimeSeconds":1797000000},
      {"id":2289,"name":"Codeforces Round 1099","phase":"CODING","durationSeconds":7200,"startTimeSeconds":1700000000},
      {"id":2288,"name":"Old round","phase":"FINISHED","durationSeconds":7200,"startTimeSeconds":1600000000}
    ]}""";

  static final String ATC = """
    <div id="contest-table-active"></div>
    <div id="contest-table-upcoming"><table><tbody>
    <tr><td><a href='x'><time class='fixtime fixtime-full'>2026-11-21 21:00:00+0900</time></a></td>
      <td><span>A</span> <a href="/contests/abc485">AtCoder Beginner Contest 485</a></td><td class="text-center">01:40</td><td> - 1999</td></tr>
    <tr><td><a href='x'><time class='fixtime fixtime-full'>2026-11-29 19:00:00+0900</time></a></td>
      <td><a href="/contests/ahc075">AtCoder Heuristic Contest 075</a></td><td class="text-center">04:00</td><td>All</td></tr>
    </tbody></table></div>
    <div id="contest-table-recent"><table><tbody>
    <tr><td><time class='fixtime fixtime-full'>2020-01-01 21:00:00+0900</time></td><td><a href="/contests/abc100">Past</a></td><td>01:40</td></tr>
    </tbody></table></div>""";

  AtomicInteger calls = new AtomicInteger();
  Map<String, String> responses = new HashMap<>();
  Instant now = Instant.parse("2026-11-17T12:00:00Z");

  ContestService service() {
    return new ContestService(url -> {
      calls.incrementAndGet();
      String body = responses.get(url.contains("codeforces") ? "cf" : "atc");
      if (body == null) throw new IllegalStateException("down");
      return body;
    }, () -> now);
  }

  @BeforeEach
  void setup() {
    responses.put("cf", CF);
    responses.put("atc", ATC);
  }

  List<Map<String, Object>> contests(Map<String, Object> result) {
    return Store.items(result.get("contests"));
  }

  @Test
  void bothSourcesMergeInStartOrderWithUtcTimesAndLinks() {
    var list = contests(service().upcoming());
    assertEquals(List.of("AtCoder Beginner Contest 485", "AtCoder Heuristic Contest 075", "Codeforces Round 1100 (Div. 2)"),
      list.stream().map(c -> c.get("title")).toList(), "only contests that have not finished, soonest first");
    var abc = list.get(0);
    assertEquals("AtCoder", abc.get("platform"));
    assertEquals("2026-11-21T12:00:00Z", abc.get("start"), "+0900 converted to UTC");
    assertEquals(100, abc.get("durationMinutes"));
    assertEquals("https://atcoder.jp/contests/abc485", abc.get("url"));
    var cf = list.get(2);
    assertEquals("https://codeforces.com/contests/2290", cf.get("url"));
    assertEquals(120, cf.get("durationMinutes"));
    assertEquals(Instant.ofEpochSecond(1797000000).toString(), cf.get("start"));
  }

  @Test
  void aSourceThatFailsIsReportedWhileTheOtherStillShows() {
    responses.remove("atc");
    var result = service().upcoming();
    assertEquals(List.of("Codeforces"), contests(result).stream().map(c -> c.get("platform")).distinct().toList());
    var sources = Store.items(result.get("sources"));
    assertEquals(false, sources.stream().filter(s -> "AtCoder".equals(s.get("platform"))).findFirst().orElseThrow().get("ok"));
    assertEquals(true, sources.stream().filter(s -> "Codeforces".equals(s.get("platform"))).findFirst().orElseThrow().get("ok"));
  }

  @Test
  void resultsAreCachedForAnHourAndTheLastGoodListSurvivesAnOutage() {
    var s = service();
    s.upcoming();
    int first = calls.get();
    s.upcoming();
    assertEquals(first, calls.get(), "no refetch within the hour");
    now = now.plusSeconds(3601);
    responses.clear();
    var stale = s.upcoming();
    assertTrue(calls.get() > first, "refetched after the hour");
    assertEquals(3, contests(stale).size(), "the last good lists are kept when both sources fail");
    assertTrue(Store.items(stale.get("sources")).stream().noneMatch(x -> Boolean.TRUE.equals(x.get("ok"))));
  }

  @Test
  void contestsThatHaveEndedDropOffTheCachedList() {
    var s = service();
    s.upcoming();
    now = Instant.parse("2026-11-25T00:00:00Z");
    var titles = contests(s.upcoming()).stream().map(c -> c.get("title")).toList();
    assertFalse(titles.contains("AtCoder Beginner Contest 485"));
  }
  @Test
  void aSlowSourceNeverMakesOtherRequestsWait() throws Exception {
    var entered = new java.util.concurrent.CountDownLatch(1);
    var release = new java.util.concurrent.CountDownLatch(1);
    var s = new ContestService(url -> {
      if (url.contains("codeforces")) {
        entered.countDown();
        try {
          release.await();
        } catch (InterruptedException e) {
          Thread.currentThread().interrupt();
        }
        return CF;
      }
      return ATC;
    }, () -> now);
    var slow = new Thread(s::upcoming);
    slow.start();
    assertTrue(entered.await(2, java.util.concurrent.TimeUnit.SECONDS));
    var quick = assertTimeoutPreemptively(java.time.Duration.ofMillis(800), s::upcoming, "a second request must not wait for the slow fetch");
    assertNotNull(quick.get("contests"));
    release.countDown();
    slow.join(2000);
    assertEquals(3, contests(s.upcoming()).size(), "the slow fetch still lands");
  }
  @Test
  void oneBadRowIsSkippedAndHtmlEntitiesInTitlesAreDecoded() {
    responses.put("cf", """
      {"status":"OK","result":[
        {"id":2291,"name":"Round with no start","phase":"BEFORE","durationSeconds":7200},
        {"id":2290,"name":"Codeforces Round 1100 (Div. 2)","phase":"BEFORE","durationSeconds":7200,"startTimeSeconds":1797000000}
      ]}""");
    responses.put("atc", ATC.replace("AtCoder Beginner Contest 485", "AtCoder Beginner Contest 485 &amp; Friends&#39; Cup"));
    var result = service().upcoming();
    var titles = contests(result).stream().map(c -> c.get("title")).toList();
    assertTrue(titles.contains("Codeforces Round 1100 (Div. 2)"), "the good Codeforces row still shows");
    assertTrue(titles.contains("AtCoder Beginner Contest 485 & Friends' Cup"), titles.toString());
    assertTrue(Store.items(result.get("sources")).stream().allMatch(x -> Boolean.TRUE.equals(x.get("ok"))));
  }
}
