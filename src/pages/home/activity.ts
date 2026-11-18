/** Activity maths for the dashboard. Days are UTC dates (YYYY-MM-DD), as the server records them. */
type Activity = Record<string, number>;

const DAY = 86_400_000;
const iso = (t: number) => new Date(t).toISOString().slice(0, 10);
const startOfDay = (d: Date) => Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate());

/** Consecutive active days ending today, or ending yesterday if today has no activity yet. */
export function streak(activity: Activity, today = new Date()) {
  let day = startOfDay(today);
  if (!activity[iso(day)]) day -= DAY;
  let n = 0;
  while (activity[iso(day)]) {
    n++;
    day -= DAY;
  }
  return n;
}

/** Activity over the last seven days, today included. */
export function weekCount(activity: Activity, today = new Date()) {
  const end = startOfDay(today);
  let total = 0;
  for (let i = 0; i < 7; i++) total += activity[iso(end - i * DAY)] ?? 0;
  return total;
}

/** `count` weeks of seven days ending today, oldest first, for a heatmap. */
export function weeks(activity: Activity, today = new Date(), count = 12) {
  const end = startOfDay(today);
  const first = end - (count * 7 - 1) * DAY;
  return Array.from({ length: count }, (_, w) =>
    Array.from({ length: 7 }, (_, d) => {
      const date = iso(first + (w * 7 + d) * DAY);
      return { date, count: activity[date] ?? 0 };
    }),
  );
}
