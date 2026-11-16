"""🎯 Predicted exam questions - waves (16/11/2026: class examples with new data + the catch of the past exams:
plane-wave question 1 with oblique incidence, Poynting, conductors). Numbers checked (asserts).
  python predict_waves.py -> chapters/predict-waves.json (publish inspect=exercises)"""
import json
import math
from pathlib import Path

Q = []


def q(title, question, solution):
    Q.append({"add": True, "free": True, "source": "exam", "title": "🎯 שאלה צפויה: " + title, "question_md": question,
              "solution_md": solution, "exam_style": True, "uncertain": False})


th = math.radians(20)
tt = math.asin(2 * math.sin(th))
e1, e2 = 60 * math.pi, 120 * math.pi
G = (e2 * math.cos(th) - e1 * math.cos(tt)) / (e2 * math.cos(th) + e1 * math.cos(tt))
assert abs(math.degrees(tt) - 43.16) < 0.01 and abs(G - 0.441) < 1e-3
q("פגיעה אלכסונית TE מתווך צפוף לאוויר – וזווית קריטית",
  r"""(כמו שאלה 1 במבחני העבר ותרגול 4.) גל מישורי בקיטוב TE, $1\,GHz$, עובר מתווך עם $\varepsilon_r=4$, $\mu_0$ (בצד $z<0$) לאוויר. זווית פגיעה $20^\circ$.

1. מצא את זווית ההעברה.
2. חשב $\Gamma$ ו-$\tau$ (של השדה החשמלי).
3. **הקאץ':** מה הזווית הקריטית? מה קורה בזווית פגיעה של $40^\circ$?""",
  r"""### 1. סנל
$$n_1\sin\theta_i=n_2\sin\theta_t\;\Rightarrow\;\sin\theta_t=2\sin20^\circ=0.684\;\Rightarrow\;\theta_t\approx43.2^\circ$$ ✅

### 2. מקדמים (TE)
$\eta_1=\frac{120\pi}{2}=188.5\,\Omega$, $\eta_2=377\,\Omega$:
**נוסחה:** $$\Gamma_{TE}=\frac{\eta_2\cos\theta_i-\eta_1\cos\theta_t}{\eta_2\cos\theta_i+\eta_1\cos\theta_t}$$
**הצבה:** $$\Gamma=\frac{377\cdot0.940-188.5\cdot0.729}{377\cdot0.940+188.5\cdot0.729}=\frac{354.3-137.5}{354.3+137.5}$$
**תוצאה:** $$\Gamma\approx0.441,\qquad\tau=1+\Gamma\approx1.441$$ ✅
($\tau>1$ – מותר! זה יחס **שדות**, לא הספקים.)

### 3. הקאץ' – זווית קריטית
$$\sin\theta_c=\frac{n_2}{n_1}=\frac12\;\Rightarrow\;\theta_c=30^\circ$$ ✅
ב-$40^\circ>\theta_c$: $\sin\theta_t=1.29>1$ ⇐ **החזרה מלאה**, $|\Gamma|=1$, ובאוויר נשאר רק גל דועך (אין העברת הספק). ✅

💡 **הרעיון:** קודם $n$ ו-$\eta$ בכל תווך, אחר כך סנל, ורק אז $\Gamma$. מתווך צפוף לדליל – תמיד לבדוק זווית קריטית.""")

