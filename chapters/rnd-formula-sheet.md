<!-- print: large -->
# דף נוסחאות – אותות אקראיים ורעש

## 1. הסתברות – הבסיס

**תוחלת ושונות**
$$E[X]=\int x f_X(x)dx\quad(\text{רציף}),\qquad E[X]=\sum_k x_kP(X=x_k)\quad(\text{בדיד})$$
$$E[g(X)]=\int g(x)f_X(x)dx$$
$$\mathrm{Var}(X)=E[X^2]-E^2[X],\qquad \mathrm{Var}(aX+b)=a^2\mathrm{Var}(X)$$

**שני משתנים**
$$\mathrm{Cov}(X,Y)=E[XY]-E[X]E[Y],\qquad \rho=\frac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}$$
$$\mathrm{Var}(X\pm Y)=\mathrm{Var}X+\mathrm{Var}Y\pm2\mathrm{Cov}(X,Y)$$

- בלתי תלויים ⇐ $E[XY]=E[X]E[Y]$ ⇐ חסרי קורלציה (ההפך – רק בגאוסי).
- $f_{X|Y}(x|y)=\dfrac{f_{XY}(x,y)}{f_Y(y)}$, $\ f_Y(y)=\int f_{XY}(x,y)dx$
- החלקה: $E[X]=E\big[E[X|Y]\big]$
- שונות שלמה: $\mathrm{Var}X=E[\mathrm{Var}(X|Y)]+\mathrm{Var}(E[X|Y])$

**⚠️ רציף או בדיד?** אם נתונה **צפיפות** $f(x)$ – זה רציף, ומחשבים עם **אינטגרל**, לא עם סכום.

## 2. פילוגים חשובים

| פילוג | צפיפות / הסתברות | $E$ | $\mathrm{Var}$ |
|---|---|---|---|
| אחיד $U[a,b]$ | $\frac1{b-a}$ | $\frac{a+b}2$ | $\frac{(b-a)^2}{12}$ |
| מעריכי $\lambda$ | $\lambda e^{-\lambda x},\ x\ge0$ | $\frac1\lambda$ | $\frac1{\lambda^2}$ |
| גאוסי $N(\mu,\sigma^2)$ | $\frac{1}{\sqrt{2\pi}\sigma}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$ | $\mu$ | $\sigma^2$ |
| פואסון $\lambda$ | $\frac{\lambda^k}{k!}e^{-\lambda}$ | $\lambda$ | $\lambda$ |
| בינומי $(n,p)$ | $\binom nk p^k(1-p)^{n-k}$ | $np$ | $np(1-p)$ |
| ברנולי $p$ | $P(1)=p$ | $p$ | $p(1-p)$ |

- מעריכי: $E[X^2]=\frac2{\lambda^2}$, $\ P(X>t)=e^{-\lambda t}$ (חסר זיכרון).
- גאוסי: $P(X>a)=Q\!\left(\frac{a-\mu}{\sigma}\right)$, $\ Q(-x)=1-Q(x)$.
- אחיד $[-a,a]$: $E=0$, $E[X^2]=\frac{a^2}3$.

**אינטגרלים שחוזרים**
$$\int_0^\infty x^ne^{-ax}dx=\frac{n!}{a^{n+1}}:\quad \int_0^\infty e^{-ax}=\tfrac1a,\ \ \int_0^\infty xe^{-ax}=\tfrac1{a^2},\ \ \int_0^\infty x^2e^{-ax}=\tfrac2{a^3}$$
$$\int_{-\infty}^{\infty}e^{-\frac{x^2}{2\sigma^2}}dx=\sqrt{2\pi}\sigma,\qquad \sum_{k=0}^\infty\frac{\lambda^k}{k!}=e^\lambda,\qquad \sum_{k=0}^\infty q^k=\frac1{1-q}$$

## 3. שערוך

**משערך אופטימלי (MMSE)** = התוחלת המותנית:
$$\hat X(y)=E[X|Y=y]=\int x\,f_{X|Y}(x|y)\,dx$$

**משערך לינארי אופטימלי (LMMSE)**
$$\boxed{\hat X=E[X]+\frac{\mathrm{Cov}(X,Y)}{\mathrm{Var}(Y)}\big(Y-E[Y]\big)}$$
$$\text{השגיאה: } E[(X-\hat X)^2]=\mathrm{Var}X-\frac{\mathrm{Cov}^2(X,Y)}{\mathrm{Var}Y}=\sigma_X^2(1-\rho^2)$$

