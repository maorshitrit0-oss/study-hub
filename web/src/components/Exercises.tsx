"use client";
import { fixArabic } from "@/lib/math";

import { useState } from "react";
import { toggleExercise } from "@/app/(app)/actions";
import Chapter from "./Chapter";

export type Exercise = {
  id: string; title: string | null; question_md: string; solution_md: string | null; topic: string | null;
  source: string; exam_style: boolean; uncertain: boolean; done_at: string | null; label?: string;
  why?: string; // a core exercise: why it was picked (exercise_core.json)
  where?: string; // the exact page / slide in the source (worker/locate.py, or the core pick's "where")
};

/**
 * An exercise written as an exam multiple-choice question (Java / micro, 18/11/2026): "**א.** ..." options and a
 * solution that starts "התשובה: **X**". Then he clicks an answer, sees right / wrong, and the solution opens.
 */
// An option line: "**א.** ...", "**א.**...", "א. ...", "(א) ...", "- **א)** ..." - Gemini writes all of these (his screenshot
// 24/11/2026: an exam-style exercise showed its options as text instead of buttons).
const OPT = /(?:^|\n)[ \t]*(?:[-*][ \t]+)?(?:\*\*)?\(?([אבגד])[.)](?:\*\*)?[ \t]+/g;

function mcqOf(q: string, sol: string | null) {
  // "התשובה: **ב**" at the start, or "לכן התשובה הנכונה היא **א**." at the end (Gemini's drills, 24/11/2026); the
  // options block in the question is what makes it a multiple-choice exercise, so a phrase anywhere is safe.
  sol = sol ? fixArabic(sol) : sol;  // "התשובה הנכונה هي ב'" - Gemini slipped into Arabic (24/11/2026)
  const answer = sol?.match(/התשובה(?:\s+הנכונה)?(?:\s+היא)?\s*:?\s*\*\*\s*\(?([אבגד])/)?.[1]
    ?? sol?.match(/התשובה\s+הנכונה(?:\s+היא)?\s*:?\s*\(?([אבגד])['׳]?(?![\u0590-\u05FF])/)?.[1];
  const marks = [...q.matchAll(OPT)];
  const start = marks.findIndex((m) => m[1] === "א");
  if (!answer || start < 0) return null;
  const opts = marks.slice(start);
  // the options must be א, ב, ג... in order
  if (opts.some((m, i) => m[1] !== "אבגד"[i])) return null;
  const options = opts.map((m, i) => ({
    letter: m[1],
    md: q.slice(m.index! + m[0].length, i + 1 < opts.length ? opts[i + 1].index : q.length).replace(/\n\n✍️[\s\S]*$/, "").trim(),
  }));
  return options.length >= 2 ? { stem: q.slice(0, opts[0].index), options, answer } : null;
}

/** The formula(s) the solution uses, without the substitution or the result (his request 19/11/2026: he does not know
 *  the formulas by heart and not all are on the formula sheet - he wants the formula, then solves alone). */
function formulaOf(sol: string | null): string | null {
  if (!sol) return null;
  const lines = sol.split("\n");
  const out: string[] = [];
  for (let i = 0; i < lines.length && out.length < 4; i++) {
    const l = lines[i];
    if (/למה לא/.test(l)) break;  // the wrong-options notes are not formulas
    if (!/נוסח[הא]|הקשרים|הכלי/.test(l) || /הצבה|תוצאה/.test(l) || /^\s*-/.test(l)) continue;
    if (l.includes("$")) { out.push(l.replace(/^\*\*\d+\.\s*/, "**").replace(/^#+\s*/, "")); continue; }
    // "**נוסחה:**" with the formula in one of the next lines
    for (let j = i + 1; j < Math.min(lines.length, i + 5); j++) {
      if (/הצבה|תוצאה/.test(lines[j])) break;
      if (lines[j].trim() === "$$") {  // a block: "$$" alone, the formula, "$$" (24/11/2026: the hint showed empty)
        const end = lines.findIndex((x, k) => k > j && x.trim() === "$$");
        if (end > j) { out.push(lines.slice(j, end + 1).join("\n")); i = end; }
        break;
      }
      if (lines[j].includes("$$")) { out.push(lines[j]); i = j; break; }
    }
  }
  return out.length ? out.join("\n\n") : null;
}

const SOURCE: Record<string, string> = { lesson: "מהשיעור", homework: "שיעורי בית", exam: "מבחן קודם", sheet: "דף תרגילים" };

/** Exercises to solve on paper: the question, the solution hidden until he has tried, and "✓ פתרתי". */
export default function Exercises({ items, slideUrls = {} }: { items: Exercise[]; slideUrls?: Record<number, string> }) {
  const [done, setDone] = useState(() => new Set(items.filter((x) => x.done_at).map((x) => x.id)));
  const [picked, setPicked] = useState<Record<string, string>>({});
  // Another week's list in the same place (week tabs, 21/11/2026: his week 2 looked unsolved after opening week 3
  // first - the marks of the first list stayed): take the new list's marks.
  const itemsKey = items.map((x) => x.id + (x.done_at ? "1" : "0")).join(",");
  const [shownKey, setShownKey] = useState(itemsKey);
  if (shownKey !== itemsKey) {
    setShownKey(itemsKey);
    setDone(new Set(items.filter((x) => x.done_at).map((x) => x.id)));
    setPicked({});
  }
  if (!items.length) return <p className="text-sm text-muted">אין תרגילים.</p>;
  return (
    <ol className="space-y-4">
      {items.map((x, i) => {
        const solved = done.has(x.id);
        return (
          <li key={x.id} className={`rounded-xl border border-line p-3 ${solved ? "opacity-60" : ""}`}>
            <p className="font-semibold">{i + 1}. {x.title ?? "תרגיל"}</p>
            <p className="text-xs text-muted">
              מקור: {x.label ?? SOURCE[x.source] ?? "-"}{x.where ? ` · 📍 ${x.where}` : ""} · {SOURCE[x.source] ?? ""}{x.exam_style ? " · ⭐ סגנון מבחן" : ""}
            </p>
            {x.why && <p className="text-xs text-accent mt-1">🎯 למה עכשיו: {x.why}</p>}
            {formulaOf(x.solution_md) && (
              <details className="mt-2 rounded-xl bg-accent-soft p-2">
                <summary className="cursor-pointer text-sm text-accent">📐 הנוסחה לשאלה (בלי התשובה)</summary>
                <div className="mt-1"><Chapter md={formulaOf(x.solution_md)!} slideUrls={slideUrls} /></div>
              </details>
            )}
            {(() => {
              const m = mcqOf(x.question_md, x.solution_md);
              if (!m) return <div className="mt-2"><Chapter md={x.question_md} slideUrls={slideUrls} /></div>;
              const choice = picked[x.id];
              return (
                <div className="mt-2 space-y-2">
                  <Chapter md={m.stem} slideUrls={slideUrls} />
                  {m.options.map((o) => {
                    const tone = !choice ? "border-line" : o.letter === m.answer ? "border-good bg-good/10" : o.letter === choice ? "border-bad bg-bad/10" : "border-line opacity-60";
                    return (
                      <button key={o.letter} type="button" disabled={!!choice}
                        className={`w-full text-start rounded-xl border p-2 flex gap-2 items-start ${tone}`}
                        onClick={() => {
                          setPicked({ ...picked, [x.id]: o.letter });
                          if (o.letter === m.answer && !done.has(x.id)) {  // right on the first try = solved
                            setDone(new Set(done).add(x.id));
                            toggleExercise(x.id, true).catch(() => {});
                          }
                        }}>
                        <b>{o.letter}.</b><div className="flex-1 min-w-0"><Chapter md={o.md} slideUrls={slideUrls} /></div>
                      </button>
                    );
                  })}
                  {choice && (
                    <>
                      <p className={`font-semibold ${choice === m.answer ? "text-good" : "text-bad"}`}>
                        {choice === m.answer ? "✅ נכון!" : `❌ לא נכון – התשובה הנכונה: ${m.answer}`}
                      </p>
                      <p className="text-xs text-muted">✍️ עכשיו לכתוב במחברת את הנימוק, ולהשוות לפתרון:</p>
                      <div className="rounded-xl bg-bg p-2"><Chapter md={x.solution_md!} slideUrls={slideUrls} /></div>
                      <button type="button" className="text-xs text-accent" onClick={() => { const n = { ...picked }; delete n[x.id]; setPicked(n); }}>↺ לנסות שוב</button>
                    </>
                  )}
                </div>
              );
            })()}
            {x.solution_md && !mcqOf(x.question_md, x.solution_md) && (
              <details className="mt-2">
                <summary className="cursor-pointer text-sm text-accent">פתרון (קודם לפתור לבד על דף)</summary>
                {x.uncertain && <p className="text-sm text-warn mt-2">⚠️ לא בטוח בפתרון - לבדוק מול המרצה / הפתרון הרשמי.</p>}
                <div className="mt-2"><Chapter md={x.solution_md} slideUrls={slideUrls} /></div>
              </details>
            )}
            <button className={`mt-2 text-sm ${solved ? "text-good" : "text-muted"}`} onClick={() => {
              const next = new Set(done);
              if (solved) next.delete(x.id); else next.add(x.id);
              setDone(next);
              toggleExercise(x.id, !solved).catch(() => {});
            }}>{solved ? "✓ פתרתי · לבטל" : "◻ סמן שפתרתי"}</button>
          </li>
        );
      })}
    </ol>
  );
}
