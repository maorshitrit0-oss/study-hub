"""Class exercises ("📌 מהכיתה") of digital, micro, linear and comm, checked by Claude 15/11/2026 ("what about the other
courses?" - the exam is built from the exercises seen in class). Fixes:
- Digital lecture 4: the NMOS inverter with a resistor load had the data of slide 6 (R=1k) and V_OL=0.1 (wrong even for
  those data: 1.13). Replaced by the full class exercise of slides 7-12 (R=10k, k'=20u, W/L=10): V_OL=0.59, V_IL=1.5,
  V_IH=3.082, V_M=2.56, NM_H=1.918, NM_L=0.91, P_avg=1.1025 mW - every number re-solved and equal to the slides.
- Micro: the three bit-field exercises had C code written as LaTeX formulas -> real C code blocks.
- Linear: two-stage op-amp (broken $$ delimiter, layout) and the active low-pass (a garbled "(שגוי תוקן:" line).
- Comm: 5.8 GHz distance (a wrong 47.7 in the substitution; 20log f = 195.27), Q(2) = 0.0228 (not 0.00228),
  dBm / SNR layout.
  python class_1511.py -> chapters/class-1511-<course>.json (publish inspect=exercises, one per course)"""
import json
from pathlib import Path

DIGITAL = [{"id": "ce0d3288-745a-47e4-8e8b-1fdc03d5cd0f",
 "title": "📌 מהכיתה: מהפך NMOS עם נגד עומס – כל נקודות ה-VTC, שולי רעש והספק",
 "question_md": r"""נתון מהפך NMOS עם נגד עומס (שקפים 7–12 בהרצאה):
$$R=10\,k\Omega,\quad V_{DD}=5\,V,\quad V_t=1\,V,\quad k_n'=\mu_nC_{ox}=20\,\mu A/V^2,\quad W/L=10$$

1. מצא את $V_{OH}$ ו-$V_{OL}$.
2. מצא את $V_{IL}$, $V_{IH}$, $V_M$, וחשב את $V_{LS}$ ואת $V_{TW}$.
3. חשב את שולי הרעש $NM_H$ ו-$NM_L$.
4. חשב את ההספק הסטטי הממוצע.""",
 "solution_md": r"""**נתון עזר:** $$k_n'\frac WL=20\mu\cdot10=0.2\,mA/V^2$$

### סעיף 1 – $V_{OH}$ ו-$V_{OL}$

**$V_{OH}$:** כש-$V_I<V_t=1\,V$ הטרנזיסטור בקיטעון, אין זרם, אין מפל על הנגד:
$$V_{OH}=V_{DD}=5\,V$$ ✅

**$V_{OL}$:** כש-$V_I=5\,V$ המוצא נמוך ⇐ $V_{DS}<V_{GS}-V_t$ ⇐ **טריודה**.

**נוסחה:** $$I_D=k_n'\frac WL\left[(V_I-V_t)V_O-\tfrac12V_O^2\right]=0.2(V_I-1)V_O-0.1V_O^2\;[mA]$$

$$V_O=V_{DD}-I_DR=5-2(V_I-1)V_O+V_O^2$$

**הצבה** ($V_I=5$): $$V_O=5-8V_O+V_O^2\;\Rightarrow\;V_O^2-9V_O+5=0$$

**תוצאה:** $$V_O=\frac{9-\sqrt{61}}{2}\;\Rightarrow\;V_{OL}=0.59\,V$$ ✅ (השורש השני, 8.4 V, גדול מ-$V_{DD}$ ונפסל)

### סעיף 2 – $V_{IL}$, $V_{IH}$, $V_M$

**ברוויה** ($V_O>V_I-1$): $$I_D=\tfrac12k_n'\tfrac WL(V_I-1)^2=0.1(V_I-1)^2\;\Rightarrow\;V_O=5-(V_I-1)^2$$

**$V_{IL}$** – הנקודה הראשונה שבה השיפוע $-1$ (עדיין ברוויה):
$$\frac{dV_O}{dV_I}=-2(V_I-1)=-1\;\Rightarrow\;V_{IL}=1.5\,V$$ ✅
בדיקה: $V_O=5-0.5^2=4.75\,V>V_I-1=0.5$ ⇐ אכן רוויה.

**$V_{IH}$** – השיפוע $-1$ בטריודה. גוזרים את $V_O=5-2(V_I-1)V_O+V_O^2$ לפי $V_I$ ומציבים $\frac{dV_O}{dV_I}=-1$:
$$-1=-2V_O+2(V_I-1)-2V_O\;\Rightarrow\;V_O=\frac{2V_I-1}{4}$$
מציבים בחזרה ופותרים: $$3V_I^2-3V_I-19.25=0\;\Rightarrow\;V_{IH}=\frac{3+\sqrt{240}}{6}=3.082\,V$$ ✅
(שם $V_O=1.29\,V$ – קטן מ-$V_I-1$, טריודה כנדרש)

**$V_M$** – $V_O=V_I$ (ברוויה): $$V_M=5-(V_M-1)^2\;\Rightarrow\;V_M^2-V_M-4=0\;\Rightarrow\;V_M=\frac{1+\sqrt{17}}{2}=2.56\,V$$ ✅

**מפתח לוגי ורוחב מעבר:**
$$V_{LS}=V_{OH}-V_{OL}=5-0.59=4.41\,V$$ ✅
$$V_{TW}=V_{IH}-V_{IL}=3.082-1.5=1.582\,V$$ ✅

### סעיף 3 – שולי רעש

$$NM_H=V_{OH}-V_{IH}=5-3.082=1.918\,V$$ ✅
$$NM_L=V_{IL}-V_{OL}=1.5-0.59=0.91\,V$$ ✅

### סעיף 4 – הספק סטטי

- מוצא גבוה (כניסה נמוכה): הטרנזיסטור בקיטעון, $I=0$ ⇐ $P(OH)=0$.
- מוצא נמוך: $$P(OL)=V_{DD}\cdot\frac{V_{DD}-V_{OL}}{R}=5\cdot\frac{5-0.59}{10\,k}=2.205\,mW$$

**תוצאה:** $$P_{AVG}=\frac{P(OH)+P(OL)}2=1.1025\,mW$$ ✅

> ⚠️ תוקן: בגרסה הקודמת היו הנתונים של שקף 6 ($R=1\,k\Omega$, $k_n'W/L=1\,mA/V^2$) ו-$V_{OL}=0.1\,V$ – גם עבורם זה לא נכון (יוצא 1.13 V). זה התרגיל שנפתר בכיתה בשקפים 7–12, וכל המספרים נפתרו מחדש ותואמים לשקפים.

💡 **הרעיון:** $V_{OH}$ – קיטעון; $V_{OL}$ ו-$V_{IH}$ – טריודה; $V_{IL}$ ו-$V_M$ – רוויה. תמיד מנחשים מצב, פותרים, ובודקים את התנאי."""}]

