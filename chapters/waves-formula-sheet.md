## 🧭 מה שואלים ← מה עושים (לפי התרגילים שנפתרו)
| נותנים / שואלים | הדרך | מקור |
|---|---|---|
| שדות $\vec D,\vec H$ – "האם מקיימים מקסוול?" | $\nabla\times$, $\nabla\cdot$ לכל שדה, ולהשוות ל-$\partial/\partial t$, $\vec J=\sigma\vec E$, $\rho$ | ת1 |
| $\vec E(z,t)$ – מצא $\vec B,\vec H$ | $\nabla\times\vec E=-\partial\vec B/\partial t$ ← אינטגרל בזמן ← $\vec H=\vec B/\mu$ | ת1 |
| $\vec E$ בתוך/מחוץ לכדור – מטען נפחי/משטחי | $\rho=\varepsilon\,\nabla\cdot\vec E$ ;  $\rho_s=\varepsilon_0(E_{out,r}-E_{in,r})\big|_{r=R}$ | ה1 |
| "האם השדה משמר?" | $\nabla\times\vec E=0 \iff \oint\vec E\cdot d\vec\ell=0$ | ה1 |
| $\cos(\omega t-\alpha y-\beta z)$ – תנאי על הקבועים | הלמהולץ: $\alpha^2+\beta^2=k^2=\omega^2\mu\varepsilon$ | ה1 |
| $f$ ו-$\lambda$ בתווך – מצא $k,v_p,\varepsilon_r,\eta$ | $k=\frac{2\pi}{\lambda}$, $v_p=\lambda f$, $\varepsilon_r=(c/v_p)^2$, $\eta=\eta_0/\sqrt{\varepsilon_r}$ | ה1 |
| $f,\sigma,\varepsilon_r$ – סווג תווך, $\alpha,\beta,\delta,\eta$ | **קודם** $x=\frac{\sigma}{\omega\varepsilon}$ ← טבלת התווכים (§5) | ת2 |
| פאזור עם $e^{-j(k_xx+k_yy+k_zz)}$ – רכיב חסר | $k_x^2+k_y^2+k_z^2=k^2$ ;  $\vec k\cdot\vec E_0=0$ | ה3 |
| גל בריק: כיוון, משרעת, "מקסימום ב-$t=0,\ z=z_0$" | $\phi=kz_0$ בתוך $\cos(\omega t-kz+\phi)$ ;  $\vec H=\frac1{\eta_0}\hat k\times\vec E$ | ה3 |
| תווך הפסדי: $E$ במרחק $z$, ביטוי ל-$\vec H$ | $E_0e^{-\alpha z}$ ;  $\vec H$ עם $\eta$ **מרוכב** (מוסיף פאזה $\theta_\eta$) | ה2 |
| פאזור $\tilde E$ – מצא $\vec h(t)$ וסוג קיטוב | $\tilde H=\frac1\eta\hat k\times\tilde E$ ← $\text{Re}\{\tilde He^{j\omega t}\}$ ← $\Delta\phi$ (§7) | ת3 |
| $E_{0x},E_{0y},\Delta\phi$ – זווית האליפסה | $\tan2\theta$ (§7) – **לשים לב לרביע** | ת2-3 |
| גל פוגע במשטח – החזרה/העברה | $\Gamma,\ T$ (§8) | ה3 |
| ממוצע זמני / הספק | $\tfrac12\tilde E\cdot\tilde E^*$ ;  $\tfrac12\text{Re}\{\tilde E\times\tilde H^*\}$ | ה2-3 |

