import { ThinkingLevel, type Content, type Part } from "@google/genai";
import { friendlyGeminiError, withGemini } from "@/lib/gemini";
import { supabaseServer } from "@/lib/supabase/server";
import { DRIVE_PREFIX, geminiFilePart, materialBlob } from "@/lib/files";
import { EXAM_LABEL, lessonName, type Course, type Lesson } from "@/lib/types";

export const maxDuration = 300;

const MAX_CONTEXT_CHARS = 400_000;
const MAX_FILE_BYTES = 250 * 1024 * 1024;
// Course files (PDFs etc.) are big and slow to send; attach them only when the question needs them.
const NEEDS_FILES = /מבחן|בחינ|עבר|סילבוס|מצגת|שקפ|קובץ|קבצ|pdf|חוברת|דוח|מטל|תרגיל בית|ניסוי|בוחן/i;

const SYSTEM = `אתה המרצה והמתרגל הפרטי של סטודנט להנדסת חשמל, בקורס אחד ספציפי. ענה תמיד בעברית, ומונחים טכניים גם באנגלית.
הסטודנט לא חזק באנגלית: כשאתה מצטט או מסביר חומר שכתוב באנגלית (שקפים, קבצים, שאלות ממבחנים) - תרגם אותו לעברית במלואו, והשאר את המונחים באנגלית בסוגריים.
הסטודנט לומד מקריאה ולא מצפייה בהרצאות. בסס תשובות על חומר הקורס שמצורף (פרקי ההרצאות והתרגולים, וקבצים כמו מבחני עבר ומצגות) וציין מאיזו הרצאה/קובץ זה מגיע.
- נוסחאות ב-LaTeX: $...$ או $$...$$. קוד בבלוקי קוד.
- כשמבקשים ללמד: נושא אחרי נושא, אינטואיציה -> פורמליזם -> דוגמה, ושאלת הבנה בסוף כל שלב.
- כשמבקשים שאלון/תרגול: שאלה אחת בכל פעם, 4 תשובות ממוספרות 1-4, חכה לתשובה ואז הסבר.
- כשמבקשים הכנה למבחן: נתח את מבחני העבר המצורפים (סוג שאלות, נושאים חוזרים, משקלים) ובנה תוכנית/מבחן לדוגמה בסגנון שלהם.
- כשמצורפת תמונה (לוח, מחברת, שאלה מצולמת) - קרא אותה בעיון ועבוד איתה.
- אם משהו לא מופיע בחומר - אמור זאת, ואז ענה מהידע הכללי שלך וסמן שזה מחוץ לחומר.
- בקורס מעבדה: עבוד רק בגבולות חוברת הניסוי והדוח המכין. עזור להבין ולפתור את שאלות הדוח המכין (הסבר כל צעד - הסטודנט צריך להבין, לא רק להעתיק).
  "תכין אותי ללוח": תן לו להסביר את הניסוי במילים שלו, ואז שאל כמו מדריך המעבדה, שאלה אחת בכל פעם, תקן ותן ציון בסוף.
  "בוחן כניסה": שאלות קצרות בסגנון בוחן כניסה על הניסוי, אחת בכל פעם.

דוחות קודמים (סוג הקובץ prev_report, למשל של שותפים שעשו את המעבדה בסמסטר קודם):
- כשמבקשים "מה לשנות" - השווה את הדוח הקודם לחוברת הניסוי הנוכחית, סעיף אחרי סעיף (מטרה, רקע, ציוד, מהלך, שרטוטים/מעגלים, טבלאות, גרפים, ניתוח, מסקנות, שאלות).
- פרט כל שינוי במדויק: מה כתוב בדוח, מה צריך להיות לפי החוברת, ואיפה בחוברת זה מופיע (עמוד/סעיף/שאלה). כולל שינויים קטנים: ערכי רכיבים, מספרי שאלות, שלבים שנוספו או הוסרו.
- מדידות, תוצאות וגרפים חייבים להיות מהמדידות של הסטודנט עצמו במפגש - סמן אותם "להחליף במדידות שלכם" ואל תעתיק ערכים מהדוח הקודם כאילו הם שלו.
- אם החוברת לא מצורפת או שאינך בטוח איזה ניסוי זה - שאל לפני שאתה עונה.

דיוק לפני הכל - הסטודנט ייבחן על מה שתלמד אותו:
- לפני שאתה מלמד הגדרה, נוסחה, משפט או פתרון - ודא אותם מול חומר הקורס ומול הידע המקצועי. חשב מחדש כל חישוב, ובדוק יחידות וסימנים.
- כשאתה נותן שאלה ותשובה - פתור בעצמך לפני שאתה קובע מה נכון, וודא שיש תשובה נכונה אחת בלבד.
- אם המרצה אמר משהו שונה מהמקובל - הצג את שניהם, הסבר את ההבדל, ואמור מה כנראה ייבדק במבחן של המרצה הזה.
- אם אינך בטוח ב-100% - אמור זאת במפורש ("כדאי לוודא מול המרצה/הספר") ואל תנחש.
- אם הסטודנט טוען משהו שגוי - תקן אותו בעדינות, גם אם הוא מתעקש.`;

