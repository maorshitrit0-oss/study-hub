"""Comm assignments (מטלות 1/4/5/8) (28/11/2026) + the 14.2.21 "improved SSB" question settled by assignment 5 Q8
(official answer 37 dB = SNR in the given BW + 3 dB). Writes chapters/fix_2811_comm_assign.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש; המספרים חושבו מחדש."
S = {}

S["c032070b"] = r"""### 📘 מה צריך לדעת קודם
- $T_e=(F-1)T_0$, $T_{sys}=T_{in}+T_e$, $N=kT_{sys}B$.
- "מקלט SSB משופר" (לפי השקפים והתשובה הנתונה): מקבל את כל הספק האות ומסנן רעש רק ברוחב פס צד אחד – מרוויח $3\text{ dB}$ על היחס ברוחב השידור.

### ✍️ הדרך המלאה (כמו במחברת)
1. $F=10^{0.2}=1.585$ ⇐ $T_e=0.585\cdot290=169.7\text{ K}$ ⇐ $T_{sys}=120+169.7=289.7\text{ K}$.
2. רעש ברוחב השידור $100\text{ kHz}$: $N=1.38\cdot10^{-23}\cdot289.7\cdot10^5=4.0\cdot10^{-16}\text{ W}=-124.0\text{ dBm}$ ⇐ $SNR=-90+124.0=34.0\text{ dB}$.
3. שיפור המקלט: $+3\text{ dB}$ (רעש רק ב-$50\text{ kHz}$):
✅ $SNR_{out}\approx37\text{ dB}$ – כמו התשובה הנתונה.

💡 **הרעיון:** קודם טמפרטורת מערכת ורעש, ואז ה-$3\text{ dB}$ של הגלאי המשופר. (כך נפתרת גם שאלה 11 בבחינה 14.2.21: $31.75+3\approx34\text{ dB}$.)"""

S["1d50dda9"] = r"""### 📘 מה צריך לדעת קודם
- נצילות AM: $\eta=\frac{m^2X_{rms}^2}{1+m^2X_{rms}^2}$ (כש-$|x(t)|\le1$).
- $m>1$ ⇐ אפנון-יתר: המעטפה $1+m\,x(t)$ חוצה את האפס.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** ✅ $\eta$ עולה עם $m$: פסי הצד (המידע) גדלים ביחס לנשא, שלא נושא מידע.

**ב.** $X_{rms}^2=0.49$:
- $m=0.5$: $\eta=\frac{0.25\cdot0.49}{1+0.1225}=\frac{0.1225}{1.1225}=0.109$ ✅ $10.9\%$
- $m=1$: $\eta=\frac{0.49}{1.49}=0.329$ ✅ $32.9\%$
- $m=1.2$: $\eta=\frac{0.7056}{1.7056}=0.414$ ✅ $41.4\%$

**ג.** ✅ ב-$m=1.2$ הנצילות "נראית" גבוהה יותר, אבל המעטפה מתהפכת (חוצה 0) ⇐ גלאי מעטפה מחזיר $|1+m\,x(t)|$ – עיוות שלא ניתן לתקן. לכן עובדים עם $m\le1$.

💡 **הרעיון:** יותר $m$ = יותר נצילות, עד $m=1$; אחרי זה – עיוות."""

S["9e0050ab"] = r"""### 📘 מה צריך לדעת קודם
- אפנון זווית: התדר הרגעי $f_i=f_c+\frac{1}{2\pi}\frac{d\phi}{dt}$; לכל טון $\beta_k\sin(2\pi f_kt)$ הסטייה $\beta_kf_k$, ובמקרה הגרוע הן מצטברות.
- קרסון: $BW=2(\Delta f+f_{max})$.

### ✍️ הדרך המלאה (כמו במחברת)
1. $\phi(t)=2\sin(2\pi\cdot10^5t)+4\sin(2\pi\cdot2.5\cdot10^5t)$ (כי $5\pi\cdot10^5=2\pi\cdot2.5\cdot10^5$).
2. $\Delta f=2\cdot100\text{k}+4\cdot250\text{k}=1.2\text{ MHz}$; $f_{max}=250\text{ kHz}$.
3. $BW=2(1.2+0.25)=2.9\text{ MHz}$.
✅ $2.9\text{ MHz}$ – **לא מופיע באפשרויות** ⇐ "פתרון אחר".
> הערה: 880 kHz (ג) היא התשובה של שאלה דומה עם $4\sin(7\pi\cdot10^4t)$ (טון ב-35 kHz) – ייתכן שהנוסח כאן הועתק עם טעות. כפי שהשאלה כתובה, התשובה היא $2.9\text{ MHz}$.

💡 **הרעיון:** סכום הסטיות של כל הטונים + התדר הגבוה ביותר."""

NOTE_ISB = ("\n\n> ⚠️ הערה למטלה: הנוסחה $m_1\\cos\\omega_ct+m_2\\sin\\omega_ct$ היא בעצם **אפנון ניצב (QAM)** – כל אות תופס את **שני** פסי הצד "
            "($m_1$: 9 ו-11 kHz, $m_2$: 8 ו-12 kHz), כפי שחושב כאן; המשפט במטלה ש\"$m_1$ ב-USB ו-$m_2$ ב-LSB\" לא נכון לנוסחה הזו. ISB אמיתי דורש "
            "התמרת הילברט: $[m_1\\cos-\\hat m_1\\sin]+[m_2\\cos+\\hat m_2\\sin]$ ⇐ $m_1$ רק ב-11 kHz ו-$m_2$ רק ב-8 kHz. השחזור בגלאי מכפלה עם $\\cos$ ועם $\\sin$ נכון בשני המקרים.")
NOTE_SSB = ("\n\n> 🔎 הוכרע (28/11): במטלה 5 שאלה 8 (\"מקלט SSB משופר\") התשובה הרשמית 37 dB = היחס ברוחב השידור + 3 dB. "
            "כאן: $SNR=-74+105.75=31.75\\text{ dB}$, ועם המקלט המשופר $\\approx34.75$ ⇐ **ד (34 dB)**.")


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "comm_todo.json").read_text(encoding="utf-8"))}
    # 9e0050ab stays uncertain: the source page is a scan, the options do not fit the stored phase function
    out = [{"id": xs[k]["id"], "title": xs[k]["title"], "solution_md": s + DONE, "uncertain": k == "9e0050ab"} for k, s in S.items()]
    out.append({"id": xs["3b704d5e"]["id"], "title": xs["3b704d5e"]["title"], "solution_md": xs["3b704d5e"]["solution_md"].rstrip() + OK, "uncertain": False})
    out.append({"id": xs["cb2b751e"]["id"], "title": xs["cb2b751e"]["title"], "solution_md": xs["cb2b751e"]["solution_md"].rstrip() + NOTE_ISB + OK, "uncertain": False})
    out.append({"id": xs["3bdb1500"]["id"], "title": xs["3bdb1500"]["title"], "solution_md": xs["3bdb1500"]["solution_md"].replace("\\n", "\n").rstrip() + OK, "uncertain": False})
    for k in ("8cb843f4", "6d54fc6f"):
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + NOTE_SSB + OK, "uncertain": False})
    (HERE.parent / "fix_2811_comm_assign.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
