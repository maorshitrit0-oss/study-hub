import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * Class meetings that did not take place (his request 10/11/2026: "tomorrow there is no lecture and no practice - a
 * make-up later"). A cancelled meeting is not counted: lecture N stays lecture N and is simply taught at the next
 * meeting, so numbering, study weeks and the upload reminders all move on by one meeting. Kept in storage
 * (<user>/cancelled_meetings.json = ["<slot_id>|<YYYY-MM-DD>", ...]) - no schema change.
 */
const path = (userId: string) => `${userId}/cancelled_meetings.json`;

export async function loadCancelled(sb: SupabaseClient, userId?: string): Promise<Set<string>> {
  const uid = userId ?? (await sb.auth.getUser()).data.user?.id;
  if (!uid) return new Set();
  const { data } = await sb.storage.from("study").download(path(uid));
  if (!data) return new Set();
  try { return new Set(JSON.parse(await data.text()) as string[]); } catch { return new Set(); }
}

export async function saveCancelled(sb: SupabaseClient, userId: string, keys: Set<string>) {
  await sb.storage.from("study").upload(path(userId), new Blob([JSON.stringify([...keys].sort())], { type: "application/json" }),
    { upsert: true, contentType: "application/json" });
}
