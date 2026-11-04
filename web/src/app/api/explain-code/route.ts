import { generateJson, friendlyGeminiError } from "@/lib/gemini";
import { supabaseServer } from "@/lib/supabase/server";

export const maxDuration = 120;

// He is not strong in code (04/11/2026): under every code block in the app, each line translated into Hebrew.
const SYSTEM = `אתה מסביר קוד לסטודנט להנדסת חשמל שלא חזק בתכנות (מכיר מעט מושגים ב-C++).
קיבלת קטע קוד (Java / C / אסמבלי / SystemVerilog / Python וכו'). לכל שורה בקוד, לפי הסדר - "he": מה השורה עושה, בעברית פשוטה,
משפט או שניים: מה היא עושה ולמה היא שם. כל מילה שמורה, טיפוס, פונקציה או סימן (למשל public, static, int, ;, {}, ++, %, ==)
שמופיעים בפעם הראשונה - מה הם אומרים. שורה ריקה או רק סוגר } - הסבר קצר מה נסגר. מונחים באנגלית בסוגריים.
"code": השורה עצמה כמו שהיא (בלי רווחים בהתחלה). רק נכון; אם זה פלט ולא קוד - הסבר מה רואים בו.`;

const SCHEMA = {
  type: "object",
  properties: { lines: { type: "array", items: { type: "object", properties: { code: { type: "string" }, he: { type: "string" } }, required: ["code", "he"] } } },
  required: ["lines"],
};

export async function POST(req: Request) {
  const sb = await supabaseServer();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return Response.json({ error: "צריך להתחבר" }, { status: 401 });
  const { code, lang } = (await req.json()) as { code?: string; lang?: string };
  if (!code?.trim() || code.length > 12000) return Response.json({ error: "קוד ריק או ארוך מדי" }, { status: 400 });
  try {
    const out = await generateJson<{ lines: { code: string; he: string }[] }>(
      [{ text: `שפה: ${lang || "לא ידוע"}\n\n${code}` }], SCHEMA, SYSTEM);
    return Response.json({ lines: (out.lines ?? []).filter((l) => l.code.trim() && l.he.trim()) });
  } catch (e) {
    return Response.json({ error: friendlyGeminiError(e) }, { status: 502 });
  }
}
