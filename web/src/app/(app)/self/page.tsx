import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { FREEZES, weekDates } from "@/lib/skills";
import { ensureCadenceTracks } from "@/lib/cadenceTracks";
import { catchUps, ensureSelfSlots, ensureSessionLesson, mainTrack, syncVlsiTasks } from "@/lib/selfPlan";
import { VLSI_PROGRAM, sessionDates, sessionKey, type Session } from "@/lib/vlsiProgram";
import { openSessionLesson, setSessionDone, startSession } from "../actions";
import Fold from "@/components/Fold";

const ddmm = (d: string) => `${d.slice(8, 10)}/${d.slice(5, 7)}`;

type LessonRef = { id: string; status: string } | null | undefined;

function SessionCard({ s, date, done, courseId, current, lesson }: {
  s: Session; date: string; done: boolean; courseId: string; current: boolean; lesson: LessonRef;
}) {
  const key = sessionKey(s);
  return (
    <article className={`rounded-xl border p-3 space-y-2 ${current ? "border-accent bg-accent-soft" : "border-line"} ${done ? "opacity-60" : ""}`}>
      <div className="flex justify-between items-start gap-2">
        <h3 className="font-semibold">{done ? "✅ " : current ? "▶️ " : ""}מפגש {s.n}: {s.title}</h3>
        <span className="text-xs text-muted shrink-0">{s.n === 1 ? "שישי" : "מוצ״ש"} {ddmm(date)}</span>
      </div>
      <p className="text-sm">🎯 {s.goal}</p>
      {s.setup && (
        <details className="text-sm">
          <summary className="cursor-pointer text-accent">🛠️ הכנה: מה לפתוח ואיך</summary>
          <ol className="list-decimal ps-5 mt-1 space-y-1">{s.setup.map((x) => <li key={x}>{x}</li>)}</ol>
        </details>
      )}
      <p className="text-sm">🔧 <b>משימה:</b> {s.task}</p>
      <details className="text-sm">
        <summary className="cursor-pointer text-accent">🎤 שאלות ראיון לסיום</summary>
        <ul className="list-disc ps-5 mt-1 space-y-1">
          {s.interview.map((x) => (
            <li key={x.q}>
              {x.q}{" "}
              <a href={x.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent underline">🔗 {x.src}</a>
            </li>
          ))}
        </ul>
        <p className="text-xs text-muted mt-1">כל שאלה עם הקישור לעמוד שממנו היא נלקחה.</p>
      </details>
      {s.cadence && <p className="text-xs text-muted">📺 רשות: {s.cadence}</p>}
      <div className="flex gap-2 flex-wrap">
        {lesson ? (
          <Link href={`/lessons/${lesson.id}`} className="btn">
            {lesson.status === "ready" ? "📄 השיעור: סיכום, תרגילים ושאלון" : "⏳ השיעור נכתב..."}
          </Link>
        ) : (
          <form action={openSessionLesson.bind(null, courseId, VLSI_PROGRAM.indexOf(s))}>
            <button className="btn">📄 להכין את השיעור</button>
          </form>
        )}
        <form action={startSession.bind(null, courseId, key, `שבוע ${s.week} · מפגש ${s.n}: ${s.title}`)}>
          <button className="btn-ghost">💬 להרחיב עם המורה</button>
        </form>
        <form action={setSessionDone.bind(null, key, !done)}>
          <button className="btn-ghost">{done ? "↩️ לא סיימתי" : "✓ סיימתי את המפגש"}</button>
        </form>
      </div>
    </article>
  );
}

/** "🎓 לימוד VLSI": the guided 12-week program (Friday + Saturday night), the topic map, and Cadence as an extra. */
export default async function SelfStudy() {
  const { sb } = await requireUser();
  const { data: all } = await sb.from("courses").select("name").eq("kind", "self");
  await ensureCadenceTracks(sb, (all ?? []).map((c) => c.name)).catch(() => 0);
  const [track, { data: tracks }] = await Promise.all([
    mainTrack(sb),
    sb.from("courses").select("id, name").eq("kind", "self").eq("archived", false).order("created_at"),
  ]);
  if (track) await Promise.all([ensureSelfSlots(sb, track.id).catch(() => {}), syncVlsiTasks(sb, track.id).catch(() => {})]);
  const [{ data: tasks }, pending] = await Promise.all([
    sb.from("deadlines").select("external_uid, done").like("external_uid", "vlsi:%"),
    catchUps(sb).catch(() => [] as string[]),
  ]);
  // The current and the next session have their lesson written ahead (once each); the rest when opened.
  if (track) {
    const idx = VLSI_PROGRAM.findIndex((s) => !(tasks ?? []).some((t) => t.done && t.external_uid === `vlsi:${sessionKey(s)}`));
    if (idx >= 0) await Promise.all([ensureSessionLesson(sb, track.id, idx), ensureSessionLesson(sb, track.id, idx + 1)]).catch(() => {});
  }
  const { data: lessonRows } = track
    ? await sb.from("lessons").select("id, number, status").eq("course_id", track.id).eq("kind", "lecture")
    : { data: [] };
  const lessonOf = new Map((lessonRows ?? []).map((l) => [l.number as number, { id: l.id as string, status: l.status as string }]));
  const doneKeys = new Set((tasks ?? []).filter((t) => t.done).map((t) => (t.external_uid as string).slice(5)));
  const dates = sessionDates(FREEZES);
  const currentIdx = VLSI_PROGRAM.findIndex((s) => !doneKeys.has(sessionKey(s)));
  const current = VLSI_PROGRAM[currentIdx];
  const { today } = weekDates();
  const freeze = FREEZES.find((f) => today >= f.from && today <= f.to);
  const weeks = [...new Set(VLSI_PROGRAM.map((s) => s.week))];
  const doneCount = VLSI_PROGRAM.filter((s) => doneKeys.has(sessionKey(s))).length;

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">🎓 לימוד VLSI</h1>
      <p className="text-sm text-muted">
        תוכנית מודרכת של 12 שבועות: בשישי בבוקר ובמוצאי שבת. בכל מפגש כתוב מה לפתוח, מה ללמוד עם המורה, מה לבנות ומה אמור
        לצאת. דדליין: סוף המפגש של מוצ״ש; מפגש שלא סיימת עובר לפעם הבאה.
      </p>
      <div className="h-1.5 rounded-full bg-bg overflow-hidden">
        <div className="h-full bg-good" style={{ width: `${(100 * doneCount) / VLSI_PROGRAM.length}%` }} />
      </div>
      <p className="text-xs text-muted">{doneCount} מתוך {VLSI_PROGRAM.length} מפגשים</p>
      {freeze && <p className="card text-sm text-warn">⏸️ {freeze.text}</p>}
      {pending.length > 0 && (
        <div className="card bg-warn-soft text-sm">
          <p className="font-semibold">קודם השלמות ({pending.length}) - ואז לימוד VLSI:</p>
          <ul className="list-disc ps-5 mt-1">{pending.slice(0, 5).map((t) => <li key={t}>{t}</li>)}</ul>
          <Link href="/week" className="text-accent">לשבוע שלי ←</Link>
        </div>
      )}

      {track && current && (
        <section className="space-y-2">
          <h2 className="font-semibold">המפגש הבא · שבוע {current.week}</h2>
          <SessionCard s={current} date={dates[currentIdx]} done={false} courseId={track.id} current lesson={lessonOf.get(currentIdx + 1)} />
        </section>
      )}
      {track && !current && <p className="card">🎉 סיימת את כל 12 השבועות!</p>}

      {track && weeks.map((w) => {
        const list = VLSI_PROGRAM.map((s, i) => ({ s, i })).filter(({ s }) => s.week === w);
        const allDone = list.every(({ s }) => doneKeys.has(sessionKey(s)));
        return (
          <Fold key={w} id={`vlsi-week-${w}`} title={`${allDone ? "✅ " : ""}שבוע ${w}: ${list[0].s.title}`}
            hint={`דדליין ${ddmm(dates[list[list.length - 1].i])}`}>
            <div className="space-y-3">
              {list.map(({ s, i }) => (
                <SessionCard key={sessionKey(s)} s={s} date={dates[i]} done={doneKeys.has(sessionKey(s))} courseId={track.id}
                  current={i === currentIdx} lesson={lessonOf.get(i + 1)} />
              ))}
            </div>
          </Fold>
        );
      })}

      {track && (
        <Link href={`/self/${track.id}`} className="card block">
          <span className="font-semibold">🗺️ מפת הנושאים והרמות שלי</span>
          <span className="block text-xs text-muted">איפה אתה בכל נושא (המורה מעדכן אחרי כל מפגש), והפרויקט.</span>
        </Link>
      )}
      <Fold id="vlsi-cadence" title="📺 קורסי Cadence (רשות)" hint={`${(tracks ?? []).filter((t) => t.id !== track?.id).length}`}>
        <ul className="divide-y divide-line">
          {(tracks ?? []).filter((t) => t.id !== track?.id).map((t) => (
            <li key={t.id}><Link href={`/self/${t.id}`} className="block py-2.5 text-sm">{t.name}</Link></li>
          ))}
        </ul>
        <p className="text-xs text-muted mt-2">הסרטונים באנגלית; בכל מפגש בתוכנית כתוב איזה פרק מתאים לו.</p>
      </Fold>
    </div>
  );
}
