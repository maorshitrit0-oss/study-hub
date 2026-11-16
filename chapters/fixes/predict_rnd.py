"""🎯 Predicted exam questions - random signals (16/11/2026: his exam's four question types with new data + a catch;
the lecturer adapts Bar-Ilan questions). Numbers checked in python (asserts below).
  python predict_rnd.py -> chapters/predict-rnd.json (publish inspect=exercises)"""
import json
import math
from pathlib import Path

import numpy as np

Q = []


def q(title, question, solution):
    Q.append({"add": True, "free": True, "source": "exam", "title": "🎯 שאלה צפויה: " + title, "question_md": question,
              "solution_md": solution, "exam_style": True, "uncertain": False})


q("תהליך עם מקדמים אקראיים – תוחלת, אוטוקורלציה, וההפרש שלו",
  r"""(כמו שאלה 1 במבחן שלך, נתונים אחרים.) $X[n]=A+B\,n$, כאשר $A$ ו-$B$ בלתי תלויים: $E[A]=1$, $\mathrm{Var}(A)=2$, $E[B]=0$, $\mathrm{Var}(B)=1$.

1. מצא $E[X[n]]$ ו-$R_X[n,m]$. האם $X$ סטציונרי במובן הרחב?
2. $Y[n]=X[n]-X[n-1]$. מצא תוחלת ואוטוקורלציה. האם $Y$ סטציונרי?
3. **הקאץ':** $Z[n]=X[n]+X[n-1]$ – סטציונרי?""",
  r"""### 1. $X$
$$E[X[n]]=E[A]+n\,E[B]=1$$
$$R_X[n,m]=E[(A+Bn)(A+Bm)]=E[A^2]+(n+m)E[A]E[B]+nm\,E[B^2]$$
$E[A^2]=\mathrm{Var}(A)+E[A]^2=3$, $E[B^2]=1$, $E[A]E[B]=0$:
$$R_X[n,m]=3+nm$$ ✅
תלוי ב-$n$ וב-$m$ בנפרד, לא רק בהפרש ⇐ **לא WSS** (למרות שהתוחלת קבועה).

### 2. $Y$
$$Y[n]=(A+Bn)-(A+B(n-1))=B$$
$$E[Y]=0,\qquad R_Y[n,m]=E[B^2]=1$$ ✅ ⇐ **WSS** (תהליך קבוע אקראי – אותו ערך בכל הזמנים).

### 3. הקאץ' – $Z$
$$Z[n]=2A+B(2n-1),\quad E[Z]=2,\quad\mathrm{Var}(Z[n])=4\cdot2+(2n-1)^2\cdot1$$ ✅
השונות גדלה עם $n$ ⇐ **לא WSS**. ההפרש "מבטל" את $A$ ואת התלות ב-$n$; הסכום לא.

💡 **הרעיון:** WSS = תוחלת קבועה **וגם** $R$ תלוי רק ב-$n-m$. בדיקה מהירה: אם השונות תלויה ב-$n$ – לא WSS.""")

q("אות דרך מסנן – צפיפות הספק והספק במוצא",
  r"""(כמו שאלה 2 במבחן שלך.) $X(t)=\cos(2\pi\cdot500t+\Theta)+N(t)$, $\Theta\sim U[0,2\pi)$, $N$ רעש לבן עם $S_N(f)=1$, בלתי תלוי ב-$\Theta$.
$X$ עובר במסנן מעביר פס אידיאלי בהגבר 2 בתחום $400<|f|<600\,Hz$.

1. מצא $S_X(f)$ ו-$S_Y(f)$ ושרטט.
2. מה ההספק במוצא?
3. **הקאץ':** איזה מסנן $H_2$ ייתן במוצא רק את הקוסינוס בלי רעש? ואם הפס הוא $510<|f|<600$?""",
  r"""### 1. צפיפויות
קוסינוס עם פאזה אחידה: $R(\tau)=\tfrac12\cos(2\pi500\tau)$ ⇐ $S(f)=\tfrac14[\delta(f-500)+\delta(f+500)]$. הרעש בלתי תלוי ⇐ מחברים:
$$S_X(f)=\tfrac14[\delta(f-500)+\delta(f+500)]+1$$
$$S_Y(f)=|H|^2S_X=4S_X\ \text{בפס},\ 0\ \text{מחוץ לו}$$ ✅

### 2. הספק
- קוסינוס: $4\cdot\tfrac12=2$
- רעש: $4\cdot1\cdot(\text{רוחב כולל }2\cdot200\,Hz)=1600$
$$P_Y=2+1600=1602$$ ✅

### 3. הקאץ'
אין מסנן ממשי שמשאיר רק את הקוסינוס: הרעש לבן ויש לו הספק **גם** ב-$500\,Hz$. ככל שהפס צר יותר – פחות רעש, אבל לא אפס.
פס $510<|f|<600$: התדר $500$ **בחוץ** ⇐ נשאר רק רעש: $4\cdot1\cdot2\cdot90=720$ ✅

💡 **הרעיון:** $S_Y=|H|^2S_X$; הספק = שטח מתחת ל-$S_Y$ (כולל שני הצדדים של ציר התדר). דלתא של קוסינוס בפס ⇐ תורמת $|H|^2\cdot A^2/2$.""")

