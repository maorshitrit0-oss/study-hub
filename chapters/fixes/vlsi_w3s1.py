"""Self-study, week 3 session 1 (SystemVerilog: module, ports, logic, assign vs always_comb) - in the approved format
of 2.2 (13/11/2026): today's grammar -> blocks line by line -> climbing exercises -> FULL simulation guide (Vivado +
EDA Playground) -> board practice (7-segment, finding the display polarity live with two switches).
All code is in vlsi_w3s1_sv/ and was run in Icarus Verilog 12 (-g2012): both muxes agree on all 8 inputs; the
7-segment table lights the right segments for all 16 digits; the XOR exercise matches; the enable version goes dark.
  python vlsi_w3s1.py -> chapters/vlsi-w3s1.json  (published as lecture 5 of the self-study course)"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent / "vlsi_w3s1_sv"
src = lambda n: (D / n).read_text(encoding="utf-8").rstrip()  # noqa: E731
code = lambda c: "```systemverilog\n" + c + "\n```"  # noqa: E731
MUX, TBM, HEX, TOP = src("mux.sv"), src("tb_mux.sv"), src("hex7seg.sv"), src("top.sv")
XDC = "\n".join(l for l in (Path(__file__).resolve().parents[2] / "fpga" / "pa35t_edu.xdc").read_text(encoding="utf-8").splitlines()
                if l.startswith("set_property") and (any(f"{{{p}[" in l for p in ("seg1", "dig1"))
                                                     or any(f"{{sw[{i}]}}" in l for i in range(8))))  # only the ports of top
EX = src("ex.sv").split("module hex7seg_en")[0].rstrip()

GRAMMAR = r"""## 🧭 איך המפגש הזה בנוי
המפגש פותח את **שלב ב – השפה צעד אחר צעד**. היום לומדים לכתוב רכיב צירופי (בלי זיכרון) **בשתי דרכים** – `assign`
ו-`always_comb` – ולבחור ביניהן. אחר כך: Mux בשתי הדרכים ובדיקה שמוכיחה שהן זהות, מפענח לתצוגת 7 מקטעים, תרגול
שמטפס בהדרגה, סימולציה מלאה, ולוח: ספרה הקסדצימלית מהמתגים על התצוגה.

## 📘 הדקדוק של היום – 6 חלקים

**1. מודול ופורטים (חזרה קצרה).**
```systemverilog
module mux2_assign (
    input  logic a, b, s,     // three 1-bit inputs
    output logic y            // one 1-bit output
);
    // the logic
endmodule
```
- רשימת הפורטים בסוגריים; **פסיק** בין פורטים, **בלי פסיק** אחרי האחרון; `);` סוגר את הרשימה.
- כמה פורטים מאותו סוג בשורה אחת: `input logic a, b, s`.

**2. `logic` – הטיפוס של היום.** ב-SystemVerilog כותבים `logic` כמעט לכל דבר: פורטים וחוטים פנימיים.
- ב-Verilog הישנה היו שניים: `wire` (חוט – רק `assign` מחובר אליו) ו-`reg` (משתנה בתוך `always`). `logic` מחליף את
  שניהם: אפשר לתת לו ערך גם ב-`assign` וגם ב-`always`. **הכלל היחיד:** לכל `logic` יש **מקור אחד** – או `assign` אחד,
  או בלוק `always` אחד. שני מקורות לאותו אות = שגיאה.

**3. `assign` – חוט קבוע.** `assign y = s ? b : a;` – y מחובר **תמיד** לביטוי. מתאים כשהלוגיקה היא **ביטוי אחד**.

