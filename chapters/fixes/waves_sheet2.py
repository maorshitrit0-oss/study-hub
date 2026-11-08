"""Waves - practice sheet 2 (plane waves in lossless / lossy media): checked against the PDF and its final answers,
every number recomputed, solutions written out in full (08/11/2026). Run: python waves_sheet2.py > waves_sheet2.json"""
import json

S = []

S.append({"id": "2cb89521-6679-4b65-8130-918d2c6deb65", "uncertain": False,
"question_md": r"""גל מישורי בתדירות $\omega = 12 \times 10^8\ [\text{rad/s}]$ מתקדם באוויר ($z<0$) ופוגע בניצב ב-$z=0$ בחומר ($z>0$) בעל המציינים הבאים:
$$\varepsilon_r = 5,\quad \mu_r = 1,\quad \sigma = 10^{-4}\ [\text{S/m}]$$
אמפליטודת השדה החשמלי בכניסה לתווך ($z=0$), בזמן $t=0$, היא $100\ [\text{V/m}]$.

א. מצאו את השדות החשמלי והמגנטי הממשיים, $\vec e_t(z,t)$ ו-$\vec h_t(z,t)$, שעוברים מהאוויר לחומר.
ב. חשבו את גודל ההספק הממוצע, $P_{avg}$, הנישא ע"י הגל המועבר לחומר, ואת סך ההספק החוצה שטח של $10\,\text{m}^2$ של המישור $2z+y=5$ הנמצא בעומק $z=1\,\text{m}$.

> כיוון השדה לא כתוב בדף; בתשובות הסופיות הוא $\hat x$ (ואז $\vec h$ ב-$\hat y$).""",
"solution_md": r"""
### שלב 1: איזה תווך זה? (תמיד ראשון)
$$\varepsilon=5\varepsilon_0=5\cdot8.854\cdot10^{-12}=4.43\cdot10^{-11}\ \tfrac{\text F}{\text m}$$
$$\frac{\sigma}{\omega\varepsilon}=\frac{10^{-4}}{1.2\cdot10^9\cdot4.43\cdot10^{-11}}=\frac{10^{-4}}{0.0531}\approx1.88\cdot10^{-3}\ll1$$
⇐ **דיאלקטרי דל הפסדים** – משתמשים בקירובים.

### שלב 2: הקבועים
**קבוע פאזה** (כמו בלי הפסדים):
$$\beta\approx\omega\sqrt{\mu\varepsilon}=\frac{\omega\sqrt{\varepsilon_r}}{c}=\frac{1.2\cdot10^9\cdot\sqrt5}{3\cdot10^8}=4\sqrt5\approx8.95\approx9\ \left[\tfrac{\text{rad}}{\text m}\right]$$
**עכבה:**
$$\eta\approx\sqrt{\frac{\mu}{\varepsilon}}=\frac{\eta_0}{\sqrt{\varepsilon_r}}=\frac{376.7}{\sqrt5}\approx168.5\ \Omega$$
**קבוע ניחות** (דל הפסדים):
$$\alpha\approx\frac{\sigma}{2}\sqrt{\frac{\mu}{\varepsilon}}=\frac{10^{-4}}{2}\cdot168.5\approx8.4\cdot10^{-3}\ \left[\tfrac1{\text m}\right]$$
**הפאזה של $\eta$** (קטנה מאוד): $\theta_\eta\approx\tfrac12\arctan\frac{\sigma}{\omega\varepsilon}\approx\tfrac12\cdot1.88\cdot10^{-3}\ \text{rad}\approx0.05^\circ$.

### שלב 3 (סעיף א): השדות
גל שמתקדם ב-$+z$ ודועך: $E_0e^{-\alpha z}\cos(\omega t-\beta z)$, עם $E_0=100$ ב-$z=0,t=0$:
$$\boxed{\vec e_t=100\,e^{-8.4\cdot10^{-3}z}\cos(1.2\cdot10^9t-9z)\,\hat x\ \left[\tfrac{\text V}{\text m}\right]}$$
$\vec h=\frac1\eta\hat k\times\vec e$, עם $\hat z\times\hat x=\hat y$. המשרעת $100/168.5\approx0.59$, והפאזה של $\vec h$ **מפגרת** ב-$\theta_\eta$ (מחלקים ב-$\eta=|\eta|e^{j\theta_\eta}$):
$$\boxed{\vec h_t=0.59\,e^{-8.4\cdot10^{-3}z}\cos(1.2\cdot10^9t-9z-0.05^\circ)\,\hat y\ \left[\tfrac{\text A}{\text m}\right]}$$
✅ מתאים לדף (שם $0.06^\circ$ – עיגול).

### שלב 4 (סעיף ב): הספק
$$\vec S_{avg}=\tfrac12\text{Re}\{\tilde E\times\tilde H^*\}=\frac{|E_0|^2}{2|\eta|}\cos\theta_\eta\,e^{-2\alpha z}\,\hat z$$
$$\frac{100^2}{2\cdot168.5}\cdot\underbrace{\cos(0.05^\circ)}_{\approx1}\approx29.7\ \Rightarrow\ \boxed{\vec S_{avg}\approx29.7\,e^{-0.0168z}\,\hat z\ \left[\tfrac{\text W}{\text m^2}\right]}$$
(בחזקה $2\alpha=0.0168$ – כי הספק הוא ריבוע השדה.)

**ההספק דרך המישור $2z+y=5$:** הנורמל של מישור $ax+by+cz=d$ הוא $(a,b,c)$, כאן $\hat n=\frac{(0,1,2)}{\sqrt5}$. רק הרכיב של $\vec S$ בכיוון $\hat n$ חוצה את המישור:
$$\hat z\cdot\hat n=\frac{2}{\sqrt5}\approx0.894$$
$$P=S_{avg}(z=1)\cdot\frac2{\sqrt5}\cdot A=29.7\cdot e^{-0.0168}\cdot0.894\cdot10\approx\boxed{261\ \text W}$$

> ⚠️ בדף התשובות: $59.5\,e^{-0.0168z}$ ו-$523\,\text W$ – בדיוק פי 2 (בלי ה-$\tfrac12$ של הממוצע). עם משרעת שיא $100\,\text{V/m}$ הממוצע בזמן כולל $\tfrac12$ ⇐ $29.7$ ו-$261\,\text W$. אם התכוונו ל-$100$ כערך RMS – אז $59.5$ ו-$523$. כדאי לשאול את המתרגל איזו מוסכמה.

💡 **הרעיון:** סיווג ← קירוב דל-הפסדים ($\beta\approx\omega\sqrt{\mu\varepsilon}$, $\alpha\approx\frac\sigma2\eta$) ← $\vec h=\frac1\eta\hat k\times\vec e$ ← $S_{avg}=\frac{|E|^2}{2|\eta|}\cos\theta_\eta e^{-2\alpha z}$ ← הספק דרך משטח = $\vec S\cdot\hat n\cdot A$.
"""})

