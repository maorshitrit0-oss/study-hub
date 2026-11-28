"""Micro: exercises whose stored solution was hollow (28/11/2026), solved in full by Claude. Pure-C parts compiled and
run with gcc in the session (powers sum, sine series, bit operations); Arduino/ESP32 calls follow the course labs.
Writes chapters/fix_2811_micro_hollow.json for publish.yml inspect=exercises (course ^מיקרו)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש במלואו; קוד C טהור הודר והורץ."

S = {}

S["19c0e98b"] = r"""### 📘 מה צריך לדעת קודם
- `timerBegin(f)` (ספריית ESP32 3.x) קובע את **תדר הספירה** של הטיימר ב-Hz: הטיימר מוסיף 1 בכל $\frac1f$ שניות.
- `timerAlarm(timer, N, true, 0)`: פסיקה כשהמונה מגיע ל-N, `true` = חוזר על עצמו (auto-reload).
- גל ריבועי שמתהפך בכל פסיקה: מחזור שלם = שתי פסיקות.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** `timerBegin(1000000)` ⇐ תדר ספירה $1\text{ MHz}$:
$$T_{tick}=\frac{1}{f}=\frac{1}{10^6\text{ Hz}}=1\ \mu\text{s}$$
✅ המונה עולה ב-1 כל מיקרו-שנייה (רזולוציה של $1\ \mu\text{s}$).

**ב.**
$$T_{int}=N\cdot T_{tick}=250{,}000\cdot1\ \mu\text{s}=0.25\text{ s}$$
✅ פסיקה כל $0.25\text{ s}$, כלומר $4$ פסיקות בשנייה.

**ג.** כל פסיקה הופכת את `outputLevel`: פסיקה אחת ל-1, הבאה ל-0. מחזור שלם (1 ואז 0) = 2 פסיקות:
$$T_{wave}=2\cdot0.25=0.5\text{ s}\qquad f_{wave}=\frac{1}{0.5}=2\text{ Hz}$$
✅ $2\text{ Hz}$ – חצי מקצב הפסיקות, כי כל פסיקה היא רק **חצי** מחזור.

**ד.** רוצים $1\text{ kHz}$: מחזור $1\text{ ms}$, חצי מחזור $500\ \mu\text{s}$ ⇐ פסיקה כל $500\ \mu\text{s}$:
$$N=\frac{500\ \mu\text{s}}{1\ \mu\text{s}}=500$$
✅ משנים רק את השורה: `timerAlarm(timer, 500, true, 0);` (הרזולוציה `timerBegin(1000000)` נשארת). כדי לראות את הגל על פין – לכתוב את `outputLevel` לפין (למשל `digitalWrite` ב-`loop`).

💡 **הרעיון:** זמן = מספר ספירות × זמן ספירה; גל ריבועי = שתי פסיקות למחזור."""

S["8726c97a"] = r"""### 📘 מה צריך לדעת קודם
- `#include "Dog.h"` פשוט **מעתיק** את תוכן הקובץ לתוך `Dog.c` לפני הקומפילציה.
- כל קובץ `.c` מקומפל **בנפרד**: הקומפיילר רואה רק את מה שבקובץ ובקבצים שנכללו בו.
- ב-`Dog.h` של התרגיל יש הגדרות שהמימוש משתמש בהן: המסכות (`AGE_MASK`, `AGE_SHIFT` ...) ואב-טיפוס של הפונקציות.

### ✍️ הדרך המלאה (כמו במחברת)
1. קומפילציה של `Dog.c`: הקומפיילר מגיע לשורה כמו `*dog &= ~AGE_MASK;` – ו-`AGE_MASK` לא הוגדר בקובץ הזה (ההגדרה ב-`Dog.h`, שלא נכלל).
2. ✅ **שגיאת קומפילציה**: "`AGE_MASK` undeclared" (מזהה לא מוכר) – בכל שימוש במסכה/קבוע/טיפוס מ-`Dog.h`.
3. אם במקרה `Dog.c` לא משתמש באף הגדרה מ-`Dog.h` (רק `unsigned char` וקבועים מספריים) – הקובץ **כן** יתקמפל. אבל אז אין בדיקה שהחתימות ב-`Dog.c` תואמות להצהרות ב-`Dog.h` שבהן `main.c` משתמש: חתימה שונה תעבור קומפילציה ותיתן התנהגות שגויה בזמן ריצה. לכן תמיד כוללים את קובץ הכותרת גם בקובץ המימוש.

