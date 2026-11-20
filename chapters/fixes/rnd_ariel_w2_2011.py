"""Random signals, session 2 (WSS) - exercises at HER level (his remark 20/11/2026: "the first exercise is my exam, the
other two are not at her level"; random phase - not in any of her 4 Ariel exams: 12/07 sem. B moed A, 29/07 moed B,
08/10 summer moed A, 26/10 his exam). The Bar-Ilan random-phase questions (7888a5c6, 80bc90e2) leave the week;
her two process questions come in, word for word from her forms + her official solutions, laid out like the exam
(one given per line) and explained in words first.
  python rnd_ariel_w2_2011.py -> chapters/rnd-ariel-w2-2011.json (publish inspect=exercises: added to session 2 + week 2)"""
import json
from pathlib import Path

SRC = "\n\n> 📝 מתוך מבחן של המרצה שלך באריאל ({}), עם הפתרון הרשמי שלה."

Q_AB = {
    "add": True, "kind": "other", "number": 2, "week": 2, "lock": True, "exam_style": True, "source": "exam",
    "title": "מבחן אריאל (קיץ תשפ\"ו מועד א׳) שאלה 2 – A cos + B sin: סמ\"ר? סמ\"ר במשותף?",
    "question_md": r"""**שאלה 2 (30%)**

נתון תהליך אקראי בזמן בדיד:

$$X[n]=A\cos(\omega_0n)+B\sin(\omega_0n)$$

כאשר:
- $A,B$ משתנים אקראיים **בלתי תלויים**
- $E[A]=E[B]=0$
- $E[A^2]=E[B^2]=\sigma^2$

**א.** מצאו את $E[X[n]]$ ואת $R_X[n_1,n_2]$. האם התהליך WSS? האם הוא SSS?

**ב.** מגדירים $Z[n]=X[n]+C$, כאשר $C$ קבוע (לא אקראי). עבור אילו ערכים של $C$ התהליך $Z[n]$ הוא WSS?

**ג.** מגדירים $Y[n]=A\cos(\omega_0n)-B\sin(\omega_0n)$. האם $X[n],Y[n]$ סטציונריים במשותף במובן הרחב (JWSS)?

נתון: $\cos(a+b)=\cos a\cos b-\sin a\sin b$, $\quad\cos(a-b)=\cos a\cos b+\sin a\sin b$""" + SRC.format("קיץ תשפ״ו, מועד א׳, 08/10/2026"),
    "solution_md": r"""### 📘 מה צריך לדעת קודם (במילים)

- **WSS (סמ"ר)** = שני תנאים: (1) התוחלת **לא תלויה בזמן**; (2) האוטוקורלציה תלויה **רק בהפרש** $n_1-n_2$, לא בזמנים עצמם.
- **הכלי של השאלה:** $A,B$ בלתי תלויים עם תוחלת 0 ⇐ $E[AB]=E[A]E[B]=0$. זה מה שמעלים את האיברים המעורבים.
- **SSS** דורש שכל הפילוג יהיה זהה בכל זמן – יותר חזק מ-WSS.
- **JWSS** = כל אחד WSS, **וגם** הקרוס-קורלציה $R_{XY}$ תלויה רק בהפרש.

### ✍️ א. תוחלת, אוטוקורלציה, WSS / SSS

**תוחלת** – התוחלת "נכנסת" פנימה, וה-cos/sin הם מספרים (לא אקראיים):

$$E[X[n]]=E[A]\cos(\omega_0n)+E[B]\sin(\omega_0n)=0+0=0$$

**אוטוקורלציה** – פותחים סוגריים:

$$R_X[n_1,n_2]=E\big[(A\cos\omega_0n_1+B\sin\omega_0n_1)(A\cos\omega_0n_2+B\sin\omega_0n_2)\big]$$

$$=E[A^2]\cos\omega_0n_1\cos\omega_0n_2+E[B^2]\sin\omega_0n_1\sin\omega_0n_2+E[AB]\,(\dots)$$

$E[AB]=0$, ו-$E[A^2]=E[B^2]=\sigma^2$:

$$R_X=\sigma^2\big(\cos\omega_0n_1\cos\omega_0n_2+\sin\omega_0n_1\sin\omega_0n_2\big)=\sigma^2\cos\big(\omega_0(n_1-n_2)\big)$$

(השתמשנו בזהות $\cos(a-b)$ הנתונה.)

**WSS?** התוחלת קבועה (0) ו-$R_X$ תלוי רק ב-$n_1-n_2$ ⇐ **כן, WSS**.

**SSS?** לא: המשתנים $A,B$ מוכפלים במקדמים שמשתנים עם $n$, ולכן הפילוג של $X[n]$ עצמו משתנה מזמן לזמן (בלי הנחה על הפילוג של $A,B$).

### ✍️ ב. $Z[n]=X[n]+C$

$$E[Z[n]]=E[X[n]]+C=C\quad\text{– קבוע}$$

$$R_Z=E[(X[n_1]+C)(X[n_2]+C)]=R_X[n_1,n_2]+C\big(E[X[n_1]]+E[X[n_2]]\big)+C^2=\sigma^2\cos\big(\omega_0(n_1-n_2)\big)+C^2$$

תלוי רק בהפרש ⇐ **WSS לכל ערך של $C$**.

### ✍️ ג. JWSS?

$Y[n]$ בנוי בדיוק כמו $X[n]$ (רק סימן אחר ל-$B$) ⇐ גם הוא WSS. נשאר לבדוק את הקרוס-קורלציה:

$$R_{XY}=E\big[(A\cos\omega_0n_1+B\sin\omega_0n_1)(A\cos\omega_0n_2-B\sin\omega_0n_2)\big]=\sigma^2\big(\cos\omega_0n_1\cos\omega_0n_2-\sin\omega_0n_1\sin\omega_0n_2\big)$$

$$R_{XY}=\sigma^2\cos\big(\omega_0(n_1+n_2)\big)$$

תלוי ב-**סכום** $n_1+n_2$, לא רק בהפרש ⇐ **לא JWSS**.

💡 **הרעיון:** בשאלות "מקדמים אקראיים" הכול נפתח לסוגריים, $E[AB]=0$ מוחק את האיברים המעורבים, ואז מסתכלים: הפרש (✓) או סכום/זמנים עצמם (✗)."""}

