import type { SupabaseClient } from "@supabase/supabase-js";
import type { Question as Base } from "./types";

type Question = Base & { course_id: string };

// Spaced repetition (Leitner): the more times in a row a question was answered correctly, the longer until it
// comes back. A wrong answer brings it back the next day. Built only from the attempts already recorded.
const INTERVAL_DAYS = [1, 3, 7, 14, 30, 60]; // index = correct answers in a row (0 = last answer was wrong)
const DAY = 864e5;

type Attempt = { question_id: string; is_correct: boolean; created_at: string };

async function allAttempts(sb: SupabaseClient) {
  const rows: Attempt[] = [];
  for (let from = 0; ; from += 1000) { // PostgREST returns at most 1000 rows per request
    const { data } = await sb.from("attempts").select("question_id, is_correct, created_at").order("created_at").range(from, from + 999);
    rows.push(...((data ?? []) as Attempt[]));
    if (!data || data.length < 1000) return rows;
  }
}

/** Questions whose review date has come, most overdue first. */
export async function dueReviews(sb: SupabaseClient, courseId?: string) {
  const attempts = await allAttempts(sb);
  const state = new Map<string, { streak: number; last: number }>();
  for (const a of attempts) {
    const s = state.get(a.question_id) ?? { streak: 0, last: 0 };
    state.set(a.question_id, { streak: a.is_correct ? s.streak + 1 : 0, last: new Date(a.created_at).getTime() });
  }
  const now = Date.now();
  const due = [...state].map(([id, s]) => ({ id, at: s.last + INTERVAL_DAYS[Math.min(s.streak, INTERVAL_DAYS.length - 1)] * DAY }))
    .filter((x) => x.at <= now).sort((a, b) => a.at - b.at);
  if (!due.length) return { total: 0, questions: [] as Question[] };

  const { data: courses } = await sb.from("courses").select("id").eq("archived", false);
  const active = new Set((courses ?? []).map((c) => c.id));
  const ids = due.map((d) => d.id);
  const questions: Question[] = [];
  for (let i = 0; i < ids.length; i += 200) {
    const { data } = await sb.from("questions").select("id, course_id, lesson_id, topic, question, options, correct, explanation, difficulty").in("id", ids.slice(i, i + 200));
    questions.push(...((data ?? []) as Question[]));
  }
  const order = new Map(ids.map((id, i) => [id, i]));
  const list = questions.filter((q) => active.has(q.course_id) && (!courseId || q.course_id === courseId))
    .sort((a, b) => order.get(a.id)! - order.get(b.id)!);
  return { total: list.length, questions: list };
}
