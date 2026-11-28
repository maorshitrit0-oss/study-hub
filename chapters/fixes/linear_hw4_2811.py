"""Linear circuits - "עבודת בית 4 - BJT ניתוח DC" questions 10, 15, 16, 18, solved by Claude from the sheet and checked
against its final answers (28/11/2026). Q18's stored answer (0.93 mA) ignored the base resistor - corrected to 0.84 mA.
Writes chapters/fix_2811_lin_hw4.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש מהדף ונבדק מול התשובות הסופיות שבסוף עבודת הבית."
Q, S = {}, {}

Q["5e8be879"] = r"""**שאלה 10** (עבודת בית 4). טרנזיסטור $pnp$: האמיטר דרך $1\text{ k}\Omega$ ל-$+5\text{ V}$, הבסיס דרך $10\text{ k}\Omega$ לאדמה, הקולקטור דרך $10\text{ k}\Omega$ ל-$-5\text{ V}$. נתון $\beta_{min}=30$ במצב פעיל, $V_{EC,sat}=0.2\text{ V}$, $V_{EB}=0.7\text{ V}$.

א. באיזה מצב נמצא הטרנזיסטור? ב. מצא את $V_B,V_C,V_E,I_B,I_C,I_E$."""
S["5e8be879"] = r"""### 📘 מה צריך לדעת קודם
- שיטה: מניחים **פעיל**, מחשבים, ובודקים. אם יוצא $V_C>V_E$ ב-$pnp$ (צומת ה-BC בממתח קדמי) – ההנחה נכשלה ⇐ **רוויה**.
- ברוויה: $V_{EB}=0.7$, $V_{EC}=0.2$, ו-$\frac{I_C}{I_B}<\beta_{min}$.

### ✍️ הדרך המלאה (כמו במחברת)
**א. הנחת פעיל:** $I_B=\frac{V_B}{10\text{k}}$ (יוצא מהבסיס לאדמה), $I_E=\frac{5-(V_B+0.7)}{1\text{k}}=31I_B$:
$$4.3-V_B=3.1V_B\ \Rightarrow\ V_B=1.05\text{ V},\ I_E=3.25\text{ mA},\ I_C=3.15\text{ mA}$$
$$V_C=-5+3.15\cdot10=26.5\text{ V}>V_E$$
בלתי אפשרי ⇐ ✅ **רוויה**.

**ב. ברוויה:** $V_E=V_B+0.7$, $V_C=V_E-0.2=V_B+0.5$.
$$\underbrace{\frac{4.3-V_B}{1}}_{I_E}=\underbrace{\frac{V_B}{10}}_{I_B}+\underbrace{\frac{V_B+5.5}{10}}_{I_C}\ \Rightarrow\ 43-10V_B=2V_B+5.5$$
✅ $V_B=3.125\text{ V}$, $V_E=3.825\text{ V}$, $V_C=3.625\text{ V}$

✅ $I_B=0.31\text{ mA}$, $I_C=0.86\text{ mA}$, $I_E=1.18\text{ mA}$

בדיקה: $\frac{I_C}{I_B}=2.8<30$ ✔ – רוויה עמוקה (כמו בתשובות הסופיות).

💡 **הרעיון:** נגד אמיטר קטן ($1\text{k}$) מול נגד קולקטור גדול ($10\text{k}$) ⇐ הזרם ה"רצוי" גדול מדי, והטרנזיסטור נדחף לרוויה."""

Q["93d82146"] = r"""**שאלה 15** (עבודת בית 4). ספקים $\pm10\text{ V}$, $\beta=100$, $|V_{BE}|=0.7\text{ V}$.
- $Q_1$ ($pnp$): הבסיס ($V_1$) דרך $100\text{ k}\Omega$ לאדמה; האמיטר ($V_2$) דרך $R_{E1}=9.1\text{ k}\Omega$ ל-$+10$; הקולקטור ($V_3$) דרך $R_{C1}=9.1\text{ k}\Omega$ ל-$-10$.
- $Q_2$ ($npn$): הבסיס ב-$V_3$; הקולקטור ($V_5$) דרך $R_{C2}=5.1\text{ k}\Omega$ ל-$+10$; האמיטר ($V_4$) דרך $R_{E2}=4.3\text{ k}\Omega$ ל-$-10$.

מהו $V_3$ עבור $\beta=100$?

**א.** $V_3=-1.86\text{ V}$

**ב.** $V_3=0.7\text{ V}$

