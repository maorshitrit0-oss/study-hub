/**
 * His guided 12-week VLSI program (approved 03/11/2026): two sessions a week - Friday morning and Saturday night -
 * each with its goal, set-up steps (free tools in the browser, nothing to install), what to learn with the tutor,
 * a hands-on task with what should come out, and interview questions. Built on the roadmap in vlsiSyllabus.ts
 * (topic names match it, so the tutor's level updates land on the right topics). The exam freeze (FREEZES) pauses it.
 */
/** An interview question and the page it comes from (found and checked 03/11/2026 - nothing invented). */
export type Interview = { q: string; src: string; url: string };

export type Session = {
  week: number; n: 1 | 2; title: string; goal: string;
  setup?: string[];     // exact steps before starting
  learn: string[];      // roadmap topics for the tutor
  task: string;         // hands-on, with what should come out
  interview: Interview[]; // open questions to finish with, each from a real page he can open
  board?: string;       // "🔧 על הלוח": this session's step of the CV project on his Artix-7 board
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

/**
 * The CV project built along the 12 weeks on his board (approved 04/11/2026): a "Mini-TPU" - a systolic array of
 * int8 multiply-accumulate units running a small neural network that tells drone sound from other sound, clips sent
 * from the PC over UART. Aimed at NVIDIA / Google / Amazon / Apple / Intel / Marvell (AI accelerators) and Elbit /
 * Rafael (real-time signal processing on FPGA). Each session adds one piece ("board").
 */
export const PROJECT = "Mini-TPU: מאיץ AI בחומרה (מערך סיסטולי של יחידות MAC ב-int8) שמזהה רחפנים לפי קול - על לוח PuZhi PA35T-EDU (Artix-7 XC7A35T)";

/** His board (PuZhi PA35T-EDU manual V1.0); the full pin file is fpga/pa35t_edu.xdc in the repository. */
export const BOARD_PINS = [
  "שבב: xc7a35tfgg484-2. שעון: 200MHz דיפרנציאלי R4/T4 (צריך IBUFDS). כפתור reset: R14.",
  "6 לדים (דולקים ב-1): J21 J19 H19 K18 K19 L19. 3 כפתורים (0 כשלוחצים): W21 Y21 U21. 16 מתגים: H13 G13 G15 G16 J14 H14 G17 G18 J15 H15 H17 H18 J22 H22 H20 G20.",
  "UART (CH340, Type-C): FPGA_TX=P15, FPGA_RX=P14. שתי תצוגות של 4 ספרות (7-segment): מקטעים a-g,dp ובחירת ספרה - בקובץ הפינים.",
];
const PINS_URL = "https://github.com/maorshitrit0-oss/study-hub/blob/main/fpga/pa35t_edu.xdc";

/** Installing Vivado once (session 1) - free, no license for Artix-7. */
const VIVADO = [
  "נרשמים בחינם ל-AMD ב-account.amd.com (שם ומייל אמיתיים).",
  "מורידים מ-xilinx.com/support/download.html את AMD Unified Installer (Windows Self Extracting Web Installer), הגרסה החדשה.",
  "בהתקנה: Vivado ← Vivado ML Standard (חינם) ← Devices: רק Artix-7 ← להשאיר מסומן Install Cable Drivers ← תיקייה C:\\Xilinx (בלי עברית ובלי OneDrive). צריך כ-60GB פנויים.",
  "פרויקט: Create Project ← שם mini_tpu בתיקייה C:\\fpga ← RTL Project ← Part: xc7a35tfgg484-2.",
  `מורידים את קובץ הפינים מ-${PINS_URL} (Download raw file) ומוסיפים: Add Sources ← Add or create constraints.`,
  "צריבה כל פעם: Generate Bitstream ← Open Hardware Manager ← Open Target ← Auto Connect ← Program Device. הלוח מחובר ב-Type-C ליציאת ה-JTAG.",
];

export const VLSI_PROGRAM: Session[] = [
  { week: 1, n: 1, title: "שעון ודלגלג D", goal: "להבין מתי דלגלג 'רואה' את הכניסה ולחזות את Q מגרף",
    setup: [...VIVADO, ...EDA], learn: ["שעון ועליית שעון (ציר זמן)", "דלגלג D בלי איפוס: חיזוי Q מגלי סימולציה"],
    task: "מריצים ב-EDA Playground את הדלגלג שהמורה נותן. לפני ההרצה מציירים על דף את Q; אחרי - משווים לגרף ב-EPWave.",
    board: "התקנת Vivado ופרויקט mini_tpu, ואז 'שלום עולם' של FPGA: מונה של 27 ביט על שעון ה-200MHz מהבהב את LED1 בערך פעם בשנייה. מבינים למה צריך מונה כדי לראות משהו בעין.",
    interview: [{ q: "מה ההבדל בין latch לדלגלג?", src: "Glassdoor - שאלה מראיון", url: "https://clear.glassdoor.nl/Interview/What-is-the-difference-between-a-latch-and-a-flip-flop-QTN_8893168.htm" }, { q: "מה זה setup time ו-hold time, ולמה הכניסה צריכה להיות יציבה סביב עליית השעון?", src: "Futurense - שאלות ראיון VLSI", url: "https://futurense.com/blog/vlsi-design-interview-questions" }] },
  { week: 1, n: 2, title: "איפוס סינכרוני ואסינכרוני", goal: "לדעת לחזות Q עם איפוס משני הסוגים",
    learn: ["איפוס סינכרוני", "איפוס אסינכרוני", "השוואה: איפוס סינכרוני מול אסינכרוני", "שחרור איפוס (reset release)"],
    task: "משנים את הדלגלג משבוע 1 לאיפוס סינכרוני ואז לאסינכרוני, ורואים בגרף את ההבדל ברגע האיפוס.",
    board: "מוסיפים את כפתור ה-reset (R14) לאיפוס המונה: פעם סינכרוני ופעם אסינכרוני, ורואים על הלוח שהנורה נעצרת.",
    interview: [{ q: "מה ההבדל בין איפוס סינכרוני לאסינכרוני?", src: "Glassdoor - שאלה מראיון ב-Cerium Systems", url: "https://www.glassdoor.com/Interview/What-is-the-difference-between-Synchronous-and-Asynchronous-Reset-QTN_4962603.htm" }, { q: "למה משחררים איפוס אסינכרוני בצורה סינכרונית (async assert, sync de-assert)?", src: "Altera Community - דיון", url: "https://community.altera.com/discussions/fpga-device/reset-query/75108/replies/75113" }] },
  { week: 2, n: 1, title: "XOR ומחבר מלא", goal: "לבנות מחבר מלא ולהבין מאיפה Sum ומאיפה Carry",
    learn: ["XOR", "מחבר מלא: הפרדה בין Sum ל-Carry"],
    task: "קוד ראשון: מחבר מלא (full adder) ב-SystemVerilog, ובדיקה שמריצה את כל 8 הצירופים. בגרף: Sum ו-Carry לכל צירוף.",
    board: "מחבר מלא על הלוח: SW1-SW3 הם A, B, Cin; LED1=Sum, LED2=Carry. בודקים את כל 8 הצירופים במתגים מול טבלת האמת.",
    interview: [{ q: "כתוב את Sum ו-Carry של מחבר מלא בשערים.", src: "ChipVerify - הסבר", url: "https://chipverify.com/digital-fundamentals/digital-full-adder-circuit" }] },
  { week: 2, n: 2, title: "Mux, Decoder ומחבר ripple", goal: "לזהות אבני בניין צירופיות ולהבין למה ripple איטי",
    learn: ["Mux, Decoder ו-Priority encoder", "מחבר ripple-carry ולמה הוא איטי", "Glitches ו-hazards בלוגיקה צירופית"],
    task: "מחברים 4 מחברים מלאים למחבר של 4 ביטים ובודקים 5+3 ו-15+1. רואים בגרף את ה-Carry 'מתגלגל'.",
    board: "מחבר של 4 ביטים: SW1-4 ועוד SW5-8, התוצאה (5 ביטים) על הלדים. זה החיבור שבתוך יחידת ה-MAC של הפרויקט.",
    interview: [{ q: "מה העיכוב של מחבר ripple של N ביטים?", src: "Virtual Labs IIT Kharagpur - הסבר", url: "https://coa-iitkgp.vlabs.ac.in/exp/ripple-carry-adder/theory.html" }, { q: "איך בונים Mux 4:1 מ-Mux 2:1?", src: "AmbitionBox - שאלות ראיון RTL Design Engineer", url: "https://www.ambitionbox.com/profiles/rtl-design-engineer/interview-questions/fresher-candidates" }] },
  { week: 3, n: 1, title: "SystemVerilog: module ו-assign", goal: "לקרוא ולכתוב מודול פשוט - כל שורה מובנת",
    learn: ["module, פורטים ו-logic", "assign מול always_comb"],
    task: "כותבים מחדש את ה-Mux בשתי דרכים (assign ו-always_comb) ומוודאים בבדיקה ששתיהן נותנות אותה תוצאה.",
    board: "מפענח 7-segment: ספרה הקסדצימלית מהמתגים על ספרה אחת בתצוגה. קודם מגלים את הקוטביות (מדליקים הכל ב-0 ואז ב-1).",
    interview: [{ q: "מה ההבדל בין logic ל-wire?", src: "ChipVerify - הסבר", url: "https://chipverify.com/systemverilog/systemverilog-data-type-logic" }, { q: "מתי משתמשים ב-always_comb ולא ב-assign?", src: "Verification Academy - דיון", url: "https://verificationacademy.com/forums/t/continuous-assignment-vs-always-comb/32792" }],
    cadence: "SystemVerilog for Design and Verification - סקירה וטיפוסי נתונים" },
  { week: 3, n: 2, title: "always_ff ו-<= מול =", goal: "לכתוב אוגר נכון ולהבין למה non-blocking",
    learn: ["always_ff והשמה non-blocking (<=)", "Blocking מול non-blocking - מה ההבדל בסימולציה"],
    task: "אוגר של 8 ביטים עם איפוס ו-enable. אחר כך מחליפים <= ב-= בשרשרת של שני אוגרים ורואים בגרף מה נשבר.",
    board: "אוגר עם enable: לחיצה על KEY1 שומרת את ערך המתגים, והוא נשאר בתצוגה. (זה האוגר שיחזיק את המשקלים במאיץ.)",
    interview: [{ q: "מה ההבדל בין blocking ל-non-blocking?", src: "Glassdoor - שאלה מראיון ב-Intel", url: "https://www.glassdoor.com.au/Interview/In-Verilog-what-is-the-difference-between-a-blocking-and-non-blocking-statement-QTN_188714.htm" }, { q: "מה יקרה אם נשתמש ב-= בתוך always של שרשרת אוגרים (race)?", src: "VLSI Web - שאלות ראיון Verilog", url: "https://vlsiweb.com/verilog-hdl-interview-questions/" }],
    cadence: "SystemVerilog for Design and Verification - בלוקים פרוצדורליים" },
  { week: 4, n: 1, title: "Latch בטעות, parameters ו-case", goal: "לכתוב קוד שלא מייצר חומרה שלא התכוונת אליה",
    learn: ["Latch לא מכוון: איך נוצר ואיך נמנעים", "Parameters ווקטורים", "case, unique case ו-default"],
    task: "כותבים decoder עם case בלי default, ואז עם default - ומשווים (במפגש הבא נראה את ה-latch בשרטוט).",
    board: "מנהל תצוגה לכל 8 הספרות (סריקה מהירה עם case ו-parameters): מציג מספר של 32 ביט. מכאן כל תוצאה של הפרויקט תופיע כאן.",
    interview: [{ q: "איך נוצר latch לא מכוון ואיך מונעים אותו?", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/why-latches-are-inferred-because-of-the-incomplete-if-else-statement-in-verilog.120799/" }, { q: "מה עושים unique case ו-priority case?", src: "ChipVerify - הסבר", url: "https://www.chipverify.com/systemverilog/systemverilog-unique-priority-case" }] },
  { week: 4, n: 2, title: "למה הקוד הופך: שערים אמיתיים", goal: "לראות את החומרה שהקוד שלך מייצר",
    setup: DIGITALJS, learn: ["Latch לא מכוון: איך נוצר ואיך נמנעים"],
    task: "מדביקים ב-DigitalJS את המחבר, ה-Mux וה-decoder בלי default - ורואים איפה מופיע ה-latch.",
    board: "ב-Vivado: Open Elaborated Design ← Schematic, ואחרי סינתזה רואים איך המחבר הפך ל-LUTs ו-carry chain; מוודאים שאין אזהרת latch.",
    interview: [{ q: "מה סינתזה עושה עם if בלי else בבלוק צירופי?", src: "Nandland - הסבר", url: "https://nandland.com/how-to-avoid-creating-a-latch/" }] },
  { week: 5, n: 1, title: "Testbench: שעון, איפוס וגירויים", goal: "לבדוק קוד בלי לסמוך על העין",
    setup: EDA, learn: ["Testbench: שעון, איפוס וגירויים", "קריאת גלי סימולציה ב-EDA Playground"],
    task: "testbench למחבר של 4 ביטים: שעון, איפוס, ולולאה על כל הכניסות. מדביקים למורה את הקישור.",
    board: "לב הפרויקט - יחידת MAC: acc += a*b ב-int8 (סימן!), צובר של 24 ביט. סימולציה ב-Vivado Simulator, ועל הלוח: SW1-8=a, SW9-16=b, KEY1 צובר, התוצאה בתצוגה.",
    interview: [{ q: "מה חייב להיות ב-testbench בסיסי, ואיך יוצרים בו שעון?", src: "Xilinx XAPP199 - Writing Efficient Testbenches", url: "https://gab.wallawalla.edu/~larry.aamodt/engr433/xilinx_14/xapp199_writing_test_benches.pdf" }],
    cadence: "Xcelium Simulator - מה סימולטור עושה (רשות)" },
  { week: 5, n: 2, title: "בדיקה שבודקת את עצמה", goal: "שהבדיקה תגיד לבד PASS או FAIL",
    learn: ["Testbench שבודק את עצמו (self-checking)", "מודל ייחוס (reference model)", "Assertions בסיסיים (SVA)"],
    task: "מוסיפים לבדיקה השוואה למודל ייחוס (a+b) ו-$error על כל אי-התאמה. מכניסים באג בכוונה ורואים שהבדיקה תופסת.",
    board: "בדיקה שבודקת את עצמה ל-MAC: 1,000 צירופים אקראיים מול מודל ייחוס, כולל קצוות (-128*-128). מכניסים באג (בלי סימן) ורואים שנתפס.",
    interview: [{ q: "מה זה self-checking testbench ולמה זה עדיף?", src: "Xilinx XAPP199", url: "https://gab.wallawalla.edu/~larry.aamodt/engr433/xilinx_14/xapp199_writing_test_benches.pdf" }, { q: "מה ההבדל בין immediate assertion ל-concurrent assertion?", src: "Prepfully - שאלת ראיון", url: "https://prepfully.com/answers/assertions-differences-sv" }] },
  { week: 6, n: 1, title: "מכונות מצבים: Moore ו-Mealy", goal: "לתכנן מכונת מצבים מתרשים",
    learn: ["מכונת מצבים: Moore מול Mealy", "קידוד מכונת מצבים ב-SystemVerilog"],
    task: "מכונת מצבים של רמזור (אדום ← ירוק ← צהוב) עם מונה זמן, ובדיקה שמראה את המעברים בגרף.",
    board: "בקר (FSM) למאיץ: IDLE ← LOAD ← COMPUTE ← DONE. הבקר מזין ל-MAC 4 זוגות מספרים ומחשב מכפלה סקלרית (dot product) - הפעולה הבסיסית של רשת נוירונים. מצב הבקר על הלדים.",
    interview: [{ q: "מה ההבדל בין Moore ל-Mealy, ואיזה מגיב מהר יותר?", src: "Climb the Ladder - שאלות ראיון", url: "https://climbtheladder.com/sequence-detector-interview-questions" }, { q: "צייר FSM שמזהה את הרצף 101.", src: "InterviewPal - שאלת ראיון", url: "https://www.interviewpal.com/interview-question/sequence-detector-101" }] },
  { week: 6, n: 2, title: "מונים ומחלקי תדר", goal: "לבנות מונה ולחלק שעון",
    learn: ["מונים (counters) ומחלקי תדר"],
    task: "מונה 0-9 עם איפוס, ומחלק תדר ב-2 וב-4. בגרף: היציאה בחצי ובשליש מקצב השעון.",
    board: "מונה מחזורים (performance counter) שסופר כמה מחזורי שעון לקח החישוב ומציג בתצוגה. מעכשיו מודדים ביצועים - בדיוק מה ששואלים ב-NVIDIA.",
    interview: [{ q: "איך מחלקים שעון ב-3 עם duty cycle של 50%?", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/clock-divider-by-3-with-50-duty-cycle.48149/" }] },
  { week: 7, n: 1, title: "אוגר הזזה, LFSR וזיהוי עלייה", goal: "להכיר אבני בניין שחוזרות בכל ראיון",
    learn: ["אוגר הזזה ו-LFSR", "זיהוי עלייה של אות (edge detector)"],
    task: "אוגר הזזה של 8 ביטים, LFSR של 4 ביטים (רואים את 15 המצבים), ו-edge detector שמוציא פולס אחד.",
    board: "LFSR שמייצר וקטורי בדיקה בתוך השבב (BIST) + זיהוי לחיצה (edge detector) ו-debounce לכפתורים - כל לחיצה מריצה חישוב אחד.",
    interview: [{ q: "כתוב edge detector ב-Verilog.", src: "InterviewPal - שאלת ראיון", url: "https://www.interviewpal.com/interview-question/edge-detector-verilog" }, { q: "למה LFSR של 4 ביטים עובר רק 15 מצבים?", src: "Project Nayuki - הסבר", url: "https://www.nayuki.io/page/galois-linear-feedback-shift-register" }] },
  { week: 7, n: 2, title: "ALU קטן", goal: "לחבר הכל לבלוק אחד עם בדיקה",
    learn: ["Register file ו-ALU פשוט"],
    task: "ALU של 4 פעולות (חיבור, חיסור, AND, OR) עם בדיקה מול מודל ייחוס לכל פעולה.",
    board: "מ-ALU ל-PE (processing element): MAC עם העברת נתונים לשכן. מחברים 2x2 PEs למערך סיסטולי ראשון ומכפילים מטריצות 2x2 בסימולציה מול Python.",
    interview: [{ q: "איך מזהים overflow בחיבור עם סימן?", src: "GATE Overflow - שאלה", url: "https://gateoverflow.in/43765" }] },
  { week: 8, n: 1, title: "תזמון: setup, hold ותדר מקסימלי", goal: "לחשב את התדר המקסימלי של מעגל",
    learn: ["עיכובים לאורך המסלול הקריטי", "Setup time, hold time ו-clock-to-Q", "תדר מקסימלי ממסלול קריטי"],
    task: "תרגיל חישוב עם המורה: נתונים clk-to-Q, עיכוב לוגיקה ו-setup - מחשבים תדר מקסימלי, ובודקים הפרת hold.",
    board: "Run Implementation ← Report Timing Summary ב-200MHz: קוראים WNS, מוצאים את המסלול הקריטי (הכופל) ומחשבים תדר מקסימלי.",
    interview: [{ q: "הסבר setup ו-hold, ומה עושים בהפרת setup?", src: "Dataford - שאלת ראיון", url: "https://dataford.io/questions/explain-setup-time-and-hold-time-and-what-steps-would-you-take-to-resolve-a-setup-time-violation" }, { q: "מה עושים אם יש הפרת hold?", src: "Physical Design Interview Guide", url: "https://physical-design-interview-guide.github.io/page/7/" }] },
  { week: 8, n: 2, title: "Pipelining ו-metastability", goal: "לתקן מסלול איטי ולסנכרן אות חיצוני",
    learn: ["תיקון הפרת setup: pipelining", "הפרת hold ולמה היא מסוכנת יותר", "Metastability וסנכרון בשני דלגלגים"],
    task: "מכניסים שלב pipeline למחבר ארוך, ובונים synchronizer של שני דלגלגים לאות כניסה.",
    board: "מוסיפים pipeline ל-PE (אוגר אחרי הכפל) עד שהתזמון עובר ב-200MHz, ו-synchronizer של שני דלגלגים לכפתורים ולקו ה-UART.",
    interview: [{ q: "מה זה metastability ולמה שני דלגלגים עוזרים?", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/how-2-ff-synchronizer-solves-metastability-issues.345525/" }, { q: "מה pipelining נותן ומה המחיר שלו?", src: "Dataford - שאלת ראיון", url: "https://dataford.io/questions/pipelining-trade-offs" }] },
  { week: 9, n: 1, title: "valid/ready ו-UART", goal: "להבין איך בלוקים מעבירים נתונים בלי לאבד אותם",
    learn: ["Handshake של valid/ready", "Backpressure ו-skid buffer"],
    task: "ממשק valid/ready בסיסי ובדיקה שמראה העברה, המתנה (ready=0) והמשך - בדיוק הממשק שבין ה-UART למאיץ.",
    board: "UART RX ב-115200: Tera Term במחשב שולח בייטים והם מופיעים בתצוגה; valid/ready בין ה-UART למאיץ.",
    interview: [{ q: "מתי מתבצעת העברה ב-valid/ready?", src: "VLSI Verify - שאלות ראיון AXI", url: "https://vlsiverify.com/interview-questions/axi-interview-questions/" }, { q: "למה valid לא יכול לחכות ל-ready?", src: "Arm Community - דיון", url: "https://community.arm.com/support-forums/f/architectures-and-processors-forum/7288/in-axi-interface-is-the-valid-signal-of-the-master-dependent-on-the-slave-s-ready-signal" }] },
  { week: 9, n: 2, title: "FIFO סינכרוני", goal: "לבנות FIFO עם full ו-empty נכונים",
    learn: ["FIFO סינכרוני: מצביעים, full ו-empty"],
    task: "FIFO של 8 מקומות: כתיבה, קריאה, full, empty, ובדיקה שממלאת עד הסוף ומרוקנת.",
    board: "FIFO בין ה-UART למאיץ + UART TX: סקריפט Python שולח 1,000 בייטים ובודק שכולם חזרו (loopback) - בלי לאבד אף אחד.",
    interview: [{ q: "איך יודעים ש-FIFO מלא ולא ריק כשהמצביעים שווים?", src: "VLSI Verify - Synchronous FIFO", url: "https://vlsiverify.com/verilog/verilog-codes/synchronous-fifo/" }] },
  { week: 10, n: 1, title: "FIFO אסינכרוני וקוד Gray", goal: "להבין איך עוברים בין שני שעונים",
    learn: ["FIFO אסינכרוני וקוד Gray (מושגים)", "Clock domain crossing (CDC) - מושגים"],
    task: "ממירים מונה בינארי לקוד Gray ובחזרה, ומסבירים למורה למה זה חשוב במעבר בין שעונים.",
    board: "הרשת: ב-Google Colab מאמנים רשת קטנה על מאגר קולות רחפנים (DroneAudioDataset), מקטינים ל-int8 ומייצאים את המשקלים לקובץ .mem שנטען לזיכרון ה-BRAM עם $readmemh.",
    interview: [{ q: "למה משתמשים בקוד Gray במצביעים של FIFO אסינכרוני?", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/why-read-and-write-pointers-are-gray-encoded-in-fifo-design.41748/" }, { q: "תכנן FIFO אסינכרוני.", src: "Glassdoor - שאלה מראיון ב-Qualcomm", url: "https://www.glassdoor.co.uk/Interview/Write-some-codes-to-explain-how-to-design-asynchronous-FIFO-QTN_4543801.htm" }] },
  { week: 10, n: 2, title: "שילוב: ה-Mini-TPU מזהה רחפן", goal: "הפרויקט עובד מקצה לקצה על הלוח",
    learn: ["Backpressure ו-skid buffer", "Coverage - מה זה ולמה זה חשוב"],
    task: "מחברים UART + FIFO + בקר + מערך סיסטולי, ובדיקה אקראית עם backpressure לפני שצורבים.",
    board: "שילוב מלא: מערך סיסטולי 4x4 מריץ את הרשת. Python שולח קטע קול (מאפיינים) ב-UART, הלוח מחזיר 'רחפן / לא רחפן', LED אדום נדלק ברחפן, ובתצוגה - כמה מחזורים לקח.",
    interview: [{ q: "אם code coverage וגם functional coverage ב-100%, האימות גמור?", src: "Verification Academy - דיון", url: "https://verificationacademy.com/forums/t/if-both-functional-and-code-coverage-are-100-then-can-we-say-that-the-verification-is-complete/36125" }] },
  { week: 11, n: 1, title: "סינתזה ו-STA", goal: "להבין מה קורה לקוד בדרך לשבב", learn: ["סינתזה: מקוד לשערים", "Static timing analysis (STA)"],
    task: "קוראים עם המורה את דוח התזמון של הפרויקט שלך (slack לכל מסלול) ומבינים כל שורה.",
    board: "דוחות Vivado של הפרויקט: שטח (LUT, DSP, BRAM), תזמון והספק (Report Power). משווים זמן חישוב ללוח מול Python במחשב - המספרים שנכנסים לקורות החיים.",
    interview: [{ q: "מה זה slack שלילי ואיך מתקנים?", src: "PracHub - תרגילי STA לראיון", url: "https://prachub.com/resources/static-timing-analysis-interview-exercises-setup-hold-and-constraint-debugging" }],
    cadence: "Genus Synthesis - מה זה סינתזה (רשות)" },
  { week: 11, n: 2, title: "מקוד לשבב: Place & Route", goal: "לראות את הפרויקט שלך כשבב",
    learn: ["Place & Route ועץ שעון (clock tree)", "צריכת הספק ו-clock gating", "DFT ו-scan chain (מושגים)"],
    task: "ב-Vivado: Open Implemented Design ← Device - רואים איפה ה-PEs ישבו בשבב, ומסבירים במילים מה כל שלב עשה (סינתזה, מיקום, חיווט, עץ שעון).",
    board: "GitHub: קוד, README עם תרשים בלוקים, תוצאות ודוחות, וסרטון הדגמה קצר של הלוח מזהה רחפן. (רשות: הרצת PE אחד ב-OpenLane כדי לראות אותו כשבב.)",
    interview: [{ q: "מה השלבים מ-RTL ל-GDS, ולמה צריך עץ שעון (CTS)?", src: "Maven Silicon - שאלות ראיון Physical Design", url: "https://www.maven-silicon.com/vlsi-jobs/physical-design-interview-questions/" }] },
  { week: 12, n: 1, title: "שאלות ראיון קלאסיות", goal: "לפתור ולהסביר בקול שאלות שחוזרות",
    learn: ["שאלות קלאסיות: חלוקת שעון ב-2 וב-3", "שאלות קלאסיות: ספירת אחדים, בדיקת חזקה של 2"],
    task: "פותרים עם המורה 4 שאלות ראיון בקול (כמו בראיון אמיתי), וכותבים קוד לשתיים מהן ב-EDA Playground.",
    board: "שאלות ראיון על הפרויקט: למה מערך סיסטולי חוסך גישות לזיכרון, מה מפסידים ב-int8, ואיפה צוואר הבקבוק (UART מול חישוב).",
    interview: [{ q: "חלק שעון ב-3 עם 50% duty cycle.", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/clock-divider-by-3-with-50-duty-cycle.48149/" }, { q: "בדוק אם מספר הוא חזקה של 2 ב-Verilog.", src: "EDAboard - דיון", url: "https://www.edaboard.com/threads/determine-whether-a-binary-number-is-of-power-of-two-in-verilog-code.386863/" }] },
  { week: 12, n: 2, title: "ראיון דמה", goal: "להציג את הפרויקט ולעמוד בראיון",
    learn: ["להסביר את הפרויקט שלך ב-3 דקות"],
    task: "ראיון דמה מלא עם המורה: הצגת ה-Mini-TPU ב-3 דקות, ואז שאלות טכניות. בסוף - משוב ומה לשפר.",
    board: "מציגים את הפרויקט ב-3 דקות עם הסרטון והמספרים, ושורה מוכנה לקורות החיים.",
    interview: [{ q: "ספר על הפרויקט שלך (בראיונות ASIC ב-NVIDIA רוב הזמן עובר על הפרויקטים מקורות החיים).", src: "Glassdoor - ראיונות ASIC Design ב-NVIDIA", url: "https://clear.glassdoor.nl/Interview/NVIDIA-ASIC-Design-Engineer-Interview-Questions-EI_IE7633.0,6_KO7,27.htm" }] },
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
    s.board ? `🔧 על הלוח (הפרויקט ${PROJECT}): ${s.board}\nפינים: ${BOARD_PINS.join(" ")}` : "",
    `שאלות ראיון לסיום (מקור לכל אחת): ${s.interview.map((i) => `${i.q} [${i.src}: ${i.url}]`).join(" | ")}`,
    "תלמד אותי לפי הכללים שלי: לאט, עם דוגמאות, כל שורת קוד מוסברת, ושאלות פתוחות. תתחיל.",
  ].filter(Boolean).join("\n");
}
