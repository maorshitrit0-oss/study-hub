import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import AddLesson from "@/components/AddLesson";
import DeadlineRow from "@/components/DeadlineRow";
import Materials from "@/components/Materials";
import CourseFacts, { type Fact } from "@/components/CourseFacts";
import { isWeak, pct, topicStats } from "@/lib/progress";
import { isPast } from "@/lib/format";
import { DAYS, EXAM_LABEL, KIND_LABEL, SLOT_LABEL, hhmm, type Slot, lessonName, type Course, type Deadline, type Lesson } from "@/lib/types";

const STATUS: Record<Lesson["status"], [string, string]> = {
  queued: ["בתור", "text-muted"],
  processing: ["בעיבוד", "text-warn"],
  transcribed: ["מחכה לכתיבה", "text-warn"],
  ready: ["מוכן", "text-good"],
  error: ["שגיאה", "text-bad"],
};

export default async function CoursePage({ params }: PageProps<"/courses/[id]">) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: lessons }, { data: materials }, { data: deadlines }, stats, { data: facts }, { data: settings }, { data: slots }] = await Promise.all([
    sb.from("courses").select("*").eq("id", id).maybeSingle(),
    sb.from("lessons").select("id, kind, number, title, status, progress, read_at, created_at").eq("course_id", id).order("created_at"),
    sb.from("materials").select("id, title, kind, storage_path").eq("course_id", id).order("created_at"),
    sb.from("deadlines").select("*").eq("course_id", id).order("due_at"),
    topicStats(sb, id),
    sb.from("course_facts").select("id, category, text, lesson_id").eq("course_id", id).order("created_at"),
    sb.from("settings").select("is_reservist").eq("user_id", userId).maybeSingle(),
    sb.from("schedule_slots").select("*").eq("course_id", id).order("weekday").order("start_time"),
  ]);
  if (!course) notFound();
  const c = course as Course;
  const ls = (lessons ?? []) as Lesson[];
  const nextNumber = Math.max(0, ...ls.filter((l) => l.kind === "lecture").map((l) => l.number ?? 0)) + 1;
  const upcoming = ((deadlines ?? []) as Deadline[]).filter((d) => !d.done || !isPast(d.due_at));
  const answered = stats.reduce((a, s) => a + s.answered, 0);
  const readyCount = ls.filter((l) => l.status === "ready").length;
  const readCount = ls.filter((l) => l.status === "ready" && l.read_at).length;

  return (
    <div className="space-y-5">
      <header>
        <div className="flex justify-between items-start gap-3">
          <div>
            <h1 className="text-2xl font-bold">{c.name}</h1>
            <p className="text-sm text-muted mt-0.5">
              {KIND_LABEL[c.kind]}
              {c.year ? ` · שנה ${c.year}` : ""}
              {c.semester ? ` · סמסטר ${c.semester}` : ""}
              {c.lecturer ? ` · ${c.lecturer}` : ""}
            </p>
          </div>
          <Link href={`/courses/${id}/edit`} className="btn-ghost text-sm">עריכה</Link>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {c.exam_type && <span className="chip">מבחן: {EXAM_LABEL[c.exam_type]}</span>}
          {c.grade_weights.map((w) => <span key={w.name} className="chip">{w.name} {w.weight}%</span>)}
          {c.archived && <span className="chip">בארכיון</span>}
        </div>
        {c.notes && <p className="text-sm text-muted mt-2 whitespace-pre-line">{c.notes}</p>}
        {(slots ?? []).length > 0 && (
          <ul className="text-sm mt-2 space-y-0.5">
            {((slots ?? []) as Slot[]).map((s) => (
              <li key={s.id} className="text-muted">
                🕒 {SLOT_LABEL[s.kind]}: יום {DAYS[s.weekday]} {hhmm(s.start_time)}–{hhmm(s.end_time)}{s.room ? ` · חדר ${s.room}` : ""}
              </li>
            ))}
          </ul>
        )}
      </header>

      <div className="grid grid-cols-2 gap-3">
        <Link href={`/courses/${id}/chat`} className="card text-center font-medium">💬 צ&apos;אט על הקורס</Link>
        <Link href={`/courses/${id}/practice`} className="card text-center font-medium">✍️ תרגול שאלות</Link>
      </div>

      <CourseFacts facts={(facts ?? []) as Fact[]} reservist={!!settings?.is_reservist}
        lessonNames={new Map(ls.map((l) => [l.id, lessonName(l)]))} />

      <section className="card scroll-mt-4" id="add">
        <h2 className="font-semibold mb-3">הוספת הרצאה / תרגול</h2>
        <AddLesson courseId={id} nextNumber={nextNumber} />
      </section>

      <section className="card">
        <div className="flex justify-between items-baseline mb-1">
          <h2 className="font-semibold">חומר הקורס</h2>
          {readyCount > 0 && <span className="text-sm text-muted">קראת {readCount} מתוך {readyCount}</span>}
        </div>
        {readyCount > 0 && (
          <div className="h-1.5 rounded-full bg-bg overflow-hidden mb-2">
            <div className="h-full bg-good" style={{ width: `${(100 * readCount) / readyCount}%` }} />
          </div>
        )}
        {ls.length ? (
          <ul className="divide-y divide-line">
            {ls.map((l) => (
              <li key={l.id}>
                <Link href={`/lessons/${l.id}`} className="flex items-center justify-between gap-3 py-3">
                  <span className="min-w-0">
                    <span className={`font-medium ${l.read_at ? "text-muted" : ""}`}>{lessonName(l)}</span>
                    {l.title && l.kind !== "web" && <span className="text-sm text-muted"> · {l.title}</span>}
                    {l.read_at && <span className="text-xs text-good"> ✓ נקרא</span>}
                  </span>
                  <span className={`text-xs shrink-0 ${STATUS[l.status][1]}`}>{STATUS[l.status][0]}</span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted py-2">עוד אין חומר. הדבק קישור לזום למעלה.</p>
        )}
      </section>

      {stats.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-1">איפה אני עומד</h2>
          <p className="text-xs text-muted mb-3">
            לפי התשובה האחרונה לכל שאלה. {answered ? "" : "פתור שאלונים כדי לראות את המצב."}
          </p>
          <ul className="space-y-2.5">
            {stats.sort((a, b) => (pct(a) ?? 101) - (pct(b) ?? 101)).map((s) => {
              const p = pct(s);
              return (
                <li key={s.topic}>
                  <Link href={`/courses/${id}/practice?topic=${encodeURIComponent(s.topic)}`}>
                    <div className="flex justify-between text-sm">
                      <span>{s.topic}{isWeak(s) && <span className="text-bad"> · לחזק</span>}</span>
                      <span className="text-muted">{p === null ? "לא נבדק" : `${p}%`} · {s.answered}/{s.total}</span>
                    </div>
                    <div className="mt-1 h-1.5 rounded-full bg-bg overflow-hidden">
                      <div className={`h-full ${p === null ? "" : p < 70 ? "bg-bad" : p < 85 ? "bg-warn" : "bg-good"}`}
                        style={{ width: `${p ?? 0}%` }} />
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <section className="card">
        <h2 className="font-semibold mb-3">קבצים (מצגות, מבחני עבר, סילבוס)</h2>
        <Materials courseId={id} userId={userId} items={materials ?? []} />
      </section>

      <section className="card">
        <div className="flex justify-between items-center mb-1">
          <h2 className="font-semibold">משימות ומבחנים</h2>
          <Link href={`/deadlines?course=${id}`} className="text-sm text-accent">+ הוספה</Link>
        </div>
        {upcoming.length ? (
          <ul className="divide-y divide-line">{upcoming.map((d) => <DeadlineRow key={d.id} d={d} />)}</ul>
        ) : (
          <p className="text-sm text-muted py-2">אין משימות פתוחות.</p>
        )}
      </section>
    </div>
  );
}