**ג.** $V_3=-2.56\text{ V}$

**ד.** $V_3=1.86\text{ V}$"""
S["93d82146"] = r"""התשובה: **א**

### 📘 מה צריך לדעת קודם
- $I_B=\frac{I_E}{\beta+1}$; זרם הבסיס של $pnp$ **יוצא** מהבסיס.
- כש-$\beta=\infty$ (סעיף א במקור) – אין זרמי בסיס: $V_1=0$, $V_2=0.7$, $I_{E1}=\frac{9.3}{9.1}=1.022\text{ mA}$, $V_3=-0.7$, $V_4=-1.4$, $I_{E2}=2\text{ mA}$, $V_5=-0.2\text{ V}$.

### ✍️ הדרך המלאה (כמו במחברת)
1. **$Q_1$:** $V_1=100\text{k}\cdot\frac{I_{E1}}{101}$, ו-$I_{E1}=\frac{10-0.7-V_1}{9.1\text{k}}$:
$$9.1I_{E1}=9.3-0.990I_{E1}\ \Rightarrow\ I_{E1}=0.922\text{ mA}$$
$V_1=0.91\text{ V}$, $V_2=1.61\text{ V}$, $I_{C1}=0.913\text{ mA}$.
2. **הצומת $V_3$:** $I_{C1}$ מתחלק בין $R_{C1}$ לבסיס של $Q_2$:
$$0.913=\frac{V_3+10}{9.1}+\frac{V_3+9.3}{4.3\cdot101}$$
✅ $V_3\approx-1.85\text{ V}$ (בתשובות הסופיות: $-1.856$)
3. $V_4=V_3-0.7\approx-2.55\text{ V}$; $I_{E2}=\frac{-2.55+10}{4.3}=1.73\text{ mA}$; $V_5=10-1.715\cdot5.1=1.25\text{ V}$.

**למה לא האחרות:** ג – זה $V_4$ (האמיטר), לא $V_3$; ב, ד – סימן או $V_{BE}$ במקום מתח הצומת.

💡 **הרעיון:** עם $\beta$ סופי זרם הבסיס של $Q_2$ "גונב" חלק מ-$I_{C1}$, ולכן $V_3$ נמוך מ-$-0.7$ של המקרה האידאלי."""

Q["2baed17d"] = r"""**שאלה 16** (עבודת בית 4). $V_{CC}=12\text{ V}$, $\beta=100$, $V_{BE}=0.7\text{ V}$.
- $Q_1$: מחלק $R_{B1}=100\text{ k}\Omega$ (ל-$V_{CC}$) ו-$R_{B2}=22\text{ k}\Omega$ (לאדמה); $R_{C1}=5.1\text{ k}\Omega$; $R_{E1}=1\text{ k}\Omega$ עם קבל מעקף $10\ \mu\text{F}$.
- $Q_2$: הבסיס מחובר לקולקטור של $Q_1$; $R_{C2}$ ל-$V_{CC}$; $R_{E2}=50\ \Omega$ לאדמה.

נדרש מתח ישר של $6\text{ V}$ בין הקולקטור של $Q_2$ לאדמה. מהו $R_{C2}$?"""
S["2baed17d"] = r"""### 📘 מה צריך לדעת קודם
- ב-DC הקבל נתק (המעקף לא משנה את נקודת העבודה).
- מחלק בסיס ⇐ תבנין: $V_{TH}=V_{CC}\frac{R_{B2}}{R_{B1}+R_{B2}}$, $R_{TH}=R_{B1}\parallel R_{B2}$, $I_B=\frac{V_{TH}-0.7}{R_{TH}+(\beta+1)R_E}$.

### ✍️ הדרך המלאה (כמו במחברת)
1. $V_{TH}=12\cdot\frac{22}{122}=2.164\text{ V}$, $R_{TH}=100\parallel22=18.03\text{ k}\Omega$.
2. $I_{B1}=\frac{2.164-0.7}{18.03+101\cdot1}=12.3\ \mu\text{A}$ ⇐ $I_{C1}=1.23\text{ mA}$.
3. **הקולקטור של $Q_1$** ($V_{C1}$): הזרם ב-$R_{C1}$ = $I_{C1}+I_{B2}$, ו-$I_{B2}=\frac{V_{C1}-0.7}{101\cdot0.05\text{k}}$:
$$\frac{12-V_{C1}}{5.1}=1.23+\frac{V_{C1}-0.7}{5.05}\ \Rightarrow\ V_{C1}=3.20\text{ V}$$
4. $I_{E2}=\frac{3.20-0.7}{50\ \Omega}=50.0\text{ mA}$ ⇐ $I_{C2}=\frac{100}{101}\cdot50.0=49.5\text{ mA}$.
5. $$R_{C2}=\frac{12-6}{49.5\text{ mA}}$$
✅ $R_{C2}\approx121\ \Omega$ (בתשובות הסופיות: $122\ \Omega$)

