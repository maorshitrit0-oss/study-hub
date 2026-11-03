/**
 * His guided 12-week VLSI program (approved 03/11/2026): two sessions a week - Friday morning and Saturday night -
 * each with its goal, set-up steps (free tools in the browser, nothing to install), what to learn with the tutor,
 * a hands-on task with what should come out, and interview questions. Built on the roadmap in vlsiSyllabus.ts
 * (topic names match it, so the tutor's level updates land on the right topics). The exam freeze (FREEZES) pauses it.
 */
export type Session = {
  week: number; n: 1 | 2; title: string; goal: string;
  setup?: string[];     // exact steps before starting
  learn: string[];      // roadmap topics for the tutor
  task: string;         // hands-on, with what should come out
  interview: string[];  // open questions to finish with
  cadence?: string;     // optional matching Cadence video chapter
};

const EDA = [
  "נכנסים ל-edaplayground.com ← Log in (למעלה מימין) ← Google. (פעם אחת)",
  "בצד שמאל: Languages & Libraries ← Testbench + Design: SystemVerilog/Verilog.",
  "Tools & Simulators: Icarus Verilog 12.0, ומסמנים ✓ Open EPWave after run (כדי לראות גרפים).",
  "יש שני חלונות: מימין design.sv (התכנון), משמאל testbench.sv (הבדיקה). מדביקים את הקוד שהמורה נותן.",
  "Run (למעלה) ← בתחתית מופיע הפלט, ונפתח חלון EPWave עם הגרפים. Save נותן קישור - מדביקים אותו למורה.",
];
const DIGITALJS = [
  "נכנסים ל-digitaljs.tilk.eu (בלי הרשמה).",
  "מדביקים את קוד ה-SystemVerilog בחלון, ולוחצים Synthesize and simulate!",
  "מופיע שרטוט השערים שהקוד הפך אליו. לחיצה על כניסה משנה אותה ל-0/1 ורואים את היציאה משתנה.",
];