MICRO = [
 {"id": "e24e192e-1721-496a-99da-b2e7128ddde9", "solution_md": r"""**שלב 1 – הזזה:** `1 << 5` מזיז את הסיבית 1 חמישה מקומות שמאלה:
$$1\ll5=100000_2=32$$

**שלב 2 – מינוס 1:** כל הסיביות שמתחת הופכות ל-1:
$$32-1=31=11111_2$$ ✅

```c
#define AGE_BITS 5
#define MAX_AGE ((1 << AGE_BITS) - 1)   /* 31 */
```

💡 **הרעיון:** $(1\ll n)-1$ נותן מסכה של $n$ אחדות – הערך המקסימלי ששדה של $n$ ביטים יכול להחזיק. כך לא כותבים "מספר קסם"."""},
 {"id": "9df26f09-e09c-48b3-a2ca-26a2e76765fc", "solution_md": r"""**שלב 1 – בדיקת מצביע:** אם המצביע הוא `NULL` מחזירים $-1$.

**שלב 2 – עדכון ביט 1:** המסכה היא $1\ll1=2$ (בבינארי `00000010`).
- הדלקה: `OR` עם המסכה – שאר הביטים לא משתנים.
- כיבוי: `AND` עם השלילה של המסכה (`11111101`) – רק ביט 1 מתאפס.

```c
#define HAPPY_BIT  1
#define HAPPY_MASK (1 << HAPPY_BIT)     /* 2 */

int dog_set_is_happy(unsigned char *dog, int status)
{
    if (!dog)
        return -1;
    if (status)
        *dog |= HAPPY_MASK;
    else
        *dog &= ~HAPPY_MASK;
    return 0;
}
```
✅

💡 **הרעיון:** הדלקת ביט = `|=` מסכה; כיבוי ביט = `&=` שלילת המסכה."""},
 {"id": "553159a3-4484-466f-a0e1-0cc3cbc6224a", "solution_md": r"""**שלב 1 – בדיקות:** מצביע לא תקין, או גיל מחוץ ל-$0..31$ ⇐ מחזירים $-1$.

**שלב 2 – המסכה של השדה:** 5 ביטים שמתחילים בביט 2:
$$AGE\_MASK=31\ll2=01111100_2=124$$

**שלב 3 – איפוס השדה:** `AND` עם השלילה (`10000011`) – הביטים 2–6 מתאפסים, ביטים 0, 1, 7 נשמרים.

**שלב 4 – הצבה:** מזיזים את הגיל החדש למקומו ועושים `OR`.

```c
#define AGE_START_BIT 2
#define AGE_BITS      5
#define MAX_AGE  ((1 << AGE_BITS) - 1)            /* 31 */
#define AGE_MASK (MAX_AGE << AGE_START_BIT)       /* 0x7C */

int dog_set_age(unsigned char *dog, int new_age)
{
    if (!dog || new_age < 0 || new_age > MAX_AGE)
        return -1;
    *dog &= ~AGE_MASK;                              /* clear bits 2..6 */
    *dog |= (unsigned char)(new_age << AGE_START_BIT);
    return 0;
}
```
✅

**דוגמה:** `*dog = 0x83` (ביטים 7, 1, 0 דולקים), `new_age = 5`: איפוס ⇐ `0x83`; $5\ll2=20=$ `0x14` ⇐ התוצאה `0x97`.

💡 **הרעיון:** עדכון שדה של כמה ביטים = קודם לאפס (`&= ~MASK`), אחר כך להזיז ולהדליק (`|= value << start`). בלי האיפוס – ביטים של הגיל הישן נשארים."""},
]

