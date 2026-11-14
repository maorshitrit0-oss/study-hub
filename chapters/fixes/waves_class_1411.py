"""Waves: the class exercises extracted by classex.py, checked by Claude 14/11/2026 (he starts the course at 8:00 the next
morning; "the exam is built from the exercises of the lectures and practices"). Fixes:
- Faraday (B from a time-varying E): the sign of the curl was wrong -> B = +(3πE0/ω) sin(3πz) sin(ωt) ŷ.
- Maxwell check of static fields: "u x" in H was a garbled 15x (only 15 makes ∇·B = 0); the Gauss laws added.
- 1 MHz medium: σ/(ωε) ≈ 8.99·10⁴, not 89.875 (the conclusion "good conductor" stands).
  python waves_class_1411.py -> chapters/waves-class-1411.json (publish inspect=exercises)"""
import json
from pathlib import Path

FIX = [
    {"id": "b075adf5-a80f-4de1-a07b-7f29e9b53064", "solution_md": r"""**שלב 1 – הרוטור של E** (לשדה יש רק רכיב $x$ שתלוי ב-$z$):

**נוסחה:** $$\nabla\times\vec E=\frac{\partial E_x}{\partial z}\,\hat y$$

**הצבה:** $$\frac{\partial}{\partial z}\left[E_0\cos(3\pi z)\cos(\omega t)\right]=-3\pi E_0\sin(3\pi z)\cos(\omega t)$$

**תוצאה:** $$\nabla\times\vec E=-3\pi E_0\sin(3\pi z)\cos(\omega t)\,\hat y$$

**שלב 2 – חוק פאראדיי:** $$\frac{\partial\vec B}{\partial t}=-\nabla\times\vec E=3\pi E_0\sin(3\pi z)\cos(\omega t)\,\hat y$$

**אינטגרציה בזמן** ($\int\cos\omega t\,dt=\frac{\sin\omega t}{\omega}$):

$$\vec B(z,t)=\frac{3\pi E_0}{\omega}\sin(3\pi z)\sin(\omega t)\,\hat y=\frac{E_0}{3\cdot10^9}\sin(3\pi z)\sin(\omega t)\,\hat y$$ ✅

> ⚠️ תוקן: בפתרון הקודם הרוטור נכתב עם סימן הפוך ($-\partial E_x/\partial z$), ולכן B יצא עם מינוס. הנכון: $(\nabla\times\vec E)_y=\partial E_x/\partial z$.

**שלב 3:** $$\vec H=\frac{\vec B}{\mu_0}=\frac{E_0}{3\cdot10^9\,\mu_0}\sin(3\pi z)\sin(\omega t)\,\hat y$$ ✅

> ⚠️ לבדוק מול הלוח: כדי שהשדה יקיים את משוואות מקסוול בריק צריך $\omega=ck=3\cdot10^8\cdot3\pi=9\pi\cdot10^8$. עם $9\pi\cdot10^9$ כמו בנתון – $\omega/k$ יוצא פי 10 ממהירות האור. ייתכן שבלוח היה $10^8$; השיטה זהה.

💡 **הרעיון:** רוטור של E ← מינוס ← אינטגרל בזמן = B. זה גל עומד: $\cos(3\pi z)\cos(\omega t)$ ב-E נותן $\sin(3\pi z)\sin(\omega t)$ ב-B – הזזה של רבע גל ורבע מחזור."""},
    {"id": "768dc496-37a4-4ba3-b36f-54ade9167198",
     "question_md": r"""נתונים שני שדות סטטיים במרחב: $$\vec D=6\hat x-2y\hat y+2z\hat z,\qquad \vec H=15x\hat x+10y\hat y-25z\hat z$$
בתווך: $\sigma=0$, $\rho_v=0$, $\mu=10^{-5}\,H/m$, $\varepsilon=4\cdot10^{-9}\,F/m$. בדוק אם השדות מקיימים את ארבע משוואות מקסוול.""",
     "solution_md": r"""**שלב 1 – חוק גאוס החשמלי:** $\nabla\cdot\vec D=\rho_v$.

$$\nabla\cdot\vec D=\frac{\partial(6)}{\partial x}+\frac{\partial(-2y)}{\partial y}+\frac{\partial(2z)}{\partial z}=0-2+2=0=\rho_v$$ ✅

**שלב 2 – גאוס המגנטי:** $\nabla\cdot\vec B=\mu\,\nabla\cdot\vec H=0$.

$$\nabla\cdot\vec H=15+10-25=0$$ ✅ (בדיוק בגלל המקדם 15 – כל מספר אחר היה סותר את המשוואה)

**שלב 3 – פאראדיי:** $\nabla\times\vec E=-\partial\vec B/\partial t$. השדות סטטיים ⇐ אגף ימין 0.
כל רכיב של D תלוי רק בקואורדינטה של עצמו ($D_y$ רק ב-$y$, $D_z$ רק ב-$z$) ⇐ כל הנגזרות הצולבות אפס ⇐ $$\nabla\times\vec E=\frac1\varepsilon\nabla\times\vec D=0$$ ✅

**שלב 4 – אמפר:** $\nabla\times\vec H=\vec J+\partial\vec D/\partial t$. $\sigma=0$ ⇐ $\vec J=0$; סטטי ⇐ $\partial\vec D/\partial t=0$.
גם ב-H כל רכיב תלוי רק בקואורדינטה של עצמו ⇐ $$\nabla\times\vec H=0$$ ✅

**תוצאה:** ארבע המשוואות מתקיימות ✅

> ⚠️ תוקן: בנוסח הקודם היה כתוב "u x" במקום $15x$ (שגיאת העתקה), ונבדקו רק פאראדיי ואמפר. הוספו שני חוקי גאוס – שם רואים למה המקדם הוא 15.

💡 **הרעיון:** בדיקת שדה = 4 משוואות: שתי דיברגנץ (מטענים) ושני רוטורים (פאראדיי, אמפר). שדה שהרכיב שלו תלוי רק בקואורדינטה של עצמו – תמיד חסר רוטור."""},
    {"id": "30c4dbdd-1ed6-47e5-8751-4503cae6adf4", "solution_md": r"""**סעיף א – סיווג:** משווים זרם הולכה לזרם העתקה.

**נוסחה:** $$\frac{\sigma}{\omega\varepsilon}=\frac{\sigma}{2\pi f\varepsilon_r\varepsilon_0}$$

**הצבה:** $$\frac{40}{2\pi\cdot10^6\cdot8\cdot8.854\cdot10^{-12}}=\frac{40}{4.45\cdot10^{-4}}$$

**תוצאה:** $$\approx8.99\cdot10^4\gg1$$ ⇐ **מוליך טוב** ✅

> ⚠️ תוקן: בפתרון הקודם נכתב 89.875 – שגיאה בסדר גודל. היחס הוא כ-90,000; המסקנה (מוליך טוב) נשארת.

**סעיף ב – α ו-β (מוליך טוב):**

**נוסחה:** $$\alpha=\beta=\sqrt{\pi f\mu\sigma}$$

**הצבה:** $$\sqrt{\pi\cdot10^6\cdot4\pi\cdot10^{-7}\cdot40}=\sqrt{157.9}$$

**תוצאה:** $$\alpha=\beta\approx12.57\,[1/m]$$ ✅

**סעיף ג – עומק חדירה:** $$\delta=\frac1\alpha=\frac{1}{12.57}\approx0.0796\,m=79.6\,mm$$ ✅

**סעיף ד – עכבה:**

**נוסחה:** $$\eta=(1+j)\sqrt{\frac{\omega\mu}{2\sigma}}$$

**הצבה:** $$\sqrt{\frac{2\pi\cdot10^6\cdot4\pi\cdot10^{-7}}{80}}=\sqrt{0.0987}\approx0.314$$

**תוצאה:** $$\eta\approx0.314(1+j)\,\Omega$$ ✅ (פאזה $45^\circ$ – אופייני למוליך טוב)

💡 **הרעיון:** קודם מסווגים לפי $\sigma/\omega\varepsilon$, ורק אז בוחרים נוסחאות: מוליך טוב ⇐ $\alpha=\beta=\sqrt{\pi f\mu\sigma}$."""},
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "waves-class-1411.json"
    out.write_text(json.dumps(FIX, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(FIX))
