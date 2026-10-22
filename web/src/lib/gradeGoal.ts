// Grade-average math, matching the university sheet: numeric grades x credits / credits;
// failed courses count, "עבר" and 0-credit courses don't.

export type GradeRow = {
  id: string; academic_year: string; semester: string; code: string | null; name: string; credits: number | string;
  grade: string | null; failed: boolean;
};

export const num = (g: string | null) => (g !== null && g !== "" && Number.isFinite(Number(g)) ? Number(g) : null);

/** Sum of grade x credits and the credits behind it, over graded rows (optionally with expected grades). */
export function totals(rows: GradeRow[], expected: Record<string, number> = {}) {
  let sum = 0, credits = 0;
  for (const r of rows) {
    const g = num(r.grade) ?? expected[r.id] ?? null;
    const c = Number(r.credits);
    if (g !== null && c > 0) { sum += g * c; credits += c; }
  }
  return { sum, credits };
}

/** Average needed on `openCredits` more credits to reach `target`, given the current totals. */
export function needed(target: number, sum: number, credits: number, openCredits: number) {
  return openCredits > 0 ? (target * (credits + openCredits) - sum) / openCredits : null;
}

/** Rows without a grade yet (current semester and pending exams). */
export const pending = (rows: GradeRow[]) => rows.filter((r) => !r.grade);

/** Same course code (the university appends a group number: 002-4366110-01). */
export const sameCode = (a?: string | null, b?: string | null) => !!a && !!b && a.slice(0, 11) === b.slice(0, 11);
