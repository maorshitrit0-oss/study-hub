import { createHash } from "node:crypto";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { Fact } from "@/components/CourseFacts";

/** One line of "מידע על הקורס" after merging repeats (worker/facts.py); ids = the original course_facts rows. */
export type MergedFact = { category: string; text: string; ids: string[] };

/** Same as worker/facts.py signature(). */
export const factsSignature = (facts: { id: string }[]) =>
  createHash("sha1").update(facts.map((f) => f.id).sort().join(",")).digest("hex");

/**
 * The course info without repeats: the merged list (worker/facts.py, kept as facts_merged.json), adjusted to the
 * facts that exist now - deleted rows drop out, rows added since the merge show as they are. Nothing is deleted here.
 */
export async function mergedFacts(sb: SupabaseClient, userId: string, courseId: string, facts: Fact[]): Promise<MergedFact[]> {
  const own = (f: Fact): MergedFact => ({ category: f.category, text: f.text, ids: [f.id] });
  let items: MergedFact[] = [];
  try {
    const { data } = await sb.storage.from("study").download(`${userId}/materials/${courseId}/facts_merged.json`);
    if (data) items = (JSON.parse(await data.text()).items ?? []) as MergedFact[];
  } catch { /* not merged yet */ }
  const alive = new Set(facts.map((f) => f.id));
  const merged = items.map((it) => ({ ...it, ids: it.ids.filter((id) => alive.has(id)) })).filter((it) => it.ids.length);
  const covered = new Set(merged.flatMap((it) => it.ids));
  return [...merged, ...facts.filter((f) => !covered.has(f.id)).map(own)];
}

/** Grade components, exam format and formula sheet per course, for the timetable (worker/facts.py "summary"). */
export type CourseSummary = { grade?: string; exam?: string; formula_sheet?: string };

export async function courseSummaries(sb: SupabaseClient, courses: { id: string; user_id: string }[]) {
  const out = await Promise.all(courses.map(async (c) => {
    try {
      const { data } = await sb.storage.from("study").download(`${c.user_id}/materials/${c.id}/facts_merged.json`);
      return [c.id, data ? ((JSON.parse(await data.text()).summary ?? {}) as CourseSummary) : {}] as const;
    } catch {
      return [c.id, {}] as const;
    }
  }));
  return new Map<string, CourseSummary>(out);
}
