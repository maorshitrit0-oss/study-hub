import BackLink from "@/components/BackLink";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { fetchAll } from "@/lib/fetchAll";
import Warmup, { type WarmLesson } from "@/components/Warmup";
import { isSiteLesson } from "@/lib/week";
import { lessonName, isSession, type Lesson, type Question } from "@/lib/types";

const LESSONS = 3; // the last lessons it covers
const PER_LESSON = 3;

/** In the order taught: lecture N, practice N, lecture N+1... (by number, lecture before practice, then upload time). */
const byMeeting = (a: Lesson, b: Lesson) => (a.number ?? 999) - (b.number ?? 999)
  || (a.kind === b.kind ? 0 : a.kind === "lecture" ? -1 : 1) || a.created_at.localeCompare(b.created_at);

/** Per lesson: wrong last time first, then never answered, then the rest (a little shuffle inside each group). */
function pick(last: Lesson[], questions: (Question & { source?: string | null })[], attempts: { question_id: string; is_correct: boolean }[]) {
  const lastAnswer = new Map<string, boolean>();
  for (const a of attempts) lastAnswer.set(a.question_id, a.is_correct);
  const rank = (q: Question) => (lastAnswer.get(q.id) === false ? 0 : !lastAnswer.has(q.id) ? 1 : 2) + Math.random() * 0.9;
  return last.flatMap((l) => questions.filter((q) => q.lesson_id === l.id && !q.source)
    .map((q) => ({ q, r: rank(q) })).sort((a, b) => a.r - b.r).slice(0, PER_LESSON).map((x) => x.q));
}

/**
 * 🔥 Warm-up before the next class (09/11/2026): short questions on the last lessons of the course (wrong last time
 * first, then never answered), and at the end what to read before the class, per lesson.
 */
export default async function WarmupPage({ params }: PageProps<"/courses/[id]/warmup">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const [{ data: course }, { data: lessons }, questions, attempts] = await Promise.all([
    sb.from("courses").select("id, name").eq("id", id).maybeSingle(),
    sb.from("lessons").select("id, kind, number, title, status, created_at, source_url, transcript, chapter_md, summary_md").eq("course_id", id).eq("status", "ready"),
    fetchAll<Question & { source?: string | null }>(() => sb.from("questions").select("*").eq("course_id", id).order("id")),
    fetchAll<{ question_id: string; is_correct: boolean }>(() => sb.from("attempts").select("question_id, is_correct").eq("course_id", id).order("created_at").order("id")),
  ]);
  if (!course) notFound();
  const withQ = new Set(questions.filter((q) => !q.source).map((q) => q.lesson_id));
  // Lessons taught in class (and self-study sessions), not last year's site material.
  const ls = ((lessons ?? []) as unknown as (Lesson & { summary_md?: string | null })[])
    .filter((l) => withQ.has(l.id) && !isSiteLesson(l) && ["lecture", "practice", "web", "other"].includes(l.kind))
    .sort((a, b) => Number(isSession(a)) - Number(isSession(b)) || byMeeting(a, b));
  const lectures = ls.filter((l) => !isSession(l));
  const last = (lectures.length ? lectures : ls).slice(-LESSONS);
  const set = pick(last, questions, attempts);
  const info: WarmLesson[] = last.map((l) => ({
    id: l.id,
    label: `${lessonName(l)}${l.title && l.kind !== "web" && !isSession(l) ? ` · ${l.title}` : ""}`,
    hasSummary: !!l.summary_md && l.summary_md !== l.chapter_md,
  }));

  return (
    <div className="space-y-4">
      <BackLink href={`/courses/${id}`}>→ {course.name}</BackLink>
      <h1 className="text-2xl font-bold">🔥 חימום לפני השיעור הבא</h1>
      <p className="text-sm text-muted">
        {set.length} שאלות קצרות על {info.map((l) => l.label).join(", ")} – כדי לראות שאתה על החומר. בסוף: מה לקרוא לפי התוצאות.
      </p>
      <div className="card">
        {set.length ? <Warmup key={set.map((x) => x.id).join()} questions={set} lessons={info} courseId={id} />
          : <p className="text-muted">עוד אין שיעורים מוכנים עם שאלות בקורס הזה.</p>}
      </div>
    </div>
  );
}