## 1. כלים וקטוריים (ה1, ת1)
$$\vec A\cdot\vec B=A_xB_x+A_yB_y+A_zB_z=|\vec A||\vec B|\cos\varphi \qquad |\vec A|=\sqrt{A_x^2+A_y^2+A_z^2}$$
$$\vec A\times\vec B=\begin{vmatrix}\hat x&\hat y&\hat z\\A_x&A_y&A_z\\B_x&B_y&B_z\end{vmatrix},\quad |\vec A\times\vec B|=|\vec A||\vec B|\sin\varphi$$
$$\text{proj}_{\vec C}\vec A=\frac{\vec A\cdot\vec C}{|\vec C|^2}\vec C$$
$$\nabla\Phi=\partial_x\Phi\,\hat x+\partial_y\Phi\,\hat y+\partial_z\Phi\,\hat z \qquad \nabla\cdot\vec A=\partial_xA_x+\partial_yA_y+\partial_zA_z$$
$$\nabla\times\vec A=\hat x(\partial_yA_z-\partial_zA_y)-\hat y(\partial_xA_z-\partial_zA_x)+\hat z(\partial_xA_y-\partial_yA_x)$$
$$\nabla^2\Phi=\partial_x^2\Phi+\partial_y^2\Phi+\partial_z^2\Phi \qquad \nabla\times(\nabla\times\vec E)=\nabla(\nabla\cdot\vec E)-\nabla^2\vec E$$
סטוקס: $\int_S(\nabla\times\vec A)\cdot d\vec s=\oint_C\vec A\cdot d\vec\ell$ · גאוס: $\int_V\nabla\cdot\vec A\,dv=\oint_S\vec A\cdot d\vec s$

**גלילי** $(\rho,\varphi,z)$: $x=\rho\cos\varphi,\ y=\rho\sin\varphi$ · $\nabla\cdot\vec A=\frac1\rho\partial_\rho(\rho A_\rho)+\frac1\rho\partial_\varphi A_\varphi+\partial_zA_z$

**כדורי** $(r,\theta,\varphi)$: $x=r\sin\theta\cos\varphi,\ y=r\sin\theta\sin\varphi,\ z=r\cos\theta$
$$\nabla\cdot\vec A=\frac1{r^2}\partial_r(r^2A_r)+\frac1{r\sin\theta}\partial_\theta(\sin\theta\,A_\theta)+\frac1{r\sin\theta}\partial_\varphi A_\varphi$$
$$\nabla\times\vec A=\frac{1}{r\sin\theta}\left[\partial_\theta(A_\varphi\sin\theta)-\partial_\varphi A_\theta\right]\hat r$$
$$+\frac1r\left[\frac1{\sin\theta}\partial_\varphi A_r-\partial_r(rA_\varphi)\right]\hat\theta+\frac1r\left[\partial_r(rA_\theta)-\partial_\theta A_r\right]\hat\varphi$$
> בלי תלות ב-$\varphi$ ו-$A_\varphi=0$: נשאר רק הרכיב $\hat\varphi$ (תרגיל הכדור, ה1).

## 2. משוואות מקסוול (ה1, ת1)
$$\nabla\times\vec E=-\frac{\partial\vec B}{\partial t}\ (-\vec M) \qquad \nabla\times\vec H=\vec J+\frac{\partial\vec D}{\partial t} \qquad \nabla\cdot\vec D=\rho \qquad \nabla\cdot\vec B=0$$
$$\vec D=\varepsilon\vec E,\quad \vec B=\mu\vec H,\quad \vec J=\sigma\vec E,\quad \varepsilon=\varepsilon_r\varepsilon_0,\ \mu=\mu_r\mu_0 \qquad \nabla\cdot\vec J+\partial_t\rho=0$$
אינטגרלי (פאראדיי): $\oint_C\vec E\cdot d\vec\ell=-\frac{d}{dt}\int_S\vec B\cdot d\vec s$ · $\vec M$ = זרם מגנטי פיקטיבי (Pozar), לא קיים בטבע.
> ⭐ $\hat x E(z)$ ← הרוטור כולו ב-$\hat y$: $\nabla\times(\hat xE_x(z))=\hat y\,\partial_zE_x$ (ת1). ⚠️ $\vec H=\vec B/\mu$ – **מחלקים** ב-$\mu$ (על הלוח הוכפל בטעות).