💡 **הרעיון:** כל קובץ `.c` מקומפל לבד – מה שלא נכלל בו, הקומפיילר לא מכיר."""

S["0c2c2376"] = r"""התשובה: **ב**

### 📘 מה צריך לדעת קודם
- גיל בביטים 2–6 (5 ביטים). `>> 2` מזיז את השדה לביט 0; `& 0x1F` (= `00011111`) משאיר רק 5 ביטים.

### ✍️ הדרך המלאה (כמו במחברת)
1. `0xB6` בבינארית: `B` = `1011`, `6` = `0110` ⇐ `1011 0110`.
2. `dog >> 2`: `0010 1101`.
3. `& 0x1F`: `0010 1101 & 0001 1111 = 0000 1101`.
4. `01101` בעשרוני: $8+4+1=13$.

✅ הגיל הוא 13.

### ❌ למה לא האחרות
- **א (45):** `0010 1101` = 45 – שכחו את ה-`& 0x1F`, ונשאר גם ביט 7 (המין) בתוך הערך.
- **ג (22):** הזזה ב-3 במקום ב-2 (`0001 0110` = 22).
- **ד (54):** `0x36` – רק ביטים 0–5 בלי הזזה (`0xB6 & 0x3F` = 54).

💡 **הרעיון:** לקריאת שדה: מזיזים ימינה למקום 0, ואז מסכה ברוחב השדה."""

S["f5c2db76"] = r"""### 📘 מה צריך לדעת קודם
- `INPUT_PULLUP`: הפין מחובר דרך נגד פנימי ל-3.3V ⇐ כפתור משוחרר = `HIGH` (1), כפתור לחוץ (מחובר ל-GND) = `LOW` (0).
- `FALLING`: פסיקה רק במעבר מ-1 ל-0.
- שגרת פסיקה צריכה להיות קצרה; עבודה "כבדה" עושים ב-`loop`.
- `volatile`: המהדר חייב לקרוא את המשתנה מהזיכרון בכל פעם, כי הוא יכול להשתנות מחוץ לזרימה הרגילה (בפסיקה).

### ✍️ הדרך המלאה (כמו במחברת)
**סעיף א – ✅ א.** לחיצה מחברת את GPIO4 לאדמה: הפין יורד מ-1 ל-0, וזה בדיוק `FALLING`.
- ב: מעבר 0←1 הוא `RISING` (שחרור).
- ג: פסיקה מופעלת על **מעבר**, לא על רמה – פעם אחת ללחיצה.
- ד: "כל שינוי" הוא `CHANGE`, לא `FALLING`.

**סעיף ב – ✅ ד.** `onButton` רק מציבה `buttonEvent = true`. ה-`loop` רואה את הדגל, מאפס אותו, הופך את `ledState` וכותב לפין 5.
- א: הכתיבה לפין נעשית ב-`loop`, לא בפסיקה.
- ב: `IRAM_ATTR` רק שם את הפונקציה בזיכרון RAM מהיר; אין קשר לאתחול.
- ג: אין המתנה בשגרת פסיקה.

**סעיף ג – ✅ ב.** מצב התחלתי כבוי (`LOW`). כל לחיצה הופכת: 1 ← דולק, 2 ← כבוי, 3 ← דולק.
- א: מספר **אי-זוגי** של היפוכים מסתיים במצב ההפוך מההתחלה.
- ג: אחרי כל אירוע הדגל מתאפס – אין הבהוב.
- ד: `bool` נכתב ל-`digitalWrite` כ-0/1, זה תקין.

**סעיף ד – ✅ א.** הפסיקה משנה את `buttonEvent` "מאחורי הגב" של `loop`. בלי `volatile` המהדר עלול לשמור את הערך ברגיסטר ולא לראות את השינוי.
- ב: `volatile` לא שומר ערך אחרי כיבוי (זה RTC/Flash).
- ג: כל `bool` יכול להכיל אמת/שקר.
- ד: `volatile` **לא** נותן הגנה מהתנגשויות (לזה צריך קטע קריטי / אטומיות).

