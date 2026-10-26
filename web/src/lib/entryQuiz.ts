import type { Part } from "@google/genai";
import type { SupabaseClient } from "@supabase/supabase-js";
import { generateJson } from "./gemini";
import { geminiFilePart, materialBlob } from "./files";

/** Lab entry quizzes: 3 multiple-choice questions at the start of every experiment, on the prelab report and its
 * Multisim simulations. Students before him (Sunday/Monday groups) report what they were asked. */
export const ENTRY_TOPIC = (n: number) => `בוחן כניסה - ניסוי ${n}`;
export const ENTRY_FILE = /בוחן|כניסה|quiz/i;

type Q = { question: string; options: string[]; correct: number; explanation: string; uncertain: boolean };
type Out = { reported: Q[]; practice: Q[] };
type FileOut = { items: (Q & { experiment: number })[] };

const QUESTION = {
  type: "object",
  properties: {
    question: { type: "string" },
    options: { type: "array", items: { type: "string" } },
    correct: { type: "integer" },
    explanation: { type: "string" },
    uncertain: { type: "boolean" },
  },
  required: ["question", "options", "correct", "explanation", "uncertain"],
};

const RULES = `כללים לכל שאלה:
- שאלה אמריקאית בעברית עם 4 תשובות (options), correct = האינדקס (מ-0) של התשובה הנכונה.
- פתור כל שאלה בעצמך מאפס לפי חומר הניסוי (חוברת, דוח מכין, סימולציות Multisim). התשובה חייבת להיות נכונה.
- explanation: הסבר מלא שלב אחרי שלב למה זו התשובה, עם החישוב/הנוסחה, ולמה המסיחים שגויים. בסוף: איפה זה בדוח המכין.
- אם אינך בטוח בתשובה (חסר מידע, השאלה כפי שדווחה עמומה) - uncertain=true, וכתוב בהסבר מה לא ברור.
- נוסחאות ב-LaTeX בין $...$.`;

const REPORT_PROMPT = (n: number) => `סטודנטים שעשו את ניסוי ${n} במעבדה לפני הסטודנט סיפרו מה נשאלו בבוחן הכניסה (3 שאלות אמריקאיות,
על הדוח המכין ועל הסימולציות ב-Multisim). הדיווח שלהם מצורף (טקסט ו/או צילומים) - לפעמים חלקי, בעל-פה, בלי תשובות.
1. reported: כל שאלה שדווחה, משוחזרת כשאלה אמריקאית מלאה. אם דווחו תשובות - השתמש בהן; אחרת בנה מסיחים סבירים.
2. practice: 6-8 שאלות דומות (אותם נושאים, ניסוחים ומספרים אחרים) - כדי שהוא יבין ולא רק ישנן.
${RULES}`;

const FILE_PROMPT = `הקובץ המצורף מכיל שאלות מבחני כניסה (בוחן כניסה) של מעבדה, לפי ניסויים.
הוצא כל שאלה (items), עם experiment = מספר הניסוי / הבוחן שהיא שייכת אליו (בוחן כניסה 1 = ניסוי 1).
אם יש בקובץ תשובה מסומנת - השתמש בה, אבל בדוק אותה; אם היא שגויה, תקן וכתוב זאת בהסבר.
${RULES}`;

/** The experiment's chapter and booklet, so answers follow this lab's own prelab. */
async function experimentParts(sb: SupabaseClient, courseId: string, n: number): Promise<{ parts: Part[]; lessonId: string | null }> {
  const { data: lesson } = await sb.from("lessons").select("id, chapter_md, source_path").eq("course_id", courseId)
    .eq("kind", "lab").eq("number", n).order("created_at").limit(1).maybeSingle();
  const parts: Part[] = [];
  if (lesson?.chapter_md) parts.push({ text: `=== פרק הקריאה של ניסוי ${n} ===\n${lesson.chapter_md.slice(0, 80_000)}` });
  if (lesson?.source_path) {
    try {
      const blob = await materialBlob(sb, { storage_path: lesson.source_path, mime: null });
      parts.push({ text: `=== חוברת / דוח מכין של ניסוי ${n} ===` }, await geminiFilePart(lesson.source_path, blob, blob.type || "application/pdf"));
    } catch { /* the chapter is enough */ }
  }
  if (!parts.length) parts.push({ text: `(אין עדיין באפליקציה חומר של ניסוי ${n} - ענה לפי ידע הנדסי, וסמן uncertain כשצריך את החוברת.)` });
  return { parts, lessonId: lesson?.id ?? null };
}

function rows(courseId: string, lessonId: string | null, n: number, qs: Q[], source: string) {
  return qs.filter((q) => q.question?.trim() && q.options?.length >= 2 && q.correct >= 0 && q.correct < q.options.length)
    .map((q) => ({
      course_id: courseId, lesson_id: lessonId, experiment: n, source, topic: ENTRY_TOPIC(n),
      question: q.question.trim(), options: q.options, correct: q.correct,
      explanation: (q.uncertain ? "⚠️ **לא בטוח** - לבדוק מול הדוח המכין או לשאול בקבוצה.\n\n" : "") + (q.explanation ?? ""),
      difficulty: 2,
    }));
}

