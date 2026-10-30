import type { SupabaseClient } from "@supabase/supabase-js";
import { fetchAll } from "./fetchAll";
import { classMeetings } from "./recordings";
import { semesterWeek } from "./week";
import type { Exercise } from "@/components/Exercises";

export type ExerciseRow = Exercise & { course_id: string; lesson_id: string | null; material_id: string | null; ord: number };

const israelDate = (d: Date) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(d);

/**
 * Exercises by semester week, per course: a lesson's exercises belong to the week of the class it recorded (or the
 * week it was uploaded); a homework / past-exam exercise belongs to every week whose lessons cover its topic.
 */
export async function exercisesByWeek(sb: SupabaseClient, courseId?: string) {
  const [{ held }, rows, { data: lessons }, { data: materials }] = await Promise.all([
    classMeetings(sb),
    fetchAll<ExerciseRow>(() => {
      const q = sb.from("exercises").select("*").order("created_at").order("ord");
      return courseId ? q.eq("course_id", courseId) : q;
    }).catch(() => [] as ExerciseRow[]),
    (courseId ? sb.from("lessons").select("id, course_id, kind, number, topics, created_at").eq("course_id", courseId)
      : sb.from("lessons").select("id, course_id, kind, number, topics, created_at")),
    (courseId ? sb.from("materials").select("id, title").eq("course_id", courseId) : sb.from("materials").select("id, title")),
  ]);
  const lessonWeek = new Map<string, number>();
  for (const m of held) if (m.lesson) lessonWeek.set(m.lesson.id, semesterWeek(m.date));
  for (const l of lessons ?? []) if (!lessonWeek.has(l.id)) lessonWeek.set(l.id, semesterWeek(israelDate(new Date(l.created_at))));
  const topicsOf = new Map<string, Set<string>>(); // `${course}|${week}` -> topics taught that week
  for (const l of lessons ?? []) {
    const k = `${l.course_id}|${lessonWeek.get(l.id)}`;
    const set = topicsOf.get(k) ?? new Set<string>();
    for (const t of (l.topics ?? []) as string[]) set.add(t);
    topicsOf.set(k, set);
  }
  const fileName = new Map((materials ?? []).map((m) => [m.id, m.title as string]));
  const labeled = rows.map((x) => ({ ...x, label: x.material_id ? fileName.get(x.material_id) ?? undefined : undefined }));

  /** The exercises of semester week w in a course: from its lessons, then files on the topics it taught. */
  function forWeek(course: string, w: number) {
    const fromLessons = labeled.filter((x) => x.course_id === course && x.lesson_id && lessonWeek.get(x.lesson_id) === w);
    const topics = topicsOf.get(`${course}|${w}`) ?? new Set<string>();
    const fromFiles = labeled.filter((x) => x.course_id === course && !x.lesson_id && x.topic && topics.has(x.topic));
    return { fromLessons, fromFiles };
  }
  const fileExercises = (course: string) => labeled.filter((x) => x.course_id === course && !x.lesson_id);
  return { forWeek, fileExercises, all: labeled };
}

/**
 * One task per course for his study week: "✍️ לפתור: <course> שבוע N - k תרגילים" (closes when all are marked solved).
 * Runs when home or the task list loads, like the other synced tasks.
 */
export async function syncExerciseTasks(sb: SupabaseClient) {
  const { studyWeek, STUDY_LAG, weekDays } = await import("./week");
  const { israelLocalToIso } = await import("./format");
  const w = studyWeek();
  const [{ forWeek }, { data: courses }, { data: tasks }] = await Promise.all([
    exercisesByWeek(sb),
    sb.from("courses").select("id, name").eq("archived", false).neq("kind", "self"),
    sb.from("deadlines").select("id, external_uid, done, title").like("external_uid", "ex:%"),
  ]);
  const have = new Map((tasks ?? []).map((t) => [t.external_uid as string, t]));
  const add = [];
  for (const c of courses ?? []) {
    const { fromLessons, fromFiles } = forWeek(c.id, w);
    const list = [...fromLessons, ...fromFiles];
    if (!list.length) continue;
    const left = list.filter((x) => !x.done_at).length;
    const uid = `ex:${c.id}:${w}`;
    const title = `✍️ לפתור: ${c.name} שבוע ${w} - ${list.length} תרגילים`;
    const t = have.get(uid);
    if (t) {
      if ((!left) !== t.done || t.title !== title) await sb.from("deadlines").update({ done: !left, title }).eq("id", t.id);
      continue;
    }
    add.push({
      course_id: c.id, kind: "other", title, done: !left,
      due_at: israelLocalToIso(`${weekDays(w + STUDY_LAG).end}T20:00`),
      notes: `נוצר אוטומטית. התרגילים: /courses/${c.id}/exercises?w=${w} - נסגר לבד כשמסמנים את כולם כפתורים.`,
      external_uid: uid,
    });
  }
  if (add.length) await sb.from("deadlines").upsert(add, { onConflict: "user_id,external_uid", ignoreDuplicates: true });
}