LINEAR = [
 {"id": "258f4f74-7732-4159-bee1-ca3eb7e03fa4", "solution_md": r"""**שלב 1 – מגבר ראשון** (מהפך, הדק $-$ באדמה מדומה). KCL בהדק $-$:

**נוסחה:** $$\frac{V_{in}-0}{10\,k}=\frac{0-V_x}{30\,k}$$

**תוצאה:** $$V_x=-3V_{in}$$

**שלב 2 – מגבר שני** (מהפך עם שני נגדים של $40\,k$):

**נוסחה:** $$\frac{V_x-0}{40\,k}=\frac{0-V_{out}}{40\,k}$$

**תוצאה:** $$V_{out}=-V_x=3V_{in}$$

**סעיף א – הגבר:** $$A_v=\frac{V_{out}}{V_{in}}=3$$ ✅

**סעיף ב – התנגדות מבוא.** מהמקור יוצאים שני זרמים: דרך $10\,k$ לאדמה המדומה, ודרך נגד המשוב הגלובלי $20\,k$ אל המוצא:

**נוסחה:** $$I_{in}=\frac{V_{in}}{10\,k}+\frac{V_{in}-V_{out}}{20\,k}$$

**הצבה:** $$I_{in}=\frac{V_{in}}{10\,k}+\frac{V_{in}-3V_{in}}{20\,k}=\frac{V_{in}}{10\,k}-\frac{V_{in}}{10\,k}=0$$

**תוצאה:** $$R_{in}=\frac{V_{in}}{I_{in}}\to\infty$$ ✅

💡 **הרעיון:** המשוב הגלובלי מחזיר מהמוצא בדיוק את הזרם שהמגבר הראשון "לוקח" – המקור לא מספק זרם בכלל, ולכן התנגדות המבוא אינסופית."""},
 {"id": "8539b42d-a6e8-4e12-bd28-a190e933f550", "solution_md": r"""**שלב 1 – עכבת המשוב** ($R_2$ במקביל ל-$C$):

**נוסחה:** $$Z_f=R_2\parallel\frac1{j\omega C}=\frac{R_2}{1+j\omega R_2C}$$

**הצבה:** $$R_2C=50\cdot10^3\cdot10^{-6}=0.05\,s$$

**תוצאה:** $$Z_f=\frac{50\,k\Omega}{1+j0.05\omega}$$

**שלב 2 – פונקציית התמסורת** (מגבר מהפך):

**נוסחה:** $$H(j\omega)=-\frac{Z_f}{R_1}=-\frac{R_2}{R_1}\cdot\frac1{1+j\omega R_2C}$$

**הצבה ותוצאה:** $$H(j\omega)=\frac{-2.5}{1+j0.05\omega}$$ ✅ (הגבר DC: $-2.5$, כלומר $\approx8\,dB$)

**שלב 3 – תדר החיתוך:**

**נוסחה:** $$f_c=\frac1{2\pi R_2C}$$

**הצבה:** $$f_c=\frac1{2\pi\cdot0.05}$$

**תוצאה:** $$f_c\approx3.18\,Hz$$ ✅ ($\omega_c=20\,rad/s$)

💡 **הרעיון:** בתדר נמוך הקבל "פתוח" והמעגל הוא מגבר מהפך $-R_2/R_1$; בתדר גבוה הקבל מקצר את המשוב וההגבר יורד. הקוטב ב-$1/R_2C$."""},
]

