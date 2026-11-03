import type { SupabaseClient } from "@supabase/supabase-js";
import { FREEZES } from "./skills";

/**
 * Self-study on Friday morning and Saturday night (03/11/2026), when nothing from the week is left to catch up on.
 * The two slots live in the timetable (added once, editable there); the sessions are the 12-week VLSI program
 * (vlsiProgram.ts), each a task he marks done on the VLSI page.
 */
export const SELF_SLOTS = [
  { weekday: 5, start: "10:00", end: "12:00" }, // Friday morning
  { weekday: 6, start: "20:30", end: "22:00" }, // Saturday night
];

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

/**
 * Each program session is a task "🎓 VLSI שבוע W · מפגש N" due at the end of its slot (he marks it done on the VLSI
 * page); an unfinished one stays open, so it carries over to the next session.
 */
export async function syncVlsiTasks(sb: SupabaseClient, courseId: string) {
  const { VLSI_PROGRAM, sessionDates, sessionKey } = await import("./vlsiProgram");
  const { israelLocalToIso } = await import("./format");
  const dates = sessionDates(FREEZES);
  const { data: have } = await sb.from("deadlines").select("external_uid").like("external_uid", "vlsi:%");
  const known = new Set((have ?? []).map((d) => d.external_uid));
  const add = VLSI_PROGRAM.map((s, i) => ({
    course_id: courseId, kind: "other", done: false,
    title: `🎓 VLSI שבוע ${s.week} · מפגש ${s.n}: ${s.title}`,
    due_at: israelLocalToIso(`${dates[i]}T${s.n === 1 ? SELF_SLOTS[0].end : SELF_SLOTS[1].end}`),
    notes: "מתוכנית ה-VLSI (12 שבועות). מסמנים בדף לימוד VLSI.",
    external_uid: `vlsi:${sessionKey(s)}`,
  })).filter((r) => !known.has(r.external_uid));
  if (add.length) await sb.from("deadlines").upsert(add, { onConflict: "user_id,external_uid", ignoreDuplicates: true });
}
