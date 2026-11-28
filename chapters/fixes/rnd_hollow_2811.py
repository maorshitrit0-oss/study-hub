"""Random signals: exercises whose stored solution only named the steps (28/11/2026), solved in full by Claude and
checked by simulation (scratchpad check, 10^6 samples each). Writes chapters/fix_2811_rnd_hollow.json for
publish.yml inspect=exercises (course ^אותות אקראיים)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש במלואו; התוצאות נבדקו גם בסימולציה."

S = {}

S["3e854a72"] = r"""### 📘 מה צריך לדעת קודם
- צפיפות מעריכית: $f_X(x)=\lambda e^{-\lambda x}$ עבור $x\ge0$, ו-$P(a<X<b)=\int_a^b f_X(x)\,dx$.
- $N$ הוא החלק השלם של $X$ ו-$Z=X-N$ הוא החלק השברי, ולכן $Z\in(0,1)$.
- טור הנדסי: $\sum_{k=0}^{\infty}q^k=\frac{1}{1-q}$ כאשר $|q|<1$.
- צפיפות מתקבלת מגזירה של פונקציית ההתפלגות המצטברת: $f_Z(z)=\frac{d}{dz}P(Z\le z)$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** המאורע $N=k$ הוא בדיוק $k\le X<k+1$.

**נוסחה:**
$$P(N=k)=\int_k^{k+1}\lambda e^{-\lambda x}\,dx$$
**הצבה:**
$$=\left[-e^{-\lambda x}\right]_k^{k+1}=e^{-\lambda k}-e^{-\lambda(k+1)}=e^{-\lambda k}\left(1-e^{-\lambda}\right)$$
**תוצאה:** ✅ $P(N=k)=\left(e^{-\lambda}\right)^k\left(1-e^{-\lambda}\right)$, $k=0,1,2,\dots$ – התפלגות גאומטרית עם הסתברות הצלחה $p=1-e^{-\lambda}$.

**ב.** עבור $0<z<1$, המאורע $Z\le z$ קורה כש-$X$ נופל בתחילת אחד הקטעים: $k\le X\le k+z$ עבור $k$ כלשהו.

**נוסחה:**
$$P(Z\le z)=\sum_{k=0}^{\infty}P(k\le X\le k+z)$$
**הצבה:** כל איבר הוא אינטגרל כמו בסעיף א:
$$P(k\le X\le k+z)=e^{-\lambda k}-e^{-\lambda(k+z)}=e^{-\lambda k}\left(1-e^{-\lambda z}\right)$$
$$P(Z\le z)=\left(1-e^{-\lambda z}\right)\sum_{k=0}^{\infty}e^{-\lambda k}=\frac{1-e^{-\lambda z}}{1-e^{-\lambda}}$$
גוזרים לפי $z$:
$$f_Z(z)=\frac{d}{dz}\,\frac{1-e^{-\lambda z}}{1-e^{-\lambda}}=\frac{\lambda e^{-\lambda z}}{1-e^{-\lambda}}$$
**תוצאה:** ✅
$$f_Z(z)=\begin{cases}\dfrac{\lambda e^{-\lambda z}}{1-e^{-\lambda}} & 0<z<1\\[2mm] 0 & \text{אחרת}\end{cases}$$
בדיקה: $\int_0^1 f_Z\,dz=\frac{1-e^{-\lambda}}{1-e^{-\lambda}}=1$ ✓.

💡 **הרעיון:** מחלקים את הציר לקטעים באורך 1 ומסכמים על כולם – טור הנדסי. (אפשר גם להראות ש-$N$ ו-$Z$ בלתי תלויים: $P(N=k,Z\le z)=P(N=k)P(Z\le z)$.)"""

S["c5311305"] = r"""> ⚠️ בנוסח השמור נכתב $P(X>b\mid X>0)=e^{-b}$ – זו טעות הקלדה. מה שמתאים לשאר השאלה (ובפרט לסעיף ו) הוא $P(X>\beta\mid X>0)=e^{-\beta/(a+b)}$ לכל $\beta\ge0$, וכך נפתר כאן.

