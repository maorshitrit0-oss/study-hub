import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import Quiz from "@/components/Quiz";
import type { Question } from "@/lib/types";

const SIZE = 10;

function pickPractice(questions: Question[], last: Map<string, boolean>, size: number) {
  const rank = (x: Question) => (last.get(x.id) === false ? 0 : !last.has(x.id) ? 1 : 2) + Math.random() * 0.9;
  return questions.map((q) => ({ q, r: rank(q) })).sort((a, b) => a.r - b.r).slice(0, size).map((x) => x.q);
}

/** Practice set: weakest material first - wrong last time, then never answered, then the rest. */
export default async function Practice({ params, searchParams }: PageProps<"/courses/[id]/practice">) {
  const { id } = await params;
  const topic = (await searchParams).topic as string | undefined;
  const { sb } = await requireUser();
  let q = sb.from("questions").select("id, lesson_id, topic, question, options, explanation, difficulty").eq("course_id", id);
  if (topic) q = q.eq("topic", topic);
  const [{ data: course }, { data: questions }, { data: attempts }] = await Promise.all([
    sb.from("courses").select("name").eq("id", id).single(),
    q,
    sb.from("attempts").select("question_id, is_correct").eq("course_id", id).order("created_at"),
  ]);
  const last = new Map<string, boolean>();
  for (const a of attempts ?? []) last.set(a.question_id, a.is_correct);
  const set = pickPractice((questions ?? []) as Question[], last, SIZE);

  return (
    <div className="space-y-4">
      <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course?.name}</Link>
      <h1 className="text-2xl font-bold">תרגול{topic ? `: ${topic}` : ""}</h1>
      <p className="text-sm text-muted">קודם שאלות שטעית בהן, אחר כך שאלות חדשות.</p>
      <div className="card">
        {set.length ? <Quiz key={set.map((x) => x.id).join()} questions={set} title="תרגול" /> : <p className="text-muted">אין עדיין שאלות בקורס הזה.</p>}
      </div>
    </div>
  );
}
