"""🎯 Predicted exam questions - digital circuits (his request 16/11/2026: "the lecturers say: know the lectures, the
practices and their examples and you will pass - they will not give the same question, they change the data and add a
catch; build the expected exam on that, using the past exams"). Each question = a class example with new data + the
catch the past exams use; every number solved here (python check at the bottom).
  python predict_digital.py -> chapters/predict-digital.json (publish inspect=exercises: free exercises, ids in the log)"""
import json
import math
from pathlib import Path

Q = []


def q(title, question, solution):
    Q.append({"add": True, "free": True, "source": "exam", "title": "🎯 שאלה צפויה: " + title, "question_md": question,
              "solution_md": solution, "exam_style": True, "uncertain": False})


# --- 1. resistor-load NMOS inverter: the class example (R=10k) turned into a DESIGN question + delay (the catch) ---
kn, VDD, Vt, R, CL = 0.2e-3, 5.0, 1.0, 25e3, 1e-12
a = kn * R  # 5 1/V
VOL = (21 - math.sqrt(441 - 50)) / 5
VIL = 1 + 1 / a
VOH_ = math.sqrt(2 / 3)
VIH = 1 + 2 * VOH_ - 0.2
VM = (4 + math.sqrt(41)) / 5
Rmin = (5 - 0.3) / (0.2 * (4 * 0.3 - 0.3 ** 2 / 2))  # kOhm
assert abs(VOL - 0.2452) < 1e-3 and abs(VIH - 2.433) < 1e-3 and abs(VM - 2.081) < 1e-3 and abs(Rmin - 20.35) < 0.01
q("מהפך NMOS עם נגד – תכנון הנגד, שולי רעש וזמן עלייה",
  r"""מהפך NMOS עם נגד עומס (כמו הדוגמה בהרצאה 4, נתונים אחרים): $V_{DD}=5\,V$, $V_t=1\,V$, $k_n'=20\,\mu A/V^2$, $W/L=10$.

1. מה הנגד **המינימלי** $R$ כך ש-$V_{OL}\le0.3\,V$ (כניסה $5\,V$)?
2. בוחרים $R=25\,k\Omega$. חשב $V_{OL}$, $V_{IL}$, $V_{IH}$, $V_M$ ושולי הרעש.
3. ההספק הסטטי הממוצע.
4. **הקאץ':** קיבול מוצא $C_L=1\,pF$. מה $t_{PLH}$? מה קורה ל-$V_{OL}$ ול-$t_{PLH}$ אם מגדילים את $R$?""",
  rf"""**נתון עזר:** $k_n=k_n'\frac WL=0.2\,mA/V^2$.

### 1. נגד מינימלי
כניסה $5\,V$, מוצא נמוך ⇐ טריודה:
$$I_D=k_n\left[(V_{{GS}}-V_t)V_O-\tfrac12V_O^2\right]=0.2\left[4\cdot0.3-\tfrac12\cdot0.3^2\right]=0.231\,mA$$
$$R=\frac{{V_{{DD}}-V_O}}{{I_D}}=\frac{{4.7}}{{0.231\,m}}\approx20.3\,k\Omega$$ ✅ ⇐ צריך $R\ge20.3\,k\Omega$ (נגד גדול יותר ⇐ $V_{{OL}}$ קטן יותר).

### 2. נקודות ה-VTC עם $R=25\,k\Omega$
$k_nR=5\,V^{{-1}}$.

**$V_{{OL}}$** (טריודה): $$V_O=5-5\left[4V_O-\tfrac12V_O^2\right]\Rightarrow2.5V_O^2-21V_O+5=0\Rightarrow V_{{OL}}={VOL:.3f}\,V$$ ✅

**$V_{{IL}}$** (רוויה): $$V_O=5-2.5(V_I-1)^2,\quad\frac{{dV_O}}{{dV_I}}=-5(V_I-1)=-1\Rightarrow V_{{IL}}={VIL:.1f}\,V$$ ✅

**$V_{{IH}}$** (טריודה, שיפוע $-1$): גוזרים $V_O=5-5(V_I-1)V_O+2.5V_O^2$ ⇐ $V_I-1=2V_O-0.2$; מציבים ⇐ $7.5V_O^2=5$ ⇐ $V_O={VOH_:.3f}\,V$:
$$V_{{IH}}=1+2\cdot{VOH_:.3f}-0.2={VIH:.2f}\,V$$ ✅

**$V_M$** ($V_O=V_I$, רוויה): $$V=5-2.5(V-1)^2\Rightarrow2.5V^2-4V-2.5=0\Rightarrow V_M={VM:.2f}\,V$$ ✅

**שולי רעש:** $$NM_L=V_{{IL}}-V_{{OL}}={VIL - VOL:.2f}\,V,\qquad NM_H=V_{{OH}}-V_{{IH}}=5-{VIH:.2f}={5 - VIH:.2f}\,V$$ ✅

### 3. הספק סטטי
$$P(OL)=V_{{DD}}\frac{{V_{{DD}}-V_{{OL}}}}{{R}}=5\cdot\frac{{{5 - VOL:.3f}}}{{25\,k}}={5 * (5 - VOL) / 25:.3f}\,mW,\quad P(OH)=0$$
$$P_{{avg}}={5 * (5 - VOL) / 50:.3f}\,mW$$ ✅

### 4. הקאץ' – זמן עלייה
במעבר ל-1 הטרנזיסטור נסגר והקבל נטען **דרך הנגד**:
$$t_{{PLH}}\approx0.69\,RC_L=0.69\cdot25\,k\cdot1\,p\approx17.3\,ns$$ ✅

**מגדילים את $R$:** $V_{{OL}}$ יורד (טוב) ⇐ אבל $t_{{PLH}}$ גדל באותו יחס והמעגל איטי יותר. זה המחיר של מהפך עם נגד – ולכן עוברים לעומס אקטיבי ול-CMOS.

💡 **הרעיון:** אותה שיטה כמו בכיתה (קיטעון / רוויה / טריודה + שיפוע $-1$), רק בכיוון ההפוך: מהדרישה על $V_{{OL}}$ מוצאים את $R$.""")

