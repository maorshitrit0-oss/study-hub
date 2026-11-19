"""Micro: one OPEN code-understanding question a week (his exam: 6 multiple choice + 2 open code questions, 19/11/2026).
Every output was run: w1.c, w2.c in gcc (micro_open_1911/); the Arduino trace of week 3 in python below.
  python micro_open_1911.py -> chapters/micro-open-1911.json (publish inspect=exercises; adds to lecture N + week N)"""
import json
from pathlib import Path

C = lambda c: "```c\n" + c.strip() + "\n```"  # noqa: E731
TAIL = "\n\n✍️ *שאלה פתוחה כמו במבחן (10 נק'): לכתוב במחברת את הדרך – ערכים בבינארי, שורה אחרי שורה – ורק אחר כך לפתוח את הפתרון.*"


def trace(reads, edge=True):
    last, c = "H", 0
    for n in reads:
        if (last == "H" or not edge) and n == "L":
            c += 1
        last = n
    return c


assert trace("HHLLLHLHHL") == 3 and trace("HHLLLHLHHL", edge=False) == 5 and trace("HLHLLLH") == 2

W1 = {"add": True, "kind": "lecture", "number": 1, "week": 1, "lock": True, "exam_style": True,
      "title": "🧩 שאלה פתוחה: מעקב אחרי פעולות ביטים",
      "question_md": "נתון הקוד הבא (ב-C):\n\n" + C(open(Path(__file__).with_name("micro_open_1911") / "w1.c").read().split("int main(void) {")[1].rsplit("return 0;", 1)[0]) +
      "\n\n**א.** מה ערכו של `x` (בהקסה ובבינארי) אחרי כל אחת משלוש הפעולות? (3 הדפסות)\n\n**ב.** מה תדפיס שורת ה-`if`? הסבר.\n\n"
      "**ג.** מה מדפיסה השורה האחרונה, ומה היא \"שולפת\" מתוך `x`?\n\n**ד.** כתוב שורה אחת שמכבה את ביטים 0–3 בלי לגעת בשאר." + TAIL,
      "solution_md": r"""### א. מעקב שורה אחרי שורה
| שורה | פעולה | בינארי | הקסה |
|---|---|---|---|
| התחלה | | `1011 0100` | `0xB4` |
| `x \|= (1<<1)` | **הדלקת** ביט 1 (מסכה `0000 0010`) | `1011 0110` | `0xB6` |
| `x &= ~(1<<4)` | **כיבוי** ביט 4 (מסכה `1110 1111`) | `1010 0110` | `0xA6` |
| `x ^= 0x0F` | **היפוך** ביטים 0–3 (`0110`⇐`1001`) | `1010 1001` | `0xA9` |

### ב. `bit7 on`
$x \,\&\, (1\ll7)$ = `1010 1001 & 1000 0000` = `1000 0000` ≠ 0 ⇐ התנאי אמת. (בודקים ביט עם AND ומסכה של ביט אחד.)

### ג. מדפיס `4: 2`
`x >> 2` = `0010 1010`; `& 0x3` משאיר את שני הביטים התחתונים = `10` = **2**. כלומר השורה שולפת את **ביטים 2–3** של `x` כמספר.

### ד. כיבוי ביטים 0–3
```c
x &= ~0x0F;   /* = x &= 0xF0 */
```

✅ נבדק בהרצה (gcc): `0xB6`, `0xA6`, `0xA9`, `bit7 on`, `2`.

💡 **הרעיון:** OR מדליק, AND עם מסכה הפוכה מכבה, XOR הופך, הזזה + AND שולפת שדה."""}

