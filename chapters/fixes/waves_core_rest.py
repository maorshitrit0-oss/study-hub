"""Waves core exercises (weeks 1 and 3) not covered by the practice-sheet fixes: checked, re-solved, in full (08/11/2026)."""
import json

S = []

S.append({"id": "b2dd7932-682c-4e4b-9c38-da4fa6e5e57f", "uncertain": False, "solution_md": r"""
### מה נותנים ומה הכלים
$f=5\,\text{GHz}$, $\lambda=3\,\text{cm}$ **בתוך החומר**, $\mu_r=1$, בלי הפסדים. כל הקשרים של גל מישורי בתווך חסר הפסדים:
$$k=\frac{2\pi}{\lambda},\qquad v_p=\lambda f=\frac\omega k=\frac{c}{\sqrt{\varepsilon_r\mu_r}},\qquad \eta=\sqrt{\frac\mu\varepsilon}=\eta_0\sqrt{\frac{\mu_r}{\varepsilon_r}}$$

### 1. קבוע ההתפשטות
$$k=\frac{2\pi}{\lambda}=\frac{2\pi}{0.03}\approx\boxed{209.4\ \left[\tfrac{\text{rad}}{\text m}\right]}$$

### 2. מהירות הפאזה
$$v_p=\lambda f=0.03\cdot5\cdot10^9=\boxed{1.5\cdot10^8\ \left[\tfrac{\text m}{\text s}\right]}$$
(חצי ממהירות האור.)

### 3. המקדם הדיאלקטרי היחסי
$$v_p=\frac{c}{\sqrt{\varepsilon_r}}\ \Rightarrow\ \varepsilon_r=\left(\frac{c}{v_p}\right)^2=\left(\frac{3\cdot10^8}{1.5\cdot10^8}\right)^2=\boxed{4}$$

### 4. העכבה
$$\eta=\frac{\eta_0}{\sqrt{\varepsilon_r}}=\frac{377}{2}\approx\boxed{188.5\ \Omega}$$

**בדיקה:** $k=\omega\sqrt{\mu\varepsilon}=\frac{2\pi\cdot5\cdot10^9\cdot2}{3\cdot10^8}=209.4$ ✅

💡 **הרעיון:** מה שנמדד בתוך החומר ($\lambda$) נותן ישר את $k$ ואת $v_p$; היחס $c/v_p$ הוא $n=\sqrt{\varepsilon_r}$, וממנו $\eta=\eta_0/n$. זה בדיוק הסעיף הראשון בכל שאלת גל במבחן ("מקדמי שבירה, עכבות, קבועי התקדמות").
"""})

