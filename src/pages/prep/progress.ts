type Attempt = { challengeId: string; correct: boolean };

/** A guide is passed once each of its questions has at least one correct attempt. */
export function guidePassed(challengeIds: string[], attempts: Attempt[]) {
  if (!challengeIds.length) return false;
  const right = new Set(attempts.filter((a) => a.correct).map((a) => a.challengeId));
  return challengeIds.every((id) => right.has(id));
}

export function trackProgress(guides: { track: string; challengeIds: string[] }[], attempts: Attempt[]) {
  const out: Record<string, { passed: number; total: number }> = {};
  for (const g of guides) {
    const row = (out[g.track] ??= { passed: 0, total: 0 });
    row.total++;
    if (guidePassed(g.challengeIds, attempts)) row.passed++;
  }
  return out;
}
