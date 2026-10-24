import type { SupabaseClient } from "@supabase/supabase-js";
import type { Module } from "./vlsiSyllabus";

// Three self-study tracks that follow Cadence online courses he has access to (24/10/2026). The syllabi come from
// Cadence's public course descriptions (82143, 86220, 86218); the videos themselves are his, in English - the tutor
// teaches the same topics in Hebrew and explains screenshots he sends. Claude never logs into his Cadence account.

const RULES = `איך ללמד אותי (חובה):
• בעברית ומהבסיס; מונחים ופקודות באנגלית. לא להניח שאני מכיר מושג.
• כל נושא בסדר הזה: רקע (למה זה קיים, איזו בעיה זה פותר) ← 🏠 דוגמה מחיי היום-יום ← ההגדרה ← דוגמת קוד/פקודה קצרה ← שאלה אמריקאית אחת עם 4 אפשרויות.
• לחכות לתשובה שלי, לבקש נימוק, ואם טעיתי - להסביר מאיפה הטעות.
• לאט: מושג חדש אחד בכל פעם. אם לא הבנתי - דוגמה אחרת מהחיים, לא אותו הסבר שוב.
• בלי מחמאות אוטומטיות. לא להמציא פקודות, אופציות או תוצאות של כלי - אם לא בטוח, להגיד.
• אני רואה את סרטוני הקורס באנגלית: כשאני שולח צילום שקף או מסך - לתרגם לעברית ולהסביר אותו.`;