S.append({"id": "a26af07a-237f-4738-a410-dca431fc50c8", "uncertain": False, "solution_md": r"""
### סעיף א: השדה המגנטי
גל בריק, מתקדם ב-$+z$ ($e^{-j\beta z}$), ולכן $\hat k=\hat z$ ו-$\eta=\eta_0$:
$$\tilde H=\frac1{\eta_0}\,\hat z\times\tilde E=\frac{E_0}{\eta_0}\left(\hat z\times\hat x+j\rho_0\,\hat z\times\hat y\right)e^{-j\beta z}$$
$\hat z\times\hat x=\hat y$ ו-$\hat z\times\hat y=-\hat x$:
$$\tilde H=\frac{E_0}{\eta_0}\left(\hat y-j\rho_0\hat x\right)e^{-j\beta z}$$
**מעבר לזמן:** $\vec h=\text{Re}\{\tilde He^{j\omega t}\}$. עם $\text{Re}\{e^{j\theta}\}=\cos\theta$ ו-$\text{Re}\{-je^{j\theta}\}=\sin\theta$:
$$\boxed{\vec h(z,t)=\frac{E_0}{\eta_0}\Big[\cos(\omega t-\beta z)\,\hat y+\rho_0\sin(\omega t-\beta z)\,\hat x\Big]}\ \left[\tfrac{\text A}{\text m}\right]$$
(זהה ל-$-\rho_0\cos(\omega t-\beta z+\frac\pi2)\hat x$, כי $\cos(a+\frac\pi2)=-\sin a$.)

### סעיף ב: מתי הקיטוב מעגלי
מסתכלים על $\tilde E$: רכיב $x$ עם משרעת $E_0$ ופאזה 0; רכיב $y$ עם $j\rho_0E_0$. אם $\rho_0$ ממשי:
- משרעת $y$ היא $|\rho_0|E_0$.
- $j=e^{j\pi/2}$, ולכן הפאזה של $y$ היא $+\frac\pi2$ אם $\rho_0>0$, ו-$-\frac\pi2$ אם $\rho_0<0$.

מעגלי = משרעות שוות **וגם** $\Delta\phi=\pm\frac\pi2$:
$$|\rho_0|=1\ \Rightarrow\ \boxed{\rho_0=\pm1}$$
- $\rho_0=+1$: $\Delta\phi=+\frac\pi2$ ⇐ לפי מוסכמת התרגול CCW (במבט בכיוון ההתקדמות זה LHCP).
- $\rho_0=-1$: $\Delta\phi=-\frac\pi2$ ⇐ CW (RHCP).

### סעיף ג: מתי ליניארי
ליניארי דורש $\Delta\phi=0$ או $\pi$. כאן לכל $\rho_0\ne0$ ממשי ההפרש הוא $\pm\frac\pi2$ – לא ליניארי. נשאר:
$$\boxed{\rho_0=0}$$
(נשאר רק $\hat x$ – ליניארי לאורך ציר $x$.)
(אם $\rho_0$ היה מותר להיות מדומה, למשל $\rho_0=-j a$, היה יוצא $\tilde E=E_0(\hat x+a\hat y)$ – ליניארי בזווית $\arctan a$.)

**כל שאר הערכים** ($\rho_0$ ממשי, $\ne0,\pm1$): **אליפטי**, עם צירים לאורך $x$ ו-$y$.

💡 **הרעיון:** $\tilde H=\frac1\eta\hat k\times\tilde E$; את סוג הקיטוב קוראים ישר מהפאזור: $j$ = $+90^\circ$, $-j$ = $-90^\circ$, ומשווים משרעות.
"""})

S.append({"id": "3875244a-01bf-4e97-bd82-a21b145d5f7b", "uncertain": False, "solution_md": r"""
### הנוסחה
$$\tan(2\theta)=\frac{2E_{0x}E_{0y}\cos\Delta\phi}{E_{0x}^2-E_{0y}^2}$$
$\theta$ היא זווית **הציר הראשי** (הארוך) של האליפסה מציר $x$.

### הצבה
$E_{0x}=1$, $E_{0y}=2$, $\Delta\phi=-\frac\pi4$, $\cos(-\frac\pi4)=\frac{\sqrt2}2$:
$$\tan(2\theta)=\frac{2\cdot1\cdot2\cdot\frac{\sqrt2}{2}}{1-4}=\frac{2\sqrt2}{-3}\approx-0.943$$

### ⚠️ המלכודת: באיזה רביע
$\arctan(-0.943)=-43.3^\circ$ – אבל זה רק אחד משני הפתרונות. כדי לבחור נכון מסתכלים על **הסימנים** של המונה והמכנה (כמו `atan2`):
- מונה $=2\sqrt2>0$
- מכנה $=-3<0$

מונה חיובי ומכנה שלילי ⇐ $2\theta$ ברביע **השני**:
$$2\theta=180^\circ-43.3^\circ=136.7^\circ\ \Rightarrow\ \boxed{\theta\approx68.3^\circ}$$

**בדיקת שכל:** $E_{0y}=2>E_{0x}=1$ – האליפסה "שוכבת" קרוב לציר $y$, ולכן הציר הראשי צריך להיות קרוב ל-$90^\circ$, לא ל-$-22^\circ$. ✅

> ⚠️ הגרסה הקודמת כאן נתנה $\theta\approx-21.65^\circ$ – זה הכיוון של **הציר הקטן** ($68.3^\circ-90^\circ$). כלל: כשהמכנה שלילי ($E_{0y}>E_{0x}$) מוסיפים $180^\circ$ ל-$2\theta$.

### כיוון הסיבוב
$\Delta\phi=-\frac\pi4$ (שלילי, לא $0$ ולא $\pi$) ⇐ אליפטי, ולפי מוסכמת התרגול הסיבוב **CW**.

💡 **הרעיון:** הנוסחה נותנת $\tan$ של $2\theta$ – תמיד לבדוק את סימני המונה והמכנה ולבחור רביע, ולוודא שהתוצאה מתאימה לרכיב הגדול יותר.
"""})

