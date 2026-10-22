import type { SupabaseClient } from "@supabase/supabase-js";
import { israelNow } from "./format";
import type { Slot } from "./types";

export type Missing = { slot: Slot; date: string };

const DAY_MS = 864e5;
// First day of the current semester (Israel). Update each semester (see docs/HANDOFF.md).
export const SEMESTER_START = process.env.SEMESTER_START || "2026-10-18";

/** YYYY-MM-DD of a date in Israel. */
function israelDate(d: Date) {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);
}

/**
 * Lecture/practice meetings since the semester started that still have no recording.
 * A meeting counts as covered when it was marked ("uploaded" / "no recording"), or when a lesson of the
 * same course and kind was added on or after that day (lessons are matched to meetings in date order).
 */
export async function missingRecordings(sb: SupabaseClient): Promise<Missing[]> {
  const since = new Date(`${SEMESTER_START}T00:00:00+03:00`);
  const days = Math.ceil((Date.now() - since.getTime()) / DAY_MS);
  const [{ data: slots }, { data: marks }, { data: lessons }] = await Promise.all([
    sb.from("schedule_slots").select("*").in("kind", ["lecture", "practice"]).not("course_id", "is", null),
    sb.from("recording_marks").select("slot_id, class_date").gte("class_date", israelDate(since)),
    sb.from("lessons").select("course_id, kind, created_at").gte("created_at", since.toISOString()).order("created_at"),
  ]);
  const now = israelNow();
  const today = israelDate(new Date());
  const marked = new Set((marks ?? []).map((m) => `${m.slot_id}|${m.class_date}`));

  const meetings: Missing[] = [];
  for (const s of (slots ?? []) as (Slot & { created_at: string })[]) {
    for (let k = days; k >= 0; k--) {
      const d = new Date(Date.now() - k * DAY_MS);
      const date = israelDate(d);
      const weekday = new Date(`${date}T12:00:00Z`).getUTCDay();
      if (weekday !== s.weekday || date < SEMESTER_START) continue;
      if (date === today && now.time < s.end_time.slice(0, 5)) continue; // class not over yet
      meetings.push({ slot: s, date });
    }
  }
  meetings.sort((a, b) => a.date.localeCompare(b.date));

  const used = new Set<number>();
  const pending = (lessons ?? []) as { course_id: string; kind: string; created_at: string }[];
  return meetings.filter((m) => {
    if (marked.has(`${m.slot.id}|${m.date}`)) return false;
    const i = pending.findIndex((l, j) => !used.has(j) && l.course_id === m.slot.course_id
      && l.kind === m.slot.kind && israelDate(new Date(l.created_at)) >= m.date);
    if (i >= 0) {
      used.add(i);
      return false;
    }
    return true;
  });
}
