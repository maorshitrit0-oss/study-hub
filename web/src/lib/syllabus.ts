import { generateJson } from "./gemini";
import { geminiFilePart } from "./files";
import type { SupabaseClient } from "@supabase/supabase-js";

const SCHEMA = {
  type: "object",
  properties: {
    facts: {
      type: "array",
      items: {
        type: "object",
        properties: {
          category: { type: "string", enum: ["exam", "exam_hint", "grading", "reservist", "assignments", "attendance", "materials", "other"] },
          text: { type: "string" },
        },
        required: ["category", "text"],
      },
    },
    topics: { type: "array", items: { type: "string" } },
    exam_type: { type: "string", enum: ["mcq", "open", "mixed", "none", "unknown"] },
    grade_weights: {
      type: "array",
      items: { type: "object", properties: { name: { type: "string" }, weight: { type: "integer" } }, required: ["name", "weight"] },
    },
  },
  required: ["facts", "topics", "exam_type", "grade_weights"],
};

const PROMPT = `זה סילבוס (או מסמך מנהלי) של קורס בהנדסת חשמל. חלץ ממנו כל מידע מנהלי חשוב לסטודנט, משפט ברור אחד לכל פריט, עם מספרים ותאריכים מדויקים:
exam = מבנה המבחן (אמריקאי/פתוח, משך, חומר עזר מותר, מועדים); exam_hint = מה ייכלל או לא ייכלל במבחן; grading = משקלים, ציון עובר, ציון מגן, בונוסים;
reservist = הקלות ונהלים למשרתי מילואים ומה צריך לעשות ועד מתי; assignments = מטלות, הגשות, חובות; attendance = נוכחות; materials = ספרות, תוכנות, דף נוסחאות; other = כל דבר מנהלי חשוב אחר.
את רשימת נושאי הלימוד אל תכניס ל-facts אלא ל-topics: הנושאים לפי הסדר שבסילבוס (שם קצר לכל נושא; אם יש חלוקה לשבועות - נושא לכל שבוע). exam_type ו-grade_weights רק אם כתובים במפורש, אחרת "unknown" ורשימה ריקה. ענה בעברית.`;

export const looksLikeSyllabus = (name: string) => /syl|סילבוס|syllabus|מידע.?על.?הקורס|course.?info/i.test(name);

/** Builds the Gemini part for a document: PDFs/images go in as-is, Word files are converted to text. */
async function documentPart(file: Blob, mime: string, name: string) {
  const ext = name.toLowerCase().split(".").pop() ?? "";
  const bytes = Buffer.from(await file.arrayBuffer());
  if (ext === "docx" || mime.includes("wordprocessingml")) {
    const mammoth = await import("mammoth");
    const { value } = await mammoth.extractRawText({ buffer: bytes });
    return { text: `=== תוכן המסמך ===\n${value}` };
  }
  if (ext === "pdf" || mime === "application/pdf") return geminiFilePart(`syllabus:${name}:${file.size}`, file, "application/pdf");
  if (mime.startsWith("image/")) return geminiFilePart(`syllabus:${name}:${file.size}`, file, mime);
  if (["txt", "md"].includes(ext) || mime.startsWith("text/")) return { text: `=== תוכן המסמך ===\n${bytes.toString("utf8")}` };
  throw new Error(`אי אפשר לקרוא קובץ מסוג ${ext || mime} - העלה את הסילבוס כ-PDF או Word (docx)`);
}

/** Reads an uploaded syllabus with Gemini and stores its admin facts on the course. Returns a status line. */
export async function extractSyllabus(sb: SupabaseClient, courseId: string, file: Blob, mime: string, name: string) {
  const out = await generateJson<{
    facts?: { category: string; text: string }[];
    exam_type?: string;
    grade_weights?: { name: string; weight: number }[];
    topics?: string[];
  }>([{ text: PROMPT }, await documentPart(file, mime, name)], SCHEMA);

  // Replace facts from an earlier syllabus; lecture facts and ones the user added stay.
  const del = await sb.from("course_facts").delete().eq("course_id", courseId).eq("source", "syllabus");
  if (del.error) throw new Error(`שמירה נכשלה: ${del.error.message}`);
  const facts = (out.facts ?? []).filter((f) => f.text);
  if (facts.length) {
    const ins = await sb.from("course_facts").insert(facts.map((f) => ({ course_id: courseId, category: f.category, text: f.text, source: "syllabus" })));
    if (ins.error) throw new Error(`שמירה נכשלה: ${ins.error.message}`);
  }

  const { data: course } = await sb.from("courses").select("exam_type, grade_weights").eq("id", courseId).single();
  const update: Record<string, unknown> = {};
  if (!course?.exam_type && out.exam_type && out.exam_type !== "unknown") update.exam_type = out.exam_type;
  const weights = (out.grade_weights ?? []).filter((w) => w.name && w.weight);
  if (!course?.grade_weights?.length && weights.length) update.grade_weights = weights;
  const topics = (out.topics ?? []).filter(Boolean);
  if (topics.length) update.syllabus_topics = topics;
  if (Object.keys(update).length) await sb.from("courses").update(update).eq("id", courseId);
  return facts.length || topics.length
    ? `✓ נקראו ${facts.length} פרטים ו-${topics.length} נושאים מהסילבוס - מופיעים בראש דף הקורס`
    : "הסילבוס נקרא, אבל לא נמצא בו מידע על המבחן או על הנושאים";
}