S.append({"id": "7299a28d-c2ca-4283-b270-c9d143f147a3", "uncertain": False, "solution_md": r"""
### מה זה "מוליך טוב"
מוליך טוב: זרם ההולכה גדול בהרבה מזרם ההעתקה:
$$\frac{\sigma}{\omega\varepsilon}\gg1$$
ככל שהתדר עולה, $\omega\varepsilon$ גדל והיחס יורד – לכן יש **תדר מקסימלי** שעד אליו החומר "מוליך טוב".

### החישוב
גבול: $\frac{\sigma}{\omega\varepsilon}=1$ ⇐ $\omega=\frac{\sigma}{\varepsilon}$ ⇐ $f=\frac{\sigma}{2\pi\varepsilon}$:
$$\varepsilon=5\varepsilon_0=5\cdot8.854\cdot10^{-12}=4.427\cdot10^{-11}$$
$$f_{max}=\frac{0.12}{2\pi\cdot4.427\cdot10^{-11}}=\frac{0.12}{2.78\cdot10^{-10}}\approx\boxed{431\ \text{MHz}}$$
✅ זו התשובה בדף ($430\,\text{MHz}$).

### הערה חשובה למבחן
ב-$f=431\,\text{MHz}$ היחס שווה **בדיוק 1** – שם החומר הוא "הפסדי כללי", לא ממש "מוליך טוב". אם דורשים $\frac{\sigma}{\omega\varepsilon}\ge10$ (הכלל המעשי, כמו $\le0.1$ לדל-הפסדים בתרגול 2):
$$f\le\frac{0.12}{2\pi\cdot4.427\cdot10^{-11}\cdot10}\approx43\ \text{MHz}$$
במבחן: לכתוב את החישוב לגבול $=1$ (כמו בדף), ולהוסיף משפט שבפועל "$\gg1$" אומר כמה מונים מתחת לתדר הזה.

💡 **הרעיון:** הסיווג תלוי בתדר: אותו חומר מוליך טוב בתדר נמוך ודיאלקטרי בתדר גבוה.
"""})

