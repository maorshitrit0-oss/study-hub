import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * One name per topic (worker/topics.py): original topic name -> merged name, per course. Missing map or name ->
 * the name as it is. Nothing in the database is renamed.
 */
export async function topicMaps(sb: SupabaseClient, courseIds: string[]) {
  const ids = [...new Set(courseIds)];
  if (!ids.length) return new Map<string, Record<string, string>>();
  const { data: courses } = await sb.from("courses").select("id, user_id").in("id", ids);
  const maps = await Promise.all((courses ?? []).map(async (c) => {
    try {
      const { data } = await sb.storage.from("study").download(`${c.user_id}/materials/${c.id}/topics_merged.json`);
      return [c.id as string, data ? (JSON.parse(await data.text()).map ?? {}) as Record<string, string> : {}] as const;
    } catch {
      return [c.id as string, {}] as const;
    }
  }));
  return new Map(maps);
}

export const mergedTopic = (maps: Map<string, Record<string, string>>, courseId: string, topic: string | null) =>
  (topic && maps.get(courseId)?.[topic.trim()]) || topic || "כללי";