W2 = {"add": True, "kind": "lecture", "number": 2, "week": 2, "lock": True, "exam_style": True,
      "title": "🧩 שאלה פתוחה: באג בפונקציית Setter (Bit Packing)",
      "question_md": "בבית אחד שמורים נתוני כלב: ביטים 0–3 גיל, ביט 4 \"שמח\", ביטים 5–7 גודל.\n\n" +
      C(open(Path(__file__).with_name("micro_open_1911") / "w2.c").read().split("#include <stdint.h>")[1].rsplit("return 0;", 1)[0] + "    return 0;\n}") +
      "\n\n**א.** מה מודפס בשורה `a`? פרק את הבית לשדות.\n\n**ב.** מה מודפס בשורה `b`? למה הגיל יצא 15 ולא 6?\n\n"
      "**ג.** הסבר את התיקון ב-`dog_set_age` ומה מודפס בשורה `c`.\n\n**ד.** למה ב-`dog_set_age` יש גם `age & AGE_MASK`?" + TAIL,
      "solution_md": r"""### א. `a: 0x79`
- גודל: `3 << 5` = `0110 0000` (`0x60`)
- גיל: `|= 9` ⇐ `0000 1001` – עובד רק כי השדה היה ריק
- שמח: `|= 0x10` ⇐ `0001 0000`

סה"כ `0111 1001` = **`0x79`** ⇐ גודל 3, שמח 1, גיל 9.

### ב. `b: 0x7F age=15`
`dog_set_age_bug` עושה רק OR: `1001 | 0110 = 1111` ⇐ הביטים הישנים של 9 **לא נמחקו**, ולכן הגיל = 15.
בית: `0111 1111` = `0x7F`.

### ג. התיקון: קודם לנקות, אחר כך לכתוב
```c
d->data = (d->data & ~AGE_MASK) | (age & AGE_MASK);
```
1. `d->data & ~0x0F` = `0111 1111 & 1111 0000` = `0111 0000` – מחקנו רק את שדה הגיל.
2. `| 0110` ⇐ `0111 0110` = **`0x76`**.

מודפס: `c: 0x76 age=6 size=3` – השדות האחרים לא נפגעו.

### ד. הגנה על השדות השכנים
אם יעבירו גיל גדול מ-15 (למשל 18 = `1 0010`), בלי המסכה הביט העליון היה "דולף" לביט 4 ומשנה את "שמח". המסכה חותכת ל-4 ביטים.

✅ נבדק בהרצה (gcc): `0x79`, `0x7F age=15`, `0x76 age=6 size=3`.

💡 **הרעיון:** כתיבה לשדה = **נקה (AND עם ~מסכה) ואז כתוב (OR)**. OR לבד רק מוסיף אחדות."""}

W3 = {"add": True, "kind": "lecture", "number": 3, "week": 3, "lock": True, "exam_style": True,
      "title": "🧩 שאלה פתוחה: ספירת לחיצות עם זיהוי קצה",
      "question_md": "כפתור בין GPIO 4 ל-GND, לד ב-GPIO 2:\n\n" + C('''
const int BTN = 4, LED = 2;
int count = 0;
int last = HIGH;

void setup() {
    pinMode(BTN, INPUT_PULLUP);
    pinMode(LED, OUTPUT);
}

void loop() {
    int now = digitalRead(BTN);
    if (last == HIGH && now == LOW) {
        count++;
        digitalWrite(LED, count % 2);
    }
    last = now;
}''') + "\n\n**א.** מה מזהה התנאי `last == HIGH && now == LOW`? (מה קורה פיזית בכפתור)\n\n"
      "**ב.** ב-10 סיבובים של `loop` נקרא מהכפתור: `H H L L L H L H H L`. מה `count` בסוף, והאם הלד דולק?\n\n"
      "**ג.** מחקו את `last == HIGH &&` מהתנאי. מה `count` עבור אותה סדרה? למה זה גרוע?\n\n"
      "**ד.** לחיצה **אחת** עם קפיצות מגע נקראת `H L H L L L H`. כמה פעמים יגדל `count`? איך מתקנים?" + TAIL,
      "solution_md": r"""### א. קצה יורד = רגע הלחיצה
עם `INPUT_PULLUP`: משוחרר = HIGH, לחוץ = LOW. המעבר HIGH⇐LOW קורה **פעם אחת** בכל לחיצה, גם אם מחזיקים את הכפתור הרבה סיבובים.

### ב. `count = 3`, הלד **דולק**
| סיבוב | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `now` | H | H | L | L | L | H | L | H | H | L |
| קצה? | | | ✓ | | | | ✓ | | | ✓ |
| `count` | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 3 |

$3\bmod2=1$ ⇐ `digitalWrite(LED, 1)` ⇐ דולק.

### ג. בלי `last`: `count = 5`
כל סיבוב שבו הכפתור **מוחזק** נספר (5 פעמים L). מספר הספירות תלוי במהירות הלולאה ובכמה זמן מחזיקים – לא במספר הלחיצות.

### ד. גדל **פעמיים** (צריך פעם אחת)
הקפיצה `H L H L` יוצרת שני קצוות יורדים. התיקון – **debounce**: לקבל מצב חדש רק אחרי שהוא יציב זמן מה, למשל:
```c
if (now != last) lastChange = millis();
if (millis() - lastChange > 20 && now != stable) {
    stable = now;
    if (stable == LOW) count++;
}
last = now;
```

✅ הסדרות נבדקו בסימולציה (3, 5, 2).

💡 **הרעיון:** סופרים **מעברים**, לא מצבים – ומסננים קפיצות מגע לפני שסופרים."""}

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "micro-open-1911.json"
    out.write_text(json.dumps([W1, W2, W3], ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
