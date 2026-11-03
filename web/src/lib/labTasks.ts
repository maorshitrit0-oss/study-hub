import type { SupabaseClient } from "@supabase/supabase-js";
import { israelLocalToIso } from "./format";
import { SEMESTER_START } from "./recordings";

const DAY_MS = 864e5;
const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);

/**
 * Lab: experiment N is the Nth lab day in the timetable; on that day he hands in the summary report of experiment
 * N-1. Tasks "📝 להעלות דוח מסכם ניסוי N-1" (done when a file "דוח מסכם ניסוי N-1 ..." is in the course) and
 * "🎯 לרשום מה שאלו בבוחן הכניסה של ניסוי N-1" (done when a report of that experiment's entry quiz exists).
 */
export async function syncLabTasks(sb: SupabaseClient) {
  const [{ data: slots }, { data: tasks }] = await Promise.all([
    sb.from("schedule_slots").select("course_id, weekday, end_time").eq("kind", "lab").not("course_id", "is", null),
    sb.from("deadlines").select("id, external_uid, done").or("external_uid.like.labrep:%,external_uid.like.labq:%"),
  ]);
  if (!slots?.length) return;
  const have = new Map((tasks ?? []).map((t) => [t.external_uid as string, t]));
  const today = israelDate(new Date());
  const add: Record<string, unknown>[] = [], close: string[] = [];
  for (const courseId of [...new Set(slots.map((s) => s.course_id as string))]) {
    const days = new Set(slots.filter((s) => s.course_id === courseId).map((s) => s.weekday));
    const dates: string[] = [];
    for (let t = Date.parse(`${SEMESTER_START}T12:00:00Z`); israelDate(new Date(t)) <= today; t += DAY_MS) {
      if (days.has(new Date(t).getUTCDay())) dates.push(israelDate(new Date(t)));
    }
    const [{ data: mats }, entry] = await Promise.all([
      sb.from("materials").select("title").eq("course_id", courseId),
      sb.from("entry_reports").select("experiment").eq("course_id", courseId),
    ]);
    const reported = new Set((entry.data ?? []).map((r) => r.experiment));
    dates.forEach((date, i) => {
      const n = i; // experiment of the previous lab day (lab day i+1 = experiment i+1)
      if (n < 1) return;
      const items = [
        [`labrep:${courseId}:${n}`, `📝 להעלות דוח מסכם ניסוי ${n} (שלך ושל השותפה)`,
          (mats ?? []).some((m) => new RegExp(`דוח מסכם ניסוי ${n}(?!\\d)`).test(m.title))],
        [`labq:${courseId}:${n}`, `🎯 לרשום מה שאלו בבוחן הכניסה של ניסוי ${n}`, reported.has(n)],
      ] as const;
      for (const [uid, title, done] of items) {
        const t = have.get(uid);
        if (t) { if (done && !t.done) close.push(t.id); continue; }
        add.push({ course_id: courseId, kind: "other", title, done, due_at: israelLocalToIso(`${date}T23:00`),
          notes: "נוצר אוטומטית ביום המעבדה. נסגר לבד כשמעלים את הדוח / רושמים את השאלות.", external_uid: uid });
      }
    });
  }
  if (add.length) await sb.from("deadlines").upsert(add, { onConflict: "user_id,external_uid", ignoreDuplicates: true });
  if (close.length) await sb.from("deadlines").update({ done: true }).in("id", close);
}
