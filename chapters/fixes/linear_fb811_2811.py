"""Linear circuits - "הרצאה 8-1-1 - מגברי משוב - תרגיל" (the lecturer's handwritten worked examples 1, 2, 4, 5, 6),
rewritten by Claude from the scanned pages (28/11/2026). Example 1's numbers re-computed: his r_in used r_pi=0.899k
and a'_R=265k (both small slips) - flagged. Writes chapters/fix_2811_lin_fb811.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נכתב מחדש לפי הפתרון בכתב יד של המרצה (קובץ 8-1-1); המספרים חושבו מחדש."
Q, S = {}, {}
LEG = r"""- סימון המרצה: אות ראשונה = חיבור בכניסה (S טור / P מקביל), אות שנייה = חיבור במוצא. **SIPO** = מתח-טור, **PIPO** = מתח-מקביל, **SISO** = זרם-טור, **PISO** = זרם-מקביל.
- זיהוי לפי המרצה: **מקצרים** את $R_L$ – אם המשוב נעלם, הדגימה היא **מתח** (מקביל); אם לא – **זרם** (טור). **מקצרים** את $v_s$ – אם המשוב נעלם, ההחזרה **מקבילית**; אם לא – **טורית**.
- $A=\frac{a}{1+Ba}$; בצד שמחובר בטור ההתנגדות גדלה פי $(1+Ba)$, בצד שמחובר במקביל היא קטנה פי $(1+Ba)$."""

Q["97f5063e"] = r"""**תרגיל 1** (תרגול משוב 8-1-1). מגבר אמיטר משותף: $R_C=2.7\text{ k}\Omega$ מ-$V_{CC}$ לקולקטור; $R_3=89\text{ k}\Omega$ מהקולקטור לבסיס (משוב); $R_E=0.5\text{ k}\Omega$ באמיטר **עם קבל מעקף**; $v_s$ (אידאלי) דרך קבל לבסיס; $v_o$ מהקולקטור דרך קבל על $R_L=10\text{ k}\Omega$. נתון $I_C=3\text{ mA}$, $\beta=100$.

חשב את הגבר החוג הסגור $A_R=\frac{v_o}{i_s}$ ואת התנגדות המבוא עם משוב $R_{in}$.

**א.** $A_R\approx-62\text{ k}\Omega$, $R_{in}\approx0.26\text{ k}\Omega$

**ב.** $A_R\approx-45\text{ k}\Omega$, $R_{in}\approx0.50\text{ k}\Omega$

**ג.** $A_R\approx-120\text{ k}\Omega$, $R_{in}\approx0.15\text{ k}\Omega$

**ד.** $A_R\approx-62\text{ k}\Omega$, $R_{in}\approx0.85\text{ k}\Omega$"""
S["97f5063e"] = r"""התשובה: **א**

### 📘 מה צריך לדעת קודם
""" + LEG + r"""
- $g_m=\frac{I_C}{26\text{ mV}}$, $r_\pi=\frac{\beta}{g_m}$.

### ✍️ הדרך המלאה (כמו במחברת)
1. $g_m=\frac{3}{26}=0.115\ \text{S}$, $r_\pi=\frac{100}{0.115}=866\ \Omega$.
2. **זיהוי:** $v_s\uparrow\Rightarrow I_B\uparrow\Rightarrow I_C\uparrow\Rightarrow V_{CE}\downarrow\Rightarrow V_C\downarrow\Rightarrow V_B\downarrow$ – משוב שלילי. קיצור $R_L$ מבטל אותו (מתח), קיצור $v_s$ מבטל אותו (מקביל) ⇐ **PIPO**.
3. $$B=\frac{i_f}{v_o}=\frac{-v_o/R_3}{v_o}=-\frac{1}{R_3}=-\frac{1}{89\text{ k}\Omega}$$
4. **בלי משוב** (עם ההעמסות: $R_3$ בכניסה ו-$R_3$ במוצא):
$$a_R=\frac{v_o}{i_i}=-g_m\,(R_C\parallel R_L\parallel R_3)(r_\pi\parallel R_3)=-0.115\cdot2.076\text{k}\cdot0.858\text{k}=-205\text{ k}\Omega$$
$$r_{in}=R_3\parallel r_\pi=0.858\text{ k}\Omega,\qquad r_{out}=R_C\parallel R_3=2.62\text{ k}\Omega$$
5. $1+Ba_R=1+\frac{205}{89}=3.30$:
$$A_R=\frac{-205}{3.30}$$
✅ $A_R\approx-62\text{ k}\Omega$
$$R_{in}=\frac{0.858}{3.30}$$
✅ $R_{in}\approx0.26\text{ k}\Omega$
6. ל-$R_{out}$ (בלי $R_L$): $a_R'=-g_m(R_C\parallel R_3)(r_\pi\parallel R_3)=-0.115\cdot2.62\text{k}\cdot0.858\text{k}=-258\text{ k}\Omega$:
$$R_{out}=\frac{2.62}{1+\frac{258}{89}}\approx0.67\text{ k}\Omega$$

