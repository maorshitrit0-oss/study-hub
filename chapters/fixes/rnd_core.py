"""Random signals and noise (retake, exam 22/12/2026): 6 Thursday sets built from the recent exams (Bar-Ilan 83-302,
from his Drive): tashpad A/B (with official solutions), tashpah B, tashpav A (student reconstructions). Each exercise
solved from scratch; official-solution mistakes flagged with a warning (09/11/2026)."""
import json

E26 = "מבחן מועד א' תשפ\"ו - שחזור סטודנטים.pdf"
E25B = "מבחן מועד ב' תשפ\"ה.pdf"
E24A = "מבחן מועד א' תשפ\"ד.pdf"
E24B = "מבחן מועד ב' תשפ\"ד - פתרון רשמי.pdf"

S = []


def add(material, title, q, sol, topic, uncertain=False):
    S.append({"add": True, "material": material, "source": "exam", "ord": len(S), "title": title, "question_md": q,
              "solution_md": sol, "topic": topic, "exam_style": True, "uncertain": uncertain})


# ---------------- Thursday 1 (12/11): random vectors, covariance, MMSE ----------------
add(E24A, "תשפ\"ד א' שאלה 1ב - מטריצת הקווריאנס של y=Ax", r"""
יהי $\underline{x}$ וקטור אקראי עם תוחלת $\mu_x$ ומטריצת קווריאנס $\mathbf C_{xx}$, ויהי $\underline y=\mathbf A\underline x$ כאשר $\mathbf A$ מטריצה דטרמיניסטית.
הוכח/י: $\mathbf C_{yy}=\mathbf A\mathbf C_{xx}\mathbf A^\top$.""", r"""
### הגדרה
$$\mathbf C_{yy}=E\{(\underline y-\mu_y)(\underline y-\mu_y)^\top\}$$

### שלב 1: התוחלת של $y$
התוחלת לינארית, ו-$\mathbf A$ קבועה:
$$\mu_y=E\{\mathbf A\underline x\}=\mathbf A\,E\{\underline x\}=\mathbf A\mu_x$$

### שלב 2: הסטייה מהתוחלת
$$\underline y-\mu_y=\mathbf A\underline x-\mathbf A\mu_x=\mathbf A(\underline x-\mu_x)$$

### שלב 3: הצבה
$$\mathbf C_{yy}=E\{\mathbf A(\underline x-\mu_x)\,[\mathbf A(\underline x-\mu_x)]^\top\}=E\{\mathbf A(\underline x-\mu_x)(\underline x-\mu_x)^\top\mathbf A^\top\}$$
(השתמשנו ב-$(\mathbf{AB})^\top=\mathbf B^\top\mathbf A^\top$.)
$\mathbf A$ ו-$\mathbf A^\top$ קבועות ויוצאות מהתוחלת:
$$\mathbf C_{yy}=\mathbf A\,E\{(\underline x-\mu_x)(\underline x-\mu_x)^\top\}\,\mathbf A^\top=\boxed{\mathbf A\mathbf C_{xx}\mathbf A^\top}\ \blacksquare$$

💡 **הרעיון:** "תוחלת של מטריצה לינארית במשתנה" = מוציאים את הקבועות משמאל ומימין. השאלה הזו הופיעה גם בתשפ"ד א' וגם בתשפ"ד ב' – 20 נקודות על שלוש שורות.
""", "וקטורים אקראיים")

add(E24A, "תשפ\"ד א' שאלה 1ג - מטריצת הקורלציה אי-שלילית", r"""
הוכח/י כי $\mathbf R_{xx}=E\{\underline x\,\underline x^\top\}$ הינה מטריצה אי-שלילית מוגדרת.""", r"""
### מה צריך להראות
מטריצה $\mathbf R$ היא אי-שלילית מוגדרת אם **לכל** וקטור דטרמיניסטי $\underline a$:
$$\underline a^\top\mathbf R\,\underline a\ \ge 0$$

### ההוכחה
ניקח $\underline a$ כלשהו:
$$\underline a^\top\mathbf R_{xx}\underline a=\underline a^\top E\{\underline x\underline x^\top\}\underline a=E\{\underline a^\top\underline x\,\underline x^\top\underline a\}$$
($\underline a$ קבוע, נכנס לתוך התוחלת.)
נגדיר את המשתנה האקראי **הסקלרי** $z=\underline a^\top\underline x$. אז $\underline x^\top\underline a=z$ (סקלר שווה לשחלוף שלו), ולכן:
$$\underline a^\top\mathbf R_{xx}\underline a=E\{z\cdot z\}=E\{z^2\}\ \ge0$$
כי תוחלת של ריבוע של מ"מ ממשי אינה שלילית. $\blacksquare$

(בנוסף $\mathbf R_{xx}$ סימטרית: $\mathbf R_{xx}^\top=E\{(\underline x\underline x^\top)^\top\}=E\{\underline x\underline x^\top\}=\mathbf R_{xx}$.)

💡 **הרעיון:** הטריק הקבוע – "סוגרים" את המטריצה עם $\underline a$ ומקבלים $E\{z^2\}$. אותו טריק מוכיח שגם $\mathbf C_{xx}$ ושגם $S_X(f)\ge0$.
""", "וקטורים אקראיים")

add(E24B, "תשפ\"ד ב' שאלה 4 - נקודה אחידה בעיגול היחידה", r"""
יהיו $(x_0,y_0)$ הקואורדינטות של נקודה אקראית המתפלגת **אחיד** בעיגול היחידה ($x^2+y^2\le1$).
חשב/י את המשערך האופטימלי (במובן מינימום שגיאה ריבועית ממוצעת) של $x_0$ מתוך המדידה $y=y_0$.""", r"""
### הכלי
המשערך האופטימלי במובן MMSE הוא **התוחלת המותנית**: $\hat x(y)=E[X\mid Y=y]$.

### שלב 1: הצפיפות המשותפת
שטח העיגול $\pi$, ולכן $f_{XY}(x,y)=\frac1\pi$ בתוך העיגול ו-0 מחוצה לו.

### שלב 2: הצפיפות השולית של $Y$ (עבור $|y|\le1$)
עבור $y$ נתון, $x$ נע בין $-\sqrt{1-y^2}$ ל-$\sqrt{1-y^2}$:
$$f_Y(y)=\int_{-\sqrt{1-y^2}}^{\sqrt{1-y^2}}\frac1\pi\,dx=\frac{2\sqrt{1-y^2}}{\pi}$$

### שלב 3: הצפיפות המותנית
$$f_{X|Y}(x\mid y)=\frac{f_{XY}}{f_Y}=\frac{1/\pi}{2\sqrt{1-y^2}/\pi}=\frac{1}{2\sqrt{1-y^2}},\qquad |x|\le\sqrt{1-y^2}$$
כלומר בהינתן $y$, $X$ **אחיד** על הקטע $[-\sqrt{1-y^2},\sqrt{1-y^2}]$.

> ⚠️ בפתרון הרשמי כתוב $\frac{2}{\sqrt{1-y^2}}$ – זו טעות: צפיפות כזו לא מסתכמת ל-1. הנכון הוא $\frac{1}{2\sqrt{1-y^2}}$ (התשובה הסופית לא משתנה).

### שלב 4: התוחלת המותנית
התפלגות אחידה על קטע סימטרי סביב 0:
$$\hat x(y)=E[X\mid Y=y]=\boxed{0}$$

### השגיאה (להשלמה)
$E[(X-0)^2\mid y]=\frac{(2\sqrt{1-y^2})^2}{12}=\frac{1-y^2}{3}$. כלומר המדידה לא עוזרת לנחש את **הערך**, אבל כן מקטינה את אי-הוודאות.

💡 **הרעיון:** $X$ ו-$Y$ **חסרי קורלציה אבל תלויים** (התחום של $x$ תלוי ב-$y$). MMSE = תוחלת מותנית; כשהמותנה סימטרי סביב 0 – המשערך 0.
""", "שערוך MMSE")

