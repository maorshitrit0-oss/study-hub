"""Waves - practice sheet 1 (Maxwell and boundary conditions): checked against the PDF and its final answers,
re-solved from scratch, solutions written out in full (08/11/2026). Run: python waves_sheet1.py > waves_sheet1.json"""
import json

S = []

S.append({"id": "0f49ad90-516c-42f2-873c-beadd448e51d", "uncertain": False, "solution_md": r"""
### מה שואלים ואיך ניגשים
נותנים שדה חשמלי $\vec e$ ומבקשים את השדה המגנטי שמלווה אותו. הכלי: **חוק פאראדיי** $\nabla\times\vec e=-\mu\,\partial\vec h/\partial t$ – מחשבים רוטור של $\vec e$, ואז אינטגרל בזמן. אחר כך בודקים את שאר משוואות מקסוול (אמפר וגאוס).

### שלב 0: לכתוב את השדות בזמן (בלי Re)
$$\text{Re}\{E_0e^{j\theta}\}=E_0\cos\theta ,\qquad \cos(-x)=\cos x$$
$$\vec e_1=E_0\cos(\omega t-k_xx-k_yy)\,\hat z \qquad (\varphi_1\equiv\omega t-k_xx-k_yy)$$
$$\vec e_2=E_0\cos(\omega t+k_xx+k_yy)\,\hat z \qquad (\varphi_2\equiv\omega t+k_xx+k_yy)$$
גל 1 מתקדם בכיוון $+(k_x,k_y)$ (הפאזה $\omega t-\vec k\cdot\vec r$), וגל 2 בכיוון ההפוך.

### שלב 1: רוטור של שדה שיש לו רק רכיב $z$
$$\nabla\times(e_z\hat z)=\hat x\,\frac{\partial e_z}{\partial y}-\hat y\,\frac{\partial e_z}{\partial x}$$
לגל 1 (כלל השרשרת: $\frac{\partial}{\partial x}\cos\varphi_1=-\sin\varphi_1\cdot(-k_x)=k_x\sin\varphi_1$):
$$\frac{\partial e_{1z}}{\partial y}=k_yE_0\sin\varphi_1,\qquad \frac{\partial e_{1z}}{\partial x}=k_xE_0\sin\varphi_1$$
$$\nabla\times\vec e_1=E_0\sin\varphi_1\,(k_y\hat x-k_x\hat y)$$

### שלב 2: פאראדיי ואינטגרל בזמן
$$-\mu\frac{\partial\vec h_1}{\partial t}=E_0\sin\varphi_1(k_y\hat x-k_x\hat y)\ \Rightarrow\ \frac{\partial\vec h_1}{\partial t}=-\frac{E_0}{\mu}\sin\varphi_1(k_y\hat x-k_x\hat y)$$
$\int\sin(\omega t+c)\,dt=-\frac1\omega\cos(\omega t+c)$, ולכן (בלי רכיב קבוע בזמן):
$$\boxed{\vec h_1=\frac{E_0}{\mu\omega}\cos(\omega t-k_xx-k_yy)\,[k_y\hat x-k_x\hat y]}\ \left[\tfrac{\text{A}}{\text{m}}\right]$$
✅ זהה לתשובה הסופית בדף.

לגל 2 באותה דרך: $\frac{\partial e_{2z}}{\partial y}=-k_yE_0\sin\varphi_2$, $\frac{\partial e_{2z}}{\partial x}=-k_xE_0\sin\varphi_2$, לכן $\nabla\times\vec e_2=E_0\sin\varphi_2(-k_y\hat x+k_x\hat y)$ ו-
$$\boxed{\vec h_2=\frac{E_0}{\mu\omega}\cos(\omega t+k_xx+k_yy)\,[-k_y\hat x+k_x\hat y]}$$
**בדיקה בדרך אחרת:** בגל מישורי $\vec h=\frac1\eta\hat k\times\vec e$. לגל 2 $\hat k_2=-(k_x\hat x+k_y\hat y)/k$, ו-$\hat k_2\times\hat z=(k_x\hat y-k_y\hat x)/k$; עם $\eta=\omega\mu/k$ יוצא בדיוק אותו ביטוי. ✅

> ⚠️ בדף התשובות כתוב $\vec h_2=\frac{E_0}{\mu\omega}\cos(\omega t-k_xx-k_yy)[k_y\hat x+k_x\hat y]$. זה לא מתאים לגל 2 (הפאזה שלו $\omega t+k_xx+k_yy$, וגם הכיוון לא ניצב ל-$\vec k_2$: $(k_x,k_y)\cdot(k_y,k_x)\ne0$). כנראה טעות הקלדה – לשאול את המתרגל.

### שלב 3: האם הזוגות מקיימים את כל משוואות מקסוול?
**גאוס:** $\nabla\cdot\vec e_1=\partial_ze_{1z}=0$ ✅. $\nabla\cdot\vec h_1=\frac{E_0}{\mu\omega}[k_y\,\partial_x\cos\varphi_1-k_x\,\partial_y\cos\varphi_1]=\frac{E_0}{\mu\omega}[k_yk_x-k_xk_y]\sin\varphi_1=0$ ✅

**אמפר** (בלי זרמים): $\nabla\times\vec h_1=\varepsilon\,\partial\vec e_1/\partial t$. ל-$\vec h_1$ יש רק $x,y$ שתלויים ב-$x,y$, ולכן רק רכיב $z$:
$$(\nabla\times\vec h_1)_z=\frac{\partial h_y}{\partial x}-\frac{\partial h_x}{\partial y}=\frac{E_0}{\mu\omega}\left[-k_x\cdot k_x-k_y\cdot k_y\right]\sin\varphi_1=-\frac{E_0(k_x^2+k_y^2)}{\mu\omega}\sin\varphi_1$$
$$\varepsilon\frac{\partial e_{1z}}{\partial t}=-\varepsilon\omega E_0\sin\varphi_1$$
שווים רק אם
$$\boxed{k_x^2+k_y^2=\omega^2\mu\varepsilon=k^2}$$
(אותו תנאי יוצא לגל 2). **מסקנה:** שני הזוגות מקיימים את משוואות מקסוול **בתנאי** $k_x^2+k_y^2=\omega^2\mu\varepsilon$ – זה קשר הנפיצה (Dispersion) מההרצאה.

💡 **הרעיון:** $\vec e\to\vec h$ תמיד דרך פאראדיי (רוטור ואז אינטגרל בזמן); הבדיקה של "האם מקיים מקסוול" היא בעיקר אמפר, ושם יוצא התנאי על $k$.
"""})

