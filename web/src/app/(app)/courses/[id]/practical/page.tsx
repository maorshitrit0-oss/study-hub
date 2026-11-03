import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Chapter from "@/components/Chapter";
import LabGraph, { type GraphSpec } from "@/components/LabGraph";
import VirtualLab from "@/components/VirtualLab";
import RebuildPractical from "@/components/RebuildPractical";

type Q = {
  id: number; experiment: number; type: "graph" | "theory" | "build"; source: string; question_md: string; answer_md: string;
  graph?: GraphSpec;
  build?: { goal?: string; circuit_md?: string; wiring_steps?: string[]; instruments?: string[]; expected?: string; mistakes?: string[] };
};
type Bank = { experiments: { n: number; title: string }[]; hints: string[]; questions: Q[] };

const TYPE = { graph: "📈 גרף", theory: "💡 תיאוריה", build: "🔧 בנייה" } as const;
const MIDTERM_LAST = 5; // the midterm covers experiments 1-5 (incl. 5)

/** A fixed pick for a given seed, so a mock exam stays the same until "another exam" is pressed. */
function pick<T>(list: T[], seed: number) {
  return list.length ? list[Math.abs(Math.imul(seed, 2654435761) >>> 0) % list.length] : undefined;
}

function Question({ q, n }: { q: Q; n?: number }) {
  return (
    <article className="card space-y-2">
      <p className="text-xs text-muted">{n ? `שאלה ${n} · ` : ""}{TYPE[q.type]} · ניסוי {q.experiment} · מקור: {q.source}</p>
      <Chapter md={q.question_md} slideUrls={{}} />
      {q.graph && <LabGraph g={q.graph} />}
      {q.type === "build" && <VirtualLab />}
      <details>
        <summary className="cursor-pointer text-sm text-accent">תשובה (קודם לנסות לבד)</summary>
        <div className="mt-2 space-y-3">
          <Chapter md={q.answer_md} slideUrls={{}} />
          {q.build && (
            <div className="space-y-2 text-sm">
              {q.build.circuit_md && <><h4 className="font-semibold">המעגל</h4><Chapter md={q.build.circuit_md} slideUrls={{}} /></>}
              {!!q.build.wiring_steps?.length && <><h4 className="font-semibold">חיווט על המטריצה</h4>
                <ol className="list-decimal ps-5 space-y-1">{q.build.wiring_steps.map((s, i) => <li key={i}>{s}</li>)}</ol></>}
              {!!q.build.instruments?.length && <><h4 className="font-semibold">הגדרות המכשירים</h4>
                <ul className="list-disc ps-5 space-y-1">{q.build.instruments.map((s, i) => <li key={i}>{s}</li>)}</ul></>}
              {q.build.expected && <><h4 className="font-semibold">מה אמור להופיע בסקופ</h4><p>{q.build.expected}</p></>}
              {!!q.build.mistakes?.length && <><h4 className="font-semibold">טעויות נפוצות</h4>
                <ul className="list-disc ps-5 space-y-1">{q.build.mistakes.map((s, i) => <li key={i}>{s}</li>)}</ul></>}
            </div>
          )}
        </div>
      </details>
    </article>
  );
}

/** The lab's practical exam: practice by experiment and type, or a mock exam (midterm 1-5 / final) of 3 questions. */
export default async function Practical({ params, searchParams }: PageProps<"/courses/[id]/practical">) {
  const { id } = await params;
  const sp = await searchParams;
  const { sb, userId } = await requireUser();
  const { data: course } = await sb.from("courses").select("name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const { data: file } = await sb.storage.from("study").download(`${userId}/materials/${id}/practical.json`);
  const bank: Bank | null = file ? JSON.parse(await file.text()) : null;
  const mode = (sp.mode as string) || "practice";
  const seed = Number(sp.seed) || 1;
  const exp = Number(sp.exp) || 0;
  const type = sp.type as Q["type"] | undefined;
  const tab = (m: string, label: string) => (
    <Link href={`/courses/${id}/practical?mode=${m}`}
      className={`px-3 py-1.5 rounded-xl text-sm ${mode === m ? "bg-accent text-white" : "bg-accent-soft text-accent"}`}>{label}</Link>
  );

  let body: React.ReactNode = <p className="card text-muted">מאגר השאלות עוד לא נבנה. הוא נבנה לבד מפרקי הניסויים, הדוחות המסכמים, הקלטות המרצה ובוחני הכניסה, כמה דקות אחרי שמעלים משהו.</p>;
  if (bank?.questions.length) {
    if (mode === "practice") {
      const list = bank.questions.filter((q) => (!exp || q.experiment === exp) && (!type || q.type === type));
      const chip = (q: string, label: string, on: boolean) => (
        <Link key={q} href={`/courses/${id}/practical?mode=practice${q}`} className={`chip ${on ? "!bg-accent !text-white" : ""}`}>{label}</Link>);
      body = (
        <>
          <div className="flex flex-wrap gap-1.5">
            {chip(type ? `&type=${type}` : "", "כל הניסויים", !exp)}
            {bank.experiments.map((e) => chip(`&exp=${e.n}${type ? `&type=${type}` : ""}`, `ניסוי ${e.n}`, exp === e.n))}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {chip(exp ? `&exp=${exp}` : "", "כל הסוגים", !type)}
            {(["graph", "theory", "build"] as const).map((t) => chip(`${exp ? `&exp=${exp}` : ""}&type=${t}`, TYPE[t], type === t))}
          </div>
          {list.length ? list.map((q) => <Question key={q.id} q={q} />) : <p className="card text-muted">אין שאלות כאלה עדיין.</p>}
        </>
      );
    } else {
      const pool = bank.questions.filter((q) => mode === "final" || q.experiment <= MIDTERM_LAST);
      const exam = (["graph", "theory", "build"] as const).map((t, k) => pick(pool.filter((q) => q.type === t), seed * 7 + k)).filter(Boolean) as Q[];
      body = (
        <>
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted">{mode === "midterm" ? `מבחן אמצע: ניסויים 1-${MIDTERM_LAST}` : "מבחן סוף: כל הניסויים"} · 3 שאלות כמו במבחן</p>
            <Link href={`/courses/${id}/practical?mode=${mode}&seed=${seed + 1}`} className="btn-ghost text-sm">🎲 מבחן אחר</Link>
          </div>
          {exam.map((q, i) => <Question key={q.id} q={q} n={i + 1} />)}
        </>
      );
    }
  }

  return (
    <div className="space-y-4">
      <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course.name}</Link>
      <h1 className="text-2xl font-bold">🧪 מבחן מעשי</h1>
      <div className="flex gap-2 flex-wrap">{tab("practice", "תרגול")}{tab("midterm", "מבחן אמצע (1-5)")}{tab("final", "מבחן סוף")}</div>
      {!!bank?.hints.length && (
        <details className="card">
          <summary className="cursor-pointer font-semibold">⭐ מה המרצה אמרה על המבחן ({bank.hints.length})</summary>
          <ul className="list-disc ps-5 mt-2 space-y-1 text-sm">{bank.hints.map((h, i) => <li key={i}>{h}</li>)}</ul>
        </details>
      )}
      {body}
      <RebuildPractical courseId={id} />
    </div>
  );
}