# --- 2. ring oscillator + dynamic power (lecture 2 class examples together, + scaling the supply = the catch) ---
f1 = 1 / (2 * 7 * 50e-12)
P1 = 7 * 10e-15 * 1.2 ** 2 * f1
f2 = 1 / (2 * 7 * 60e-12)
P2 = 7 * 10e-15 * 1.0 ** 2 * f2
assert abs(f1 / 1e9 - 1.4286) < 1e-3 and abs(P1 * 1e6 - 144.0) < 0.1 and abs(P2 * 1e6 - 83.3) < 0.1
q("מתנד טבעת והספק דינמי – ומה קורה כשמורידים מתח",
  r"""מתנד טבעת של $N=7$ מהפכים, $t_p=50\,ps$ לכל מהפך, קיבול $C=10\,fF$ במוצא של כל מהפך, $V_{DD}=1.2\,V$.

1. מה תדר התנודה?
2. מה ההספק הדינמי של כל הטבעת?
3. **הקאץ':** מורידים את המתח ל-$V_{DD}=1.0\,V$ וההשהיה גדלה ל-$t_p=60\,ps$. מה התדר וההספק עכשיו? פי כמה ירד ההספק, ולמה יותר מהתדר?""",
  rf"""### 1. תדר
**נוסחה:** $$f=\frac1{{2Nt_p}}$$
**הצבה:** $$f=\frac1{{2\cdot7\cdot50\,ps}}=\frac1{{700\,ps}}$$
**תוצאה:** $$f\approx{f1 / 1e9:.3f}\,GHz$$ ✅

### 2. הספק דינמי
כל מהפך מחליף מצב פעם בכל מחזור:
**נוסחה:** $$P=N\cdot C\,V_{{DD}}^2\,f$$
**הצבה:** $$P=7\cdot10\,f\cdot1.44\cdot{f1 / 1e9:.3f}\,G$$
**תוצאה:** $$P\approx{P1 * 1e6:.0f}\,\mu W$$ ✅

### 3. מתח נמוך
$$f'=\frac1{{2\cdot7\cdot60\,ps}}\approx{f2 / 1e9:.3f}\,GHz,\qquad P'=7\cdot10\,f\cdot1^2\cdot{f2 / 1e9:.3f}\,G\approx{P2 * 1e6:.1f}\,\mu W$$ ✅

**היחס:** $P/P'\approx{P1 / P2:.2f}$, בזמן שהתדר ירד רק פי ${f1 / f2:.2f}$ – כי ההספק תלוי ב-**ריבוע** המתח: $(1.2)^2=1.44$.

💡 **הרעיון:** $f=1/2Nt_p$ ו-$P=CV^2f$ – שתי הנוסחאות מהכיתה. הורדת מתח חוסכת הספק בריבוע ומשלמת במהירות.""")