> ⚠️ בדף של המרצה: $r_{in}=0.88\text{ k}\Omega$ (חושב עם $0.899$ במקום $0.866$) ⇐ $0.266\text{ k}\Omega$, ו-$a_R'=-265\text{ k}\Omega$ ⇐ $R_{out}=0.658\text{ k}\Omega$. עם $r_\pi=866\ \Omega$ יוצא $0.26$ ו-$0.67\text{ k}\Omega$; התשובה לשאלה (א) לא משתנה.

**למה לא האחרות:** ד – $0.85\text{ k}\Omega$ הוא $r_{in}$ **בלי** המשוב (שכחו לחלק ב-$1+Ba_R$); ב, ג – לא מתקבלים מהמעגל.

💡 **הרעיון:** נגד מקולקטור לבסיס = PIPO: מקטין את ההגבר ואת שתי ההתנגדויות פי $1+Ba_R$."""

Q["36595015"] = r"""**תרגיל 2** (תרגול משוב 8-1-1). מגבר שרת לא-הופך: $v_i$ לכניסה $+$; $R_1$ מהכניסה $-$ לאדמה; $R_2$ מהמוצא $v_o$ לכניסה $-$. מגבר השרת: $a_v\to\infty$ (למשל $10^5$), $r_{in}=\infty$, $r_{out}=0$.

א. זהה את סוג המשוב. ב. חשב את מקדם המשוב $B$. ג. שרטט מגבר ללא משוב עם העמסות, ומצא את ההגבר בחוג סגור ואת $R_{in}$, $R_{out}$."""
S["36595015"] = r"""### 📘 מה צריך לדעת קודם
""" + LEG + r"""

### ✍️ הדרך המלאה (כמו במחברת)
**א.** משוב שלילי (חוזר לכניסה $-$). קיצור $R_L$ ⇐ המשוב נעלם ⇐ דגימת **מתח**. קיצור $v_s$ ⇐ המשוב **לא** נעלם (הוא נכנס לכניסה השנייה) ⇐ החזרה **טורית**.
✅ **SIPO** (מתח-טור)

**ב.**
$$V_f=V_o\frac{R_1}{R_1+R_2}$$
✅ $B=\frac{V_f}{V_o}=\frac{R_1}{R_1+R_2}$

**ג.** מגבר ללא משוב: בכניסה $-$ לאדמה – $R_1\parallel R_2$ (המוצא מקוצר); במוצא – $R_1+R_2$ לאדמה (הכניסה פתוחה). עם מגבר אידאלי: $a_v=\infty$, $r_{in}=\infty$, $r_{out}=0$.
$$A_v=\frac{a_v}{1+Ba_v}\xrightarrow{a_v\to\infty}\frac{1}{B}$$
✅ $A_v=1+\frac{R_2}{R_1}$, $R_{in}=r_{in}(1+Ba_v)=\infty$, $R_{out}=\frac{r_{out}}{1+Ba_v}=0$

💡 **הרעיון:** כשההגבר הפתוח עצום, ההגבר נקבע רק על ידי רשת המשוב: $\frac{1}{B}$."""

Q["da031414"] = r"""**תרגיל 4** (תרגול משוב 8-1-1). אמיטר משותף עם נגד אמיטר: $v_{in}$ לבסיס, $R_E$ מהאמיטר לאדמה, $R_L$ מהקולקטור ל-$V_{CC}$ (בעומס זורם $i_o$). $r_o=\infty$.

א. זהה את סוג המשוב. ב. חשב את $B$. ג. חשב את ההגבר בחוג פתוח $a_G=\frac{i_o}{v_{in}}$, את $r_{in}$, $r_{out}$, ואת $A_G$, $R_{in}$, $R_{out}$ עם המשוב."""
S["da031414"] = r"""### 📘 מה צריך לדעת קודם
""" + LEG + r"""
- ב-SISO ההגבר הוא **מוליכות** $a_G=\frac{i_o}{v_i}$, ו-$B=\frac{v_f}{i_o}$ ביחידות של התנגדות.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** קיצור $R_L$ לא מבטל את המשוב (זרם האמיטר עדיין זורם ב-$R_E$) ⇐ דגימת **זרם**. קיצור $v_s$ לא מבטל אותו ($v_f$ על $R_E$ בטור עם $v_\pi$) ⇐ **טור**.
✅ **SISO** (זרם-טור)

