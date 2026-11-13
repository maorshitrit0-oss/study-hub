"""Self-study, week 2 session 2 (Mux, Decoder, ripple adder) - rewritten understanding-first (his request 13/11/2026:
"I can read the code but I can't write it from a blank page; I don't know what to do in Vivado after writing the code").
Order: the SystemVerilog grammar of today, piece by piece -> each block explained line by line -> exercises that climb
(predict -> fill blanks -> change -> write alone) -> the board task with every Vivado click and what you should see.
  python vlsi_w2s2.py -> chapters/vlsi-w2s2.json  (published as lecture 4 of the self-study course)"""
import json
from pathlib import Path

FA = """module full_adder (
    input  logic a, b, cin,     // three 1-bit inputs
    output logic s, cout        // sum and carry out
);
    assign s    = a ^ b ^ cin;                 // sum: 1 when an odd number of inputs is 1
    assign cout = (a & b) | (cin & (a ^ b));   // carry: at least two of the three are 1
endmodule"""

ADDER4 = """module adder4 (
    input  logic [3:0] a, b,    // two 4-bit numbers (0..15)
    output logic [4:0] sum      // 5 bits: 15+15 = 30 needs 5 bits
);
    logic c1, c2, c3;           // the carries between the stages ("wires" inside the module)

    full_adder fa0 (.a(a[0]), .b(b[0]), .cin(1'b0), .s(sum[0]), .cout(c1));
    full_adder fa1 (.a(a[1]), .b(b[1]), .cin(c1),   .s(sum[1]), .cout(c2));
    full_adder fa2 (.a(a[2]), .b(b[2]), .cin(c2),   .s(sum[2]), .cout(c3));
    full_adder fa3 (.a(a[3]), .b(b[3]), .cin(c3),   .s(sum[3]), .cout(sum[4]));
endmodule"""

MUX2 = """module mux2 (
    input  logic a, b,   // the two data inputs
    input  logic s,      // select
    output logic y
);
    assign y = s ? b : a;   // s=1 -> b, s=0 -> a
endmodule"""

MUX4 = """module mux4 (
    input  logic [3:0] d,   // four data inputs d[0]..d[3]
    input  logic [1:0] s,   // select 0..3
    output logic y
);
    logic lo, hi;           // the outputs of the first two mux2

    mux2 m0 (.a(d[0]), .b(d[1]), .s(s[0]), .y(lo));   // picks d0 / d1
    mux2 m1 (.a(d[2]), .b(d[3]), .s(s[0]), .y(hi));   // picks d2 / d3
    mux2 m2 (.a(lo),   .b(hi),   .s(s[1]), .y(y));    // picks between them
endmodule"""

DEC = """module dec2to4 (
    input  logic [1:0] sel,
    output logic [3:0] y
);
    always_comb begin            // combinational block: re-evaluated whenever sel changes
        case (sel)
            2'd0:    y = 4'b0001;
            2'd1:    y = 4'b0010;
            2'd2:    y = 4'b0100;
            default: y = 4'b1000;   // sel = 3 (default also prevents a latch)
        endcase
    end
endmodule"""

TB = """module tb_adder4;                 // a testbench has no ports
    logic [3:0] a, b;
    logic [4:0] sum;

    adder4 dut (.a(a), .b(b), .sum(sum));   // the circuit under test

    initial begin
        a = 4'd5;  b = 4'd3;  #10;          // put values, wait 10 ns
        $display("5 + 3 = %0d", sum);
        a = 4'd15; b = 4'd1;  #10;
        $display("15 + 1 = %0d", sum);
        $finish;                            // end of the simulation
    end
endmodule"""

TOP = """module top (
    input  logic [7:0] sw,      // switches SW1..SW8
    output logic [4:0] led      // LED1..LED5
);
    adder4 u_add (.a(sw[3:0]), .b(sw[7:4]), .sum(led));
endmodule"""

