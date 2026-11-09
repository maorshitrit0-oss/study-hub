import type { SupabaseClient } from "@supabase/supabase-js";
import { fetchAll } from "./fetchAll";
import { isSiteLesson } from "./week";
import { lessonName, isSession, type Lesson, type Question } from "./types";

/**
 * 🔥 The warm-up before a lesson (his request 09/11/2026): questions on EVERY lesson taught before it in the course
 * (lecture 1 part A, part B, practice 1, lecture 2 ...), at least one from each, about 10 in all and more when there are
 * more earlier lessons; the extra ones from the most recent lessons; questions he got wrong first.
 */
export const WARMUP_SIZE = 10;
const HEB_PART: Record<string, number> = { "א": 1, "ב": 2, "ג": 3, "ד": 4 };

export function partOf(l: Pick<Lesson, "title">) {
  const m = (l.title ?? "").match(/חלק\s*['׳]?\s*(\d+|[אבגד](?![א-ת]))/);
  return m ? Number(m[1]) || HEB_PART[m[1]] || 0 : 0;
}

/** The order he studies them: lecture N (part 1, part 2 ...), then practice N; sessions by their number. */
export function byMeeting(a: Lesson, b: Lesson) {
  return Number(isSession(a)) - Number(isSession(b))
    || (a.number ?? 999) - (b.number ?? 999)
    || (a.kind === b.kind ? 0 : a.kind === "lecture" ? -1 : 1)
    || partOf(a) - partOf(b)
    || a.created_at.localeCompare(b.created_at);
}

type L = Lesson & { summary_md?: string | null };
export type WarmLesson = { id: string; label: string; hasSummary: boolean };

/** The lessons that come before `lessonId` in the course (taught ones: lectures, practices, web lessons, or sessions). */
export function before(all: L[], lessonId: string) {
  const ls = all.filter((l) => l.status === "ready" && !isSiteLesson(l) && ["lecture", "practice", "web", "other"].includes(l.kind));
  const me = all.find((l) => l.id === lessonId);
  if (!me) return [];
  const same = ls.filter((l) => isSession(l) === isSession(me)).sort(byMeeting);
  return same.filter((l) => l.id !== lessonId && byMeeting(l, me) < 0);
}

export async function warmupFor(sb: SupabaseClient, courseId: string, lessonId: string) {
  const [{ data: lessons }, questions, attempts] = await Promise.all([
    sb.from("lessons").select("id, kind, number, title, status, created_at, source_url, transcript, chapter_md, summary_md, read_at").eq("course_id", courseId),
    fetchAll<Question & { source?: string | null }>(() => sb.from("questions").select("*").eq("course_id", courseId).order("id")),
    fetchAll<{ question_id: string; is_correct: boolean }>(() => sb.from("attempts").select("question_id, is_correct").eq("course_id", courseId).order("created_at").order("id")),
  ]);
  const withQ = new Set(questions.filter((q) => !q.source).map((q) => q.lesson_id));
  const prev = before((lessons ?? []) as unknown as L[], lessonId).filter((l) => withQ.has(l.id));
  const set = pick(prev, questions.filter((q) => !q.source), attempts);
  const info: WarmLesson[] = prev.filter((l) => set.some((q) => q.lesson_id === l.id)).map((l) => ({
    id: l.id,
    label: `${lessonName(l)}${l.title && l.kind !== "web" && !isSession(l) ? ` · ${l.title}` : ""}`,
    hasSummary: !!l.summary_md && l.summary_md !== l.chapter_md,
  }));
  return { questions: set, lessons: info };
}

/** One question from each earlier lesson, then more from the newest ones up to WARMUP_SIZE; wrong-last-time first. */
function pick(prev: L[], questions: Question[], attempts: { question_id: string; is_correct: boolean }[]) {
  const last = new Map<string, boolean>();
  for (const a of attempts) last.set(a.question_id, a.is_correct);
  const rank = (q: Question) => (last.get(q.id) === false ? 0 : !last.has(q.id) ? 1 : 2) + Math.random() * 0.9;
  const pools = prev.map((l) => questions.filter((q) => q.lesson_id === l.id).map((q) => ({ q, r: rank(q) }))
    .sort((a, b) => a.r - b.r).map((x) => x.q));
  const taken = pools.map(() => 1); // one from each lesson
  let total = pools.length;
  for (let round = 0; total < WARMUP_SIZE && round < 10; round++) {
    let added = false;
    for (let i = pools.length - 1; i >= 0 && total < WARMUP_SIZE; i--) { // newest lessons first
      if (taken[i] < pools[i].length && taken[i] < 2 + round) { taken[i]++; total++; added = true; }
    }
    if (!added) break;
  }
  return pools.flatMap((p, i) => p.slice(0, taken[i]));
}

/** The lesson to warm up for now: the first lesson (in order) he has not marked read, else the last one. */
export function nextLesson(all: L[]) {
  const ls = all.filter((l) => l.status === "ready" && !isSiteLesson(l) && !isSession(l)
    && ["lecture", "practice", "web"].includes(l.kind)).sort(byMeeting);
  return ls.find((l) => !l.read_at) ?? ls.at(-1) ?? null;
}
