import { isSiteLesson } from "./week";
import type { SupabaseClient } from "@supabase/supabase-js";
import { topicStats, isWeak, type TopicStat } from "./progress";
import { classMeetings } from "./recordings";
import type { Course, Deadline, Lesson } from "./types";

export type Reminder = { text: string; href: string };
export type CoursePlan = {
  course: Course;
  score: number;
  level: "high" | "medium" | "low";
  reasons: string[];
  reminders: Reminder[];
  classLessons: number;      // class meetings so far (lectures + practices, or lab experiments)
  lectures: number;          // lectures held so far: by the timetable, or uploaded if more
  practices: number;
  missingUploads: number;
  read: number;
  ready: number;
  mastery: number | null;     // % of the course's questions answered correctly (latest answer)
  covered: Set<number>;       // syllabus topic numbers taught in class
  readCovered: Set<number>;   // ...of those, ones whose lesson the student read
};

const DAY = 864e5;

/**
 * Where each course stands and how much it needs this week: unread chapters, recordings not uploaded
 * yet, tasks and exams coming up, weak topics, missing course files.
 */
export async function weeklyPlan(sb: SupabaseClient): Promise<CoursePlan[]> {
  const [{ data: courses }, { data: lessons }, { data: deadlines }, meetings, { data: materials }, stats, { data: titles }] =
    await Promise.all([
      sb.from("courses").select("*").eq("archived", false),
      lessonsWithCoverage(sb),
      sb.from("deadlines").select("*").eq("done", false).gte("due_at", new Date(Date.now() - DAY).toISOString()),
      classMeetings(sb).catch(() => ({ held: [], missing: [] })),
      sb.from("materials").select("course_id, kind, title"),
      topicStats(sb),
      sb.from("deadlines").select("course_id, title"),
    ]);
  const now = new Date();

  return ((courses ?? []) as Course[]).map((course) => {
    const ls = ((lessons ?? []) as (Lesson & { syllabus_covered?: number[] })[]).filter((l) => l.course_id === course.id);
    const ds = ((deadlines ?? []) as Deadline[]).filter((d) => d.course_id === course.id);
    const cs: TopicStat[] = stats.filter((s) => s.course_id === course.id);
    const mats = (materials ?? []).filter((m) => m.course_id === course.id);
    const reasons: string[] = [];
    const reminders: Reminder[] = [];
    let score = 0;

    const ready = ls.filter((l) => l.status === "ready");
    const unread = ready.filter((l) => !l.read_at && !isSiteLesson(l));
    if (unread.length) {
      score += unread.length * 3;
      reasons.push(`${unread.length} פרקים שעוד לא קראת`);
    }

    // Recordings since the semester started not uploaded yet (the home page lists them with actions).
    const missingUploads = meetings.missing.filter((m) => m.slot.course_id === course.id).length;
    if (missingUploads) {
      score += missingUploads * 2;
      reasons.push(`${missingUploads} הקלטות שעוד לא העלית`);
    }

    const exam = ds.filter((d) => d.kind === "exam").sort((a, b) => a.due_at.localeCompare(b.due_at))[0];
    if (exam) {
      const days = (new Date(exam.due_at).getTime() - now.getTime()) / DAY;
      if (days < 30) {
        score += Math.round(30 - days);
        reasons.push(`מבחן בעוד ${Math.max(0, Math.floor(days))} ימים`);
      }
    }
    // Tasks with no submission date published yet: keep asking to check the course site.
    for (const d of ds.filter((x) => x.check_due)) {
      reminders.push({ text: `לבדוק מתי מגישים את "${d.title}" ב${course.name} (עוד אין מועד הגשה)`, href: `/deadlines/${d.id}` });
    }
    for (const d of ds.filter((x) => x.kind !== "exam" && !x.check_due)) {
      const days = (new Date(d.due_at).getTime() - now.getTime()) / DAY;
      if (days > 7) continue;
      score += days < 3 ? 10 : 5;
      reasons.push(`${d.title} להגשה בעוד ${Math.max(0, Math.floor(days))} ימים`);
      // Reminders are about submissions and exams, not about reading (he sees that in "על מה להשקיע").
      reminders.push({ text: `${d.kind === "exam" ? "להתכונן ל" : "להגיש את "}"${d.title}" ב${course.name} - בעוד ${Math.max(0, Math.floor(days))} ימים`, href: `/deadlines/${d.id}` });
    }

    const weak = cs.filter(isWeak).length;
    if (weak) {
      score += weak * 2;
      reasons.push(`${weak} נושאים לחיזוק`);
    }

    // Assignment files without a deadline: "מטלה 3.pdf" uploaded but no task "מטלה 3" with a due date.
    const allDeadlines = (titles ?? []).filter((d) => d.course_id === course.id);
    for (const m of mats) {
      const hit = m.title?.match(/(מטלה|תרגיל בית|עבודת בית|assignment|homework|hw)\s*(\d+)?/i);
      if (!hit) continue;
      const label = `${hit[1]}${hit[2] ? ` ${hit[2]}` : ""}`;
      if (!allDeadlines.some((d) => d.title.includes(label))) {
        reminders.push({ text: `לבדוק מתי מגישים את "${label}" ב${course.name} ולהוסיף משימה (הקובץ הועלה, אין מועד)`, href: `/deadlines?course=${course.id}` });
      }
    }

    if (course.kind !== "self" && !mats.some((m) => m.kind === "syllabus")) {
      reminders.push({ text: `להעלות את הסילבוס של ${course.name}`, href: `/courses/${course.id}` });
    }
    if (course.exam_type && course.exam_type !== "none" && !mats.some((m) => m.kind === "past_exam")) {
      reminders.push({ text: `להעלות מבחני עבר ב${course.name}`, href: `/courses/${course.id}` });
    }

    // Meetings held per the timetable; uploaded lessons win when there are more (e.g. no timetable entered).
    const held = (kind: string) => Math.max(
      meetings.held.filter((m) => m.slot.course_id === course.id && m.slot.kind === kind).length,
      // Two Zoom parts of one lecture share its number: count meetings, not uploads.
      new Set(ls.filter((l) => l.kind === kind).map((l) => l.number ?? l.id)).size);
    const lectures = held("lecture");
    const practices = held("practice");
    const total = cs.reduce((a, s) => a + s.total, 0);
    const correct = cs.reduce((a, s) => a + s.correct, 0);
    const covered = new Set(ls.flatMap((l) => l.syllabus_covered ?? []));
    const readCovered = new Set(ls.filter((l) => l.read_at).flatMap((l) => l.syllabus_covered ?? []));
    return {
      course, score, reasons, reminders, missingUploads,
      level: score >= 15 ? "high" : score >= 6 ? "medium" : "low",
      classLessons: course.kind === "lab" ? ls.filter((l) => l.kind === "lab").length : lectures + practices,
      lectures, practices,
      read: ls.filter((l) => l.read_at).length,
      ready: ready.length,
      mastery: total ? Math.round((100 * correct) / total) : null,
      covered, readCovered,
    } satisfies CoursePlan;
  }).sort((a, b) => b.score - a.score);
}

/** Lessons with their syllabus coverage; works before the syllabus_covered column exists too. */
async function lessonsWithCoverage(sb: SupabaseClient) {
  const cols = "id, course_id, kind, number, title, status, read_at, created_at, source_url";
  const res = await sb.from("lessons").select(`${cols}, syllabus_covered`);
  return res.error ? sb.from("lessons").select(cols) : res;
}

export const LEVEL_LABEL = { high: "להשקיע השבוע", medium: "לשים לב", low: "במצב טוב" } as const;
export const LEVEL_TONE = { high: "text-bad bg-bad-soft", medium: "text-warn bg-warn-soft", low: "text-good bg-good-soft" } as const;