XDC = """set_property -dict {PACKAGE_PIN H13 IOSTANDARD LVCMOS33} [get_ports {sw[0]}]
set_property -dict {PACKAGE_PIN G13 IOSTANDARD LVCMOS33} [get_ports {sw[1]}]
set_property -dict {PACKAGE_PIN G15 IOSTANDARD LVCMOS33} [get_ports {sw[2]}]
set_property -dict {PACKAGE_PIN G16 IOSTANDARD LVCMOS33} [get_ports {sw[3]}]
set_property -dict {PACKAGE_PIN J14 IOSTANDARD LVCMOS33} [get_ports {sw[4]}]
set_property -dict {PACKAGE_PIN H14 IOSTANDARD LVCMOS33} [get_ports {sw[5]}]
set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVCMOS33} [get_ports {sw[6]}]
set_property -dict {PACKAGE_PIN G18 IOSTANDARD LVCMOS33} [get_ports {sw[7]}]
set_property -dict {PACKAGE_PIN J21 IOSTANDARD LVCMOS33} [get_ports {led[0]}]
set_property -dict {PACKAGE_PIN J19 IOSTANDARD LVCMOS33} [get_ports {led[1]}]
set_property -dict {PACKAGE_PIN H19 IOSTANDARD LVCMOS33} [get_ports {led[2]}]
set_property -dict {PACKAGE_PIN K18 IOSTANDARD LVCMOS33} [get_ports {led[3]}]
set_property -dict {PACKAGE_PIN K19 IOSTANDARD LVCMOS33} [get_ports {led[4]}]"""


def code(c):
    return "```systemverilog\n" + c + "\n```"


GRAMMAR = r"""## 🧭 איך המפגש הזה בנוי
קודם **הדקדוק** של SystemVerilog שצריך היום – 7 חלקים קטנים, כל אחד עם דוגמה של שורה אחת. אחר כך כל רכיב (Mux,
Decoder, מחבר) מוסבר **שורה אחרי שורה**. ואז תרגול שמטפס בהדרגה: לקרוא ולנחש ← להשלים חסרים ← לשנות ← לכתוב לבד.
בסוף – המשימה על הלוח עם **כל לחיצה ב-Vivado** ומה אמור להופיע.

> 💡 כמו בשפה: קודם לומדים מילים ומבנה משפט, ורק אז כותבים חיבור. אף אחד לא כותב קוד מדף ריק בלי להכיר את 7 החלקים האלה.

## 📘 הדקדוק של היום – 7 חלקים

**1. מודול = רכיב עם כניסות ויציאות.** כמו שבב על לוח: יש לו שם, רגליים נכנסות ורגליים יוצאות.
```systemverilog
module name ( input logic a, output logic y );
    // what is inside
endmodule
```
- `module ... endmodule` – תחילת וסוף הרכיב.
- `input logic a` – רגל כניסה בשם a, ביט אחד. `output logic y` – רגל יציאה.
- **אחרי כל שורה בתוך המודול – נקודה-פסיק `;`** (חוץ מ-`begin`/`end`/`endmodule`).

**2. וקטור = כמה ביטים יחד.** `logic [3:0] a` הוא מספר של 4 ביטים: `a[3] a[2] a[1] a[0]` (a[0] הוא הביט הימני, הקטן).
- `a[0]` – ביט אחד מתוכו. `sw[3:0]` – ארבעת הביטים התחתונים.

**3. `assign` = חוט קבוע.** `assign y = a & b;` אומר "y מחובר תמיד ל-AND של a ו-b". זה לא פקודה שרצה פעם אחת –
זה חיווט: כל שינוי ב-a או b משנה את y מיד.

**4. אופרטורים:** `&` וגם, `|` או, `^` XOR, `~` היפוך, `+` חיבור. ובחירה: `s ? b : a` = "אם s אז b, אחרת a" –
זה בדיוק Mux.

**5. מספרים עם גודל:** `4'b0101` = 4 ביטים בבינארי (5). `4'd5` = 4 ביטים בעשרוני (5). `1'b0` = ביט אחד, אפס.
המספר לפני הגרש = כמה ביטים; האות = הבסיס (b בינארי, d עשרוני, h הקסה).

**6. `always_comb` + `case` = טבלת אמת בקוד.** כשנוח יותר לכתוב "אם הכניסה X – היציאה Y":
```systemverilog
always_comb begin
    case (sel)
        2'd0:    y = 4'b0001;
        default: y = 4'b1000;
    endcase
end
```
- `default` חובה: בלי ערך לכל מקרה, הכלי בונה latch (זיכרון) בטעות.

**7. שימוש ברכיב בתוך רכיב (instantiation).** כמו להלחים שבב על לוח ולחבר לו חוטים:
```systemverilog
full_adder fa0 (.a(x), .b(y), .cin(1'b0), .s(s0), .cout(c1));
```
- `full_adder` – איזה רכיב. `fa0` – השם של העותק הזה (יכולים להיות כמה עותקים).
- `.a(x)` – "את הרגל a של הרכיב מחברים לחוט x שאצלי". הנקודה = שם הרגל ברכיב, בסוגריים = החוט אצלך.

> ⭐ אם זוכרים את 7 החלקים האלה – אפשר לקרוא ולכתוב את כל הקוד של היום."""