- עקרון האורתוגונליות: $E[(X-\hat X)\,Y]=0$.
- גאוסיים במשותף ⇐ MMSE = LMMSE.

**מקרה נפוץ: $Y=X+N$, $X,N$ בלתי תלויים**
$$E[Y]=E[X]+E[N],\quad \mathrm{Var}Y=\mathrm{Var}X+\mathrm{Var}N,\quad \mathrm{Cov}(X,Y)=\mathrm{Var}X$$
$$\hat X=E[X]+\frac{\sigma_X^2}{\sigma_X^2+\sigma_N^2}\big(Y-E[Y]\big)$$
(ואם $Y=X-N$: $\mathrm{Cov}(X,Y)$ עדיין $=\mathrm{Var}X$, ו-$E[Y]=E[X]-E[N]$.)

**וקטורים:** $\mu_y=\mathbf A\mu_x$, $\ \mathbf C_{yy}=\mathbf A\mathbf C_{xx}\mathbf A^\top$, $\ \hat{\underline x}=\mu_x+\mathbf C_{xy}\mathbf C_{yy}^{-1}(\underline y-\mu_y)$

### 🧭 מתכון – שאלת שערוך

1. לזהות: רציף/בדיד; מה נתון (צפיפות? בלתי תלויים?).
2. לחשב $E[X],E[Y],\mathrm{Var}Y,\mathrm{Cov}(X,Y)$ – כל אחד בשורה.
3. להציב בנוסחת ה-LMMSE, ולפשט.
4. אם מבקשים "אופטימלי" (לא לינארי): $f_{X|Y}$ ואז $E[X|Y]$.

## 4. תהליכים אקראיים

$$m_X(t)=E[X(t)],\qquad R_X(t_1,t_2)=E[X(t_1)X(t_2)]$$
$$C_X(t_1,t_2)=R_X(t_1,t_2)-m_X(t_1)m_X(t_2)$$
$$R_{XY}(t_1,t_2)=E[X(t_1)Y(t_2)]$$