COMM = [
 {"id": "ff8590cc-440d-49a9-adf1-5f04974789c5", "solution_md": r"""**נוסחה (FSPL בדציבלים):** $$FSPL=20\log_{10}d+20\log_{10}f+20\log_{10}\frac{4\pi}{c}$$

הקבוע: $$20\log_{10}\frac{4\pi}{3\cdot10^8}=-147.56\,dB$$

**סעיף א – $f_1=2.45\,GHz$:**

**הצבה:** $$104=20\log_{10}d_1+187.78-147.56\;\Rightarrow\;20\log_{10}d_1=63.78$$

**תוצאה:** $$d_1=10^{63.78/20}\approx1.55\,km$$ ✅

**סעיף ב – $f_2=5.8\,GHz$:**

**הצבה:** $$104=20\log_{10}d_2+195.27-147.56\;\Rightarrow\;20\log_{10}d_2=56.29$$

**תוצאה:** $$d_2=10^{56.29/20}\approx652\,m$$ ✅

**בדיקה מהירה:** אותו תקציב ⇐ $d\propto1/f$: $$\frac{d_1}{d_2}=\frac{5.8}{2.45}=2.37$$ ✔

> ⚠️ תוקן: בהצבה של סעיף ב היה כתוב 47.7 במקום $20\log_{10}(5.8\cdot10^9)=195.27$. התוצאה הסופית לא השתנתה.

💡 **הרעיון:** בתקציב קישור קבוע, הכפלת התדר מקצרת את הטווח פי 2 (כי $FSPL$ גדל ב-$20\log f$)."""},
 {"id": "c60c0f64-1492-4349-9f15-c5297c626d19", "solution_md": r"""**נוסחה:** $$P_{dBm}=10\log_{10}\frac{P}{1\,mW}$$

**הצבה:** $$P_{dBm}=10\log_{10}\frac{10\,W}{10^{-3}\,W}=10\log_{10}10^4$$

**תוצאה:** $$P_{dBm}=40\,dBm$$ ✅ (וגם $10\,dBW$ – תמיד $dBm=dBW+30$)

💡 **הרעיון:** dBm = דציבלים ביחס למיליוואט. כל פי 10 בהספק מוסיף 10 dB."""},
 {"id": "f498bfee-a386-452e-98db-ff01b61b31a7", "solution_md": r"""**ליניארי:**

**נוסחה:** $$SNR=\frac{P_r}{P_n}$$

**הצבה:** $$SNR=\frac{10^{-3}\,W}{10^{-12}\,W}$$

**תוצאה:** $$SNR=10^9$$ ✅

**בדציבלים:**

**נוסחה:** $$SNR_{dB}=10\log_{10}SNR$$

**הצבה:** $$10\log_{10}10^9$$

**תוצאה:** $$SNR_{dB}=90\,dB$$ ✅

בדיקה: $P_r=0\,dBm$, $P_n=-90\,dBm$ ⇐ ההפרש 90 dB ✔

💡 **הרעיון:** יחס הספקים בדציבלים = הפרש בין שני ההספקים ב-dBm."""},
 {"id": "e79529cb-8d6b-46d1-8501-6d5182cc8d0f", "solution_md": r"""**שלב 1 – ההסתברות כאינטגרל של הצפיפות הגאוסית מעל הסף:**
$$P_e=P(n>L)=\int_L^\infty\frac1{\sqrt{2\pi}\,\sigma}e^{-n^2/2\sigma^2}\,dn$$

**שלב 2 – החלפת משתנה** $u=n/\sigma$ ⇐ פונקציית Q:
$$P_e=\int_{L/\sigma}^\infty\frac1{\sqrt{2\pi}}e^{-u^2/2}\,du=Q\!\left(\frac L\sigma\right)$$

**שלב 3 – הצבה:** $$P_e=Q(2)$$

**תוצאה:** $$P_e\approx0.0228=2.28\%$$ ✅

> ⚠️ תוקן: בגרסה הקודמת נכתב בסוגריים 0.00228 – זה 0.228%. הנכון: $Q(2)=0.02275$.

💡 **הרעיון:** הסתברות שהרעש יחצה את הסף = $Q(\text{סף}/\sigma)$. ערכים לזכור: $Q(1)\approx0.159$, $Q(2)\approx0.023$, $Q(3)\approx0.00135$."""},
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for name, fx in (("digital", DIGITAL), ("micro", MICRO), ("linear", LINEAR), ("comm", COMM)):
        out = root / f"class-1511-{name}.json"
        out.write_text(json.dumps(fx, ensure_ascii=False, indent=1), encoding="utf-8")
        print(out, len(fx))
