"use client";

import { useState } from "react";
import { answerQuestion } from "@/app/(app)/actions";
import type { Question } from "@/lib/types";
import { Rich } from "./Chapter";

type Q = Omit<Question, "explanation"> & { explanation?: string | null };

/** One question at a time; feedback is instant and the answer is recorded in the background. */
export default function Quiz({ questions, title = "שאלון" }: { questions: Q[]; title?: string }) {
  const [i, setI] = useState(0);
  const [chosen, setChosen] = useState<number | null>(null);
  const [correct, setCorrect] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const done = i >= questions.length;

  if (!questions.length) return <p className="text-muted">אין שאלות.</p>;

  if (done) {
    const p = Math.round((100 * score) / questions.length);
    return (
      <div className="text-center space-y-3 py-4">
        <div className="text-4xl font-bold">{p}%</div>
        <p>{score} מתוך {questions.length} נכונות. {p >= 85 ? "מצוין! 🎉" : p >= 70 ? "טוב, יש מה לחזק." : "שווה לחזור על הפרק ולנסות שוב."}</p>
        <button className="btn" onClick={() => { setI(0); setScore(0); setChosen(null); setCorrect(null); }}>שוב</button>
      </div>
    );
  }

  const q = questions[i];
  function pick(k: number) {
    if (chosen !== null) return;
    setChosen(k);
    setCorrect(q.correct);
    if (q.correct === k) setScore((s) => s + 1);
    answerQuestion(q.id, k).catch(() => {});
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-sm text-muted">
        <span>{title}</span>
        <span>{i + 1} / {questions.length}{q.topic ? ` · ${q.topic}` : ""}</span>
      </div>
      <div className="font-medium text-lg leading-relaxed"><Rich text={q.question} /></div>
      <ol className="space-y-2">
        {q.options.map((opt, k) => {
          let cls = "border-line";
          if (correct !== null && k === correct) cls = "border-good bg-good-soft";
          else if (chosen === k && correct !== null) cls = "border-bad bg-bad-soft";
          else if (chosen === k) cls = "border-accent";
          return (
            <li key={k}>
              <button onClick={() => pick(k)} disabled={chosen !== null}
                className={`w-full text-start flex gap-3 items-start rounded-xl border-2 px-3 py-3 ${cls}`}>
                <span className="font-bold text-muted">{k + 1}.</span>
                <span className="min-w-0"><Rich text={opt} /></span>
              </button>
            </li>
          );
        })}
      </ol>
      {correct !== null && (
        <div className={`rounded-xl p-3 ${chosen === correct ? "bg-good-soft" : "bg-bad-soft"}`}>
          <p className="font-semibold mb-1">{chosen === correct ? "נכון ✓" : `לא נכון - התשובה היא ${correct + 1}`}</p>
          {q.explanation && <div className="text-sm"><Rich text={q.explanation} /></div>}
        </div>
      )}
      {correct !== null && (
        <button className="btn w-full" onClick={() => { setI(i + 1); setChosen(null); setCorrect(null); }}>
          {i + 1 < questions.length ? "לשאלה הבאה" : "לסיכום"}
        </button>
      )}
    </div>
  );
}