add(E24A, "תשפ\"ד א' שאלה 3 - שערוך הסתברות ברנולי עם פילוג Beta", r"""
$Y=\sum_{i=1}^N X_i$, כאשר $X_i$ ברנולי בת"ס עם הסתברות $q$. הפרמטר $q$ הוא הגרלה של $Q$ בעל צפיפות
$f_Q(q)=\frac{(1-q)^{\beta-1}q^{\alpha-1}}{B(\alpha,\beta)}$, $0\le q\le1$.
א. הראה/י ש-$p_{Y|Q}(y|q)=\binom Ny(1-q)^{N-y}q^y$.
ב. הראה/י ש-$p_Y(y)=\binom Ny\frac{B(y+\alpha,N-y+\beta)}{B(\alpha,\beta)}$.
ג. הראה/י ש-$f_{Q|Y}(q|y)=\frac{(1-q)^{N-y+\beta-1}q^{y+\alpha-1}}{B(y+\alpha,N-y+\beta)}$.
ד. חשב/י את המשערך האופטימלי (MMSE) של $Q$.
נוסחאות: $B(\alpha,\beta)=\int_0^1(1-q)^{\beta-1}q^{\alpha-1}dq$, $\ \frac{B(s+1,\ell)}{B(s,\ell)}=\frac{s}{s+\ell}$.""", r"""
### א. בהינתן $Q=q$
הניסויים בת"ס עם הסתברות הצלחה $q$, ולכן סכומם בינומי:
$$p_{Y|Q}(y|q)=\binom Ny q^y(1-q)^{N-y},\quad y=0,\dots,N$$

### ב. הפילוג השולי (נוסחת ההסתברות השלמה)
$$p_Y(y)=\int_0^1p_{Y|Q}(y|q)f_Q(q)\,dq=\frac{\binom Ny}{B(\alpha,\beta)}\int_0^1(1-q)^{N-y+\beta-1}q^{y+\alpha-1}dq=\binom Ny\frac{B(y+\alpha,\,N-y+\beta)}{B(\alpha,\beta)}$$
(האינטגרל הוא בדיוק הגדרת $B$ עם $\alpha\to y+\alpha$, $\beta\to N-y+\beta$.)

### ג. הפילוג האחורי (בייס)
$$f_{Q|Y}(q|y)=\frac{p_{Y|Q}(y|q)f_Q(q)}{p_Y(y)}=\frac{(1-q)^{N-y+\beta-1}q^{y+\alpha-1}}{B(y+\alpha,N-y+\beta)}$$
(ה-$\binom Ny$ וה-$B(\alpha,\beta)$ מצטמצמים.) זה שוב פילוג Beta – עם $\alpha'=\alpha+y$, $\beta'=\beta+N-y$.

### ד. המשערך האופטימלי
$$\hat Q_{mmse}(y)=E[Q|Y=y]=\int_0^1q\,f_{Q|Y}(q|y)dq=\frac{\int_0^1(1-q)^{N-y+\beta-1}q^{(y+\alpha+1)-1}dq}{B(y+\alpha,N-y+\beta)}=\frac{B(y+\alpha+1,\,N-y+\beta)}{B(y+\alpha,\,N-y+\beta)}$$
לפי יחס ה-Beta עם $s=y+\alpha$, $\ell=N-y+\beta$:
$$\hat Q_{mmse}=\frac{s}{s+\ell}=\boxed{\frac{\alpha+y}{\alpha+\beta+N}}$$

> ⚠️ בפתרון הרשמי התשובה הסופית היא $\frac{\alpha+y+1}{\alpha+N+\beta}$ – **טעות**: לפי הנוסחה הנתונה, $s$ הוא $\alpha+y$ (לא $\alpha+y+1$).

**בדיקת שכל:** בלי מדידות ($N=0$, $y=0$) מקבלים $\frac{\alpha}{\alpha+\beta}$ = התוחלת של Beta ✔. עם הרבה מדידות ($N\to\infty$) מקבלים $\approx\frac yN$ = שכיחות ההצלחות ✔.

💡 **הרעיון:** שערוך בייסיאני: בייס ← פילוג אחורי ← תוחלתו. "מזהים" את האינטגרל כפונקציה ידועה (כאן Beta) במקום לחשב.
""", "שערוך MMSE")

# ---------------- Thursday 2 (19/11): processes, WSS, autocorrelation ----------------
add(E24B, "תשפ\"ד ב' שאלה 1ב - קוסינוס עם פאזה אקראית הוא WSS", r"""
$X(t)=A\cos(\Omega_0t-\Theta)$, כאשר $\Theta\sim U[0,2\pi]$, $A$ מ"מ בעל מומנט שני סופי ובת"ס ב-$\Theta$, ו-$\Omega_0$ קבוע.
הוכח/י ש-$X(t)$ סטציונרי במובן הרחב.""", r"""
### מה צריך: (1) תוחלת קבועה, (2) אוטוקורלציה שתלויה רק ב-$\tau$, (3) הספק סופי.

### (1) התוחלת
$A$ ו-$\Theta$ בת"ס:
$$E\{X(t)\}=E\{A\}\cdot E\{\cos(\Omega_0t-\Theta)\}=E\{A\}\cdot\frac1{2\pi}\int_0^{2\pi}\cos(\Omega_0t-\theta)d\theta=E\{A\}\cdot0=0$$
(אינטגרל של קוסינוס על מחזור שלם.)

### (2) האוטוקורלציה
$$R_X(t,t+\tau)=E\{A^2\}\,E\{\cos(\Omega_0t-\Theta)\cos(\Omega_0(t+\tau)-\Theta)\}$$
עם $\cos a\cos b=\frac12[\cos(b-a)+\cos(a+b)]$:
$$=\frac{E\{A^2\}}2\Big[\cos(\Omega_0\tau)+\underbrace{E\{\cos(\Omega_0(2t+\tau)-2\Theta)\}}_{=0\ \text{(שני מחזורים שלמים)}}\Big]=\boxed{\frac{E\{A^2\}}2\cos(\Omega_0\tau)}$$
תלוי רק ב-$\tau$ ✔.

### (3) הספק סופי
$R_X(0)=\frac{E\{A^2\}}2<\infty$ כי המומנט השני של $A$ סופי ✔.

ולכן $X(t)$ סטציונרי במובן הרחב. $\blacksquare$

💡 **הרעיון:** הפאזה האחידה "מוחקת" כל איבר עם $t$ (תדר כפול). זה הבסיס לכל שאלת אפנון במבחן (תשפ"ו שאלה 1, תשפ"ה ב' שאלה 1).
""", "סטציונריות")