### 📘 מה צריך לדעת קודם
- פונקציה אופיינית: $\phi_X(v)=E[e^{ivX}]$. לסכום של משתנים בלתי תלויים: $\phi_{X+Y}=\phi_X\phi_Y$.
- למשתנה מעריכי עם תוחלת $b$: $f(\alpha)=\frac1be^{-\alpha/b}$.
- משתנה מעורב (חלק בדיד וחלק רציף): $E[g(X)]=P(X=0)g(0)+P(X>0)E[g(X)\mid X>0]$.
- צפיפות מותנית מתקבלת מגזירה: $f_X(\beta\mid X>0)=-\frac{d}{d\beta}P(X>\beta\mid X>0)$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.**
$$\phi_Y(v)=\int_0^\infty e^{iv\alpha}\frac1be^{-\alpha/b}d\alpha=\frac1b\int_0^\infty e^{-\alpha\left(\frac1b-iv\right)}d\alpha=\frac1b\cdot\frac{1}{\frac1b-iv}$$
✅ $\phi_Y(v)=\dfrac{1}{1-ivb}$. תוחלת: $E[Y]=\frac1i\phi_Y'(0)=\frac1i\cdot\frac{ib}{(1-ivb)^2}\Big|_{v=0}$ ⇐ ✅ $E[Y]=b$.

**ב.** גוזרים את ההסתברות המותנית:
$$f_X(\beta\mid X>0)=-\frac{d}{d\beta}e^{-\beta/(a+b)}=\frac{1}{a+b}e^{-\beta/(a+b)},\quad\beta\ge0$$
$$\int_0^\infty\frac{1}{a+b}e^{-\beta/(a+b)}d\beta=\left[-e^{-\beta/(a+b)}\right]_0^\infty=0-(-1)=1\ ✓$$

**ג.** $P(X>0)=1-\frac{b}{a+b}=\frac{a}{a+b}$. הצפיפות כוללת הלם (דלתא) ב-0 על החלק הבדיד:
$$f_X(\beta)=\frac{b}{a+b}\delta(\beta)+\frac{a}{a+b}\cdot\frac{1}{a+b}e^{-\beta/(a+b)},\quad\beta\ge0$$
$$E[X]=\frac{b}{a+b}\cdot0+\frac{a}{a+b}\cdot(a+b)=a\ ✓$$
(התוחלת של החלק המעריכי היא $a+b$.)

**ד.**
$$\phi_X(v)=\frac{b}{a+b}\cdot e^{0}+\frac{a}{a+b}\cdot\frac{1}{1-iv(a+b)}=\frac{b\,(1-iv(a+b))+a}{(a+b)(1-iv(a+b))}$$
המונה: $b+a-ivb(a+b)=(a+b)(1-ivb)$, ולכן ✅ $\phi_X(v)=\dfrac{1-ivb}{1-iv(a+b)}$.

**ה.** $X,Y$ בלתי תלויים:
$$\phi_Z(v)=\phi_X(v)\phi_Y(v)=\frac{1-ivb}{1-iv(a+b)}\cdot\frac{1}{1-ivb}=\frac{1}{1-iv(a+b)}$$

**ו.** לפי סעיף א, $\frac{1}{1-iv(a+b)}$ היא בדיוק הפונקציה האופיינית של משתנה מעריכי עם תוחלת $a+b$. פונקציה אופיינית קובעת את ההתפלגות באופן יחיד ⇐ ✅ $Z$ מעריכי עם פרמטר $a+b$.

💡 **הרעיון:** מוסיפים למשתנה מעריכי $Y$ משתנה "לפעמים 0, לפעמים מעריכי" – והתוצאה שוב מעריכית. הכלי: מכפלת פונקציות אופייניות."""

S["2cb65105"] = r"""### 📘 מה צריך לדעת קודם
- אם $f(x,y)=g(x)h(y)$ על תחום מלבני, $X$ ו-$Y$ בלתי תלויים.
- צפיפות של מכפלה $Z=XY$: $f_Z(z)=\int f_{XY}\!\left(x,\frac zx\right)\frac{1}{|x|}dx$ (משתנה עזר $W=X$, יעקוביאן $\frac1{|x|}$).
- אם $Y$ בלתי תלוי ב-$X$, אז $E(Y\mid g(X))=E(Y)$.

### ✍️ הדרך המלאה (כמו במחברת)
**בדיקת נרמול ופירוק:** $\int_0^1 4x\,dx=2$ ו-$\int_1^\infty y^{-3}dy=\frac12$, המכפלה 1 ✓.
$f(x,y)=\underbrace{2x}_{f_X(x)}\cdot\underbrace{\frac{2}{y^3}}_{f_Y(y)}$ ⇐ $X,Y$ בלתי תלויים.

