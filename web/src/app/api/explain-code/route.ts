import { generateJson, friendlyGeminiError } from "@/lib/gemini";
import { supabaseServer } from "@/lib/supabase/server";
import { codeHash } from "@/lib/codeHash";

export const maxDuration = 120;

// He is not strong in code (04/11/2026): under every code block in the app, each line translated into Hebrew.
// Kept in storage (<user>/codelines/<hash>.json) so it is written once for all his devices; worker/codelines.py writes
// them ahead of time every morning, so a block is explained even on a day the free Gemini quota is gone (06/11/2026).
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

type Line = { code: string; he: string };

export async function POST(req: Request) {
  const sb = await supabaseServer();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) return Response.json({ error: "צריך להתחבר" }, { status: 401 });
  const { code, lang } = (await req.json()) as { code?: string; lang?: string };
  if (!code?.trim() || code.length > 12000) return Response.json({ error: "קוד ריק או ארוך מדי" }, { status: 400 });
  const path = `${user.id}/codelines/${codeHash(code)}.json`;
  const store = sb.storage.from("study");
  const { data: saved } = await store.download(path);
  if (saved) {
    try { return Response.json({ lines: JSON.parse(await saved.text()).lines as Line[] }); } catch { /* rewrite it */ }
  }
  try {
    const out = await generateJson<{ lines: Line[] }>([{ text: `שפה: ${lang || "לא ידוע"}\n\n${code}` }], SCHEMA, SYSTEM);
    const lines = (out.lines ?? []).filter((l) => l.code.trim() && l.he.trim());
    if (lines.length) {
      await store.upload(path, new Blob([JSON.stringify({ lines })], { type: "application/json" }), { upsert: true });
    }
    return Response.json({ lines });
  } catch (e) {
    const error = friendlyGeminiError(e);
    // Gemini out for now: not a failure of his - the page shows a quiet note instead of a red error.
    const later = /המכסה|עמוסים|RESOURCE_EXHAUSTED|UNAVAILABLE|429|503/.test(error);
    return Response.json({ error, later }, { status: 502 });
  }
}