S.append({"id": "feb73418-c4e9-45e5-8926-5d1fdd3fc1fa", "uncertain": False, "solution_md": r"""
### מה יש לנו
באזור $z<0$ (דיאלקטרי, $\sigma=0$): $\vec e=E_0\sin(\beta z)\sin(\omega t)\,\hat y$. באזור $z>0$ מוליך מושלם – שם אין שדה. זה **גל עומד** (מכפלה של פונקציית מקום בפונקציית זמן) – מה שנוצר כשגל פוגע ב-PEC ומוחזר.

### סעיף א: התנאי לקיום מקסוול
בתווך בלי מקורות כל רכיב מקיים את משוואת הגלים (מתקבלת מפאראדיי + אמפר):
$$\nabla^2\vec e-\mu\varepsilon\frac{\partial^2\vec e}{\partial t^2}=0$$
גוזרים:
$$\nabla^2\vec e=\frac{\partial^2 e_y}{\partial z^2}\hat y=-\beta^2E_0\sin(\beta z)\sin(\omega t)\hat y=-\beta^2\vec e$$
$$\frac{\partial^2\vec e}{\partial t^2}=-\omega^2\vec e$$
מציבים: $-\beta^2\vec e+\mu\varepsilon\omega^2\vec e=0$, ולכן
$$\boxed{\beta=\omega\sqrt{\mu\varepsilon}}$$
(בריק: $\beta=\omega/c$)
בנוסף $\nabla\cdot\vec e=\partial_ye_y=0$ ✅ (אין תלות ב-$y$).

### סעיף ב: השדה המגנטי (פאראדיי)
$$\nabla\times(e_y\hat y)=-\frac{\partial e_y}{\partial z}\hat x+\frac{\partial e_y}{\partial x}\hat z=-\beta E_0\cos(\beta z)\sin(\omega t)\,\hat x$$
$$-\mu\frac{\partial\vec h}{\partial t}=-\beta E_0\cos(\beta z)\sin(\omega t)\hat x\ \Rightarrow\ \frac{\partial\vec h}{\partial t}=\frac{\beta E_0}{\mu}\cos(\beta z)\sin(\omega t)\hat x$$
אינטגרל בזמן ($\int\sin\omega t\,dt=-\frac1\omega\cos\omega t$):
$$\boxed{\vec h=-\hat x\,\frac{E_0\beta}{\mu\omega}\cos(\omega t)\cos(\beta z)}\ \left[\tfrac{\text{A}}{\text{m}}\right]$$
✅ זהה לתשובה בדף.

**שימו לב:** ב-$z=0$ השדה החשמלי מתאפס ($\sin0=0$) – בדיוק תנאי השפה של PEC ($E_t=0$) – אבל השדה המגנטי מקסימלי ($\cos0=1$).

### סעיף ג: זרם השפה על המוליך
תנאי השפה: $\hat n\times(\vec h_1-\vec h_2)=\vec J_s$, כאשר **$\hat n$ מצביע מהמוליך אל האזור שבו יש שדה**. כאן השדה ב-$z<0$ והמוליך ב-$z>0$, ולכן $\hat n=-\hat z$, ובתוך המוליך $\vec h_2=0$:
$$\vec J_s=(-\hat z)\times\vec h(z=0)=(-\hat z)\times\left(-\hat x\frac{E_0\beta}{\mu\omega}\cos\omega t\right)=(\hat z\times\hat x)\frac{E_0\beta}{\mu\omega}\cos\omega t$$
ו-$\hat z\times\hat x=\hat y$:
$$\boxed{\vec J_s=\hat y\,\frac{E_0\beta}{\mu\omega}\cos(\omega t)}\ \left[\tfrac{\text{A}}{\text{m}}\right]$$
✅ זהה לדף (שם כתוב גם $\cos\beta z$, שב-$z=0$ שווה 1).

> ⚠️ הגרסה הקודמת כאן נתנה $-\hat y$ – כי לקחה $\hat n=+\hat z$. הכלל: הנורמל יוצא **מהמוליך אל השדה**.

💡 **הרעיון:** גל עומד מול PEC: $E$ מתאפס על הקיר, $H$ מקסימלי שם, והזרם על הקיר הוא $\hat n\times\vec H$.
"""})

