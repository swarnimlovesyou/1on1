import { describe, expect, it } from "vitest";
import { simulate, type Settings } from "./trafficModel";

const base: Settings = { rate: 50, servers: 1, serviceRate: 100, cache: false, hitRate: 0.8, dbCapacity: 10_000 };
const finite = (r: ReturnType<typeof simulate>) =>
  [r.throughput, r.dropped, r.latencyMs, r.appUtil, r.dbUtil].every((v) => Number.isFinite(v) && v >= 0);

describe("simulate", () => {
  it("matches M/M/1 for one server and a fast database", () => {
    const r = simulate(base);
    // app: 1 / (100 - 50) = 20 ms; database: 1 / (10000 - 50) ≈ 0.1 ms
    expect(r.latencyMs).toBeCloseTo(20 + 1000 / 9950, 2);
    expect(r.appUtil).toBeCloseTo(0.5);
    expect(r.dropped).toBe(0);
  });

  it("matches M/M/c (Erlang C) for two servers", () => {
    const r = simulate({ ...base, rate: 100, servers: 2 });
    // a = 1, ρ = 0.5, C(2,1) = 1/3, Wq = (1/3)/100 s, W = 3.33 + 10 ms
    expect(r.latencyMs - 1000 / (10_000 - 100)).toBeCloseTo(13.333, 2);
  });

  it("drops what the app tier cannot take and names it the bottleneck", () => {
    const r = simulate({ ...base, rate: 500, servers: 2 });
    expect(r.throughput).toBeCloseTo(190);
    expect(r.dropped).toBeCloseTo(310);
    expect(r.bottleneck).toBe("app");
    expect(finite(r)).toBe(true);
  });

  it("a cache shields the database; with no cache the database can be the bottleneck", () => {
    const busy = { ...base, rate: 400, servers: 8, dbCapacity: 300 };
    const without = simulate(busy);
    const withCache = simulate({ ...busy, cache: true, hitRate: 0.8 });
    expect(without.bottleneck).toBe("database");
    expect(without.dropped).toBeGreaterThan(0);
    expect(withCache.dbUtil).toBeCloseTo((400 * 0.2) / 300);
    expect(withCache.dropped).toBe(0);
    expect(withCache.latencyMs).toBeLessThan(without.latencyMs);
  });

  it("more servers never make latency worse", () => {
    let last = Infinity;
    for (let servers = 1; servers <= 12; servers++) {
      const r = simulate({ ...base, rate: 300, servers });
      expect(r.latencyMs).toBeLessThanOrEqual(last + 1e-9);
      last = r.latencyMs;
    }
  });

  it("stays finite at the extremes", () => {
    for (const s of [
      { ...base, rate: 0 },
      { ...base, rate: 1e6 },
      { ...base, cache: true, hitRate: 1 },
      { ...base, cache: true, hitRate: 0 },
      { ...base, servers: 0 },
      { ...base, dbCapacity: 1 },
    ]) expect(finite(simulate(s))).toBe(true);
  });

  it("reports no bottleneck when every tier is comfortable", () => {
    expect(simulate({ ...base, rate: 10, servers: 4 }).bottleneck).toBe("none");
  });
});
