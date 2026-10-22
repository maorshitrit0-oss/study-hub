import { GoogleGenAI, type Content, type Part } from "@google/genai";
import { supabaseServer } from "@/lib/supabase/server";
import { EXAM_LABEL, lessonName, type Course, type Lesson } from "@/lib/types";

export const maxDuration = 60;

const MAX_CONTEXT_CHARS = 400_000;
const MAX_FILE_BYTES = 15 * 1024 * 1024;

const SYSTEM = `אתה המרצה והמתרגל הפרטי של סטודנט להנדסת חשמל, בקורס אחד ספציפי. ענה תמיד בעברית, ומונחים טכניים גם באנגלית.
הסטודנט לומד מקריאה ולא מצפייה בהרצאות. בסס תשובות על חומר הקורס שמצורף (פרקי ההרצאות והתרגולים, וקבצים כמו מבחני עבר ומצגות) וציין מאיזו הרצאה/קובץ זה מגיע.
- נוסחאות ב-LaTeX: $...$ או $$...$$. קוד בבלוקי קוד.
- כשמבקשים ללמד: נושא אחרי נושא, אינטואיציה -> פורמליזם -> דוגמה, ושאלת הבנה בסוף כל שלב.
- כשמבקשים שאלון/תרגול: שאלה אחת בכל פעם, 4 תשובות ממוספרות 1-4, חכה לתשובה ואז הסבר.
- כשמבקשים הכנה למבחן: נתח את מבחני העבר המצורפים (סוג שאלות, נושאים חוזרים, משקלים) ובנה תוכנית/מבחן לדוגמה בסגנון שלהם.
- כשמצורפת תמונה (לוח, מחברת, שאלה מצולמת) - קרא אותה בעיון ועבוד איתה.
- אם משהו לא מופיע בחומר - אמור זאת, ואז ענה מהידע הכללי שלך וסמן שזה מחוץ לחומר.`;

export async function POST(req: Request) {
  const sb = await supabaseServer();
  const { data: auth } = await sb.auth.getClaims();
  if (!auth?.claims) return new Response("unauthorized", { status: 401 });
  if (!process.env.GEMINI_API_KEY) return new Response("GEMINI_API_KEY לא מוגדר ב-Vercel", { status: 500 });

  const { courseId, message, imagePaths = [] } = (await req.json()) as {
    courseId: string; message: string; imagePaths?: string[];
  };

  const [{ data: course }, { data: lessons }, { data: materials }, { data: history }] = await Promise.all([
    sb.from("courses").select("*").eq("id", courseId).single(),
    sb.from("lessons").select("kind, number, title, chapter_md, created_at").eq("course_id", courseId).eq("status", "ready").order("created_at"),
    sb.from("materials").select("title, kind, storage_path, mime, size_bytes").eq("course_id", courseId).order("created_at"),
    sb.from("chat_messages").select("role, content").eq("course_id", courseId).order("created_at", { ascending: false }).limit(20),
  ]);
  if (!course) return new Response("course not found", { status: 404 });
  const c = course as Course;

  // Course context: info + reading chapters (newest kept if over budget) + PDFs/images.
  let context = `קורס: ${c.name}\nמרצה: ${c.lecturer ?? "-"}\nסוג מבחן: ${c.exam_type ? EXAM_LABEL[c.exam_type] : "לא ידוע"}\n` +
    `משקלים: ${c.grade_weights.map((w) => `${w.name} ${w.weight}%`).join(", ") || "-"}\nהערות: ${c.notes ?? "-"}\n`;
  const chapters = ((lessons ?? []) as Lesson[]).map((l) => `\n\n######## ${lessonName(l)}${l.title ? ` - ${l.title}` : ""}\n${l.chapter_md}`);
  let budget = MAX_CONTEXT_CHARS - context.length;
  const kept: string[] = [];
  for (const ch of chapters.reverse()) {
    if (ch.length > budget) break;
    kept.unshift(ch);
    budget -= ch.length;
  }
  context += kept.join("");

  const contextParts: Part[] = [{ text: `=== חומר הקורס ===\n${context}` }];
  let bytes = 0;
  for (const m of materials ?? []) {
    const ok = m.mime === "application/pdf" || m.mime?.startsWith("image/") || m.mime?.startsWith("text/");
    if (!ok || bytes + (m.size_bytes ?? 0) > MAX_FILE_BYTES) continue;
    const { data: blob } = await sb.storage.from("study").download(m.storage_path);
    if (!blob) continue;
    bytes += blob.size;
    contextParts.push({ text: `קובץ: ${m.title} (${m.kind})` });
    contextParts.push({ inlineData: { mimeType: m.mime!, data: Buffer.from(await blob.arrayBuffer()).toString("base64") } });
  }

  const userParts: Part[] = [{ text: message }];
  for (const p of imagePaths) {
    const { data: blob } = await sb.storage.from("study").download(p);
    if (blob) userParts.push({ inlineData: { mimeType: blob.type || "image/jpeg", data: Buffer.from(await blob.arrayBuffer()).toString("base64") } });
  }

  const contents: Content[] = [
    { role: "user", parts: contextParts },
    { role: "model", parts: [{ text: "קיבלתי את חומר הקורס. במה נתחיל?" }] },
    ...((history ?? []).reverse().map((h) => ({ role: h.role, parts: [{ text: h.content }] }))),
    { role: "user", parts: userParts },
  ];

  await sb.from("chat_messages").insert({ course_id: courseId, role: "user", content: message, image_paths: imagePaths });

  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const stream = await ai.models.generateContentStream({
    model: process.env.GEMINI_MODEL || "gemini-flash-latest",
    contents,
    config: { systemInstruction: SYSTEM },
  });

  const encoder = new TextEncoder();
  let full = "";
  return new Response(
    new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const t = chunk.text;
            if (t) {
              full += t;
              controller.enqueue(encoder.encode(t));
            }
          }
        } catch (e) {
          const msg = `\n\n⚠️ שגיאה: ${(e as Error).message}`;
          full += msg;
          controller.enqueue(encoder.encode(msg));
        }
        if (full) await sb.from("chat_messages").insert({ course_id: courseId, role: "model", content: full });
        controller.close();
      },
    }),
    { headers: { "Content-Type": "text/plain; charset=utf-8" } },
  );
}
