"""Waves: exercises whose stored solution was hollow / wrong / flagged (28/11/2026), solved by Claude; every number
recomputed in python in the session (polarization sums, Fresnel TM/TE, TIR, sea water). Writes
chapters/fix_2811_waves_hollow.json for publish.yml inspect=exercises (course ^גלים)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש במלואו; כל המספרים חושבו מחדש."

S = {}

S["13a31ffe"] = r"""### 📘 מה צריך לדעת קודם
- קיטוב לפי $E_{0x},E_{0y}$ והפרש הפאזה $\Delta\phi=\phi_y-\phi_x$, אחרי שכותבים את שני הרכיבים כ**קוסינוס עם משרעת חיובית**.
- $\sin a=\cos\left(a-\frac\pi2\right)$.
- מוסכמת התרגול (גל ב-$+z$): $\Delta\phi=-\frac\pi2$ ⇐ סיבוב עם כיוון השעון (CW) במבט בכיוון ההתקדמות = RHCP.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $E_y=3\sin\omega t=3\cos\left(\omega t-\frac\pi2\right)$, ולכן
$$E_{0x}=E_{0y}=3,\qquad \Delta\phi=-\frac\pi2-0=-\frac\pi2$$
משרעות שוות והפרש פאזה $\pm\frac\pi2$ ⇐ ✅ **קיטוב מעגלי**.

**ב.** עוקבים אחרי הקצה של הווקטור:
- $\omega t=0$: $\vec E=3\hat x$.
- $\omega t=\frac\pi2$: $\vec E=3\hat y$.

הווקטור עובר מ-$\hat x$ ל-$\hat y$. הגל מתקדם ב-$+z$: כשאגודל יד ימין בכיוון $+z$, האצבעות מתכופפות מ-$x$ ל-$y$ ⇐ ✅ **מעגלי ימני (RHCP)**. במבט בכיוון ההתקדמות (מאחורי הגל, לכיוון $+z$) הסיבוב **עם כיוון השעון** – כמו במוסכמת התרגול ל-$\Delta\phi=-\frac\pi2$.

💡 **הרעיון:** מעגלי = משרעות שוות + רבע מחזור הפרש; כיוון – לפי יד ימין מול כיוון ההתקדמות."""

S["cfcba41c"] = r"""### 📘 מה צריך לדעת קודם
- גל מקוטב **ליניארית** כששני הרכיבים באותה פאזה (או הפוכה): אז היחס $E_y/E_x$ ממשי.
- $1+e^{j\theta}=2\cos\frac\theta2\,e^{j\theta/2}$ ו-$1-e^{j\theta}=-2j\sin\frac\theta2\,e^{j\theta/2}$.

### ✍️ הדרך המלאה (כמו במחברת)
מחברים רכיב-רכיב, עם $\varphi_1=\varphi_2+\frac\pi4$:
$$\tilde E_x=E_{10}e^{j\varphi_1}+E_{20}e^{j\varphi_2},\qquad \tilde E_y=-jE_{10}e^{j\varphi_1}+jE_{20}e^{j\varphi_2}$$
**כאשר $E_{10}=E_{20}=E_0$** (המקרה שבו התשובה פשוטה), מוציאים $E_0e^{j\varphi_2}$:
$$\tilde E_x=E_0e^{j\varphi_2}\left(1+e^{j\pi/4}\right)=2E_0\cos\frac\pi8\,e^{j(\varphi_2+\pi/8)}$$
$$\tilde E_y=jE_0e^{j\varphi_2}\left(1-e^{j\pi/4}\right)=j\cdot\left(-2j\sin\frac\pi8\right)E_0e^{j(\varphi_2+\pi/8)}=2E_0\sin\frac\pi8\,e^{j(\varphi_2+\pi/8)}$$
לשני הרכיבים **אותה פאזה** $\varphi_2+\frac\pi8$ ⇐ ✅ **קיטוב ליניארי**, בזווית
$$\tan\gamma=\frac{E_y}{E_x}=\tan\frac\pi8\ \Rightarrow\ \gamma=\frac\pi8=22.5^\circ\ \text{מציר }x$$
(נבדק מספרית: היחס $E_y/E_x=0.4142=\tan22.5^\circ$ בכל רגע.)
> ⚠️ בפתרון הקודם נכתב $67.5^\circ$ – זה לא נכון לנתונים האלה. ($-22.5^\circ$ היה יוצא אם $\varphi_2=\varphi_1+\frac\pi4$.)