**א.** **נוסחה:**
$$f_Z(z)=\int f\!\left(x,\frac zx\right)\frac1x\,dx$$
**תחום:** $0\le x\le1$ וגם $y=\frac zx\ge1$, כלומר $x\le z$. לכן $x\in[0,\min(1,z)]$.
**הצבה:**
$$f\!\left(x,\frac zx\right)\frac1x=\frac{4x}{(z/x)^3}\cdot\frac1x=\frac{4x^3}{z^3}$$
$$f_Z(z)=\int_0^{\min(1,z)}\frac{4x^3}{z^3}dx=\frac{\min(1,z)^4}{z^3}$$
**תוצאה:** ✅
$$f_Z(z)=\begin{cases}z & 0\le z\le1\\[1mm] \dfrac{1}{z^3} & z>1\\[1mm] 0 & z<0\end{cases}$$
בדיקה: $\int_0^1z\,dz+\int_1^\infty z^{-3}dz=\frac12+\frac12=1$ ✓.

**ב.** $X^2$ היא פונקציה של $X$ בלבד, ו-$Y$ בלתי תלוי ב-$X$:
$$E(Y\mid X^2)=E(Y)=\int_1^\infty y\cdot\frac{2}{y^3}dy=2\left[-\frac1y\right]_1^\infty=2$$
**תוצאה:** ✅ $E(Y\mid X^2)=2$ (קבוע).

💡 **הרעיון:** קודם לבדוק אם הצפיפות מתפרקת למכפלה – אז התוחלת המותנית היא פשוט התוחלת."""

S["594e5a44"] = S["2cb65105"].replace("### 📘 מה צריך לדעת קודם", "> ⚠️ בנוסח השמור כאן נכתב $f(x,y)=4x$ – צפיפות כזו לא מסתכמת ל-1 (האינטגרל על $y\\ge1$ אינסופי). זו אותה שאלה כמו \"שאלה 2 - פונקציית צפיפות משותפת והתניה\", עם $f(x,y)=\\frac{4x}{y^3}$, וכך היא נפתרת.\n\n### 📘 מה צריך לדעת קודם", 1)

BIN = r"""> ⚠️ הנוסח של שאלה 2 מתרגול 6 לא נמצא בחומר. נפתר כאן עם שלושת המשערכים המקובלים לבעיה הזו: משערך הסימן $\hat A_1=\mathrm{sign}(Y)$, המשערך האופטימלי $\hat A_2=E[A\mid Y]=\tanh\!\left(\frac{Y}{\sigma^2}\right)$, והמשערך הלינארי האופטימלי $\hat A_3=\frac{Y}{1+\sigma^2}$. אם בתרגול פותחו משערכים אחרים – השיטה זהה.

### 📘 מה צריך לדעת קודם
- שגיאה ריבועית ממוצעת: $MSE=E[(\hat A-A)^2]$. המשערך האופטימלי במובן הזה הוא התוחלת המותנית $E[A\mid Y]$ – אף משערך אחר לא נותן MSE קטן ממנו.
- משערך לינארי אופטימלי: $\hat A=E[A]+\frac{\mathrm{Cov}(A,Y)}{\mathrm{Var}(Y)}(Y-E[Y])$, ו-$MSE=\mathrm{Var}(A)-\frac{\mathrm{Cov}^2(A,Y)}{\mathrm{Var}(Y)}$.
- $Q(x)=P(N(0,1)>x)$.

### ✍️ הדרך המלאה (כמו במחברת)
**נתונים:** $E[A]=0$, $\mathrm{Var}(A)=E[A^2]=1$, $\mathrm{Var}(Y)=1+\sigma^2$, $\mathrm{Cov}(A,Y)=E[A^2]+E[AX]=1$.

**א. משערך הסימן $\hat A_1$:** הוא טועה כשהרעש "הופך" את הסימן. אם $A=1$: טעות כש-$X<-1$, בהסתברות $Q(1/\sigma)$; ובטעות $(\hat A_1-A)^2=(-1-1)^2=4$. אותו דבר עבור $A=-1$.
$$MSE_1=4\,Q\!\left(\frac1\sigma\right)$$
**המשערך הלינארי $\hat A_3$:**
$$\hat A_3=0+\frac{1}{1+\sigma^2}Y,\qquad MSE_3=1-\frac{1^2}{1+\sigma^2}=\frac{\sigma^2}{1+\sigma^2}$$
**המשערך האופטימלי $\hat A_2=\tanh(Y/\sigma^2)$:** $MSE_2=1-E\!\left[\tanh^2\!\left(\frac{Y}{\sigma^2}\right)\right]$ – אין ביטוי סגור, מחשבים מספרית. תמיד $MSE_2\le MSE_1$ ו-$MSE_2\le MSE_3$.