export const VLSI_PROGRAM: Session[] = [
  { week: 1, n: 1, title: "שעון ודלגלג D", goal: "להבין מתי דלגלג 'רואה' את הכניסה ולחזות את Q מגרף",
    setup: EDA, learn: ["שעון ועליית שעון (ציר זמן)", "דלגלג D בלי איפוס: חיזוי Q מגלי סימולציה"],
    task: "מריצים ב-EDA Playground את הדלגלג שהמורה נותן. לפני ההרצה מציירים על דף את Q; אחרי - משווים לגרף ב-EPWave.",
    interview: ["מה ההבדל בין latch לדלגלג?", "למה הכניסה צריכה להיות יציבה סביב עליית השעון?"] },
  { week: 1, n: 2, title: "איפוס סינכרוני ואסינכרוני", goal: "לדעת לחזות Q עם איפוס משני הסוגים",
    learn: ["איפוס סינכרוני", "איפוס אסינכרוני", "השוואה: איפוס סינכרוני מול אסינכרוני", "שחרור איפוס (reset release)"],
    task: "משנים את הדלגלג משבוע 1 לאיפוס סינכרוני ואז לאסינכרוני, ורואים בגרף את ההבדל ברגע האיפוס.",
    interview: ["מתי עדיף איפוס אסינכרוני ומה הסכנה בשחרור שלו?", "צייר Q כשהאיפוס עולה באמצע מחזור."] },
  { week: 2, n: 1, title: "XOR ומחבר מלא", goal: "לבנות מחבר מלא ולהבין מאיפה Sum ומאיפה Carry",
    learn: ["XOR", "מחבר מלא: הפרדה בין Sum ל-Carry"],
    task: "קוד ראשון: מחבר מלא (full adder) ב-SystemVerilog, ובדיקה שמריצה את כל 8 הצירופים. בגרף: Sum ו-Carry לכל צירוף.",
    interview: ["כתוב את Sum ו-Carry של מחבר מלא בשערים.", "למה XOR נקרא 'מחבר בלי נשא'?"] },
  { week: 2, n: 2, title: "Mux, Decoder ומחבר ripple", goal: "לזהות אבני בניין צירופיות ולהבין למה ripple איטי",
    learn: ["Mux, Decoder ו-Priority encoder", "מחבר ripple-carry ולמה הוא איטי", "Glitches ו-hazards בלוגיקה צירופית"],
    task: "מחברים 4 מחברים מלאים למחבר של 4 ביטים ובודקים 5+3 ו-15+1. רואים בגרף את ה-Carry 'מתגלגל'.",
    interview: ["מה העיכוב של מחבר ripple של N ביטים?", "איך בונים Mux 4:1 מ-Mux 2:1?"] },
  { week: 3, n: 1, title: "SystemVerilog: module ו-assign", goal: "לקרוא ולכתוב מודול פשוט - כל שורה מובנת",
    learn: ["module, פורטים ו-logic", "assign מול always_comb"],
    task: "כותבים מחדש את ה-Mux בשתי דרכים (assign ו-always_comb) ומוודאים בבדיקה ששתיהן נותנות אותה תוצאה.",
    interview: ["מה ההבדל בין logic ל-wire?", "מתי משתמשים ב-always_comb ולא ב-assign?"],
    cadence: "SystemVerilog for Design and Verification - סקירה וטיפוסי נתונים" },
  { week: 3, n: 2, title: "always_ff ו-<= מול =", goal: "לכתוב אוגר נכון ולהבין למה non-blocking",
    learn: ["always_ff והשמה non-blocking (<=)", "Blocking מול non-blocking - מה ההבדל בסימולציה"],
    task: "אוגר של 8 ביטים עם איפוס ו-enable. אחר כך מחליפים <= ב-= בשרשרת של שני אוגרים ורואים בגרף מה נשבר.",
    interview: ["מה יקרה אם נשתמש ב-= בתוך always_ff של שרשרת אוגרים?", "מה ההבדל בין blocking ל-non-blocking?"],
    cadence: "SystemVerilog for Design and Verification - בלוקים פרוצדורליים" },
  { week: 4, n: 1, title: "Latch בטעות, parameters ו-case", goal: "לכתוב קוד שלא מייצר חומרה שלא התכוונת אליה",
    learn: ["Latch לא מכוון: איך נוצר ואיך נמנעים", "Parameters ווקטורים", "case, unique case ו-default"],
    task: "כותבים decoder עם case בלי default, ואז עם default - ומשווים (במפגש הבא נראה את ה-latch בשרטוט).",
    interview: ["איך נוצר latch לא מכוון ואיך מונעים אותו?", "מה עושה unique case?"] },
  { week: 4, n: 2, title: "למה הקוד הופך: שערים אמיתיים", goal: "לראות את החומרה שהקוד שלך מייצר",
    setup: DIGITALJS, learn: ["Latch לא מכוון: איך נוצר ואיך נמנעים"],
    task: "מדביקים ב-DigitalJS את המחבר, ה-Mux וה-decoder בלי default - ורואים איפה מופיע ה-latch.",
    interview: ["מה סינתזה עושה עם if בלי else בתוך always_comb?"] },
  { week: 5, n: 1, title: "Testbench: שעון, איפוס וגירויים", goal: "לבדוק קוד בלי לסמוך על העין",
    setup: EDA, learn: ["Testbench: שעון, איפוס וגירויים", "קריאת גלי סימולציה ב-EDA Playground"],
    task: "testbench למחבר של 4 ביטים: שעון, איפוס, ולולאה על כל הכניסות. מדביקים למורה את הקישור.",
    interview: ["מה חייב להיות ב-testbench בסיסי?", "איך יוצרים שעון בסימולציה?"],
    cadence: "Xcelium Simulator - מה סימולטור עושה (רשות)" },
  { week: 5, n: 2, title: "בדיקה שבודקת את עצמה", goal: "שהבדיקה תגיד לבד PASS או FAIL",
    learn: ["Testbench שבודק את עצמו (self-checking)", "מודל ייחוס (reference model)", "Assertions בסיסיים (SVA)"],
    task: "מוסיפים לבדיקה השוואה למודל ייחוס (a+b) ו-$error על כל אי-התאמה. מכניסים באג בכוונה ורואים שהבדיקה תופסת.",
    interview: ["מה זה self-checking testbench ולמה זה עדיף?", "מה זה assertion?"] },
  { week: 6, n: 1, title: "מכונות מצבים: Moore ו-Mealy", goal: "לתכנן מכונת מצבים מתרשים",
    learn: ["מכונת מצבים: Moore מול Mealy", "קידוד מכונת מצבים ב-SystemVerilog"],
    task: "מכונת מצבים של רמזור (אדום ← ירוק ← צהוב) עם מונה זמן, ובדיקה שמראה את המעברים בגרף.",
    interview: ["מה ההבדל בין Moore ל-Mealy, ואיזה מגיב מהר יותר?", "צייר FSM שמזהה את הרצף 101."] },
  { week: 6, n: 2, title: "מונים ומחלקי תדר", goal: "לבנות מונה ולחלק שעון",
    learn: ["מונים (counters) ומחלקי תדר"],
    task: "מונה 0-9 עם איפוס, ומחלק תדר ב-2 וב-4. בגרף: היציאה בחצי ובשליש מקצב השעון.",
    interview: ["איך מחלקים שעון ב-2? וב-3 עם duty cycle של 50%?"] },
  { week: 7, n: 1, title: "אוגר הזזה, LFSR וזיהוי עלייה", goal: "להכיר אבני בניין שחוזרות בכל ראיון",
    learn: ["אוגר הזזה ו-LFSR", "זיהוי עלייה של אות (edge detector)"],
    task: "אוגר הזזה של 8 ביטים, LFSR של 4 ביטים (רואים את 15 המצבים), ו-edge detector שמוציא פולס אחד.",
    interview: ["כתוב edge detector בשני דלגלגים.", "למה LFSR של 4 ביטים עובר רק 15 מצבים?"] },
  { week: 7, n: 2, title: "ALU קטן", goal: "לחבר הכל לבלוק אחד עם בדיקה",
    learn: ["Register file ו-ALU פשוט"],
    task: "ALU של 4 פעולות (חיבור, חיסור, AND, OR) עם בדיקה מול מודל ייחוס לכל פעולה.",
    interview: ["איך מזהים overflow בחיבור עם סימן?"] },
  { week: 8, n: 1, title: "תזמון: setup, hold ותדר מקסימלי", goal: "לחשב את התדר המקסימלי של מעגל",
    learn: ["עיכובים לאורך המסלול הקריטי", "Setup time, hold time ו-clock-to-Q", "תדר מקסימלי ממסלול קריטי"],
    task: "תרגיל חישוב עם המורה: נתונים clk-to-Q, עיכוב לוגיקה ו-setup - מחשבים תדר מקסימלי, ובודקים הפרת hold.",
    interview: ["כתוב את משוואת ה-setup ואת משוואת ה-hold.", "מה עושים אם יש הפרת hold?"] },
  { week: 8, n: 2, title: "Pipelining ו-metastability", goal: "לתקן מסלול איטי ולסנכרן אות חיצוני",
    learn: ["תיקון הפרת setup: pipelining", "הפרת hold ולמה היא מסוכנת יותר", "Metastability וסנכרון בשני דלגלגים"],
    task: "מכניסים שלב pipeline למחבר ארוך, ובונים synchronizer של שני דלגלגים לאות כניסה.",
    interview: ["מה זה metastability ולמה שני דלגלגים עוזרים?", "מה המחיר של pipelining?"] },
  { week: 9, n: 1, title: "valid/ready - תחילת הפרויקט", goal: "להבין איך בלוקים מעבירים נתונים בלי לאבד אותם",
    learn: ["Handshake של valid/ready", "Backpressure ו-skid buffer"],
    task: "הפרויקט (Streaming Buffer): ממשק valid/ready בסיסי ובדיקה שמראה העברה, המתנה (ready=0) והמשך.",
    interview: ["מתי מתבצעת העברה ב-valid/ready?", "למה valid לא יכול לחכות ל-ready?"] },
  { week: 9, n: 2, title: "FIFO סינכרוני", goal: "לבנות FIFO עם full ו-empty נכונים",
    learn: ["FIFO סינכרוני: מצביעים, full ו-empty"],
    task: "FIFO של 8 מקומות: כתיבה, קריאה, full, empty, ובדיקה שממלאת עד הסוף ומרוקנת.",
    interview: ["איך יודעים ש-FIFO מלא ולא ריק כשהמצביעים שווים?"] },
  { week: 10, n: 1, title: "FIFO אסינכרוני וקוד Gray", goal: "להבין איך עוברים בין שני שעונים",
    learn: ["FIFO אסינכרוני וקוד Gray (מושגים)", "Clock domain crossing (CDC) - מושגים"],
    task: "ממירים מונה בינארי לקוד Gray ובחזרה, ומסבירים למורה למה זה חשוב במעבר בין שעונים.",
    interview: ["למה משתמשים בקוד Gray במצביעים של FIFO אסינכרוני?"] },
  { week: 10, n: 2, title: "סיום הפרויקט", goal: "Streaming Buffer עובד ונבדק",
    learn: ["Backpressure ו-skid buffer", "Coverage - מה זה ולמה זה חשוב"],
    task: "מחברים FIFO + valid/ready לפרויקט שלם, ובדיקה אקראית עם backpressure. הקישור נשמר להצגה בראיון.",
    interview: ["מה הבדיקה שלך מכסה, ומה עוד לא?"] },
  { week: 11, n: 1, title: "סינתזה ו-STA", goal: "להבין מה קורה לקוד בדרך לשבב",
    setup: DIGITALJS, learn: ["סינתזה: מקוד לשערים", "Static timing analysis (STA)"],
    task: "מסנתזים את ה-FIFO ב-DigitalJS ורואים את השערים; עם המורה קוראים דוח תזמון לדוגמה (slack).",
    interview: ["מה זה slack שלילי ואיך מתקנים?"],
    cadence: "Genus Synthesis - מה זה סינתזה (רשות)" },
  { week: 11, n: 2, title: "מקוד לשבב: Place & Route", goal: "לראות את הפרויקט שלך כשבב",
    setup: ["המורה נותן במפגש קישור למחברת Google Colab מוכנה של OpenLane (חינם, בלי התקנה).",
      "ב-Colab: Runtime ← Run all, ומחכים כמה דקות.", "בסוף מופיעה תמונה של השבב (layout) ודוחות שטח ותזמון."],
    learn: ["Place & Route ועץ שעון (clock tree)", "צריכת הספק ו-clock gating", "DFT ו-scan chain (מושגים)"],
    task: "מריצים את ה-FIFO שלך עד layout, ומסבירים במילים מה כל שלב עשה (סינתזה, מיקום, חיווט, עץ שעון).",
    interview: ["מה השלבים מ-RTL ל-GDS?", "למה צריך עץ שעון?"] },
  { week: 12, n: 1, title: "שאלות ראיון קלאסיות", goal: "לפתור ולהסביר בקול שאלות שחוזרות",
    learn: ["שאלות קלאסיות: חלוקת שעון ב-2 וב-3", "שאלות קלאסיות: ספירת אחדים, בדיקת חזקה של 2"],
    task: "פותרים עם המורה 4 שאלות ראיון בקול (כמו בראיון אמיתי), וכותבים קוד לשתיים מהן ב-EDA Playground.",
    interview: ["חלק שעון ב-3 עם 50% duty cycle.", "בדוק אם מספר הוא חזקה של 2 בשורה אחת."] },
  { week: 12, n: 2, title: "ראיון דמה", goal: "להציג את הפרויקט ולעמוד בראיון",
    learn: ["להסביר את הפרויקט שלך ב-3 דקות"],
    task: "ראיון דמה מלא עם המורה: הצגת הפרויקט ב-3 דקות, ואז שאלות טכניות. בסוף - משוב ומה לשפר.",
    interview: ["ספר על פרויקט שעשית ועל באג שמצאת בו."] },
];