S.append({"id": "a036ab0b-ce91-4bbd-b62e-cdba1762cb41", "uncertain": False, "solution_md": r"""
### מה נותנים
$\eta=200e^{j30^\circ}\ \Omega$ ו-$\vec h=10e^{-\alpha z}\cos(\omega t-\tfrac12z)\hat y$. מהביטוי קוראים: $\beta=0.5\ [\text{rad/m}]$, והגל מתקדם ב-$+z$ (מינוס לפני $\beta z$).

### סעיף א: $\alpha$ ו-$\delta$
**הקשר המרכזי:** משתי הנוסחאות $\gamma=\sqrt{j\omega\mu(\sigma+j\omega\varepsilon)}$ ו-$\eta=\sqrt{\frac{j\omega\mu}{\sigma+j\omega\varepsilon}}$ – כופלים:
$$\gamma\,\eta=j\omega\mu$$
$j\omega\mu$ הוא מספר מדומה טהור – זווית $90^\circ$. בכפל מרוכבים **הזוויות מתחברות**:
$$\arg\gamma+\arg\eta=90^\circ\ \Rightarrow\ \arg\gamma=90^\circ-30^\circ=60^\circ$$
$\gamma=\alpha+j\beta$ ⇐ $\tan(\arg\gamma)=\frac\beta\alpha$:
$$\tan60^\circ=\sqrt3=\frac{0.5}{\alpha}\ \Rightarrow\ \boxed{\alpha=\frac{0.5}{\sqrt3}\approx0.289\ \left[\tfrac1{\text m}\right]}$$
$$\boxed{\delta=\frac1\alpha=2\sqrt3\approx3.46\ [\text m]}$$
✅ זהה לדף.

**בונוס – מה התדר?** $|\gamma||\eta|=\omega\mu_0$: $|\gamma|=\sqrt{0.289^2+0.5^2}=0.577$ ⇐ $\omega=\frac{0.577\cdot200}{4\pi\cdot10^{-7}}\approx9.2\cdot10^7\ \text{rad/s}$ (זה ה-$92\cdot10^6$ בתשובה בדף).

### סעיף ב: השדה החשמלי
**כיוון:** $\vec S=\vec e\times\vec h$ צריך להצביע ל-$+z$. עם $\vec h\parallel\hat y$: $\hat x\times\hat y=\hat z$ ⇐ $\vec e\parallel\hat x$. (פורמלית: $\vec e=\eta\,\vec h\times\hat k$, ו-$\hat y\times\hat z=\hat x$.)

**משרעת ופאזה:** בפאזורים $\tilde E=\eta\tilde H$: המשרעת $200\cdot10=2000\ \text{V/m}$, והפאזה $+30^\circ$ (כפל ב-$e^{j30^\circ}$ – $\vec e$ **מקדים** את $\vec h$).
$$\boxed{\vec e(z,t)=2000\,e^{-0.289z}\cos\!\left(\omega t-0.5z+30^\circ\right)\hat x\ \left[\tfrac{\text V}{\text m}\right]}\qquad(\omega\approx9.2\cdot10^7)$$

> ⚠️ בדף התשובות: $2e^{-0.287z}\cos(92\cdot10^6t-0.5z-30^\circ)\,\hat y$ [kV/m]. שתי בעיות: (1) $\hat y$ – אבל $\vec e$ חייב להיות ניצב ל-$\vec h$ שכבר ב-$\hat y$; (2) $-30^\circ$ – אבל $\tilde E=\eta\tilde H$ מוסיף $+30^\circ$. המשרעת (2 kV/m) נכונה. לבדוק עם המתרגל.

### סעיף ג: MATLAB
```matlab
alpha = 0.5/sqrt(3);  beta = 0.5;      % [1/m], [rad/m]
w = 9.2e7;  E0 = 2000;  th = pi/6;      % [rad/s], [V/m], phase of eta
z = linspace(0, 5/alpha, 500);          % five skin depths
e_env = E0*exp(-alpha*z);               % the decaying amplitude
t = 0;                                   % a snapshot at t = 0
e = E0*exp(-alpha*z).*cos(w*t - beta*z + th);
plot(z, e, z, e_env, '--', z, -e_env, '--'); grid on
xlabel('z [m]'); ylabel('e_x [V/m]'); title('E field in the lossy medium')
```

💡 **הרעיון:** $\gamma\eta=j\omega\mu$ ⇐ זווית $\gamma$ = $90^\circ$ פחות זווית $\eta$ ⇐ היחס $\beta/\alpha$. ואז $\tilde E=\eta\tilde H$ (כולל הפאזה) בכיוון שנותן $\vec S$ ב-$+z$.
"""})

