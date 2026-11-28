"""Comm, lesson exercises (28/11/2026): checked by Claude; broken formatting fixed; the two multiple-choice ones made
open (comm exam is open). Writes chapters/fix_2811_comm_lesson.json."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נכתב מחדש; המספרים נבדקו."
S, Q = {}, {}

S["32a312be"] = r"""### 📘 מה צריך לדעת קודם
- אורך גל: $\lambda=\frac{c}{f}$. אנטנה יעילה צריכה אורך של לפחות כרבע אורך גל ($\frac\lambda4$) – לכן משדרים בתדר נשא גבוה ולא את האות עצמו.

### ✍️ הדרך המלאה (כמו במחברת)
**1.** 
$$\lambda=\frac{c}{f}=\frac{3\cdot10^8}{1.5\cdot10^3}=2\cdot10^5\text{ m}=200\text{ km}$$
**2.**
$$\ell_{min}=\frac\lambda4=\frac{200\text{ km}}{4}=50\text{ km}$$
✅ $\lambda=200\text{ km}$, אנטנה של $50\text{ km}$ – לא מעשי, ולכן מאפננים על נשא בתדר גבוה.

💡 **הרעיון:** אורך האנטנה פרופורציוני לאורך הגל – תדר נמוך דורש אנטנה ענקית."""

S["e8f7871f"] = r"""### 📘 מה צריך לדעת קודם
- מודל הערוץ: $R(t)\approx\alpha S(t)+N(t)$ – הנחתה (מקדם $\alpha$) ורעש לבן גאוסי מתווסף.

### ✍️ הדרך המלאה (כמו במחברת)
1. מציבים $\alpha=0.2$ ואת האות המשודר:
$$R(t)\approx0.2\cos\left(2\pi\cdot10^6t-\frac\pi2\right)+N(t)$$
2. אפשר לכתוב גם בעזרת $\cos\left(x-\frac\pi2\right)=\sin x$:
$$R(t)\approx0.2\sin\left(2\pi\cdot10^6t\right)+N(t)$$
✅ טון של $1\text{ MHz}$ עם משרעת $0.2$, ועליו רעש.

💡 **הרעיון:** הערוץ מכפיל במקדם הנחתה ומוסיף רעש."""

S["9f837f53"] = r"""### 📘 מה צריך לדעת קודם
- צפיפות הספק הרעש: $N_0=k_BT_e$ (ביחידות W/Hz).

### ✍️ הדרך המלאה (כמו במחברת)
$$N_0=k_BT_e=1.38\cdot10^{-23}\cdot1160=1.6008\cdot10^{-20}\ \frac{\text{W}}{\text{Hz}}$$
✅ $N_0\approx1.6\cdot10^{-20}\ \frac{\text{W}}{\text{Hz}}$ (בדיקה: $1.38\cdot1160=1600.8$).
ב-dBm/Hz: $10\log_{10}\frac{1.6\cdot10^{-20}}{10^{-3}}=-168\ \frac{\text{dBm}}{\text{Hz}}$ (לעומת $-174$ ב-$290\text{ K}$: הטמפרטורה גבוהה פי 4 ⇐ $+6\text{ dB}$).

💡 **הרעיון:** הספק הרעש ליחידת רוחב סרט פרופורציוני לטמפרטורה."""
Q["9f837f53"] = r"נתונה מערכת תקשורת שבה הטמפרטורה האפקטיבית היא $T_e=1160\text{ K}$, וקבוע בולצמן הוא $k_B\approx1.38\cdot10^{-23}\ \frac{\text{J}}{\text{K}}$. חשבו את צפיפות הספק הרעש $N_0$ במערכת."

S["b514bb62"] = r"""### 📘 מה צריך לדעת קודם
- משפט וינר-חינצ'ין: צפיפות ההספק הספקטרלית היא התמרת פורייה של האוטוקורלציה: $S_n(f)=\mathcal F\{R_n(\tau)\}$.
- $\mathcal F\{\delta(\tau)\}=1$.

### ✍️ הדרך המלאה (כמו במחברת)
$$S_n(f)=\int_{-\infty}^{\infty}\frac{N_0}{2}\delta(\tau)e^{-j2\pi f\tau}d\tau=\frac{N_0}{2}$$
$$S_n(f)=\frac{4\cdot10^{-20}}{2}=2\cdot10^{-20}\ \frac{\text{W}}{\text{Hz}}$$
✅ קבוע לכל $f$ (דו-צדדי) – זו המשמעות של "לבן".

💡 **הרעיון:** אוטוקורלציה דלתא ⇐ ספקטרום שטוח; גובהו $\frac{N_0}{2}$."""
Q["b514bb62"] = r"תהליך אקראי של רעש לבן מאופיין בפונקציית אוטוקורלציה $R_n(\tau)=\frac{N_0}{2}\delta(\tau)$, כאשר $N_0=4\cdot10^{-20}\ \frac{\text{W}}{\text{Hz}}$. השתמשו במשפט וינר-חינצ'ין כדי למצוא את צפיפות ההספק הספקטרלית $S_n(f)$ של הרעש."

Q["93c294b4"] = (r"נתון משדר בעל הספק שידור $P_t=100\text{ mW}$, שבח אנטנת שידור $G_t=2\text{ dB}$, שבח אנטנת קליטה $G_r=2\text{ dB}$, "
                 r"ורגישות קליטה נדרשת (הספק נקלט מינימלי) $P_r=-80\text{ dBm}$. חשבו את ההפסד המרבי המותר בחלל החופשי ($FSPL$) ביחידות $\text{dB}$.")
Q["c4d02b4e"] = (r"נתון מעגל RL המשמש כמסנן מעביר נמוכים, עם השראות סליל $L=10\text{ mH}$ והתנגדות נגד $R=100\ \Omega$. חשבו:" "\n"
                 r"1. את קבוע הזמן $\tau$ של המעגל." "\n" r"2. את תדר מחצית ההספק ($-3\text{ dB}$) $f_c$." "\n" r"3. את ההגבר והפאזה בתדר זה.")


def main():
    xs = [x for x in json.loads((SP / "comm_todo.json").read_text(encoding="utf-8")) if not x["material"]]
    out = []
    for x in xs:
        k = x["id"][:8]
        fx = {"id": x["id"], "title": x["title"], "uncertain": False}
        fx["solution_md"] = (S[k] + DONE) if k in S else (x["solution_md"].rstrip() + OK)
        if k in Q:
            fx["question_md"] = Q[k]
        out.append(fx)
    (HERE.parent / "fix_2811_comm_lesson.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