S.append({"id": "d6580bc6-4223-4d8a-9542-cd487ae1ab80", "uncertain": True, "solution_md": r"""
### מה מבקשים
להוכיח משוואת גלים בתווך "כירלי" – תווך שבו $\vec D$ תלוי גם ב-$\vec H$ (או $\vec B$) ו-$\vec H$ תלוי גם ב-$\vec E$. הדרך הקבועה לכל "הוכח משוואת גלים": **רוטור על פאראדיי ← להציב את אמפר ← הזהות $\nabla\times\nabla\times\vec E=\nabla(\nabla\cdot\vec E)-\nabla^2\vec E$**.

### הכלים (פאזורים, $e^{j\omega t}$, בלי מקורות)
$$\nabla\times\tilde E=-j\omega\tilde B\qquad(1)\qquad\qquad \nabla\times\tilde H=j\omega\tilde D\qquad(2)$$

### ⚠️ לפני שמתחילים – בעיה בנוסח
כמו שהקשרים מודפסים בדף ($\tilde D=\varepsilon\tilde E+j\xi\tilde H$ וגם $\tilde H=\frac1\mu\tilde B+j\xi\tilde E$) היחידות לא מסתדרות: ב-$\vec D$ המקדם $\xi$ צריך יחידות של [s/m], וב-$\vec H$ יחידות של [S] – אותו $\xi$ לא יכול להיות שניהם, והחישוב לא מגיע לתוצאה המבוקשת. בספרות התווך הכירלי כתוב עם $\vec B$ בשתי המשוואות:
$$\tilde D=\varepsilon\tilde E+j\xi\tilde B,\qquad \tilde H=\frac1\mu\tilde B+j\xi\tilde E$$
נפתור עם הצורה הזו (כנראה זו הכוונה).

### שלב 1: לבטא הכל דרך $\tilde E$
מ-(1): $\tilde B=\frac{j}{\omega}\nabla\times\tilde E$ (כי $\frac{1}{-j}=j$).

לכן
$$\tilde H=\frac{j}{\omega\mu}\nabla\times\tilde E+j\xi\tilde E,\qquad \tilde D=\varepsilon\tilde E+j\xi\cdot\frac{j}{\omega}\nabla\times\tilde E=\varepsilon\tilde E-\frac{\xi}{\omega}\nabla\times\tilde E$$

### שלב 2: להציב באמפר (2)
אגף שמאל: $\nabla\times\tilde H=\frac{j}{\omega\mu}\nabla\times\nabla\times\tilde E+j\xi\nabla\times\tilde E$

אגף ימין: $j\omega\tilde D=j\omega\varepsilon\tilde E-j\xi\nabla\times\tilde E$

משווים, מחלקים ב-$j$ ומכפילים ב-$\omega\mu$:
$$\nabla\times\nabla\times\tilde E+\omega\mu\xi\nabla\times\tilde E=\omega^2\mu\varepsilon\tilde E-\omega\mu\xi\nabla\times\tilde E$$
$$\nabla\times\nabla\times\tilde E=k^2\tilde E-2\omega\mu\xi\,\nabla\times\tilde E\qquad(k^2=\omega^2\mu\varepsilon)$$

### שלב 3: הזהות והדיברגנץ
$\nabla\cdot\tilde D=0$ ו-$\nabla\cdot\tilde B=0$ (בלי מקורות), ולכן $\varepsilon\nabla\cdot\tilde E=\nabla\cdot\tilde D-j\xi\nabla\cdot\tilde B=0$, כלומר $\nabla\cdot\tilde E=0$. אז
$$\nabla\times\nabla\times\tilde E=\nabla(\nabla\cdot\tilde E)-\nabla^2\tilde E=-\nabla^2\tilde E$$
ומקבלים:
$$\boxed{\nabla^2\tilde E+k^2\tilde E-2\omega\mu\xi\,\nabla\times\tilde E=0}$$

### על הסימן של האיבר האחרון
בדף כתוב $+2\omega\mu\xi\nabla\times\tilde E$. הסימן תלוי במוסכמה: עם $e^{j\omega t}$ (הנדסה, כמו בקורס) יוצא מינוס; אם הקשרים לקוחים מספר פיזיקה עם $e^{-i\omega t}$ (שם $i=-j$), אותו תווך נותן פלוס. המבנה של ההוכחה זהה.

> ⚠️ לא בטוח מה הייתה כוונת המתרגל בנוסח (H או B, ואיזו מוסכמת זמן) – כדאי לשאול. הדרך (פאראדיי ← אמפר ← זהות הרוטור הכפול) היא מה שצריך לדעת.

💡 **הרעיון:** בכל "הוכח משוואת גלים": מבטאים הכל דרך $\tilde E$, רוטור כפול, והזהות $\nabla\times\nabla\times=\nabla\nabla\cdot-\nabla^2$. האיבר $\nabla\times\tilde E$ שנשאר הוא מה שהופך את התווך לכירלי (מסובב קיטוב).
"""})