**ב.** ($i_o$ זורם אל הקולקטור, ולכן באמיטר $-i_o$)
$$v_f=-i_oR_E$$
✅ $B=\frac{v_f}{i_o}=-R_E$

**ג.** בלי משוב: בכניסה $r_\pi$ בטור עם $R_E$ (המוצא "פתוח" לגבי המשוב):
$$v_\pi=v_{in}\frac{r_\pi}{r_\pi+R_E},\qquad i_o=-g_mv_\pi$$
$$a_G=\frac{i_o}{v_{in}}=\frac{-g_mr_\pi}{r_\pi+R_E},\qquad r_{in}=r_\pi+R_E,\qquad r_{out}=\infty\ (r_o=\infty)$$
$$1+Ba_G=1+\frac{g_mr_\pi R_E}{r_\pi+R_E}=\frac{r_\pi+(\beta+1)R_E}{r_\pi+R_E}$$
✅ $A_G=\frac{a_G}{1+Ba_G}=\frac{-\beta}{r_\pi+(\beta+1)R_E}$

✅ $R_{in}=r_{in}(1+Ba_G)=r_\pi+(\beta+1)R_E$

✅ $R_{out}=r_{out}(1+Ba_G)$ – גדלה (במוצא טורי).

> ⚠️ במחברת המרצה נכתב $r_{out}=R_L$. עם $r_o=\infty$ ההתנגדות שמסתכלים לתוך הקולקטור אינסופית (גם בלי משוב), והעומס $R_L$ הוא מחוץ לחוג; הנוסחה $R_{out}=r_{out}(1+Ba_G)$ נכונה, אבל עבור $r_{out}$ של הטרנזיסטור.

💡 **הרעיון:** נגד אמיטר לא מעוקף = משוב SISO. כך מקבלים את הנוסחאות המוכרות $r_\pi+(\beta+1)R_E$ ו-$\frac{-\beta R_L}{r_\pi+(\beta+1)R_E}$."""

Q["7e482e40"] = r"""**תרגיל 5** (תרגול משוב 8-1-1). שתי דרגות אמיטר משותף. $Q_1$: $v_{in}$ לבסיס, $R_C$ בקולקטור; באמיטר $R_E$ **עם קבל מעקף**, ומתחתיו $R_1$ לאדמה (בלי מעקף). קבל צימוד מהקולקטור של $Q_1$ לבסיס $Q_2$. $Q_2$: אמיטר באדמה, $R_L$ בקולקטור, $v_o$ בקולקטור. משוב: $R_2$ מ-$v_o$ לצומת שבין $R_E$ ל-$R_1$.

א. זהה את סוג המשוב. ב. חשב את $B$. ג. מצא את $a_v=\frac{v_o}{v_{in}}$ בלי משוב (עם העמסות), $r_{in}$, $r_{out}$, ואת $R_{if}$, $R_{of}$."""
S["7e482e40"] = r"""### 📘 מה צריך לדעת קודם
""" + LEG + r"""

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $v_{in}\uparrow\Rightarrow v_{C1}\downarrow\Rightarrow v_{B2}\downarrow\Rightarrow v_{C2}\uparrow\Rightarrow v_{E1}\uparrow\Rightarrow v_{BE1}\downarrow$ – משוב שלילי. קיצור $R_L$ (המוצא) מבטל אותו ⇐ **מתח**; קיצור $v_{in}$ לא מבטל ($v_f$ באמיטר) ⇐ **טור**.
✅ **SIPO**

**ב.**
$$V_f=V_o\frac{R_1}{R_1+R_2}$$
✅ $B=\frac{R_1}{R_1+R_2}$ (חיובי, וגם $a_v>0$ – שתי דרגות הופכות)

**ג.** העמסות: באמיטר של $Q_1$ – $R_1\parallel R_2$; במוצא – $R_1+R_2$ במקביל ל-$R_L$. ($R_E$ מעוקף.)
$$v_{\pi1}=v_{in}\frac{r_{\pi1}}{r_{\pi1}+(R_1\parallel R_2)(g_{m1}r_{\pi1}+1)}$$
$$v_{\pi2}=-g_{m1}v_{\pi1}\,(R_C\parallel r_{\pi2}),\qquad v_o=-g_{m2}v_{\pi2}\left[(R_1+R_2)\parallel R_L\right]$$
✅ $a_v=\frac{g_{m1}g_{m2}\,r_{\pi1}(R_C\parallel r_{\pi2})\left[(R_1+R_2)\parallel R_L\right]}{r_{\pi1}+(R_1\parallel R_2)(g_{m1}r_{\pi1}+1)}$