add(E24B, "תשפ\"ד ב' שאלה 2 - צפיפות הספק של קוסינוס עם תדר אקראי", r"""
$X(t)=A\cos(\Omega t-\Theta)$, כאשר $A$ קבוע, $\Omega$ מ"מ בעל צפיפות $f_\Omega(\omega)$, ו-$\Theta\sim U(0,2\pi]$ בת"ס ב-$\Omega$.
הראה/י כי $S_{XX}(\omega)=\frac{\pi A^2}2\big[f_\Omega(\omega)+f_\Omega(-\omega)\big]$.""", r"""
### שלב 1: תוחלת
מתנים על $\Omega=\omega$ ומחשבים את התוחלת על $\Theta$: $E\{\cos(\omega t-\Theta)\}=0$ לכל $\omega$ ⇐ $E\{X(t)\}=0$.

### שלב 2: אוטוקורלציה
$$R_X(t,t+\tau)=A^2E\{\cos(\Omega t-\Theta)\cos(\Omega(t+\tau)-\Theta)\}=\frac{A^2}2E\{\cos(\Omega\tau)\}+\frac{A^2}2\underbrace{E\{\cos(\Omega(2t+\tau)-2\Theta)\}}_{0}$$
$$\Rightarrow\ R_X(\tau)=\frac{A^2}2\int\cos(\tilde\omega\tau)f_\Omega(\tilde\omega)d\tilde\omega$$
תלוי רק ב-$\tau$ ⇐ WSS, ומותר לחשב צפיפות הספק.

### שלב 3: התמרת פורייה
מחליפים סדר בין התוחלת (אינטגרל על $\tilde\omega$) להתמרה, ומשתמשים ב-$\mathcal F\{\cos(\tilde\omega\tau)\}=\pi[\delta(\omega-\tilde\omega)+\delta(\omega+\tilde\omega)]$:
$$S_X(\omega)=\frac{A^2}2\int\pi[\delta(\omega-\tilde\omega)+\delta(\omega+\tilde\omega)]f_\Omega(\tilde\omega)d\tilde\omega=\boxed{\frac{\pi A^2}2[f_\Omega(\omega)+f_\Omega(-\omega)]}\ \blacksquare$$
(הדלתא "שולפת" את $f_\Omega$ בנקודה $\tilde\omega=\omega$ ובנקודה $\tilde\omega=-\omega$.)

**בדיקה:** $\frac1{2\pi}\int S_X d\omega=\frac{A^2}{4}\cdot2=\frac{A^2}2=R_X(0)$ ✔.

💡 **הרעיון:** הצורה של צפיפות ההספק = הפילוג של התדר. התמרה של $E\{\cos\}$ = תוחלת של התמרה (לינאריות).
""", "צפיפות הספק")

add(E26, "תשפ\"ו א' שאלה 1א - אפנון I/Q עם פאזה אקראית", r"""
$X(t)=Y(t)\cos(2\pi f_0t+\varphi)-Z(t)\sin(2\pi f_0t+\varphi)$, כאשר $Y,Z$ סמ"ר במשותף עם תוחלות 0, $\varphi\sim U[0,2\pi]$ בת"ס בהם,
ונתון כי צפיפות ההספק המשותפת $S_{YZ}(f)$ ממשית וזוגית.
מצא/י את $R_X(\tau)$. האם $X(t)$ סמ"ר?
(נוסח לפי שחזור הסטודנטים של מועד א' תשפ"ו.)""", r"""
### סימונים
$\theta_t=2\pi f_0t+\varphi$, $\omega_0=2\pi f_0$, ו-$R_{YZ}(\tau)=E\{Y(t)Z(t+\tau)\}$.

### שלב 1: תוחלת
$E\{X\}=E\{Y\}E\{\cos\theta_t\}-E\{Z\}E\{\sin\theta_t\}=0$.

### שלב 2: ארבעת האיברים
$$R_X(t,t+\tau)=R_Y(\tau)E\{\cos\theta_t\cos\theta_{t+\tau}\}+R_Z(\tau)E\{\sin\theta_t\sin\theta_{t+\tau}\}$$
$$\qquad-R_{YZ}(\tau)E\{\cos\theta_t\sin\theta_{t+\tau}\}-R_{ZY}(\tau)E\{\sin\theta_t\cos\theta_{t+\tau}\}$$
התוחלות על $\varphi$ (האיברים בתדר כפול מתאפסים):
- $E\{\cos\theta_t\cos\theta_{t+\tau}\}=E\{\sin\theta_t\sin\theta_{t+\tau}\}=\frac12\cos\omega_0\tau$
- $E\{\cos\theta_t\sin\theta_{t+\tau}\}=\frac12\sin\omega_0\tau$, $\ E\{\sin\theta_t\cos\theta_{t+\tau}\}=-\frac12\sin\omega_0\tau$

$$\Rightarrow\ R_X(\tau)=\frac12[R_Y(\tau)+R_Z(\tau)]\cos\omega_0\tau-\frac12[R_{YZ}(\tau)-R_{ZY}(\tau)]\sin\omega_0\tau$$

### שלב 3: האיבר המשותף מתאפס
$R_{ZY}(\tau)=R_{YZ}(-\tau)$. $S_{YZ}$ ממשית וזוגית ⇐ $R_{YZ}$ ממשית וזוגית ⇐ $R_{YZ}(\tau)-R_{YZ}(-\tau)=0$:
$$\boxed{R_X(\tau)=\tfrac12[R_Y(\tau)+R_Z(\tau)]\cos(2\pi f_0\tau)}$$

### האם סמ"ר?
תוחלת קבועה (0) ואוטוקורלציה שתלויה רק ב-$\tau$ ⇐ **כן**, $X(t)$ סמ"ר ✔.

💡 **הרעיון:** בשאלות אפנון בונים טבלה של ארבע תוחלות טריגונומטריות. האיבר המשותף נעלם כש-$S_{YZ}$ ממשית וזוגית – לבדוק את זה במפורש, זה מה שנותן את הנקודות.
""", "סטציונריות")