💡 **הרעיון:** פסיקה קצרה שמרימה דגל + `loop` שמטפל בו – והדגל `volatile`."""

S["c7f5ff26"] = r"""### 📘 מה צריך לדעת קודם
- EXT1 מאפשר התעוררות מ**כמה** פינים: מסכת ביטים של 64 ביט, ביט לכל GPIO (`1ULL << n`).
- מצב `ESP_EXT1_WAKEUP_ANY_HIGH`: מתעורר כשאחד הפינים במסכה ב-1. (חיבור הכפתורים: בין הפין ל-3.3V, עם נגד pull-down.)
- אחרי התעוררות מ-deep sleep התוכנית מתחילה מ-`setup` מחדש. `esp_sleep_get_ext1_wakeup_status()` מחזירה מסכה של הפינים שגרמו להתעוררות.

### ✍️ הדרך המלאה (כמו במחברת)
1. בונים מסכה לשני הפינים: $2^{32}+2^{33}$, כלומר `(1ULL << 32) | (1ULL << 33)`. חייבים `ULL` – `1 << 32` ב-`int` של 32 ביט לא מוגדר.
2. ב-`setup`: בודקים אם ההתעוררות היא מ-EXT1, ואם כן – איזה ביט דולק במסכה.
3. מפעילים EXT1 ונכנסים לשינה.

```c
#include "esp_sleep.h"

#define WAKE_MASK ((1ULL << GPIO_NUM_32) | (1ULL << GPIO_NUM_33))  // bits 32 and 33

void setup() {
  Serial.begin(115200);
  delay(500);                                            // time to open the serial monitor

  if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT1) {
    uint64_t pins = esp_sleep_get_ext1_wakeup_status();  // which pins woke us
    if (pins & (1ULL << GPIO_NUM_32)) Serial.println("Woken by GPIO32");
    if (pins & (1ULL << GPIO_NUM_33)) Serial.println("Woken by GPIO33");
  } else {
    Serial.println("First boot");
  }

  esp_sleep_enable_ext1_wakeup(WAKE_MASK, ESP_EXT1_WAKEUP_ANY_HIGH);  // any of them HIGH -> wake
  Serial.println("Going to sleep");
  esp_deep_sleep_start();                                // never returns
}

void loop() {}                                           // not reached
```
✅ לחיצה על כפתור 32 מדפיסה "Woken by GPIO32", על 33 – "Woken by GPIO33".

💡 **הרעיון:** EXT1 = מסכה של פינים; אחרי ההתעוררות שואלים את המסכה מי העיר."""

S["67fe2f8e"] = r"""### 📘 מה צריך לדעת קודם
- ב-ESP32 כל ביט ברגיסטר של 32 ביט שייך ל-GPIO אחד (ביט $n$ ⇐ GPIO $n$, עבור 0–31).

### ✍️ הדרך המלאה (כמו במחברת)
| רגיסטר | תפקיד |
|---|---|
| `GPIO_OUT_REG` | ערך הפלט של כל 32 הפינים: ביט 1 ⇐ הפין ב-HIGH, ביט 0 ⇐ LOW. כתיבה אליו משנה את **כל** הפינים. |
| `GPIO_OUT_W1TS_REG` | "Write 1 To Set": כתיבת 1 לביט $n$ מדליקה **רק** את פין $n$; ביטים עם 0 לא משתנים. |
| `GPIO_ENABLE_REG` | הפעלת דרייבר הפלט: ביט 1 ⇐ הפין פלט; ביט 0 ⇐ הפין לא מוציא מתח (קלט). |

✅ דוגמה: להדליק GPIO18 בלי לגעת באחרים – לכתוב `1 << 18` ל-`GPIO_OUT_W1TS_REG` (ואחרי שהדלקנו את ביט 18 ב-`GPIO_ENABLE_REG`).

💡 **הרעיון:** OUT = הערך, W1TS = שינוי ביט בודד בלי קריאה-שינוי-כתיבה, ENABLE = האם הפין בכלל פלט."""

S["b3793e56"] = r"""### 📘 מה צריך לדעת קודם
- כל איבר בטור מתקבל מהקודם: $t_i=t_{i-1}\cdot\frac{-x^2}{(2i)(2i+1)}$ – בלי לחשב עצרת וחזקה מאפס (עצרת גדלה מהר ועולה על גבולות `int`).