## 3. תנאי שפה ($\hat n$ מ-2 אל 1) (ה1, ה2)
| | נורמלי | משיקי |
|---|---|---|
| חשמלי | $\hat n\cdot(\vec D_1-\vec D_2)=\rho_s$ | $\hat n\times(\vec E_1-\vec E_2)=-\vec M_s$ (בד"כ $0$: $E_{1t}=E_{2t}$) |
| מגנטי | $\hat n\cdot(\vec B_1-\vec B_2)=0$ | $\hat n\times(\vec H_1-\vec H_2)=\vec J_s$ |

מוליך אידיאלי (קיר חשמלי, "קצר"): $\hat n\times\vec E=0,\ \hat n\cdot\vec B=0$, בתוכו $\vec E=\vec H=0$, $\vec J_s=\hat n\times\vec H$ · קיר מגנטי ("נתק"): $\hat n\times\vec H=0$

## 4. פאזורים (ה1, ה2)
$$\vec{\mathcal E}(\vec r,t)=\text{Re}\{\tilde E(\vec r)e^{j\omega t}\} \qquad \partial_t\to j\omega$$
$$A\cos(\omega t+\phi)\leftrightarrow Ae^{j\phi} \qquad A\sin(\omega t+\phi)\leftrightarrow -jAe^{j\phi}$$
$$\nabla\times\tilde E=-j\omega\mu\tilde H \qquad \nabla\times\tilde H=(\sigma+j\omega\varepsilon)\tilde E$$
$$\nabla^2\tilde E+k^2\tilde E=0,\qquad k=\omega\sqrt{\mu\varepsilon}$$
גל $\tilde E=\vec E_0e^{-j\vec k\cdot\vec r}$: $\ \nabla\to-j\vec k$ ⟹ $\nabla\cdot\tilde E=0\iff\vec k\cdot\vec E_0=0$, $\ \nabla^2\to-|\vec k|^2$, $\ k_x^2+k_y^2+k_z^2=k^2$
$$\overline{|\vec{\mathcal E}|^2}=\frac1T\int_0^T\vec{\mathcal E}\cdot\vec{\mathcal E}\,dt=\frac12\tilde E\cdot\tilde E^*=\frac12(E_1^2+E_2^2+E_3^2)$$
$$E_{rms}=|\tilde E|/\sqrt2$$
> בה1 הופיע גם הכתיב $e^{i(\vec k\cdot\vec r-\omega t)}$ (פיזיקה, $i=-j$) – אותן תוצאות לגדלים ($\nabla^2\to-k^2$).

## 5. גל מישורי וסיווג תווכים (ה1, ה2, ת2)
$$\gamma^2=j\omega\mu(\sigma+j\omega\varepsilon),\qquad \gamma=\alpha+j\beta$$
$$\mathcal E(z,t)=E_0e^{-\alpha z}\cos(\omega t-\beta z+\phi)$$
$$\eta=\sqrt{\frac{j\omega\mu}{\sigma+j\omega\varepsilon}}=\frac{j\omega\mu}{\gamma}$$
$$v_p=\frac\omega\beta=\lambda f \qquad \lambda=\frac{2\pi}\beta \qquad \delta_s=\frac1\alpha \qquad \alpha_{dB/m}=8.686\,\alpha$$
$$\varepsilon=\varepsilon'-j\varepsilon'' \qquad \tan\delta=\frac{\omega\varepsilon''+\sigma}{\omega\varepsilon'}\ \ (\text{בלי }\varepsilon'':\ \tfrac{\sigma}{\omega\varepsilon})$$

| $x=\frac{\sigma}{\omega\varepsilon}$ | $\alpha$ [Np/m] | $\beta$ [rad/m] | $\eta$ [Ω] |
|---|---|---|---|
| $0$ חסר הפסדים | $0$ | $\omega\sqrt{\mu\varepsilon}=\frac{\omega n}{c}$ | $\sqrt{\mu/\varepsilon}=\eta_0\sqrt{\mu_r/\varepsilon_r}$ |
| $\ll1$ (בפועל $\lesssim0.1$) דל הפסדים | $\frac\sigma2\sqrt{\frac\mu\varepsilon}=\frac{\omega\sqrt{\mu\varepsilon}}2\tan\delta$ | $\omega\sqrt{\mu\varepsilon}$ | $\approx\sqrt{\mu/\varepsilon}$ |
| $\gg1$ מוליך טוב | $\sqrt{\pi f\mu\sigma}=\sqrt{\frac{\omega\mu\sigma}2}$ | $=\alpha$ | $(1+j)\sqrt{\frac{\omega\mu}{2\sigma}}=(1+j)\frac\alpha\sigma$ (פאזה $45^\circ$) |
| $\approx1$ כללי | $\omega\sqrt{\frac{\mu\varepsilon}2}\sqrt{\sqrt{1+x^2}-1}$ | $\omega\sqrt{\frac{\mu\varepsilon}2}\sqrt{\sqrt{1+x^2}+1}$ | נוסחה מלאה למעלה |
| $\sigma\to\infty$ (PEC) | $\infty$, $\delta_s=0$ | | $0$ |