# ---------------- Thursday 3 (26/11): LTI systems and PSD ----------------
add(E24A, "תשפ\"ד א' שאלה 1א - אוטוקורלציה במוצא מערכת LTI", r"""
יהי $x(t)$ תהליך סמ"ר עם אוטוקורלציה $R_{xx}(\tau)$, ותהי $h(t)$ מערכת לינארית יציבה. נסמן $y(t)=x(t)*h(t)$.
הוכח/י: $R_{yy}(\tau)=R_{xx}(\tau)*h(\tau)*h(-\tau)$.""", r"""
### שלב 1: כותבים את הקונבולוציה
$$y(t)=\int h(\alpha)x(t-\alpha)d\alpha,\qquad y(t+\tau)=\int h(\beta)x(t+\tau-\beta)d\beta$$

### שלב 2: האוטוקורלציה (תוחלת נכנסת לאינטגרלים)
$$R_{yy}(t,t+\tau)=\iint h(\alpha)h(\beta)\,E\{x(t-\alpha)x(t+\tau-\beta)\}\,d\alpha\,d\beta=\iint h(\alpha)h(\beta)R_{xx}(\tau-\beta+\alpha)\,d\alpha\,d\beta$$
(הפרש הזמנים: $(t+\tau-\beta)-(t-\alpha)=\tau-\beta+\alpha$.) לא תלוי ב-$t$ ⇐ $y$ סמ"ר.

### שלב 3: מזהים קונבולוציות
נגדיר $g(\tau)=\int h(\beta)R_{xx}(\tau-\beta)d\beta=[R_{xx}*h](\tau)$. אז:
$$R_{yy}(\tau)=\int h(\alpha)\,g(\tau+\alpha)\,d\alpha\ \overset{\alpha=-\gamma}{=}\ \int h(-\gamma)\,g(\tau-\gamma)\,d\gamma=[g*h(-\cdot)](\tau)$$
$$\Rightarrow\ \boxed{R_{yy}(\tau)=R_{xx}(\tau)*h(\tau)*h(-\tau)}\ \blacksquare$$

### בתדר (המסקנה שמשתמשים בה כל הזמן)
$\mathcal F\{h(-\tau)\}=H^*(f)$ ⇐ $S_{yy}(f)=S_{xx}(f)|H(f)|^2$.

💡 **הרעיון:** שתי קונבולוציות בזמן, בתדר מכפלה ב-$|H|^2$. החלפת משתנה $\alpha\to-\gamma$ היא כל הטריק.
""", "מערכות LTI")

add(E26, "תשפ\"ו א' שאלה 1ב - מציאת S_Y מתוך S_X", r"""
בהמשך לשאלה 1א (אפנון I/Q עם פאזה אקראית), נתון:
- $R_Y(\tau)=3R_Z(\tau)$
- $S_{YZ}(f)=B\left(1-\frac{|f|}{f_1}\right)$ עבור $|f|\le f_1$ ואפס אחרת
- $S_X(f)$ הוא שני משולשים בגובה $A$, ממורכזים ב-$\pm f_0$ ורוחב בסיסם $2f_1$ (מ-$f_0-f_1$ עד $f_0+f_1$), כאשר $0\le f_1\le f_0$.

מצא/י את $S_Y(f)$.""", r"""
### שלב 1: מה ידוע מסעיף א
$S_{YZ}$ ממשית וזוגית ⇐ האיבר המשותף נעלם:
$$R_X(\tau)=\tfrac12[R_Y(\tau)+R_Z(\tau)]\cos(2\pi f_0\tau)$$

### שלב 2: הצבת $R_Z=\frac13R_Y$
$$R_X(\tau)=\tfrac12\cdot\tfrac43R_Y(\tau)\cos(2\pi f_0\tau)=\tfrac23R_Y(\tau)\cos(2\pi f_0\tau)$$

### שלב 3: לתדר
כפל ב-$\cos(2\pi f_0\tau)$ = הזזה לשני הצדדים וחצי:
$$S_X(f)=\tfrac23\cdot\tfrac12[S_Y(f-f_0)+S_Y(f+f_0)]=\tfrac13[S_Y(f-f_0)+S_Y(f+f_0)]$$

### שלב 4: השוואה לשרטוט
כל משולש ב-$S_X$ (גובה $A$, חצי-רוחב $f_1$) הוא $\frac13$ של $S_Y$ מוזז. כיוון ש-$f_1\le f_0$ המשולשים לא חופפים, ולכן:
$$\boxed{S_Y(f)=3A\left(1-\frac{|f|}{f_1}\right),\ |f|\le f_1;\ \ 0\ \text{אחרת}}$$
(וכמובן $S_Z=\frac13S_Y=A(1-|f|/f_1)$.)

### ⚠️ על הנוסח
בשני השחזורים של המבחן היחס בין $Y$ ל-$Z$ כתוב לא ברור ("$3$" או "$\frac13$"). באופן כללי, אם $R_Z=kR_Y$:
$$S_Y(f)=\frac{4A}{1+k}\left(1-\frac{|f|}{f_1}\right)$$
עבור $k=\frac13$ (כלומר $R_Y=3R_Z$) מקבלים $3A$, ועבור $k=3$ מקבלים $A$.

💡 **הרעיון:** אפנון בקוסינוס = הזזת הספקטרום ל-$\pm f_0$ עם פקטור $\frac14$ (לכל $|\cdot|^2$ של חצי). את $S_Y$ "מחזירים" על ידי הזזה חזרה לאפס.
""", "צפיפות הספק", uncertain=True)

add(E26, "תשפ\"ו א' שאלה 1ג - המסנן הלינארי האופטימלי ל-Y בהינתן X", r"""
בהמשך לשאלה 1 (אפנון I/Q עם פאזה אקראית $\varphi\sim U[0,2\pi]$ בת"ס ב-$Y,Z$):
מהו המסנן הלינארי האופטימלי לשערוך $Y(t)$ בהינתן התהליך $X(t)$?""", r"""
### הכלי: מסנן וינר (לא סיבתי)
$$H(f)=\frac{S_{XY}(f)}{S_X(f)},\qquad R_{XY}(\tau)=E\{X(t)Y(t+\tau)\}$$
לפני שמחשבים משהו – בודקים את הקורלציה המשותפת.

### שלב 1: הקורלציה המשותפת
$$R_{XY}(\tau)=E\{[Y(t)\cos\theta_t-Z(t)\sin\theta_t]\,Y(t+\tau)\}=R_Y(\tau)\underbrace{E\{\cos\theta_t\}}_{0}-R_{ZY}(\tau)\underbrace{E\{\sin\theta_t\}}_{0}=0$$
($\varphi$ בת"ס ב-$Y,Z$, והתוחלת של $\cos$ ושל $\sin$ עם פאזה אחידה היא 0.)

### שלב 2: המסנן
$$S_{XY}(f)\equiv0\ \Rightarrow\ \boxed{H(f)=0}$$
המשערך הלינארי האופטימלי הוא $\hat Y(t)=0$ (= התוחלת), והשגיאה הריבועית הממוצעת: $E\{Y^2\}=R_Y(0)=\int S_Y(f)df$.

### למה זה הגיוני
$X$ ו-$Y$ **חסרי קורלציה** (לא בהכרח בלתי תלויים!). מסנן לינארי רואה רק קורלציה, ולכן אין לו מה לעשות. משערך **לא** לינארי (שיודע לשחזר את הפאזה) כן היה יכול לעזור.

💡 **הרעיון:** בשאלת וינר תמיד מתחילים מ-$R_{XY}$. אם הוא 0 – התשובה 0, וזה בדיוק המלכודת של הסעיף (וגם של תשפ"ה ב' שאלה 1א).
""", "מסנן וינר")

