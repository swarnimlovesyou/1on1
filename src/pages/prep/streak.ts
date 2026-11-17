/** Correct answers in a row during this visit to a drill. */
export function nextStreak(streak: number, correct: boolean) {
  return correct ? streak + 1 : 0;
}
