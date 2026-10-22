import type { SupabaseClient } from "@supabase/supabase-js";
import { israelLocalToIso } from "./format";
import { SEMESTER_START } from "./recordings";
import { lessonName, type Slot } from "./types";

const DAY_MS = 864e5;
const PREFIX = "prep:";
const NEXT = { lecture: "ההרצאה הבאה", practice: "התרגול הבא" } as const;

const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);

/** Start of the course's first class after `from`: same kind (lecture/practice) if the timetable has one. */
function nextClass(slots: Slot[], courseId: string, kind: string, from: Date) {
  const mine = slots.filter((s) => s.course_id === courseId);
  const pool = mine.some((s) => s.kind === kind) ? mine.filter((s) => s.kind === kind) : mine;
  for (let k = 1; k <= 14 && pool.length; k++) {
    const date = israelDate(new Date(from.getTime() + k * DAY_MS));
    const weekday = new Date(`${date}T12:00:00Z`).getUTCDay();
    const slot = pool.filter((s) => s.weekday === weekday).sort((a, b) => a.start_time.localeCompare(b.start_time))[0];
    if (slot) return israelLocalToIso(`${date}T${slot.start_time.slice(0, 5)}`);
  }
  return new Date(from.getTime() + 7 * DAY_MS).toISOString();
}

/**
 * Every lecture/practice gets a task "learn it before the next class of the course", due when that class starts;
 * the task closes itself once the chapter is marked read. Idempotent - runs when the task list is shown.
 */
export async function syncPrepTasks(sb: SupabaseClient) {
  const [{ data: lessons }, { data: slots }, { data: tasks }, { data: courses }] = await Promise.all([
    sb.from("lessons").select("id, course_id, kind, number, title, read_at, created_at")
      .in("kind", ["lecture", "practice"]).gte("created_at", `${SEMESTER_START}T00:00:00+03:00`),
    sb.from("schedule_slots").select("*"),
    sb.from("deadlines").select("id, external_uid, done").like("external_uid", `${PREFIX}%`),
    sb.from("courses").select("id, kind"),
  ]);
  const kinds = new Map((courses ?? []).map((c) => [c.id, c.kind]));
  const have = new Map((tasks ?? []).map((t) => [t.external_uid as string, t]));
  const add = [];
  for (const l of lessons ?? []) {
    if (!["course", "project"].includes(kinds.get(l.course_id) ?? "")) continue;
    const t = have.get(PREFIX + l.id);
    if (t) {
      if (l.read_at && !t.done) await sb.from("deadlines").update({ done: true }).eq("id", t.id);
      continue;
    }
    add.push({
      course_id: l.course_id,
      kind: "other",
      title: `📖 ללמוד את ${lessonName(l)} לפני ${NEXT[l.kind as keyof typeof NEXT]}`,
      due_at: nextClass((slots ?? []) as Slot[], l.course_id, l.kind, new Date(l.created_at)),
      done: !!l.read_at,
      notes: "נוצר אוטומטית. נסגר לבד כשמסמנים את הפרק כנקרא.",
      external_uid: PREFIX + l.id,
    });
  }
  if (add.length) await sb.from("deadlines").upsert(add, { onConflict: "user_id,external_uid", ignoreDuplicates: true });
}

/**
 * One-off repair: the Moodle tasks of 22/10/2026 were inserted by SQL that looked for "ליניאר", but his course is
 * spelled "לינאריים", so they were left without a course. Attach them (and any like them) to the right course.
 */
export async function attachOrphanTasks(sb: SupabaseClient) {
  // Readable Moodle screenshot (22/10/2026): linear circuits assignments 1-5 all close Fri 08/01/2027 23:00.
  await sb.from("deadlines").update({
    due_at: "2027-01-08T23:00:00+02:00", check_due: false,
    notes: "לפי המודל: נפתחה 21/10/2026, נסגרת יום שישי 08/01/2027 בשעה 23:00 (כל 5 המטלות באותו מועד).",
  }).like("external_uid", "moodle-shot-linear-%").eq("check_due", true);
  const { data: orphans } = await sb.from("deadlines").select("id, external_uid").is("course_id", null).like("external_uid", "moodle-shot-%");
  if (!orphans?.length) return;
  const { data: courses } = await sb.from("courses").select("id, name, kind").neq("kind", "lab");
  const find = (re: RegExp) => (courses ?? []).find((c) => re.test(c.name))?.id;
  const target: Record<string, string | undefined> = { linear: find(/לינאר|ליניאר/), java: find(/java/i) };
  for (const o of orphans) {
    const key = (o.external_uid as string).replace(/^moodle-shot-/, "").replace(/-\d+$/, "");
    if (target[key]) await sb.from("deadlines").update({ course_id: target[key] }).eq("id", o.id);
  }
}

/** Close the lesson's prep task when it is read (and reopen it if the read mark is removed). */
export async function closePrepTask(sb: SupabaseClient, lessonId: string, read: boolean) {
  await sb.from("deadlines").update({ done: read }).eq("external_uid", PREFIX + lessonId);
}
