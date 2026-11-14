import type { SupabaseClient } from "@supabase/supabase-js";
import { israelLocalToIso } from "./format";
import { FREEZES } from "./skills";
import { SELF_SLOTS } from "./selfPlan";

const WEEK_MS = 7 * 24 * 3600 * 1000;
const DAY_MS = 864e5;
// Real outside deadlines keep their date (an exam, a submission, the lab report / entry quiz): only study tasks move.
// Self-study sessions ("vlsi:") are scheduled by resumeSelfStudy below, not week by week.
const FIXED_UID = /^(labrep:|labq:|vlsi:)/;

const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);

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
  await resumeSelfStudy(sb).catch(() => {});
}

/**
 * Self-study goes on from where he stopped (his request 13-14/11/2026): the first unfinished session is on the next
 * self-study slot from tomorrow on, and every later session follows it slot by slot (Friday, Saturday night, ...),
 * skipping the exam freeze. Only sessions whose date passed move the chain; a plan that is on time stays as it is.
 */
export async function resumeSelfStudy(sb: SupabaseClient) {
  const { data } = await sb.from("deadlines").select("id, due_at, external_uid").eq("done", false).like("external_uid", "vlsi:%");
  const open = (data ?? []).map((d) => {
    const [w, n] = (d.external_uid as string).slice(5).split("-").map(Number);
    return { ...d, order: w * 10 + n };
  }).sort((a, b) => a.order - b.order);
  // on time (the first open session's slot has not ended yet): nothing to move
  if (!open.length || Date.parse(open[0].due_at) > Date.now()) return;
  // the coming slots, from tomorrow (today he already stopped)
  const slots: string[] = [];
  for (let k = 1; slots.length < open.length && k < 400; k++) {
    const date = israelDate(new Date(Date.now() + k * DAY_MS));
    if (FREEZES.some((f) => date >= f.from && date <= f.to)) continue;
    const weekday = new Date(`${date}T12:00:00Z`).getUTCDay();
    const slot = SELF_SLOTS.find((s) => s.weekday === weekday);
    if (slot) slots.push(israelLocalToIso(`${date}T${slot.end}`));
  }
  for (let i = 0; i < open.length && i < slots.length; i++) {
    if (open[i].due_at !== slots[i]) await sb.from("deadlines").update({ due_at: slots[i] }).eq("id", open[i].id);
  }
}