S.append({"id": "c13181f7-ae06-4fa8-ae72-81d6f59465a3", "uncertain": False, "solution_md": r"""
### סעיף א: סיווג
$$\omega=2\pi\cdot10^6,\qquad \varepsilon=8\varepsilon_0=7.08\cdot10^{-11}$$
$$\frac{\sigma}{\omega\varepsilon}=\frac{40}{2\pi\cdot10^6\cdot7.08\cdot10^{-11}}=\frac{40}{4.45\cdot10^{-4}}\approx89.9\gg1$$
⇐ **מוליך טוב**
> ⚠️ בדף התשובות כתוב "מוליך גרוע" – טעות: היחס 90 פירושו מוליך טוב (וגם סעיף ב בדף משתמש בנוסחאות מוליך טוב, $\alpha=\beta$).

### סעיף ב: $\alpha$ ו-$\beta$
במוליך טוב:
$$\alpha=\beta=\sqrt{\pi f\mu\sigma}=\sqrt{\pi\cdot10^6\cdot4\pi\cdot10^{-7}\cdot40}$$
מסדרים: $10^6\cdot10^{-7}=0.1$, ו-$\pi\cdot4\pi\cdot0.1\cdot40=16\pi^2$:
$$\boxed{\alpha=\beta=\sqrt{16\pi^2}=4\pi\approx12.57}\quad \alpha\left[\tfrac1{\text m}\right],\ \beta\left[\tfrac{\text{rad}}{\text m}\right]$$

### סעיף ג: העומק שבו המשרעת עשירית
המשרעת דועכת כמו $e^{-\alpha z}$:
$$e^{-\alpha d}=0.1\ \Rightarrow\ -\alpha d=\ln0.1=-\ln10\ \Rightarrow\ d=\frac{\ln10}{\alpha}=\frac{2.303}{12.57}\approx\boxed{0.183\ [\text m]}$$
(להשוואה: עומק החדירה $\delta=1/\alpha=0.0796$ m הוא העומק שבו נשאר $1/e\approx37\%$.)

### סעיף ד: העכבה
$$\eta=(1+j)\sqrt{\frac{\omega\mu}{2\sigma}}=(1+j)\sqrt{\frac{2\pi\cdot10^6\cdot4\pi\cdot10^{-7}}{80}}=(1+j)\sqrt{\frac{\pi^2}{100}}=(1+j)\frac{\pi}{10}$$
$$\boxed{\eta\approx0.314+j0.314\ [\Omega]}\qquad|\eta|=0.444\,\Omega,\ \theta_\eta=45^\circ$$
קיצור: במוליך טוב $\sqrt{\frac{\omega\mu}{2\sigma}}=\frac\alpha\sigma=\frac{12.57}{40}=0.314$.

### סעיף ה: MATLAB – $\alpha(f)$
```matlab
mu0 = 4*pi*1e-7;  eps0 = 8.854e-12;
sigma = 40;  eps = 8*eps0;  mu = mu0;
f = logspace(4, 7, 400);                 % 10 kHz .. 10 MHz
w = 2*pi*f;
x = sigma./(w*eps);                      % loss ratio (check: >> 1 all the way)
alpha_exact = w.*sqrt(mu*eps/2).*sqrt(sqrt(1+x.^2)-1);
alpha_good  = sqrt(pi*f*mu*sigma);       % good-conductor formula
loglog(f, alpha_exact, f, alpha_good, '--'); grid on
xlabel('f [Hz]'); ylabel('\alpha [1/m]'); legend('exact','good conductor')
```
בגרף רואים ש-$\alpha\propto\sqrt f$ (קו ישר בשיפוע ½ ב-log-log) ושני הקווים כמעט חופפים, כי היחס $\sigma/\omega\varepsilon$ גדול בכל התחום.

💡 **הרעיון:** סיווג ← $\alpha=\beta=\sqrt{\pi f\mu\sigma}$ ← עומק לפי $e^{-\alpha d}=$ היחס ← $\eta=(1+j)\alpha/\sigma$.
"""})

