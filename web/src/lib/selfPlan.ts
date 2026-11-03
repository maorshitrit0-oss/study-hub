import type { SupabaseClient } from "@supabase/supabase-js";
import { FREEZES, type Skill } from "./skills";

/**
 * Self-study on Friday morning and Saturday night (03/11/2026), when nothing from the week is left to catch up on.
 * The two slots live in the timetable (added once, editable there); each upcoming session gets the next topic of the
 * track that is not closed yet (level < 3), in the roadmap's order.
 */
export const SELF_SLOTS = [
  { weekday: 5, start: "10:00", end: "12:00" }, // Friday morning
  { weekday: 6, start: "20:30", end: "22:00" }, // Saturday night
];
const DAY_MS = 864e5;
const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);

/** The track the plan follows: the VLSI one when there is one, otherwise the first self-study track. */
export async function mainTrack(sb: SupabaseClient) {
  const { data } = await sb.from("courses").select("id, name").eq("kind", "self").eq("archived", false).order("created_at");
  return (data ?? []).find((c) => /VLSI/i.test(c.name)) ?? data?.[0] ?? null;
}

/** Adds the Friday / Saturday-night slots to the timetable once (he can move or delete them there). */
export async function ensureSelfSlots(sb: SupabaseClient, courseId: string) {
  const { data } = await sb.from("schedule_slots").select("id").eq("course_id", courseId).limit(1);
  if (data?.length) return;
  await sb.from("schedule_slots").insert(SELF_SLOTS.map((s) => ({
    course_id: courseId, title: "לימוד עצמי", kind: "other", weekday: s.weekday, start_time: s.start, end_time: s.end,
  })));
}

/** Open catch-up work: overdue uploads, unread lessons and unsolved exercise weeks. */
export async function catchUps(sb: SupabaseClient) {
  const { data } = await sb.from("deadlines").select("title, external_uid").eq("done", false)
    .lt("due_at", new Date().toISOString())
    .or("external_uid.like.upload:%,external_uid.like.prep:%,external_uid.like.ex:%,external_uid.like.labrep:%");
  return (data ?? []).map((d) => d.title as string);
}

export type Session = { date: string; weekday: number; start: string; topic: Skill | null };

/** The next sessions (weeks ahead) with a topic each; exam-period freezes are skipped. */
export async function selfPlan(sb: SupabaseClient, courseId: string, weeks = 6): Promise<Session[]> {
  const [{ data: slots }, { data: skills }] = await Promise.all([
    sb.from("schedule_slots").select("weekday, start_time").eq("course_id", courseId),
    sb.from("skills").select("*").eq("course_id", courseId).eq("kind", "topic").order("ord"),
  ]);
  const todo = ((skills ?? []) as Skill[]).filter((s) => s.level < 3);
  const out: Session[] = [];
  for (let k = 0; k < weeks * 7; k++) {
    const date = israelDate(new Date(Date.now() + k * DAY_MS));
    const weekday = new Date(`${date}T12:00:00Z`).getUTCDay();
    if (FREEZES.some((f) => date >= f.from && date <= f.to)) continue;
    for (const s of (slots ?? []).filter((x) => x.weekday === weekday).sort((a, b) => a.start_time.localeCompare(b.start_time))) {
      out.push({ date, weekday, start: s.start_time.slice(0, 5), topic: todo[out.length] ?? null });
    }
  }
  return out;
}