### ✍️ הדרך המלאה (כמו במחברת)
1. $t_0=x$, הסכום מתחיל ב-$x$.
2. בכל צעד $i=1..n$: $t_i=t_{i-1}\cdot\frac{-x^2}{(2i)(2i+1)}$ ומוסיפים לסכום.
   בדיקה: $t_1=x\cdot\frac{-x^2}{2\cdot3}=-\frac{x^3}{3!}$ ✓, $t_2=-\frac{x^3}{3!}\cdot\frac{-x^2}{4\cdot5}=\frac{x^5}{5!}$ ✓.

```c
#include <stdio.h>

double my_sin(double x, int n) {          // series up to (-1)^n x^(2n+1)/(2n+1)!
    double term = x, sum = x;
    for (int i = 1; i <= n; i++) {
        term *= -x * x / ((2 * i) * (2 * i + 1));  // next term from the previous one
        sum += term;
    }
    return sum;
}

int main(void) {
    printf("%f\n", my_sin(1.0, 5));       // 0.841471
    return 0;
}
```
✅ הורץ: `my_sin(1, 5)` = $0.841471$ ו-`my_sin(3, 10)` = $0.141120$ – זהים ל-`sin` של הספרייה.

💡 **הרעיון:** מחשבים כל איבר מהקודם – פחות חישובים ובלי גלישה."""

S["031966d6"] = r"""### 📘 מה צריך לדעת קודם
- $5^{17}\approx7.6\cdot10^{11}$ – גדול מ-`int` (עד $\approx2.1\cdot10^9$). לכן `long long` (עד $\approx9.2\cdot10^{18}$).

### ✍️ הדרך המלאה (כמו במחברת)
1. פונקציה שמכפילה את הבסיס בעצמו `exp` פעמים.
2. קוראים לה שלוש פעמים ומחברים.

```c
#include <stdio.h>

long long power(long long base, int exp) {   // base^exp by repeated multiplication
    long long result = 1;
    for (int i = 0; i < exp; i++)
        result *= base;
    return result;
}

int main(void) {
    long long sum = power(2, 20) + power(3, 15) + power(5, 17);
    printf("%lld\n", sum);
    return 0;
}
```
**הצבה:** $2^{20}=1{,}048{,}576$, $3^{15}=14{,}348{,}907$, $5^{17}=762{,}939{,}453{,}125$.
✅ $2^{20}+3^{15}+5^{17}=762{,}954{,}850{,}608$ (הורץ).

💡 **הרעיון:** פונקציה אחת לשימוש חוזר + לבחור טיפוס שמספיק לתוצאה."""

S["5cd64a13"] = r"""### 📘 מה צריך לדעת קודם
- EXT0: התעוררות מפין **אחד**, ברמה שבוחרים (0 או 1).
- כפתור בין GPIO33 ל-GND עם pull-up: משוחרר = 1, לחוץ = 0 ⇐ מתעוררים ברמה 0. בשינה עמוקה ה-pull-up הרגיל כבוי, ולכן מפעילים את ה-pull-up של תחום ה-RTC.
- אחרי ההתעוררות הקוד מתחיל שוב ב-`setup`.

### ✍️ הדרך המלאה (כמו במחברת)
```c
#include "esp_sleep.h"
#include "driver/rtc_io.h"

#define BUTTON GPIO_NUM_33

void setup() {
  Serial.begin(115200);
  delay(500);

  if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT0)
    Serial.println("Button woke me up");

  rtc_gpio_pullup_en(BUTTON);              // keep the pin HIGH while sleeping
  rtc_gpio_pulldown_dis(BUTTON);
  esp_sleep_enable_ext0_wakeup(BUTTON, 0); // wake when the pin goes LOW (pressed)
  Serial.println("Sleeping...");
  esp_deep_sleep_start();
}

void loop() {}
```
✅ לחיצה ⇐ הפין ב-0 ⇐ ההתקן מתעורר ומדפיס "Button woke me up", ואז חוזר לישון.

💡 **הרעיון:** EXT0 = פין אחד + רמה; את סיבת ההתעוררות בודקים ב-`setup`."""

S["1590cbbc"] = r"""### 📘 מה צריך לדעת קודם
- `1U << k` = מספר עם 1 רק בביט $k$. `& ~(1U << k)` מכבה ביט $k$; `| (1U << k)` מדליק ביט $k$.
- ביטים נספרים מימין, החל מ-0.