מוליך טוב: $\delta_s=\frac1{\sqrt{\pi f\mu\sigma}}=\sqrt{\frac2{\omega\mu\sigma}}$ · $R_s=\text{Re}\{\eta\}=\sqrt{\frac{\omega\mu}{2\sigma}}=\frac1{\sigma\delta_s}$ · הספק נבלע לשטח: $\frac{P}{A}=\frac12R_s|H_t|^2$
> ⭐ $\delta_s$ **קטן** כש-$\sigma$ או $f$ גדלים (ת2: מי ים ב-5GHz, $x=0.177$ ← דל הפסדים, $\alpha\approx83.7$, $\delta\approx12$mm; הקירוב סוטה ב-0.4% מהמדויק). ⚠️ המתרגל אמר את ההפך – טעות.

## 6. גל מישורי: $\vec E$ ↔ $\vec H$ והספק (ה1, ה3, ת3)
$$\tilde H=\frac1\eta\,\hat k\times\tilde E \qquad \tilde E=-\eta\,\hat k\times\tilde H$$
$$\hat k=\hat e_E\times\hat e_H \qquad \eta=\frac{E_x}{H_y}=\frac{\omega\mu}k$$
$$\vec S_{avg}=\frac12\text{Re}\{\tilde E\times\tilde H^*\}$$
חסר הפסדים: $|\vec S_{avg}|=\frac{|E_0|^2}{2\eta}$ · הפסדי: $|\vec S_{avg}|=\frac{|E_0|^2}{2|\eta|}e^{-2\alpha z}\cos\theta_\eta$
דוגמאות: $\hat z\times\hat x=\hat y$, $\hat z\times\hat y=-\hat x$, $\hat z\times(-\hat x)=-\hat y$ · $\frac{1.2}{120\pi}=\frac1{100\pi}$ (ה3)

## 7. קיטוב (ה3, ת2, ת3)
$$\vec{\mathcal E}=\hat xE_{0x}\cos(\omega t-\beta z+\phi_x)+\hat yE_{0y}\cos(\omega t-\beta z+\phi_y)$$
$$\Delta\phi=\phi_y-\phi_x$$
> ⭐ קודם להביא את שני הרכיבים ל**קוסינוס עם משרעת חיובית** ($-\cos a=\cos(a\pm\pi)$, $\sin a=\cos(a-\tfrac\pi2)$), רק אז $\Delta\phi$. בפאזור: $+j\leftrightarrow+\tfrac\pi2$, $-j\leftrightarrow-\tfrac\pi2$.

| סוג | תנאי | |
|---|---|---|
| ליניארי | $\Delta\phi=0,\pm\pi$ | זווית מציר $x$: $\theta=\arctan\frac{E_{0y}}{E_{0x}}$ |
| מעגלי | $E_{0x}=E_{0y}$ **וגם** $\Delta\phi=\pm\frac\pi2$ | $+\frac\pi2$: CCW · $-\frac\pi2$: CW (מוסכמת התרגול) |
| אליפטי | כל השאר | $\tan2\theta=\frac{2E_{0x}E_{0y}\cos\Delta\phi}{E_{0x}^2-E_{0y}^2}$ |