/** One classmates' report -> the questions they were asked + similar practice questions. */
export async function processReport(sb: SupabaseClient, reportId: string) {
  const { data: r } = await sb.from("entry_reports").select("*").eq("id", reportId).single();
  if (!r) throw new Error("הדיווח לא נמצא");
  try {
    const n = r.experiment as number;
    const { parts, lessonId } = await experimentParts(sb, r.course_id, n);
    const report: Part[] = [{ text: `=== הדיווח של הסטודנטים ===\n${r.text ?? "(ראה צילומים)"}` }];
    for (const path of (r.image_paths ?? []) as string[]) {
      const { data } = await sb.storage.from("study").download(path);
      if (data) report.push(await geminiFilePart(path, data, data.type || "image/jpeg"));
    }
    const out = await generateJson<Out>([{ text: REPORT_PROMPT(n) }, ...parts, ...report], {
      type: "object",
      properties: { reported: { type: "array", items: QUESTION }, practice: { type: "array", items: QUESTION } },
      required: ["reported", "practice"],
    });
    const insert = [...rows(r.course_id, lessonId, n, out.reported ?? [], "entry_reported"),
      ...rows(r.course_id, lessonId, n, out.practice ?? [], "entry_practice")];
    if (!insert.length) throw new Error("לא זוהו שאלות בדיווח");
    const { error } = await sb.from("questions").insert(insert);
    if (error) throw new Error(error.message);
    await sb.from("entry_reports").update({ status: "done", error: null }).eq("id", reportId);
    return `✓ ${out.reported?.length ?? 0} שאלות שנשאלו + ${out.practice?.length ?? 0} שאלות תרגול נוספו לניסוי ${n}`;
  } catch (e) {
    const msg = (e as Error).message;
    await sb.from("entry_reports").update({ status: "error", error: msg.slice(0, 500) }).eq("id", reportId);
    throw e;
  }
}

/** Course files that hold past entry quizzes ("בוחן כניסה 1", "2"...) -> questions per experiment. Each file once. */
export async function importEntryFiles(sb: SupabaseClient, courseId: string) {
  const [{ data: materials }, { data: done }] = await Promise.all([
    sb.from("materials").select("id, title, storage_path, mime").eq("course_id", courseId),
    sb.from("entry_reports").select("material_id").eq("course_id", courseId).not("material_id", "is", null),
  ]);
  const seen = new Set((done ?? []).map((d) => d.material_id));
  const todo = (materials ?? []).filter((m) => ENTRY_FILE.test(m.title) && !seen.has(m.id));
  if (!todo.length) return "לא נמצאו קבצים חדשים עם בחני כניסה (שם הקובץ צריך לכלול 'בוחן' או 'כניסה')";
  let count = 0;
  const per = new Map<number, number>();
  for (const m of todo) {
    const blob = await materialBlob(sb, m);
    const out = await generateJson<FileOut>([{ text: FILE_PROMPT }, await geminiFilePart(m.storage_path, blob, m.mime || blob.type || "application/pdf")], {
      type: "object",
      properties: { items: { type: "array", items: { ...QUESTION, properties: { ...QUESTION.properties, experiment: { type: "integer" } },
        required: [...QUESTION.required, "experiment"] } } },
      required: ["items"],
    });
    const byExp = new Map<number, Q[]>();
    for (const q of out.items ?? []) if (q.experiment > 0) byExp.set(q.experiment, [...(byExp.get(q.experiment) ?? []), q]);
    for (const [n, qs] of byExp) {
      const { lessonId } = await experimentLesson(sb, courseId, n);
      const insert = rows(courseId, lessonId, n, qs, "entry_reported");
      if (insert.length) {
        const { error } = await sb.from("questions").insert(insert);
        if (error) throw new Error(error.message);
        count += insert.length;
        per.set(n, (per.get(n) ?? 0) + insert.length);
      }
    }
    await sb.from("entry_reports").insert({ course_id: courseId, material_id: m.id, text: m.title, status: "done" });
  }
  const list = [...per].sort((a, b) => a[0] - b[0]).map(([n, c]) => `ניסוי ${n}: ${c}`).join(", ");
  return `✓ נקראו ${todo.length} קבצים - ${count} שאלות${list ? ` (${list})` : ""}`;
}

async function experimentLesson(sb: SupabaseClient, courseId: string, n: number) {
  const { data } = await sb.from("lessons").select("id").eq("course_id", courseId).eq("kind", "lab").eq("number", n)
    .order("created_at").limit(1).maybeSingle();
  return { lessonId: data?.id ?? null };
}