💡 **הרעיון:** $Q_2$ עם $50\ \Omega$ באמיטר "מעמיס" את הקולקטור של $Q_1$ ($I_{B2}\approx0.5\text{ mA}$) – בלי לקחת אותו בחשבון $V_{C1}$ יוצא $5.7\text{ V}$ והזרם פי שניים."""

Q["e62bd2f9"] = r"""**שאלה 18** (שאלת רשות, עבודת בית 4). $V_i$ דרך $10\text{ k}\Omega$ וקבל לבסיס; $100\text{ k}\Omega$ מהבסיס לאדמה. הקולקטור דרך $10\text{ k}\Omega$ ל-$+10\text{ V}$, ומשם קבל ל-$V_o$ על עומס $10\text{ k}\Omega$. האמיטר דרך $10\text{ k}\Omega$ ל-$-10\text{ V}$, עם קבל מעקף לאדמה. $\beta=100$, $V_{BE}=0.7\text{ V}$.

א. בצע ניתוח DC. ב. מצא פרמטרי אות קטן, את ההגבר, וצייר מעגל תמורה."""
S["e62bd2f9"] = r"""### 📘 מה צריך לדעת קודם
- ב-DC הקבלים נתק: המקור והעומס מנותקים.
- KVL בחוג הבסיס-אמיטר: $0-I_BR_B-V_{BE}-I_ER_E=-V_{EE}$.
- $g_m=\frac{I_C}{V_T}$ ($V_T=26\text{ mV}$), $r_\pi=\frac{\beta}{g_m}$.

### ✍️ הדרך המלאה (כמו במחברת)
**א. DC**
$$I_B=\frac{10-0.7}{100\text{k}+101\cdot10\text{k}}=\frac{9.3}{1110\text{k}}=8.38\ \mu\text{A}$$
✅ $I_C=0.838\text{ mA}$, $I_E=0.846\text{ mA}$
- $V_B=-I_B\cdot100\text{k}=-0.84\text{ V}$, $V_E=-1.54\text{ V}$, $V_C=10-0.838\cdot10=1.62\text{ V}$.
- $V_{CE}=3.16\text{ V}>0.2$ ⇐ ✅ פעיל.

> ⚠️ בפתרון הקודם יצא $0.93\text{ mA}$ – הוא הניח $V_B=0$ ושכח את המפל על $100\text{ k}\Omega$ ($0.84\text{ V}$).

**ב. אות קטן**
- $g_m=\frac{0.838}{26}=32.2\text{ mS}$, $r_\pi=\frac{100}{32.2\text{m}}=3.1\text{ k}\Omega$.
- מעגל תמורה: $V_i$ – $10\text{k}$ – בסיס; מהבסיס $100\text{k}\parallel r_\pi$ לאדמה; מקור $g_mv_\pi$ מהקולקטור לאדמה, ובמקביל $10\text{k}\parallel10\text{k}$ (האמיטר מוארק דרך הקבל).
- $R_{in}=100\text{k}\parallel3.1\text{k}=3.01\text{ k}\Omega$.
$$\frac{v_o}{v_b}=-g_m(10\text{k}\parallel10\text{k})=-32.2\text{m}\cdot5\text{k}=-161$$
$$\frac{v_o}{v_i}=-161\cdot\frac{3.01}{3.01+10}$$
✅ $A_v=\frac{v_o}{v_i}\approx-37$ (מהבסיס: $-161$)

💡 **הרעיון:** "המפתיעה" – נגד הבסיס הגדול מוריד $0.84\text{ V}$, והנגד $10\text{k}$ של המקור מול $R_{in}=3\text{k}$ מוריד את ההגבר פי 4."""


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "lin_todo.json").read_text(encoding="utf-8"))}
    out = [{"id": xs[k]["id"], "title": xs[k]["title"], "question_md": Q[k], "solution_md": S[k] + DONE, "uncertain": False}
           for k in S]
    (HERE.parent / "fix_2811_lin_hw4.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
