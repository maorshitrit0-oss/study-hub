import { forProjection, num, type GradeRow } from "./gradeGoal";

// A realistic expected grade per course still without one. Starts from his own record in similar courses and
// moves with what he does this semester (quiz accuracy, reading vs the class). Every new grade refines it.

type Cat = "lab" | "computers" | "physics" | "signals" | "circuits" | "math" | "project" | "other";
const CAT_LABEL: Record<Cat, string> = {
  lab: "מעבדות", computers: "תכנות ומחשבים", physics: "פיזיקה, שדות והתקנים", signals: "אותות ומערכות",
  circuits: "מעגלים", math: "מתמטיקה", project: "פרויקטים", other: "כל הקורסים",
};
// Order matters, and Hebrew has no \b: "גלים" must not match inside "מעגלים", "מעבד" not inside "מיקרו מעבדים".
const RULES: [Cat, RegExp][] = [
  ["lab", /מעבדה|מעבדת/],
  ["project", /פרויקט/],
  ["math", /חשבון|אלגברה|משוואות|הסתברות|אנליזה/],
  ["computers", /java|פייתון|תכנות|מחשב|מיקרו מעבד|vhdl|מתוכנת|ספרתיות|תכנון vlsi/i],
  ["physics", /פיזיק|שדות|(^|\s)גלים|התקני|מל"מ|אלקטרומגנט|תורת החשמל|vlsi|גלאים|אמינות|אופטו/i],
  ["signals", /אותות|בקרה|תקשורת|עיבוד/],
  ["circuits", /מעגל|הנדסת חשמל|electronic/i],
];
export const categoryOf = (name: string): Cat => RULES.find(([, re]) => re.test(name))?.[0] ?? "other";

export type Signals = { answered: number; correct: number; read: number; classLessons: number };
export type Prediction = { grade: number; why: string[]; confidence: "נמוכה" | "בינונית" | "גבוהה" };

function avg(rows: GradeRow[]) {
  let s = 0, c = 0;
  for (const r of rows) {
    const g = num(r.grade), k = Number(r.credits);
    if (g !== null && k > 0 && !r.failed) { s += g * k; c += k; }
  }
  return c ? { value: s / c, credits: c } : null;
}

export function predict(all: GradeRow[], signals: Map<string, Signals>) {
  const rows = forProjection(all);
  const graded = rows.filter((r) => num(r.grade) !== null);
  const overall = avg(graded);
  const out = new Map<string, Prediction>();
  for (const r of rows.filter((x) => !x.grade && Number(x.credits) > 0)) {
    const cat = categoryOf(r.name);
    const same = avg(graded.filter((g) => categoryOf(g.name) === cat));
    // Too little history in the category: lean on the overall average.
    const base = same && same.credits >= 4 ? same.value : overall?.value ?? 80;
    const why = [same && same.credits >= 4
      ? `הבסיס: הממוצע שלך ב${CAT_LABEL[cat]} (${same.value.toFixed(0)})`
      : `הבסיס: הממוצע הכללי שלך (${(overall?.value ?? 80).toFixed(0)})`];
    let grade = base;
    let evidence = 0;
    const s = signals.get(r.id);
    if (s && s.answered >= 15) {
      const acc = (100 * s.correct) / s.answered;
      const adj = Math.max(-10, Math.min(8, (acc - 80) * 0.4));
      grade += adj;
      evidence++;
      why.push(`שאלונים: ${acc.toFixed(0)}% נכון מתוך ${s.answered} (${adj >= 0 ? "+" : ""}${adj.toFixed(1)})`);
    } else if (s) {
      why.push(`שאלונים: עוד מעט תשובות (${s.answered}) - כדי לדייק צריך לפחות 15`);
    }
    if (s && s.classLessons >= 2) {
      const ratio = s.read / s.classLessons;
      const adj = ratio < 0.5 ? -3 : ratio >= 1 ? 2 : 0;
      grade += adj;
      evidence++;
      why.push(`קריאה: ${s.read} מתוך ${s.classLessons} שיעורים (${adj >= 0 ? "+" : ""}${adj})`);
    }
    if (r.code && all.some((x) => x.failed && x.code === r.code)) why.push("קורס חוזר: הציון החדש יחליף את הקודם");
    out.set(r.id, {
      grade: Math.round(Math.max(55, Math.min(100, grade))),
      why,
      confidence: evidence >= 2 ? "גבוהה" : evidence === 1 ? "בינונית" : "נמוכה",
    });
  }
  return out;
}
