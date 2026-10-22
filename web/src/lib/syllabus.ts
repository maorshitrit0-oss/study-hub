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

/** Reads an uploaded syllabus with Gemini and stores its admin facts on the course. Returns a status line. */
export async function extractSyllabus(sb: SupabaseClient, courseId: string, file: Blob, mime: string) {
  if (!process.env.GEMINI_API_KEY) return "לא הוגדר GEMINI_API_KEY";
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const res = await ai.models.generateContent({
    model: process.env.GEMINI_MODEL || "gemini-flash-latest",
    contents: [{
      role: "user",
      parts: [{ text: PROMPT }, { inlineData: { mimeType: mime, data: Buffer.from(await file.arrayBuffer()).toString("base64") } }],
    }],
    config: { responseMimeType: "application/json", responseJsonSchema: SCHEMA },
  });
  const out = JSON.parse(res.text ?? "{}") as {
    facts?: { category: string; text: string }[];
    exam_type?: string;
    grade_weights?: { name: string; weight: number }[];
  };

  // Syllabus facts are the ones without a lesson; replace them with the newest syllabus.
  await sb.from("course_facts").delete().eq("course_id", courseId).is("lesson_id", null);
  const facts = (out.facts ?? []).filter((f) => f.text);
  if (facts.length) await sb.from("course_facts").insert(facts.map((f) => ({ course_id: courseId, category: f.category, text: f.text })));

  const { data: course } = await sb.from("courses").select("exam_type, grade_weights").eq("id", courseId).single();
  const update: Record<string, unknown> = {};
  if (!course?.exam_type && out.exam_type && out.exam_type !== "unknown") update.exam_type = out.exam_type;
  const weights = (out.grade_weights ?? []).filter((w) => w.name && w.weight);
  if (!course?.grade_weights?.length && weights.length) update.grade_weights = weights;
  if (Object.keys(update).length) await sb.from("courses").update(update).eq("id", courseId);
  return `נקראו ${facts.length} פרטים מהסילבוס`;
}
