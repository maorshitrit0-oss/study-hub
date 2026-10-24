import { fetchAll } from "./fetchAll";
import type { SupabaseClient } from "@supabase/supabase-js";

export type TopicStat = { topic: string; answered: number; correct: number; total: number };

/**
 * Mastery per topic: for each question only the latest answer counts,
 * so re-practicing a weak topic actually moves the number.
 */
export async function topicStats(sb: SupabaseClient, courseId?: string) {
  const qs = () => {
    const q = sb.from("questions").select("id, topic, course_id").order("id");
    return courseId ? q.eq("course_id", courseId) : q;
  };
  const at = () => {
    const q = sb.from("attempts").select("question_id, is_correct, created_at").order("created_at").order("id");
    return courseId ? q.eq("course_id", courseId) : q;
  };
  const [questions, attempts] = await Promise.all([
    fetchAll<{ id: string; topic: string | null; course_id: string }>(qs),
    fetchAll<{ question_id: string; is_correct: boolean }>(at),
  ]);
  const latest = new Map<string, boolean>();
  for (const a of attempts ?? []) latest.set(a.question_id, a.is_correct);

  const byTopic = new Map<string, TopicStat & { course_id: string }>();
  for (const q of questions ?? []) {
    const key = `${q.course_id}|${q.topic || "כללי"}`;
    const s = byTopic.get(key) ?? { topic: q.topic || "כללי", answered: 0, correct: 0, total: 0, course_id: q.course_id };
    s.total++;
    if (latest.has(q.id)) {
      s.answered++;
      if (latest.get(q.id)) s.correct++;
    }
    byTopic.set(key, s);
  }
  return [...byTopic.values()];
}

export const pct = (s: { answered: number; correct: number }) =>
  s.answered ? Math.round((100 * s.correct) / s.answered) : null;

export const isWeak = (s: TopicStat) => s.answered >= 2 && (pct(s) ?? 100) < 70;