MUX_MD = r"""## 1. Mux – בורר
**מה הוא עושה:** בוחר כניסה אחת מתוך כמה ומעביר אותה ליציאה, לפי קו בחירה. כמו מתג בורר בטלוויזיה: HDMI1 או HDMI2.

| s | y |
|---|---|
| 0 | a |
| 1 | b |

""" + code(MUX2) + r"""

**שורה אחרי שורה:**
- `input logic a, b` – שתי כניסות נתונים, ביט אחד כל אחת. `input logic s` – קו הבחירה.
- `assign y = s ? b : a;` – אם s=1 היציאה היא b, אחרת a. זו כל הלוגיקה.

### Mux 4:1 משלושה Mux 2:1 (שאלת הראיון)
**הרעיון:** שני mux2 בוחרים "בתוך זוג" לפי הביט הנמוך `s[0]`, והשלישי בוחר "בין הזוגות" לפי הביט הגבוה `s[1]`.

""" + code(MUX4) + r"""

**בדיקה עם מספרים – לאט:** `s = 2'b10` = המספר **2**, אז מצפים שהיציאה תהיה **d2**.
- הביטים: `s[1]` (השמאלי) = **1**, `s[0]` (הימני) = **0**.

**שלב 1 – שני ה-Mux הראשונים מסתכלים רק על `s[0] = 0`** (s=0 → בוחרים את הכניסה הראשונה, a):

| Mux | הכניסות שלו | בוחר | היציאה |
|---|---|---|---|
| m0 | d0, d1 | d0 | lo = d0 |
| m1 | d2, d3 | d2 | hi = d2 |

**שלב 2 – m2 מסתכל על `s[1] = 1`** (s=1 → בוחר את הכניסה השנייה, b = hi) → **y = hi = d2** ✅

💡 הביט הימני בוחר **בתוך כל זוג**; הביט השמאלי בוחר **איזה זוג**.

## 2. Decoder – מפענח 2→4
**מה הוא עושה:** מקבל מספר (0..3) ומדליק **קו אחד בלבד** מתוך 4 – את הקו שמספרו נבחר. כמו בורר קומה במעלית.

| sel | y (y3 y2 y1 y0) |
|---|---|
| 0 | 0001 |
| 1 | 0010 |
| 2 | 0100 |
| 3 | 1000 |

""" + code(DEC) + r"""

**שורה אחרי שורה:**
- `always_comb begin ... end` – בלוק צירופי (בלי זיכרון): מחושב מחדש בכל שינוי של `sel`.
- `case (sel)` – לפי ערך sel. `2'd0:` – "כש-sel הוא 0". `y = 4'b0001;` – מדליקים את y0.
- `default` – כל מה שלא נכתב (כאן sel=3).

> 🏠 **מקודד עדיפות (Priority encoder)** הוא ההפך: מקבל כמה קווים ומחזיר את **המספר** של הקו הגבוה שדולק – למשל איזו
> בקשת פסיקה הכי דחופה."""