assert abs(math.exp(-6) * 6 ** 4 / 24 - 0.1339) < 1e-4
q("תהליך פואסון – ספירה, זמן הגעה ראשון, מי קודם, וחוסר זיכרון",
  r"""(כמו שאלה 3 במבחן שלך.) לקוחות מגיעים כתהליך פואסון בקצב $\lambda=3$ לדקה.

1. מה ההסתברות שבדיוק 4 לקוחות יגיעו בשתי דקות?
2. מה ההסתברות שהלקוח הראשון יגיע אחרי יותר מדקה?
3. תהליך שני, בלתי תלוי, בקצב $2$ לדקה. מה ההסתברות שהלקוח הראשון יהיה מהתהליך הראשון?
4. **הקאץ':** ידוע שבשתי הדקות הראשונות לא הגיע אף אחד (מהתהליך הראשון). מה ההסתברות שמישהו יגיע בדקה השלישית?""",
  r"""### 1. ספירה
$$P(N(2)=4)=e^{-\lambda t}\frac{(\lambda t)^4}{4!}=e^{-6}\frac{6^4}{24}\approx0.134$$ ✅

### 2. זמן הגעה ראשון ($T\sim\mathrm{Exp}(3)$)
$$P(T>1)=e^{-3}\approx0.050$$ ✅

### 3. מי קודם
$$P(T_1<T_2)=\frac{\lambda_1}{\lambda_1+\lambda_2}=\frac35=0.6$$ ✅

### 4. הקאץ' – חוסר זיכרון
העבר לא משנה: $$P(\text{הגעה בדקה הבאה})=1-e^{-3}\approx0.950$$ ✅ – בדיוק כמו בדקה הראשונה.

💡 **הרעיון:** ספירה ⇐ פואסון; זמן ⇐ מעריכי; מי ראשון ⇐ יחס הקצבים; "בהינתן שלא הגיע" ⇐ מתחילים מחדש.""")

C = np.array([[5, 4], [4, 8]])
w = np.linalg.solve(C, np.array([4, 4]))
assert np.allclose(w, [2 / 3, 1 / 6]) and abs(4 - w @ [4, 4] - 2 / 3) < 1e-9
q("משערך לינארי משתי מדידות עם רעשים שונים",
  r"""(כמו שאלה 4 במבחן שלך.) $Y_1=X+N_1$, $Y_2=X+N_2$; כולם בתוחלת 0 ובלתי תלויים: $\mathrm{Var}(X)=4$, $\mathrm{Var}(N_1)=1$, $\mathrm{Var}(N_2)=4$.

1. מצא את המשערך הלינארי האופטימלי $\hat X=aY_1+bY_2$.
2. מה ה-MSE?
3. **הקאץ':** השווה למשערך האינטואיטיבי $\tfrac12(Y_1+Y_2)$ ולמשערך מ-$Y_1$ בלבד.""",
  r"""### 1. משוואות נורמליות
$$C_Y=\begin{pmatrix}5&4\\4&8\end{pmatrix},\qquad C_{XY}=\begin{pmatrix}4\\4\end{pmatrix}$$
$$\begin{pmatrix}a\\b\end{pmatrix}=C_Y^{-1}C_{XY}=\frac1{24}\begin{pmatrix}8&-4\\-4&5\end{pmatrix}\begin{pmatrix}4\\4\end{pmatrix}=\begin{pmatrix}2/3\\1/6\end{pmatrix}$$ ✅
המשקלים ביחס $4:1$ – הפוך ליחס השונויות של הרעשים ($1:4$).

### 2. MSE
$$\mathrm{MSE}=\mathrm{Var}(X)-C_{XY}^TC_Y^{-1}C_{XY}=4-\left(4\cdot\tfrac23+4\cdot\tfrac16\right)=\frac23$$ ✅

### 3. השוואה
- ממוצע: $\hat X-X=\tfrac12(N_1+N_2)$ ⇐ $\mathrm{MSE}=\tfrac14(1+4)=1.25$ ✅ (גרוע יותר – נותן משקל שווה למדידה הרועשת)
- רק $Y_1$: $\hat X=\tfrac45Y_1$, $\mathrm{MSE}=4-\tfrac{16}5=0.8$ ✅
הקאץ': גם מדידה רועשת **עוזרת** ($0.8\to0.67$), אבל רק במשקל הנכון.

💡 **הרעיון:** $\hat X=C_{XY}^TC_Y^{-1}Y$, $\mathrm{MSE}=\mathrm{Var}(X)-C_{XY}^TC_Y^{-1}C_{XY}$. מדידה טובה יותר = משקל גבוה יותר.""")

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "predict-rnd.json"
    out.write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(Q))