**אם $E_{10}\ne E_{20}$:** המשרעות של הרכיבים המעגליים שונות, ולכן הסכום **אליפטי** (במקרה הקיצוני, אחד מהם 0, נשאר מעגלי).

💡 **הרעיון:** שני גלים מעגליים בכיווני סיבוב הפוכים ובאותה משרעת = גל ליניארי; הפרש הפאזה ביניהם קובע את הזווית (חצי ממנו)."""

S["812f92a7"] = r"""> ⚠️ בנוסח: $\vec E_{i0}=3.46\hat x-3\hat z$. אבל בגל מישורי $\vec k\cdot\vec E=0$, ו-$\pi(1\cdot3.46+1.73\cdot(-3))\ne0$. עם $-2\hat z$: $3.46-1.73\cdot2=0$ ✓ ו-$|\vec E_{i0}|=\sqrt{3.46^2+2^2}=4$ – בדיוק "משרעת כוללת 4" שבשאלה. לכן הנכון $\vec E_{i0}=3.46\hat x-2\hat z$, $E_{i0}=4\ \frac{\text{V}}{\text{m}}$. השדה החשמלי במישור הפגיעה ($xz$) ⇐ **קיטוב מקביל (TM)**.

### 📘 מה צריך לדעת קודם
- $k=\omega\sqrt{\mu\varepsilon}=\frac{2\pi}{\lambda}$, זווית מהנורמל ($z$): $\tan\theta=\frac{k_x}{k_z}$.
- זווית קריטית: $\sin\theta_c=\frac{n_2}{n_1}=\sqrt{\frac{\varepsilon_2}{\varepsilon_1}}$. מעליה – החזרה מלאה, $|\Gamma|=1$, גל דועך בתווך 2 בלי הספק ממוצע לתוכו.
- TM: $\Gamma_\parallel=\frac{\eta_2\cos\theta_t-\eta_1\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i}$, $T_\parallel=\frac{2\eta_2\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i}$.

### ✍️ הדרך המלאה (כמו במחברת)
**7.1** $k_1=\pi\sqrt{1+1.73^2}=2\pi\ \frac{\text{rad}}{\text{m}}$, $\tan\theta_i=\frac{1}{1.73}$ ⇐ $\theta_i=\theta_r=30^\circ$.
$$\sin\theta_c=\sqrt{\frac{1.5}{8}}=0.433\ \Rightarrow\ \theta_c=25.7^\circ<30^\circ$$
✅ החזרה מלאה: $\theta_r=30^\circ$; אין זווית העברה ממשית ($\sin\theta_t=\sqrt{\frac{8}{1.5}}\cdot0.5=1.155>1$) – בתווך 2 גל דועך.

**7.2** $\lambda_1=\frac{2\pi}{k_1}=1\text{ m}$, $f=\frac{c}{\sqrt{8}\,\lambda_1}=\frac{3\cdot10^8}{2.828}=106\text{ MHz}$ – אותו תדר לכל שלושת הגלים. המוחזר: $\lambda=1\text{ m}$. בתווך 2 הגל מתקדם רק לאורך $x$ עם $\beta=k_1\sin\theta_i=\pi$ ⇐ אורך גל לאורך הממשק $\frac{2\pi}{\pi}=2\text{ m}$, ודועך ב-$z$ עם
$$\alpha=\sqrt{k_1^2\sin^2\theta_i-k_2^2}=\sqrt{\pi^2-\left(2\pi\sqrt{\tfrac{1.5}{8}}\right)^2}=\pi\sqrt{1-0.75}=\frac\pi2\approx1.57\ \frac{\text{Np}}{\text{m}}$$