S.append({"id": "5f812d16-5004-4586-b7e0-b2e4ac83f7cc", "uncertain": False, "solution_md": r"""
### שלב 1: סיווג
$$\omega=2\pi\cdot10^8,\qquad \varepsilon=4\varepsilon_0$$
$$\frac{\sigma}{\omega\varepsilon}=\frac{2}{2\pi\cdot10^8\cdot4\cdot8.854\cdot10^{-12}}=\frac{2}{0.02225}\approx89.9\gg1$$
⇐ **מוליך טוב**
(למרות שקוראים לו "דיאלקטרי" – בתדר הזה הוא מתנהג כמוליך טוב.)

### שלב 2: $\alpha=\beta$
$$\alpha=\beta=\sqrt{\pi f\mu\sigma}=\sqrt{\pi\cdot10^8\cdot4\pi\cdot10^{-7}\cdot2}=\sqrt{80\pi^2}\approx28.1$$

### סעיף א: אורך גל ומהירות פאזה
$$\lambda=\frac{2\pi}{\beta}=\frac{2\pi}{28.1}\approx\boxed{0.224\ [\text m]}\qquad v_\varphi=\frac\omega\beta=\frac{2\pi\cdot10^8}{28.1}\approx\boxed{2.24\cdot10^7\ \left[\tfrac{\text m}{\text s}\right]}$$
(בדיקה: $v_\varphi=\lambda f=0.224\cdot10^8$ ✅. הגל איטי פי 13 מהאור.)

### סעיף ב: השדה החשמלי
משרעת $2\,\text{kV/m}$, כיוון $\hat x$ (כמו בשאלה), מתקדם ב-$+z$:
$$\boxed{\vec e(z,t)=2\,e^{-28.1z}\cos(2\pi\cdot10^8t-28.1z)\,\hat x\ \left[\tfrac{\text{kV}}{\text m}\right]}$$
> ⚠️ בדף התשובות (ובגרסה הקודמת כאן) $\hat y$ – אבל בשאלה כתוב במפורש שהשדה בכיוון $\hat x$.

### סעיף ג: וקטור פוינטינג
$$|\eta|=\sqrt{\frac{\omega\mu}{\sigma}}=\sqrt{\frac{2\pi\cdot10^8\cdot4\pi\cdot10^{-7}}{2}}\approx19.9\ \Omega,\qquad\theta_\eta=45^\circ$$
$$\vec S_{avg}=\frac{|E_0|^2}{2|\eta|}\cos\theta_\eta\,e^{-2\alpha z}\hat z=\frac{(2000)^2}{2\cdot19.9}\cdot0.707\,e^{-56.2z}\hat z$$
$$\boxed{\vec S_{avg}\approx7.1\cdot10^4\,e^{-56.2z}\,\hat z\ \left[\tfrac{\text W}{\text m^2}\right]=71\,e^{-56.2z}\ \left[\tfrac{\text{kW}}{\text m^2}\right]}$$
> ⚠️ בדף התשובות $0.07\,e^{-56z}$ [W/m²] – אותו מספר אבל ביחידות של MW/m² (חישבו עם $E$ ב-kV/m: $\text{kV}^2/\Omega=10^6\,\text W$). **ליחידות!**

💡 **הרעיון:** סיווג ← מוליך טוב ← $\lambda,v$ מ-$\beta$ ← $S_{avg}$ עם $|\eta|$ ו-$\cos45^\circ$, ולשים לב ליחידות כשהשדה ב-kV.
"""})