ADD_MD = r"""## 3. מחבר ripple-carry של 4 ביטים
**הרעיון:** מחבר מלא (מהמפגש הקודם) מחבר ביט אחד ומוציא נשא. שמים 4 כאלה בשורה, והנשא של כל אחד נכנס לבא – כמו חיבור
במאונך בבית הספר, עמודה אחרי עמודה.

""" + code(FA) + "\n\n" + code(ADDER4) + r"""

**שורה אחרי שורה:**
- `logic [3:0] a, b` – שני מספרים של 4 ביטים. `logic [4:0] sum` – 5 ביטים, כי 15+15=30 צריך ביט חמישי.
- `logic c1, c2, c3;` – החוטים הפנימיים שמעבירים את הנשא מעמודה לעמודה.
- `fa0 (... .cin(1'b0) ...)` – בעמודה הראשונה אין נשא נכנס: אפס.
- `.cout(c1)` של fa0 נכנס כ-`.cin(c1)` של fa1 – זה ה"גלגול" (ripple).
- `.cout(sum[4])` של fa3 – הנשא האחרון הוא הביט החמישי של התוצאה.

**דוגמה: 15 + 1 = 16** (1111 + 0001): בעמודה 0 יוצא נשא, שהופך לנשא בעמודה 1, ומשם ל-2 ול-3 – **הנשא עובר דרך כל
ארבעת המחברים** עד שהתוצאה 10000 מוכנה.

### ⏱️ שאלת הראיון: מה העיכוב של מחבר ripple של N ביטים?
- כל מחבר מלא צריך לחכות לנשא מהקודם. במקרה הגרוע (כמו 15+1) הנשא עובר דרך **כל** N המחברים.
- לכן העיכוב **גדל לינארית עם N**: בערך $t \approx N\cdot t_{carry}$ (כש-$t_{carry}$ הוא עיכוב הנשא במחבר אחד,
  כ-2 שערים).
- **התשובה בראיון:** "O(N) – הנשא מתגלגל דרך כל הביטים. ל-32 ביט זה איטי, ולכן יש מחברי carry-lookahead שמחשבים
  את הנשאים במקביל."

### ⚡ Glitch – קפיצה רגעית
בזמן שהנשא עוד מתגלגל, ביטי התוצאה יכולים להראות לרגע ערך לא נכון ("glitch"). לכן במערכת עם שעון קוראים את התוצאה
רק בעליית השעון – אחרי שהכול נרגע. זו בדיוק הסיבה שעיכוב קובע את מהירות השעון."""

VIVADO_MD = r"""## 🖥️ סימולציה – הסדר המלא (חוזר בכל מפגש עד 6.2, כדי שיהפוך לטבעי)
**המטרה:** לראות שהקוד עובד במחשב לפני שצורבים. מגלים טעויות בשניות ולא בחצי שעה.

### דרך א: Vivado 2025.2 (במחשב)
1. **פותחים:** תפריט התחל ← `Vivado 2025.2` ← `Open Project` ← `mini_tpu`. (פרויקט חדש: `Create Project` ← RTL Project ←
   שבב `xc7a35tfgg484-2`.)
2. **קובץ הרכיב:** בצד שמאל, `Flow Navigator` ← `PROJECT MANAGER` ← **`Add Sources`** ← `Add or create design sources` ←
   `Create File` ← File type: **SystemVerilog**, שם: `adder4` ← `OK` ← `Finish` (חלון Define Module – `OK`).
3. בחלון `Sources` לוחצים פעמיים על `adder4.sv`, מדביקים את **full_adder ו-adder4**, ושומרים: **Ctrl+S**.
4. **קובץ הבדיקה:** שוב `Add Sources` ← הפעם **`Add or create simulation sources`** ← `Create File` ← SystemVerilog,
   שם `tb_adder4` ← מדביקים את הבדיקה (בתרגיל 5) ← **Ctrl+S**.
5. ב-`Sources` ← תיקייה `Simulation Sources` ← לחיצה ימנית על `tb_adder4` ← **`Set as Top`**.
6. `Flow Navigator` ← `SIMULATION` ← **`Run Simulation`** ← **`Run Behavioral Simulation`**.
7. **בודקים – מה אמור להופיע:**
   - למטה בלשונית **`Tcl Console`**: `5 + 3 = 8` ו-`15 + 1 = 16`. ✅
   - **חלון הגלים:** הסיגנלים a, b, sum לאורך הזמן. כפתור **`Zoom Fit`** (ריבוע עם חצים) מציג הכול. לחיצה ימנית על `sum`
     ← `Radix` ← **`Unsigned Decimal`** – רואים מספרים (8, 16) במקום ביטים.
8. **אם יש שגיאה:** לשונית **`Messages`** למטה ← השורה האדומה הראשונה. 3 הטעויות הנפוצות:
   - חסר `;` בסוף שורה → "syntax error near ...".
   - שם רגל לא תואם (`.cin` ברכיב אבל `.c_in` בחיבור) → "port not found".
   - חסר `endmodule`.
   מתקנים ← Ctrl+S ← שוב `Run Behavioral Simulation` (אם שואל לסגור את הקודמת – `Yes`).

### דרך ב: EDA Playground (בדפדפן, גם מהטלפון)
1. נכנסים ל-https://www.edaplayground.com ← **`Log in`** (עם חשבון גוגל – חובה כדי להריץ).
2. בצד שמאל: `Testbench + Design` ← **SystemVerilog/Verilog**. `Tools & Simulators` ← **Icarus Verilog 12.0**.
   מסמנים **`Open EPWave after run`**.
3. בחלון **השמאלי** (`testbench.sv`) מדביקים את הבדיקה, ובחלון **הימני** (`design.sv`) את full_adder ו-adder4.
4. כדי לראות גלים, מוסיפים בתחילת ה-`initial` בבדיקה שתי שורות: `$dumpfile("dump.vcd"); $dumpvars;`
5. לוחצים **`Run`** (למעלה). למטה בלשונית `Log` יופיע `5 + 3 = 8`, וחלון הגלים (EPWave) נפתח לבד ← `Get Signals` ←
   בוחרים את a, b, sum ← `Append All`."""