Q_IID = {
    "add": True, "kind": "other", "number": 2, "week": 2, "lock": True, "exam_style": True, "source": "exam",
    "title": "מבחן אריאל (סמסטר ב׳ תשפ\"ו מועד א׳) שאלה 2 – תהליך i.i.d והילוך אקראי",
    "question_md": r"""**שאלה 2 (30%)**

נתון תהליך אקראי i.i.d בשם $X[n]$, כך שלכל $n$:
- $P(X[n]=a)=\epsilon$
- $P(X[n]=b)=2\epsilon$
- $P(X[n]=c)=1-3\epsilon$

**א.** מצאו את $E[X[n]]$, את האוטוקורלציה $R_X[n_1,n_2]$ ואת הקווריאנס $K_X[n_1,n_2]$. בטאו באמצעות $a,b,c,\epsilon$.

**ב.** עבור אילו ערכים של $a,b,c,\epsilon$ התהליך WSS? ועבור אילו הוא SSS?

**ג.** מגדירים $Y[n]=\sum_{i=1}^{n}X[i]$. תנו דוגמה לקבועים $a,b,c,\epsilon$ שעבורם $Y[n]$ הוא WSS.""" + SRC.format("סמסטר ב׳ תשפ״ו, מועד א׳, 12/07/2026"),
    "solution_md": r"""### 📘 מה צריך לדעת קודם (במילים)

- **i.i.d** = כל דגימה בלתי תלויה באחרות, וכולן עם **אותו פילוג**.
- **תוחלת של משתנה בדיד** = סכום של (ערך × ההסתברות שלו). **מומנט שני** = סכום של (ערך² × הסתברות).
- **אוטוקורלציה של i.i.d** – שני מקרים:
  - אותו זמן ($n_1=n_2$): $E[X^2]$
  - זמנים שונים: הדגימות בלתי תלויות ⇐ $E[X[n_1]]E[X[n_2]]=(E[X])^2$
- **קווריאנס:** $K=R-E[X[n_1]]E[X[n_2]]$.
- **הילוך אקראי** $Y[n]=\sum X[i]$: התוחלת והשונות **גדלות עם $n$** – בדרך כלל לא WSS.

### ✍️ א. תוחלת, אוטוקורלציה, קווריאנס

**תוחלת:**

$$E[X[n]]=a\cdot\epsilon+b\cdot2\epsilon+c(1-3\epsilon)=c+\epsilon(a+2b-3c)$$

**מומנט שני:**

$$E[X^2[n]]=a^2\epsilon+b^2\cdot2\epsilon+c^2(1-3\epsilon)$$

**אוטוקורלציה:**

$$R_X[n_1,n_2]=\begin{cases}a^2\epsilon+2b^2\epsilon+c^2(1-3\epsilon) & n_1=n_2\\[4pt]\big(a\epsilon+2b\epsilon+c(1-3\epsilon)\big)^2 & n_1\ne n_2\end{cases}$$

**קווריאנס** – מחסירים $(E[X])^2$ משני המקרים:

$$K_X[n_1,n_2]=\begin{cases}\mathrm{Var}(X[n])=E[X^2]-(E[X])^2 & n_1=n_2\\[4pt]0 & n_1\ne n_2\end{cases}$$

### ✍️ ב. WSS / SSS

תהליך i.i.d: הפילוג זהה בכל זמן, והקשר בין זמנים שונים תמיד אותו דבר (בלתי תלויים) ⇐ **SSS, ולכן גם WSS – לכל ערכי הקבועים**.

### ✍️ ג. מתי ההילוך האקראי WSS?

בדרך כלל לא: $E[Y[n]]=n\cdot E[X]$ גדל עם $n$, וגם

$$R_Y[n_1,n_2]=n_1n_2(E[X])^2+\min(n_1,n_2)\,\mathrm{Var}(X)$$

תלוי בזמנים עצמם. כדי שיהיה WSS צריך:
1. $E[X]=0$ – שהתוחלת לא תגדל;
2. $\mathrm{Var}(X)=0$ – שהאיבר עם $\min(n_1,n_2)$ ייעלם.

דוגמה (מהפתרון הרשמי): $\epsilon=0$, $c=0$ (ו-$a,b$ כלשהם). אז $X[n]=0$ תמיד ⇐ $Y[n]=0$ ⇐ WSS.

💡 **הרעיון:** i.i.d ⇐ תמיד סטציונרי. סכום מצטבר (הילוך אקראי) ⇐ בדרך כלל לא, כי התוחלת והשונות מצטברות עם הזמן."""}

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "rnd-ariel-w2-2011.json"
    out.write_text(json.dumps([Q_AB, Q_IID], ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