# ---------------- Thursday 4 (3/12): Wiener filter and matched filter ----------------
add(E24A, "תשפ\"ד א' שאלה 2א-ב - מסנן וינר עם רעש לבן", r"""
$r(t)=[q*s](t)+[g*n](t)$, ו-$y=h*r$. $s(t)$ אות סטציונרי עם $S_{ss}(f)$; $n(t)$ רעש לבן בעל צפיפות $\frac{N_0}2$ בת"ס ב-$s$.
מעוניינים לשערך $\hat s(t)=y(t)$ כך שהשגיאה $e=E\{(s(t)-\hat s(t))^2\}$ מינימלית.
א. נתון $g(t)=q(t)=\delta(t)$. קבע/י את $h$ (מערכת LTI).
ב. כעת $G(f)=1-|f|$ עבור $|f|\le1$ ו-0 אחרת (ו-$q=\delta$). (1) מה המסנן? (2) באיזה תנאי אפשר לשחזר את $s$ ללא שגיאה?""", r"""
### א. מסנן וינר
$$H(f)=\frac{S_{rs}(f)}{S_{rr}(f)}$$
- $r=s+n$, ו-$s,n$ חסרי קורלציה ⇐ $S_{rs}=S_{ss}$, $\ S_{rr}=S_{ss}+\frac{N_0}2$.
$$\boxed{H(f)=\frac{S_{ss}(f)}{S_{ss}(f)+N_0/2}}$$
איפה שהאות חזק מהרעש $H\approx1$, איפה שהרעש שולט $H\approx0$.

### ב1. רעש צבוע ב-$g$
עכשיו הרעש במדידה הוא $g*n$, עם צפיפות $\frac{N_0}2|G(f)|^2$:
$$\boxed{H(f)=\frac{S_{ss}(f)}{S_{ss}(f)+\frac{N_0}2|G(f)|^2}}$$
($S_{rs}$ לא השתנה – $q=\delta$.)

### ב2. מתי השגיאה אפס
השגיאה של וינר: $e=\int\frac{S_{ss}\cdot\frac{N_0}2|G|^2}{S_{ss}+\frac{N_0}2|G|^2}df$.
האינטגרנד אפס בכל תדר שבו אחד מהשניים אפס. $|G(f)|^2>0$ בדיוק עבור $|f|<1$, ולכן צריך:
$$\boxed{S_{ss}(f)=0\ \text{עבור}\ |f|<1}$$
כלומר האות נמצא רק בתדרים שבהם $g$ חוסם את הרעש – שם $H=1$ ומעביר אותו בלי שגיאה.

> ⚠️ בפתרון הרשמי כתוב "הרעש קיים רק עבור $|f|>1$" – זו החלפה: $G$ מעביר רעש רק ב-$|f|\le1$. התנאי הסופי שם ($S_{ss}=0$ ב-$|f|\le1$) נכון.

💡 **הרעיון:** וינר = "יחס אות לאות+רעש" בכל תדר. שגיאה אפס ⟺ האות והרעש לא חולקים אף תדר.
""", "מסנן וינר")

add(E24A, "תשפ\"ד א' שאלה 2ג-ד - לבחור את g או את q", r"""
אותה מערכת: $r=q*s+g*n$, $\hat s=h*r$, $n$ רעש לבן $\frac{N_0}2$ בת"ס ב-$s$.
ג. $q=\delta$, ו-$g(t)$ **לבחירתך**. קבע/י $g$ ו-$h$ שמביאים את השגיאה למינימום.
ד. $g=\delta$, ו-$q(t)$ **לבחירתך**. קבע/י $q$ ו-$h$.""", r"""
### ג. בוחרים את $g$
$g$ שולטת **רק על הרעש** שמגיע למדידה. נבחר:
$$\boxed{g(t)=0,\qquad h(t)=\delta(t)}$$
אז $r=s$ בדיוק, ו-$\hat s=s$ – שגיאה **אפס**.

### ד. בוחרים את $q$
$q$ שולטת על **האות** לפני שהרעש מתווסף. נבחר הגבר: $q(t)=a\,\delta(t)$. אז $r=as+n$ ומסנן וינר:
$$H(f)=\frac{a\,S_{ss}(f)}{|a|^2S_{ss}(f)+N_0/2}$$
כאשר $|a|^2/\frac{N_0}2\to\infty$:
$$H(f)\to\frac1{a}\ \Rightarrow\ \boxed{q=a\delta(t),\ h=\tfrac1a\delta(t),\ |a|\to\infty}$$
יחס האות לרעש שואף לאינסוף והשגיאה שואפת לאפס.

💡 **הרעיון:** שאלות "לבחירתך" בודקות הבנה, לא חישוב: לחסום את הרעש (ג) או להגביר את האות לפני הרעש (ד). כתבו גם את המשפט שמסביר למה.
""", "מסנן וינר")

add(E24A, "תשפ\"ד א' שאלה 2ה - המסנן המתואם", r"""
$q=g=\delta$, ו-$s(t)$ אות **דטרמיניסטי ידוע** (באנרגיה סופית). $n$ רעש לבן $\frac{N_0}2$.
מצא/י את המסנן $h$ שמביא למקסימום את
$$SNR(0)=\frac{|[s*h](0)|^2}{E\{([h*n](0))^2\}}$$
וחשב/י את יחס האות לרעש האופטימלי.""", r"""
### שלב 1: המונה והמכנה
- מונה: $[s*h](0)=\int s(\tau)h(-\tau)d\tau$.
- מכנה: רעש לבן דרך $h$: $E\{([h*n](0))^2\}=\frac{N_0}2\int|h(t)|^2dt$.

### שלב 2: קושי-שוורץ
$$\left|\int s(\tau)h(-\tau)d\tau\right|^2\le\int|s|^2\cdot\int|h|^2$$
ולכן
$$SNR(0)\le\frac{\int|s|^2\int|h|^2}{\frac{N_0}2\int|h|^2}=\frac{\int|s(t)|^2dt}{N_0/2}$$
שוויון מתקבל כש-$h(-\tau)\propto s(\tau)$:
$$\boxed{h_{opt}(t)=A\cdot s(-t)}\qquad(\text{כללי: }h=A\,s(t_0-t)\text{ עבור זמן }t_0)$$

### שלב 3: יחס האות לרעש האופטימלי
$$\boxed{SNR_{max}(0)=\frac{\int|s(t)|^2dt}{N_0/2}=\frac{2E_s}{N_0}}$$
(הקבוע $A$ מצטמצם – הגבר לא משנה יחס.)

💡 **הרעיון:** מסנן מתואם = "האות הפוך בזמן". ה-SNR המקסימלי תלוי **רק באנרגיית האות**, לא בצורתו. וינר (אות אקראי, ממזער שגיאה) ≠ מתואם (אות ידוע, ממקסם SNR ברגע אחד) – אל תבלבלו.
""", "מסנן מתואם")

