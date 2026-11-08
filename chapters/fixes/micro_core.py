"""Micro core exercises (weeks 1-3): checked against the exam papers / sources, re-solved, in full (08/11/2026)."""
import json

S = []

S.append({"id": "e161f6d5-5cd1-4f71-ba7a-7f2b2ae14a45", "uncertain": False, "solution_md": r"""
### מה בודקים פה
XOR (`^`) עם מסכה **הופך** בדיוק את הביטים שבהם במסכה יש 1, ולא נוגע בשאר. ופעמיים XOR עם אותה מסכה מחזיר את הערך המקורי, כי $a \oplus m \oplus m = a$.

### שלב 1: הערכים בבינארי
- `reg = 0x2A`: $0x2A = 2\cdot16+10 = 42 = 32+8+2$ ⇐ `0b00101010` (ביטים 1, 3, 5 דולקים).
- `mask = (1<<1) | (1<<5)`: `0b00000010 | 0b00100000 = 0b00100010`.

### שלב 2: XOR ראשון
```
  reg   0010 1010
^ mask  0010 0010
= after 0000 1000
```
ביטים 1 ו-5 היו 1 והתהפכו ל-0; ביט 3 לא במסכה ⇐ נשאר 1. ⇐ `0b00001000`.

### שלב 3: XOR שני
```
  reg   0000 1000
^ mask  0010 0010
= twice 0010 1010
```
ביטים 1 ו-5 חוזרים ל-1 ⇐ `0b00101010` – **בדיוק הערך המקורי**.

### התשובה: **ד** ✅
```
reg before      0b00101010
mask            0b00100010
reg after       0b00001000
reg after twice 0b00101010
```
> ⚠️ בגרסה הקודמת של הפתרון נכתב בטעות `0b00001010` לשורה האחרונה (התשובה שנבחרה, ד, הייתה נכונה).

**למה המסיחים לא נכונים:** א – כאילו XOR לא שינה כלום; ב – כאילו השני לא החזיר; ג – הופך רק ביט 1 (שוכח את ביט 5).

💡 **הרעיון:** `^ mask` = toggle; פעמיים = חזרה למקור. במבחן: לכתוב את שני המספרים אחד מעל השני ולעבור עמודה-עמודה.
"""})

S.append({"id": "70f90662-89d8-45b2-84c8-23a64766a5b8", "uncertain": False, "solution_md": r"""
### שלב 1: איזו הגדרה מכסה את כל התחום $0.2$–$1.6\,$V?
| הגדרה | תחום | מכסה $0.2$–$1.6$? |
|---|---|---|
| `ADC_0db` | $0.10$–$0.95$ | ❌ $1.6>0.95$ – רוויה |
| `ADC_2_5db` | $0.10$–$1.25$ | ❌ $1.6>1.25$ – רוויה |
| `ADC_6db` | $0.15$–$1.75$ | ✅ |
| `ADC_11db` | $0.15$–$3.10$ | ✅ אבל תחום רחב יותר |

שתי האפשרויות שמכסות: 6db ו-11db. **הרזולוציה הטובה יותר היא בתחום הצר יותר** – אותם 4096 ערכים מתחלקים על פחות וולטים.

### שלב 2: הרזולוציה (וולט לצעד)
12 ביט ⇐ $2^{12}=4096$ ערכים, כלומר 4095 צעדים בין המינימום למקסימום של **התחום**:
$$\Delta V=\frac{V_{max}-V_{min}}{2^{12}-1}=\frac{1.75-0.15}{4095}=\frac{1.6}{4095}\approx0.39\ \text{mV}$$
(להשוואה, 11db: $\frac{3.10-0.15}{4095}\approx0.72\,$mV – גרוע כמעט פי 2.)

### התשובה: **ב** – `ADC_6db`, רזולוציה כ-$0.391\,$mV ✅

**למה לא האחרות:**
- **א** (2.5db) – $1.6\,$V מעל $1.25\,$V ⇐ הקריאה נתקעת על 4095 (רוויה); ה-ADC לא "ממשיך מעל 4095".
- **ג** (11db) – עובד, אבל לא "ההגדרה היחידה", והרזולוציה גרועה יותר.
- **ד** (0db) – רוויה כבר מעל $0.95\,$V.

> ⚠️ תוקן: בגרסה הקודמת חושב $1.75/4096$ – צריך לחלק את **רוחב התחום** ($1.75-0.15$), וזה מה שנותן את $0.391\,$mV שבתשובה.

💡 **הרעיון:** קודם לוודא שהתחום מכסה את האות (בלי רוויה), ואז לבחור את התחום **הכי צר** ⇐ רזולוציה = רוחב התחום חלקי $2^n-1$.
"""})

