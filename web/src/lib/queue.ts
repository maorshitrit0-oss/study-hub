import type { SupabaseClient } from "@supabase/supabase-js";
import { dispatchLesson, dispatchQueue } from "./github";

/** At most this many lessons are written at the same time; the rest wait in line (worker/queue.py). */
export const PARALLEL = 2;
/** Progress line of a lesson waiting in line; "פרק מלא" in it means the full chapter was asked for. */
export const WAITING = "⏳ בתור";

/**
 * Starts writing a lesson now, or puts it in line when two are already being written (05/11/2026: he opened ~20
 * lessons at once, they all ran together and the free Gemini quota ran out - 90% failed). The half-hourly worker
 * (worker/queue.py) takes waiting lessons one by one, and stops for the day when the quota is used up.
 */
export async function startLesson(sb: SupabaseClient, id: string, author: "gemini" | "none" = "gemini", mode: "auto" | "full" = "auto") {
  if (author === "gemini") {
    const since = new Date(Date.now() - 2 * 3600_000).toISOString();
    const { count } = await sb.from("lessons").select("id", { count: "exact", head: true })
      .eq("status", "processing").gt("updated_at", since).neq("id", id);
    if ((count ?? 0) >= PARALLEL) {
      await sb.from("lessons").update({
        status: "queued", error: null,
        progress: `${WAITING}${mode === "full" ? " (פרק מלא)" : ""} - יתחיל לבד, אחד-אחד, כדי לא לגמור את המכסה של Gemini`,
      }).eq("id", id);
      await dispatchQueue(); // works the line now (one job at a time), not on GitHub's slow schedule
      return null;
    }
  }
  return dispatchLesson(id, author, mode);
}
