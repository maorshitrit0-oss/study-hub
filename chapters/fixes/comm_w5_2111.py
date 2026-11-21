"""Comm lecture 5 part A (processed 21/11/2026): its DSB-SC exercise, rewritten as an exam-like open question (his
exam: open, parts) with the full method in words first. -> chapters/comm-w5-2111.json (publish inspect=exercises)."""
import json
import math
from pathlib import Path

assert 2 * 4 == 8 and 100 - 4 == 96 and 100 + 4 == 104 and 10 / 2 == 5
assert abs(0.5 * math.cos(math.radians(60)) - 0.25) < 1e-12

Q = {"id": "63280649-5457-4e0a-9326-b040fed23437", "lock": True, "exam_style": True,
     "question_md": r"""אות מידע $x(t)$:
- רוחב סרט $B=4\,kHz$
- הספק $P_x=10\,W$

מאפננים אותו ב-DSB-SC עם גל נושא $\cos(2\pi f_ct)$, $\;f_c=100\,kHz$: $\;y(t)=x(t)\cos(2\pi f_ct)$.

**א.** מה רוחב הסרט של האות המאופנן?

**ב.** באיזה תחום תדרים (חיובי) יושב הספקטרום שלו?

**ג.** מה הספק האות המאופנן?

**ד.** במקלט סינכרוני כופלים שוב ב-$\cos(2\pi f_ct)$ ומעבירים במסנן מעביר נמוכים. מה יוצא?

**ה.** אם לגל הנושא במקלט יש שגיאת פאזה $\theta$, מה יוצא? מה קורה כש-$\theta=90^\circ$?""",
     "solution_md": r"""### 📘 מה צריך לדעת קודם (הרצאה 5, חלק א)
- **DSB-SC** = כופלים את המידע בגל נושא, בלי לשדר את הגל הנושא עצמו.
- **כפל בקוסינוס מזיז את הספקטרום** ל-$\pm f_c$: כל תדר $f$ של המידע מופיע ב-$f_c+f$ וב-$f_c-f$ ⇐ שני "צדדים".
- **ממוצע של $\cos^2$ הוא חצי** – לכן כפל בקוסינוס מוריד את ההספק לחצי.
- זהות: $\cos^2\alpha=\tfrac12+\tfrac12\cos2\alpha$.

### ✍️ א. רוחב סרט
המידע תופס $0$ עד $B$. אחרי ההזזה הוא תופס $f_c-B$ עד $f_c+B$ – שני צדדים:

$$BW_{DSB}=2B=2\cdot4\,kHz=8\,kHz$$

### ✍️ ב. תחום התדרים
$$f_c-B=100-4=96\,kHz\quad\text{עד}\quad f_c+B=100+4=104\,kHz$$

### ✍️ ג. הספק
$$P_y=\overline{x^2(t)\cos^2(2\pi f_ct)}=P_x\cdot\overline{\cos^2}=P_x\cdot\tfrac12=\frac{10}{2}=5\,W$$

### ✍️ ד. מקלט סינכרוני
כופלים שוב בקוסינוס ומשתמשים בזהות:

$$y(t)\cos(2\pi f_ct)=x(t)\cos^2(2\pi f_ct)=\tfrac12x(t)+\tfrac12x(t)\cos(2\pi\cdot2f_ct)$$

האיבר השני יושב סביב $2f_c=200\,kHz$ ⇐ המסנן מעביר הנמוכים זורק אותו ⇐ **יוצא $\tfrac12x(t)$** – המידע, בחצי משרעת.

### ✍️ ה. שגיאת פאזה
עם $\cos(2\pi f_ct+\theta)$ במקלט, הזהות $\cos a\cos b=\tfrac12[\cos(a-b)+\cos(a+b)]$ נותנת אחרי המסנן:

$$\tfrac12x(t)\cos\theta$$

- שגיאה קטנה ⇐ האות רק נחלש.
- $\theta=90^\circ$ ⇐ $\cos90^\circ=0$ ⇐ **לא יוצא כלום**. לכן במקלט סינכרוני הפאזה חייבת להיות מתואמת.

💡 **הרעיון:** DSB-SC מכפיל את רוחב הסרט, מוריד את ההספק לחצי, ודורש במקלט גל נושא באותו תדר ובאותה פאזה."""}

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "comm-w5-2111.json"
    out.write_text(json.dumps([Q], ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
