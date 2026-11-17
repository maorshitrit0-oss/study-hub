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

/** A question about understanding, not calculation: no math markup and no number-crunching in it or its options. */
export function conceptual(q: { question: string; options: string[] }) {
  return ![q.question, ...q.options].some((t) => /\$|\\\(|\\\[|\d+\s*[=×*/^]\s*\d/.test(t));
}

/**
 * Weekly review (his request 17/11/2026, replaces the daily one): every Saturday night, understanding questions only
 * (no formulas) from the lessons he marked read in the last 7 days - only those. Lessons in reading order; inside a
 * lesson, questions he got wrong or never answered come first. At most 30, shared fairly between the lessons.
 */
export async function weeklyReview(sb: SupabaseClient, max = 30) {
  const since = new Date(Date.now() - 7 * DAY).toISOString();
  const { data: lessons } = await sb.from("lessons").select("id, course_id, kind, number, title, read_at")
    .gte("read_at", since).order("read_at");
  const ls = lessons ?? [];
  if (!ls.length) return { lessons: ls, questions: [] as Question[], total: 0 };
  const { data } = await sb.from("questions").select("id, course_id, lesson_id, topic, question, options, correct, explanation, difficulty, source")
    .in("lesson_id", ls.map((l) => l.id));
  const qs = ((data ?? []) as (Question & { source?: string | null })[]).filter((q) => !q.source && conceptual(q));
  const { data: tries } = await sb.from("attempts").select("question_id, is_correct, created_at").in("question_id", qs.map((q) => q.id)).order("created_at");
  const last = new Map<string, boolean>();
  for (const t of tries ?? []) last.set(t.question_id, t.is_correct);
  const rank = (q: Question) => (last.get(q.id) === false ? 0 : last.has(q.id) ? 2 : 1); // wrong, new, right
  const per = ls.map((l) => qs.filter((q) => q.lesson_id === l.id).sort((a, b) => rank(a) - rank(b)));
  const out: Question[] = [];
  for (let i = 0; out.length < max && per.some((p) => p.length > i); i++) {
    for (const p of per) if (p[i] && out.length < max) out.push(p[i]);
  }
  // keep each lesson's questions together, in reading order
  const order = new Map(ls.map((l, i) => [l.id, i]));
  out.sort((a, b) => order.get(a.lesson_id!)! - order.get(b.lesson_id!)!);
  return { lessons: ls, questions: out, total: qs.length };
}