QUIZ = [
    ("מה עושה השורה `assign y = s ? b : a;`?", ["אם s=1 – y שווה b, אחרת a (Mux)", "y שווה s כפול b ועוד a", "שומרת את b בזיכרון", "בודקת אם s גדול מ-b"], 0,
     "`? :` היא בחירה: תנאי ? ערך-אם-כן : ערך-אם-לא.", "דקדוק SystemVerilog", 1),
    ("כמה ביטים יש ב-`logic [3:0] a`?", ["4", "3", "5", "1"], 0, "מ-3 עד 0 כולל: a[3], a[2], a[1], a[0].", "דקדוק SystemVerilog", 1),
    ("מה פירוש `4'b0110`?", ["מספר של 4 ביטים בבינארי, ערך 6", "המספר 4110", "4 בבסיס 110", "6 ביטים"], 0,
     "4 = כמה ביטים, b = בינארי, 0110 = 6.", "דקדוק SystemVerilog", 1),
    ("בשורה `full_adder fa1 (.cin(c1), ...);` מה פירוש `.cin(c1)`?", ["את הרגל cin של fa1 מחברים לחוט c1", "c1 שווה cin", "יוצרים רגל חדשה בשם c1", "מעתיקים את fa1 ל-c1"], 0,
     "נקודה + שם = הרגל ברכיב; בסוגריים = החוט אצלך.", "דקדוק SystemVerilog", 2),
    ("למה צריך `default` ב-`case` בתוך `always_comb`?", ["כדי שלכל ערך תהיה יציאה – אחרת נוצר latch בטעות", "כדי שהקוד ירוץ מהר יותר", "זה רק מנהג, אין לזה השפעה", "כדי לאפס את המערכת"], 0,
     "ערך שלא הוגדר = הכלי \"זוכר\" את הקודם = latch.", "Decoder", 2),
    ("ב-Mux 4:1 משלושה Mux 2:1, איזה ביט בוחר בשלב האחרון?", ["s[1] – הביט הגבוה", "s[0] – הביט הנמוך", "שניהם יחד", "d[3]"], 0,
     "שני הראשונים בוחרים בתוך זוג לפי s[0], האחרון בין הזוגות לפי s[1].", "Mux", 2),
    ("מה העיכוב של מחבר ripple של N ביטים?", ["גדל לינארית עם N – הנשא עובר דרך כל המחברים", "קבוע, לא תלוי ב-N", "גדל כמו N בריבוע", "תלוי רק בביט הראשון"], 0,
     "במקרה הגרוע הנשא מתגלגל דרך כל N העמודות: O(N).", "מחבר ripple", 2),
    ("איפה רואים ב-Vivado את הפלט של `$display` בסימולציה?", ["בלשונית Tcl Console למטה", "על הלדים בלוח", "בדוח הסינתזה", "בקובץ ה-XDC"], 0,
     "$display כותב טקסט לקונסולה של הסימולטור.", "Vivado", 1),
]

