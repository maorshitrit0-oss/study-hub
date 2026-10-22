export type Course = {
  id: string;
  name: string;
  code: string | null;
  kind: "course" | "lab" | "project" | "self";
  year: number | null;
  semester: string | null;
  lecturer: string | null;
  ta: string | null;
  exam_type: "mcq" | "open" | "mixed" | "none" | null;
  grade_weights: { name: string; weight: number }[];
  notes: string | null;
  archived: boolean;
};

export type Lesson = {
  id: string;
  course_id: string;
  kind: "lecture" | "practice" | "lab" | "web" | "other";
  number: number | null;
  title: string | null;
  source_url: string | null;
  status: "queued" | "processing" | "transcribed" | "ready" | "error";
  progress: string | null;
  error: string | null;
  chapter_md: string | null;
  topics: string[];
  slide_count: number;
  author: string | null;
  read_at: string | null;
  created_at: string;
};

export type Question = {
  id: string;
  lesson_id: string | null;
  topic: string | null;
  question: string;
  options: string[];
  correct: number;
  explanation: string | null;
  difficulty: number;
};

export type Deadline = {
  id: string;
  course_id: string | null;
  title: string;
  kind: "assignment" | "exam" | "quiz" | "lab_report" | "other";
  due_at: string;
  done: boolean;
  notes: string | null;
};

export const KIND_LABEL: Record<Course["kind"], string> = {
  course: "קורס", lab: "מעבדה", project: "פרויקט", self: "לימוד עצמי",
};
export const LESSON_LABEL: Record<Lesson["kind"], string> = {
  lecture: "הרצאה", practice: "תרגול", lab: "ניסוי", web: "מאמר מהאינטרנט", other: "חומר",
};
export const EXAM_LABEL: Record<string, string> = {
  mcq: "אמריקאי", open: "פתוח", mixed: "משולב", none: "ללא מבחן",
};
export const DEADLINE_LABEL: Record<Deadline["kind"], string> = {
  assignment: "מטלה", exam: "מבחן", quiz: "בוחן", lab_report: "דוח מעבדה", other: "אחר",
};

export function lessonName(l: Pick<Lesson, "kind" | "number" | "title">) {
  const base = `${LESSON_LABEL[l.kind]}${l.number ? ` ${l.number}` : ""}`;
  return l.title && l.kind === "web" ? l.title : base;
}

export type Slot = {
  id: string;
  course_id: string | null;
  title: string;
  kind: "lecture" | "practice" | "lab" | "other";
  weekday: number;
  start_time: string;
  end_time: string;
  room: string | null;
  instructor: string | null;
};

export const DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"];
export const SLOT_LABEL: Record<Slot["kind"], string> = { lecture: "הרצאה", practice: "תרגול", lab: "מעבדה", other: "אחר" };
export const hhmm = (t: string) => t.slice(0, 5);
