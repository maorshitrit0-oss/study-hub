import type { SupabaseClient } from "@supabase/supabase-js";
import { israelLocalToIso } from "./format";
import { classMeetings, SEMESTER_START, type Missing } from "./recordings";

/**
 * He studies one week behind the semester on purpose (recordings take days to come out, and he does not watch live):
 * in semester week 2 he learns week 1. Deadlines stay real. Same constant in worker/notify.py.
 */
export const STUDY_LAG = Number(process.env.STUDY_LAG ?? 1);
const DAY_MS = 864e5;
const UPLOAD = "upload:";
const SITE_WEEK = "site-week:";
const KIND = { lecture: "הרצאה", practice: "תרגול" } as const;

const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);
const ddmm = (date: string) => `${date.slice(8, 10)}/${date.slice(5, 7)}`;

/** Semester week of a YYYY-MM-DD date (week 1 starts on SEMESTER_START, a Sunday). */
export function semesterWeek(date: string) {
  return Math.floor((Date.parse(`${date}T12:00:00Z`) - Date.parse(`${SEMESTER_START}T12:00:00Z`)) / (7 * DAY_MS)) + 1;
}
export const todayWeek = () => semesterWeek(israelDate(new Date()));
export const studyWeek = () => Math.max(1, todayWeek() - STUDY_LAG);
/** First and last day (YYYY-MM-DD) of a semester week. */
export function weekDays(w: number) {
  const start = new Date(Date.parse(`${SEMESTER_START}T12:00:00Z`) + (w - 1) * 7 * DAY_MS);
  return { start: start.toISOString().slice(0, 10), end: new Date(start.getTime() + 6 * DAY_MS).toISOString().slice(0, 10) };
}

/** Last year's material imported from a lecturer's site (reference, not reading to catch up on). */
export const isSiteLesson = (l: { kind: string; source_url?: string | null }) => l.kind === "web" && !!l.source_url?.includes("notion");

export type PaceAlert = { course_id: string; title: string; due_at: string; need: number };

/** Assignments due within two weeks that need material from a week he has not reached yet. */
export async function paceAlerts(sb: SupabaseClient): Promise<PaceAlert[]> {
  const now = new Date();
  const { data } = await sb.from("deadlines").select("course_id, title, due_at, kind, check_due").eq("done", false)
    .in("kind", ["assignment", "lab_report"]).gte("due_at", now.toISOString())
    .lte("due_at", new Date(now.getTime() + 14 * DAY_MS).toISOString()).order("due_at");
  const study = studyWeek();
  return (data ?? []).filter((d) => d.course_id && !d.check_due)
    .map((d) => ({ course_id: d.course_id as string, title: d.title, due_at: d.due_at, need: semesterWeek(israelDate(new Date(d.due_at))) - 1 }))
    .filter((d) => d.need > study);
}

/**
 * Tasks that follow the timetable, kept in sync whenever home or the task list loads:
 * - "📹 להעלות" for every lecture/practice held with no recording (closes when one is uploaded or marked "none");
 * - a course with an imported site whose study week has no recording this year -> read last year's week instead.
 */
export async function syncWeekTasks(sb: SupabaseClient) {
  const [{ held, missing }, { data: tasks }, { data: courses }] = await Promise.all([
    classMeetings(sb),
    sb.from("deadlines").select("id, external_uid, done").or(`external_uid.like.${UPLOAD}%,external_uid.like.${SITE_WEEK}%`),
    sb.from("courses").select("id, name"),
  ]);
  const name = new Map((courses ?? []).map((c) => [c.id, c.name as string]));
  const have = new Map((tasks ?? []).map((t) => [t.external_uid as string, t]));
  const key = (m: Missing) => `${UPLOAD}${m.slot.id}:${m.date}`;
  const open = new Set(missing.map(key));
  const add = [];
  for (const m of missing) {
    if (have.has(key(m))) continue;
    const w = semesterWeek(m.date);
    add.push({
      course_id: m.slot.course_id, kind: "other",
      title: `📹 להעלות: ${KIND[m.slot.kind as keyof typeof KIND] ?? m.slot.title} שבוע ${w} (${ddmm(m.date)}) · ${name.get(m.slot.course_id!) ?? m.slot.title}`,
      // Two days to upload, so the chapter is ready by the time he reaches that week.
      due_at: israelLocalToIso(`${israelDate(new Date(Date.parse(`${m.date}T12:00:00Z`) + 2 * DAY_MS))}T20:00`),
      done: false,
      notes: "נוצר אוטומטית ממערכת השעות. נסגר לבד כשמעלים את ההקלטה, או כשמסמנים 'אין הקלטה' בדף הבית.",
      external_uid: key(m),
    });
  }
  // Uploaded / marked since: close.
  const close = held.map(key).filter((k) => !open.has(k) && have.get(k) && !have.get(k)!.done).map((k) => have.get(k)!.id);

  // Last year's week from the lecturer's site, when this year's lecture of that week is missing.
  const study = studyWeek();
  const { data: lessons } = await sb.from("lessons").select("id, course_id, kind, number, source_url, status, read_at");
  const lectures = new Set((lessons ?? []).filter((l) => l.kind === "lecture" && l.number).map((l) => `${l.course_id}|${l.number}`));
  for (const l of lessons ?? []) {
    if (!isSiteLesson(l) || !l.number || l.status !== "ready") continue;
    const k = `${SITE_WEEK}${l.id}`;
    const hasThisYear = lectures.has(`${l.course_id}|${l.number}`);
    const t = have.get(k);
    if (t) {
      if (!t.done && (hasThisYear || l.read_at)) close.push(t.id);
      continue;
    }
    if (l.number > study || hasThisYear || l.read_at) continue;
    add.push({
      course_id: l.course_id, kind: "other",
      title: `📼 ${name.get(l.course_id) ?? ""} שבוע ${l.number}: אין הקלטה מהשנה - לקרוא את החומר משנה שעברה`,
      due_at: israelLocalToIso(`${weekDays(l.number + STUDY_LAG).end}T20:00`),
      done: false,
      notes: "נוצר אוטומטית. נסגר לבד כשמסמנים את הפרק כנקרא, או כשמעלים את ההרצאה של השנה.",
      external_uid: k,
    });
  }
  if (add.length) await sb.from("deadlines").upsert(add, { onConflict: "user_id,external_uid", ignoreDuplicates: true });
  if (close.length) await sb.from("deadlines").update({ done: true }).in("id", close);
}