S.append({"id": "73e60ab1-974e-4e07-98a0-71b307b8b121", "uncertain": False, "solution_md": r"""
### סעיף א: סיווג
$$\frac{\sigma}{\omega\varepsilon}=\frac{4}{2\pi\cdot5\cdot10^9\cdot81\cdot8.854\cdot10^{-12}}=\frac{4}{22.5}\approx0.18$$
$0.18<1$ ⇐ **מוליך גרוע / דיאלקטרי עם הפסדים**. (בגבול הקירוב "$\ll1$", אבל הקירוב טוב מאוד – בדקנו בתרגול: שגיאה של 0.4%.)

### סעיף ב: $\alpha$ ו-$\beta$ (קירוב דל-הפסדים)
$$\eta\approx\frac{\eta_0}{\sqrt{\varepsilon_r}}=\frac{376.7}{9}=41.9\ \Omega$$
$$\alpha\approx\frac\sigma2\cdot\eta=2\cdot41.9\approx\boxed{84\ \left[\tfrac1{\text m}\right]}$$
$$\beta\approx\omega\sqrt{\mu\varepsilon}=\frac{2\pi\cdot5\cdot10^9\cdot9}{3\cdot10^8}=300\pi\approx\boxed{942.5\ \left[\tfrac{\text{rad}}{\text m}\right]}$$
✅ זהה לדף.

### סעיף ג: העומק המקסימלי
המשרעת בעומק $d$: $E(d)=E_0e^{-\alpha d}$. דורשים $E(d)\ge10\,\mu\text{V/m}$, עם $E_0=1\,\text{kV/m}$ (השדה שנכנס למים):
$$e^{-\alpha d}=\frac{10\cdot10^{-6}}{10^3}=10^{-8}\ \Rightarrow\ d=\frac{\ln10^8}{\alpha}=\frac{18.42}{83.7}\approx\boxed{0.22\ [\text m]}$$
אם מתחשבים גם בהחזרה מפני הים (רק $T=\frac{2\eta_2}{\eta_2+\eta_0}\approx0.2$ מהשדה נכנס): $E_0=200\,\text{V/m}$ ⇐ $d=\frac{\ln(2\cdot10^7)}{83.7}\approx0.20$ m.

> ⚠️ בדף התשובות $d_{max}=0.124$ m – לא הצלחתי לשחזר את המספר הזה בשום הנחה סבירה (גם לא עם $2\alpha$ או עם ההחזרה). לשאול את המתרגל איך הגיע אליו. המסקנה זהה: ב-5 GHz הצוללת שומעת רק בעומק של עשרות סנטימטרים – לכן משתמשים בתדרים נמוכים מאוד (VLF).

💡 **הרעיון:** סיווג ← קירוב מתאים ← העומק מתוך $e^{-\alpha d}=\frac{E_{min}}{E_0}$ ⇐ $d=\frac{\ln(E_0/E_{min})}{\alpha}$.
"""})