S = 100 / (2 * e1)
assert abs(S - 0.2653) < 1e-4
q("חילוץ פרמטרים מביטוי השדה וצפיפות הספק דרך משטח",
  r"""(כמו תרגילי הכיתה בשבועות 1–2.) בתווך חסר הפסדים עם $\mu=\mu_0$:
$$\vec E=10\cos(6\pi\cdot10^8t-4\pi z)\,\hat x\ [V/m]$$
1. מצא $f$, $\lambda$, מהירות, $\varepsilon_r$, $\eta$.
2. מצא את $\vec H$.
3. מה ההספק הממוצע שעובר דרך משטח של $2\,m^2$ ש**נטוי ב-$30^\circ$** ביחס למישור $xy$?""",
  r"""### 1. פרמטרים
$\omega=6\pi\cdot10^8$ ⇐ $f=3\cdot10^8\,Hz$; $k=4\pi$ ⇐ $\lambda=\frac{2\pi}k=0.5\,m$ ✅
$$v=\frac\omega k=1.5\cdot10^8\,m/s\;\Rightarrow\;\varepsilon_r=\left(\frac cv\right)^2=4$$ ✅
$$\eta=\frac{120\pi}{\sqrt{\varepsilon_r}}=60\pi\approx188.5\,\Omega$$ ✅

### 2. השדה המגנטי
התקדמות ב-$+z$, $\vec E$ ב-$\hat x$ ⇐ $\vec H$ ב-$\hat y$ (כי $\hat x\times\hat y=\hat z$):
$$\vec H=\frac{10}{188.5}\cos(6\pi\cdot10^8t-4\pi z)\,\hat y\approx0.053\cos(\dots)\,\hat y\ [A/m]$$ ✅

### 3. הספק
$$S_{avg}=\frac{E_0^2}{2\eta}=\frac{100}{2\cdot188.5}\approx0.265\,W/m^2\ (\hat z)$$
**הקאץ':** רק הרכיב **הניצב** למשטח עובר. הנורמל נטוי ב-$30^\circ$ מ-$\hat z$:
$$P=S_{avg}\cdot A\cos30^\circ=0.265\cdot2\cdot0.866\approx0.46\,W$$ ✅

💡 **הרעיון:** מהביטוי: $\omega$ ו-$k$ ⇐ הכל. כיוון $\vec H$ מ-$\hat E\times\hat H=\hat k$. הספק דרך משטח = $\vec S\cdot\hat n\,A$.""")

d = 1 / math.sqrt(math.pi * 1e7 * 4 * math.pi * 1e-7 * 5.8e7)
assert abs(d * 1e6 - 20.9) < 0.05
q("מוליך טוב – עומק חדירה ועובי מיגון",
  r"""(כמו תרגילי התווך המוליך מהכיתה.) נחושת: $\sigma=5.8\cdot10^7\,S/m$, $\mu_0$, $\varepsilon_0$. תדר $10\,MHz$.

1. בדוק שזה מוליך טוב.
2. מצא $\alpha$ ועומק החדירה.
3. **הקאץ':** מה העובי המינימלי של לוח נחושת כדי שההספק שעובר יירד ל-$1\%$?""",
  r"""### 1. סיווג
$$\frac\sigma{\omega\varepsilon_0}=\frac{5.8\cdot10^7}{2\pi\cdot10^7\cdot8.854\cdot10^{-12}}\approx10^{11}\gg1$$ ⇐ מוליך טוב ✅

### 2. ניחות
**נוסחה:** $$\alpha=\sqrt{\pi f\mu\sigma}$$
**הצבה:** $$\alpha=\sqrt{\pi\cdot10^7\cdot4\pi\cdot10^{-7}\cdot5.8\cdot10^7}$$
**תוצאה:** $$\alpha\approx4.79\cdot10^4\,1/m,\qquad\delta=\frac1\alpha\approx20.9\,\mu m$$ ✅

### 3. הקאץ' – הספק ולא שדה
השדה דועך כ-$e^{-\alpha z}$, אבל **ההספק** כ-$e^{-2\alpha z}$:
$$e^{-2z/\delta}=0.01\;\Rightarrow\;z=\frac\delta2\ln100\approx2.3\,\delta\approx48\,\mu m$$ ✅
(מי שמשתמש ב-$e^{-z/\delta}$ מקבל $96\,\mu m$ – כפול.)

💡 **הרעיון:** מוליך טוב ⇐ $\alpha=\beta=\sqrt{\pi f\mu\sigma}$, $\delta=1/\alpha$. דעיכת הספק – פעמיים מהירה מדעיכת השדה.""")

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "predict-waves.json"
    out.write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(Q))