### ✍️ הדרך המלאה (כמו במחברת)
1. `x = 0b0110 1101` – ביט 2 (השלישי מימין) הוא 1.
2. `1U << 2 = 0000 0100`, `~` ⇐ `1111 1011`.
3. `x & 1111 1011 = 0110 1001` (ביט 2 כבה).
4. `1U << 7 = 1000 0000`; `0110 1001 | 1000 0000 = 1110 1001`.

✅ `x = 0b11101001` = `0xE9` (הורץ).

💡 **הרעיון:** לכבות – AND עם מסכה הפוכה; להדליק – OR עם המסכה."""

S["b4931529"] = r"""> ⚠️ ארבעת קטעי הקוד (א-ד) של השאלה לא נשמרו בנוסח. כאן הקוד הנכון וההסבר – התשובה הנכונה היא הקטע שזהה לו.

### 📘 מה צריך לדעת קודם
- `Wire.beginTransmission(addr)` – פותח תנאי start ושולח כתובת במצב **כתיבה**.
- `Wire.write(v)` – בית לשליחה (כאן: מספר הרגיסטר).
- `Wire.endTransmission(false)` – שולח, **בלי stop** ⇐ אפשר repeated start. `endTransmission(true)` – שולח עם stop.
- `Wire.requestFrom(addr, n, true)` – repeated start + כתובת במצב **קריאה**, קורא $n$ בתים ובסוף stop.
- `Wire.read()` – בית אחד ממה שהתקבל, לפי הסדר.

### ✍️ הדרך המלאה (כמו במחברת)
```c
Wire.beginTransmission(0x39);   // start + address in write mode       (steps a, b)
Wire.write(0x0C);               // register to read                     (step c)
Wire.endTransmission(false);    // no stop -> repeated start comes next  (step d)
Wire.requestFrom(0x39, 2, true);// address in read mode, 2 bytes, stop   (steps e, f)
uint8_t msb = Wire.read();      // first byte = MSB
uint8_t lsb = Wire.read();      // second byte = LSB
uint16_t value = ((uint16_t)msb << 8) | lsb;   // MSB in the high 8 bits
```
✅ מה לבדוק בכל קטע:
1. `endTransmission(false)` ולא `true` – אחרת נשלח stop לפני הקריאה (סותר את שלב ד).
2. בקשה של **2** בתים (לא 16 – הגודל ב**ביטים**).
3. האיחוד: `msb << 8 | lsb` – לא הפוך, ולא חיבור בלי הזזה.

💡 **הרעיון:** כתיבת מספר הרגיסטר, repeated start, קריאה – והרכבת 16 ביט מ-MSB ו-LSB."""

S["553159a3"] = r"""### 📘 מה צריך לדעת קודם
- `AGE_MASK = 0x1F << 2 = 0111 1100 = 0x7C` (ביטים 2–6).
- עדכון שדה = **לנקות** (`&= ~AGE_MASK`) ואז **להכניס** (`|= new_age << 2`).

### ✍️ הדרך המלאה (כמו במחברת)
**עם איפוס:**
1. `~0x7C = 1000 0011 = 0x83`.
2. `0xFF & 0x83 = 0x83` – שדה הגיל נוקה, ביטים 0, 1, 7 נשמרו.
3. `5 << 2 = 0001 0100 = 0x14`.
4. `0x83 | 0x14 = 1001 0111 = 0x97`.

✅ `dog = 0x97` – והגיל: `(0x97 & 0x7C) >> 2 = 0x14 >> 2 = 5` ✓.

**בלי איפוס:**
`0xFF | 0x14 = 0xFF` – כל הביטים כבר היו 1, ה-OR לא משנה כלום.
✅ `dog = 0xFF` – הגיל נשאר 31 במקום 5. ❌ לכן חובה לנקות את השדה לפני ה-OR.

💡 **הרעיון:** OR רק מדליק ביטים – לא יכול לכבות ביטים ישנים של השדה."""

S["1217c0fd"] = r"""### 📘 מה צריך לדעת קודם
- מבנה הבית: ביט 0 רעב, ביט 1 שמח, ביטים 2–6 גיל (0–31), ביט 7 מין.
- מסכה לכל שדה, ו-shift למיקום השדה.
- הדלקה: `|= MASK`; כיבוי: `&= ~MASK`; קריאה: `(b & MASK) >> SHIFT`.

