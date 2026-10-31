import type { SupabaseClient } from "@supabase/supabase-js";
import { fetchAll } from "./fetchAll";
import { classMeetings } from "./recordings";
import { semesterWeek } from "./week";
import type { Exercise } from "@/components/Exercises";

export type ExerciseRow = Exercise & {
  course_id: string; lesson_id: string | null; material_id: string | null; ord: number;
  fits_lesson_id?: string | null; duplicate?: boolean; // supabase/exercises_assign.sql
};

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
  const fileName = new Map((materials ?? []).map((m) => [m.id, m.title as string]));
  const KIND: Record<string, string> = { lecture: "הרצאה", practice: "תרגול" };
  const lessonName = new Map((lessons ?? []).map((l) => [l.id, `${KIND[l.kind] ?? "שיעור"}${l.number ? ` ${l.number}` : ""}`]));
  // Where each exercise comes from, shown on it: the lesson, or the file (homework / past exam / exercise booklet).
  const labeled = rows.map((x) => ({
    ...x,
    label: x.material_id ? `📄 ${fileName.get(x.material_id) ?? "קובץ"}` : x.lesson_id ? `🎓 ${lessonName.get(x.lesson_id) ?? "שיעור"}` : undefined,
  }));

  /**
   * The exercises of semester week w in a course: from its lessons, then file exercises placed in one of its lessons
   * (worker/exercises.py assign: the earliest lesson after which the whole exercise can be solved). Each exercise is
   * in exactly one week; one not placed yet (material not taught) or a duplicate of a class exercise is in no week.
   */
  function forWeek(course: string, w: number) {
    const fromLessons = labeled.filter((x) => x.course_id === course && x.lesson_id && lessonWeek.get(x.lesson_id) === w);
    const fromFiles = labeled.filter((x) => x.course_id === course && !x.lesson_id && !x.duplicate && x.fits_lesson_id
      && lessonWeek.get(x.fits_lesson_id) === w).sort((a, b) => Number(b.exam_style) - Number(a.exam_style));
    return { fromLessons, fromFiles };
  }
  const fileExercises = (course: string) => labeled.filter((x) => x.course_id === course && !x.lesson_id);
  /** The week after which a file (e.g. "מטלה 3") can be solved: the last week that taught one of its topics. */
  function fileReadyWeek(course: string, materialId: string) {
    const mine = labeled.filter((x) => x.course_id === course && x.material_id === materialId && !x.duplicate);
    if (!mine.length || mine.some((x) => !x.fits_lesson_id)) return null; // part of it not taught yet
    return Math.max(...mine.map((x) => lessonWeek.get(x.fits_lesson_id!) ?? 0)) || null;
  }
  return { forWeek, fileExercises, fileReadyWeek, all: labeled };
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
