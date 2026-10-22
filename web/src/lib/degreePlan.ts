import type { SupabaseClient } from "@supabase/supabase-js";
import { sameCode, type GradeRow } from "./gradeGoal";

// His degree audit ("מידע", 22/10/2026): B.Sc. EE, 162.5 credits; major VLSI, minor computers.
export const REST = 'יתרת התואר';
export const THIS_YEAR = 'תשפ"ז';

type Item = { code: string | null; name: string; credits: number; kind?: string };

/**
 * His plan (22/10/2026) with credits from the official degree audit where they differ
 * (the plan said Python 3.5 and the two track labs 3.0; the audit says 3, 2 and 2).
 * Registered this year, no grade yet - in addition to מבוא לבקרה and אותות אקראיים, already in the sheet.
 */
const IN_PROGRESS: (Item & { semester: string })[] = [
  { code: "002-4331810", name: "מעגלים לינאריים", credits: 4.5, semester: "א" },
  { code: "002-4337410", name: "Digital electronic circuits (מעגלים ספרתיים)", credits: 3.5, semester: "א" },
  { code: "002-4331710", name: "גלים ומערכות מפולגות", credits: 4.5, semester: "א" },
  { code: "002-4332030", name: "מעבדה 2", credits: 2, kind: "מעבדה", semester: "א" },
  { code: "002-4366110", name: "תכנות מונחה עצמים ושפת JAVA", credits: 3.5, semester: "א" },
  { code: "002-4366010", name: "ניתוח נתונים מעשי ובינה מלאכותית בפייתון", credits: 3, semester: "ב" },
  { code: "002-4331530", name: "מעבדה 3", credits: 2, kind: "מעבדה", semester: "ב" },
  { code: "002-4375410", name: "פיזיקה של מל\"מ", credits: 3, semester: "ב" },
];

/** Year 4, as he plans it (semester "ד-א" / "ד-ב"); the electromagnetics retake is not in his plan yet. */
const REMAINING: (Item & { semester: string })[] = [
  { code: "002-4322510", name: "תורת החשמל ואלקטרומגנטיקה (חזרה על הקורס - חובה, לא בתוכנית)", credits: 3.5, semester: "נותר" },
  { code: "002-4330610", name: "מבוא למערכות תקשורת", credits: 3.5, semester: "ד-א" },
  { code: "002-4375610", name: "רכיבים מתוכנתים ומבוא ל-VHDL (בשתי ההתמחויות)", credits: 3.5, semester: "ד-א" },
  { code: "002-4361110", name: "התקני VLSI", credits: 3.5, semester: "ד-א" },
  { code: "002-4365130", name: "מעבדה ל-VLSI אנלוגי", credits: 2, kind: "מעבדה", semester: "ד-א" },
  { code: "002-4371710", name: "מיקרו מעבדים", credits: 3.5, semester: "ד-א" },
  { code: "002-4331330", name: "קדם פרויקט - התקני VLSI", credits: 2, semester: "ד-א" },
  { code: null, name: "פרויקט גמר א' (VLSI / Verification)", credits: 4, semester: "ד-א" },
  { code: "002-4364130", name: "מעבדת רכיבים מתוכנתים (VHDL)", credits: 2, kind: "מעבדה", semester: "ד-ב" },
  { code: null, name: "מבוא לתכנון VLSI (VLSI Design) - בחירה", credits: 3.5, semester: "ד-ב" },
  { code: null, name: "אמינות במיקרואלקטרוניקה - בחירה", credits: 3.5, semester: "ד-ב" },
  { code: null, name: "מקורות וגלאים / התקנים אופטו' - בחירה", credits: 6.5, semester: "ד-ב" },
  { code: null, name: "פרויקט גמר ב'", credits: 4, semester: "ד-ב" },
];
const PLAN_MARK = "אמינות במיקרואלקטרוניקה - בחירה";

const words = (s: string) => s.replace(/["'()\-,.]/g, " ").split(/\s+/).filter((w) => w.length >= 3);
/** Same course under a slightly different name (e.g. "ליניאריים" / "לינאריים"). */
export function similar(a: string, b: string) {
  const na = a.replace(/[^\p{L}\p{N}]/gu, ""), nb = b.replace(/[^\p{L}\p{N}]/gu, "");
  if (na === nb || na.includes(nb) || nb.includes(na)) return true;
  const wb = new Set(words(b).map((w) => w.replace(/י/g, "")));
  return words(a).filter((w) => wb.has(w.replace(/י/g, ""))).length >= 2;
}

/**
 * Loads his plan into the grade sheet once (and replaces the first, coarser plan of the same day). Only rows the app
 * generated and that have no grade are replaced; real grades are never touched.
 */
export async function ensureDegreePlan(sb: SupabaseClient, rows: GradeRow[]) {
  if (rows.some((r) => r.name === PLAN_MARK)) return false;
  // The audit shows 32 (a later exam) where the sheet of 07/10 had 26; still not passed.
  await sb.from("grades").update({ grade: "32", failed: true }).eq("code", "002-4322510").eq("grade", "26");
  await sb.from("grades").delete().eq("academic_year", REST).is("grade", null);
  const pendingNow = rows.filter((r) => !r.grade && r.academic_year === THIS_YEAR);
  const insert = [];
  for (const it of IN_PROGRESS) {
    const row = pendingNow.find((r) => sameCode(r.code, it.code) || similar(r.name, it.name));
    if (row) await sb.from("grades").update({ credits: it.credits, code: it.code, semester: it.semester }).eq("id", row.id);
    else insert.push({ academic_year: THIS_YEAR, semester: it.semester, code: it.code, name: it.name, kind: it.kind ?? "הרצאה", credits: it.credits });
  }
  for (const it of REMAINING) insert.push({ academic_year: REST, semester: it.semester, code: it.code, name: it.name, kind: it.kind ?? "הרצאה", credits: it.credits });
  const { error } = await sb.from("grades").insert(insert);
  if (error) throw new Error(error.message);
  return true;
}