S.append({"id": "c0f71e7d-c257-415c-8768-7374beb4a179", "uncertain": True, "solution_md": r"""
### מה צריך לעשות
הגיל שמור **בתוך** בית אחד, בביטים 2–6 (5 ביטים ⇐ 0 עד 31). שאר הביטים בבית שייכים לשדות אחרים – אסור לפגוע בהם. לכן עדכון שדה הוא תמיד **שני שלבים**:
1. **לנקות** את השדה: `*dog &= ~AGE_MASK` (ביטים 2–6 ל-0, השאר נשארים).
2. **להכניס** את הערך החדש במקום: `*dog |= (new_age << AGE_SHIFT)`.

בלי שלב 1, ה-OR רק "מוסיף" ביטים – אם הגיל היה 5 (`00101`) וכותבים 2 (`00010`), יוצא `00111` = 7. ❌

### הקבועים (כמו בתרגול)
```c
#define AGE_SHIFT 2                              // first bit of the age field
#define AGE_MASK  (0x1F << AGE_SHIFT)            // 0b01111100: bits 2..6
#define MAX_AGE   31                             // 5 bits -> 0..31
```

### הפתרון
```c
int dog_set_age(unsigned char* dog, int new_age) {
    if (dog == NULL) return -1;                         // no byte to write to
    if (new_age < 0 || new_age > MAX_AGE) return -1;    // does not fit in 5 bits
    *dog &= (unsigned char)~AGE_MASK;                   // step 1: clear bits 2..6 only
    *dog |= (unsigned char)(new_age << AGE_SHIFT);      // step 2: put the new age there
    return 0;                                           // success
}
```

### בדיקה עם מספרים
`*dog = 0b10010101` (גיל נוכחי: ביטים 2–6 = `00101` = 5), `new_age = 18` (`10010`):
- ניקוי: `0b10010101 & 0b10000011 = 0b10000001` – ביטים 0, 1, 7 נשמרו ✅
- `18 << 2 = 0b01001000`
- OR: `0b10000001 | 0b01001000 = 0b11001001` ⇐ ביטים 2–6 = `10010` = 18 ✅

> ⚠️ הפתרון הקודם כאן עשה רק OR (בלי הניקוי) ולא בדק את הקלט – זה הבאג הקלאסי שהתרגיל בא ללמד. שמות הקבועים כאן כמו בנוסח השאלה; אם בתרגול הם הוגדרו אחרת – אותו רעיון בדיוק.

💡 **הרעיון:** עדכון שדה בתוך רגיסטר/בית = **AND עם המסכה ההפוכה, ואז OR עם הערך המוזז**. זה בדיוק מה שעושים עם רגיסטרים של ESP32.
"""})