### ✍️ הדרך המלאה (כמו במחברת)
```c
#include <stdio.h>

#define HUNGRY_MASK 0x01                  // bit 0
#define HAPPY_MASK  0x02                  // bit 1
#define AGE_SHIFT   2
#define AGE_MASK    (0x1F << AGE_SHIFT)   // bits 2..6 = 0x7C
#define SEX_MASK    0x80                  // bit 7 (1 = female)

int dog_set_is_hungry(unsigned char *b, int on) {
    if (b == NULL) return -1;
    if (on) *b |= HUNGRY_MASK; else *b &= ~HUNGRY_MASK;
    return 0;
}
int dog_set_is_happy(unsigned char *b, int on) {
    if (b == NULL) return -1;
    if (on) *b |= HAPPY_MASK; else *b &= ~HAPPY_MASK;
    return 0;
}
int dog_set_age(unsigned char *b, int age) {
    if (b == NULL || age < 0 || age > 31) return -1;   // 5 bits only
    *b &= ~AGE_MASK;                                   // clear the field
    *b |= (unsigned char)(age << AGE_SHIFT);           // put the new value
    return 0;
}
int dog_set_sex(unsigned char *b, int female) {
    if (b == NULL) return -1;
    if (female) *b |= SEX_MASK; else *b &= ~SEX_MASK;
    return 0;
}
int dog_get_is_hungry(unsigned char b) { return (b & HUNGRY_MASK) != 0; }
int dog_get_is_happy(unsigned char b)  { return (b & HAPPY_MASK) != 0; }
int dog_get_age(unsigned char b)       { return (b & AGE_MASK) >> AGE_SHIFT; }
int dog_get_sex(unsigned char b)       { return (b & SEX_MASK) != 0; }

int main(void) {
    unsigned char bitbite = 0;
    dog_set_age(&bitbite, 13);
    dog_set_is_happy(&bitbite, 1);
    dog_set_sex(&bitbite, 1);
    printf("0x%02X age=%d\n", bitbite, dog_get_age(bitbite));   // 0xB6 age=13
    return 0;
}
```
✅ הורץ: גיל 13, שמח, נקבה ⇐ `0xB6` (`1011 0110`), והגיל נקרא בחזרה כ-13.

💡 **הרעיון:** שדה = מסכה + shift; setter = לנקות ואז להכניס; getter = AND ואז shift ימינה."""

S["b801435b"] = r"""### 📘 מה צריך לדעת קודם
- `GPIO_IN_REG` (`0x3FF4403C`) מחזיק את מצב **כל** הפינים 0–31: ביט $n$ = הרמה של GPIO $n$.
- קריאת רגיסטר: `*(volatile uint32_t *)addr`; בודקים ביט בודד עם `& (1u << n)`.

### ✍️ הדרך המלאה (כמו במחברת)
**1.** לולאת polling: קוראים את הכפתור (נניח GPIO4) ומשקפים ל-GPIO18:
```c
#define REG(a) (*(volatile uint32_t *)(a))
#define GPIO_IN_REG       REG(0x3FF4403C)
#define GPIO_OUT_W1TS_REG REG(0x3FF44008)
#define GPIO_OUT_W1TC_REG REG(0x3FF4400C)
#define BTN (1u << 4)
#define LED (1u << 18)

void loop() {
  if (GPIO_IN_REG & BTN) GPIO_OUT_W1TS_REG = LED;   // button reads 1 -> LED on
  else                   GPIO_OUT_W1TC_REG = LED;   // button reads 0 -> LED off
}
```
✅ הלולאה רצה מיליוני פעמים בשנייה, לכן הנורית מגיבה "מיד" ללחיצה ולשחרור (מיקרו-שניות).

**2.** ✅ אין רגיסטר נפרד לכל פין – החומרה מחזירה מילה אחת של 32 ביט. הקריאה תמיד מחזירה את כולה, ולכן "חותכים" את הביט שלנו עם מסכה. בלי המסכה, כל פין אחר שב-1 היה נראה כמו לחיצה.

**3.** ✅ active-LOW (כפתור לאדמה עם pull-up): לחוץ = 0. התנאי מתהפך – `if ((GPIO_IN_REG & BTN) == 0)` ⇐ להדליק. וצריך להפעיל pull-up לפין, כדי שבמצב משוחרר הוא יהיה 1 ולא "צף".

