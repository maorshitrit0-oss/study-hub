import { GoogleGenAI } from "@google/genai";
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
    exam_type: { type: "string", enum: ["mcq", "open", "mixed", "none", "unknown"] },
    grade_weights: {
      type: "array",
      items: { type: "object", properties: { name: { type: "string" }, weight: { type: "integer" } }, required: ["name", "weight"] },
    },
  },
  required: ["facts", "exam_type", "grade_weights"],
};

const PROMPT = `זה סילבוס (או מסמך מנהלי) של קורס בהנדסת חשמל. חלץ ממנו כל מידע מנהלי חשוב לסטודנט, משפט ברור אחד לכל פריט, עם מספרים ותאריכים מדויקים:
exam = מבנה המבחן (אמריקאי/פתוח, משך, חומר עזר מותר, מועדים); exam_hint = מה ייכלל או לא ייכלל במבחן; grading = משקלים, ציון עובר, ציון מגן, בונוסים;
reservist = הקלות ונהלים למשרתי מילואים ומה צריך לעשות ועד מתי; assignments = מטלות, הגשות, חובות; attendance = נוכחות; materials = ספרות, תוכנות, דף נוסחאות; other = כל דבר מנהלי חשוב אחר.
אל תכלול את רשימת נושאי הלימוד עצמה. exam_type ו-grade_weights רק אם כתובים במפורש, אחרת "unknown" ורשימה ריקה. ענה בעברית.`;

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
  if (ext === "pdf" || mime === "application/pdf") return { inlineData: { mimeType: "application/pdf", data: bytes.toString("base64") } };
  if (mime.startsWith("image/")) return { inlineData: { mimeType: mime, data: bytes.toString("base64") } };
  if (["txt", "md"].includes(ext) || mime.startsWith("text/")) return { text: `=== תוכן המסמך ===\n${bytes.toString("utf8")}` };
  throw new Error(`אי אפשר לקרוא קובץ מסוג ${ext || mime} - העלה את הסילבוס כ-PDF או Word (docx)`);
}

/** Reads an uploaded syllabus with Gemini and stores its admin facts on the course. Returns a status line. */
export async function extractSyllabus(sb: SupabaseClient, courseId: string, file: Blob, mime: string, name: string) {
  if (!process.env.GEMINI_API_KEY) throw new Error("לא הוגדר GEMINI_API_KEY ב-Vercel");
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const res = await ai.models.generateContent({
    model: process.env.GEMINI_MODEL || "gemini-flash-latest",
    contents: [{ role: "user", parts: [{ text: PROMPT }, await documentPart(file, mime, name)] }],
    config: { responseMimeType: "application/json", responseJsonSchema: SCHEMA },
  });
  const out = JSON.parse(res.text ?? "{}") as {
    facts?: { category: string; text: string }[];
    exam_type?: string;
    grade_weights?: { name: string; weight: number }[];
  };

  // Syllabus facts are the ones without a lesson; replace them with the newest syllabus.
  const del = await sb.from("course_facts").delete().eq("course_id", courseId).is("lesson_id", null);
  if (del.error) throw new Error(`שמירה נכשלה: ${del.error.message}`);
  const facts = (out.facts ?? []).filter((f) => f.text);
  if (facts.length) {
    const ins = await sb.from("course_facts").insert(facts.map((f) => ({ course_id: courseId, category: f.category, text: f.text })));
    if (ins.error) throw new Error(`שמירה נכשלה: ${ins.error.message}`);
  }

  const { data: course } = await sb.from("courses").select("exam_type, grade_weights").eq("id", courseId).single();
  const update: Record<string, unknown> = {};
  if (!course?.exam_type && out.exam_type && out.exam_type !== "unknown") update.exam_type = out.exam_type;
  const weights = (out.grade_weights ?? []).filter((w) => w.name && w.weight);
  if (!course?.grade_weights?.length && weights.length) update.grade_weights = weights;
  if (Object.keys(update).length) await sb.from("courses").update(update).eq("id", courseId);
  return facts.length ? `✓ נקראו ${facts.length} פרטים מהסילבוס - מופיעים למעלה ב"מידע על הקורס"` : "הסילבוס נקרא, אבל לא נמצא בו מידע על המבחן או הציון";
}
