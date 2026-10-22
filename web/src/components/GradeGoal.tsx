"use client";

import { useState } from "react";
import { setGradeRow } from "@/app/(app)/actions";
import { forProjection, needed, num, pending, totals, type GradeRow } from "@/lib/gradeGoal";
import { REST } from "@/lib/degreePlan";

const fmt = (x: number | null) => (x === null ? "—" : x.toFixed(1));

/**
 * What grades are needed for a target average: by the end of this year, and by the end of the degree
 * (the rest of the degree is in the sheet as rows without a grade). Expected grades can be typed in to see the effect.
 */
export default function GradeGoal({ rows: all }: { rows: GradeRow[] }) {
  const [target, setTarget] = useState(90);
  const [expected, setExpected] = useState<Record<string, number>>({});
  const now = totals(all); // today's official average, failed grades included
  const rows = forProjection(all); // the future: a retake's grade replaces the failed one
  const base = totals(rows, expected);
  const open = pending(rows).filter((r) => Number(r.credits) > 0);
  const free = (list: GradeRow[]) => list.filter((r) => expected[r.id] === undefined).reduce((a, r) => a + Number(r.credits), 0);
  const thisYear = open.filter((r) => r.academic_year !== REST);
  const needYear = needed(target, base.sum, base.credits, free(thisYear));
  const needDegree = needed(target, base.sum, base.credits, free(open));
  const missingCredits = pending(rows).filter((r) => !(Number(r.credits) > 0));
  const replaced = all.filter((r) => !rows.includes(r));
  // Ending average if every course left gets the same grade.
  const endWith = (g: number) => { const t = totals(rows, Object.fromEntries(open.map((r) => [r.id, expected[r.id] ?? g]))); return t.sum / t.credits; };

  const row = (r: GradeRow, need: number | null) => {
    const mine = expected[r.id];
    return (
      <li key={r.id} className="py-2 flex justify-between items-center gap-3">
        <span className="min-w-0">
          <span className="font-medium">{r.name}</span>
          <span className="block text-xs text-muted">{Number(r.credits)} נק&quot;ז</span>
        </span>
        <span className="flex items-center gap-2 shrink-0">
          {mine === undefined && need !== null && (
            <span className={`font-bold ${need > 100 ? "text-bad" : "text-accent"}`}>{need > 100 ? ">100" : Math.ceil(need)}</span>
          )}
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
  };

  return (
    <section className="card space-y-4">
      <h2 className="font-semibold">🎯 יעד ממוצע</h2>
      <label className="text-sm block">ממוצע יעד
        <input className="input mt-1" type="number" min={60} max={100} value={target} onChange={(e) => setTarget(Number(e.target.value) || 0)} />
      </label>
      <p className="text-xs text-muted">ממוצע מצטבר היום: <b>{fmt(now.credits ? now.sum / now.credits : null)}</b> ({now.credits} נק&quot;ז עם ציון). המספר ליד כל קורס = הציון הממוצע שצריך בכל מה שנשאר עד סוף התואר. אפשר לכתוב ציון צפוי בקורס, והשאר מתעדכן.</p>

      {missingCredits.length > 0 && (
        <div className="rounded-xl bg-warn-soft p-3 text-sm space-y-2">
          <p>לקורסים האלה חסרות נקודות זכות (מלא, או מחק ב-× ברשימה למטה אם זה כפול):</p>
          {missingCredits.map((r) => (
            <label key={r.id} className="flex justify-between items-center gap-2">
              <span>{r.name}</span>
              <input className="input w-24" type="number" step="0.5" min={0} max={10} placeholder="נק״ז"
                onBlur={(e) => e.target.value && setGradeRow(r.id, { credits: Number(e.target.value) })} />
            </label>
          ))}
        </div>
      )}

      <div className="rounded-xl bg-accent-soft p-3 text-sm space-y-1.5">
        <p>
          {needYear === null ? "" : needYear <= 100
            ? <>עד סוף השנה: ממוצע <b>{Math.ceil(needYear)}</b> בקורסים של השנה מביא ל-{target}.</>
            : <>עד סוף השנה ל-{target}: <b>לא אפשרי</b> (היה צריך {fmt(needYear)}).</>}
        </p>
        <p>
          {needDegree === null ? "" : needDegree <= 100
            ? <>עד סוף התואר: צריך ממוצע <b>{fmt(needDegree)}</b> בכל מה שנשאר ({free(open)} נק&quot;ז).</>
            : <>עד סוף התואר ל-{target}: <b>לא אפשרי</b> (היה צריך {fmt(needDegree)}) - כדאי לבחור יעד נמוך יותר.</>}
        </p>
        <p className="text-muted">אם תקבל בכל מה שנשאר 85 / 90 / 95 - תסיים עם {fmt(endWith(85))} / {fmt(endWith(90))} / {fmt(endWith(95))}.</p>
      </div>

      {replaced.map((r) => (
        <p key={r.id} className="text-sm">🔁 {r.name} ({r.grade}) לא נכלל בחישוב העתידי: הציון בקורס החוזר מחליף אותו.</p>
      ))}
      <p className="text-xs text-muted">
        בסוף התואר הממוצע יהיה על {totals(rows, Object.fromEntries(open.map((r) => [r.id, 0]))).credits} נק&quot;ז:
        {" "}{base.credits - (expected ? Object.keys(expected).reduce((a, id) => a + Number(open.find((r) => r.id === id)?.credits ?? 0), 0) : 0)} שכבר יש בהם ציון + {open.reduce((a, r) => a + Number(r.credits), 0)} שעוד לפניך. כל קורס נספר פעם אחת.
      </p>

      <details open>
        <summary className="cursor-pointer text-sm font-semibold">רשום השנה ({thisYear.length} קורסים, {thisYear.reduce((a, r) => a + Number(r.credits), 0)} נק&quot;ז)</summary>
        <ul className="divide-y divide-line">{thisYear.map((r) => row(r, needDegree))}</ul>
      </details>
      <details open>
        <summary className="cursor-pointer text-sm font-semibold">עוד לא נלקח ({open.length - thisYear.length} פריטים, {open.filter((r) => r.academic_year === REST).reduce((a, r) => a + Number(r.credits), 0)} נק&quot;ז)</summary>
        <ul className="divide-y divide-line">{open.filter((r) => r.academic_year === REST).map((r) => row(r, needDegree))}</ul>
      </details>
    </section>
  );
}