**7.3** ✅ $\vec k_r=\pi(\hat x-1.73\hat z)$. בתווך 2: $e^{-j\pi x}e^{-\frac\pi2z}$ – רכיב $x$ ממשי $\pi$, ובמקום רכיב $z$ ממשי יש דעיכה $\alpha=\frac\pi2$.

**7.4** ✅ $|\Gamma|=1$ ⇐ $E_{r0}=E_{i0}=4\ \frac{\text{V}}{\text{m}}$ (בשינוי פאזה). לגל הדועך יש משרעת על הממשק ($T\ne0$), אבל הוא לא מתפשט.

**7.5** ✅ $P_t=0$ – לגל הדועך אין הספק ממוצע לתוך תווך 2 (רכיב $z$ של וקטור פוינטינג מדומה טהור).

**7.6** $\varepsilon_2=2.5\varepsilon_0$: $\sin\theta_c=\sqrt{\frac{2.5}{8}}=0.559$ ⇐ $\theta_c=34.0^\circ>30^\circ$ ⇐ **יש** גל עובר.
$$\sin\theta_t=\sqrt{\frac{8}{2.5}}\cdot0.5=0.894\ \Rightarrow\ \theta_t=63.43^\circ,\ \cos\theta_t=0.447$$
$$\eta_1=\frac{120\pi}{\sqrt8}=133.3\,\Omega,\qquad \eta_2=\frac{120\pi}{\sqrt{2.5}}=238.4\,\Omega$$
$$T_\parallel=\frac{2\cdot238.4\cdot0.866}{238.4\cdot0.447+133.3\cdot0.866}=\frac{412.9}{222.0}=1.860\ \Rightarrow\ E_{t0}=1.860\cdot4=7.44\ \frac{\text{V}}{\text{m}}$$
$$P_t=\frac{E_{t0}^2}{2\eta_2}=\frac{7.44^2}{2\cdot238.4}=0.116\ \frac{\text{W}}{\text{m}^2}$$
✅ $P_t\approx0.116\ \frac{\text{W}}{\text{m}^2}$ (בכיוון $\vec k_t$); הרכיב הניצב לממשק: $P_t\cos\theta_t=0.052$.
**בדיקת שימור:** $\Gamma_\parallel=-0.040$, $P_i\cos\theta_i=\frac{16}{2\cdot133.3}\cdot0.866=0.0520=P_r\cos\theta_i+P_t\cos\theta_t$ ✓.
> ⚠️ בפתרון הקודם נכתב $0.229$ – לא מתקבל מאף גרסה של הנתונים (גם לא עם $E_{i0}=4.58$ או קיטוב TE). לבדוק מול הפתרון הרשמי.

💡 **הרעיון:** קודם להשוות $\theta_i$ ל-$\theta_c$. מעל – החזרה מלאה וגל דועך; מתחת – פרנל רגיל ובדיקת שימור הספק."""

S["14e6fc12"] = r"""### 📘 מה צריך לדעת קודם
- כותבים את שני הרכיבים כקוסינוס עם משרעת חיובית; $\Delta\phi=\phi_y-\phi_x$.
- $\sin a=\cos\left(a-\frac\pi2\right)$, $-\sin a=\cos\left(a+\frac\pi2\right)$.
- זווית האליפסה: $\tan2\gamma=\frac{2E_{0x}E_{0y}\cos\Delta\phi}{E_{0x}^2-E_{0y}^2}$ – **לשים לב לרביע**: מכנה שלילי ⇐ $2\gamma$ ברביע השני.
- כאן הגלים מתקדמים ב-**$-z$** (יש $\omega t+\beta z$), ולכן כיוון הסיבוב במבט בכיוון ההתקדמות הפוך לגל ב-$+z$.