S.append({"id": "cf42a626-1f56-4185-9799-eb4dc6520498", "uncertain": False, "solution_md": r"""
### התשובה הקצרה
`volatile` אומר למהדר: **"הערך של המשתנה הזה יכול להשתנות מבחוץ – אל תניח שאתה יודע מה יש בו"**. לכן כל קריאה מהקוד באמת ניגשת לזיכרון, וכל כתיבה באמת נכתבת – המהדר לא "מקצר" אותן.

### למה צריך את זה
המהדר עושה אופטימיזציות: אם הוא רואה לולאה שקוראת משתנה שאף אחד בתוך הלולאה לא משנה, הוא מרשה לעצמו לקרוא אותו פעם אחת (לרגיסטר) ולהשתמש בעותק. במערכת משובצת זה שובר את התוכנית, כי משתנים משתנים "מאחורי הגב" של הקוד:
1. **שגרת פסיקה (ISR)** משנה דגל שהלולאה הראשית בודקת.
2. **רגיסטר חומרה** (GPIO, טיימר, UART) שהחומרה משנה בעצמה.
3. **משימה אחרת** (FreeRTOS) שכותבת לאותו משתנה.

### דוגמה – הבאג בלי volatile
```c
bool buttonEvent = false;              // WRONG: should be volatile
void IRAM_ATTR onButton() { buttonEvent = true; }   // set by the interrupt
void loop() {
    while (!buttonEvent) { }           // the compiler may read it once and loop forever
    buttonEvent = false;
}
```
עם `volatile bool buttonEvent = false;` הלולאה קוראת את הזיכרון בכל סיבוב ורואה את השינוי מהפסיקה. ✅

### מה volatile **לא** עושה (מלכודות מבחן – שאלה 7ד במועד ב')
- ❌ לא שומר את הערך אחרי כיבוי (זה זיכרון לא-נדיף, flash/NVS).
- ❌ לא מגן מהתנגשויות בין משימות (לזה צריך mutex / critical section / atomic).
- ❌ לא קשור לאמת/שקר.

💡 **הרעיון:** משתנה שמשותף ל-ISR ולתוכנית הראשית, או כתובת של רגיסטר חומרה ⇐ `volatile`.
"""})

S.append({"id": "19ec7fa7-7a62-4c11-a460-fa719aa13331", "uncertain": False, "solution_md": r"""
### הבעיה
כפתור מכני "מקפץ" (bounce): בלחיצה אחת המגע נפתח ונסגר כמה פעמים במשך כמה מילישניות. אם קוראים אותו ישר – לחיצה אחת נספרת כמה לחיצות.

### הרעיון
מקבלים מצב חדש **רק אם הקריאה נשארה זהה לפחות 20 ms ברצף**. בכל פעם שהקריאה משתנה – מאפסים את השעון ומתחילים לספור מחדש. משתמשים ב-`millis()` (ולא ב-`delay()`), כך שהתוכנית לא נעצרת.

### הקוד
```cpp
const int BTN = 4;                 // button between GPIO4 and GND
const unsigned long DEBOUNCE_MS = 20;

int lastReading = HIGH;            // last raw reading
int stableState = HIGH;            // the accepted (debounced) state
unsigned long lastChange = 0;      // when the raw reading last changed

void setup() {
  pinMode(BTN, INPUT_PULLUP);      // released = HIGH, pressed = LOW
  Serial.begin(115200);
}

void loop() {
  int reading = digitalRead(BTN);
  if (reading != lastReading) {          // the raw signal moved (bounce or a real press)
    lastChange = millis();               // restart the 20 ms count
    lastReading = reading;
  }
  if (millis() - lastChange >= DEBOUNCE_MS && reading != stableState) {
    stableState = reading;               // stable for 20 ms -> accept it
    if (stableState == LOW) Serial.println("pressed");   // act once per press
  }
}
```

### מעקב עם מספרים
| זמן [ms] | קריאה | מה קורה |
|---|---|---|
| 1000 | LOW | שינוי ⇐ `lastChange=1000` |
| 1003 | HIGH | קפיצה ⇐ `lastChange=1003` |
| 1005 | LOW | קפיצה ⇐ `lastChange=1005` |
| 1025 | LOW | $1025-1005=20\ge20$ ⇐ מתקבל "לחוץ", מודפס פעם אחת ✅ |

**למה `millis() - lastChange`** ולא השוואה ישירה: חיסור של `unsigned long` עובד נכון גם כש-`millis()` מתאפס אחרי ~49 ימים.

💡 **הרעיון:** "יציב X מילישניות" = לאפס טיימר בכל שינוי, ולקבל את המצב כשהטיימר עבר X. בלי `delay` – הלולאה ממשיכה לעבוד.
"""})

