"use client";

import { useState } from "react";
import { toggleExercise } from "@/app/(app)/actions";
import Chapter from "./Chapter";

export type Exercise = {
  id: string; title: string | null; question_md: string; solution_md: string | null; topic: string | null;
  source: string; exam_style: boolean; uncertain: boolean; done_at: string | null; label?: string;
};

const SOURCE: Record<string, string> = { lesson: "מהשיעור", homework: "שיעורי בית", exam: "מבחן קודם", sheet: "דף תרגילים" };

/** Exercises to solve on paper: the question, the solution hidden until he has tried, and "✓ פתרתי". */
export default function Exercises({ items, slideUrls = {} }: { items: Exercise[]; slideUrls?: Record<number, string> }) {
  const [done, setDone] = useState(() => new Set(items.filter((x) => x.done_at).map((x) => x.id)));
  if (!items.length) return <p className="text-sm text-muted">אין תרגילים.</p>;
  return (
    <ol className="space-y-4">
      {items.map((x, i) => {
        const solved = done.has(x.id);
        return (
          <li key={x.id} className={`rounded-xl border border-line p-3 ${solved ? "opacity-60" : ""}`}>
            <div className="flex justify-between items-start gap-2">
              <p className="font-semibold">{i + 1}. {x.title ?? "תרגיל"}</p>
              <span className="text-xs text-muted shrink-0">
                {x.exam_style && "⭐ סגנון מבחן · "}{x.label ?? SOURCE[x.source] ?? ""}
              </span>
            </div>
            <div className="mt-2"><Chapter md={x.question_md} slideUrls={slideUrls} /></div>
            {x.solution_md && (
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
