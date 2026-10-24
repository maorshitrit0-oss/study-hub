import { friendlyGeminiError, withGemini } from "@/lib/gemini";
import { supabaseServer } from "@/lib/supabase/server";
import { saveMessage, validThread } from "@/lib/threads";
import { lessonName, type Lesson } from "@/lib/types";

export const maxDuration = 120;

const MAX_CONTEXT_CHARS = 250_000;

const VERIFY = `אתה בודק עובדות קפדן בהנדסת חשמל. סטודנט קיבל תשובה מעוזר AI על חומר הקורס, והוא ייבחן על זה - אסור שתישאר טעות.
קיבלת את חומר הקורס (פרקי השיעורים), את השאלה ואת התשובה. בדוק את התשובה פריט אחרי פריט:
- כל הגדרה, נוסחה, יחידה, סימן ומספר - מול חומר הקורס ומול הידע המקצועי (ובחיפוש אם צריך).
- כל חישוב ופתרון - פתור מחדש בעצמך מאפס, בלי להעתיק מהתשובה, והשווה.
- אם בתשובה יש שאלה אמריקאית - פתור אותה וודא שיש תשובה נכונה אחת בדיוק.
- אם המרצה בחומר אמר משהו אחר מהתשובה - ציין מה אמר המרצה.
כתוב בעברית, קצר וברור:
שורה ראשונה: "✅ התשובה נכונה" או "⚠️ יש מה לתקן" או "❓ לא ניתן לאמת במלואה".
אחר כך: רשימת התיקונים (מה נכתב, מה נכון, ולמה), ומה שאי אפשר לאמת. אל תחזור על מה שנכון.
נוסחאות ב-LaTeX: קצרות בתוך משפט ב-$...$, משוואה מלאה בשורה נפרדת ב-$$...$$.`;

/** Second, independent check of one chat answer (on demand, to save the free daily quota). */
export async function POST(req: Request) {
  const sb = await supabaseServer();
  const { data: auth } = await sb.auth.getClaims();
  if (!auth?.claims) return new Response("unauthorized", { status: 401 });
  const { courseId, question, answer, threadId: rawThread } = (await req.json()) as {
    courseId: string; question: string; answer: string; threadId?: string;
  };
  if (typeof answer !== "string" || !answer.trim() || answer.length > 60_000 || typeof question !== "string" || question.length > 20_000) {
    return new Response("bad request", { status: 400 });
  }
  const threadId = validThread(rawThread);
  const [{ data: course }, { data: lessons }, { data: facts }] = await Promise.all([
    sb.from("courses").select("name, notes").eq("id", courseId).single(),
    sb.from("lessons").select("kind, number, title, chapter_md").eq("course_id", courseId).eq("status", "ready").order("created_at"),
    sb.from("course_facts").select("category, text").eq("course_id", courseId),
  ]);
  if (!course) return new Response("course not found", { status: 404 });

  let budget = MAX_CONTEXT_CHARS;
  const kept: string[] = [];
  for (const l of ((lessons ?? []) as Lesson[]).reverse()) {
    const ch = `\n\n######## ${lessonName(l)}${l.title ? ` - ${l.title}` : ""}\n${l.chapter_md}`;
    if (ch.length > budget) break;
    kept.unshift(ch);
    budget -= ch.length;
  }
  const material = `קורס: ${course.name}\n${course.notes ?? ""}\n${(facts ?? []).map((f) => `- [${f.category}] ${f.text}`).join("\n")}${kept.join("")}`;
  const prompt = `=== חומר הקורס ===\n${material}\n\n=== השאלה של הסטודנט ===\n${question}\n\n=== התשובה לבדיקה ===\n${answer}`;

  let text: string;
  try {
    text = await withGemini("work", async (ai, model) => {
      const run = (search: boolean) => ai.models.generateContent({
        model,
        contents: prompt,
        config: { systemInstruction: VERIFY, ...(search ? { tools: [{ googleSearch: {} }] } : {}) },
      });
      // Search grounding helps, but some models/quotas refuse it: then check without.
      const res = await run(true).catch(() => run(false));
      return res.text?.trim() || "❓ הבדיקה לא החזירה תוצאה - לנסות שוב.";
    });
  } catch (e) {
    text = `⚠️ הבדיקה נכשלה: ${friendlyGeminiError(e)}`;
  }
  const content = `🔍 **בדיקת התשובה**\n\n${text}`;
  await saveMessage(sb, { course_id: courseId, role: "model", content }, threadId);
  return new Response(content, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
