import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import DeadlineRow from "@/components/DeadlineRow";
import { isWeak, pct, topicStats } from "@/lib/progress";
import { isoFromNow, israelNow } from "@/lib/format";
import SlotCard from "@/components/SlotCard";
import MissingRecordings from "@/components/MissingRecordings";
import { missingRecordings } from "@/lib/recordings";
import { LEVEL_LABEL, LEVEL_TONE, weeklyPlan } from "@/lib/plan";
import { UsageAlerts, type Snapshot } from "@/components/Usage";
import { DAYS, lessonName, type Course, type Deadline, type Lesson, type Slot } from "@/lib/types";

export default async function Home() {
  const { sb } = await requireUser();
  const in14 = isoFromNow(14);
  const now = israelNow();
  const [{ data: courses }, { data: deadlines }, { data: lessons }, stats, { data: today }, missing] = await Promise.all([
    sb.from("courses").select("*").eq("archived", false).order("year").order("name"),
    sb.from("deadlines").select("*").eq("done", false).lte("due_at", in14).order("due_at").limit(8),
    sb.from("lessons").select("id, course_id, kind, number, title, status, progress, read_at, created_at")
      .order("created_at", { ascending: false }).limit(30),
    topicStats(sb),
    sb.from("schedule_slots").select("*").eq("weekday", now.weekday).order("start_time"),
    missingRecordings(sb).catch(() => []),
  ]);
  const [plan, { data: usage }] = await Promise.all([
    weeklyPlan(sb),
    sb.from("usage_snapshot").select("data").eq("id", 1).maybeSingle(),
  ]);
  const usageAlerts = (usage?.data as Snapshot | undefined)?.alerts ?? [];
  const focus = plan.filter((p) => p.score > 0).slice(0, 3);
  const reminders = plan.flatMap((p) => p.reminders).slice(0, 6);
  const todaySlots = ((today ?? []) as Slot[]).filter((s) => s.end_time.slice(0, 5) > now.time);
  const courseName = new Map((courses as Course[] | null)?.map((c) => [c.id, c.name]));
  const active = (lessons as Lesson[] | null)?.filter((l) => l.status !== "ready" && l.status !== "error") ?? [];
  const unread = (lessons as Lesson[] | null)?.filter((l) => l.status === "ready" && !l.read_at).slice(0, 5) ?? [];
  const weak = stats.filter(isWeak).sort((a, b) => (pct(a) ?? 0) - (pct(b) ?? 0)).slice(0, 5);

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">מה לומדים היום?</h1>
        <Link href="/settings" aria-label="הגדרות" className="text-muted p-2 -m-2">
          <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
          </svg>
        </Link>
      </div>

      {todaySlots.length > 0 && (
        <section className="card">
          <div className="flex justify-between items-center mb-2">
            <h2 className="font-semibold">היום באוניברסיטה · יום {DAYS[now.weekday]}</h2>
            <Link href="/schedule" className="text-sm text-accent">המערכת</Link>
          </div>
          <div className="space-y-2">
            {todaySlots.map((s) => (
              <SlotCard key={s.id} s={s} courseName={s.course_id ? courseName.get(s.course_id) : undefined}
                now={s.start_time.slice(0, 5) <= now.time} />
            ))}
          </div>
        </section>
      )}

      <MissingRecordings items={missing} courseName={courseName} />

      {usageAlerts.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">⚠️ צריך לטפל</h2>
          <UsageAlerts snap={usage!.data as Snapshot} />
        </section>
      )}

      {focus.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">על מה להשקיע השבוע</h2>
          <ul className="space-y-3">
            {focus.map((p) => (
              <li key={p.course.id}>
                <Link href={`/courses/${p.course.id}`} className="block">
                  <div className="flex justify-between items-center gap-2">
                    <span className="font-medium">{p.course.name}</span>
                    <span className={`text-xs rounded-full px-2 py-0.5 shrink-0 ${LEVEL_TONE[p.level]}`}>{LEVEL_LABEL[p.level]}</span>
                  </div>
                  <div className="text-xs text-muted mt-0.5">{p.reasons.join(" · ")}</div>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {reminders.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">תזכורות</h2>
          <ul className="space-y-2 text-sm">
            {reminders.map((r) => (
              <li key={r.text}><Link href={r.href} className="flex gap-2"><span>📌</span><span>{r.text}</span></Link></li>
            ))}
          </ul>
        </section>
      )}

      {active.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">בעיבוד</h2>
          <ul className="space-y-2">
            {active.map((l) => (
              <li key={l.id}>
                <Link href={`/lessons/${l.id}`} className="flex justify-between gap-2">
                  <span>{courseName.get(l.course_id)} · {lessonName(l)}</span>
                  <span className="text-xs text-muted truncate">{l.progress ?? "בתור"}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {unread.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">מחכה לקריאה</h2>
          <ul className="divide-y divide-line">
            {unread.map((l) => (
              <li key={l.id}>
                <Link href={`/lessons/${l.id}`} className="flex justify-between py-2.5">
                  <span>{lessonName(l)}</span>
                  <span className="text-sm text-muted">{courseName.get(l.course_id)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="card">
        <div className="flex justify-between items-center mb-1">
          <h2 className="font-semibold">דדליינים קרובים</h2>
          <Link href="/deadlines" className="text-sm text-accent">הכל</Link>
        </div>
        {deadlines?.length ? (
          <ul className="divide-y divide-line">
            {(deadlines as Deadline[]).map((d) => (
              <DeadlineRow key={d.id} d={d} courseName={d.course_id ? courseName.get(d.course_id) : undefined} />
            ))}
          </ul>
        ) : (
          <p className="text-muted text-sm py-2">אין משימות בשבועיים הקרובים.</p>
        )}
      </section>

      {weak.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">נושאים לחיזוק</h2>
          <ul className="space-y-2">
            {weak.map((s) => (
              <li key={`${s.course_id}${s.topic}`}>
                <Link href={`/courses/${s.course_id}/practice?topic=${encodeURIComponent(s.topic)}`} className="flex justify-between">
                  <span>{s.topic} <span className="text-xs text-muted">· {courseName.get(s.course_id)}</span></span>
                  <span className="text-bad font-medium">{pct(s)}%</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <div className="flex justify-between items-center mb-2">
          <h2 className="font-semibold">הקורסים שלי</h2>
          <Link href="/courses/new" className="btn-ghost text-sm">+ קורס</Link>
        </div>
        {courses?.length ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {(courses as Course[]).map((c) => {
              const cs = stats.filter((s) => s.course_id === c.id);
              const answered = cs.reduce((a, s) => a + s.answered, 0);
              const correct = cs.reduce((a, s) => a + s.correct, 0);
              const total = cs.reduce((a, s) => a + s.total, 0);
              return (
                <Link key={c.id} href={`/courses/${c.id}`} className="card block">
                  <div className="font-semibold">{c.name}</div>
                  <div className="text-xs text-muted mt-0.5">
                    {c.year ? `שנה ${c.year}` : ""} {c.semester ? `· סמסטר ${c.semester}` : ""}
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-bg overflow-hidden">
                    <div className="h-full bg-good" style={{ width: `${total ? (100 * correct) / total : 0}%` }} />
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {total ? `${correct}/${total} שאלות נשלטות · ${answered ? Math.round((100 * correct) / answered) : 0}% הצלחה` : "עוד אין שאלות"}
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="card text-center py-8">
            <p className="mb-3">עוד אין קורסים. מתחילים מהוספת קורס ראשון.</p>
            <Link href="/courses/new" className="btn">הוספת קורס</Link>
          </div>
        )}
      </section>
    </div>
  );
}