# ---------------- Thursday 5 (10/12): Poisson processes ----------------
add(E26, "תשפ\"ו א' שאלה 3א - זמן הקפיצה הראשונה מעריכי", r"""
יהי $N(t)$ תהליך פואסון עם קצב $\lambda_n$, ו-$U_1$ זמן הקפיצה הראשונה שלו.
הוכח/י (הוכחה מלאה): $f_{U_1}(u)=\lambda_ne^{-\lambda_nu}$ עבור $u\ge0$ ו-0 אחרת.""", r"""
### שלב 1: מאורע שקול
"הקפיצה הראשונה אחרי $u$" ⟺ "עד הזמן $u$ לא הייתה אף קפיצה":
$$\{U_1>u\}=\{N(u)=0\}$$

### שלב 2: הסתברות
$N(u)\sim\text{Poisson}(\lambda_nu)$ (ו-$N(0)=0$):
$$P(U_1>u)=P(N(u)=0)=\frac{(\lambda_nu)^0}{0!}e^{-\lambda_nu}=e^{-\lambda_nu},\quad u\ge0$$

### שלב 3: פונקציית הפילוג המצטבר ונגזרת
$$F_{U_1}(u)=1-e^{-\lambda_nu}\ \Rightarrow\ \boxed{f_{U_1}(u)=\frac{d}{du}F_{U_1}=\lambda_ne^{-\lambda_nu},\ u\ge0}$$
ועבור $u<0$: $P(U_1\le u)=0$ ⇐ $f=0$. $\blacksquare$

💡 **הרעיון:** שאלות על זמני קפיצה תמיד הופכים לשאלות על **ספירה**: $\{U_k>u\}=\{N(u)<k\}$. ככה מוכיחים גם שזמן הקפיצה ה-$k$ הוא Gamma.
""", "תהליך פואסון")

add(E26, "תשפ\"ו א' שאלה 3ב - מי קופץ ראשון", r"""
$N(t)$ ו-$M(t)$ תהליכי פואסון **בלתי תלויים** עם קצבים $\lambda_n,\lambda_m$. $U_1,V_1$ זמני הקפיצה הראשונה שלהם.
חשב/י $P(U_1>V_1)$, ומצא/י עבור אילו ערכי $\lambda_n,\lambda_m$ ההסתברות שווה $\frac12$.""", r"""
### שלב 1: מה ידוע
מסעיף א: $U_1\sim\text{Exp}(\lambda_n)$, $V_1\sim\text{Exp}(\lambda_m)$, והם בת"ס (התהליכים בת"ס).

### שלב 2: התניה על $V_1$
$$P(U_1>V_1)=\int_0^\infty P(U_1>v)\,f_{V_1}(v)\,dv=\int_0^\infty e^{-\lambda_nv}\cdot\lambda_me^{-\lambda_mv}dv$$
$$=\lambda_m\int_0^\infty e^{-(\lambda_n+\lambda_m)v}dv=\boxed{\frac{\lambda_m}{\lambda_n+\lambda_m}}$$

### שלב 3: מתי שווה חצי
$$\frac{\lambda_m}{\lambda_n+\lambda_m}=\frac12\iff2\lambda_m=\lambda_n+\lambda_m\iff\boxed{\lambda_n=\lambda_m}$$
(הגיוני: אותו קצב ⇐ סימטריה.)

### מסקנה שימושית
התהליך $N(t)+M(t)$ הוא פואסון עם קצב $\lambda_n+\lambda_m$, וכל קפיצה שלו "שייכת" ל-$M$ בהסתברות $\frac{\lambda_m}{\lambda_n+\lambda_m}$, בלי תלות בשאר.

💡 **הרעיון:** $P(\text{מעריכי א}>\text{מעריכי ב})=\frac{\lambda_\text{ב}}{\lambda_\text{א}+\lambda_\text{ב}}$ – מי שהקצב שלו גבוה יותר "מנצח" בהסתברות גבוהה יותר.
""", "תהליך פואסון")

add(E26, "בסגנון תשפ\"ו א' שאלה 3ה - שערוך בתהליך פואסון", r"""
$N(t)$ תהליך פואסון עם קצב $\lambda$, ו-$0<t<s$.
א. מצא/י את המשערך האופטימלי (MMSE) של $N(t)$ בהינתן $N(s)$, ואת השגיאה הריבועית הממוצעת.
ב. מצא/י את המשערך האופטימלי של $N(s)$ בהינתן $N(t)$, ואת השגיאה.
(סעיף ה בשחזורי תשפ"ו שואל שערוך של תהליך שבנוי מפואסונים בהינתן ערך מאוחר יותר; הנוסח המדויק בשחזורים לא ברור – זה התרגיל שמלמד בדיוק את הכלים.)""", r"""
### א. העבר בהינתן העתיד: $E[N(t)\mid N(s)=k]$
בהינתן ש-$k$ קפיצות קרו ב-$[0,s]$, הזמנים שלהן מפוזרים **אחיד ובלתי תלוי** על $[0,s]$. כל קפיצה נופלת ב-$[0,t]$ בהסתברות $p=\frac ts$:
$$N(t)\mid N(s)=k\ \sim\ \text{Bin}\left(k,\tfrac ts\right)$$
$$\boxed{\hat N(t)=E[N(t)\mid N(s)]=\frac ts\,N(s)}$$
השגיאה = התוחלת של השונות המותנית:
$$E\{(N(t)-\hat N(t))^2\}=E\left\{N(s)\tfrac ts\left(1-\tfrac ts\right)\right\}=\lambda s\cdot\tfrac ts\left(1-\tfrac ts\right)=\boxed{\lambda t\left(1-\tfrac ts\right)}$$

### ב. העתיד בהינתן העבר: $E[N(s)\mid N(t)]$
$N(s)=N(t)+[N(s)-N(t)]$, והתוספת **בלתי תלויה** בעבר (תוספות בת"ס) עם פילוג $\text{Poisson}(\lambda(s-t))$:
$$\boxed{\hat N(s)=N(t)+\lambda(s-t)}$$
השגיאה = שונות התוספת: $\boxed{\lambda(s-t)}$.

### שימו לב
במקרה א' המשערך **כפלי** (בינומי), במקרה ב' **חיבורי** (תוספות בת"ס). בשניהם הוא לינארי – ולכן כאן MMSE = LMMSE.

💡 **הרעיון:** שתי תכונות של פואסון פותרות כמעט כל שאלה: תוספות בלתי תלויות (קדימה בזמן), וזמני קפיצה אחידים בהינתן הספירה (אחורה בזמן).
""", "תהליך פואסון")