✅ $r_{in}=r_{\pi1}+(g_{m1}r_{\pi1}+1)(R_1\parallel R_2)$ ⇐ $R_{if}=r_{in}(1+a_vB)$

✅ $r_{out}=R_L\parallel(R_1+R_2)$ ⇐ $R_{of}=\frac{r_{out}}{1+a_vB}$

💡 **הרעיון:** מתח-טור: הכניסה (טור) גדלה, המוצא (מקביל) קטן, וההגבר שואף ל-$\frac{1}{B}=1+\frac{R_2}{R_1}$."""

Q["e6234ab0"] = r"""**תרגיל 6** (תרגול משוב 8-1-1). שתי דרגות. $Q_1$: $v_{in}$ (זרם $i_{in}$) לבסיס, אמיטר באדמה, $R_1$ בקולקטור. קבל צימוד לבסיס $Q_2$. $Q_2$: $R_L$ בקולקטור ($i_o$, $v_o$), $R_E$ מהאמיטר לאדמה. משוב: $R_2$ מהאמיטר של $Q_2$ לבסיס של $Q_1$.

א. זהה את סוג המשוב. ב. חשב את $B$. ג. מצא את הגבר הזרם בלי משוב $a_i=\frac{i_o}{i_{in}}$ (עם העמסות), $r_{in}$, $r_{out}$, ואת $R_{if}$, $R_{of}$."""
S["e6234ab0"] = r"""### 📘 מה צריך לדעת קודם
""" + LEG + r"""
- ב-PISO ההגבר הוא הגבר **זרם** $a_i=\frac{i_o}{i_{in}}$ ו-$B=\frac{i_f}{i_o}$ (בלי יחידות).

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $v_{in}\uparrow\Rightarrow v_{C1}\downarrow\Rightarrow v_{B2}\downarrow\Rightarrow v_{E2}\downarrow\Rightarrow v_{in}\downarrow$ – משוב שלילי. קיצור $R_L$ לא מבטל (זרם האמיטר עדיין ב-$R_E$) ⇐ **זרם**; קיצור $v_s$ מבטל ($R_2$ הולך לאדמה) ⇐ **מקביל**.
✅ **PISO** (זרם-מקביל)

**ב.** כשהכניסה מקוצרת, $i_o$ (באמיטר) מתחלק בין $R_E$ ל-$R_2$:
$$i_f=i_o\frac{R_E}{R_E+R_2}$$
✅ $B=\frac{R_E}{R_E+R_2}$

**ג.** העמסות: בכניסה – $R_2+R_E$ לאדמה (במקביל ל-$r_{\pi1}$); באמיטר של $Q_2$ – $R_2\parallel R_E$.
$$v_{\pi1}=i_{in}\frac{(R_E+R_2)\,r_{\pi1}}{R_E+R_2+r_{\pi1}}$$
$$v_{\pi2}=-g_{m1}v_{\pi1}\left(R_1\parallel\left[r_{\pi2}+(g_{m2}r_{\pi2}+1)(R_2\parallel R_E)\right]\right)\frac{r_{\pi2}}{r_{\pi2}+(g_{m2}r_{\pi2}+1)(R_2\parallel R_E)}$$
$$i_o=-g_{m2}v_{\pi2}$$
✅ $a_i=g_{m1}g_{m2}\frac{\left(R_1\parallel\left[r_{\pi2}+(g_{m2}r_{\pi2}+1)(R_2\parallel R_E)\right]\right)r_{\pi2}\,r_{\pi1}(R_E+R_2)}{\left[r_{\pi2}+(g_{m2}r_{\pi2}+1)(R_2\parallel R_E)\right](R_E+R_2+r_{\pi1})}$

✅ $r_{in}=(R_2+R_E)\parallel r_{\pi1}$ ⇐ $R_{if}=\frac{r_{in}}{1+a_iB}$

✅ $r_{out}$ – במוצא הטורי ⇐ $R_{of}=r_{out}(1+a_iB)$ (במחברת $r_{out}=R_L$; עם $r_o=\infty$ ההתנגדות לתוך הקולקטור אינסופית, ראה ההערה בתרגיל 4)

💡 **הרעיון:** דגימה באמיטר = זרם, החזרה לצומת הבסיס = מקביל ⇐ מגבר זרם: $A_i\to\frac{1}{B}=1+\frac{R_2}{R_E}$."""


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "lin_todo.json").read_text(encoding="utf-8"))}
    out = [{"id": xs[k]["id"], "title": xs[k]["title"], "question_md": Q[k], "solution_md": S[k] + DONE, "uncertain": False}
           for k in S]
    (HERE.parent / "fix_2811_lin_fb811.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
