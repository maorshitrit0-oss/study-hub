import type { SupabaseClient } from "@supabase/supabase-js";
import { withGemini } from "./gemini";

/**
 * Documents built from everything a course has, kept as course files (materials) so the course chat sees them too:
 * a formula sheet (two A4 pages: the one double-sided page allowed in the exam) and, for a lab, what to expect in
 * the practical final exam. Rebuilt on request as lessons are added.
 */
export const DOCS = {
  formulas: { file: "formula_sheet.md", title: "📄 דף נוסחאות" },
  practical: { file: "practical_exam.md", title: "🧪 המבחן המעשי - מה צפוי" },
} as const;
export type DocKind = keyof typeof DOCS;

const FORMULAS = `בנה דף נוסחאות למבחן בקורס, מכל החומר המצורף (תקצירים ופרקים של כל השיעורים עד עכשיו).
הדף צריך להיכנס בשני עמודי A4 (דף אחד דו-צדדי, כמו שמותר להביא למבחן), ולכן:
- מסודר לפי נושאים (כותרות ### קצרות), בסדר שבו נלמדו.
- כל הנוסחאות, ההגדרות הקצרות, היחידות, תנאי השימוש ("נכון רק כאשר...") והטריקים שהמרצה הראה לפתרון תרגילים.
- כל משוואה בשורה נפרדת $$...$$. טבלאות Markdown כשזה חוסך מקום (למשל השוואה בין מקרים).
- בלי הסברים ארוכים ובלי דוגמאות - רק מה שצריך מול תרגיל במבחן.
- רק מה שהופיע בחומר. בדוק כל נוסחה (ממדים, סימנים, מקדמים) - טעות בדף נוסחאות עולה ציון.
- בסוף: "### טעויות נפוצות" - 3-6 שורות.
החזר רק את הדף (Markdown), בלי הקדמה.`;

const PRACTICAL = `בנה דף הכנה למבחן המעשי בסוף המעבדה, מכל החומר המצורף (פרקי הניסויים, הדוחות המכינים ושאלות בוחני הכניסה).
המבנה של המבחן (לפי מה שהסטודנט סיפר על המבחן המעשי במעבדה הקודמת): 3 שאלות -
(1) שאלה תיאורטית או שאלה על גרף, על כל החומר של הסמסטר; (2) שאלה מילולית;
(3) לבנות מעגל על המטריצה (breadboard) ולהראות אותו עובד במכשירים - למשל מקבלים שני גלים ובונים מגבר סוכם ומראים בסקופ.
אין יום תרגול מעשי השנה; הסטודנט מתרגל בניה בבית בסימולטור (Tinkercad Circuits / Falstad).
כתוב בעברית:
## מבנה המבחן ואיך להתכונן
## לכל ניסוי (### ניסוי N - שם)
- שאלות תיאוריה / גרפים שעלולות להישאל - עם תשובה קצרה ונכונה.
- שאלות מילוליות - עם תשובה קצרה.
- מעגלים שעלולים לבקש לבנות: המעגל, ערכי רכיבים טיפוסיים, חיווט על המטריצה צעד אחרי צעד, כיוון מחולל האותות,
  הסקופ והמולטימטר, מה אמור להופיע על המסך, וטעויות נפוצות.
## רשימת "חובה לדעת לבנות" - כל המעגלים מכל הניסויים, מהסביר ביותר לפחות.
## 3 מבחני דמה - כל אחד 3 שאלות במבנה של המבחן, עם תשובות.
רק על בסיס החומר המצורף; מה שהוא הערכה שלך - סמן "(הערכה)". בדוק כל נוסחה וערך.`;

export async function buildDoc(sb: SupabaseClient, courseId: string, kind: DocKind) {
  const [{ data: course }, { data: lessons }] = await Promise.all([
    sb.from("courses").select("id, name, user_id").eq("id", courseId).single(),
    sb.from("lessons").select("*").eq("course_id", courseId).eq("status", "ready").order("number").order("created_at"),
  ]);
  if (!course) throw new Error("הקורס לא נמצא");
  // chapter_md is the full chapter when there is one, the summary otherwise.
  const parts = (lessons ?? []).map((l) => `######## ${l.kind} ${l.number ?? ""} ${l.title ?? ""}\n${(l.chapter_md ?? "").slice(0, 40_000)}`);
  if (kind === "practical") {
    const { data: qs } = await sb.from("questions").select("question, options, correct, experiment")
      .eq("course_id", courseId).not("source", "is", null).limit(200);
    if (qs?.length) parts.push("######## שאלות בוחני כניסה שנשאלו\n" + qs.map((q) => `ניסוי ${q.experiment}: ${q.question} -> ${q.options[q.correct]}`).join("\n"));
  }
  if (!parts.length) throw new Error("אין עדיין שיעורים מוכנים בקורס");
  const text = await withGemini("work", async (ai, model) => {
    const res = await ai.models.generateContent({
      model,
      contents: [{ role: "user", parts: [{ text: `קורס: ${course.name}\n\n${kind === "formulas" ? FORMULAS : PRACTICAL}` }, { text: parts.join("\n\n") }] }],
    });
    return (res.text ?? "").replace(/^```(?:markdown|md)?\s*|\s*```$/g, "").trim();
  });
  if (!text) throw new Error("Gemini החזיר דף ריק - לנסות שוב");
  const path = `${course.user_id}/materials/${courseId}/${DOCS[kind].file}`;
  const stamp = `> נבנה ${new Date().toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" })} מ-${(lessons ?? []).length} שיעורים.\n\n`;
  const { error } = await sb.storage.from("study").upload(path, new Blob([stamp + text], { type: "text/markdown" }), { upsert: true, contentType: "text/markdown; charset=utf-8" });
  if (error) throw new Error(error.message);
  const { data: have } = await sb.from("materials").select("id").eq("storage_path", path).maybeSingle();
  if (!have) await sb.from("materials").insert({ course_id: courseId, title: DOCS[kind].title, kind: "other", storage_path: path, mime: "text/plain" });
}

export async function readDoc(sb: SupabaseClient, userId: string, courseId: string, kind: DocKind) {
  const { data } = await sb.storage.from("study").download(`${userId}/materials/${courseId}/${DOCS[kind].file}`);
  return data ? await data.text() : null;
}