const DAY_MS = 864e5;
export const PROGRAM_START = "2026-11-06"; // the first Friday
const iso = (t: number) => new Date(t).toISOString().slice(0, 10);

/** Session dates: Friday (n=1) and the next day, Saturday night (n=2), week after week; frozen weeks skipped. */
export function sessionDates(freezes: { from: string; to: string }[]) {
  const out: string[] = [];
  let friday = Date.parse(`${PROGRAM_START}T12:00:00Z`);
  while (out.length < VLSI_PROGRAM.length) {
    const fri = iso(friday), sat = iso(friday + DAY_MS);
    if (!freezes.some((f) => (fri >= f.from && fri <= f.to) || (sat >= f.from && sat <= f.to))) out.push(fri, sat);
    friday += 7 * DAY_MS;
  }
  return out;
}

export const sessionKey = (s: Pick<Session, "week" | "n">) => `${s.week}-${s.n}`;

/** What the tutor is told when a session starts (the chat opens with it). */
export function sessionPrompt(s: Session) {
  return [
    `מפגש שבוע ${s.week} · חלק ${s.n}: ${s.title}.`,
    `המטרה: ${s.goal}.`,
    `הנושאים מהמפה: ${s.learn.join("; ")}.`,
    `המשימה המעשית בסוף: ${s.task}`,
    `שאלות ראיון לסיום: ${s.interview.join(" | ")}`,
    "תלמד אותי לפי הכללים שלי: לאט, עם דוגמאות, כל שורת קוד מוסברת, ושאלות פתוחות. תתחיל.",
  ].join("\n");
}
