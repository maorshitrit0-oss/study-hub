import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import Words from "@/components/Words";
import BuildGlossary from "@/components/BuildGlossary";
import type { Term } from "@/lib/glossary";

/** English words from the course material: a word list and a quiz on them. */
export default async function WordsPage({ searchParams }: PageProps<"/words">) {
  const courseId = (await searchParams).course as string | undefined;
  const { sb } = await requireUser();
  let q = sb.from("glossary").select("id, course_id, lesson_id, en, he, explanation").order("created_at");
  if (courseId) q = q.eq("course_id", courseId);
  const [{ data: terms, error }, { data: courses }, { data: lessons }] = await Promise.all([
    q,
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
    courseId
      ? sb.from("lessons").select("id").eq("course_id", courseId).eq("status", "ready")
      : Promise.resolve({ data: [] as { id: string }[] }),
  ]);
  const course = courses?.find((c) => c.id === courseId);
  const list = (terms ?? []) as Term[];
  const covered = new Set(list.map((t) => t.lesson_id));
  const missing = (lessons ?? []).filter((l) => !covered.has(l.id)).length;

  return (
    <div className="space-y-4">
      {course && <Link href={`/courses/${course.id}`} className="text-sm text-accent">→ {course.name}</Link>}
      <h1 className="text-2xl font-bold">מילים באנגלית{course ? ` · ${course.name}` : ""}</h1>
      <p className="text-sm text-muted">המונחים באנגלית מהחומר של הקורסים, עם התרגום וההסבר בעברית. כל פרק חדש מוסיף את המילים שלו.</p>

      <div className="flex flex-wrap gap-2">
        <Link href="/words" className={`chip ${!courseId ? "border-accent text-accent" : ""}`}>כל הקורסים</Link>
        {(courses ?? []).map((c) => (
          <Link key={c.id} href={`/words?course=${c.id}`} className={`chip ${c.id === courseId ? "border-accent text-accent" : ""}`}>{c.name}</Link>
        ))}
      </div>

      {error && <p className="card text-sm text-warn">צריך להריץ את קוד ה-SQL של המילים ב-Supabase (glossary.sql).</p>}
      {courseId && missing > 0 && !error && (
        <div className="card space-y-2">
          <p className="text-sm">ל-{missing} פרקים בקורס עוד אין רשימת מילים (נכתבו לפני שהתכונה נוספה).</p>
          <BuildGlossary courseId={courseId} />
        </div>
      )}
      <Words terms={list} courseNames={Object.fromEntries((courses ?? []).map((c) => [c.id, c.name]))} showCourse={!courseId} />
    </div>
  );
}