S.append({"id": "af6d8cbf-4074-4408-8426-578bef778106", "uncertain": True, "solution_md": r"""
### מה יש לנו
הממשק הוא המישור $y=0$. **הנורמל** מתווך 2 (למטה) לתווך 1 (למעלה): $\hat n=\hat y$. הרכיב **הנורמלי** הוא $y$; הרכיבים **המשיקים** הם $x$ ו-$z$. על הממשק זורם זרם משטחי $\vec J_s=j_0\hat z$.

### שלב 1: הרכיב הנורמלי – מוצאים את $\mu_2$
$\nabla\cdot\vec B=0$ נותן: $B$ הנורמלי רציף.
$$B_{1y}=B_{2y}\ \Rightarrow\ \mu_1H_{1y}=\mu_2H_{2y}\ \Rightarrow\ \boxed{\mu_2=\frac{H_{1y}}{H_{2y}}\,\mu_1}$$

### שלב 2: הרכיבים המשיקים – מוצאים את $H_{1x},H_{1z}$
$$\hat n\times(\vec H_1-\vec H_2)=\vec J_s,\qquad \hat n=\hat y$$
מכפלות: $\hat y\times\hat x=-\hat z$, $\hat y\times\hat y=0$, $\hat y\times\hat z=\hat x$. לכן
$$\hat y\times(\vec H_1-\vec H_2)=(H_{1z}-H_{2z})\,\hat x-(H_{1x}-H_{2x})\,\hat z$$
משווים ל-$j_0\hat z$ רכיב-רכיב:
- רכיב $\hat x$: $H_{1z}-H_{2z}=0\Rightarrow H_{1z}=H_{2z}$
- רכיב $\hat z$: $-(H_{1x}-H_{2x})=j_0\Rightarrow H_{1x}=H_{2x}-j_0$

$$\boxed{\vec H_1=(H_{2x}-j_0)\,\hat x+H_{1y}\,\hat y+H_{2z}\,\hat z}\ \left[\tfrac{\text{A}}{\text{m}}\right]$$

**בדיקת שכל:** זרם בכיוון $z$ יוצר קפיצה ברכיב ה-$H$ שניצב לו ומשיק למשטח – כלומר ב-$H_x$ – ולא ב-$H_z$ (כמו תיל: השדה המגנטי מסתובב סביב הזרם, לא לאורכו).

> ⚠️ **בדף התשובות כתוב** $\mu_2=-\frac{H_{1y}}{H_{2y}}\mu_1$ ו-$\vec h_1=H_{2x}\hat x+H_{1y}\hat y+(j_0+H_{2z})\hat z$. לפי תנאי השפה זה לא יכול להיות: (1) $B_n$ רציף נותן $\mu_2$ בלי מינוס (מינוס היה נותן $\mu_2<0$ כשהרכיבים באותו סימן); (2) זרם ב-$\hat z$ לא משנה את $H_z$. אפשרות: בדף התכוונו לזרם בכיוון $\hat x$, או שזו טעות. **לשאול את המתרגל לפני המבחן.**

💡 **הרעיון:** בכל תרגיל ממשק: מזהים נורמל, נורמלי ← $B_n$ (ו-$D_n$) רציף; משיקי ← $\hat n\times(\vec H_1-\vec H_2)=\vec J_s$, ופותחים רכיב-רכיב.
"""})

