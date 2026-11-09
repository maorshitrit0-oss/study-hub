import type { SupabaseClient } from "@supabase/supabase-js";

const WEEK_MS = 7 * 24 * 3600 * 1000;
// Real outside deadlines keep their date (an exam, a submission, the lab report / entry quiz): only study tasks move.
const FIXED_UID = /^(labrep:|labq:)/;

/**
 * An open study task whose date passed moves to the same time next week (his request 09/11/2026: "push it to next
 * week's deadline instead of leaving it and writing that it passed"). Repeats by whole weeks until it is in the future.
 */
export async function rollOverdueTasks(sb: SupabaseClient) {
  const now = Date.now();
  const { data } = await sb.from("deadlines").select("id, due_at, external_uid, kind").eq("done", false).eq("kind", "other")
    .lt("due_at", new Date(now).toISOString());
  for (const d of data ?? []) {
    if (FIXED_UID.test(d.external_uid ?? "")) continue;
    let t = Date.parse(d.due_at);
    while (t <= now) t += WEEK_MS;
    await sb.from("deadlines").update({ due_at: new Date(t).toISOString() }).eq("id", d.id);
  }
}