💡 **הרעיון:** קוראים מילה שלמה, מסכה לביט אחד; active-LOW הופך את התנאי."""

S["94bf45f8"] = r"""### 📘 מה צריך לדעת קודם
- ב-ESP32 כל ביט ברגיסטרים של 32 ביט שייך ל-GPIO אחד (0–31).

### ✍️ הדרך המלאה (כמו במחברת)
**1. הכתובות (ESP32):**

| רגיסטר | כתובת | תפקיד |
|---|---|---|
| `GPIO_OUT_REG` | `0x3FF44004` | ערך הפלט של כל הפינים |
| `GPIO_OUT_W1TS_REG` | `0x3FF44008` | כתיבת 1 ⇐ הפין ל-HIGH |
| `GPIO_OUT_W1TC_REG` | `0x3FF4400C` | כתיבת 1 ⇐ הפין ל-LOW |
| `GPIO_ENABLE_REG` | `0x3FF44020` | ביט 1 ⇐ הפין פלט |
| `GPIO_ENABLE_W1TS_REG` | `0x3FF44024` | כתיבת 1 ⇐ הפעלת פלט |
| `GPIO_ENABLE_W1TC_REG` | `0x3FF44028` | כתיבת 1 ⇐ ביטול פלט |
| `GPIO_IN_REG` | `0x3FF4403C` | מצב הקלט של כל הפינים |

**2.** ✅ IO_MUX קובע לכל רגל ("pad") איזו פונקציה מחוברת אליה – ממשק ייעודי או GPIO. בשדה `MCU_SEL` הערך 2 (Function 2, כשהספירה מ-0) מחבר את הרגל ל-GPIO דרך מטריצת ה-GPIO. ב-GPIO18 וב-GPIO4 זו הבחירה שמאפשרת לשלוט בהם עם רגיסטרי ה-GPIO.

**3.** ✅ ל-GPIO34–39 אין בכלל דרייבר פלט (וגם אין להם pull-up/pull-down פנימיים) – אפשר רק לקרוא אותם. כתיבה אליהם לא תוציא מתח, ולכן הם לא מתאימים לנורית.

**4.** ✅ `0x100` (= 256) ב-`GPIO_FUNCx_OUT_SEL`: "אין פריפריה – הפין מקבל את הערך מהביט שלו ב-`GPIO_OUT_REG`". כלומר זה מה שהופך את הפין לפלט GPIO פשוט שהתוכנה שולטת בו.

**5.** ✅ מגע מכני "קופץ" כמה פעמים במשך כמה מילי-שניות. הלולאה דוגמת מהר מאוד, ולכן רואה כמה מעברים ללחיצה אחת. הקוד נכון לוגית, אבל הקלט עצמו רועש – צריך לחכות שהקלט יתייצב (debounce).

💡 **הרעיון:** IO_MUX ← מטריצה (`0x100`) ← ENABLE ← OUT: ארבעה צעדים עד שפין מוציא מתח."""

S["86f93c05"] = r"""### 📘 מה צריך לדעת קודם
- מגע מכני רוטט כמה מילי-שניות כשהוא נסגר ונפתח.

### ✍️ הדרך המלאה (כמו במחברת)
**1.** ✅ כשהמגעים נפגשים הם קופצים זה מזה כמה פעמים לפני שהם נסגרים סופית. כל קפיצה היא מעבר 1←0 או 0←1, והבקר מהיר מספיק לראות כל אחד מהם.

**2.** ✅ **קפצונים**: כמה מעברים **בשבריר השנייה** של הלחיצה או השחרור – רעש מכני. **הפעלה חוזרת בזמן לחיצה**: הקוד בודק **רמה** ("לחוץ?") בכל סיבוב של הלולאה, ולכן מבצע את הפעולה שוב ושוב כל עוד הכפתור לחוץ – בעיה של הקוד, לא של המגע. פתרון: לזהות **מעבר** (קודם 1, עכשיו 0).

**3.** ✅ אין צורך בנגד חיצוני: הנגד הפנימי מחזיק את הפין ב-1 כשהכפתור משוחרר, והכפתור מחובר פשוט לאדמה. בלי pull-up הפין "צף" וקורא רעש.

**4.** ✅ `delay()` עוצר את **כל** התוכנית – בזמן הזה אין טיפול בחיישנים, בתקשורת או בכפתורים אחרים. עם `millis()` שומרים את זמן המעבר האחרון ובודקים אם עבר מספיק זמן, בלי לעצור את הלולאה.