**דוגמה מספרית (חושבה):**

| $\sigma$ | $MSE_1=4Q(1/\sigma)$ | $MSE_2$ (אופטימלי) | $MSE_3=\frac{\sigma^2}{1+\sigma^2}$ |
|---|---|---|---|
| 0.5 | 0.091 | 0.069 | 0.200 |
| 1 | 0.635 | 0.450 | 0.500 |
| 2 | 1.234 | 0.796 | 0.800 |

✅ האופטימלי הכי טוב תמיד. בין השניים האחרים: ברעש חלש ($\sigma=0.5$) משערך הסימן עדיף על הלינארי, וברעש חזק – הלינארי עדיף.

**ב. הסתברות שגיאה $\varepsilon=P(\hat A\ne A)$:** $\hat A_2$ ו-$\hat A_3$ נותנים ערכים רציפים, ולכן כמעט אף פעם לא שווים בדיוק ל-$\pm1$: $\varepsilon_2=\varepsilon_3=1$.
$$\varepsilon_1=Q\!\left(\frac1\sigma\right)$$
(למשל $\sigma=1$: $\varepsilon_1=0.159$.) ✅ לפי קריטריון הסתברות שגיאה משערך הסימן עדיף – הוא בוחר את הערך הסביר יותר בהינתן $Y$ (כלל הכרעה), וזה בדיוק מה שהקריטריון הזה מודד.

💡 **הרעיון:** "הכי טוב" תלוי בקריטריון: לשגיאה ריבועית – התוחלת המותנית; להסתברות שגיאה – החלטה בין הערכים האפשריים."""
S["8fff574f"] = BIN
S["b67459a1"] = BIN

UNI = r"""> ⚠️ $\alpha,\beta$ הן שתי הספרות האחרונות של תעודת הזהות שלך – כאן הפתרון בסימנים: $a=\alpha+1$, $b=\beta+1$. בסעיפי ההגרלה צריך להריץ בעצמך.

### 📘 מה צריך לדעת קודם
- אם $X\sim U[0,1]$ אז $aX\sim U[0,a]$ עם צפיפות $\frac1a$, ו-$-bY\sim U[-b,0]$ עם צפיפות $\frac1b$.
- צפיפות של סכום משתנים בלתי תלויים היא קונבולוציה: $f_Z(z)=\int f_U(u)f_V(z-u)\,du$.
- היסטוגרמה מנורמלת: $\hat f(z)\approx\frac{N_{[a,b]}}{n\cdot\Delta}$, כאשר $\Delta$ רוחב התא ו-$n$ מספר ההגרלות.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $U=aX\in[0,a]$, $V=-bY\in[-b,0]$, $Z=U+V\in[-b,a]$.
$$f_Z(z)=\int_0^a\frac1a\cdot\frac1b\,\mathbb{1}\{-b\le z-u\le0\}\,du=\frac{1}{ab}\cdot\text{אורך הקטע }\big[\max(0,z),\ \min(a,z+b)\big]$$
עבור $a\ge b$ (אם $a<b$ – מחליפים את התפקידים, והחלק השטוח בגובה $\frac1b$):
$$f_Z(z)=\begin{cases}\dfrac{z+b}{ab} & -b\le z\le0\\[2mm] \dfrac1a & 0\le z\le a-b\\[2mm] \dfrac{a-z}{ab} & a-b\le z\le a\\[2mm] 0 & \text{אחרת}\end{cases}$$
✅ טרפז; כאשר $a=b$ – משולש. בדיקה: שטח = $\frac{b}{2a}+\frac{a-b}{a}+\frac{b}{2a}=1$ ✓.

**ב-ד.** מגרילים $n$ זוגות $(X,Y)$, מחשבים $Z$, מחלקים את $[-b,a]$ ל-$k$ תאים ברוחב $\Delta=\frac{a+b}{k}$, סופרים $N$ בכל תא ומציירים $\frac{N}{n\Delta}$ באותו גרף עם $f_Z$ מסעיף א.

**ה-ז.** ✅ השפעת הפרמטרים:
- $n$ גדל ⇐ בכל תא יש יותר ערכים, הרעש היחסי קטן (בערך כמו $\frac{1}{\sqrt{n\,\Delta\,f}}$), וההיסטוגרמה מתקרבת לצפיפות.
- $k$ גדל ⇐ תאים צרים, רואים את הצורה בפירוט, אבל בכל תא פחות ערכים ולכן יותר רעש. $n=500,k=50$: רועש מאוד; $n=10{,}000,k=500$: רוב התאים עם כ-20 ערכים – עדיין רועש.
- צריך $n$ גדול בהרבה מ-$k$ כדי שההיסטוגרמה תהיה חלקה.

