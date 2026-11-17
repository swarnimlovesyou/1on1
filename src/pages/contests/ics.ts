export type Contest = { id: string; platform: string; title: string; start: string; durationMinutes: number; url: string };

const stamp = (d: Date) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
const text = (s: string) => s.replace(/\\/g, "\\\\").replace(/([,;])/g, "\\$1").replace(/\n/g, "\\n");

/** A one-event iCalendar file in UTC, so any calendar app shows it in the learner's own time zone. */
export function icsFor(c: Contest, now = new Date()) {
  const start = new Date(c.start);
  const end = new Date(start.getTime() + c.durationMinutes * 60_000);
  return (
    [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//1on1//Contests//EN",
      "BEGIN:VEVENT",
      `UID:${c.id}@1on1`,
      `DTSTAMP:${stamp(now)}`,
      `DTSTART:${stamp(start)}`,
      `DTEND:${stamp(end)}`,
      `SUMMARY:${text(c.title)}`,
      `URL:${c.url}`,
      `DESCRIPTION:${text(c.platform + " contest. " + c.url)}`,
      "END:VEVENT",
      "END:VCALENDAR",
    ].join("\r\n") + "\r\n"
  );
}

/** "in 3 d 4 h", "in 45 min", or "live now" until it ends. */
export function countdown(c: Contest, now = Date.now()) {
  const start = new Date(c.start).getTime();
  const end = start + c.durationMinutes * 60_000;
  if (now >= start) return now < end ? "live now" : "ended";
  const minutes = Math.round((start - now) / 60_000);
  const d = Math.floor(minutes / 1440), h = Math.floor((minutes % 1440) / 60), m = minutes % 60;
  return d ? `in ${d} d ${h} h` : h ? `in ${h} h ${m} min` : `in ${m} min`;
}