EX = [
    dict(title="🔧 תרגול על הלוח: מחבר 4 ביטים – כל הצעדים",
         question_md="""בונים על הלוח את המחבר: **SW1–SW4 הם המספר a, SW5–SW8 הם b, והתוצאה (5 ביטים) על LED1–LED5.**
זה תרגול של Vivado והלוח (לא חובה – אם הסימולציה בתרגיל 5 עובדת, הבנת את המפגש). בשבוע 9 המחבר הזה ייכנס
ליחידת ה-MAC של הפרויקט. **קודם מוודאים שהסימולציה עובדת (תרגיל 5).**""",
         solution_md="""**שלב 1 – קובץ ה-top (מחבר בין הלוח למחבר):** `Add Sources` ← design sources ← Create File ← SystemVerilog, שם `top`:

""" + code(TOP) + """

- `sw[3:0]` הם 4 המתגים הראשונים → המספר a. `sw[7:4]` → המספר b. `led` (5 ביטים) → התוצאה.
- ב-`Sources` ← `Design Sources` ← לחיצה ימנית על `top` ← **`Set as Top`**.

**שלב 2 – קובץ הפינים (XDC):** `Add Sources` ← **`Add or create constraints`** ← Create File, שם `pins` ← מדביקים
(רק הפינים שבשימוש – כל פורט ב-top חייב שורה):

```text
""" + XDC + """
```

**שלב 3 – הלחיצות, לפי הסדר** (ב-`Flow Navigator`):
1. `SYNTHESIS` ← **`Run Synthesis`** ← OK. מחכים לסימן ✓ (דקה-שתיים).
2. בחלון שקופץ: **`Run Implementation`** ← OK.
3. בחלון שקופץ: **`Generate Bitstream`** ← OK. (אם יש שגיאה אדומה על פורט "unconstrained" – חסרה שורה ב-XDC.)
4. מחברים את הלוח ב-USB ומדליקים אותו. בחלון שקופץ: **`Open Hardware Manager`**.
5. למעלה בפס הירוק: **`Open target`** ← **`Auto Connect`**. אמור להופיע השבב `xc7a35t`.
6. **`Program device`** ← `Program`. אחרי כמה שניות הלוח מתוכנת.

**שלב 4 – מה אמור לקרות על הלוח (הבדיקה):**
| מתגים | a + b | לדים (LED5..LED1) |
|---|---|---|
| הכול למטה | 0 + 0 = 0 | הכול כבוי |
| SW1 ו-SW3 למעלה (a=5), SW5 ו-SW6 למעלה (b=3) | 5 + 3 = 8 | רק **LED4** דולק (01000) |
| SW1–SW4 למעלה (a=15), SW5 למעלה (b=1) | 15 + 1 = 16 | רק **LED5** דולק (10000) |
| SW1–SW8 למעלה | 15 + 15 = 30 | LED5, LED4, LED3, LED2 (11110) |

**אם לא עובד:**
- הלוח לא נמצא ב-Auto Connect → כבל USB אחר / הלוח כבוי / דרייבר הכבל (מההתקנה).
- הלדים הפוכים מהצפוי → לבדוק שהמתג "למעלה" הוא 1 (אפשר לבדוק: כל המתגים למטה = הכול כבוי).
- שגיאה בסינתזה → `Messages`, השורה האדומה הראשונה.""",
         topic="תרגול על הלוח"),
    dict(title="תרגיל 1 · 🔍 לקרוא ולנחש (בלי לכתוב)",
         question_md="""בלי להריץ – מה היציאה?
1. ב-`mux2`: `a=0, b=1, s=1` → `y = ?`
2. ב-`mux4`: `d = 4'b1010`, `s = 2'b01` → `y = ?`
3. ב-`dec2to4`: `sel = 2'd2` → `y = ?`
4. ב-`adder4`: `a = 4'd6, b = 4'd7` → `sum = ?` (בעשרוני ובבינארי)""",
         solution_md="""1. `s=1` → בוחר את b → **y = 1**.
2. `d = 1010` פירושו d[3]=1, d[2]=0, d[1]=1, d[0]=0. `s = 01` → `s[0]=1`: m0 נותן d[1]=1, m1 נותן d[3]=1;
   `s[1]=0` → m2 בוחר את lo = **1**. (בדיקה: s=1 → d[1]=1 ✅)
3. `sel=2` → **y = 4'b0100**.
4. 6+7 = **13** = **01101** (5 ביטים).

💡 **הרעיון:** לפני שכותבים – קוראים קוד ומנחשים. אם הניחוש נכון, מבינים את הרכיב.""",
         topic="Mux"),
    dict(title="תרגיל 2 · ✏️ להשלים את החסר – Mux 2:1",
         question_md="""השלם את 4 החסרים (`___`):
```systemverilog
module mux2 (
    input  logic a, b,
    input  logic ___,
    output logic y
);
    ___ y = s ? ___ : a;
___
```""",
         solution_md="""```systemverilog
module mux2 (
    input  logic a, b,
    input  logic s,
    output logic y
);
    assign y = s ? b : a;
endmodule
```
- `s` – קו הבחירה הוא כניסה.
- `assign` – חוט קבוע.
- `b` – כש-s=1 בוחרים את b.
- `endmodule` – סוגרים את המודול (בלי `;`).

**עוד תרגול (בדיקה אוטומטית מיידית):** https://hdlbits.01xz.net/wiki/Mux2to1 – כותבים שורה אחת ולוחצים **`Submit`**.
ואחריו גרסת הווקטורים: https://hdlbits.01xz.net/wiki/Mux2to1v""",
         topic="Mux"),
    dict(title="תרגיל 3 · ✏️ להשלים את החסר – Mux 4:1 משלושה Mux 2:1",
         question_md="""השלם את החיבורים:
```systemverilog
module mux4 (input logic [3:0] d, input logic [1:0] s, output logic y);
    logic lo, hi;
    mux2 m0 (.a(d[0]), .b(___),  .s(___),  .y(lo));
    mux2 m1 (.a(___),  .b(d[3]), .s(s[0]), .y(___));
    mux2 m2 (.a(lo),   .b(hi),   .s(___),  .y(y));
endmodule
```""",
         solution_md="""```systemverilog
    mux2 m0 (.a(d[0]), .b(d[1]), .s(s[0]), .y(lo));
    mux2 m1 (.a(d[2]), .b(d[3]), .s(s[0]), .y(hi));
    mux2 m2 (.a(lo),   .b(hi),   .s(s[1]), .y(y));
```
- m0 בוחר בזוג הראשון (d0/d1) לפי **s[0]**.
- m1 בוחר בזוג השני (d2/d3) לפי s[0], והתוצאה ב-**hi**.
- m2 בוחר בין הזוגות לפי **s[1]**.

💡 **שיטה לזכור:** הביט הנמוך בוחר "בתוך זוג", הגבוה – "איזה זוג".

**אתגר (רשות):** https://hdlbits.01xz.net/wiki/Mux256to1 – Mux של 256 כניסות בשורה אחת. רמז: `assign out = in[sel];`""",
         topic="Mux"),
    dict(title="תרגיל 4 · 🔧 לשנות – Decoder עם כניסת הפעלה",
         question_md="""קח את `dec2to4` והוסף כניסה `en` (ביט אחד): כש-`en = 0` כל היציאות 0; כש-`en = 1` הוא עובד כרגיל.
רמז: `if (!en) ... else case ...` בתוך ה-`always_comb`.""",
         solution_md="""```systemverilog
module dec2to4_en (
    input  logic [1:0] sel,
    input  logic       en,      // new: enable
    output logic [3:0] y
);
    always_comb begin
        if (!en)
            y = 4'b0000;            // disabled: nothing on
        else
            case (sel)
                2'd0:    y = 4'b0001;
                2'd1:    y = 4'b0010;
                2'd2:    y = 4'b0100;
                default: y = 4'b1000;
            endcase
    end
endmodule
```
- `input logic en` – כניסה חדשה, ומוסיפים פסיק בשורה שלפניה.
- `if (!en)` – `!` היא "לא": כש-en=0.
- כל ענף נותן ערך ל-y – לכן אין latch.

💡 **ככה כותבים קוד חדש בהתחלה:** לוקחים קוד שעובד ומשנים דבר אחד.""",
         topic="Decoder"),
    dict(title="תרגיל 5 · ✍️ לכתוב לבד – מחבר 4 ביטים + בדיקה (עם רמזים)",
         question_md="""נתון לך `full_adder` (בפרק). כתוב לבד:
1. `adder4` – שני מספרים של 4 ביטים, תוצאה של 5 ביטים, מ-4 עותקים של `full_adder`.
2. `tb_adder4` – בדיקה ששמה 5+3 ואז 15+1 ומדפיסה את התוצאה.

**סולם רמזים** (לפתוח רק אם נתקעים, אחד אחרי השני):
- רמז 1: כמה חוטי נשא פנימיים צריך בין 4 מחברים? (3)
- רמז 2: מה נכנס ל-`cin` של המחבר הראשון? (`1'b0`)
- רמז 3: לאן הולך ה-`cout` של האחרון? (`sum[4]`)
- רמז 4: בבדיקה – `initial begin ... end`, ובין ערכים `#10;`.

**איפה כותבים:** ב-Vivado או ב-EDA Playground (הדרכים בפרק, בחלק "סימולציה").
**עוד תרגול באותו נושא (בדיקה אוטומטית מיידית):**
- מחבר מלא: https://hdlbits.01xz.net/wiki/Fadd
- מחבר ripple של 3 ביטים: https://hdlbits.01xz.net/wiki/Adder3
(ב-HDLBits כותבים בתוך המודול שכבר נתון, לוחצים **`Submit`**, ומקבלים מיד "Success" או גרף של מה שיצא שונה.)""",
         solution_md="""**המחבר:**

""" + code(ADDER4) + """

**הבדיקה:**

""" + code(TB) + """

**שורה אחרי שורה בבדיקה:**
- `module tb_adder4;` – לבדיקה אין רגליים: היא "הלוח" שמחובר לרכיב.
- `adder4 dut (...)` – העותק של המחבר שנבדק (dut = device under test).
- `initial begin ... end` – רץ פעם אחת מתחילת הסימולציה.
- `a = 4'd5; b = 4'd3; #10;` – שמים ערכים ומחכים 10 ננו-שניות שהמעגל יגיב.
- `$display("5 + 3 = %0d", sum);` – מדפיס ל-Tcl Console. `%0d` = המספר בעשרוני.
- `$finish;` – סוף.

**ב-Vivado:** לפי הצעדים בפרק (Add Sources ← simulation sources ← Set as Top ← Run Behavioral Simulation).
**אמור להופיע ב-Tcl Console:** `5 + 3 = 8` ו-`15 + 1 = 16`.""",
         topic="מחבר ripple"),
]