# ---------------- Thursday 6 (17/12): Gaussian + full exam questions ----------------
add(E25B, "תשפ\"ה ב' שאלה 1א-ב - מסנן לינארי אופטימלי עם אפנון", r"""
$\{V_t\}$ תהליך גאוסי סטציונרי, תוחלת 0, $S_V(f)=A$ עבור $|f|\le D$ ו-0 אחרת.
א. $\Theta\sim U[0,2\pi]$ בת"ס ב-$V$, $f_1=200D$, ו-$Y_t=V_t\cos(2\pi f_1t+\Theta)$. מצא/י את המסנן הלינארי האופטימלי לשערוך $\{Y_t\}$ בהינתן $\{V_t\}$.
ב. $Z_t=Y_t\cos(2\pi f_1t+\Theta)$. מצא/י את המסנן הלינארי האופטימלי לשערוך $\{V_t\}$ בהינתן $\{Z_t\}$, ואת השגיאה הריבועית הממוצעת.
עזר: $\cos\alpha\cos\beta=\frac12(\cos(\alpha+\beta)+\cos(\alpha-\beta))$.""", r"""
### א. $Y$ מתוך $V$
$$R_{VY}(\tau)=E\{V_tV_{t+\tau}\cos(2\pi f_1(t+\tau)+\Theta)\}=R_V(\tau)\cdot E\{\cos(\cdot+\Theta)\}=0$$
$\Rightarrow\ S_{VY}=0\ \Rightarrow\ \boxed{H(f)=0}$, כלומר $\hat Y_t=0$ (חסרי קורלציה – מסנן לינארי לא יכול לעזור).

### ב. $V$ מתוך $Z$
$Z_t=V_t\cos^2\theta_t=\frac{V_t}2+\frac{V_t}2\cos(2\theta_t)$, כאשר $\theta_t=2\pi f_1t+\Theta$.

**קורלציה משותפת:**
$$R_{ZV}(\tau)=E\{V_tV_{t+\tau}\}E\{\cos^2\theta_t\}=\tfrac12R_V(\tau)\ \Rightarrow\ S_{ZV}(f)=\tfrac12S_V(f)$$

**אוטוקורלציה של $Z$:** $E\{\cos^2\theta_t\cos^2\theta_{t+\tau}\}=\frac14E\{(1+\cos2\theta_t)(1+\cos2\theta_{t+\tau})\}=\frac14+\frac18\cos(4\pi f_1\tau)$:
$$R_Z(\tau)=R_V(\tau)\left[\tfrac14+\tfrac18\cos(4\pi f_1\tau)\right]$$
$$S_Z(f)=\tfrac14S_V(f)+\tfrac1{16}\big[S_V(f-2f_1)+S_V(f+2f_1)\big]$$
החלקים ב-$\pm2f_1=\pm400D$ רחוקים מ-$|f|\le D$ – **לא חופפים**.

**המסנן:**
- עבור $|f|\le D$: $H=\frac{S_{ZV}}{S_Z}=\frac{A/2}{A/4}=2$.
- בכל מקום אחר $S_{ZV}=0$ ⇐ $H=0$.
$$\boxed{H(f)=2\ \text{עבור}\ |f|\le D,\ 0\ \text{אחרת}}$$
מסנן מעביר-נמוכים אידיאלי עם הגבר 2: הוא מעביר את $\frac{V_t}2$ וחוסם את $\frac{V_t}2\cos2\theta_t$ (שיושב סביב $\pm2f_1$), ומכפיל ב-2 ⇐ $\hat V_t=V_t$.

**השגיאה:**
$$e=\int\left(S_V-\frac{|S_{ZV}|^2}{S_Z}\right)df=\int_{-D}^{D}\left(A-\frac{A^2/4}{A/4}\right)df=\boxed{0}$$

💡 **הרעיון:** זה **גילוי קוהרנטי**: כפל שני באותו קוסינוס ⇐ $\cos^2=\frac12+\frac12\cos2\theta$ ⇐ מסנן נמוכים מחזיר את האות. בסעיף א' אותו אות "נעלם" כי אין סנכרון.
""", "מסנן וינר")