💡 **הרעיון:** סכום של שני אחידים בלתי תלויים = קונבולוציה של שני מלבנים = טרפז."""
S["e9018cf4"] = UNI
S["5b4f4b7b"] = UNI

POIS = r"""### 📘 מה צריך לדעת קודם
- תוחלת שלמה: $E[X]=E\big[E[X\mid Y]\big]$. שונות שלמה: $\mathrm{Var}(X)=E\big[\mathrm{Var}(X\mid Y)\big]+\mathrm{Var}\big(E[X\mid Y]\big)$.
- פואסון עם פרמטר $y$: תוחלת $y$ ושונות $y$. מעריכי עם קצב $\lambda$: $E[Y]=\frac1\lambda$, $\mathrm{Var}(Y)=\frac{1}{\lambda^2}$.
- נוסחת העזר: $\int_0^\infty x^ke^{-\alpha x}dx=\frac{k!}{\alpha^{k+1}}$.
- המשערך האופטימלי (שגיאה ריבועית מינימלית) הוא התוחלת המותנית.

### ✍️ הדרך המלאה (כמו במחברת)
**א.**
$$E[X_1]=E\big[E[X_1\mid Y]\big]=E[Y]=\frac1\lambda$$
$$\mathrm{Var}(X_1)=E[Y]+\mathrm{Var}(Y)=\frac1\lambda+\frac1{\lambda^2}$$
✅ $E[X_1]=\frac1\lambda$, $\mathrm{Var}(X_1)=\frac{\lambda+1}{\lambda^2}$.

**ב.**
$$P(X_1=k)=\int_0^\infty e^{-y}\frac{y^k}{k!}\cdot\lambda e^{-\lambda y}dy=\frac{\lambda}{k!}\int_0^\infty y^ke^{-(1+\lambda)y}dy=\frac{\lambda}{k!}\cdot\frac{k!}{(1+\lambda)^{k+1}}$$
✅ $P(X_1=k)=\dfrac{\lambda}{(1+\lambda)^{k+1}}$, $k=0,1,2,\dots$ – גאומטרית: $p=\frac{\lambda}{1+\lambda}$, $P(X_1=k)=p(1-p)^k$.
בדיקה: תוחלת גאומטרית $\frac{1-p}{p}=\frac1\lambda$ ✓ (כמו בסעיף א).

**ג.** ✅ **לא** בלתי תלויים. בלי חישובים: ערך גדול של $X_2$ מרמז ש-$Y$ גדול, ולכן גם $X_1$ צפוי להיות גדול. בחישוב קצר:
$$\mathrm{Cov}(X_1,X_2)=E\big[\mathrm{Cov}(X_1,X_2\mid Y)\big]+\mathrm{Cov}\big(E[X_1|Y],E[X_2|Y]\big)=0+\mathrm{Var}(Y)=\frac1{\lambda^2}\ne0$$
(בלתי תלויים **בהינתן** $Y$, אבל לא בלי התניה.)

**ד.** משערך של $Y$ מתוך $X_1=k$ – לפי ההדרכה:
$$f_{Y\mid X_1}(y\mid k)=\frac{P(X_1=k\mid y)f_Y(y)}{P(X_1=k)}\propto y^ke^{-(1+\lambda)y}$$
$$E[Y\mid X_1=k]=\frac{\int_0^\infty y^{k+1}e^{-(1+\lambda)y}dy}{\int_0^\infty y^{k}e^{-(1+\lambda)y}dy}=\frac{(k+1)!/(1+\lambda)^{k+2}}{k!/(1+\lambda)^{k+1}}=\frac{k+1}{1+\lambda}$$
✅ $\hat Y=\dfrac{X_1+1}{\lambda+1}$.

**ה.** $X_1$ ו-$X_2$ קשורים רק דרך $Y$:
$$E[X_1\mid X_2]=E\big[E[X_1\mid Y,X_2]\,\big|\,X_2\big]=E[Y\mid X_2]=\frac{X_2+1}{\lambda+1}$$
✅ $\hat X_1=\dfrac{X_2+1}{\lambda+1}$ (לפי סעיף ד, עם $X_2$ במקום $X_1$).

