import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ArrowRight } from "@phosphor-icons/react";
import { simulate, type Result, type Settings } from "./trafficModel";

type Key = Exclude<keyof Settings, "cache">;

const SLIDERS: { key: Key; label: string; min: number; max: number; step: number; format: (v: number) => string }[] = [
  { key: "rate", label: "Requests per second", min: 10, max: 2000, step: 10, format: (v) => `${v}/s` },
  { key: "servers", label: "App servers", min: 1, max: 20, step: 1, format: (v) => `${v}` },
  { key: "serviceRate", label: "Requests one server handles per second", min: 50, max: 500, step: 10, format: (v) => `${v}/s` },
  { key: "dbCapacity", label: "Database capacity", min: 100, max: 5000, step: 50, format: (v) => `${v}/s` },
];

const TIER_NAME = { app: "App servers", database: "Database", none: "None" } as const;
const round = (v: number) => Math.round(v);
const pct = (v: number) => `${Math.round(v * 100)}%`;

function load(util: number) {
  return util >= 0.8 ? "hot" : util >= 0.6 ? "warm" : "calm";
}

function describe(label: string, from: string, to: string, before: Result, after: Result) {
  const parts = [`${label}: ${from} → ${to}.`, `Average latency ${round(before.latencyMs)} → ${round(after.latencyMs)} ms`];
  if (round(before.dropped) || round(after.dropped)) parts.push(`dropped ${round(before.dropped)} → ${round(after.dropped)}/s`);
  return parts[0] + " " + parts.slice(1).join(", ") + ".";
}

/** Sliders over a tiny system: load balancer, app servers, an optional cache and a database. */
export default function PlaygroundPage() {
  const [settings, setSettings] = useState<Settings>({ rate: 300, servers: 2, serviceRate: 200, cache: false, hitRate: 0.8, dbCapacity: 1000 });
  const [change, setChange] = useState("Move a slider to see what changes.");
  const result = simulate(settings);
  const last = useRef(result);

  function update(next: Settings, label: string, from: string, to: string) {
    const after = simulate(next);
    setChange(describe(label, from, to, last.current, after));
    last.current = after;
    setSettings(next);
  }

  const tiers = [
    { name: "Clients", detail: `${settings.rate}/s`, state: "calm" },
    { name: "Load balancer", detail: "spreads requests", state: "calm" },
    { name: `App servers ×${settings.servers}`, detail: pct(result.appUtil) + " busy", state: load(result.appUtil) },
    ...(settings.cache ? [{ name: "Cache", detail: pct(settings.hitRate) + " hits", state: "calm" }] : []),
    { name: "Database", detail: pct(result.dbUtil) + " busy", state: load(result.dbUtil) },
  ];

  return (
    <article className="prep-guide playground">
      <Link className="back-link" to="/prep/system-design">
        <ArrowLeft size={16} aria-hidden="true" />
        Back to system design
      </Link>
      <h1 className="display">Traffic playground</h1>
      <p className="prose">
        Change the load and the system, and watch where requests queue up. This is a teaching model, not a capacity planner: real systems
        have bursts, slow requests and network costs this leaves out.
      </p>

      <ol className="playground-tiers" aria-label="The system, left to right">
        {tiers.map((t, i) => (
          <li key={t.name} className={"tier tier-" + t.state}>
            <strong>{t.name}</strong>
            <span>{t.detail}</span>
            {i < tiers.length - 1 && <ArrowRight className="tier-arrow" size={16} aria-hidden="true" />}
          </li>
        ))}
      </ol>

      <div className="playground-grid">
        <form className="playground-controls" onSubmit={(e) => e.preventDefault()}>
          {SLIDERS.map((s) => (
            <label key={s.key}>
              <span>
                {s.label} <output>{s.format(settings[s.key])}</output>
              </span>
              <input
                type="range"
                aria-label={s.label}
                min={s.min}
                max={s.max}
                step={s.step}
                value={settings[s.key]}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  update({ ...settings, [s.key]: v }, s.label, s.format(settings[s.key]), s.format(v));
                }}
              />
            </label>
          ))}
          <label className="playground-check">
            <input
              type="checkbox"
              aria-label="Cache"
              checked={settings.cache}
              onChange={(e) => update({ ...settings, cache: e.target.checked }, "Cache", settings.cache ? "on" : "off", e.target.checked ? "on" : "off")}
            />
            <span>Cache in front of the database</span>
          </label>
          {settings.cache && (
            <label>
              <span>
                Cache hit rate <output>{pct(settings.hitRate)}</output>
              </span>
              <input
                type="range"
                aria-label="Cache hit rate"
                min={0}
                max={0.99}
                step={0.01}
                value={settings.hitRate}
                onChange={(e) => {
                  const v = Number(e.target.value);
                  update({ ...settings, hitRate: v }, "Cache hit rate", pct(settings.hitRate), pct(v));
                }}
              />
            </label>
          )}
        </form>

        <section className="playground-results">
          <dl>
            <div>
              <dt>Answered</dt>
              <dd data-metric="throughput">{round(result.throughput)}/s</dd>
            </div>
            <div>
              <dt>Dropped</dt>
              <dd data-metric="dropped">{round(result.dropped)}/s</dd>
            </div>
            <div>
              <dt>Average latency</dt>
              <dd data-metric="latency">{round(result.latencyMs)} ms</dd>
            </div>
            <div>
              <dt>App servers busy</dt>
              <dd data-metric="appUtil">{pct(result.appUtil)}</dd>
            </div>
            <div>
              <dt>Database busy</dt>
              <dd data-metric="dbUtil">{pct(result.dbUtil)}</dd>
            </div>
          </dl>
          <p className="playground-bottleneck">
            Bottleneck: <strong>{TIER_NAME[result.bottleneck]}</strong>
            {result.bottleneck === "none" ? " — every tier has room to spare." : " — this tier is above 80% busy, so its queue grows fast."}
          </p>
          <p className="playground-change muted" aria-live="polite">
            {change}
          </p>
        </section>
      </div>
      <p className="muted small">
        How it works: the app servers are modelled as one queue shared by every server (M/M/c), the database as a single queue that only sees
        cache misses (M/M/1), and a cache hit costs about 1 ms. A tier never takes more than 95% of its capacity here; the rest is dropped.
      </p>
    </article>
  );
}