# --- 3. NMOS as a switch: Ron at small VDS vs VDS/ID at a large one (the catch) + saturation ---
kn3, Vov = 0.4e-3, 2.5
Ron = 1 / (kn3 * Vov)
I1 = kn3 * (Vov * 1 - 0.5)
I3 = 0.5 * kn3 * Vov ** 2
assert abs(Ron - 1000) < 1e-6 and abs(I1 - 0.8e-3) < 1e-9 and abs(I3 - 1.25e-3) < 1e-9
q("טרנזיסטור NMOS כמתג – התנגדות, תחום עבודה וזרם",
  r"""טרנזיסטור NMOS: $k_n'\frac WL=0.4\,mA/V^2$, $V_t=0.8\,V$, $V_{GS}=3.3\,V$.

1. מה ההתנגדות $R_{on}$ של התעלה כש-$V_{DS}$ קטן מאוד?
2. $V_{DS}=1\,V$: באיזה תחום הטרנזיסטור? מה $I_D$ ומה היחס $V_{DS}/I_D$? למה הוא שונה מ-$R_{on}$?
3. $V_{DS}=3\,V$: באיזה תחום? מה $I_D$?""",
  rf"""$V_{{ov}}=V_{{GS}}-V_t=2.5\,V$.

### 1. $R_{{on}}$
ב-$V_{{DS}}$ קטן מזניחים את $\tfrac12V_{{DS}}^2$: $I_D\approx k_nV_{{ov}}V_{{DS}}$:
$$R_{{on}}=\frac1{{k_nV_{{ov}}}}=\frac1{{0.4\,m\cdot2.5}}=1\,k\Omega$$ ✅

### 2. $V_{{DS}}=1\,V$
$V_{{DS}}=1<V_{{ov}}=2.5$ ⇐ **טריודה**.
$$I_D=k_n\left[V_{{ov}}V_{{DS}}-\tfrac12V_{{DS}}^2\right]=0.4\,m\,[2.5-0.5]=0.8\,mA$$ ✅
$$\frac{{V_{{DS}}}}{{I_D}}=\frac{{1}}{{0.8\,m}}=1.25\,k\Omega$$ ✅
**הקאץ':** גדול מ-$R_{{on}}$, כי האיבר $-\tfrac12V_{{DS}}^2$ כבר לא זניח – התעלה "נצבטת" ליד הדריין. $R_{{on}}$ מתאים רק ל-$V_{{DS}}$ קטן.

### 3. $V_{{DS}}=3\,V$
$V_{{DS}}=3>V_{{ov}}=2.5$ ⇐ **רוויה**:
$$I_D=\tfrac12k_nV_{{ov}}^2=\tfrac12\cdot0.4\,m\cdot6.25=1.25\,mA$$ ✅

💡 **הרעיון:** קודם משווים $V_{{DS}}$ ל-$V_{{GS}}-V_t$ ⇐ בוחרים נוסחה. מתג טוב = $V_{{ov}}$ גדול ⇐ $R_{{on}}$ קטן.""")

# --- 4. BJT inverter: the lecture 4 example with new resistors + noise margins and the active-region gain ---
IB = (5 - 0.2) / 2e3 / 40
VIH4 = 0.7 + IB * 20e3
assert abs(VIH4 - 1.9) < 1e-9
q("מהפך ביפולרי – נקודות ה-VTC, שולי רעש והגבר",
  r"""מהפך ביפולרי (כמו הדוגמה בהרצאה 4): $V_{CC}=5\,V$, $R_C=2\,k\Omega$, $R_B=20\,k\Omega$, $\beta=40$, $V_{BE(on)}=0.7\,V$, $V_{CE(sat)}=0.2\,V$.

1. מצא $V_{OH}$, $V_{OL}$, $V_{IL}$, $V_{IH}$.
2. חשב את שולי הרעש.
3. מה שיפוע ה-VTC באזור הפעיל? **הקאץ':** מה קורה ל-$V_{IH}$ אם $\beta$ גדל ל-80?""",
  rf"""### 1. נקודות
- $V_I<0.7\,V$ ⇐ קיטעון, $I_C=0$ ⇐ $V_{{OH}}=V_{{CC}}=5\,V$ ✅, ו-$V_{{IL}}=0.7\,V$ ✅ (שם מתחיל זרם).
- רוויה ⇐ $V_{{OL}}=V_{{CE(sat)}}=0.2\,V$ ✅
- **$V_{{IH}}$** = הכניסה שבה הטרנזיסטור בדיוק נכנס לרוויה:
$$I_C=\frac{{V_{{CC}}-V_{{CE(sat)}}}}{{R_C}}=\frac{{4.8}}{{2\,k}}=2.4\,mA,\quad I_B=\frac{{I_C}}\beta=\frac{{2.4}}{{40}}=0.06\,mA$$
$$V_{{IH}}=V_{{BE}}+I_BR_B=0.7+0.06\,m\cdot20\,k=1.9\,V$$ ✅

### 2. שולי רעש
$$NM_L=V_{{IL}}-V_{{OL}}=0.7-0.2=0.5\,V,\qquad NM_H=V_{{OH}}-V_{{IH}}=5-1.9=3.1\,V$$ ✅

### 3. שיפוע והקאץ'
באזור הפעיל $V_O=V_{{CC}}-\beta\frac{{V_I-0.7}}{{R_B}}R_C$:
$$\frac{{dV_O}}{{dV_I}}=-\beta\frac{{R_C}}{{R_B}}=-40\cdot\frac{{2}}{{20}}=-4$$ ✅
**$\beta=80$:** $I_B=2.4/80=0.03\,mA$ ⇐ $V_{{IH}}=0.7+0.6=1.3\,V$, השיפוע $-8$: המעבר חד יותר ו-$NM_H$ גדל ל-$3.7\,V$.

💡 **הרעיון:** $V_{{IL}}$ = תחילת ההולכה, $V_{{IH}}$ = כניסה לרוויה. ב-BJT הרוויה נקבעת מ-$I_B=I_{{C,sat}}/\beta$.""")

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "predict-digital.json"
    out.write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(Q))
