import type { SupabaseClient } from "@supabase/supabase-js";
import type { Skill } from "./skills";

// Syllabus for his self-study track (digital design / RTL / SystemVerilog), written 22/10/2026.
// Order follows his own decision: first "what the flip-flop sees and when", then the gaps from his fundamentals test,
// then timing, SystemVerilog, verification, building blocks, interfaces (his Streaming Buffer project), the chip flow
// (his mentor is in back-end) and interview practice. Topics he already had keep their title, level and notes.
export type Module = { title: string; goal: string; topics: string[] };

export const VLSI_SYLLABUS: Module[] = [
  { title: "א. מה הדלגלג רואה ומתי", goal: "לחזות Q מגלי סימולציה, כולל איפוס - הבסיס לכל השאר", topics: [
    "שעון ועליית שעון (ציר זמן)",
    "דלגלג D בלי איפוס: חיזוי Q מגלי סימולציה",
    "איפוס סינכרוני",
    "איפוס אסינכרוני",
    "השוואה: איפוס סינכרוני מול אסינכרוני",
    "שחרור איפוס (reset release)",
    "Enable בדלגלג ואוגר (register) של כמה ביטים",
  ] },
  { title: "ב. לוגיקה צירופית - סגירת הפערים מהמבחן", goal: "לבנות ולנתח מעגלים בסיסיים בלי טעויות", topics: [
    "XOR",
    "מחבר מלא: הפרדה בין Sum ל-Carry",
    "Mux, Decoder ו-Priority encoder",
    "מחבר ripple-carry ולמה הוא איטי",
    "Glitches ו-hazards בלוגיקה צירופית",
  ] },
  { title: "ג. תזמון (Timing)", goal: "להבין מה מגביל את תדר השעון ואיך מתקנים", topics: [
    "עיכובים לאורך המסלול הקריטי",
    "Setup time, hold time ו-clock-to-Q",
    "תדר מקסימלי ממסלול קריטי",
    "תיקון הפרת setup: pipelining",
    "הפרת hold ולמה היא מסוכנת יותר",
    "Metastability וסנכרון בשני דלגלגים",
  ] },
  { title: "ד. SystemVerilog לתכנון (RTL)", goal: "לכתוב קוד שמסונתז לחומרה שהתכוונת אליה", topics: [
    "module, פורטים ו-logic",
    "assign מול always_comb",
    "always_ff והשמה non-blocking (<=)",
    "Blocking מול non-blocking - מה ההבדל בסימולציה",
    "Latch לא מכוון: איך נוצר ואיך נמנעים",
    "Parameters ווקטורים",
    "case, unique case ו-default",
  ] },
  { title: "ה. אימות (Verification) בסיסי", goal: "לבדוק את הקוד שלך בלי לסמוך על העין", topics: [
    "Testbench: שעון, איפוס וגירויים",
    "קריאת גלי סימולציה ב-EDA Playground",
    "Testbench שבודק את עצמו (self-checking)",
    "מודל ייחוס (reference model)",
    "Assertions בסיסיים (SVA)",
    "Coverage - מה זה ולמה זה חשוב",
  ] },
  { title: "ו. מכונות מצבים ואבני בניין", goal: "לתכנן בלוקים שחוזרים בכל שבב ובכל ראיון", topics: [
    "מכונת מצבים: Moore מול Mealy",
    "קידוד מכונת מצבים ב-SystemVerilog",
    "מונים (counters) ומחלקי תדר",
    "אוגר הזזה ו-LFSR",
    "זיהוי עלייה של אות (edge detector)",
    "Register file ו-ALU פשוט",
  ] },
  { title: "ז. ממשקים וזרימת נתונים (הפרויקט)", goal: "כל מה שצריך ל-Streaming Buffer", topics: [
    "Handshake של valid/ready",
    "Backpressure ו-skid buffer",
    "FIFO סינכרוני: מצביעים, full ו-empty",
    "FIFO אסינכרוני וקוד Gray (מושגים)",
    "Clock domain crossing (CDC) - מושגים",
  ] },
  { title: "ח. מ-RTL לשבב", goal: "להבין את התהליך שבו עובד המנטור (Back-End)", topics: [
    "סינתזה: מקוד לשערים",
    "Static timing analysis (STA)",
    "Place & Route ועץ שעון (clock tree)",
    "צריכת הספק ו-clock gating",
    "DFT ו-scan chain (מושגים)",
  ] },
  { title: "ט. הכנה לראיונות סטודנט", goal: "לפתור ולהסביר בקול שאלות קלאסיות", topics: [
    "שאלות קלאסיות: חלוקת שעון ב-2 וב-3",
    "שאלות קלאסיות: ספירת אחדים, בדיקת חזקה של 2",
    "להסביר את הפרויקט שלך ב-3 דקות",
  ] },
];

/** Puts the syllabus into his roadmap once: keeps existing topics (level, notes), adds the rest in order. */
export async function ensureSyllabus(sb: SupabaseClient, courseId: string, skills: Skill[], current: unknown) {
  if (Array.isArray(current) && current.length) return false;
  const topics = skills.filter((s) => s.kind === "topic");
  let ord = 0;
  const headers: string[] = [];
  const add = [];
  for (const m of VLSI_SYLLABUS) {
    headers.push(`${ord + 1}|${m.title}|${m.goal}`);
    for (const t of m.topics) {
      ord++;
      const have = topics.find((s) => s.title === t);
      if (have) await sb.from("skills").update({ ord }).eq("id", have.id);
      else add.push({ course_id: courseId, kind: "topic", ord, title: t, level: 0 });
    }
  }
  // Topics the tutor added along the way go after the syllabus.
  for (const extra of topics.filter((s) => !VLSI_SYLLABUS.some((m) => m.topics.includes(s.title)))) {
    await sb.from("skills").update({ ord: ++ord }).eq("id", extra.id);
  }
  if (add.length) await sb.from("skills").insert(add);
  await sb.from("courses").update({ syllabus_topics: headers }).eq("id", courseId);
  return true;
}

/** Module headers stored in courses.syllabus_topics as "firstOrd|title|goal". */
export function parseModules(raw: unknown) {
  return (Array.isArray(raw) ? raw : []).map((h) => String(h).split("|"))
    .filter((p) => p.length >= 2).map(([from, title, goal]) => ({ from: Number(from), title, goal: goal ?? "" }));
}
