"use client";

import { useState } from "react";
import { setGradeRow } from "@/app/(app)/actions";
import { needed, num, pending, totals, type GradeRow } from "@/lib/gradeGoal";
import { REST } from "@/lib/degreePlan";

const fmt = (x: number | null) => (x === null ? "—" : x.toFixed(1));

/**
 * What grades are needed for a target average: by the end of this year, and by the end of the degree
 * (the rest of the degree is in the sheet as rows without a grade). Expected grades can be typed in to see the effect.
 */
export default function GradeGoal({ rows }: { rows: GradeRow[] }) {
  const [target, setTarget] = useState(90);
  const [expected, setExpected] = useState<Record<string, number>>({});
  const now = totals(rows);
  const base = totals(rows, expected);
  const open = pending(rows).filter((r) => Number(r.credits) > 0);
  const free = (list: GradeRow[]) => list.filter((r) => expected[r.id] === undefined).reduce((a, r) => a + Number(r.credits), 0);
  const thisYear = open.filter((r) => r.academic_year !== REST);
  const needYear = needed(target, base.sum, base.credits, free(thisYear));
  const needDegree = needed(target, base.sum, base.credits, free(open));
  const missingCredits = pending(rows).filter((r) => !(Number(r.credits) > 0));
  const failed = rows.filter((r) => r.failed && Number(r.credits) > 0);
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

      {failed.map((r) => {
        const replaced = totals(rows.filter((x) => x.id !== r.id), Object.fromEntries(open.map((o) => [o.id, expected[o.id] ?? target])));
        return (
          <p key={r.id} className="text-sm">
            💡 {r.name} ({r.grade}) נספר היום בממוצע. אם בקורס החוזר הציון החדש <b>מחליף</b> את הישן, ובכל מה שנשאר תקבל {target} -
            תסיים עם <b>{fmt(replaced.sum / replaced.credits)}</b> (במקום {fmt(endWith(target))}).
            <span className="text-muted"> לבדוק בתקנון של אריאל איזה ציון נספר בקורס חוזר.</span>
          </p>
        );
      })}

      <details>
        <summary className="cursor-pointer text-sm font-semibold">השנה ({thisYear.length} קורסים)</summary>
        <ul className="divide-y divide-line">{thisYear.map((r) => row(r, needDegree))}</ul>
      </details>
      <details>
        <summary className="cursor-pointer text-sm font-semibold">עד סוף התואר ({open.length - thisYear.length} פריטים)</summary>
        <ul className="divide-y divide-line">{open.filter((r) => r.academic_year === REST).map((r) => row(r, needDegree))}</ul>
      </details>
    </section>
  );
}
