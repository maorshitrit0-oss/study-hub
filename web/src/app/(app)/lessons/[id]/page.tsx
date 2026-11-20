import Link from "next/link";
import { understandingOnly } from "@/lib/review";
import BackLink from "@/components/BackLink";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import AutoRefresh from "@/components/AutoRefresh";
import Chapter from "@/components/Chapter";
import Quiz from "@/components/Quiz";
import Studio from "@/components/Studio";
import { loadMedia } from "@/lib/studio";
import { deleteLesson, markRead, markReadAndGo, pasteTranscript, retryLesson, updateLesson } from "../../actions";
import Exercises, { type Exercise } from "@/components/Exercises";
import Fold from "@/components/Fold";
import { LESSON_LABEL, lessonName, isSession, type Lesson } from "@/lib/types";
import { warmupFor } from "@/lib/warmup";
import Warmup from "@/components/Warmup";
import { PROJECT, VLSI_PROGRAM } from "@/lib/vlsiProgram";

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
  const warm = lesson.status === "ready" ? await warmupFor(sb, lesson.course_id, id) : { questions: [], lessons: [] };
  const questions = (all ?? []).filter((q) => !q.source);
  // Lectures and practices: a short summary + the exercises (supabase/exercises.sql); the full chapter on request.
  const { data: exRows } = await sb.from("exercises").select("*").eq("lesson_id", id).order("ord");
  const where: Record<string, string> = await sb.storage.from("study").download(`${userId}/materials/${lesson.course_id}/exercise_where.json`)
    .then(async ({ data }) => (data ? JSON.parse(await data.text()) : {})).catch(() => ({}));
  const exercises = (exRows ?? []).map((x) => ({ ...x, where: where[x.id] || undefined }));
  const summary = (lesson as Lesson & { summary_md?: string | null }).summary_md ?? null;
  // A self-study session is written as one full chapter (with the project task among its exercises).
  const self = (lesson.transcript ?? "").startsWith("<!-- vlsi-session -->");
  const summaryText = self ? null : summary;
  const full = self ? lesson.chapter_md : lesson.chapter_md && lesson.chapter_md !== summary ? lesson.chapter_md : null;
  // Self-study: the session's job-interview questions also close the quiz (his request, 06/11/2026), each with its source.
  const interview = self && lesson.number ? VLSI_PROGRAM[lesson.number - 1]?.interview ?? [] : [];
  const project = (exercises ?? []).filter((x) => (x.title ?? "").startsWith("🔧"));
  const exerciseFold = (exercises ?? []).length > 0 && (
    <Fold id={`exercises-${id}`} title={self && project.length ? (project.some((x) => (x.title ?? "").startsWith("🔧 תרגול")) ? "✍️ תרגילים ותרגול על הלוח" : "🔧 משימת הפרויקט ותרגילים") : "✍️ תרגילים מהשיעור"} hint={`${exercises!.length}`}>
      <p className="text-xs text-muted mb-3">{self && project.length ? "המשימה של היום בפרויקט - כמו תרגיל בית: לנסות לבד, ורק אחר כך לפתוח את הפתרון." : "לפתור על דף, ורק אחר כך לפתוח את הפתרון."}</p>
      <Exercises items={(exercises ?? []) as Exercise[]} slideUrls={slideUrls} />
    </Fold>
  );
  // Self-study flow (his request 20/11/2026): video -> chapter -> quiz -> "what does this code do" multiple choice ->
  // what to know before the hands-on part -> the practical work = today's part of the CV project.
  const sess = self && lesson.number ? VLSI_PROGRAM[lesson.number - 1] : undefined;
  const codeEx = (exercises ?? []).filter((x) => !(x.title ?? "").startsWith("🔧"));
  const selfFlow = self && (
    <>
      {codeEx.length > 0 && (
        <>
          <a href="#self-ex" className="btn w-full text-center">⬅️ סיימתי את השאלון – לתרגילים: מה הקוד עושה</a>
          <div id="self-ex">
            <Fold id={`self-ex-${id}`} title="✍️ תרגילים: מה הקוד עושה (אמריקאי)" hint={`${codeEx.length}`}>
              <p className="text-xs text-muted mb-3">כמו בשאלת קוד בראיון: לקרוא את הקוד, לבחור תשובה – ואז לראות את ההסבר המלא.</p>
              <Exercises items={codeEx as Exercise[]} slideUrls={slideUrls} />
            </Fold>
          </div>
        </>
      )}
      {(project.length > 0 || sess) && (
        <>
          <a href="#self-practical" className="btn w-full text-center">⬅️ עכשיו תרגול מעשי – החלק של היום בפרויקט</a>
          <div id="self-practical">
            <Fold id={`self-practical-${id}`} title="🛠️ תרגול מעשי + החלק של היום בפרויקט">
              {sess?.setup && sess.setup.length > 0 && (
                <div className="mb-4">
                  <p className="font-semibold">🧰 מה צריך לדעת ולפתוח לפני שמתחילים</p>
                  <ol className="list-decimal ps-5 text-sm space-y-1 mt-1">{sess.setup.map((x) => <li key={x}>{x}</li>)}</ol>
                </div>
              )}
              {sess?.task && <p className="text-sm mb-3">🎯 <b>המשימה המעשית:</b> {sess.task}</p>}
              {sess?.board && (
                <div className="rounded-xl bg-accent-soft p-3 mb-4 text-sm">
                  <p className="font-semibold">🔧 הפרויקט: חלק {lesson.number} מתוך {VLSI_PROGRAM.length}</p>
                  <p className="text-xs text-muted">{PROJECT}</p>
                  <p className="mt-1">היום בונים: {sess.board}</p>
                </div>
              )}
              {project.length > 0 && <Exercises items={project as Exercise[]} slideUrls={slideUrls} />}
            </Fold>
          </div>
        </>
      )}
    </>
  );
  const studioFold = lesson.status === "ready" && lesson.chapter_md && (
    <Studio courseId={lesson.course_id} lessons={[{ id, label: lessonName(lesson) }]} items={media === null ? null : media.filter((m) => m.kind !== "examples")}
      canVideo={/!\[[^\]]*\]\(slide:\d+\)/.test(lesson.chapter_md)} title={self ? "🎬 סרטון המפגש" : undefined} />
  );
  // The next lesson of the course (his request 16/11/2026): part A -> part B of the same lecture, lecture N -> practice N,
  // practice N -> lecture N+1 (lab N -> lab N+1, session N -> session N+1). "📦" notebooks and unnumbered lessons are skipped.
  const { data: sibs } = await sb.from("lessons").select("id, kind, number, title, status, created_at").eq("course_id", lesson.course_id);
  const RANK: Record<string, number> = { lecture: 0, practice: 1, lab: 2, other: 3 };
  const seq = (sibs ?? []).filter((l) => l.number && l.status === "ready" && !(l.title ?? "").startsWith("📦")
      && (lesson.kind === "other") === (l.kind === "other"))
    .sort((a, b) => a.number - b.number || (RANK[a.kind] ?? 9) - (RANK[b.kind] ?? 9)
      || (a.title ?? "").localeCompare(b.title ?? "", "he") || a.created_at.localeCompare(b.created_at));
  const at = seq.findIndex((l) => l.id === id);
  const next = at >= 0 ? seq[at + 1] : undefined;
  const nextName = next ? `${lessonName(next as Lesson)}${/חלק/.test(next.title ?? "") ? ` – ${(next.title ?? "").match(/חלק\s*\S+/)?.[0]}` : ""}` : "";
  // His flow (16/11/2026): lecture (parts) -> practice N -> the exercises of week N -> lecture N+1. So the last lesson of
  // week N (the practice, or the lecture when there is no practice) leads to the week's exercises, not to lecture N+1.
  const weekDone = (lesson.kind === "lecture" || lesson.kind === "practice") && !!lesson.number && !self
    && (!next || (next.number ?? 0) > lesson.number);
  const nextHref = weekDone ? `/courses/${lesson.course_id}/exercises?w=${lesson.number}` : next ? `/lessons/${next.id}` : "";
  const nextLabel = weekDone ? `לתרגילים של שבוע ${lesson.number}` : `לשיעור הבא: ${nextName}`;
  const quizFold = lesson.status === "ready" && (
    <section className="space-y-3" id="quiz">
      {questions.length > 0 && (
        <Fold id={`quiz-${id}`} title="✅ שאלון אמריקאי" hint={`${understandingOnly(questions).length}`}>
          <Quiz questions={understandingOnly(questions)} title="שאלון סיכום" />
          {interview.length > 0 && (
            <div className="mt-5 border-t border-line pt-3 text-sm">
              <p className="font-semibold">🎤 לסיום: שאלות מראיונות עבודה</p>
              <p className="text-xs text-muted mb-2">שאלות פתוחות. לענות בקול או על דף כאילו אתה בראיון, ורק אחר כך לפתוח את המקור ולבדוק.</p>
              <ol className="list-decimal ps-5 space-y-1">
                {interview.map((x) => (
                  <li key={x.q}>
                    {x.q}{" "}
                    <a href={x.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent underline">🔗 {x.src}</a>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </Fold>
      )}
      <form action={markRead.bind(null, id, !lesson.read_at)}>
        {lesson.read_at ? (
          <button className="w-full text-sm text-muted py-2">✓ סומן כנקרא · לחץ לביטול הסימון</button>
        ) : (
          <button className="btn-ghost w-full">✓ סיימתי עם השיעור הזה</button>
        )}
      </form>
      {nextHref && (lesson.read_at ? (
        <Link href={nextHref} className="btn w-full text-center">⬅️ {nextLabel}</Link>
      ) : (
        <form action={markReadAndGo.bind(null, id, nextHref)}>
          <button className="btn w-full">✓ סיימתי ⬅️ {nextLabel}</button>
        </form>
      ))}
      {lesson.kind === "lab" && lesson.number && (
        <Link href={`/courses/${lesson.course_id}/entry?n=${lesson.number}`} className="btn-ghost w-full">🎯 תרגול לבוחן הכניסה של ניסוי {lesson.number}</Link>
      )}
    </section>
  );

  return (
    <article className="space-y-5">
      <BackLink href={`/courses/${lesson.course_id}`}>→ {lesson.courses.name}</BackLink>
      <header>
        <h1 className="text-2xl font-bold mt-1">{lessonName(lesson)}{lesson.title && lesson.kind !== "web" && !isSession(lesson) ? ` · ${lesson.title}` : ""}</h1>
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
              {((lesson.error ?? "").includes("זום") || (lesson.source_url ?? "").includes("zoom.us")) && (
                <form action={pasteTranscript.bind(null, id)} className="space-y-2 pt-3 border-t border-line">
                  <p className="text-sm font-medium">או: התמלול של זום – <Link href="/zoom" className="text-accent underline">בלחיצה אחת עם הסימנייה</Link>, או להדביק כאן</p>
                  <p className="text-xs text-muted">בדף ההקלטה בזום, בחלונית Transcript מימין: לגלול עד הסוף, לסמן הכל, להעתיק ולהדביק כאן. הפרק ייכתב מהתמלול (בלי צילומי השקפים).</p>
                  <textarea name="transcript" rows={5} className="input w-full" dir="auto" placeholder="התמלול מזום..." />
                  <button className="btn">לכתוב את הפרק מהתמלול</button>
                </form>
              )}
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

      {/* Everything folded by default (05/11/2026) - he opens what he wants: the condensed summary, the full chapter,
          the exercises, the quiz. Every lesson: warm-up -> video -> chapter -> condensed -> quiz -> exercises (14/11/2026). */}
      {/* 🔥 First thing in the lesson (09/11/2026): a warm-up on every lesson before this one, then what to re-read. */}
      {lesson.status === "ready" && warm.questions.length > 0 && (
        <Fold id={`warmup-${id}`} title="🔥 חימום לפני השיעור" defaultOpen={!lesson.read_at}
          hint={`${warm.questions.length} שאלות · ${warm.lessons.length} שיעורים קודמים`}>
          <p className="text-sm text-muted mb-3">על כל מה שלפני השיעור הזה: {warm.lessons.map((l) => l.label).join(" · ")}</p>
          <Warmup key={warm.questions.map((q) => q.id).join()} questions={warm.questions} lessons={warm.lessons} courseId={lesson.course_id} />
        </Fold>
      )}

      {/* Every lesson (14/11/2026): warm-up -> video -> full chapter -> (condensed) -> quiz -> exercises. */}
      {studioFold}


      {full && (
        <Fold id={`chapter-${id}`} title="📖 פרק מלא">
          {examples && (
            <details className="rounded-xl bg-accent-soft p-3 mb-4">
              <summary className="cursor-pointer font-semibold">🏠 רקע ודוגמאות מחיי היום-יום לשיעור הזה</summary>
              {examples.status === "ready" && examples.script ? <Chapter md={examples.script} slideUrls={{}} />
                : examples.status === "error" ? <p className="text-sm text-bad mt-2">⚠️ {examples.error}</p>
                : <p className="text-sm text-muted mt-2 animate-pulse">מכין רקע ודוגמה מהחיים לכל נושא... (כמה דקות)</p>}
              {(examples.status === "queued" || examples.status === "processing") && <AutoRefresh seconds={20} />}
            </details>
          )}
          <Chapter md={full} slideUrls={slideUrls} />
        </Fold>
      )}

      {lesson.status === "ready" && !self && summaryText && (
        <Fold id={`summary-${id}`} title="📝 סיכום מתומצת - מסקנות השיעור">
          <Chapter md={summaryText} slideUrls={slideUrls} />
        </Fold>
      )}
      {/* Always both (his wish 11/11/2026): no button - the queue writes the missing full chapter by itself. */}
      {!full && summaryText && lesson.status === "ready" && (
        <p className="text-sm text-muted text-center">📖 הפרק המלא נכתב אוטומטית ויופיע כאן (בתור, לפי המכסה של Gemini)</p>
      )}

      {/* Lectures and practices: the exercises are solved only in the course's exercises tab, week N = lecture N
          (his way, 11/11/2026) - here only a link to that week. */}
      {quizFold}
      {!self && (exercises ?? []).length > 0 && (lesson.kind === "lecture" || lesson.kind === "practice") && lesson.number ? (
        <Link href={`/courses/${lesson.course_id}/exercises?w=${lesson.number}`} className="card block text-center text-sm font-medium">
          ✍️ התרגילים של השיעור הזה – בעמודת התרגילים, שבוע {lesson.number}
        </Link>
      ) : !self && exerciseFold}
      {selfFlow}

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




      <div className="flex justify-between text-sm">
        {lesson.source_url && <a href={lesson.source_url} target="_blank" rel="noreferrer" className="text-accent">המקור</a>}
        <form action={deleteLesson.bind(null, id, lesson.course_id)}><button className="text-bad">מחיקה</button></form>
      </div>
    </article>
  );
}