S.append({"id": "3e428ce1-a105-4877-95c6-ee219905c849", "uncertain": False, "solution_md": r"""
### סימונים
$u\equiv kr$. השדות: $h_\phi=h_0\frac{\sin\theta}{u}\left(\frac{\sin u}{u}-\cos u\right)$, $e_r=h_0\frac{2\eta\cos\theta}{u^2}\left(\frac{\sin u}{u}-\cos u\right)$, $e_\theta=h_0\frac{-\eta\sin\theta}{u^2}F(u)$, כאשר $F(u)=\frac{u^2-1}{u}\sin u+\cos u$.

דיברגנץ כדורי:
$$\nabla\cdot\vec A=\frac1{r^2}\frac{\partial}{\partial r}(r^2A_r)+\frac1{r\sin\theta}\frac{\partial}{\partial\theta}(\sin\theta\,A_\theta)+\frac1{r\sin\theta}\frac{\partial A_\phi}{\partial\phi}$$

### סעיף א1: $\nabla\cdot\vec h=0$
ל-$\vec h$ יש רק רכיב $\phi$, והוא לא תלוי ב-$\phi$ ⇐ שני האיברים הראשונים אפס (אין $h_r,h_\theta$) והשלישי $\partial_\phi h_\phi=0$. ✅

### סעיף א2: $\nabla\cdot\vec e=0$
**איבר רדיאלי.** $r^2e_r=\frac{2\eta h_0\cos\theta}{k^2}\left(\frac{\sin u}{u}-\cos u\right)$, ו-$\frac{\partial}{\partial r}=k\frac{d}{du}$:
$$\frac{d}{du}\left(\frac{\sin u}{u}-\cos u\right)=\frac{u\cos u-\sin u}{u^2}+\sin u=\frac{u\cos u-\sin u+u^2\sin u}{u^2}$$
$$\frac1{r^2}\frac{\partial(r^2e_r)}{\partial r}=\frac{k^2}{u^2}\cdot\frac{2\eta h_0\cos\theta}{k^2}\cdot k\,\frac{u\cos u-\sin u+u^2\sin u}{u^2}=\frac{2\eta h_0k\cos\theta}{u^4}\,(u\cos u-\sin u+u^2\sin u)$$
**איבר זוויתי.** $\sin\theta\,e_\theta=-\frac{\eta h_0\sin^2\theta}{u^2}F$, ו-$\frac{\partial}{\partial\theta}\sin^2\theta=2\sin\theta\cos\theta$:
$$\frac1{r\sin\theta}\frac{\partial(\sin\theta e_\theta)}{\partial\theta}=\frac{k}{u\sin\theta}\cdot\left(-\frac{2\eta h_0\sin\theta\cos\theta}{u^2}F\right)=-\frac{2\eta h_0k\cos\theta}{u^4}\,(uF)$$
ו-$uF=(u^2-1)\sin u+u\cos u=u^2\sin u-\sin u+u\cos u$ – **בדיוק** אותו ביטוי כמו באיבר הרדיאלי. הסכום אפס:
$$\nabla\cdot\vec e=0$$ ✅

### סעיף ב: $e_\theta$ על השפה ⇒ התנאי על $ka$
על משטח של PEC הרכיב המשיק של $\vec E$ מתאפס. על כדור הנורמל הוא $\hat r$, והמשיקים הם $\theta,\phi$. $e_\phi=0$ ממילא, אז נשאר $e_\theta(r=a)=0$:
$$\frac{k^2a^2-1}{ka}\sin ka+\cos ka=0$$
מכפילים ב-$\frac{ka}{\cos ka}$:
$$(k^2a^2-1)\tan ka+ka=0\ \Rightarrow\ \boxed{\tan ka=\frac{ka}{1-k^2a^2}}$$
(זו משוואה שקובעת באילו תדרים השדה הזה יכול להתקיים בכדור – תדרי תהודה של חלל.)

### סעיף ג: זרם השפה
$$\vec J_s=\hat n\times\vec H\big|_{r=a}$$
כאשר $\hat n$ מצביע מהמוליך אל האזור שבו יש שדה.
השדה בפנים והמוליך מבחוץ ⇐ $\hat n=-\hat r$. מכפלה: $\hat r\times\hat\phi=-\hat\theta$ (כי $\hat\theta\times\hat\phi=\hat r$ ⇐ $\hat\phi\times\hat r=\hat\theta$ ⇐ $\hat r\times\hat\phi=-\hat\theta$). לכן
$$\vec J_s=(-\hat r)\times h_\phi\hat\phi=+h_\phi(a)\,\hat\theta=h_0\frac{\sin\theta}{ka}\left(\frac{\sin ka}{ka}-\cos ka\right)\hat\theta\ \left[\tfrac{\text{A}}{\text{m}}\right]$$

> ⚠️ בדף התשובות (ובגרסה הקודמת כאן) $\vec J_s=-h_0\frac{\sin\theta}{ka}(\dots)\hat\theta$ – זה יוצא אם לוקחים $\hat n=+\hat r$ (החוצה). בשאלה 2 באותו דף הנורמל נלקח מהמוליך אל השדה ($-\hat z$), ולפי אותו כלל כאן $\hat n=-\hat r$ והסימן חיובי. הגודל זהה – לשאול את המתרגל איזה כיוון נורמל הוא רוצה.

💡 **הרעיון:** דיברגנץ כדורי עם הצבה $u=kr$ (מסדר את הנגזרות); PEC ⇐ $E$ משיק $=0$ על השפה ⇐ משוואת תהודה; $\vec J_s=\hat n\times\vec H$.
"""})

