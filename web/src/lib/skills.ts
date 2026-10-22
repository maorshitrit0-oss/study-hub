import type { SupabaseClient } from "@supabase/supabase-js";

export type Skill = {
  id: string; course_id: string; kind: "topic" | "project"; ord: number; title: string;
  level: number; notes: string | null; updated_at: string;
};

/** The four levels he measures himself by (0 = not started). */
export const LEVELS = ["עוד לא התחלתי", "נחשפתי", "פותר עם הכוונה", "פותר ומסביר לבד", "מיישם ומדבג במקרה חדש"];
export const PROJECT_LEVELS = ["לא התחלתי", "התחלתי", "באמצע", "עובד", "נבדק ומוכן להצגה"];
export const LEVEL_TONE = ["bg-bg text-muted", "bg-bad-soft text-bad", "bg-warn-soft text-warn", "bg-good-soft text-good", "bg-accent text-white"];

/** Exam weeks: no new development (from his plan). */
export const FREEZES = [{ from: "2027-01-10", to: "2027-01-25", text: "תקופת מבחנים (10-25 בינואר): אין פיתוח חדש, רק חזרות קצרות" }];

/**
 * The tutor ends a turn with lines like "📈 התקדמות: <נושא> → 3 | <הערה>"; apply them to the roadmap.
 * Returns what changed, for the reply's footer.
 */
export async function applyProgress(sb: SupabaseClient, courseId: string, reply: string) {
  const lines = [...reply.matchAll(/📈\s*התקדמות:\s*(.+?)\s*(?:→|->|=)\s*(?:רמה\s*)?([0-4])\s*(?:\|\s*(.+))?$/gm)];
  if (!lines.length) return 0;
  const { data } = await sb.from("skills").select("*").eq("course_id", courseId);
  const skills = (data ?? []) as Skill[];
  const norm = (s: string) => s.replace(/[*_`"']/g, "").trim();
  let n = 0;
  for (const [, rawTitle, lvl, note] of lines) {
    const title = norm(rawTitle);
    const s = skills.find((x) => norm(x.title) === title) ?? skills.find((x) => norm(x.title).includes(title) || title.includes(norm(x.title)));
    if (!s) continue;
    const date = new Intl.DateTimeFormat("he-IL", { timeZone: "Asia/Jerusalem", day: "2-digit", month: "2-digit" }).format(new Date());
    const notes = note ? `${s.notes ? `${s.notes}\n` : ""}${date}: ${note.trim()}` : s.notes;
    await sb.from("skills").update({ level: Number(lvl), notes, updated_at: new Date().toISOString() }).eq("id", s.id);
    n++;
  }
  return n;
}

/** Text block describing the roadmap for the tutor's context. */
export function roadmapText(skills: Skill[]) {
  const part = (kind: Skill["kind"], names: string[]) => skills.filter((s) => s.kind === kind).sort((a, b) => a.ord - b.ord)
    .map((s) => `${s.ord}. ${s.title} - רמה ${s.level} (${names[s.level]})${s.notes ? `\n   הערות: ${s.notes.replace(/\n/g, " / ")}` : ""}`).join("\n");
  return `מפת הלימוד (לפי הסדר):\n${part("topic", LEVELS)}\n\nשלבי הפרויקט:\n${part("project", PROJECT_LEVELS)}`;
}

/** Sunday of this week (YYYY-MM-DD), and today; the week starts on Sunday in Israel. */
export function weekDates() {
  const now = new Date();
  return {
    weekStart: new Date(now.getTime() - now.getDay() * 864e5).toISOString().slice(0, 10),
    today: now.toISOString().slice(0, 10),
  };
}
