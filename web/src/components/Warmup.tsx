"use client";

import Link from "next/link";
import Quiz from "./Quiz";
import type { Question } from "@/lib/types";

export type WarmLesson = { id: string; label: string; hasSummary: boolean };

/**
 * The warm-up before a class (his request 09/11/2026): a few short questions on the last lessons, then what to do by
 * the result - per lesson: all good, read the condensed summary, or read the full chapter.
 */
export default function Warmup({ questions, lessons, courseId }: { questions: Question[]; lessons: WarmLesson[]; courseId: string }) {
  return (
    <Quiz questions={questions} title="🔥 חימום" end={(results, again) => {
      const rows = lessons.map((l) => {
        const qs = questions.filter((q) => q.lesson_id === l.id);
        const ok = qs.filter((q) => results[q.id]).length;
        return { l, ok, n: qs.length, p: qs.length ? ok / qs.length : 1 };
      }).filter((r) => r.n > 0);
      const total = rows.reduce((a, r) => a + r.ok, 0);
      const all = rows.reduce((a, r) => a + r.n, 0);
      const weak = rows.filter((r) => r.p < 0.75);
      return (
        <div className="space-y-4 py-2">
          <div className="text-center">
            <div className="text-4xl font-bold">{all ? Math.round((100 * total) / all) : 0}%</div>
            <p className="mt-1">{total} מתוך {all} נכונות</p>
          </div>
          {weak.length === 0 ? (
            <p className="rounded-xl bg-good-soft p-3 text-center font-medium">🎉 אתה על החומר – אפשר להתחיל את השיעור הבא.</p>
          ) : (
            <p className="rounded-xl bg-accent-soft p-3 font-medium">לפני השיעור – לחזק את מה שמסומן למטה (בערך {weak.length * 15} דקות):</p>
          )}
          <ul className="space-y-2">
            {rows.map(({ l, ok, n, p }) => (
              <li key={l.id} className="rounded-xl border border-line p-3">
                <div className="flex justify-between gap-2">
                  <span className="font-medium">{l.label}</span>
                  <span className="text-sm text-muted">{ok}/{n}</span>
                </div>
                {p >= 0.75 ? (
                  <p className="text-sm text-good mt-1">✅ שולט – אין צורך לחזור</p>
                ) : p >= 0.5 || !l.hasSummary ? (
                  <Link href={`/lessons/${l.id}#${l.hasSummary ? "summary" : "chapter"}-${l.id}`} className="text-sm text-accent mt-1 block">
                    📝 לקרוא את {l.hasSummary ? "הסיכום המתומצת" : "הפרק"} ←
                  </Link>
                ) : (
                  <Link href={`/lessons/${l.id}#chapter-${l.id}`} className="text-sm text-bad mt-1 block">📖 לקרוא את הפרק המלא ←</Link>
                )}
              </li>
            ))}
          </ul>
          <div className="grid grid-cols-2 gap-2">
            <button className="btn-ghost" onClick={again}>שוב</button>
            <Link href={`/courses/${courseId}`} className="btn text-center">לקורס</Link>
          </div>
        </div>
      );
    }} />
  );
}