### ✍️ הדרך המלאה (כמו במחברת)
נסמן $a=\omega t+\beta z$.

**$\vec e_1$:** $E_y=\sin a=\cos\left(a-\frac\pi2\right)$, משרעות $1,1$, $\Delta\phi=-\frac\pi2$ ⇐ מעגלי. ב-$z=0$: הווקטור עובר מ-$\hat x$ (ב-$\omega t=0$) ל-$\hat y$ (ב-$\omega t=\frac\pi2$). הגל נע ב-$-z$, ובמבט בכיוון ההתקדמות (מלמעלה, לכיוון $-z$) זה נראה ✅ **מעגלי CCW** (נגד כיוון השעון).

**$\vec e_2$:** $E_y=-\sin a=\cos\left(a+\frac\pi2\right)$, $\Delta\phi=+\frac\pi2$ ⇐ ✅ **מעגלי CW** (הפוך מ-$\vec e_1$).

**$\vec e_3$:** $E_y=-2\sin\left(a-\frac\pi4\right)=2\cos\left(a+\frac\pi4\right)$ ⇐ $E_{0x}=1$, $E_{0y}=2$, $\Delta\phi=+\frac\pi4$ ⇐ משרעות שונות ⇐ **אליפטי**.
$$\tan2\gamma=\frac{2\cdot1\cdot2\cdot\cos\frac\pi4}{1^2-2^2}=\frac{2.828}{-3}=-0.943$$
המכנה שלילי ⇐ $2\gamma$ ברביע השני: $2\gamma=180^\circ-43.3^\circ=136.7^\circ$.
✅ $\gamma\approx68.3^\circ$ מציר $x$ (הציר **הגדול** – הגיוני, כי $E_{0y}>E_{0x}$ והאליפסה "עומדת"). כיוון הסיבוב: **CW** במבט בכיוון ההתקדמות (לפי $\Delta\phi>0$ בגל ב-$-z$; כך גם בהרצאה).
> ⚠️ בפתרון הקודם נכתב $\gamma=21.6^\circ$ – זה $-21.7^\circ$ בלי תיקון הרביע, כלומר כיוון **הציר הקטן**. הנכון $68.3^\circ$ (כמו בדף הנוסחאות, ת3).

💡 **הרעיון:** קוסינוסים חיוביים ← $\Delta\phi$ ← סוג; באליפטי – $\tan2\gamma$ עם בדיקת רביע."""

S["7a9f6d36"] = r"""### 📘 מה צריך לדעת קודם
- $e^{-jkz}$ עם $k>0$ (ובזמן $e^{j\omega t}$) ⇐ גל שמתקדם ב-$+z$.
- $(\hat x\pm j\hat y)$ – משרעות שוות והפרש פאזה $\pm\frac\pi2$ ⇐ מעגלי.
- גל ליניארי ⇐ לשני הרכיבים אותה פאזה (היחס ביניהם ממשי).

### ✍️ הדרך המלאה (כמו במחברת)
**2.1** בשני הגלים הפאזה $\omega t-k_iz$ ⇐ מתקדמים ב-$+z$. בזמן, ב-$z=0$:
$$\vec e_1=\hat x\cos\omega t-\hat y\sin\omega t,\qquad \vec e_2=\hat x\cos\omega t+\hat y\sin\omega t$$
$\vec e_1$: מ-$\hat x$ (ב-$t=0$) ל-$-\hat y$ (רבע מחזור אחר כך) – במבט על מישור $xy$ כשציר $z$ יוצא מהדף (מול הגל המגיע) זה ✅ **CW**. $\vec e_2$: מ-$\hat x$ ל-$+\hat y$ ⇐ ✅ **CCW**.
(במבט מאחורי הגל, בכיוון ההתקדמות, שני הכיוונים מתהפכים – תמיד לציין מאיזה צד מסתכלים.)

