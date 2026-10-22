"use client";

import { useState } from "react";
import { setGradeRow } from "@/app/(app)/actions";
import { needed, num, pending, totals, type GradeRow } from "@/lib/gradeGoal";

const fmt = (x: number | null) => (x === null ? "—" : x.toFixed(1));

/** What grades are needed to reach a target average: this semester, and until the end of the degree. */
export default function GradeGoal({ rows }: { rows: GradeRow[] }) {
  const [target, setTarget] = useState(90);
  const [degree, setDegree] = useState(160);
  const [expected, setExpected] = useState<Record<string, number>>({});
  const open = pending(rows);
  const now = totals(rows);
  const withExpected = totals(rows, expected);
  const openRows = open.filter((r) => Number(r.credits) > 0 && expected[r.id] === undefined);
  const openCredits = openRows.reduce((a, r) => a + Number(r.credits), 0);
  const need = needed(target, withExpected.sum, withExpected.credits, openCredits);
  const avgAfter = withExpected.credits ? withExpected.sum / withExpected.credits : null;

  // Until the end of the degree: credits left after everything listed (passed, graded, pending).
  const listed = rows.reduce((a, r) => a + Number(r.credits), 0);
  const left = Math.max(0, degree - listed);
  const needAll = needed(target, withExpected.sum, withExpected.credits, openCredits + left);
  const failed = rows.filter((r) => r.failed && Number(r.credits) > 0);
  const missingCredits = open.filter((r) => !(Number(r.credits) > 0));

  return (
    <section className="card space-y-4">
      <h2 className="font-semibold">🎯 יעד ממוצע</h2>
      <div className="grid grid-cols-2 gap-3">
        <label className="text-sm">ממוצע יעד
          <input className="input mt-1" type="number" min={60} max={100} value={target} onChange={(e) => setTarget(Number(e.target.value) || 0)} />
        </label>
        <label className="text-sm">נק&quot;ז בכל התואר
          <input className="input mt-1" type="number" min={100} max={200} value={degree} onChange={(e) => setDegree(Number(e.target.value) || 0)} />
        </label>
      </div>
      <p className="text-xs text-muted">ממוצע מצטבר היום: <b>{fmt(now.credits ? now.sum / now.credits : null)}</b> על {now.credits} נק&quot;ז עם ציון מספרי. סך נק&quot;ז בתואר - לבדוק בתקנון (160 הוא הערכה).</p>

      {missingCredits.length > 0 && (
        <div className="rounded-xl bg-warn-soft p-3 text-sm space-y-2">
          <p>חסרות נקודות זכות לקורסים האלה - מלא מתוך המידע/הסילבוס כדי שהחישוב יהיה נכון:</p>
          {missingCredits.map((r) => (
            <label key={r.id} className="flex justify-between items-center gap-2">
              <span>{r.name}</span>
              <input className="input w-24" type="number" step="0.5" min={0} max={10} placeholder="נק״ז"
                onBlur={(e) => e.target.value && setGradeRow(r.id, { credits: Number(e.target.value) })} />
            </label>
          ))}
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold mb-1">הקורסים שעוד אין בהם ציון</h3>
        <p className="text-xs text-muted mb-2">אפשר לכתוב ציון צפוי בקורס - והיעד בשאר יחושב מחדש.</p>
        <ul className="divide-y divide-line">
          {open.filter((r) => Number(r.credits) > 0).map((r) => {
            const mine = expected[r.id];
            return (
              <li key={r.id} className="py-2 flex justify-between items-center gap-3">
                <span className="min-w-0">
                  <span className="font-medium">{r.name}</span>
                  <span className="block text-xs text-muted">{Number(r.credits)} נק&quot;ז</span>
                </span>
                <span className="flex items-center gap-2 shrink-0">
                  {mine === undefined && <span className={`font-bold ${need !== null && need > 100 ? "text-bad" : "text-accent"}`}>{need === null ? "—" : need > 100 ? ">100" : Math.ceil(need)}</span>}
                  <input className="input w-20 text-center" type="number" min={0} max={100} placeholder="צפוי"
                    onChange={(e) => setExpected((x) => {
                      const v = num(e.target.value);
                      const next = { ...x };
                      if (v === null) delete next[r.id]; else next[r.id] = v;
                      return next;
                    })} />
                </span>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="rounded-xl bg-accent-soft p-3 text-sm space-y-1">
        {need !== null && (need <= 100
          ? <p>כדי להגיע ל-{target} כבר עכשיו: ממוצע <b>{Math.ceil(need)}</b> בקורסים שמסומנים למעלה.</p>
          : <p>להגיע ל-{target} כבר בסוף הסמסטר הזה <b>לא אפשרי</b> (צריך {fmt(need)}) - זה יעד לסוף התואר.</p>)}
        {Object.keys(expected).length > 0 && avgAfter !== null && <p>עם הציונים הצפויים שכתבת: ממוצע {fmt(avgAfter)}.</p>}
        {needAll !== null && (
          <p>עד סוף התואר (עוד כ-{left} נק&quot;ז אחרי הקורסים שברשימה): צריך ממוצע <b>{fmt(needAll)}</b> בכל מה שנשאר{needAll > 100 ? " - לא אפשרי, כדאי לבחור יעד אחר" : ""}.</p>
        )}
      </div>

      {failed.map((r) => {
        const fixed = totals(rows.map((x) => (x.id === r.id ? { ...x, grade: String(target) } : x)));
        return (
          <p key={r.id} className="text-sm">
            💡 {r.name} ({r.grade}): אם תחזור על הקורס ותקבל {target}, והציון החדש יחליף את הישן - הממוצע המצטבר יעלה ל-<b>{fmt(fixed.sum / fixed.credits)}</b>.
            <span className="text-muted"> (לבדוק בתקנון של אריאל איזה ציון נספר בקורס חוזר.)</span>
          </p>
        );
      })}
    </section>
  );
}
