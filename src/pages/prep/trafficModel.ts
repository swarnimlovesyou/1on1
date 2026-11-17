/**
 * A teaching model of a small web system, not a capacity planner.
 * App servers form one M/M/c queue (Erlang C); a cache answers a share of requests in about 1 ms;
 * the database is an M/M/1 queue that sees only cache misses. Each tier admits at most 95% of its
 * capacity (above that, queues grow without bound), and the rest is counted as dropped.
 */
export type Settings = {
  rate: number; // requests per second arriving
  servers: number; // app servers behind the load balancer
  serviceRate: number; // requests per second one server can handle
  cache: boolean;
  hitRate: number; // 0..1, share of requests the cache answers
  dbCapacity: number; // requests per second the database can handle
};

export type Tier = "app" | "database" | "none";

export type Result = {
  throughput: number; // requests per second answered
  dropped: number; // requests per second turned away
  latencyMs: number; // average response time of answered requests
  appUtil: number; // 0..0.95
  dbUtil: number; // 0..0.95
  bottleneck: Tier;
};

export const MAX_UTILISATION = 0.95;
const CACHE_MS = 1;

/** Probability an arrival has to wait in an M/M/c queue with offered load a = λ/μ (needs a < c). */
function erlangC(c: number, a: number) {
  let term = 1; // a^k / k!
  let sum = 0;
  for (let k = 0; k < c; k++) {
    sum += term;
    term *= a / (k + 1);
  }
  const waiting = term / (1 - a / c);
  return waiting / (sum + waiting);
}

export function simulate(s: Settings): Result {
  const servers = Math.max(1, Math.round(s.servers));
  const mu = Math.max(1, s.serviceRate);
  const rate = Math.max(0, s.rate);
  const dbCap = Math.max(1, s.dbCapacity);
  const hit = s.cache ? Math.min(1, Math.max(0, s.hitRate)) : 0;

  const appCap = servers * mu;
  const app = Math.min(rate, MAX_UTILISATION * appCap);
  const appWait = app === 0 ? 1 / mu : erlangC(servers, app / mu) / (appCap - app) + 1 / mu;

  const misses = app * (1 - hit);
  const db = Math.min(misses, MAX_UTILISATION * dbCap);
  const dbWait = 1 / (dbCap - db);

  const appUtil = app / appCap;
  const dbUtil = db / dbCap;
  const top = Math.max(appUtil, dbUtil);
  return {
    throughput: app - (misses - db),
    dropped: rate - app + (misses - db),
    latencyMs: 1000 * appWait + hit * CACHE_MS + (1 - hit) * 1000 * dbWait,
    appUtil,
    dbUtil,
    bottleneck: top < 0.8 ? "none" : appUtil >= dbUtil ? "app" : "database",
  };
}