**2.2** ב-$z=0$ האקספוננטים שווים ל-1:
$$\tilde E_{sum}=(\hat x+j\hat y)+(\hat x-j\hat y)=2\hat x$$
✅ רק רכיב $x$ ⇐ **ליניארי** לאורך ציר $x$.

**2.3** מוציאים $e^{-jk_1z}$ ומשתמשים ב-$k_2=k_1+\Delta k$:
$$\tilde E_{sum}=e^{-jk_1z}\left[(\hat x+j\hat y)+(\hat x-j\hat y)e^{-j\Delta k\,z}\right]$$
ב-$\Delta k\,z=90^\circ$: $e^{-j\pi/2}=-j$:
$$(\hat x+j\hat y)+(\hat x-j\hat y)(-j)=\hat x+j\hat y-j\hat x-\hat y=(1-j)\hat x-(1-j)\hat y=(1-j)(\hat x-\hat y)$$
✅ שני הרכיבים באותה פאזה ובאותו גודל, ובסימנים הפוכים ⇐ **ליניארי** לאורך $\hat x-\hat y$, כלומר בזווית $45^\circ$ לציר $x$ (מתחתיו: $-45^\circ$).
**הכללה:** לכל $z$ הקיטוב ליניארי, בזווית $-\frac{\Delta k\,z}{2}$ – ציר הקיטוב מסתובב לאורך ההתקדמות.

💡 **הרעיון:** סכום של שני מעגליים הפוכים = ליניארי; הפרש הפאזה המצטבר $\Delta k\,z$ מסובב את הציר בחצי ממנו."""

S["5ff0de73"] = r"""### 📘 מה צריך לדעת קודם
- ממוצע על מחזור: $\frac1T\int_0^T(\cdot)\,dt$, עם $T=\frac{2\pi}{\omega}$.
- $\cos^2u=\frac{1+\cos2u}{2}$, והממוצע של $\cos(2\omega t+c)$ על מחזור שלם הוא 0.
- $\hat x\cdot\hat x=1$, $\hat x\cdot\hat y=0$ וכו'.

### ✍️ הדרך המלאה (כמו במחברת)
**1.** מכפלה סקלרית – האיברים המעורבים מתאפסים כי וקטורי היחידה ניצבים:
$$\vec{\mathcal E}\cdot\vec{\mathcal E}=A_1^2\cos^2(\omega t+\phi_1)+A_2^2\cos^2(\omega t+\phi_2)+A_3^2\cos^2(\omega t+\phi_3)$$
**2.** ממוצע של איבר אחד:
$$\frac1T\int_0^TA_i^2\cos^2(\omega t+\phi_i)\,dt=\frac{A_i^2}{T}\int_0^T\frac{1+\cos(2\omega t+2\phi_i)}{2}dt=\frac{A_i^2}{T}\cdot\frac{T}{2}+0=\frac{A_i^2}{2}$$
(האינטגרל של $\cos(2\omega t+2\phi_i)$ על מחזור שלם הוא 0 – שני מחזורים שלמים שלו.)
**3.** סוכמים:
$$\overline{|\vec{\mathcal E}|^2}=\frac12\left(A_1^2+A_2^2+A_3^2\right)$$
**4.** הפאזור: $\tilde E=\hat xA_1e^{j\phi_1}+\hat yA_2e^{j\phi_2}+\hat zA_3e^{j\phi_3}$, ולכן
$$\tilde E\cdot\tilde E^*=A_1^2+A_2^2+A_3^2=|\tilde E|^2$$
✅ $\overline{|\vec{\mathcal E}|^2}=\frac12\left(A_1^2+A_2^2+A_3^2\right)=\frac12|\tilde E|^2$ – **בלי תלות בפאזות** $\phi_i$. ∎

💡 **הרעיון:** כל רכיב תורם חצי מריבוע המשרעת שלו; האיברים המעורבים נעלמים כי הכיוונים ניצבים."""

S["99054ea6"] = r"""> ⚠️ הנתונים תלויים בתעודת הזהות שלך – כאן השיטה, עם הדוגמה מהשאלה (123456789).

