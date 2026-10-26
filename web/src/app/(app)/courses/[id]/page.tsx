import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import AddLesson from "@/components/AddLesson";
import DeadlineRow from "@/components/DeadlineRow";
import Materials from "@/components/Materials";
import SiteImport from "@/components/SiteImport";
import Studio from "@/components/Studio";
import { loadMedia } from "@/lib/studio";
import CourseFacts, { type Fact } from "@/components/CourseFacts";
import { isWeak, pct, topicStats } from "@/lib/progress";
import { isPast } from "@/lib/format";
import { forProjection, needed, pending, sameCode, totals, type GradeRow } from "@/lib/gradeGoal";
import { LEVEL_LABEL, LEVEL_TONE, weeklyPlan } from "@/lib/plan";
import { DAYS, EXAM_LABEL, KIND_LABEL, SLOT_LABEL, hhmm, type Slot, lessonName, type Course, type Deadline, type Lesson } from "@/lib/types";

const STATUS: Record<Lesson["status"], [string, string]> = {
  queued: ["בתור", "text-muted"],
  processing: ["בעיבוד", "text-warn"],
  transcribed: ["מחכה לכתיבה", "text-warn"],
  ready: ["מוכן", "text-good"],
  error: ["שגיאה", "text-bad"],
};

/** Lectures, practices and other material as separate groups (a lab keeps one list). */
function groupLessons(ls: Lesson[], isLab: boolean): [string, Lesson[]][] {
  if (isLab) return [["", ls]];
  const groups: [string, Lesson[]][] = [
    ["הרצאות", ls.filter((l) => l.kind === "lecture")],
    ["תרגולים", ls.filter((l) => l.kind === "practice")],
    ["חומר נוסף", ls.filter((l) => l.kind !== "lecture" && l.kind !== "practice")],
  ];
  return groups.filter(([, g]) => g.length);
}

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
  if (c.kind === "self") redirect(`/self/${id}`); // self-study has its own page
  const [plan, { data: grades }] = await Promise.all([
    weeklyPlan(sb).then((all) => all.find((p) => p.course.id === id)),
    sb.from("grades").select("*"),
  ]);
  // Grade needed here for a 90 average at the end of the degree, assuming the same grade in everything left.
  const gradeRows = forProjection((grades ?? []) as GradeRow[]);
  const open = pending(gradeRows).filter((r) => Number(r.credits) > 0);
  const mine = open.find((r) => sameCode(r.code, c.code) || r.name === c.name);
  const sofar = totals(gradeRows);
  const need90 = mine ? needed(90, sofar.sum, sofar.credits, open.reduce((a, r) => a + Number(r.credits), 0)) : null;
  const ls = (lessons ?? []) as Lesson[];
  const nextByKind = Object.fromEntries(["lecture", "practice", "lab", "other"]
    .map((k) => [k, Math.max(0, ...ls.filter((l) => l.kind === k).map((l) => l.number ?? 0)) + 1]));
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
          {need90 !== null && (
            <Link href="/grades" className="chip">🎯 לממוצע 90 בסוף התואר: {need90 > 100 ? "לא אפשרי" : `צריך ${Math.ceil(need90)}`}</Link>
          )}
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

      <div className={`grid ${c.kind === "lab" ? "grid-cols-2" : "grid-cols-3"} gap-3`}>
        <Link href={`/courses/${id}/chat`} className="card text-center font-medium">💬 צ&apos;אט על הקורס</Link>
        <Link href={`/courses/${id}/practice`} className="card text-center font-medium">✍️ תרגול שאלות</Link>
        {c.kind === "lab" && <Link href={`/courses/${id}/entry`} className="card text-center font-medium">🎯 בוחן כניסה</Link>}
        <Link href={`/words?course=${id}`} className="card text-center font-medium">🔤 מילים באנגלית</Link>
      </div>

      {plan && (
        <section className="card">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-semibold">המצב שלי מול הכיתה</h2>
            <span className={`text-xs rounded-full px-2 py-0.5 ${LEVEL_TONE[plan.level]}`}>{LEVEL_LABEL[plan.level]}</span>
          </div>
          {/* Lectures and practices are counted separately in every course; a lab counts experiments. */}
          <div className={`grid ${c.kind === "lab" ? "grid-cols-3" : "grid-cols-4"} gap-2 text-center`}>
            {(c.kind === "lab"
              ? [[plan.classLessons, "ניסויים"], [plan.read, "קראתי"]]
              : [[plan.lectures, "הרצאות בכיתה"], [plan.practices, "תרגולים בכיתה"], [plan.read, "קראתי"]]
            ).map(([n, label]) => (
              <div key={label} className="rounded-xl bg-accent-soft p-2">
                <div className="text-xl font-bold">{n}</div>
                <div className="text-xs text-muted">{label}</div>
              </div>
            ))}
            <div className="rounded-xl bg-accent-soft p-2">
              <div className="text-xl font-bold">{plan.mastery === null ? "—" : `${plan.mastery}%`}</div>
              <div className="text-xs text-muted">שליטה בחומר</div>
            </div>
          </div>
          {plan.reasons.length > 0 && <p className="text-sm text-muted mt-3">השבוע: {plan.reasons.join(" · ")}</p>}
          {plan.reminders.length > 0 && (
            <ul className="text-sm mt-2 space-y-1">
              {plan.reminders.map((r) => <li key={r.text}><Link href={r.href}>📌 {r.text}</Link></li>)}
            </ul>
          )}
        </section>
      )}

      {(c.syllabus_topics?.length ?? 0) > 0 && plan && (
        <details className="card">
          <summary className="cursor-pointer font-semibold">
            הסילבוס · נלמדו בכיתה {plan.covered.size} מתוך {c.syllabus_topics!.length} נושאים
          </summary>
          <ol className="mt-3 space-y-1.5 text-sm">
            {c.syllabus_topics!.map((t, i) => {
              const n = i + 1;
              const taught = plan.covered.has(n);
              const read = plan.readCovered.has(n);
              return (
                <li key={n} className="flex gap-2">
                  <span className="w-5 shrink-0 text-center">{read ? "✅" : taught ? "🟡" : "⚪"}</span>
                  <span className={taught ? "" : "text-muted"}>{n}. {t}</span>
                </li>
              );
            })}
          </ol>
          <p className="text-xs text-muted mt-3">✅ נלמד וקראתי · 🟡 נלמד בכיתה ועוד לא קראתי · ⚪ עוד לא נלמד</p>
        </details>
      )}

      <CourseFacts courseId={id} facts={(facts ?? []) as Fact[]} reservist={!!settings?.is_reservist}
        lessonNames={new Map(ls.map((l) => [l.id, lessonName(l)]))} />

      <section className="card scroll-mt-4" id="add">
        <h2 className="font-semibold mb-3">{c.kind === "lab" ? "הוספת ניסוי" : "הוספת הרצאה / תרגול"}</h2>
        <AddLesson courseId={id} userId={userId} nextByKind={nextByKind} isLab={c.kind === "lab"} />
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
          groupLessons(ls, c.kind === "lab").map(([label, group]) => (
            <div key={label}>
              {label && <h3 className="text-sm text-muted mt-3">{label} ({group.length})</h3>}
              <ul className="divide-y divide-line">
                {group.map((l) => (
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
            </div>
          ))
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

      {readyCount > 0 && (
        <Studio courseId={id} items={await loadMedia(sb, { courseId: id })}
          lessons={ls.filter((l) => l.status === "ready").map((l) => ({ id: l.id, label: `${lessonName(l)}${l.title && l.kind !== "web" ? ` · ${l.title}` : ""}` }))} />
      )}

      <section className="card">
        <h2 className="font-semibold mb-3">קבצים (מצגות, מבחני עבר, סילבוס)</h2>
        <Materials courseId={id} userId={userId} items={materials ?? []} isLab={c.kind === "lab"} />
        <SiteImport courseId={id} imported={(materials ?? []).some((m) => m.storage_path.endsWith("/site.md"))} />
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