def main():
    chapter = "\n\n".join([GRAMMAR, MUX_MD, ADD_MD, VIVADO_MD, r"""## 🎤 שאלות הראיון של היום – תשובות קצרות
- **מה העיכוב של מחבר ripple של N ביטים?** גדל לינארית: הנשא עובר דרך כל N המחברים במקרה הגרוע ($\approx N\cdot t_{carry}$).
  לכן במחברים רחבים משתמשים ב-carry-lookahead.
- **איך בונים Mux 4:1 מ-Mux 2:1?** שלושה: שניים בוחרים בתוך כל זוג לפי `s[0]`, השלישי בוחר בין הזוגות לפי `s[1]`.

## 🔧 היום על הלוח (תרגול)
מחבר של 4 ביטים: SW1–4 ועוד SW5–8, התוצאה על הלדים. הצעדים המלאים בתרגיל "תרגול על הלוח". זה לא חובה – אם
הסימולציה עובדת, הבנת. בשבוע 9 המחבר הזה ייכנס ליחידת ה-MAC של הפרויקט."""])
    summary = r"""## 🎯 המסר של המפגש
- **Mux** בוחר כניסה אחת לפי קו בחירה: `assign y = s ? b : a;`. Mux 4:1 = שלושה Mux 2:1 (`s[0]` בתוך זוג, `s[1]` בין זוגות).
- **Decoder** 2→4 מדליק קו אחד לפי המספר: `always_comb` + `case` + `default`.
- **מחבר ripple** = מחברים מלאים בשורה, הנשא מתגלגל ← עיכוב לינארי ב-N.
- **הדקדוק:** module/endmodule, `input/output logic`, וקטור `[3:0]`, `assign`, `? :`, `4'b0101`, instantiation עם `.port(wire)`.
- **ב-Vivado:** קוד ← Add Sources ← בדיקה ב-simulation sources ← Set as Top ← Run Behavioral Simulation ← Tcl Console.
- **על הלוח (תרגול):** top + XDC ← Synthesis ← Implementation ← Bitstream ← Hardware Manager ← Program.
- **לתרגל עוד:** HDLBits Mux2to1, Fadd, Adder3."""
    data = {"title": "שבוע 2 · מפגש 2: Mux, Decoder ומחבר ripple", "chapter_md": chapter, "summary_md": summary,
            "topics": ["דקדוק SystemVerilog", "Mux", "Decoder", "מחבר ripple", "Vivado"],
            "glossary": [], "course_facts": [], "syllabus_covered": [], "exam_type": "mcq", "grade_weights": [], "homework": [],
            "exercises": [dict(x, exam_style=False, uncertain=False) for x in EX],
            "questions": [dict(question=q, options=o, correct=c, explanation=e, topic=t, difficulty=d) for q, o, c, e, t, d in QUIZ],
            "verification": {"fixes": ["נכתב מחדש על ידי Claude בגישה של הבנה לפני כתיבה (בקשתו 13/11/2026). הפינים מ-fpga/pa35t_edu.xdc."],
                             "uncertain": ["שמות הכפתורים ב-Vivado לפי גרסאות 2023-2025; אם שם שונה מעט ב-2025.2 – הסדר זהה."]}}
    out = Path(__file__).resolve().parents[1] / "vlsi-w2s2.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(chapter))


if __name__ == "__main__":
    main()