### 📘 מה צריך לדעת קודם
- גל בזמן ב-$z=0$: $E_x=E_{0x}\cos(\omega t+\phi_x)$, $E_y=E_{0y}\cos(\omega t+\phi_y)$. "דיאגרמת קיטוב" = המסלול של הנקודה $(E_x,E_y)$ במשך מחזור אחד.
- זווית האליפסה: $\tan2\gamma=\frac{2E_{0x}E_{0y}\cos\Delta\phi}{E_{0x}^2-E_{0y}^2}$.

### ✍️ הדרך המלאה (כמו במחברת)
**דוגמה (ת"ז 123456789):** $\Delta\varphi=\varphi_x-\varphi_y=89-12=77^\circ$, $\frac{E_{0x}}{E_{0y}}=5$. בוחרים $E_{0y}=1$, $E_{0x}=5$, $\varphi_y=0$, $\varphi_x=77^\circ$.
1. וקטור זמן על מחזור אחד, למשל 200 נקודות של $\omega t$ מ-0 עד $2\pi$.
2. מחשבים $E_x=5\cos(\omega t+77^\circ)$ ו-$E_y=\cos(\omega t)$ (להמיר מעלות לרדיאנים!).
3. משרטטים $E_y$ מול $E_x$, צירים בקנה מידה שווה, וחץ / נקודה ב-$t=0$ כדי להראות את כיוון הסיבוב.

**מה צפוי לצאת:** אליפסה (משרעות שונות, $\Delta\phi\ne0,\pm\pi$):
$$\tan2\gamma=\frac{2\cdot5\cdot1\cdot\cos77^\circ}{25-1}=\frac{2.25}{24}=0.094\ \Rightarrow\ \gamma\approx2.7^\circ$$
✅ אליפסה כמעט אופקית ($E_{0x}$ גדול פי 5). $\phi_y-\phi_x=-77^\circ<0$ ⇐ כיוון סיבוב CW לפי מוסכמת התרגול (גל ב-$+z$). אם $|\Delta\varphi|$ יוצא $0^\circ$ או $180^\circ$ – קו ישר; אם $90^\circ$ ויחס 1 – מעגל.

💡 **הרעיון:** משרטטים $E_y(t)$ מול $E_x(t)$, ובודקים את הזווית והכיוון מול הנוסחאות."""

ADD = {
    "451e3d9e": r"""

**ג. המשמעות הפיזיקלית (משפט פוינטינג):**
- **החלק הממשי** קטן כמו $e^{-2\alpha z}$: ההספק הממוצע שזורם דרך מישור $z$ קטן עם המרחק. לפי משפט פוינטינג, ההפרש בין ההספק שנכנס לנפח לבין זה שיוצא ממנו הוא ההספק שנבלע בו – הפסדי ההולכה $\frac\sigma2|\tilde E|^2$ (והפסדים דיאלקטריים): $-\frac{d}{dz}\left(\tfrac12\text{Re}\{S_z\}\right)=$ ההספק שנבלע ליחידת נפח. ✅ הדעיכה = האנרגיה שהופכת לחום.
- **החלק המדומה** ($\propto\sin\theta_\eta$) הוא הספק ריאקטיבי: $2\omega(W_m-W_e)$ – אנרגיה שנאגרת ומוחזרת בכל מחזור בין השדה המגנטי לחשמלי, בלי לזרום הלאה. ✅ המקור: בתווך עם הפסדים $\eta$ מרוכב, ולכן $\tilde H$ מפגר אחרי $\tilde E$ בזווית $\theta_\eta$, וצפיפות האנרגיה המגנטית גדולה מהחשמלית ($W_m>W_e$). בתווך בלי הפסדים $\theta_\eta=0$ ⇐ אין חלק מדומה.""",
    "e79b3205": r"""

**תוצאה:** ✅ $\Gamma_\parallel\approx-0.28$.
> הערה: הנתונים לא לגמרי עקביים – $\eta_2=188.5\,\Omega$ פירושו $n_2=2$, ולפי סנל $\sin\theta_t=\frac{\sin30^\circ}{2}=0.25$, כלומר $\theta_t=14.5^\circ$ ולא $15^\circ$. עם $14.5^\circ$: $\Gamma_\parallel=-0.277$ – כמעט אותו דבר.""",
    "51a7311b": r"""

**תוצאה:** ✅ $\tilde{\vec H}=\frac{\beta}{\omega\mu}E_0e^{-j\beta z}\hat y=\frac{E_0}{\eta}e^{-j\beta z}\hat y$, כאשר $\frac{\beta}{\omega\mu}=\frac{1}{\eta}$. מספרית: $\frac{1}{\omega\mu}=\frac{1}{10^9\cdot4\pi\cdot10^{-7}}=7.96\cdot10^{-4}\ \frac{1}{\Omega\cdot\text{rad/m}}$ – צריך גם את $\beta$ (או $\varepsilon$) כדי לקבל מספר. בריק: $\beta=\frac{\omega}{c}=3.33\ \frac{\text{rad}}{\text{m}}$ ⇐ $\tilde H_y=\frac{E_0}{377}e^{-j\beta z}$.""",
}

# b751881a: the phase is in radians, and very sensitive to k (practice 4 warning)
FIX_B75 = ("$$\n\\cos(-248.45^\\circ) \\approx -0.967, \\quad \\vec h_t\\approx-0.84\\,\\hat y\\;A/m\n$$",
           "$$\n\\cos(-248.45\\ \\text{rad}) \\approx -0.967, \\quad \\vec h_t\\approx-0.84\\,\\hat y\\;A/m\n$$\n"
           "> ⚠️ הפאזה ברדיאנים (לא מעלות). היא גדולה מאוד (≈248 rad), ולכן רגישה לעיגולים: עם $c=2.998\\cdot10^8$ במקום $3\\cdot10^8$ "
           "יוצא $k_2=29.64$ ו-$\\vec h_t\\approx-0.79\\,\\hat y$. בחישוב כזה – לא לעגל את $k$.")

FINE_KEEP_FLAG = ["af6d8cbf", "c5ef4b9c", "d6580bc6"]  # solved well; flagged because the source sheet itself is in doubt
FINE = ["1d44efec", "2c50fbdd", "dab6987d"]


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "waves_todo.json").read_text(encoding="utf-8"))}
    out = []
    for k, sol in S.items():
        x = xs[k]
        fx = {"id": x["id"], "title": x["title"], "solution_md": sol + DONE, "uncertain": k == "812f92a7"}
        if k == "812f92a7":
            assert r"3.46\hat{x} - 3\hat{z}$ (או בהתאמה" in x["question_md"]
            fx["question_md"] = x["question_md"].replace(r"\vec{E}_{i0} = 3.46\hat{x} - 3\hat{z}$ (או בהתאמה לניצבות: משרעת כוללת $E_{i0} = 4\,\frac{\text{V}}{\text{m}}$)",
                                                         r"\vec{E}_{i0} = 3.46\hat{x} - 2\hat{z}$ (משרעת כוללת $E_{i0} = 4\,\frac{\text{V}}{\text{m}}$; בנוסח השמור היה $-3\hat z$ – טעות הקלדה)")
        out.append(fx)
    for k, extra in ADD.items():
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + extra + DONE, "uncertain": False})
    x = xs["b751881a"]
    assert FIX_B75[0] in x["solution_md"]
    out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].replace(*FIX_B75).rstrip() + OK, "uncertain": False})
    for k in FINE:
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + OK, "uncertain": False})
    for k in FINE_KEEP_FLAG:
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": x["solution_md"].rstrip() + OK, "uncertain": True})
    (HERE.parent / "fix_2811_waves_hollow.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
