"use client";

import { useEffect, useState, type ReactNode } from "react";

type Step = { title: string; body: ReactNode; next: string };

/**
 * A self-study session after the chapter (his request 20/11/2026), one stage at a time, ONE button at the end of each:
 * the multiple-choice quiz (understanding) -> "what does this code do" questions -> the practical work (= today's part
 * of the project) -> "finished the session". Stages already done stay open above; where he stopped is remembered.
 */
export default function SelfSteps({ id, steps, finish }: { id: string; steps: Step[]; finish: ReactNode }) {
  const key = `selfstep-${id}`;
  const [at, setAt] = useState(0);
  useEffect(() => {
    try {
      const n = Number(localStorage.getItem(key));
      if (n > 0) setAt(Math.min(n, steps.length - 1)); // eslint-disable-line react-hooks/set-state-in-effect
    } catch { /* private mode: start at the quiz */ }
  }, [key, steps.length]);
  const go = (n: number) => {
    setAt(n);
    try { localStorage.setItem(key, String(n)); } catch { /* not kept */ }
    setTimeout(() => document.getElementById(`${key}-${n}`)?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  };
  return (
    <section className="space-y-4">
      {steps.slice(0, at + 1).map((s, i) => (
        <div key={s.title} id={`${key}-${i}`} className="card space-y-3">
          <h2 className="font-semibold">{i + 1}. {s.title}</h2>
          {s.body}
          {i === at && (i < steps.length - 1
            ? <button type="button" className="btn w-full" onClick={() => go(i + 1)}>{s.next}</button>
            : finish)}
        </div>
      ))}
    </section>
  );
}