**4. `always_comb` – כמה צעדים שמחושבים מחדש בכל שינוי.**
```systemverilog
always_comb begin
    if (s)
        y = b;
    else
        y = a;
end
```
- `begin ... end` = הסוגריים של הבלוק (כמו `{ }` בג'אווה). בתוכו משתמשים ב-`=`.
- מתאים כשנוח לחשוב ב"אם... אחרת..." או בטבלה (`case`).
- **חובה לתת ערך ל-y בכל מסלול** (if וגם else, או `default` ב-case). אחרת הכלי "זוכר" את הערך הקודם = latch בטעות.

**5. `if` ו-`case` בתוך `always_comb`.** `if (תנאי) ... else ...` לשתי אפשרויות; `case (x) ... default: ... endcase` לטבלה.
`4'hA` = מספר של 4 ביטים בהקסה (10).

**6. השוואות:** `==` שווה, `!=` שונה (בתוך תנאים). בבדיקות (testbench) משתמשים ב-`!==` – "שונה, גם אם אחד מהם X
(לא ידוע)".

> ⭐ **הכלל לבחירה:** ביטוי אחד ← `assign`. החלטות או טבלה ← `always_comb`. החומרה שנבנית – אותה חומרה."""

MUX_MD = r"""## 1. Mux 2:1 – אותו רכיב בשתי דרכים
""" + code(MUX) + r"""

**שורה אחרי שורה:**
- `mux2_assign`: שורה אחת – `s ? b : a` ("אם s אז b, אחרת a").
- `mux2_comb`: אותו דבר כצעדים – `if (s) y = b; else y = a;`. שני הענפים נותנים ערך ל-y ← אין latch.
- בסינתזה **שניהם הופכים לאותו Mux** – ההבדל הוא רק בדרך הכתיבה.

### בדיקה שמוכיחה ששתי הגרסאות זהות
""" + code(TBM) + r"""

**שורה אחרי שורה:**
- `mux2_assign u1 (...)` ו-`mux2_comb u2 (...)` – שני הרכיבים מקבלים **אותן** כניסות.
- `for (int i = 0; i < 8; i++)` – לולאה על כל 8 הצירופים (3 כניסות ← $2^3=8$).
- `{s, a, b} = i;` – **שרשור**: מפרקים את המספר i (0..7) לשלושה ביטים: s הביט השמאלי, b הימני.
- `if (y1 !== y2) errors++;` – סופרים הבדלים.
- **אמור להופיע:** 8 שורות, ובסוף `OK: both muxes agree on all 8 inputs` (נבדק).

💡 **בדיקה שעוברת על כל הצירופים** נקראת בדיקה ממצה (exhaustive) – אפשרית כשיש מעט כניסות."""

HEX_MD = r"""## 2. מפענח לתצוגת 7 מקטעים
**מה הוא עושה:** מקבל ספרה הקסדצימלית (0..F, 4 ביטים) ומחליט אילו מ-7 המקטעים (a עד g) להדליק.

```text
 aaa
f   b
 ggg
e   c
 ddd
```
""" + code(HEX) + r"""

**שורה אחרי שורה:**
- `output logic [6:0] seg` – 7 ביטים: `seg[0]`=a, `seg[1]`=b, ... `seg[6]`=g. הכתיבה `7'b0111111` היא **g..a משמאל לימין**.
- `4'h0: seg = 7'b0111111;` – ל-0 מדליקים a,b,c,d,e,f (בלי g, הקו האמצעי).
- `4'h1: seg = 7'b0000110;` – ל-1 רק b ו-c (הצד הימני).
- `default:` – תופס את F (ומבטיח ערך לכל קלט).
- נבדק בסימולציה: לכל 16 הספרות נדלקים בדיוק המקטעים הנכונים.

> ⚠️ **קוטביות:** כאן 1 = מקטע דולק. בהרבה לוחות זה הפוך (0 = דולק). בלוח שלך זה לא כתוב במדריך – את זה נגלה היום
> על הלוח עם מתג אחד, בלי לבנות מחדש."""

VIVADO_MD = r"""## 🖥️ סימולציה – הסדר המלא (חוזר בכל מפגש עד 6.2)
### דרך א: Vivado 2025.2 (במחשב – להפעיל כמנהל: קליק ימני ← Run as administrator)
1. **פותחים:** `Open Project` ← `C:\fpga\mini_tpu`.
2. **קובץ הרכיבים:** `Flow Navigator` ← `PROJECT MANAGER` ← **`Add Sources`** ← `Add or create design sources` ←
   `Create File` ← File type: **SystemVerilog**, שם: `mux` ← `OK` ← `Finish` (חלון Define Module – `OK`).
3. ב-**`Sources`** ← `Design Sources` ← לחיצה כפולה על `mux.sv` ← מוחקים את השלד (Ctrl+A, Delete) ← מדביקים את
   **שני** הרכיבים ← **Ctrl+S**:

""" + code(MUX) + r"""

4. **קובץ הבדיקה:** שוב `Add Sources` ← **`Add or create simulation sources`** ← `Create File` ← SystemVerilog, שם
   **`tb_mux`** ← `Finish` ← ב-`Sources` ← `Simulation Sources` ← `sim_1` ← לחיצה כפולה על `tb_mux.sv` ← מוחקים
   את השלד ← מדביקים ← **Ctrl+S**:

""" + code(TBM) + r"""

5. `Simulation Sources` ← לחיצה ימנית על `tb_mux` ← **`Set as Top`**.
6. `SIMULATION` ← **`Run Simulation`** ← **`Run Behavioral Simulation`**.
7. **מה אמור להופיע:** ב-**`Tcl Console`** 8 שורות `s=.. a=.. b=.. -> assign:.. always_comb:..` ובסוף
   **`OK: both muxes agree on all 8 inputs`** ✅. בחלון הגלים: `Zoom Fit` – y1 ו-y2 נראים זהים.
8. **שגיאות נפוצות היום** (לשונית `Messages`, השורה האדומה הראשונה):
   - פסיק אחרי הפורט האחרון ברשימה → "syntax error near )".
   - `y` מקבל ערך גם ב-`assign` וגם ב-`always_comb` → "multiple drivers".
   - שכחת `else` ב-`always_comb` → אזהרה על latch (בסימולציה זה ירוץ, בסינתזה זה שגוי).
   מתקנים ← Ctrl+S ← `Run Behavioral Simulation` שוב (סגירת הקודמת – `Yes`).

### דרך ב: EDA Playground (בדפדפן, גם מהטלפון)
1. https://www.edaplayground.com ← `Log in` (חשבון גוגל).
2. שמאל: **SystemVerilog/Verilog**, `Tools & Simulators` ← **Icarus Verilog 12.0**.
3. `testbench.sv` (שמאל) ← הבדיקה; `design.sv` (ימין) ← שני ה-mux.
4. **`Run`** ← בלשונית `Log` למטה אמור להופיע `OK: both muxes agree on all 8 inputs`."""

BOARD_MD = r"""## 🔧 היום על הלוח (תרגול): ספרה על תצוגת 7 המקטעים
המתגים SW1–SW4 הם הספרה (0..F). **SW8 הופך את קוטביות המקטעים, SW7 הופך את קוטביות בחירת הספרות** – כך מגלים את
הקוטביות של הלוח **בלי לבנות מחדש**. כל ארבע הספרות של תצוגה 1 יציגו את אותה ספרה. הצעדים המלאים – בתרגיל "תרגול
על הלוח"."""

QUIZ = [
    ("מה ההבדל בין `assign` ל-`always_comb`?", ["assign לביטוי אחד, always_comb לצעדים/החלטות – שניהם בונים לוגיקה צירופית", "assign יוצר זיכרון ו-always_comb לא", "always_comb רץ רק בעליית שעון", "assign עובד רק בסימולציה"], 0,
     "שניהם צירופיים (בלי זיכרון); ההבדל בדרך הכתיבה.", "assign מול always_comb", 1),
    ("מה יקרה אם ב-`always_comb` יש `if (s) y = b;` בלי `else`?", ["נוצר latch – הכלי זוכר את הערך הקודם כש-s=0", "y יהיה 0 כש-s=0", "שגיאת תחביר", "y יהיה a"], 0,
     "בלי ערך בכל מסלול, הכלי חייב לזכור = latch בטעות.", "always_comb", 2),
    ("מה ההבדל בין `logic` ל-`wire`?", ["logic יכול לקבל ערך גם מ-assign וגם מבלוק always; wire רק מ-assign", "אין הבדל בכלל", "wire הוא 4 ביטים ו-logic ביט אחד", "logic יוצר תמיד אוגר"], 0,
     "logic מחליף את wire ואת reg; הכלל: מקור אחד לכל אות.", "logic", 2),
    ("מה עושה `{s, a, b} = 5;`?", ["s=1, a=0, b=1 – מפרק את 101 לשלושה ביטים", "s=a=b=5", "s=5 וה-a,b לא משתנים", "שגיאה"], 0,
     "שרשור: הביט השמאלי ל-s, הימני ל-b. 5 = 101.", "שרשור", 2),
    ("במפענח, `4'h1: seg = 7'b0000110;` – אילו מקטעים דולקים?", ["b ו-c", "a ו-b", "f ו-g", "d ו-e"], 0,
     "הכתיבה היא g..a משמאל לימין: הביטים 1 ו-2 = b ו-c.", "7 מקטעים", 2),
    ("למה בבדיקה משתמשים ב-`!==` ולא ב-`!=`?", ["!== מזהה גם הבדל כשאחד הערכים X (לא ידוע)", "!== מהיר יותר", "!= לא קיים בשפה", "אין הבדל"], 0,
     "!= עם X נותן X ולא 'אמת' – ההבדל היה מתפספס.", "Testbench", 3),
    ("כמה צירופים יש לבדוק בבדיקה ממצה של רכיב עם 3 כניסות של ביט?", ["8", "3", "6", "9"], 0, "$2^3=8$.", "Testbench", 1),
    ("איך מגלים את קוטביות התצוגה בלוח בלי לבנות מחדש?", ["מתג שמחליף בין התבנית להיפוך שלה (`sw[7] ? ~p : p`)", "מחברים מודד", "משנים את קובץ ה-XDC", "אי אפשר"], 0,
     "בחירה בזמן ריצה: שני המצבים צרובים, המתג בוחר.", "לוח", 2),
]

EXS = [
    dict(title="🔧 תרגול על הלוח: ספרה הקסדצימלית על תצוגת 7 מקטעים",
         question_md="""SW1–SW4 = ספרה 0..F על תצוגה 1. SW8 ו-SW7 – לגלות את הקוטביות. **קודם מוודאים שהסימולציה עובדת.**""",
         solution_md="""**שלב 1 – קבצים:** `hex7seg` (מהפרק) כ-design source, ועוד קובץ `top`:

""" + code(TOP) + """

- `hex7seg u_dec (.x(sw[3:0]), .seg(pat));` – המפענח מקבל את 4 המתגים הראשונים.
- `{1'b0, pat}` – 8 ביטים: הנקודה (dp) כבויה + 7 המקטעים.
- `sw[7] ? ~... : ...` – SW8 למעלה = הופכים את כל הביטים.
- `dig1 = sw[6] ? 4'b0000 : 4'b1111` – SW7 בוחר אם הספרות פעילות ב-1 או ב-0.
- `top` ← לחיצה ימנית ← **`Set as Top`**.

**שלב 2 – XDC** (`Add Sources` ← constraints ← קובץ `pins`; אם יש כבר קובץ מהמפגש הקודם – להחליף בו את התוכן):
```text
""" + XDC + """
```

**שלב 3 – כמו במפגש הקודם:** `Run Synthesis` ← `Run Implementation` ← `Generate Bitstream` ← `Open Hardware Manager` ←
`Open target` ← `Auto Connect` ← `Program device`.

**שלב 4 – גילוי הקוטביות (5 דקות):**
1. SW1–SW4: מעלים את SW1 ו-SW3 (= 5).
2. מנסים את 4 המצבים של SW7 ו-SW8 עד שמופיע **5** תקין.
3. **רושמים:** SW8 ___ (למעלה = מקטעים פעילים ב-0), SW7 ___ (למעלה = ספרות פעילות ב-0). זה ישמש בכל המפגשים הבאים.
4. בודקים כמה ספרות: SW1–SW4 כולם למטה = **0**, כולם למעלה = **F**, SW2+SW4 (1010) = **A**.

**אם לא עובד:** שום דבר לא נדלק באף מצב → `Messages` (אולי חסרה שורה ב-XDC); ספרה "מבולגנת" בכל המצבים → סדר
המקטעים בלוח שונה (לרשום איזה מקטע נדלק לכל ביט ולשלוח לי).""", topic="תרגול על הלוח"),
    dict(title="מה הקוד עושה 1 · Mux ב-always_comb",
         question_md="""```systemverilog
always_comb begin
    if (s)
        y = b;
    else
        y = a;
end
```
מה יהיה `y` כש-`a=1, b=0, s=0`?

**א.** `y = 1`

**ב.** `y = 0`

**ג.** `y = x` (לא מוגדר)

**ד.** נוצר latch ו-`y` שומר את הערך הקודם""",
         solution_md="""### התשובה: **א** ✅

**הדרך המלאה:**
1. `always_comb` רץ מחדש בכל שינוי של `a`, `b` או `s`.
2. `s = 0` ⇐ התנאי `if (s)` שקר ⇐ נכנסים ל-`else`.
3. `y = a = 1`.

**למה לא האחרות:**
- **ב** – זה הערך של `b`, שנבחר רק כש-`s = 1`.
- **ג** – כל הכניסות מוגדרות, ולכן גם המוצא.
- **ד** – יש `else`, אז `y` מקבל ערך בכל מסלול – אין latch.""", topic="always_comb"),
    dict(title="מה הקוד עושה 2 · שרשור ביטים",
         question_md="""```systemverilog
logic s, a, b;
initial begin
    {s, a, b} = 6;
end
```
מה הערכים אחרי ההשמה?

**א.** `s=1, a=1, b=0`

**ב.** `s=0, a=1, b=1`

**ג.** `s=1, a=0, b=1`

**ד.** `s=0, a=0, b=1`""",
         solution_md="""### התשובה: **א** ✅

**הדרך המלאה:**
1. `{s, a, b}` מחבר שלושה ביטים למספר אחד: `s` הוא הביט השמאלי (הכי משמעותי), `b` הימני.
2. 6 בבינארי בשלושה ביטים = `110`.
3. מחלקים משמאל לימין: `s=1`, `a=1`, `b=0`.

**למה לא האחרות:**
- **ב** – זה 3 (`011`), סדר הפוך.
- **ג** – זה 5 (`101`).
- **ד** – זה 1 (`001`).""", topic="assign מול always_comb"),
    dict(title="מה הקוד עושה 3 · מפענח 7 מקטעים",
         question_md="""```systemverilog
always_comb begin
    case (x)               //        gfedcba
        4'h1:    seg = 7'b0000110;
        4'h7:    seg = 7'b0000111;
        4'h8:    seg = 7'b1111111;
        default: seg = 7'b0000000;
    endcase
end
```
`x = 4'h7`. אילו מקטעים דולקים, ומה מוצג?

**א.** a, b, c – הספרה 7

**ב.** e, f, g – הספרה 7

**ג.** b, c – הספרה 1

**ד.** כל המקטעים – הספרה 8""",
         solution_md="""### התשובה: **א** ✅

**הדרך המלאה:**
1. `x = 4'h7` ⇐ השורה `4'h7: seg = 7'b0000111`.
2. סדר הביטים לפי ההערה: משמאל `g f e d c b a`.
3. שלושת הביטים הימניים הם 1 ⇐ `c`, `b`, `a` דולקים.
4. a (למעלה) + b ו-c (הצד הימני) = הצורה של **7**.

**למה לא האחרות:**
- **ב** – קרא את הביטים מהצד הלא נכון.
- **ג** – זו השורה של `4'h1`.
- **ד** – זו השורה של `4'h8`.""", topic="7 מקטעים"),
    dict(title="מה הקוד עושה 4 · היפוך קוטביות עם מתג",
         question_md="""```systemverilog
hex7seg u_dec (.x(sw[3:0]), .seg(pat));
assign seg1 = sw[7] ? ~{1'b0, pat} : {1'b0, pat};
```
(`hex7seg` נותן לספרה 1 את `pat = 7'b0000110`.) מה `seg1` כש-`sw = 8'b1000_0001`?

**א.** `8'b11111001`

**ב.** `8'b00000110`

**ג.** `8'b10000110`

**ד.** `8'b01111001`""",
         solution_md="""### התשובה: **א** ✅

**הדרך המלאה:**
1. `sw[3:0] = 0001` ⇐ הספרה 1 ⇐ `pat = 0000110`.
2. `{1'b0, pat}` = מוסיפים 0 משמאל (הנקודה כבויה) ⇐ `00000110`.
3. `sw[7]` הוא הביט השמאלי של `sw` = **1** ⇐ בוחרים את ההיפוך `~`.
4. `~00000110 = 11111001`.

**למה לא האחרות:**
- **ב** – זה המצב כש-`sw[7] = 0` (בלי היפוך).
- **ג** – הפך רק את הביט העליון.
- **ד** – הפך את כל הביטים, אבל של `{1'b1, pat}` – שרשור לא נכון.""", topic="7 מקטעים"),
    dict(title="🔧 תרגול מעשי 1 · ✏️ להשלים את החסר – Mux ב-always_comb",
         question_md="""```systemverilog
module mux2_comb (
    input  logic a, b, s,
    output logic y
);
    ___ begin
        if (___)
            y = b;
        ___
            y = a;
    ___
endmodule
```""",
         solution_md="""`always_comb` · `s` · `else` · `end`. בלי `else` – latch.

**עוד תרגול (בדיקה מיידית):** https://hdlbits.01xz.net/wiki/Always_if – אותו Mux בשתי הדרכים, בדיוק כמו היום.""",
         topic="always_comb"),
    dict(title="🔧 תרגול מעשי 2 · לשנות – מפענח עם כיבוי",
         question_md="""הוסף ל-`hex7seg` כניסה `en`: כש-`en = 0` התצוגה כבויה (כל המקטעים 0), כש-`en = 1` – רגיל.
רמז: אפשר לעטוף את המפענח הקיים ולהוסיף `assign` אחד.""",
         solution_md="""```systemverilog
module hex7seg_en (
    input  logic [3:0] x,
    input  logic       en,
    output logic [6:0] seg
);
    logic [6:0] pat;
    hex7seg u (.x(x), .seg(pat));
    assign seg = en ? pat : 7'b0000000;   // en = 0 -> display dark
endmodule
```
- משתמשים ברכיב הקיים (instantiation) ולא כותבים מחדש את הטבלה.
- נבדק: `x=3, en=1` ← `1001111`; `en=0` ← `0000000`.

💡 **ככה כותבים קוד חדש:** לוקחים רכיב שעובד ועוטפים או משנים דבר אחד.""",
         topic="7 מקטעים"),
    dict(title="🔧 תרגול מעשי 3 · ✍️ לכתוב לבד – XOR בשתי דרכים + בדיקה",
         question_md="""כתוב:
1. `xor_assign` – XOR של שני ביטים עם `assign`.
2. `xor_comb` – אותו דבר עם `always_comb` ו-`if` (בלי האופרטור `^`).
3. `tb_xor` – בדיקה ממצה (4 צירופים) שמדפיסה `OK` אם הגרסאות זהות.

**סולם רמזים:** (1) `^` הוא XOR. (2) XOR = 1 כשהביטים **שונים** ← `if (a == b) y = 0; else y = 1;`.
(3) העתק את המבנה של `tb_mux`: לולאה עד 4, `{a, b} = i;`.

**עוד:** https://hdlbits.01xz.net/wiki/Xnorgate ו-https://hdlbits.01xz.net/wiki/Truthtable1""",
         solution_md=code(EX) + """

**אמור להופיע:** 4 שורות ואז `OK: same truth table` (נבדק ב-Icarus Verilog).""",
         topic="assign מול always_comb"),
]


def _spread(exs):
    """The 'what does this code do' answers are written with the right one at א; move it to א/ב/ג/ד in turn."""
    import re as _re
    L = "אבגד"
    out, k = [], 0
    for x in exs:
        if not x["title"].startswith("מה הקוד עושה"):
            out.append(x)
            continue
        want = [0, 2, 1, 3][k % 4]
        k += 1
        q, sol = x["question_md"], x["solution_md"]
        first = q.index("\n\n**א.** ")
        opts = _re.findall(r"\n\n\*\*([אבגד])\.\*\* (.*?)(?=\n\n\*\*[אבגד]\.\*\* |$)", q[first:], _re.S)
        order = [1, 2, 3]
        order.insert(want, 0)                         # new position -> old index
        newq = q[:first] + "".join(f"\n\n**{L[i]}.** {opts[o][1]}" for i, o in enumerate(order))
        m = {L[o]: L[i] for i, o in enumerate(order)}
        sol = _re.sub(r"\*\*([אבגד])\*\*", lambda mm: f"**{m[mm.group(1)]}**", sol)
        lines = sol.split("\n")                       # keep "why not" in א..ד order
        idx = [i for i, l in enumerate(lines) if _re.match(r"- \*\*[אבגד]\*\* –", l)]
        if idx:
            block = sorted((lines[i] for i in idx), key=lambda l: L.index(l[4]))
            for i, l in zip(idx, block):
                lines[i] = l
        out.append(dict(x, question_md=newq, solution_md="\n".join(lines)))
    return out


def main():
    chapter = "\n\n".join([GRAMMAR, MUX_MD, HEX_MD, VIVADO_MD, r"""## 🎤 שאלות הראיון של היום – תשובות קצרות
- **מה ההבדל בין `logic` ל-`wire`?** `wire` הוא חוט שרק `assign` (או יציאה של רכיב) יכול לדחוף. `logic` יכול לקבל ערך
  גם מ-`assign` וגם מבלוק `always`, ומחליף את `wire` ואת `reg` – בתנאי שיש לו **מקור אחד**. (לאות עם כמה מקורות,
  כמו באס משותף, עדיין צריך `wire`.)
- **מתי `always_comb` ולא `assign`?** כשהלוגיקה היא החלטות או טבלה (`if`, `case`) – קריא יותר. `always_comb` גם
  מזהיר כשנוצר latch בטעות. לביטוי אחד – `assign`.""", BOARD_MD])
    summary = r"""## 🎯 המסר של המפגש
- **`assign`** = ביטוי אחד, חוט קבוע. **`always_comb`** = צעדים / `if` / `case`; ערך ל-y **בכל מסלול** (else / default) – אחרת latch.
- **`logic`** מחליף את wire ו-reg; מקור אחד לכל אות.
- **בדיקה ממצה:** לולאה על כל הצירופים, `{s, a, b} = i;`, השוואה עם `!==`.
- **7 מקטעים:** `case` על 16 ספרות, `7'b...` = g..a. הקוטביות של הלוח נמצאת עם מתג (`sw[7] ? ~p : p`).
- **Vivado:** design source ← simulation source ← Set as Top ← Run Behavioral Simulation ← Tcl Console."""
    data = {"title": "שבוע 3 · מפגש 1: SystemVerilog – module, logic, assign ו-always_comb", "chapter_md": chapter,
            "summary_md": summary, "topics": ["assign מול always_comb", "logic", "7 מקטעים", "Testbench", "Vivado"],
            "glossary": [], "course_facts": [], "syllabus_covered": [], "exam_type": "mcq", "grade_weights": [], "homework": [],
            "exercises": [dict(x, exam_style=False, uncertain=False) for x in _spread(
                [e for e in EXS if not e["title"].startswith("🔧")] + [e for e in EXS if e["title"].startswith("🔧 תרגול מעשי")]
                + [e for e in EXS if e["title"].startswith("🔧") and not e["title"].startswith("🔧 תרגול מעשי")])],
            "questions": [dict(question=q, options=o, correct=c, explanation=e, topic=t, difficulty=d) for q, o, c, e, t, d in QUIZ],
            "verification": {"fixes": ["נכתב על ידי Claude בפורמט שאושר (13/11/2026). כל הקוד הורץ ב-Icarus Verilog 12: שני ה-Mux זהים ב-8 הצירופים, המפענח נכון ב-16 הספרות, ה-XOR וגרסת ה-en נכונים. הפינים מ-fpga/pa35t_edu.xdc."],
                             "uncertain": ["קוטביות התצוגה וסדר המקטעים בלוח לא כתובים במדריך – לכן המתגים SW7/SW8 בתרגול על הלוח."]}}
    out = Path(__file__).resolve().parents[1] / "vlsi-w3s1.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(chapter))


if __name__ == "__main__":
    main()