S.append({"id": "7a50acd4-1a8c-4949-b99a-09dadf30a9ab", "uncertain": False, "solution_md": r"""
### שלב 1: חוק פאראדיי בצורה דיפרנציאלית
$$\nabla\times\vec e=-\frac{\partial\vec b}{\partial t}$$
$\vec e=e_x\hat x$, ומכיוון ש-$\vec b$ תלוי רק ב-$z$, גם $e_x=e_x(z,t)$. רוטור:
$$\nabla\times(e_x\hat x)=\frac{\partial e_x}{\partial z}\hat y-\frac{\partial e_x}{\partial y}\hat z=\frac{\partial e_x}{\partial z}\hat y$$
אגף ימין:
$$-\frac{\partial\vec b}{\partial t}=-B_0z\,\frac{\partial}{\partial t}\cos\omega t\;\hat y=\omega B_0z\sin(\omega t)\,\hat y$$
משווים רכיבי $y$:
$$\frac{\partial e_x}{\partial z}=\omega B_0z\sin\omega t$$
אינטגרל לפי $z$ (קבוע האינטגרציה 0 – אין שדה קבוע):
$$\boxed{\vec e=\omega B_0\frac{z^2}{2}\sin(\omega t)\,\hat x}\ \left[\tfrac{\text{V}}{\text{m}}\right]$$
✅ זהה לתשובה בדף.

### שלב 2: בדיקה בצורה האינטגרלית
$$\oint_C\vec e\cdot d\vec\ell=-\frac{d}{dt}\int_S\vec b\cdot d\vec s$$
הלולאה: מלבן במישור $xz$ בין $x=0..a$, $z=0..b$. בוחרים נורמל $d\vec s=\hat y\,dx\,dz$ (כמו $\vec b$). לפי כלל יד ימין סביב $\hat y$ ההקפה היא: $(0,0)\to(0,b)$ [לאורך $+z$] $\to(a,b)$ [לאורך $+x$] $\to(a,0)$ [לאורך $-z$] $\to(0,0)$ [לאורך $-x$]. (בדיקה: $\hat z\times\hat x=\hat y$.)

**אגף שמאל**, צלע אחר צלע:
- צלעות לאורך $z$: $\vec e\parallel\hat x$ ו-$d\vec\ell\parallel\hat z$ ⇐ $\vec e\cdot d\vec\ell=0$.
- צלע עליונה $z=b$, לאורך $+x$: $\int_0^a\omega B_0\frac{b^2}2\sin\omega t\,dx=a\,\omega B_0\frac{b^2}{2}\sin\omega t$.
- צלע תחתונה $z=0$: $e_x(0)=0$.

$$\oint\vec e\cdot d\vec\ell=\frac{a\,b^2}{2}\,\omega B_0\sin\omega t$$
**אגף ימין:** השטף
$$\Phi=\int_0^a\!\!\int_0^bB_0z\cos\omega t\,dz\,dx=\frac{a\,b^2}{2}B_0\cos\omega t\ \Rightarrow\ -\frac{d\Phi}{dt}=\frac{a\,b^2}{2}B_0\,\omega\sin\omega t$$
שני האגפים שווים ✅ – התשובה נכונה.

💡 **הרעיון:** הדיפרנציאלי נותן את השדה; האינטגרלי (סטוקס) בודק אותו: מתח סביב לולאה = מינוס קצב השינוי של השטף דרכה. הכיוון של ההקפה נקבע מכיוון $d\vec s$ לפי יד ימין.
"""})

