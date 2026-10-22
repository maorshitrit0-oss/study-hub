"use client";

import { useState } from "react";
import { answerQuestion } from "@/app/(app)/actions";
import type { Question } from "@/lib/types";

type Q = Omit<Question, "correct" | "explanation"> & { explanation?: string | null };

/** One question at a time; the correct answer is revealed by the server after answering. */
export default function Quiz({ questions, title = "שאלון" }: { questions: Q[]; title?: string }) {
  const [i, setI] = useState(0);
  const [chosen, setChosen] = useState<number | null>(null);
  const [correct, setCorrect] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [busy, setBusy] = useState(false);
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
  async function pick(k: number) {
    if (chosen !== null || busy) return;
    setBusy(true);
    setChosen(k);
    const c = await answerQuestion(q.id, k);
    setCorrect(c);
    if (c === k) setScore((s) => s + 1);
    setBusy(false);
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-sm text-muted">
        <span>{title}</span>
        <span>{i + 1} / {questions.length}{q.topic ? ` · ${q.topic}` : ""}</span>
      </div>
      <p className="font-medium text-lg leading-relaxed whitespace-pre-line">{q.question}</p>
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
                <span className="whitespace-pre-line">{opt}</span>
              </button>
            </li>
          );
        })}
      </ol>
      {correct !== null && (
        <div className={`rounded-xl p-3 ${chosen === correct ? "bg-good-soft" : "bg-bad-soft"}`}>
          <p className="font-semibold mb-1">{chosen === correct ? "נכון ✓" : `לא נכון - התשובה היא ${correct + 1}`}</p>
          {q.explanation && <p className="text-sm whitespace-pre-line">{q.explanation}</p>}
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