export const CADENCE_TRACKS: { name: string; notes: string; modules: Module[] }[] = [
  {
    name: "Cadence · SystemVerilog for Design and Verification",
    notes: `מסלול לפי קורס Cadence "SystemVerilog for Design and Verification" (גרסה 25.03). חלק תכנון (RTL וסינתזה) וחלק אימות (מחלקות, אקראיות מאולצת, כיסוי, assertions).
כלים: אין לי Xcelium מותקן - לתרגול להשתמש ב-EDA Playground (יש בו סימולטור Cadence Xcelium).

${RULES}`,
    modules: [
      { title: "א. סקירה וטיפוסי נתונים", goal: "להבין במה SystemVerilog שונה מ-Verilog ואיזה טיפוס לבחור", topics: [
        "מה זה SystemVerilog ולמה צריך אותה",
        "logic מול wire ו-reg",
        "טיפוסים של 2 ו-4 מצבים (bit מול logic, הערך X)",
        "ליטרלים: מספרים בגודל מוגדר, '0 ו-'1",
        "enum ו-typedef",
        "struct ו-packed struct",
      ] },
      { title: "ב. בלוקים פרוצדורליים, פקודות ואופרטורים", goal: "לכתוב התנהגות שמסונתזת למה שהתכוונת", topics: [
        "always_comb, always_ff ו-always_latch",
        "השמה חוסמת (=) מול לא-חוסמת (<=)",
        "if, case, unique ו-priority",
        "אופרטורים: inside, ==?, הפחתה (reduction), ++",
        "לולאות: for, foreach, repeat",
      ] },
      { title: "ג. היררכיה וחיבוריות", goal: "לחבר מודולים בלי טעויות חיווט", topics: [
        "מופע מודול: חיבור לפי שם, .name ו-.*",
        "interface - חיבור קבוצת אותות אחת",
        "modport",
        "package ו-import",
      ] },
      { title: "ד. מערכים, משימות ופונקציות", goal: "לנהל נתונים בבדיקות ובתכנון", topics: [
        "מערכים packed ו-unpacked",
        "מערך דינמי ו-queue",
        "מערך אסוציאטיבי",
        "task מול function, ו-automatic",
      ] },
      { title: "ה. אימות: מחלקות ואקראיות", goal: "לבנות סביבת בדיקה שמייצרת בדיקות לבד", topics: [
        "class ו-object (תכנות מונחה עצמים בבדיקות)",
        "ירושה ו-virtual methods",
        "rand ו-constraint (אקראיות מאולצת)",
        "fork/join, mailbox ו-semaphore",
        "clocking block",
      ] },
      { title: "ו. כיסוי ו-assertions", goal: "לדעת מה נבדק ולתפוס באגים ברגע שהם קורים", topics: [
        "covergroup, coverpoint ו-cross",
        "immediate assertions",
        "concurrent assertions: sequence ו-property",
      ] },
    ],
  },
  {
    name: "Cadence · Genus Synthesis (Stylus Common UI)",
    notes: `מסלול לפי קורס Cadence "Genus Synthesis Solution with Stylus Common UI" (גרסה 25.1): זרימת הסינתזה, אילוצים, MMMC, ניתוח תזמון, סינתזה פיזית, הספק נמוך, DFT ובדיקת שקילות.
כלים: אין לי Genus. ללמוד את המושגים והפקודות; לתרגול סינתזה בחינם אפשר להראות ב-EDA Playground (Yosys), ולציין מה שונה ב-Genus.

${RULES}`,
    modules: [
      { title: "א. מה זה סינתזה", goal: "להבין מה קורה לקוד RTL בדרך לשבב", topics: [
        "סינתזה: מקוד RTL לשערים",
        "ספריית טכנולוגיה (liberty, .lib) ותאים סטנדרטיים",
        "זרימת Genus: read_libs, read_hdl, elaborate",
        "syn_generic, syn_map ו-syn_opt",
      ] },
      { title: "ב. העבודה ב-Genus (Stylus Common UI)", goal: "להתמצא בכלי", topics: [
        "Genus shell ופקודות Stylus (get_db, set_db)",
        "ניווט בהיררכיית התכנון",
        "סיור ב-GUI",
      ] },
      { title: "ג. אילוצים ותזמון", goal: "להגיד לכלי מה המהירות הנדרשת", topics: [
        "SDC: create_clock",
        "set_input_delay ו-set_output_delay",
        "false path ו-multicycle path",
        "MMMC: מצבי עבודה (modes) ופינות (corners)",
        "report_timing: slack ומסלול קריטי",
      ] },
      { title: "ד. תוצאות ואופטימיזציה", goal: "לקרוא דוחות ולשפר זמן, שטח והספק", topics: [
        "report_area, report_power ואיכות התוצאה (QoR)",
        "סינתזת datapath",
        "עריכת netlist וקיצור זמן ריצה",
        "דיבוג בעיות סינתזה נפוצות",
      ] },
      { title: "ה. מעבר לסינתזה הבסיסית", goal: "להכיר את מה שמחבר את הסינתזה לשאר זרימת השבב", topics: [
        "סינתזה פיזית (מושגים)",
        "הספק נמוך: clock gating ו-multi-Vt",
        "DFT: scan chain ואילוצי בדיקה",
        "בדיקת שקילות (Conformal LEC) ויציאה ל-place & route",
      ] },
    ],
  },
  {
    name: "Cadence · Xcelium Simulator",
    notes: `מסלול לפי קורס Cadence "Xcelium Simulator" (גרסה 26.03): הרצה עם xrun, דיבוג וגלים, סימולציה מרובת ליבות, גלאי race, ובעיות X (x-propagation ו-x-pessimism).
כלים: ב-EDA Playground אפשר לבחור Cadence Xcelium ולהריץ דוגמאות קטנות.

${RULES}`,
    modules: [
      { title: "א. מה סימולטור עושה", goal: "להבין את שלבי ההרצה", topics: [
        "מה זה סימולציה ולמה בודקים לפני ייצור",
        "קומפילציה, elaboration וסימולציה",
        "xrun: הרצה בפקודה אחת",
      ] },
      { title: "ב. xrun בפועל", goal: "להריץ פרויקט אמיתי מהשורה", topics: [
        "אופציות נפוצות: -top, -f, +define+, -timescale",
        "-access והרשאות דיבוג",
        "ספריות ו-snapshot",
      ] },
      { title: "ג. דיבוג", goal: "למצוא באג מהר", topics: [
        "גלים (waveforms) ו-probes",
        "דיבוג בקוד המקור ו-Verisium Debug",
        "ממשק שורת הפקודה (Tcl): run, stop, value",
      ] },
      { title: "ד. בעיות מתקדמות", goal: "להבין באגים שקשה לראות", topics: [
        "race conditions וגלאי ה-race",
        "x-propagation: איך X מתפשט",
        "x-pessimism ופתרונות",
        "סימולציה מרובת ליבות (multi-core)",
      ] },
    ],
  },
];

/** Creates the Cadence tracks once (with their syllabus) for his account. */
export async function ensureCadenceTracks(sb: SupabaseClient, existing: string[]) {
  let made = 0;
  for (const t of CADENCE_TRACKS) {
    if (existing.includes(t.name)) continue;
    let ord = 0;
    const headers: string[] = [];
    const topics: string[] = [];
    for (const m of t.modules) {
      headers.push(`${ord + 1}|${m.title}|${m.goal}`);
      for (const title of m.topics) { ord++; topics.push(title); }
    }
    const { data } = await sb.from("courses").insert({ name: t.name, kind: "self", notes: t.notes, syllabus_topics: headers }).select("id").single();
    if (!data) continue;
    await sb.from("skills").insert(topics.map((title, i) => ({ course_id: data.id, kind: "topic", ord: i + 1, title, level: 0 })));
    made++;
  }
  return made;
}
