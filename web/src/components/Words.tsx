"use client";

import { useMemo, useState } from "react";
import { deleteTerm } from "@/app/(app)/actions";
import type { Term } from "@/lib/glossary";

const MISSES = "words-missed";
const SIZE = 15;

function loadMisses(): Record<string, number> {
  try { return JSON.parse(localStorage.getItem(MISSES) || "{}"); } catch { return {}; }
}
function saveMisses(m: Record<string, number>) {
  try { localStorage.setItem(MISSES, JSON.stringify(m)); } catch { /* private mode */ }
}
const key = (t: Term) => t.en.toLowerCase();

type Card = { term: Term; toHebrew: boolean; options: string[]; correct: number };

/** A quiz round: words missed before come first; each asks English → Hebrew or the other way. */
function makeRound(terms: Term[]): Card[] {
  const misses = loadMisses();
  const unique = [...new Map(terms.map((t) => [key(t), t])).values()];
  const picked = unique.map((t) => ({ t, r: -(misses[key(t)] ?? 0) + Math.random() }))
    .sort((a, b) => a.r - b.r).slice(0, SIZE).map((x) => x.t);
  return picked.map((term) => {
    const toHebrew = Math.random() < 0.65;
    const answer = toHebrew ? term.he : term.en;
    const pool = [...new Set(unique.filter((o) => key(o) !== key(term)).map((o) => (toHebrew ? o.he : o.en)))]
      .filter((x) => x !== answer).sort(() => Math.random() - 0.5).slice(0, 3);
    const options = [...pool, answer].sort(() => Math.random() - 0.5);
    return { term, toHebrew, options, correct: options.indexOf(answer) };
  });
}

export default function Words({ terms, courseNames, showCourse }: { terms: Term[]; courseNames: Record<string, string>; showCourse: boolean }) {
  const [mode, setMode] = useState<"list" | "quiz">("list");
  const [filter, setFilter] = useState("");
  const shown = useMemo(() => {
    const f = filter.trim().toLowerCase();
    return terms.filter((t) => !f || t.en.toLowerCase().includes(f) || t.he.includes(f));
  }, [terms, filter]);

  if (!terms.length) return <p className="card text-sm text-muted">עוד אין מילים. הן נוספות אוטומטית עם כל פרק חדש.</p>;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <button className={mode === "list" ? "btn" : "btn-ghost"} onClick={() => setMode("list")}>📖 רשימת המילים ({terms.length})</button>
        <button className={mode === "quiz" ? "btn" : "btn-ghost"} onClick={() => setMode("quiz")} disabled={terms.length < 4}>✍️ חידון</button>
      </div>
      {mode === "quiz" ? <WordQuiz terms={terms} /> : (
        <div className="card space-y-2">
          <input className="input" placeholder="חיפוש באנגלית או בעברית" value={filter} onChange={(e) => setFilter(e.target.value)} />
          <ul className="divide-y divide-line">
            {shown.map((t) => (
              <li key={t.id} className="py-2.5 flex gap-3 items-start">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap gap-x-3 items-baseline">
                    <span className="font-semibold" dir="ltr">{t.en}</span>
                    <span>{t.he}</span>
                  </div>
                  {t.explanation && <p className="text-sm text-muted">{t.explanation}</p>}
                  {showCourse && <p className="text-xs text-muted">{courseNames[t.course_id]}</p>}
                </div>
                <button aria-label="מחיקה" className="text-muted px-1" onClick={() => confirm(`למחוק את "${t.en}"?`) && deleteTerm(t.id)}>×</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function WordQuiz({ terms }: { terms: Term[] }) {
  const [round, setRound] = useState<Card[]>(() => makeRound(terms));
  const [i, setI] = useState(0);
  const [chosen, setChosen] = useState<number | null>(null);
  const [score, setScore] = useState(0);

  if (i >= round.length) {
    return (
      <div className="card text-center space-y-3 py-6">
        <div className="text-4xl font-bold">{score} / {round.length}</div>
        <p className="text-sm text-muted">מילים שטעית בהן יחזרו בסבב הבא.</p>
        <button className="btn" onClick={() => { setRound(makeRound(terms)); setI(0); setScore(0); setChosen(null); }}>סבב נוסף</button>
      </div>
    );
  }
  const c = round[i];
  function pick(k: number) {
    if (chosen !== null) return;
    setChosen(k);
    const m = loadMisses();
    if (k === c.correct) {
      setScore((s) => s + 1);
      if (m[key(c.term)]) m[key(c.term)] -= 1;
    } else {
      m[key(c.term)] = (m[key(c.term)] ?? 0) + 2;
    }
    saveMisses(m);
  }

  return (
    <div className="card space-y-4">
      <div className="flex justify-between text-sm text-muted">
        <span>{c.toHebrew ? "מה התרגום לעברית?" : "איך אומרים באנגלית?"}</span>
        <span>{i + 1} / {round.length}</span>
      </div>
      <p className="text-2xl font-bold text-center py-2" dir={c.toHebrew ? "ltr" : "rtl"}>{c.toHebrew ? c.term.en : c.term.he}</p>
      <ol className="space-y-2">
        {c.options.map((o, k) => {
          let cls = "border-line";
          if (chosen !== null && k === c.correct) cls = "border-good bg-good-soft";
          else if (chosen === k) cls = "border-bad bg-bad-soft";
          return (
            <li key={k}>
              <button onClick={() => pick(k)} disabled={chosen !== null} dir={c.toHebrew ? "rtl" : "ltr"}
                className={`w-full text-start rounded-xl border-2 px-3 py-3 ${cls}`}>{o}</button>
            </li>
          );
        })}
      </ol>
      {chosen !== null && (
        <>
          <div className={`rounded-xl p-3 text-sm ${chosen === c.correct ? "bg-good-soft" : "bg-bad-soft"}`}>
            <p className="font-semibold"><span dir="ltr">{c.term.en}</span> = {c.term.he}</p>
            {c.term.explanation && <p>{c.term.explanation}</p>}
          </div>
          <button className="btn w-full" onClick={() => { setI(i + 1); setChosen(null); }}>
            {i + 1 < round.length ? "למילה הבאה" : "לסיכום"}
          </button>
        </>
      )}
    </div>
  );
}
