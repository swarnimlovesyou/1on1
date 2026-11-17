import { useEffect, useState } from "react";

export function clock(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

/** Seconds left, counted from the server's own `remainingSeconds` so a wrong local clock can't shift the deadline. */
export function remainingFrom(remainingSeconds: number, receivedAt: number, now: number) {
  return Math.max(0, remainingSeconds - Math.floor((now - receivedAt) / 1000));
}

export function timeUsed(m: { startedAt: string; deadline: string; finishedAt?: string }) {
  const end = Math.min(new Date(m.finishedAt ?? m.deadline).getTime(), new Date(m.deadline).getTime());
  return clock((end - new Date(m.startedAt).getTime()) / 1000);
}

/** Ticks once a second while there is time left; `remainingSeconds` and `receivedAt` come from the latest response. */
export function useCountdown(remainingSeconds?: number, receivedAt?: number) {
  const [now, setNow] = useState(Date.now());
  const running = remainingSeconds !== undefined && remainingSeconds > 0;
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [running]);
  return remainingSeconds === undefined ? 0 : remainingFrom(remainingSeconds, receivedAt ?? now, now);
}

/** Records tab switches and fullscreen exits for an open mock, wherever the learner is working. Not proctoring. */
export function useIntegritySignals(mockId: string | undefined, report: (kind: string) => void) {
  useEffect(() => {
    if (!mockId) return;
    const onHidden = () => document.visibilityState === "hidden" && report("tab");
    const onFullscreen = () => !document.fullscreenElement && report("fullscreen");
    document.addEventListener("visibilitychange", onHidden);
    document.addEventListener("fullscreenchange", onFullscreen);
    return () => {
      document.removeEventListener("visibilitychange", onHidden);
      document.removeEventListener("fullscreenchange", onFullscreen);
    };
  }, [mockId]);
}