**5.** ✅ מתחילים ב-$20$–$50\text{ ms}$ (למשל $50\text{ ms}$). אם עדיין רואים לחיצות כפולות – מגדילים; אם הכפתור מרגיש "איטי" – מקטינים.

💡 **הרעיון:** קפצונים = רעש של המגע; פתרון – לחכות שהקלט יתייצב, בלי לעצור את התוכנית."""

S["89052244"] = r"""### 📘 מה צריך לדעת קודם
- ב-UART אין קו שעון: כל צד סופר זמן לפי ה-baud rate שלו. זמן ביט $=\frac{1}{\text{baud}}$.
- 8N1: ביט התחלה, 8 ביטי מידע, בלי parity, ביט עצירה.

### ✍️ הדרך המלאה (כמו במחברת)
$$T_{bit,tx}=\frac{1}{9600}\approx104.2\ \mu\text{s}\qquad T_{bit,rx}=\frac{1}{115200}\approx8.68\ \mu\text{s}$$
היחס 12: בזמן שהמשדר שולח ביט אחד, המקלט דוגם כ-12 "ביטים". כל ביט של המשדר נראה למקלט כרצף של 12 ביטים זהים, ולכן המקלט מרכיב בתים שגויים או מזהה שגיאות מסגרת (ביט עצירה לא במקום).

✅ **א.**
- ב: ה-baud rate קובע את **תזמון הביטים על הקו**, לא את מהירות התצוגה.
- ג: UART רגיל לא מתאים את הקצב לבד.
- ד: ב-8N1 **אין** ביט parity, ולכן גם אין שגיאת parity.

💡 **הרעיון:** בלי שעון משותף – שני הצדדים חייבים אותו baud rate."""

S["8cf252b5"] = r"""### 📘 מה צריך לדעת קודם
- `esp_sleep_enable_timer_wakeup(us)` – התעוררות אחרי זמן נתון, ב**מיקרו**-שניות: $10\text{ s}=10\cdot10^6\ \mu\text{s}$.
- ב-deep sleep ה-RAM הרגיל נמחק; משתנה עם `RTC_DATA_ATTR` נשמר בזיכרון ה-RTC ושורד את השינה.

### ✍️ הדרך המלאה (כמו במחברת)
```c
#include "esp_sleep.h"

#define uS_TO_S 1000000ULL              // microseconds in a second
#define SLEEP_S 10

RTC_DATA_ATTR int wakeCount = 0;        // kept in RTC memory during deep sleep

void setup() {
  Serial.begin(115200);
  delay(500);
  wakeCount++;                          // counts this boot / wake-up
  Serial.printf("Woke up %d times\n", wakeCount);

  esp_sleep_enable_timer_wakeup(SLEEP_S * uS_TO_S);   // 10 s
  esp_deep_sleep_start();
}

void loop() {}
```
✅ כל 10 שניות: "Woke up 1 times", "Woke up 2 times", ... (בלי `RTC_DATA_ATTR` היה מודפס תמיד 1).

💡 **הרעיון:** הזמן בטיימר במיקרו-שניות, והמונה ב-RTC כדי לשרוד את השינה."""

FIX_Q = {"83b2c6be": None}
FINE = ["2d31f517", "c0f71e7d", "3aae79ae", "32e720c8", "7ef708ca", "968bbeb5", "5fc67982", "912bcbdb", "57b69b82", "83b2c6be"]


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "micro_todo.json").read_text(encoding="utf-8"))}
    out = []
    for k, sol in S.items():
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": sol + DONE, "uncertain": k == "b4931529", "lock": True})
    for k in FINE:
        x = xs[k]
        fx = {"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + OK, "uncertain": False, "lock": True}
        if k == "83b2c6be":
            fx["question_md"] = x["question_md"].replace("**b.**", "**ב.**")
            fx["solution_md"] = fx["solution_md"].replace("\nb. שגוי", "\nב. שגוי")
        if k == "7ef708ca":  # code written as a formula (shown red)
            fx["solution_md"] = fx["solution_md"].replace("$*dog = (status) ? (*dog | 0x02) : (*dog & ~0x02);$",
                                                          "`*dog = status ? (*dog | 0x02) : (*dog & ~0x02);`")
        out.append(fx)
    (HERE.parent / "fix_2811_micro_hollow.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
