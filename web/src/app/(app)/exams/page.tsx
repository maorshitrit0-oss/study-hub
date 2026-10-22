import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import DeadlineForm from "@/components/DeadlineForm";
import { addDeadline } from "../actions";
import { topicStats } from "@/lib/progress";
import { daysLeft, fmtDue, isPast, urgency } from "@/lib/format";
import type { Deadline } from "@/lib/types";

const tone = { bad: "text-bad bg-bad-soft", warn: "text-warn bg-warn-soft", muted: "text-accent bg-accent-soft" };

/** Exam board: every exam in date order, with a countdown and how ready the course is. */
export default async function Exams() {
  const { sb } = await requireUser();
  const [{ data: exams }, { data: courses }, stats] = await Promise.all([
    sb.from("deadlines").select("*").eq("kind", "exam").order("due_at"),
    sb.from("courses").select("id, name").order("name"),
    topicStats(sb),
  ]);
  const names = new Map((courses ?? []).map((c) => [c.id, c.name]));
  const readiness = (courseId: string | null) => {
    const cs = stats.filter((s) => s.course_id === courseId);
    const total = cs.reduce((a, s) => a + s.total, 0);
    const correct = cs.reduce((a, s) => a + s.correct, 0);
    return total ? Math.round((100 * correct) / total) : null;
  };
  const all = (exams ?? []) as Deadline[];
  const upcoming = all.filter((e) => !isPast(e.due_at) && !e.done);
  const past = all.filter((e) => isPast(e.due_at) || e.done).reverse();
  const next = upcoming[0];

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">לוח מבחנים</h1>

      {next && (
        <Link href={next.course_id ? `/courses/${next.course_id}/practice` : `/deadlines/${next.id}`} className="card block bg-accent-soft border-accent">
          <div className="text-sm text-accent font-medium">המבחן הבא</div>
          <div className="text-xl font-bold mt-1">{next.course_id ? names.get(next.course_id) : next.title}</div>
          <div className="text-sm text-muted">{next.title} · {fmtDue(next.due_at)}</div>
          <div className="flex items-end justify-between mt-3">
            <div className="text-3xl font-bold">{daysLeft(next.due_at)}</div>
            {readiness(next.course_id) !== null && (
              <div className="text-sm text-muted">שליטה בחומר: <b className="text-fg">{readiness(next.course_id)}%</b></div>
            )}
          </div>
          <div className="text-xs text-accent mt-2">לתרגול השאלות של הקורס ←</div>
        </Link>
      )}

      <section className="card">
        {upcoming.length ? (
          <ul className="divide-y divide-line">
            {upcoming.map((e) => {
              const r = readiness(e.course_id);
              return (
                <li key={e.id}>
                  <Link href={`/deadlines/${e.id}`} className="flex items-center gap-3 py-3">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{e.course_id ? names.get(e.course_id) : e.title}</div>
                      <div className="text-xs text-muted">
                        {e.title} · {fmtDue(e.due_at)}{r !== null ? ` · שליטה ${r}%` : ""}
                      </div>
                      {e.notes && <div className="text-xs text-muted truncate">{e.notes}</div>}
                    </div>
                    <span className={`text-xs rounded-full px-2 py-0.5 shrink-0 ${tone[urgency(e.due_at)]}`}>{daysLeft(e.due_at)}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-muted text-sm">אין מבחנים קרובים.</p>
        )}
      </section>

      <details className="card">
        <summary className="cursor-pointer font-semibold">+ הוספת מבחן</summary>
        <div className="mt-3">
          <DeadlineForm action={addDeadline} courses={courses ?? []} defaultKind="exam" submit="הוספה" />
        </div>
      </details>

      {past.length > 0 && (
        <details className="card">
          <summary className="cursor-pointer font-medium">מבחנים שעברו ({past.length})</summary>
          <ul className="divide-y divide-line mt-2">
            {past.map((e) => (
              <li key={e.id}>
                <Link href={`/deadlines/${e.id}`} className="flex justify-between py-2.5 text-muted text-sm">
                  <span>{e.course_id ? names.get(e.course_id) : e.title} · {e.title}</span>
                  <span>{fmtDue(e.due_at)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