**סטציונרי במובן הרחב (סמ"ר / WSS)** – שני תנאים:

1. $m_X(t)=m$ קבוע.
2. $R_X(t,t+\tau)=R_X(\tau)$ – תלוי **רק** בהפרש.

**סמ"ר במשותף:** כל אחד סמ"ר **וגם** $R_{XY}(t,t+\tau)$ תלוי רק ב-$\tau$.

**תכונות $R_X(\tau)$ (סמ"ר):** $R_X(0)=E[X^2]\ge|R_X(\tau)|$, $\ R_X(-\tau)=R_X(\tau)$, $\ R_{XY}(-\tau)=R_{YX}(\tau)$

**בזמן בדיד:** אותו דבר עם $n$: $R_X[n_1,n_2]=E\{X[n_1]X[n_2]\}$, $\ k=n_2-n_1$.

**זהויות טריגו**
$$\cos a\cos b=\tfrac12[\cos(a-b)+\cos(a+b)]$$
$$\sin a\sin b=\tfrac12[\cos(a-b)-\cos(a+b)]$$
$$\sin a\cos b=\tfrac12[\sin(a+b)+\sin(a-b)]$$
$$\cos^2a=\tfrac12(1+\cos2a),\quad \sin^2a=\tfrac12(1-\cos2a)$$
$$\cos(a\pm b)=\cos a\cos b\mp\sin a\sin b$$

### ⭐ המבחן שלך: $X[n]=A+nB$ ($A,B$ בת"ס, תוחלת 0)

$$R_X[n_1,n_2]=\sigma_A^2+n_1n_2\sigma_B^2\ \Rightarrow\ \text{לא סמ"ר (תלוי ב-}n_1n_2)$$

- ההפרש $Y[n]=X[n+1]-X[n]=B$ – קבוע ⇐ $R_Y=\sigma_B^2$ ⇐ **סמ"ר**.
- **טריק:** לפשט את התהליך החדש לפני שמחשבים.

### ⭐ שני מקרים קלאסיים נוספים
**(א) משרעות אקראיות:** $X(t)=A\cos\omega_0t+B\sin\omega_0t$, $\ E[A]=E[B]=0$, $E[AB]=0$:
$$R_X(t_1,t_2)=\sigma_A^2\cos\omega_0t_1\cos\omega_0t_2+\sigma_B^2\sin\omega_0t_1\sin\omega_0t_2$$

- סמ"ר **רק אם** $\sigma_A^2=\sigma_B^2=\sigma^2$, ואז $R_X(\tau)=\sigma^2\cos\omega_0\tau$.
- $Y(t)=A\cos\omega_0t-B\sin\omega_0t$: גם אם $\sigma_A=\sigma_B$, $R_{XY}=\sigma^2\cos\omega_0(t_1+t_2)$ ⇐ **לא** סמ"ר במשותף.

**(ב) פאזה אקראית:** $X(t)=A\cos(\omega_0t+\Theta)$, $\Theta\sim U[0,2\pi]$ בת"ס:
$$m_X=0,\qquad R_X(\tau)=\frac{E[A^2]}2\cos\omega_0\tau\ \ \Rightarrow\ \text{סמ"ר}$$

- $E[\cos(\omega t+\Theta)]=0$, $\ E[\cos(\alpha+2\Theta)]=0$.

### 🧭 מתכון – שאלת סמ"ר

1. תוחלת: להוציא קבועים, $E[A]=0$ וכו'.
2. $R_X(t_1,t_2)$: לפתוח סוגריים, תוחלת לכל איבר, $E[AB]$.
3. זהויות טריגו ⇐ להפריד ל"$(t_1-t_2)$" ו"$(t_1+t_2)$".
4. אם נשאר $t_1+t_2$ ⇐ **לא** סמ"ר (או: מה התנאי שיתבטל).

## 5. צפיפות הספק ומערכות LTI

**ווינר-חינצ'ין (סמ"ר):**
$$S_X(f)=\int R_X(\tau)e^{-j2\pi f\tau}d\tau,\qquad R_X(\tau)=\int S_X(f)e^{j2\pi f\tau}df$$
$$P=E[X^2]=R_X(0)=\int_{-\infty}^{\infty}S_X(f)\,df$$

- $S_X(f)\ge0$, זוגית וממשית.

**מערכת LTI:** $Y=X*h$, $\ H(f)=\mathcal F\{h\}$
$$m_Y=m_X\,H(0)$$
$$R_Y(\tau)=R_X(\tau)*h(\tau)*h(-\tau)$$
$$\boxed{S_Y(f)=|H(f)|^2S_X(f)},\qquad S_{XY}(f)=H(f)S_X(f)$$
$$P_Y=\int|H(f)|^2S_X(f)\,df$$

**רעש לבן:** $S_N(f)=\frac{N_0}2$, $\ R_N(\tau)=\frac{N_0}2\delta(\tau)$
$$P_{out}=\frac{N_0}2\int|H(f)|^2df=\frac{N_0}{2}\int|h(t)|^2dt$$

- רוחב סרט רעש שקול: $B_N=\dfrac{\int_0^\infty|H(f)|^2df}{|H(0)|^2}$; מסנן RC: $B_N=\frac1{4RC}$.

**זוגות פורייה שימושיים**

| $R(\tau)$ | $S(f)$ |
|---|---|
| $\delta(\tau)$ | $1$ |
| $1$ | $\delta(f)$ |
| $\cos 2\pi f_0\tau$ | $\frac12[\delta(f-f_0)+\delta(f+f_0)]$ |
| $e^{-a\lvert\tau\rvert}$ | $\frac{2a}{a^2+(2\pi f)^2}$ |
| $1-\frac{\lvert\tau\rvert}T,\ \lvert\tau\rvert\le T$ | $T\,\mathrm{sinc}^2(fT)$ |
| $\mathrm{rect}$: $1$ ב-$\lvert f\rvert\le B$ | $2B\,\mathrm{sinc}(2B\tau)$ |

- $\mathrm{sinc}(x)=\frac{\sin\pi x}{\pi x}$. כפל ב-$\cos2\pi f_0\tau$ ⇐ $S$ זז ל-$\pm f_0$ עם $\frac12$.

### 🧭 מתכון – שאלת מסנן / הספק

1. לרשום $S_X(f)$ (רעש לבן = קבוע).
2. $|H(f)|^2$ – **לכתוב את התחום** (איפה $H\ne0$).
3. $S_Y=|H|^2S_X$ + **שרטוט** עם ערכים בצירים.
4. הספק = שטח מתחת ל-$S_Y$ (לנצל זוגיות: $2\int_0$).

**דוגמה (המבחן שלך):** $S_X=2$ ב-$|f|\le1$, $H=1-|f|$ ב-$|f|\le1$:
$$S_Y=2(1-|f|)^2,\ |f|\le1;\qquad P_Y=2\cdot2\int_0^1(1-f)^2df=\frac43$$

- **"מסנן $H_2\ne0$ עם מוצא 0":** $H_2=0$ בכל מקום ש-$S_X\ne0$ (כאן: $0$ ב-$|f|\le1$, $1$ מחוץ).

## 6. תהליך פואסון (קצב $\lambda$)

$$P\big(N(t)=k\big)=\frac{(\lambda t)^k}{k!}e^{-\lambda t},\qquad E[N(t)]=\mathrm{Var}[N(t)]=\lambda t$$

- תוספות **בלתי תלויות**: $N(t_2)-N(t_1)\sim\text{Poisson}(\lambda(t_2-t_1))$.
- **העבר לא משנה:** "בשעה האחרונה היו 3" – לא נכנס לחישוב על השעות הבאות (קטעים זרים).
- **"אירוע כל 20 דקות בממוצע"** ⇐ $\frac1\lambda=\frac13$ שעה ⇐ $\lambda=3$ לשעה.
- $P(N(t)=0)=e^{-\lambda t}$; $\ P(N(t)\ge1)=1-e^{-\lambda t}$.
- זמן בין קפיצות: מעריכי $\lambda$. זמן הקפיצה ה-$k$: $f(t)=\frac{\lambda^kt^{k-1}}{(k-1)!}e^{-\lambda t}$.
- $\{U_k>t\}=\{N(t)<k\}$.
- $R_N(t_1,t_2)=\lambda\min(t_1,t_2)+\lambda^2t_1t_2$ ⇐ **לא** סמ"ר.
- סכום שני תהליכים בת"ס: פואסון עם $\lambda_1+\lambda_2$; $\ P(\text{הראשון קופץ קודם})=\frac{\lambda_1}{\lambda_1+\lambda_2}$.
- בהינתן $N(s)=n$ ו-$t<s$: $N(t)\sim\text{Bin}(n,\frac ts)$.
- הסתברות מותנית: $P(A|B)=\frac{P(A\cap B)}{P(B)}$ – לפרק לתוספות בלתי תלויות!

### 🧭 מתכון – שאלת פואסון

1. **יחידות:** $\lambda$ לשעה/לדקה – להתאים ל-$t$ ($\lambda t$ = מספר צפוי).
2. לכתוב את המאורע במילים ⇐ כמספר קפיצות בקטעים **זרים**.
3. קטעים זרים ⇐ להכפיל הסתברויות.
4. "לפחות אחד" ⇐ $1-P(0)$.

## 7. תהליכים גאוסיים, וינר ומסנן מתואם

- תהליך גאוסי: כל צירוף לינארי של דגימות – גאוסי. גאוסי + סמ"ר ⇐ סטציונרי במובן הצר.
- גאוסי דרך מערכת LTI ⇐ גאוסי.
- $P(X(t)>a)=Q\big(\frac{a-m}{\sqrt{R_X(0)-m^2}}\big)$.

**מסנן וינר (לא סיבתי)** – שערוך $S$ מתוך $X=S+N$, $S,N$ חסרי קורלציה:
$$H(f)=\frac{S_{XS}(f)}{S_X(f)}=\frac{S_S(f)}{S_S(f)+S_N(f)}$$
$$e_{min}=\int\frac{S_S\,S_N}{S_S+S_N}df$$

- אם $R_{XS}=0$ ⇐ $H=0$ (המשערך = התוחלת).

**מסנן מתואם** (אות ידוע $s(t)$ ברעש לבן):
$$h(t)=k\,s(t_0-t),\qquad SNR_{max}=\frac{2E_s}{N_0},\quad E_s=\int s^2(t)dt$$

## 8. מה לכתוב כדי לקבל את כל הנקודות

- **כל** שלב בשורה: נוסחה ⇐ הצבה ⇐ תוצאה (ציון חלקי!).
- "האם סמ"ר?" ⇐ להראות את **שני** התנאים, ולכתוב **תנאי** אם יש.
- בשרטוט: צירים, ערכים, **תחום**.
- לבדוק: הספק ≥ 0, שונות ≥ 0, הסתברות בין 0 ל-1.
- עונים על **כל** השאלות. במילואים מותר לבחור בין 3 ל-4, אבל **אם עונים על שתיהן – ניקוד כפול על שני הסעיפים הטובים** ⇐ לנסות את שתיהן אם יש זמן.
- בטופס יש גם דף נוסחאות רשמי (עמ' 3-5) – הדף הזה משלים אותו.