export async function POST(req: Request) {
  const sb = await supabaseServer();
  const { data: auth } = await sb.auth.getClaims();
  if (!auth?.claims) return new Response("unauthorized", { status: 401 });

  const { courseId, message, imagePaths = [], withFiles = false } = (await req.json()) as {
    courseId: string; message: string; imagePaths?: string[]; withFiles?: boolean;
  };
  // Bound what one request can make the server download and send to Gemini.
  if (typeof message !== "string" || !message.trim() || message.length > 20_000 || !Array.isArray(imagePaths) || imagePaths.length > 10
    || imagePaths.some((p) => typeof p !== "string" || !p.startsWith(`${auth.claims.sub}/`))) {
    return new Response("bad request", { status: 400 });
  }
  const attachFiles = withFiles || NEEDS_FILES.test(message);

  const [{ data: course }, { data: lessons }, { data: materials }, { data: history }, { data: facts }, { data: settings }] = await Promise.all([
    sb.from("courses").select("*").eq("id", courseId).single(),
    sb.from("lessons").select("kind, number, title, chapter_md, created_at").eq("course_id", courseId).eq("status", "ready").order("created_at"),
    sb.from("materials").select("title, kind, storage_path, mime, size_bytes").eq("course_id", courseId).order("created_at"),
    sb.from("chat_messages").select("role, content").eq("course_id", courseId).order("created_at", { ascending: false }).limit(20),
    sb.from("course_facts").select("category, text").eq("course_id", courseId).order("created_at"),
    sb.from("settings").select("is_reservist").eq("user_id", auth.claims.sub).maybeSingle(),
  ]);
  if (!course) return new Response("course not found", { status: 404 });
  const c = course as Course;

  // Course context: info + reading chapters (newest kept if over budget) + PDFs/images.
  let context = `קורס: ${c.name}\nמרצה: ${c.lecturer ?? "-"}\nסוג מבחן: ${c.exam_type ? EXAM_LABEL[c.exam_type] : "לא ידוע"}\n` +
    `משקלים: ${c.grade_weights.map((w) => `${w.name} ${w.weight}%`).join(", ") || "-"}\nהערות: ${c.notes ?? "-"}\n` +
    `הסטודנט ${settings?.is_reservist ? "משרת מילואים בסמסטר הזה - התחשב בהקלות למילואימניקים" : "לא מסומן כמשרת מילואים כרגע"}.\n` +
    (facts?.length ? `\nמה שהמרצה אמר על הקורס (מבחן, ציון, מילואים, מטלות):\n${facts.map((f) => `- [${f.category}] ${f.text}`).join("\n")}\n` : "");
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
  // Big files (e.g. scanned quizzes) go through the Gemini Files API; cap the total per message.
  let bytes = 0;
  const files = attachFiles
    ? (materials ?? []).filter((m) => {
        const ok = m.mime === "application/pdf" || m.mime?.startsWith("image/") || m.mime?.startsWith("text/")
          || m.storage_path.startsWith(DRIVE_PREFIX);
        if (!ok || bytes + (m.size_bytes ?? 0) > MAX_FILE_BYTES) return false;
        bytes += m.size_bytes ?? 0;
        return true;
      })
    : [];
  if (!attachFiles && materials?.length) {
    context += `\n\n(יש בקורס ${materials.length} קבצים: ${materials.map((m) => m.title).join(", ")}. הם לא צורפו להודעה הזו; אם צריך אותם, בקש מהסטודנט לסמן "עם קבצי הקורס".)`;
    contextParts[0] = { text: `=== חומר הקורס ===\n${context}` };
  }
  // Download course files and chat images in parallel.
  const [fileParts, imageBlobs] = await Promise.all([
    Promise.all(files.map(async (m) => {
      try {
        const blob = await materialBlob(sb, m);
        return await geminiFilePart(m.storage_path, blob, m.mime || blob.type || "application/pdf");
      } catch {
        return null;
      }
    })),
    Promise.all(imagePaths.map((p) => sb.storage.from("study").download(p))),
  ]);
  for (const [i, m] of files.entries()) {
    const part = fileParts[i];
    if (!part) continue;
    contextParts.push({ text: `קובץ: ${m.title} (${m.kind})` });
    contextParts.push(part);
  }

  const userParts: Part[] = [{ text: message }];
  for (const { data: blob } of imageBlobs) {
    if (blob) userParts.push({ inlineData: { mimeType: blob.type || "image/jpeg", data: Buffer.from(await blob.arrayBuffer()).toString("base64") } });
  }

  const contents: Content[] = [
    { role: "user", parts: contextParts },
    { role: "model", parts: [{ text: "קיבלתי את חומר הקורס. במה נתחיל?" }] },
    ...((history ?? []).reverse().map((h) => ({ role: h.role, parts: [{ text: h.content }] }))),
    { role: "user", parts: userParts },
  ];

  const saveUser = sb.from("chat_messages").insert({ course_id: courseId, role: "user", content: message, image_paths: imagePaths });

  // Small talk needs almost no reasoning; explanations and problems get a bit more.
  const light = message.length < 80 && !imagePaths.length && !attachFiles;
  const started = Date.now();
  let stream;
  try {
    stream = await withGemini("chat", async (ai, model) => {
      const request = (thinking: boolean) => ai.models.generateContentStream({
        model,
        contents,
        config: {
          systemInstruction: SYSTEM,
          ...(thinking ? { thinkingConfig: { thinkingLevel: light ? ThinkingLevel.MINIMAL : ThinkingLevel.LOW } } : {}),
        },
      });
      // Models without thinking levels reject the setting; retry them with their default.
      return request(true).catch((e) => (/thinking/i.test(String(e?.message)) ? request(false) : Promise.reject(e)));
    });
  } catch (e) {
    await saveUser;
    const text = `⚠️ ${friendlyGeminiError(e)}`;
    await sb.from("chat_messages").insert({ course_id: courseId, role: "model", content: text });
    return new Response(text, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }
  await saveUser;

  const encoder = new TextEncoder();
  let full = "";
  return new Response(
    new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const t = chunk.text;
            if (t) {
              if (!full) console.log(`chat first token after ${Date.now() - started}ms (files: ${files.length}, light: ${light})`);
              full += t;
              controller.enqueue(encoder.encode(t));
            }
          }
        } catch (e) {
          const msg = `\n\n⚠️ ${friendlyGeminiError(e)}`;
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