S.append({"id": "f9bdd22c-6147-47cc-ab17-3263203314e0", "uncertain": False, "solution_md": r"""
### איך בודקים זוג שדות
באוויר בלי זרמים ובלי מטענים צריך את ארבע המשוואות:
$$\nabla\times\vec e=-\mu_0\frac{\partial\vec h}{\partial t},\qquad \nabla\times\vec h=\varepsilon_0\frac{\partial\vec e}{\partial t},\qquad \nabla\cdot\vec e=0,\qquad \nabla\cdot\vec h=0$$
בכל הסעיפים $\vec e=e_x(z,t)\hat x$, $\vec h=h_y(z,t)\hat y$, ולכן הדיברגנצים אפס אוטומטית ($e_x$ לא תלוי ב-$x$, $h_y$ לא תלוי ב-$y$), והרוטורים:
$$\nabla\times\vec e=\frac{\partial e_x}{\partial z}\hat y,\qquad \nabla\times\vec h=-\frac{\partial h_y}{\partial z}\hat x$$
עזר: $\mu_0=4\pi\cdot10^{-7}$, $\varepsilon_0=\frac{10^{-9}}{36\pi}$, $\omega=6\pi\cdot10^8$.

### א. $e_x=10\cos(2\pi z)\cos\omega t$, $h_y=\frac1{12\pi}\sin(2\pi z)\sin\omega t$
**פאראדיי:** $\frac{\partial e_x}{\partial z}=-20\pi\sin(2\pi z)\cos\omega t$.
$-\mu_0\frac{\partial h_y}{\partial t}=-4\pi\cdot10^{-7}\cdot\frac{6\pi\cdot10^8}{12\pi}\sin(2\pi z)\cos\omega t=-20\pi\sin(2\pi z)\cos\omega t$ ✅

**אמפר:** $-\frac{\partial h_y}{\partial z}=-\frac{2\pi}{12\pi}\cos(2\pi z)\sin\omega t=-\frac16\cos(2\pi z)\sin\omega t$.
$\varepsilon_0\frac{\partial e_x}{\partial t}=-10\,\varepsilon_0\,\omega\cos(2\pi z)\sin\omega t=-10\cdot\frac{10^{-9}}{36\pi}\cdot6\pi\cdot10^8\,(\dots)=-\frac16(\dots)$ ✅

**מקיים** ✅ (זה גל עומד בריק: $k=\omega/c=2\pi$).

### ב. $e_x=t-z\sqrt{\mu_0\varepsilon_0}$, $h_y=\sqrt{\varepsilon_0/\mu_0}\,(t-z\sqrt{\mu_0\varepsilon_0})$
**פאראדיי:** $\frac{\partial e_x}{\partial z}=-\sqrt{\mu_0\varepsilon_0}$; $\ -\mu_0\frac{\partial h_y}{\partial t}=-\mu_0\sqrt{\varepsilon_0/\mu_0}=-\sqrt{\mu_0\varepsilon_0}$ ✅

**אמפר:** $-\frac{\partial h_y}{\partial z}=\sqrt{\varepsilon_0/\mu_0}\cdot\sqrt{\mu_0\varepsilon_0}=\varepsilon_0$; $\ \varepsilon_0\frac{\partial e_x}{\partial t}=\varepsilon_0$ ✅

**מקיים** ✅ (כל פונקציה של $t-z/c$ היא גל שמתקדם ב-$+z$ במהירות $c$, ו-$e/h=\eta_0$).

### ג. $e_x=z^2\sin\omega t$, $h_y=-\frac{\omega\varepsilon_0}{3}z^3\cos\omega t$
**אמפר:** $-\frac{\partial h_y}{\partial z}=\omega\varepsilon_0z^2\cos\omega t$; $\ \varepsilon_0\frac{\partial e_x}{\partial t}=\varepsilon_0\omega z^2\cos\omega t$ ✅ (זה מתקיים)

**פאראדיי:** $\frac{\partial e_x}{\partial z}=2z\sin\omega t$, אבל
$-\mu_0\frac{\partial h_y}{\partial t}=-\mu_0\cdot\left(-\frac{\omega\varepsilon_0}{3}z^3\right)(-\omega\sin\omega t)=-\frac{\mu_0\varepsilon_0\omega^2}{3}z^3\sin\omega t$
$2z\ne-\frac{\omega^2}{3c^2}z^3$ ❌

**לא מקיים** – משוואה אחת לא מספיקה; צריך את שתיהן.

💡 **הרעיון:** "האם מקיים מקסוול" = לבדוק **גם** פאראדיי **וגם** אמפר (וגם דיברגנצים). בסעיף ג אמפר מתקיים ופאראדיי לא – מלכודת נפוצה.
"""})

print(json.dumps(S, ensure_ascii=False, indent=1))