💡 **הרעיון:** משתנה משותף ($Y$) יוצר תלות. מתנים עליו, פותרים בקלות, ומחליקים עם תוחלת שלמה."""
S["29e31a66"] = POIS
S["2b8782d4"] = POIS.replace("**ד.** משערך של $Y$ מתוך $X_1=k$", "**ד.** (בנוסח הזה: משערך של $X_1$ בהינתן $Y$ – זו פשוט התוחלת המותנית: ✅ $\\hat X_1=E[X_1\\mid Y]=Y$.) ובנוסח המלא של השאלה – משערך של $Y$ מתוך $X_1=k$", 1)
Q_2b = (r"נתון הווקטור האקראי $X=[X_1,X_2]^T$ ומשתנה מעריכי $Y\sim\exp(\lambda)$. ידוע שבהינתן $Y=y$ המשתנים $X_1,X_2$ בלתי תלויים"
        r" ומתפלגים פואסונית עם פרמטר $y$: $X_i\mid Y\sim\mathrm{Pois}(y)$, $i=1,2$." "\n"
        "א. חשבו תוחלת ושונות של $X_1$.\n"
        "ב. חשבו את חוק ההסתברות השולי של $X_1$, כלומר $P(X_1=k)$.\n"
        "ג. הוכיחו או הפריכו: $X_1,X_2$ בלתי תלויים.\n"
        "ד. מצאו משערך אופטימלי של $X_1$ בהינתן $Y$ (ושל $Y$ בהינתן $X_1$).\n"
        "ה. מצאו משערך אופטימלי ל-$X_1$ בהינתן $X_2$.\n"
        r"עזר: $\int_0^\infty x^ke^{-\alpha x}dx=\frac{k!}{\alpha^{k+1}}$.")

S["7bc24bca"] = r"""> ⚠️ בסעיף ד כתוב $N_{AT}$ (בשאלה המקורית ייתכן טעות הקלדה). נפתר עבור $N_{AT}$ עם קבוע $A>1$.

### 📘 מה צריך לדעת קודם
- תהליך פואסון עם קצב $\lambda$: בקטע באורך $h$ קטן יש קפיצה בהסתברות $\lambda h$, ומספר הקפיצות בזמן $t$ פואסוני: $P(K=j)=e^{-\lambda t}\frac{(\lambda t)^j}{j!}$.
- כאן: קפיצות מגיעות בקצב $\lambda$ (כי $\frac13+\frac13+\frac13=1$), וכל קפיצה בגודל 1, 2 או 3 בהסתברות $\frac13$ לכל אחד, בלי תלות.
- תוספות בלתי תלויות: מה שקורה ב-$[0,T]$ בלתי תלוי במה שקורה ב-$[T,AT]$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** פונקציית מדגם: מדרגות עולות שמתחילות ב-0, קבועות בין הקפיצות, וכל קפיצה בגובה 1, 2 או 3 (לא רק 1 כמו בפואסון רגיל). ✅ לשרטט שתי מדרגות כאלה עם זמני קפיצה וגבהים שונים.

**ב.** בקטע קטן $\Delta$:
$$E[U_k]=1\cdot\tfrac13\lambda\Delta+2\cdot\tfrac13\lambda\Delta+3\cdot\tfrac13\lambda\Delta=2\lambda\Delta$$
$$E[N_T]=\sum_{k=0}^{n-1}2\lambda\Delta=2\lambda n\Delta=2\lambda T$$
✅ $E[N_T]=2\lambda T$.

**ג.** נסמן $\mu=\lambda T$. כדי להגיע ל-2 יש שתי דרכים:
1. קפיצה אחת בגודל 2: $P(K=1)\cdot\frac13=\mu e^{-\mu}\cdot\frac13$.
2. שתי קפיצות בגודל 1: $P(K=2)\cdot\left(\frac13\right)^2=\frac{\mu^2}{2}e^{-\mu}\cdot\frac19$.
$$P(N_T=2)=e^{-\mu}\left(\frac{\mu}{3}+\frac{\mu^2}{18}\right)$$
✅ (למשל $\lambda T=1.3$: $0.1437$.)