S.append({"id": "c5ef4b9c-1dcf-46c9-83c6-119189f5d2de", "uncertain": True, "solution_md": r"""
### הרעיון: הלוח הוא "קו תמסורת" באורך $d$
בפגיעה ניצבת, שכבה של חומר מתנהגת בדיוק כמו קטע קו תמסורת: העכבה האופיינית שלה היא $\eta_2$, ומה ש"מאחוריה" (אזור 3) הוא העומס $Z_L$. מחשבים את העכבה ש"רואים" בחזית הלוח ($Z_{in}$), ואז את $\Gamma$ מול אזור 1.

### שלב 1: העכבות
$$\eta_1=\eta_3=\eta_0\approx377\,\Omega,\qquad \eta_2=\frac{\eta_0}{\sqrt{\varepsilon_r}},\qquad Z_L=\eta_3=\eta_0$$

### שלב 2: עכבת הכניסה בחזית הלוח
$$Z_{in}=\eta_2\,\frac{Z_L+j\eta_2\tan(\beta_2d)}{\eta_2+jZ_L\tan(\beta_2d)}$$
רבע אורך גל: $\beta_2d=\frac{2\pi}{\lambda_2}\cdot\frac{\lambda_2}4=\frac\pi2$ ⇐ $\tan\to\infty$. מחלקים מונה ומכנה ב-$\tan$ ומשאירים רק את האיברים שלו:
$$Z_{in}=\eta_2\cdot\frac{j\eta_2}{jZ_L}=\frac{\eta_2^2}{Z_L}=\frac{\eta_0^2/\varepsilon_r}{\eta_0}=\frac{\eta_0}{\varepsilon_r}$$
(זה **שנאי רבע גל**: הופך את העומס ל-$\eta_2^2/Z_L$.)

### שלב 3: מקדם ההחזרה ב-$z=0$
$$\Gamma=\frac{Z_{in}-\eta_1}{Z_{in}+\eta_1}=\frac{\frac{\eta_0}{\varepsilon_r}-\eta_0}{\frac{\eta_0}{\varepsilon_r}+\eta_0}=\boxed{\frac{1-\varepsilon_r}{1+\varepsilon_r}}$$
**דוגמה:** $\varepsilon_r=4$ ⇐ $\Gamma=-\frac35=-0.6$, כלומר $|\Gamma|^2=36\%$ מההספק חוזר.

**השוואה:** לוח בעובי **חצי** אורך גל ($\beta_2d=\pi$, $\tan=0$) נותן $Z_{in}=Z_L=\eta_0$ ⇐ $\Gamma=0$ – הלוח "שקוף". ברבע גל ההחזרה דווקא **מקסימלית**. (כדי לקבל $\Gamma=0$ ברבע גל צריך $\eta_2=\sqrt{\eta_1\eta_3}$ – זה עקרון הציפוי נגד החזרות על עדשות.)

> ⚠️ נוסח השאלה נלקח מקובץ הרצאה 3 (מצגת סרוקה) ועוד לא הושווה מילה במילה לשקף. הפתרון נבדק מאפס.

💡 **הרעיון:** שכבה = קו תמסורת ⇐ $Z_{in}$ בנוסחת הקו ⇐ $\Gamma=\frac{Z_{in}-\eta_1}{Z_{in}+\eta_1}$. רבע גל: $Z_{in}=\eta_2^2/Z_L$; חצי גל: $Z_{in}=Z_L$.
"""})

print(json.dumps(S, ensure_ascii=False, indent=1))