S.append({"id": "7e1126a3-dbe3-4a88-bb3f-1ebc50ad4e79", "uncertain": False, "solution_md": r"""
### מה עושה `INPUT_PULLUP`
הוא מחבר **נגד פנימי** (עשרות קילו-אוהם) בין הפין לבין 3.3V. הכפתור מחובר בין הפין ל-GND.

### שני המצבים
| כפתור | מה מחובר לפין | קריאה |
|---|---|---|
| **משוחרר** | רק הנגד ל-3.3V (אין זרם, אין מפל) | **HIGH** |
| **לחוץ** | חיבור ישיר ל-GND (התנגדות ~0); דרך הנגד זורם זרם קטן $\frac{3.3\text{V}}{R}$ | **LOW** |

כלומר הלוגיקה **הפוכה**: לחוץ = LOW.

### התשובה: **א** ✅

**למה האחרות לא:**
- **ב** – `INPUT_PULLUP` לא "הופך" ערכים בתוכנה; ההיפוך נובע מהחיווט (לחיצה = אדמה).
- **ג** – הנגד הפנימי חלש בכוונה (התנגדות גבוהה); החיבור הישיר לאדמה "מנצח" ומוריד את הפין ל-0.
- **ד** – בדיוק בשביל זה יש pull-up: הוא מונע פין "צף" (לא מוגדר) כשהכפתור משוחרר.

💡 **הרעיון:** כפתור לאדמה + `INPUT_PULLUP` ⇐ משוחרר HIGH, לחוץ LOW. בקוד: `if (digitalRead(4) == LOW)` = לחוץ. (במבחן הזה הופיע גם בשאלה 7: פסיקה `FALLING` = רגע הלחיצה.)
"""})

S.append({"id": "2d31f517-8377-465d-aa52-b41b0af0607f", "uncertain": True, "solution_md": r"""
### 1. למה W1TS / W1TC בטוחים יותר מ-read-modify-write
ב-RMW עושים שלוש פעולות: **קוראים** את כל הרגיסטר, **משנים** ביט, **כותבים** את כל הרגיסטר בחזרה. אם בין הקריאה לכתיבה פסיקה (או הליבה השנייה של ה-ESP32) משנה ביט **אחר** באותו רגיסטר – הכתיבה שלנו דורסת את השינוי שלה. ❌

ב-W1TS ("כתוב 1 כדי להדליק") ו-W1TC ("כתוב 1 כדי לכבות"): כותבים **רק** מסכה, בפעולה **אחת**. ביט שכתבנו בו 1 משתנה; ביט שכתבנו בו 0 – **לא נוגעים בו**. אין קריאה ⇐ אין חלון זמן להתנגשות. ✅

### 2. הקוד – הבהוב GPIO18 ברמת הרגיסטרים
```c
#include <stdint.h>
#define REG(addr) (*(volatile uint32_t *)(addr))     // a memory-mapped register

#define GPIO_OUT_W1TS_REG        REG(0x3FF44008)    // write 1 -> pin HIGH
#define GPIO_OUT_W1TC_REG        REG(0x3FF4400C)    // write 1 -> pin LOW
#define GPIO_ENABLE_W1TS_REG     REG(0x3FF44024)    // write 1 -> output driver on
#define GPIO_FUNC18_OUT_SEL_CFG  REG(0x3FF44578)    // what drives pin 18 (GPIO matrix)
#define IO_MUX_GPIO18_REG        REG(0x3FF49070)    // pad function of pin 18

#define PIN18 (1u << 18)

void led_init(void) {
    IO_MUX_GPIO18_REG = (IO_MUX_GPIO18_REG & ~(0x7u << 12)) | (2u << 12); // MCU_SEL = 2: the pad is a GPIO
    GPIO_FUNC18_OUT_SEL_CFG = 256;      // 256 = "simple GPIO output" (not a peripheral signal)
    GPIO_ENABLE_W1TS_REG = PIN18;       // enable the output driver of pin 18 only
}

void loop_blink(void) {
    GPIO_OUT_W1TS_REG = PIN18;          // LED on  (only bit 18 changes)
    delay(500);
    GPIO_OUT_W1TC_REG = PIN18;          // LED off (only bit 18 changes)
    delay(500);
}
```
**אימות:** הנורית ב-GPIO18 מהבהבת פעם בשנייה (חצי שנייה דולקת, חצי כבויה).

### 3. המסלול של אות הפלט – כל רגיסטר ותפקידו
**ערך הפלט** (W1TS/W1TC) ← **מטריצת GPIO** (FUNC18_OUT_SEL = 256: "הערך בא מהביט שלי ב-GPIO_OUT") ← **IO_MUX** (MCU_SEL: הפד עובד כ-GPIO) ← **דרייבר פלט** (ENABLE: הפין מוציא מתח) ← הרגל.
בלי כל אחד מהם – אין הבהוב: בלי ENABLE הפין נשאר קלט; בלי OUT_SEL=256 פריפריה אחרת שולטת בו.

> ⚠️ כתובות הרגיסטרים לקוחות מהשאלה (ESP32 הקלאסי). השדה MCU_SEL (ביטים 12–14, ערך 2) והערך 256 – לפי מדריך ה-ESP32; ב-ESP32-S3 הכתובות שונות.

💡 **הרעיון:** `volatile uint32_t*` לכתובת ← הגדרת הפד (IO_MUX + matrix + enable) ← W1TS/W1TC לשינוי ביט בודד בלי RMW.
"""})

