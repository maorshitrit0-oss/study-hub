import type { SupabaseClient } from "@supabase/supabase-js";

export type Media = {
  id: string; kind: "podcast" | "video" | "examples"; title: string | null; status: "queued" | "processing" | "ready" | "error";
  progress: string | null; error: string | null; script: string | null; duration_sec: number | null;
  lesson_ids: string[]; created_at: string; url?: string;
};

/** Studio items of a lesson (or of a whole course), newest first, with playable links. */
export async function loadMedia(sb: SupabaseClient, filter: { lessonId?: string; courseId?: string }) {
  let q = sb.from("lesson_media").select("*").order("created_at", { ascending: false }).limit(30);
  if (filter.lessonId) q = q.contains("lesson_ids", [filter.lessonId]);
  if (filter.courseId) q = q.eq("course_id", filter.courseId);
  const { data, error } = await q;
  if (error) return null; // studio.sql not run yet
  const rows = (data ?? []) as (Media & { storage_path: string | null })[];
  const paths = rows.filter((r) => r.storage_path).map((r) => r.storage_path!);
  if (paths.length) {
    const { data: signed } = await sb.storage.from("study").createSignedUrls(paths, 6 * 3600);
    const byPath = new Map((signed ?? []).map((s) => [s.path, s.signedUrl]));
    for (const r of rows) if (r.storage_path) r.url = byPath.get(r.storage_path) ?? undefined;
  }
  return rows.map(({ storage_path: _, ...r }) => (void _, r)) as Media[];
}