S.append({"id": "0a6cb812-26d9-4574-b193-23e56bdd1f00", "uncertain": False, "solution_md": r"""
### שלב 1: הקבועים
תווך חסר הפסדים, $\varepsilon_r=4$, $\mu_r=1$:
$$v=\frac{c}{\sqrt{\varepsilon_r}}=\frac{3\cdot10^8}{2}=1.5\cdot10^8\ \tfrac{\text m}{\text s},\qquad \omega=2\pi\cdot10^8$$
$$\beta=\frac\omega v=\frac{2\pi\cdot10^8}{1.5\cdot10^8}=\frac{4\pi}{3}\ \left[\tfrac{\text{rad}}{\text m}\right],\qquad\lambda=\frac{2\pi}{\beta}=1.5\ \text m$$
$$\eta=\frac{\eta_0}{\sqrt{\varepsilon_r}}=\frac{120\pi}{2}=60\pi\ \Omega$$

### סעיף א: השדה החשמלי
צורה כללית: $\vec e=E_0\cos(\omega t-\beta z+\phi)\hat x$, עם $E_0=100\,\mu\text{V/m}=10^{-4}\,\text{V/m}$.

**מקסימום** כשהארגומנט של ה-cos הוא 0 (או $2\pi n$). ב-$t=0$, $z=0.125$:
$$0-\frac{4\pi}{3}\cdot0.125+\phi=0\ \Rightarrow\ \phi=\frac{4\pi}{3}\cdot\frac18=\frac\pi6$$
$$\boxed{\vec e(z,t)=10^{-4}\cos\!\left(2\pi\cdot10^8t-\frac{4\pi}{3}z+\frac\pi6\right)\hat x\ \left[\tfrac{\text V}{\text m}\right]}$$

### סעיף ב: השדה המגנטי
$\vec h=\frac1\eta\hat z\times\vec e$, ו-$\hat z\times\hat x=\hat y$; $\eta$ ממשי ⇐ אותה פאזה:
$$\boxed{\vec h(z,t)=\frac{10^{-4}}{60\pi}\cos\!\left(2\pi\cdot10^8t-\frac{4\pi}{3}z+\frac\pi6\right)\hat y\ \left[\tfrac{\text A}{\text m}\right]}\approx5.3\cdot10^{-7}\,\tfrac{\text A}{\text m}$$

### סעיף ג: מיקומי המקסימום ב-$t=10$ ns
$\omega t=2\pi\cdot10^8\cdot10^{-8}=2\pi$. מקסימום כשהארגומנט $=2\pi n$:
$$2\pi-\frac{4\pi}{3}z+\frac\pi6=2\pi n\ \Rightarrow\ \frac{4\pi}{3}z=\frac{13\pi}{6}-2\pi n\ \Rightarrow\ z=\frac{13}{8}-\frac32n$$
$$\boxed{z_m=\frac{13}{8}\pm n\lambda=\frac{13}{8}\pm\frac32n\ [\text m],\quad n=0,1,2,\dots}$$
**בדיקת שכל:** ב-10 ns הגל התקדם $v\cdot t=1.5\cdot10^8\cdot10^{-8}=1.5\,\text m=\lambda$ – כלומר בדיוק אורך גל אחד, ולכן המקסימה באותם מקומות כמו ב-$t=0$ (במרווחים של $\lambda$): $0.125+1.5=1.625=\frac{13}8$ ✅.

💡 **הרעיון:** "מקסימום ב-$(t_0,z_0)$" ⇐ הארגומנט שם $=0$ ⇐ $\phi$. מקסימה בזמן אחר ⇐ ארגומנט $=2\pi n$, והמרווח בין מקסימות $=\lambda$.
"""})

print(json.dumps(S, ensure_ascii=False, indent=1))