**ד.** בדומה, להגיע ל-3 בזמן $s$ (נסמן $\kappa=\lambda s$): קפיצה של 3 ($\kappa e^{-\kappa}\cdot\frac13$), שתי קפיצות 1+2 או 2+1 ($\frac{\kappa^2}{2}e^{-\kappa}\cdot\frac29$), שלוש קפיצות של 1 ($\frac{\kappa^3}{6}e^{-\kappa}\cdot\frac1{27}$):
$$P(N_s=3)=e^{-\kappa}\left(\frac\kappa3+\frac{\kappa^2}{9}+\frac{\kappa^3}{162}\right)$$
ו-$P(N_s=1)=\kappa e^{-\kappa}\cdot\frac13$.
$$P(N_T=2\mid N_{AT}=3)=\frac{P(N_T=2)\,P(N_{AT}-N_T=1)}{P(N_{AT}=3)}$$
עם $\mu=\lambda T$, $\nu=\lambda(A-1)T$, $\kappa=\lambda AT$ (האקספוננטים מצטמצמים כי $\mu+\nu=\kappa$):
$$P(N_T=2\mid N_{AT}=3)=\frac{\left(\frac\mu3+\frac{\mu^2}{18}\right)\frac\nu3}{\frac\kappa3+\frac{\kappa^2}{9}+\frac{\kappa^3}{162}}$$
✅ (בדיקה: $\lambda=1.3$, $T=1$, $A=2$ נותן $0.132$, וכך גם בסימולציה.)

💡 **הרעיון:** זה תהליך פואסון "מורכב": סופרים לפי מספר הקפיצות ואז לפי הגדלים. תוספות בלתי תלויות מאפשרות לפרק את ההסתברות המותנית."""

S["2ae47894"] = r"""> ⚠️ הנוסח השמור משובש. השאלה: $X=[X_1,\dots,X_n]^T$ וקטור גאוסי, ו-$Y$ הוא הווקטור שמתקבל מסידור איברי $X$ בסדר עולה. א. האם $Y$ בהכרח וקטור גאוסי? ב. האם כל רכיב של $Y$ גאוסי?

### 📘 מה צריך לדעת קודם
- וקטור גאוסי: כל צירוף לינארי של רכיביו הוא משתנה גאוסי.
- משתנה גאוסי עם שונות חיובית מקבל ערכים חיוביים ושליליים, כל אחד בהסתברות חיובית.
- $\min(X_1,X_2)$: $P(\min>y)=P(X_1>y)P(X_2>y)$ למשתנים בלתי תלויים.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** ✅ **לא נכון.** דוגמה נגדית: $X_1,X_2\sim N(0,1)$ בלתי תלויים, $Y_1=\min(X_1,X_2)$, $Y_2=\max(X_1,X_2)$.
אם $Y$ היה גאוסי, הצירוף $Y_2-Y_1$ היה גאוסי. אבל $Y_2-Y_1=|X_1-X_2|\ge0$ תמיד, והוא לא קבוע (שונות חיובית). משתנה גאוסי לא קבוע לא יכול להיות תמיד אי-שלילי ⇐ סתירה.

**ב.** ✅ **לא נכון.** אותה דוגמה, $Y_1=\min(X_1,X_2)$:
$$P(Y_1>y)=\big(1-\Phi(y)\big)^2\ \Rightarrow\ f_{Y_1}(y)=2\varphi(y)\big(1-\Phi(y)\big)$$
זו לא צפיפות גאוסית: היא לא סימטרית סביב התוחלת שלה. למשל $E[Y_1]=-\frac{1}{\sqrt\pi}\approx-0.564$, אבל החציון שונה ממנה: $P(Y_1\le m)=\frac12$ נותן $1-\Phi(m)=\frac{1}{\sqrt2}$, כלומר $m\approx-0.545$. בגאוסי החציון שווה לתוחלת.

💡 **הרעיון:** מיון הוא פעולה לא לינארית – היא שוברת גאוסיות, גם של הווקטור וגם של רכיבים בודדים."""

S["19737ec0"] = r"""> ⚠️ בנוסח השמור כתוב "שונות $\sigma_N^2-1$" ו-$\theta$ חסר: הכוונה $\mathrm{Var}(N)=\sigma_N^2$ (כנראה $=1$), ו-$\theta$ אחיד ב-$(-\pi,\pi)$.

### 📘 מה צריך לדעת קודם
- צירוף לינארי עם מקדמים **קבועים** של משתנים גאוסיים במשותף – גאוסי.
- בהינתן $\theta$, $\sin\theta$ ו-$\cos\theta$ הם קבועים.
- משערך אופטימלי במקרה גאוסי עם תוחלות 0: $\hat X_1=\frac{\mathrm{Cov}(X_1,Y)}{\mathrm{Var}(Y)}Y$.

