import Link from "next/link";
import type { SupabaseClient } from "@supabase/supabase-js";
import { requireUser } from "@/lib/supabase/server";
import GradeGoal from "@/components/GradeGoal";
import { sameCode, type GradeRow } from "@/lib/gradeGoal";

const CURRENT_YEAR = 'תשפ"ז'; // academic year of the courses now in the app - update each year

/** Current courses get a grade row (no grade yet) so the target calculator includes them. */
async function addCurrentCourses(sb: SupabaseClient, rows: GradeRow[]) {
  const { data: courses } = await sb.from("courses").select("name, code, kind, semester").eq("archived", false).in("kind", ["course", "lab", "project"]);
  const add = (courses ?? []).filter((c) => !rows.some((r) => sameCode(r.code, c.code) || r.name === c.name))
    .map((c) => ({ academic_year: CURRENT_YEAR, semester: c.semester || "א", code: c.code ? c.code.slice(0, 11) : null, name: c.name, kind: c.kind === "lab" ? "מעבדה" : "הרצאה", credits: 0 }));
  if (add.length) await sb.from("grades").insert(add);
  return add.length;
}

type Grade = {
  id: string; academic_year: string; semester: string; code: string | null; name: string; kind: string | null;
  lecturer: string | null; credits: number; grade: string | null; failed: boolean;
};

const SEM_ORDER: Record<string, number> = { "א": 1, "ב": 2, "ק": 3 };
const SEM_LABEL: Record<string, string> = { "א": "סמסטר א", "ב": "סמסטר ב", "ק": "קיץ" };

/**
 * Average as the university computes it (checked against the official sheet of 07/10/2026):
 * numeric grades of courses with credit points, weighted by credits; failed courses count too.
 */
function average(rows: Grade[]) {
  let sum = 0, credits = 0;
  for (const r of rows) {
    const g = Number(r.grade), c = Number(r.credits);
    if (r.grade && Number.isFinite(g) && c > 0) {
      sum += g * c;
      credits += c;
    }
  }
  return credits ? (sum / credits).toFixed(2) : null;
}

export default async function GradesPage() {
  const { sb } = await requireUser();
  const load = () => sb.from("grades").select("*").order("academic_year").order("created_at");
  let { data, error } = await load();
  if (!error && (await addCurrentCourses(sb, (data ?? []) as GradeRow[]).catch(() => 0))) ({ data, error } = await load());
  const rows = (data ?? []) as Grade[];
  const years = [...new Set(rows.map((r) => r.academic_year))];
  const failed = rows.filter((r) => r.failed && r.credits > 0);
  const pending = rows.filter((r) => !r.grade);

  return (
    <div className="space-y-5">
      <Link href="/courses" className="text-sm text-accent">→ קורסים</Link>
      <h1 className="text-2xl font-bold">גיליון ציונים</h1>
      {error && <p className="card text-sm text-warn">צריך להריץ את קוד ה-SQL של הציונים ב-Supabase.</p>}

      {rows.length > 0 && (
        <div className="grid grid-cols-3 gap-2 text-center">
          {years.map((y) => (
            <div key={y} className="card p-3">
              <div className="text-xl font-bold">{average(rows.filter((r) => r.academic_year === y)) ?? "—"}</div>
              <div className="text-xs text-muted">ממוצע {y}</div>
            </div>
          ))}
          <div className="card p-3">
            <div className="text-xl font-bold text-accent">{average(rows) ?? "—"}</div>
            <div className="text-xs text-muted">ממוצע מצטבר</div>
          </div>
        </div>
      )}

      {rows.length > 0 && <GradeGoal rows={rows} />}

      {(failed.length > 0 || pending.length > 0) && (
        <section className="card text-sm space-y-1">
          {pending.map((r) => <p key={r.id}>⏳ עוד אין ציון: {r.name} ({r.academic_year} · {SEM_LABEL[r.semester] ?? r.semester})</p>)}
          {failed.map((r) => <p key={r.id} className="text-bad">⚠️ לא עבר: {r.name} ({r.grade}) - לבדוק אם צריך לחזור על הקורס או לגשת למועד נוסף</p>)}
        </section>
      )}

      {years.map((y) => {
        const inYear = rows.filter((r) => r.academic_year === y);
        const sems = [...new Set(inYear.map((r) => r.semester))].sort((a, b) => (SEM_ORDER[a] ?? 9) - (SEM_ORDER[b] ?? 9));
        return (
          <section key={y} className="card">
            <h2 className="font-semibold mb-2">{y}</h2>
            {sems.map((s) => (
              <div key={s} className="mb-3">
                <h3 className="text-sm text-muted mb-1">{SEM_LABEL[s] ?? s}</h3>
                <ul className="divide-y divide-line">
                  {inYear.filter((r) => r.semester === s).map((r) => (
                    <li key={r.id} className="flex justify-between gap-3 py-2">
                      <span className="min-w-0">
                        <span className="font-medium">{r.name}</span>
                        <span className="block text-xs text-muted">
                          {r.lecturer ?? ""}{r.credits ? ` · ${r.credits} נק"ז` : " · ללא נק\"ז"}
                        </span>
                      </span>
                      <span className={`font-bold shrink-0 ${r.failed ? "text-bad" : !r.grade ? "text-muted" : ""}`}>
                        {r.grade ?? "טרם נקבע"}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </section>
        );
      })}
      <p className="text-xs text-muted">ממוצע משוקלל לפי נקודות זכות, כמו בגיליון של האוניברסיטה (כולל קורסים שלא עברו; &quot;עבר&quot; וקורסים בלי נק&quot;ז לא נכנסים).</p>
    </div>
  );
}