add(E25B, "תשפ\"ה ב' שאלה 2 - שערוך עם מעריכי, גאוסי ופואסון", r"""
$Z\sim\text{Exp}(\theta)$: $f_Z(z)=\theta e^{-\theta z}$, $z\ge0$. בהינתן $Z=z$, המשתנים $A,B$ **בת"ס**, ומתקיים
$f_{A|Z}(a|z)=\frac1{\sqrt{2\pi\sigma^2}}e^{-\frac{(a-z)^2}{2\sigma^2}}$ ו-$P(B=k|Z=z)=e^{-z}\frac{z^k}{k!}$, $k=0,1,\dots$
עזר: $\int_0^\infty t^ke^{-\lambda t}dt=\frac{k!}{\lambda^{k+1}}$.
א. המשערך האופטימלי של $A$ בהינתן $Z$. ב. של $A$ בהינתן $(Z,B)$. ג. $E\{A\}$ ו-$E\{A^2\}$. ד. $\mathrm{Cov}(A,Z)$.
ה. המשערך האופטימלי של $Z$ בהינתן $B$. ו. המשערך **הלינארי** האופטימלי של $A$ בהינתן $B$. האם $A,B$ בלתי תלויים?""", r"""
### א. $E[A|Z]$
בהינתן $Z=z$: $A\sim N(z,\sigma^2)$ ⇐ $\boxed{\hat A=Z}$.

### ב. $E[A|Z,B]$
בהינתן $Z$, $A$ ו-$B$ בת"ס ⇐ $B$ לא מוסיף מידע: $\boxed{\hat A=Z}$.

### ג. מומנטים של $A$ (החלקה)
$E\{Z\}=\frac1\theta$, $E\{Z^2\}=\frac2{\theta^2}$ (מעריכי).
$$E\{A\}=E\{E[A|Z]\}=E\{Z\}=\boxed{\tfrac1\theta},\qquad E\{A^2\}=E\{\sigma^2+Z^2\}=\boxed{\sigma^2+\tfrac2{\theta^2}}$$

### ד. $\mathrm{Cov}(A,Z)$
$$E\{AZ\}=E\{Z\,E[A|Z]\}=E\{Z^2\}=\tfrac2{\theta^2}\ \Rightarrow\ \mathrm{Cov}=\tfrac2{\theta^2}-\tfrac1\theta\cdot\tfrac1\theta=\boxed{\tfrac1{\theta^2}}$$

### ה. $E[Z|B=k]$
$$f_{Z|B}(z|k)\propto f_Z(z)P(B=k|z)=\theta e^{-\theta z}e^{-z}\tfrac{z^k}{k!}\propto z^ke^{-(\theta+1)z}$$
נרמול עם נוסחת העזר ($\lambda=\theta+1$):
$$E[Z|B=k]=\frac{\int z^{k+1}e^{-(\theta+1)z}dz}{\int z^ke^{-(\theta+1)z}dz}=\frac{(k+1)!/(\theta+1)^{k+2}}{k!/(\theta+1)^{k+1}}=\boxed{\frac{k+1}{\theta+1}}$$

### ו. LMMSE של $A$ מתוך $B$
$$\hat A=E\{A\}+\frac{\mathrm{Cov}(A,B)}{\mathrm{Var}(B)}(B-E\{B\})$$
- $E\{B\}=E\{Z\}=\frac1\theta$ (תוחלת פואסון = $z$).
- $\mathrm{Var}(B)=E\{\mathrm{Var}(B|Z)\}+\mathrm{Var}(E[B|Z])=E\{Z\}+\mathrm{Var}(Z)=\frac1\theta+\frac1{\theta^2}$.
- $E\{AB\}=E\{E[A|Z]E[B|Z]\}=E\{Z^2\}=\frac2{\theta^2}$ ⇐ $\mathrm{Cov}(A,B)=\frac1{\theta^2}$.

$$\frac{\mathrm{Cov}}{\mathrm{Var}}=\frac{1/\theta^2}{(\theta+1)/\theta^2}=\frac1{\theta+1}\ \Rightarrow\ \hat A=\frac1\theta+\frac{B-\frac1\theta}{\theta+1}=\boxed{\frac{B+1}{\theta+1}}$$
(יוצא בדיוק כמו סעיף ה – כי $E[A|B]=E[Z|B]$ והוא כבר לינארי ב-$B$.)

**תלות:** $\mathrm{Cov}(A,B)=\frac1{\theta^2}\ne0$ ⇐ $A,B$ **תלויים** (קורלציה ≠ 0 גוררת תלות). הם בת"ס רק **בהינתן** $Z$.

💡 **הרעיון:** "החלקה" ($E\{\cdot\}=E\{E[\cdot|Z]\}$) ונוסחת השונות השלמה – שני הכלים שפותרים את כל השאלה. ופוסטריור Gamma מזהים מהצורה $z^ke^{-cz}$.
""", "שערוך MMSE")

add(E26, "תשפ\"ו א' שאלה 2 - תהליכים גאוסיים במשותף", r"""
$A(t),B(t)$ גאוסיים במשותף וסמ"ר במשותף, תוחלות 0. $f_0,\Delta>0$ קבועים, $\omega_0=2\pi f_0$.
$$X(t)=A(t)\cos(\omega_0t)-B(t-\Delta)\sin(\omega_0(t-\Delta))$$
א. האם $X(t)$ גאוסי? הוכח/י או הפרך/י. ב. האם $X(t)$ סמ"ר? ג. מצא/י את המשערך במובן MMSE של $X(t)$ בהינתן $A(t)$.
(לפי שחזורי הסטודנטים; באחד השחזורים הסימן בין האיברים הוא +.)""", r"""
### א. גאוסי – כן
לכל $t_1,\dots,t_n$, כל צירוף לינארי $\sum c_iX(t_i)$ הוא צירוף לינארי של דגימות של $A$ ו-$B$ (המקדמים $\cos,\sin$ דטרמיניסטיים). $A,B$ גאוסיים **במשותף** ⇐ כל צירוף כזה גאוסי ⇐ $X$ תהליך גאוסי. $\blacksquare$

### ב. סמ"ר – באופן כללי לא
התוחלת 0. נסמן $R_{AB}(\tau)=E\{A(t)B(t+\tau)\}$. האיברים העצמיים של האוטוקורלציה:
$$\tfrac12R_A(\tau)[\cos\omega_0\tau+\cos(\omega_0(2t+\tau))]+\tfrac12R_B(\tau)[\cos\omega_0\tau-\cos(\omega_0(2t+\tau)-2\omega_0\Delta)]$$
(ועוד איברים משותפים עם $R_{AB}$.) נשאר איבר שתלוי ב-$t$:
$$\tfrac12R_A(\tau)\cos(\omega_0(2t+\tau))-\tfrac12R_B(\tau)\cos(\omega_0(2t+\tau)-2\omega_0\Delta)$$
אין פאזה אקראית שתמחק אותו ⇐ **באופן כללי $X$ אינו סמ"ר**.
**דוגמה נגדית/מקרה מיוחד:** אם $R_{AB}\equiv0$, $R_A=R_B=R$ ו-$\omega_0\Delta=k\pi$, האיבר מתבטל ומקבלים $R_X(\tau)=R(\tau)\cos\omega_0\tau$ – כן סמ"ר. כלומר התשובה תלויה בנתונים; "הוכח/הפרך" = להראות את האיבר התלוי ב-$t$.

### ג. MMSE של $X(t)$ בהינתן $A(t)$
$X(t)$ ו-$A(t)$ גאוסיים במשותף, תוחלת 0 ⇐ התוחלת המותנית **לינארית**:
$$E[X(t)|A(t)]=A(t)\cos\omega_0t-\sin(\omega_0(t-\Delta))\,E[B(t-\Delta)|A(t)]$$
$$E[B(t-\Delta)|A(t)]=\frac{E\{B(t-\Delta)A(t)\}}{E\{A^2(t)\}}A(t)=\frac{R_{BA}(\Delta)}{R_A(0)}A(t)$$
(עם $R_{BA}(\tau)=E\{B(t)A(t+\tau)\}$.) ולכן:
$$\boxed{\hat X(t)=A(t)\left[\cos\omega_0t-\frac{R_{BA}(\Delta)}{R_A(0)}\sin(\omega_0(t-\Delta))\right]}$$
אם $A,B$ חסרי קורלציה – פשוט $\hat X=A(t)\cos\omega_0t$.

> ⚠️ הנוסח המדויק לא ידוע (שחזור). אם בשאלה המקורית מבקשים לשערך בהינתן **כל** התהליך $\{A(s)\}$ – צריך מסנן וינר במקום מקדם אחד. הרעיון זהה: גאוסי במשותף ⇐ MMSE = לינארי.

💡 **הרעיון:** גאוסי במשותף ⇐ (1) צירופים לינאריים גאוסיים, (2) MMSE = LMMSE. ובלי פאזה אקראית – תמיד לבדוק אם נשאר $t$ באוטוקורלציה.
""", "תהליכים גאוסיים", uncertain=True)

print(json.dumps(S, ensure_ascii=False, indent=1))