> ⚠️ **רביע:** מכנה שלילי ($E_{0y}>E_{0x}$) ← להוסיף $180^\circ$ ל-$2\theta$. דוגמה (ת3): $E_{0x}=1,E_{0y}=2,\Delta\phi=-\frac\pi4$: $\tan2\theta=-0.943$ ← $2\theta=136.7^\circ$, $\theta\approx68.3^\circ$ (לא $-21.7^\circ$ – זה הציר הקטן).

> כיוון סיבוב (גל ב-$+z$): $-\frac\pi2$ = CW במבט בכיוון ההתקדמות = RHCP (IEEE); $+\frac\pi2$ = CCW = LHCP. גל ב-$-z$ – הפוך. לוודא מול המרצה.

ת3: $\tilde E=E_0(\hat x+j\rho_0\hat y)e^{-j\beta z}$ ← $\tilde H=\frac{E_0}{\eta_0}(\hat y-j\rho_0\hat x)e^{-j\beta z}$ ; מעגלי $\rho_0=\pm1$, ליניארי $\rho_0=0$.

## 8. פגיעה בממשק (ה3)
**ניצבת** (תווך 1 ← 2):
$$\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1} \qquad T=1+\Gamma=\frac{2\eta_2}{\eta_2+\eta_1}$$
חלק ההספק המוחזר: $|\Gamma|^2$ · העובר (חסר הפסדים): $1-|\Gamma|^2$
$\tilde E_r=\hat x\,\Gamma E_0e^{+j\beta_1z}$, $\ \tilde H_r=-\hat y\,\frac{\Gamma E_0}{\eta_1}e^{+j\beta_1z}$ (⭐ סימן מינוס), $\ \tilde E_t=\hat x\,TE_0e^{-\gamma_2z}$ · PEC: $\Gamma=-1$, $\tilde E_1=-2jE_0\sin(\beta_1z)\hat x$ (גל עומד)

**אלכסונית:** $\ k_1\sin\theta_i=k_2\sin\theta_t$ (סנל), $\theta_r=\theta_i$
$$\Gamma_\perp=\frac{\eta_2\cos\theta_i-\eta_1\cos\theta_t}{\eta_2\cos\theta_i+\eta_1\cos\theta_t},\quad T_\perp=\frac{2\eta_2\cos\theta_i}{\eta_2\cos\theta_i+\eta_1\cos\theta_t}$$
$$\Gamma_\parallel=\frac{\eta_2\cos\theta_t-\eta_1\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i},\quad T_\parallel=\frac{2\eta_2\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i}$$
ברוסטר (קיטוב מקביל, $\mu_1=\mu_2$): $\tan\theta_B=\sqrt{\varepsilon_2/\varepsilon_1}$ · שכבה בעובי $d$: $Z_{in}=\eta_2\frac{Z_L+j\eta_2\tan\beta_2d}{\eta_2+jZ_L\tan\beta_2d}$

## 🔢 קבועים ויחידות
$\varepsilon_0=8.854\cdot10^{-12}$ F/m · $\mu_0=4\pi\cdot10^{-7}$ H/m · $c=3\cdot10^8$ m/s · $\eta_0=120\pi\approx377\,\Omega$ · $n=\sqrt{\mu_r\varepsilon_r}$, $v_p=c/n$

$E$ [V/m] · $H$ [A/m] · $D$ [C/m²] · $B$ [T] · $J$ [A/m²] · $\rho_s$ [C/m²] · $S$ [W/m²] · $\alpha$ [Np/m] · $\beta,k$ [rad/m] · $\eta,R_s$ [Ω] · $\sigma$ [S/m]

## ⚠️ טעויות נפוצות
- לא לכתוב יחידות (המתרגל מוריד נקודות) · לשכוח $\omega=2\pi f$ ו-GHz→Hz.
- נוסחת מוליך טוב בלי לבדוק $x=\sigma/(\omega\varepsilon)$ קודם.
- $\vec H=\vec B\cdot\mu$ במקום $\vec B/\mu$ · לשכוח את הצמוד ב-$\tilde H^*$.
- $\Delta\phi$ לפני שהבאת לקוסינוסים חיוביים · רביע ב-$\tan2\theta$.
- כיוון $\hat k\times\tilde E$ וסימן $\tilde H_r$ בגל המוחזר.
