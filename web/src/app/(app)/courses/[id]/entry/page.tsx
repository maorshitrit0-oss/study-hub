import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Quiz from "@/components/Quiz";
import EntryReport, { ReadEntryFiles, RetryReport } from "@/components/EntryReport";
import { Rich } from "@/components/Chapter";
import { fetchAll } from "@/lib/fetchAll";
import type { Question } from "@/lib/types";

// Turning a report into questions is one Gemini call with the experiment's booklet attached.
export const maxDuration = 300;

type EntryQ = Question & { source: string; experiment: number };

/** A mock quiz like the real one: 3 questions, mostly ones students were actually asked, wrong ones first. */
function mock(qs: EntryQ[], last: Map<string, boolean>) {
  const rank = (q: EntryQ) => (q.source === "entry_reported" ? 0 : 1) + (last.get(q.id) === false ? -0.5 : 0) + Math.random();
  return [...qs].sort((a, b) => rank(a) - rank(b)).slice(0, 3);
}

export default async function EntryQuiz({ params, searchParams }: PageProps<"/courses/[id]/entry">) {
  const { id } = await params;
  const sp = await searchParams;
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: labs }, { data: reports, error: missing }] = await Promise.all([
    sb.from("courses").select("name").eq("id", id).single(),
    sb.from("lessons").select("id, number, title").eq("course_id", id).eq("kind", "lab").order("number"),
    sb.from("entry_reports").select("id, experiment, text, status, error, material_id, created_at").eq("course_id", id).order("created_at", { ascending: false }),
  ]);
  if (!course) notFound();
  const questions = missing ? [] : await fetchAll<EntryQ>(() => sb.from("questions")
    .select("id, lesson_id, topic, question, options, correct, explanation, difficulty, source, experiment")
    .eq("course_id", id).not("source", "is", null).order("created_at").order("id"));
  const attempts = await fetchAll<{ question_id: string; is_correct: boolean }>(() => sb.from("attempts")
    .select("question_id, is_correct").eq("course_id", id).order("created_at").order("id"));
  const last = new Map(attempts.map((a) => [a.question_id, a.is_correct]));

  const experiments = [...new Set([...(labs ?? []).map((l) => l.number ?? 0), ...questions.map((q) => q.experiment)])]
    .filter((x) => x > 0).sort((a, b) => a - b);
  // Default: the newest experiment uploaded - the one coming up.
  const n = Number(sp.n) || experiments.at(-1) || 1;
  const mine = questions.filter((q) => q.experiment === n);
  const reported = mine.filter((q) => q.source === "entry_reported");
  const set = sp.all ? [...reported, ...mine.filter((q) => q.source !== "entry_reported")] : mock(mine, last);
  const lab = (labs ?? []).find((l) => l.number === n);

  return (
    <div className="space-y-4">
      <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course.name}</Link>
      <h1 className="text-2xl font-bold">🎯 בוחן כניסה</h1>
      {missing && <p className="card text-sm">צריך קודם להריץ ב-Supabase את הקובץ <code>supabase/entry_quiz.sql</code>.</p>}

      <div className="flex gap-2 flex-wrap">
        {experiments.map((x) => {
          const c = questions.filter((q) => q.experiment === x).length;
          return (
            <Link key={x} href={`/courses/${id}/entry?n=${x}`}
              className={`px-3 py-1.5 rounded-xl text-sm ${x === n ? "bg-accent text-white" : "bg-accent-soft text-accent"}`}>
              ניסוי {x}{c ? ` · ${c}` : ""}
            </Link>
          );
        })}
      </div>

      <section className="card space-y-3">
        <div className="flex justify-between items-center gap-2 flex-wrap">
          <h2 className="font-semibold">ניסוי {n}{lab?.title ? ` · ${lab.title}` : ""}</h2>
          <div className="flex gap-3 text-sm">
            <Link href={`/courses/${id}/entry?n=${n}&r=${(Number(sp.r) || 0) + 1}`} className="text-accent">🎲 בוחן דמה (3)</Link>
            <Link href={`/courses/${id}/entry?n=${n}&all=1`} className="text-accent">כל השאלות ({mine.length})</Link>
            {lab && <Link href={`/lessons/${lab.id}`} className="text-accent">📖 הפרק</Link>}
          </div>
        </div>
        <p className="text-sm text-muted">
          {reported.length} שאלות שסטודנטים באמת נשאלו, ועוד {mine.length - reported.length} שאלות דומות לתרגול.
          {sp.all ? " כל השאלות - קודם אלה שנשאלו." : " בוחן דמה כמו האמיתי: 3 שאלות, בעיקר כאלה שנשאלו."}
        </p>
        {set.length ? <Quiz key={set.map((q) => q.id).join()} questions={set} title="בוחן כניסה" />
          : <p className="text-muted">עוד אין שאלות לניסוי הזה. כשמישהו מהקבוצות של ראשון/שני מספר מה שאלו - להוסיף למטה.</p>}
      </section>

      {reported.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">מה שאלו בניסוי {n} - עם פתרון</h2>
          <ul className="divide-y divide-line">
            {reported.map((q) => (
              <li key={q.id} className="py-2">
                <details>
                  <summary className="cursor-pointer"><Rich text={q.question} /></summary>
                  <p className="mt-2 font-medium">✅ <Rich text={q.options[q.correct]} /></p>
                  {q.explanation && <div className="text-sm text-muted mt-1"><Rich text={q.explanation} /></div>}
                </details>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="card space-y-3">
        <h2 className="font-semibold">➕ מה שאלו? (מהקבוצות של ראשון ושני)</h2>
        <EntryReport courseId={id} userId={userId} experiment={n} experiments={experiments} />
        <ReadEntryFiles courseId={id} />
      </section>

      {(reports ?? []).length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">דיווחים</h2>
          <ul className="divide-y divide-line text-sm">
            {(reports ?? []).map((r) => (
              <li key={r.id} className="py-2">
                <span className="text-muted">{r.material_id ? "📂 קובץ" : `ניסוי ${r.experiment}`} · {new Date(r.created_at).toLocaleDateString("he-IL")} · </span>
                {r.status === "done" ? "✓" : r.status === "error" ? <>⚠️ {r.error} <RetryReport id={r.id} courseId={id} /></> : "בעבודה..."}
                {r.text && <p className="whitespace-pre-wrap line-clamp-3">{r.text}</p>}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