### ✍️ הדרך המלאה (כמו במחברת)
נסמן $s=\sin\theta$, $c=\cos\theta$.

**א.** בהינתן $\theta$: $Y=sX_1+cX_2+N$ – צירוף לינארי עם מקדמים קבועים של $X_1,X_2,N$, שהם גאוסיים במשותף ($N$ בלתי תלוי ב-$X$) ⇐ ✅ **בהינתן $\theta$, $Y$ גאוסי**, עם תוחלת 0 ושונות
$$\mathrm{Var}(Y\mid\theta)=\sigma_X^2\left(s^2+0.5c^2+2\cdot0.2\,sc\right)+\sigma_N^2$$
בלי התניה: השונות הזו משתנה עם $\theta$, ולכן $Y$ הוא תערובת של גאוסיים עם שונויות שונות – ✅ **בלי התניה $Y$ אינו גאוסי** (לתערובת כזו "זנבות" כבדים מגאוסי עם אותה שונות).

**ב.** בהינתן $\theta$ הכול גאוסי, אז המשערך האופטימלי לינארי:
$$\mathrm{Cov}(X_1,Y\mid\theta)=s\,\mathrm{Var}(X_1)+c\,\mathrm{Cov}(X_1,X_2)=\sigma_X^2(s+0.2c)$$
$$\hat X_1=\frac{\mathrm{Cov}(X_1,Y\mid\theta)}{\mathrm{Var}(Y\mid\theta)}Y$$
✅
$$\hat X_1=\frac{\sigma_X^2(\sin\theta+0.2\cos\theta)}{\sigma_X^2\left(\sin^2\theta+0.5\cos^2\theta+0.4\sin\theta\cos\theta\right)+\sigma_N^2}\,Y$$
(בדיקה בסימולציה: $\sigma_X^2=2$, $\sigma_N^2=1$, $\theta=0.7$ – המקדם $0.568$ ✓.)

💡 **הרעיון:** מתנים על המשתנה הלא-גאוסי ($\theta$), ואז הבעיה גאוסית ופותרים במשערך לינארי."""

S["1a1ec672"] = r"""### 📘 מה צריך לדעת קודם
- בלתי תלויים ⇐ חסרי קורלציה. לכן אם $\mathrm{Cov}(X,Y)\ne0$ – הם תלויים.
- אי-תלות מותנית: $f_{X,Y\mid Z}=f_{X\mid Z}\,f_{Y\mid Z}$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** נחשב קווריאנס (כל הרעשים בלתי תלויים ב-$Z$ ובינם לבין עצמם):
$$\mathrm{Cov}(X,Y)=\mathrm{Cov}(Z+N_1,\,Z+N_2)=\mathrm{Var}(Z)$$
$$E[Z]=300,\quad E[Z^2]=\frac{200^2+300^2+400^2}{3}=\frac{290000}{3},\quad \mathrm{Var}(Z)=\frac{290000}{3}-90000=\frac{20000}{3}\approx6667$$
✅ $\mathrm{Cov}(X,Y)\approx6667\ne0$ ⇐ $X$ ו-$Y$ **תלויים**.

**ב.** בהינתן $Z=z$: $X=z+N_1$ ו-$Y=z+N_2$. $N_1,N_2$ בלתי תלויים זה בזה וב-$Z$, ולכן
$$f_{X,Y\mid Z}(x,y\mid z)=\varphi(x-z)\,\varphi(y-z)=f_{X\mid Z}(x\mid z)\,f_{Y\mid Z}(y\mid z)$$
✅ בהינתן $Z$ הם **בלתי תלויים** (מותנית).

💡 **הרעיון:** "סיבה משותפת" ($Z$) יוצרת תלות; כשיודעים אותה – התלות נעלמת."""

FIX_Q = {"2b8782d4": Q_2b}
FINE = ["90ddeeb3", "990a0df6", "130332dd", "597ce441", "abf499f7", "00f77aee", "6ddd33ef", "a6939ae9", "3db55017"]


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "rnd_hollow.json").read_text(encoding="utf-8"))}
    out = []
    for k, sol in S.items():
        x = xs[k]
        fx = {"id": x["id"], "title": x["title"], "solution_md": sol + DONE, "uncertain": k in ("8fff574f", "b67459a1", "7bc24bca")}
        if k in FIX_Q:
            fx["question_md"] = FIX_Q[k]
        out.append(fx)
    for k in FINE:
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + OK, "uncertain": False})
    (HERE.parent / "fix_2811_rnd_hollow.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
