"use client";

import { useState } from "react";
import { answerQuestion } from "@/app/(app)/actions";
import type { Question } from "@/lib/types";
import { Rich } from "./Chapter";

type Q = Omit<Question, "explanation"> & { explanation?: string | null };

/**
 * The order the options are shown in (06/11/2026, he noticed the right answer was almost always first): a fixed shuffle
 * per question (seeded by its id, so it does not jump on reload), the same for old and new quizzes. Answers are still
 * recorded by the original index.
 */
function order(id: string, n: number) {
  let h = 2166136261;
  for (let i = 0; i < id.length; i++) h = Math.imul(h ^ id.charCodeAt(i), 16777619);
  const rnd = () => { h = Math.imul(h ^ (h >>> 15), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909); h ^= h >>> 16; return (h >>> 0) / 4294967296; };
  const p = Array.from({ length: n }, (_, k) => k);
  for (let k = n - 1; k > 0; k--) { const j = Math.floor(rnd() * (k + 1)); [p[k], p[j]] = [p[j], p[k]]; }
  return p;
}

/**
 * One question at a time; feedback is instant and the answer is recorded in the background. "לא יודע" shows the answer
 * with its explanation instead of a random guess; it counts as a miss (chosen -1), so the topic comes back in review.
 */
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
  const shown = order(q.id, q.options.length); // shown[k] = original index of the option shown at place k
  const right = shown.indexOf(q.correct);
  function pick(k: number) {
    if (chosen !== null || correct !== null) return;
    setChosen(k);
    setCorrect(right);
    if (right === k) setScore((s) => s + 1);
    answerQuestion(q.id, k < 0 ? -1 : shown[k]).catch(() => {});
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-sm text-muted">
        <span>{title}</span>
        <span>{i + 1} / {questions.length}{q.topic ? ` · ${q.topic}` : ""}</span>
      </div>
      <div className="font-medium text-lg leading-relaxed"><Rich text={q.question} /></div>
      <ol className="space-y-2">
        {shown.map((orig, k) => {
          const opt = q.options[orig];
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
      {correct === null && (
        <button className="btn-ghost w-full" onClick={() => pick(-1)}>🤷 לא יודע - תראה לי את התשובה</button>
      )}
      {correct !== null && (
        <div className={`rounded-xl p-3 ${chosen === correct ? "bg-good-soft" : "bg-bad-soft"}`}>
          <p className="font-semibold mb-1">{chosen === correct ? "נכון ✓" : chosen === -1 ? `התשובה היא ${correct + 1} - קרא את ההסבר` : `לא נכון - התשובה היא ${correct + 1}`}</p>
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
