import type { SupabaseClient } from "@supabase/supabase-js";
import { generateJson } from "./gemini";

export type Term = { id: string; course_id: string; lesson_id: string | null; en: string; he: string; explanation: string | null };

const SCHEMA = {
  type: "object",
  properties: {
    items: {
      type: "array",
      items: {
        type: "object",
        properties: {
          lesson: { type: "integer" },
          en: { type: "string" },
          he: { type: "string" },
          explanation: { type: "string" },
        },
        required: ["lesson", "en", "he", "explanation"],
      },
    },
  },
  required: ["items"],
};

const PROMPT = `לפניך פרקי קריאה מקורס בהנדסת חשמל. הסטודנט לא חזק באנגלית, והמבחנים והשקפים כתובים הרבה פעמים באנגלית.
לכל פרק (לפי המספר שלו) הוצא 10-30 מונחים באנגלית שמופיעים בו או שהם המונח האנגלי המקובל למושג שנלמד בו.
en - המונח באנגלית; he - התרגום/המונח המקובל בעברית בהנדסת חשמל; explanation - משפט קצר בעברית מה זה אומר בקורס.
ודא שכל תרגום נכון ומקובל. אל תמציא מונחים שלא קשורים לחומר.`;

/** Builds the English word list for lessons written before chapters came with one (one Gemini call). */
export async function fillGlossary(sb: SupabaseClient, courseId: string) {
  const [{ data: lessons }, { data: have }] = await Promise.all([
    sb.from("lessons").select("id, title, chapter_md").eq("course_id", courseId).eq("status", "ready").order("created_at"),
    sb.from("glossary").select("lesson_id").eq("course_id", courseId),
  ]);
  const done = new Set((have ?? []).map((g) => g.lesson_id));
  const todo = (lessons ?? []).filter((l) => !done.has(l.id) && l.chapter_md).slice(0, 6);
  if (!todo.length) return 0;

  const text = todo.map((l, i) => `######## פרק ${i + 1}: ${l.title ?? ""}\n${l.chapter_md!.slice(0, 60_000)}`).join("\n\n");
  const out = await generateJson<{ items?: { lesson: number; en: string; he: string; explanation: string }[] }>(
    [{ text: PROMPT }, { text }], SCHEMA);
  const seen = new Set<string>();
  const rows = (out.items ?? []).filter((t) => {
    const key = `${t.lesson}|${t.en?.trim().toLowerCase()}`;
    if (!t.en?.trim() || !t.he?.trim() || !todo[t.lesson - 1] || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).map((t) => ({ course_id: courseId, lesson_id: todo[t.lesson - 1].id, en: t.en.trim(), he: t.he.trim(), explanation: t.explanation?.trim() || null }));
  if (rows.length) {
    const { error } = await sb.from("glossary").insert(rows);
    if (error) throw new Error(error.message);
  }
  return rows.length;
}
