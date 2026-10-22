import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import AutoRefresh from "@/components/AutoRefresh";
import Chapter from "@/components/Chapter";
import Quiz from "@/components/Quiz";
import { deleteLesson, markRead, retryLesson } from "../../actions";
import { lessonName, type Lesson } from "@/lib/types";

export default async function LessonPage({ params }: PageProps<"/lessons/[id]">) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const { data } = await sb.from("lessons").select("*, courses(name)").eq("id", id).maybeSingle();
  if (!data) notFound();
  const lesson = data as Lesson & { transcript: string | null; courses: { name: string } };

  const slideUrls: Record<number, string> = {};
  if (lesson.status === "ready" && lesson.slide_count) {
    const paths = Array.from({ length: lesson.slide_count }, (_, k) => `${userId}/lessons/${id}/slide_${String(k + 1).padStart(3, "0")}.webp`);
    const { data: signed } = await sb.storage.from("study").createSignedUrls(paths, 6 * 3600);
    signed?.forEach((s, k) => { if (s.signedUrl) slideUrls[k + 1] = s.signedUrl; });
  }
  const { data: questions } = await sb.from("questions")
    .select("id, lesson_id, topic, question, options, explanation, difficulty").eq("lesson_id", id).order("created_at");

  return (
    <article className="space-y-5">
      <header>
        <Link href={`/courses/${lesson.course_id}`} className="text-sm text-accent">→ {lesson.courses.name}</Link>
        <h1 className="text-2xl font-bold mt-1">{lessonName(lesson)}{lesson.title && lesson.kind !== "web" ? ` · ${lesson.title}` : ""}</h1>
        {lesson.topics?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">{lesson.topics.map((t) => <span key={t} className="chip">{t}</span>)}</div>
        )}
      </header>

      {lesson.status !== "ready" && (
        <section className="card space-y-3">
          {lesson.status === "error" ? (
            <>
              <p className="text-bad font-medium">העיבוד נכשל</p>
              <p className="text-sm text-muted whitespace-pre-line break-words" dir="auto">{lesson.error}</p>
              <form action={retryLesson.bind(null, id)}><button className="btn">לנסות שוב</button></form>
            </>
          ) : lesson.status === "transcribed" ? (
            <p>התמלול מוכן ומחכה לכתיבת הפרק. ב-Claude Code כתוב: <b dir="ltr">כתוב את הפרק של {id}</b></p>
          ) : (
            <>
              <AutoRefresh />
              <p className="font-medium">{lesson.status === "queued" ? "בתור לעיבוד..." : "מעבד..."}</p>
              <p className="text-sm text-muted">{lesson.progress ?? "מתחיל בקרוב"}</p>
              <p className="text-xs text-muted">אפשר לסגור את הדף - העיבוד רץ בשרת. הרצאה של שעה וחצי לוקחת בערך 40 דקות.</p>
            </>
          )}
        </section>
      )}

      {lesson.chapter_md && (
        <section className="card">
          <Chapter md={lesson.chapter_md} slideUrls={slideUrls} />
        </section>
      )}

      {lesson.status === "ready" && (
        <section className="card" id="quiz">
          {!lesson.read_at && (
            <form action={markRead.bind(null, id)} className="mb-4">
              <button className="btn-ghost w-full">✓ סיימתי לקרוא</button>
            </form>
          )}
          <Quiz questions={questions ?? []} title="שאלון סיכום" />
        </section>
      )}

      {lesson.transcript && (
        <details className="card">
          <summary className="cursor-pointer font-medium">התמלול המלא</summary>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed mt-3 font-sans">{lesson.transcript}</pre>
        </details>
      )}

      <div className="flex justify-between text-sm">
        {lesson.source_url && <a href={lesson.source_url} target="_blank" rel="noreferrer" className="text-accent">המקור</a>}
        <form action={deleteLesson.bind(null, id, lesson.course_id)}><button className="text-bad">מחיקה</button></form>
      </div>
    </article>
  );
}