CORE = {"weeks": {
 "1": [
  {"id": "e161f6d5-5cd1-4f71-ba7a-7f2b2ae14a45", "why": "שאלה 1 ממועד ב' תשפ\"ו - מעקב אחרי XOR עם מסכה (בשני המבחנים יש שאלת ביטים)"},
  {"id": "1590cbbc-bc83-423d-af75-0f4e88feb3bd", "why": "שאלה 1 ממועד א' - ניקוי ביט והדלקת ביט באותה שורה"},
  {"id": "57b69b82-02d2-4b92-af55-6d02cb24642a", "why": "שאלה 2 ממועד א' - toggle עם XOR"},
  {"id": "cf42a626-1f56-4185-9799-eb4dc6520498", "why": "volatile - נשאל במבחן (7ד במועד ב') יחד עם פסיקות"}
 ],
 "2": [
  {"id": "7e1126a3-dbe3-4a88-bb3f-1ebc50ad4e79", "why": "שאלה 2 ממועד ב' - INPUT_PULLUP: לחוץ = LOW"},
  {"id": "c0f71e7d-c257-415c-8768-7374beb4a179", "why": "עדכון שדה ביטים (ניקוי + OR) - בדיוק מה שעושים ברגיסטרים"},
  {"id": "2d31f517-8377-465d-aa52-b41b0af0607f", "why": "GPIO ברמת הרגיסטרים, W1TS/W1TC"}
 ],
 "3": [
  {"id": "7a12cfef-ede4-45d4-9428-f73eaf480e84", "why": "שאלה 4 ממועד א' - רזולוציית ADC"},
  {"id": "70f90662-89d8-45b2-84c8-23a64766a5b8", "why": "שאלה 5 ממועד ב' - בחירת הנחתה ב-ADC"},
  {"id": "19ec7fa7-7a62-4c11-a460-fa719aa13331", "why": "Debounce עם millis - בסיס לשאלות הכפתור והפסיקה"}
 ]},
 "exam_note": "המבחן (תשפ\"ו): 90 דקות, אסור דף נוסחאות, מחשבון לא גרפי. 6 שאלות אמריקאיות (10 נק') על ביטים, GPIO, PWM, WDT, ADC, UART + 2 שאלות הבנת קוד (20 נק') - פסיקות ו-I2C."}

import sys
if len(sys.argv) > 1 and sys.argv[1] == "core":
    print(json.dumps(CORE, ensure_ascii=False, indent=1))
else:
    print(json.dumps(S, ensure_ascii=False, indent=1))
