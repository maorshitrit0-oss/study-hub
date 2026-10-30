import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import AutoRefresh from "@/components/AutoRefresh";
import Chapter from "@/components/Chapter";
import Quiz from "@/components/Quiz";
import Studio from "@/components/Studio";
import { loadMedia } from "@/lib/studio";
import { deleteLesson, markRead, requestFullChapter, retryLesson, updateLesson } from "../../actions";
import Exercises, { type Exercise } from "@/components/Exercises";
import Fold from "@/components/Fold";
import { LESSON_LABEL, lessonName, type Lesson } from "@/lib/types";

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
  // Studio items; chapters without everyday examples get them automatically (once).
  // Everyday examples now live inside the chapter (enrich.py / new chapters); the old separate card shows only
  // for a chapter not restructured yet.
  const media = lesson.status === "ready" ? await loadMedia(sb, { lessonId: id }) : null;
  const examples = lesson.chapter_md?.includes("🏠") ? undefined : media?.find((m) => m.kind === "examples");
  // "*" also brings `source` where it exists: lab entry-quiz questions live on their own page, not in the chapter quiz.
  const { data: all } = await sb.from("questions").select("*").eq("lesson_id", id).order("created_at");
  const questions = (all ?? []).filter((q) => !q.source);
  // Lectures and practices: a short summary + the exercises (supabase/exercises.sql); the full chapter on request.
  const { data: exercises } = await sb.from("exercises").select("*").eq("lesson_id", id).order("ord");
  const summary = (lesson as Lesson & { summary_md?: string | null }).summary_md ?? null;
  const fullChapter = lesson.chapter_md && lesson.chapter_md !== summary ? lesson.chapter_md : null;

  return (
    <article className="space-y-5">
      <header>
        <Link href={`/courses/${lesson.course_id}`} className="text-sm text-accent">→ {lesson.courses.name}</Link>
        <h1 className="text-2xl font-bold mt-1">{lessonName(lesson)}{lesson.title && lesson.kind !== "web" ? ` · ${lesson.title}` : ""}</h1>
        {lesson.topics?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">{lesson.topics.map((t) => <span key={t} className="chip">{t}</span>)}</div>
        )}
        <details className="mt-2">
          <summary className="cursor-pointer text-sm text-accent">✏️ עריכה (כותרת, מספר, סוג) - למשל חלק 1 / חלק 2</summary>
          <form action={updateLesson.bind(null, id)} className="space-y-3 mt-3">
            <div className="grid grid-cols-2 gap-3">
              <select className="input" name="kind" defaultValue={lesson.kind}>
                {Object.entries(LESSON_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
              <input className="input" name="number" type="number" min={0} defaultValue={lesson.number ?? ""} placeholder="מספר" />
            </div>
            <input className="input" name="title" defaultValue={lesson.title ?? ""} placeholder="כותרת, למשל: חלק 1 - מבוא ל-GPIO" />
            {lesson.kind !== "web" && (
              <input className="input" name="url" dir="ltr" inputMode="url" defaultValue={lesson.source_url ?? ""}
                placeholder="קישור (זום / יוטיוב / דרייב) - קישור חדש מעבד את ההקלטה מחדש" aria-label="קישור" />
            )}
            <button className="btn w-full">שמירה</button>
          </form>
        </details>
      </header>

      {lesson.status !== "ready" && (
        <section className="card space-y-3">
          {lesson.status === "error" ? (
            <>
              <p className="text-bad font-medium">העיבוד נכשל</p>
              <p className="text-sm text-muted whitespace-pre-line break-words" dir="auto">{lesson.error}</p>
              <form action={retryLesson.bind(null, id)}><button className="btn">לנסות שוב</button></form>
            </>
          ) : lesson.status === "transcribed" && lesson.title?.includes("(להשוואה)") ? (
            <p>זה התמלול של ההרצאה משנה שעברה. הוא נכנס כהשוואה לפרק של ההרצאה עם אותו מספר מהשנה.</p>
          ) : lesson.status === "transcribed" ? (
            <p>התמלול מוכן ומחכה לכתיבת הפרק. ב-Claude Code כתוב: <b dir="ltr">כתוב את הפרק של {id}</b></p>
          ) : (
            <>
              <AutoRefresh />
              <p className="font-medium">{lesson.status === "queued" ? "בתור לעיבוד..." : "מעבד..."}</p>
              <p className="text-sm text-muted">{lesson.progress ?? "מתחיל בקרוב"}</p>
              <p className="text-xs text-muted">אפשר לסגור את הדף - העיבוד רץ בשרת ותקבל התראה כשהוא מוכן. זמן העיבוד בערך 40% מאורך ההקלטה.</p>
            </>
          )}
        </section>
      )}

      {summary && (
        <section className="card">
          <Chapter md={summary} slideUrls={slideUrls} />
        </section>
      )}

      {(exercises ?? []).length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-1">✍️ תרגילים מהשיעור ({exercises!.length})</h2>
          <p className="text-xs text-muted mb-3">לפתור על דף, ורק אחר כך לפתוח את הפתרון.</p>
          <Exercises items={(exercises ?? []) as Exercise[]} slideUrls={slideUrls} />
        </section>
      )}

      {summary && !fullChapter && lesson.status === "ready" && (
        <form action={requestFullChapter.bind(null, id)}>
          <button className="btn-ghost w-full">📖 לכתוב גם פרק מלא לשיעור הזה</button>
        </form>
      )}

      {fullChapter && summary && (
        <Fold id="full-chapter" title="📖 פרק מלא">
          <Chapter md={fullChapter} slideUrls={slideUrls} />
        </Fold>
      )}

      {lesson.chapter_md && !summary && (
        <section className="card">
          {examples && (
            <details open className="rounded-xl bg-accent-soft p-3 mb-4">
              <summary className="cursor-pointer font-semibold">🏠 רקע ודוגמאות מחיי היום-יום לשיעור הזה</summary>
              {examples.status === "ready" && examples.script ? <Chapter md={examples.script} slideUrls={{}} />
                : examples.status === "error" ? <p className="text-sm text-bad mt-2">⚠️ {examples.error}</p>
                : <p className="text-sm text-muted mt-2 animate-pulse">מכין רקע ודוגמה מהחיים לכל נושא... (כמה דקות)</p>}
              {(examples.status === "queued" || examples.status === "processing") && <AutoRefresh seconds={20} />}
            </details>
          )}
          <Chapter md={lesson.chapter_md} slideUrls={slideUrls} />
        </section>
      )}

      {lesson.status === "ready" && (
        <section className="card" id="quiz">
          <form action={markRead.bind(null, id, !lesson.read_at)} className="mb-4">
            {lesson.read_at ? (
              <button className="w-full text-sm text-muted py-2">✓ סומן כנקרא · לחץ לביטול הסימון</button>
            ) : (
              <button className="btn-ghost w-full">✓ סיימתי עם השיעור הזה</button>
            )}
          </form>
          {questions.length > 0 && <Quiz questions={questions} title="שאלון סיכום" />}
          {lesson.kind === "lab" && lesson.number && (
            <Link href={`/courses/${lesson.course_id}/entry?n=${lesson.number}`} className="btn-ghost w-full mt-3">🎯 תרגול לבוחן הכניסה של ניסוי {lesson.number}</Link>
          )}
        </section>
      )}

      {Object.keys(slideUrls).length > 0 && (
        <details className="card">
          <summary className="cursor-pointer font-medium">כל צילומי הלוח ({Object.keys(slideUrls).length})</summary>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3">
            {Object.entries(slideUrls).map(([n, url]) => (
              <a key={n} href={url} target="_blank" rel="noreferrer" className="block">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={url} alt={`צילום ${n}`} loading="lazy" className="rounded-lg border border-line w-full" />
                <span className="text-xs text-muted">צילום {n}</span>
              </a>
            ))}
          </div>
        </details>
      )}

      {lesson.transcript && (
        <details className="card">
          <summary className="cursor-pointer font-medium">התמלול המלא</summary>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed mt-3 font-sans">{lesson.transcript}</pre>
        </details>
      )}

      {lesson.status === "ready" && lesson.chapter_md && (
        <Studio courseId={lesson.course_id} lessons={[{ id, label: lessonName(lesson) }]} items={media === null ? null : media.filter((m) => m.kind !== "examples")}
          canVideo={/!\[[^\]]*\]\(slide:\d+\)/.test(lesson.chapter_md)} />
      )}


      <div className="flex justify-between text-sm">
        {lesson.source_url && <a href={lesson.source_url} target="_blank" rel="noreferrer" className="text-accent">המקור</a>}
        <form action={deleteLesson.bind(null, id, lesson.course_id)}><button className="text-bad">מחיקה</button></form>
      </div>
    </article>
  );
}
