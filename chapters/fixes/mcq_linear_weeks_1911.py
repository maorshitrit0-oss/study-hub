"""Linear circuits weeks built BY HAND from lecture N + practice N only (his request 19/11/2026: "lecture, practice,
and the exercises that match them - not exercises from irrelevant lectures"). This file converts the lesson exercises
the week lists still lacked to the exam format (4-option MCQ + full method) and adds two week-3 questions on topics
lecture 3 taught with no exercise (weighted summer, log amplifier - board formulas only). The lecture-2 examples are
the lecturer's own (Sedra 1.2-1.4); their mistakes are fixed here (gain sign -200, dBm working line, P_diss with the
input power, all four saturation cases). Every number asserted in check().
  python mcq_linear_weeks_1911.py -> chapters/mcq-1911-linear-weeks.json (publish inspect=exercises, after weekset-set)"""
import json
import math
from pathlib import Path

from mcq_linear_1911 import mcq


def check():
    ok = lambda x, y, tol=0.006: abs(x - y) <= tol * max(1e-12, abs(y))  # noqa: E731
    assert ok(1e-3 * 10e3 / 10.1e3, 0.990e-3) and ok(1e-3 * 10e3 / 20e3, 0.5e-3)
    assert ok(100 / 100, 1) and ok(100 * 10e3 / 100, 1e4) and ok(100 * 10e3, 1e6)
    assert ok(10 * math.log10(5e6), 67, 0.01) and ok(10 * math.log10(8e-3), -20.97) and ok(1e-3 * 10 ** 3.8, 6.31) and ok(1e-3 * 10 ** -3.8, 0.158e-6)
    assert [min(10, 1000 * v) for v in (0.5e-3, 1e-3, 10e-3, 100e-3)] == [0.5, 1.0, 10.0, 10]
    pl, pi_, pdc = 9 * 9e-3 / 2, 1 * 0.1e-3 / 2, 2 * 10 * 9.5e-3
    assert ok(pl, 40.5e-3) and ok(pl / pi_, 810) and ok(20 * math.log10(9), 19.08) and ok(20 * math.log10(90), 39.08)
    assert ok(pdc + pi_ - pl, 149.55e-3) and ok(pl / pdc, 0.213, 0.01)
    assert ok(math.log(9.7e11) / 40, 0.690) and ok(math.log(5e11) / 40, 0.673) and ok(-40 * (10 - 5), -200)
    a = 10 * 100e3 / 101e3 * 100 * 10e3 / 11e3 * 100 / 110
    assert ok(a, 818) and ok(20 * math.log10(a), 58.3) and ok(a * 1 / 1.1, 744) and ok(20 * math.log10(a / 1.1), 57.4)
    assert ok(-(20 / 10 * 0.3 + 20 / 5 * 0.2), -1.4)
    assert ok(-1 * 0.025 * math.log(10), -0.0576)


W1 = [
    mcq("272e9e57-731d-4594-9bbf-6e9495af3866",
        "מקור נורטון: $i_s=1mA$ במקביל ל-$R_s=10k\\Omega$. מה זרם העומס עבור (א) $R_L=100\\Omega$; (ב) $R_L=10k\\Omega$?",
        ["(א) $\\approx0.99mA$; (ב) $0.5mA$", "(א) $1mA$; (ב) $1mA$", "(א) $\\approx0.01mA$; (ב) $0.5mA$", "(א) $\\approx0.99mA$; (ב) $\\approx0.91mA$"], 0,
        r"""**1. נוסחה (מחלק זרם):** $i_L=i_s\dfrac{R_s}{R_s+R_L}$

**2. (א):** $i_L=1m\cdot\dfrac{10k}{10k+0.1k}=1m\cdot0.990\approx0.99\,mA$ – כמעט כל הזרם.

**3. (ב):** $i_L=1m\cdot\dfrac{10k}{10k+10k}=0.5\,mA$ – חצי הולך לנגד הפנימי.

**4. מסקנה:** מקור זרם טוב כש-$R_L\ll R_s$.""",
        {1: "התעלם מ-$R_s$ – מקור זרם לא אידאלי.", 2: "הציב $R_L$ במונה במקום $R_s$.", 3: "השתמש בנוסחה של מחלק מתח עם $R_L=100k$."},
        "לצימוד זרם צריך $R_L\\ll R_s$ – ההפך מצימוד מתח."),
    mcq("6a1e17c3-6f83-4a98-abd5-0d3acc0051db",
        "מגבר מתח: $A_{vo}=100$, $R_i=10k\\Omega$, $R_o=100\\Omega$. מה הפרמטרים השקולים $G_m$, $A_{is}$, $R_m$?",
        ["$G_m=1A/V$, $A_{is}=10^4$, $R_m=1M\\Omega$", "$G_m=0.01A/V$, $A_{is}=10^4$, $R_m=1M\\Omega$",
         "$G_m=1A/V$, $A_{is}=1$, $R_m=1M\\Omega$", "$G_m=1A/V$, $A_{is}=10^4$, $R_m=10\\Omega$"], 0,
        r"""**1. הקשרים (טבלת ארבעת המודלים):** $A_{vo}=G_mR_o=A_{is}\dfrac{R_o}{R_i}=\dfrac{R_m}{R_i}$

**2. מוליכות העברה:** $G_m=\dfrac{A_{vo}}{R_o}=\dfrac{100}{100}=1\,A/V$

**3. הגבר זרם בקצר:** $A_{is}=A_{vo}\dfrac{R_i}{R_o}=100\cdot\dfrac{10k}{100}=10^4\,A/A$

**4. התנגדות העברה:** $R_m=A_{vo}R_i=100\cdot10k=1\,M\Omega$""",
        {1: "כפל ב-$R_o$ במקום לחלק.", 2: "הפך את היחס $R_i/R_o$.", 3: "חילק ב-$R_i$ במקום לכפול."},
        "אותו מגבר בכל אחד מארבעת המודלים – בוחרים לפי סוג האות במבוא ובמוצא."),
]

W2 = [
    mcq("13339d66-df08-44b1-b3d6-c83877963335",
        "המר: (1) $5kW$ ל-dBm; (2) $8\\mu W$ ל-dBm; (3) $38dBm$ לוואטים; (4) $-38dBm$ לוואטים.",
        ["$67dBm$; $-21dBm$; $6.3W$; $0.16\\mu W$", "$37dBm$; $-51dBm$; $6.3mW$; $0.16nW$",
         "$67dBm$; $+21dBm$; $6.3W$; $0.16\\mu W$", "$134dBm$; $-42dBm$; $63W$; $1.6\\mu W$"], 0,
        r"""**1. נוסחאות:** $P_{dBm}=10\log\dfrac{P}{1\,mW}$; $\;P=1\,mW\cdot10^{P_{dBm}/10}$

**2. (1):** $5\,kW=5\cdot10^6\,mW$ ⇐ $10\log(5\cdot10^6)=10\cdot6.70=67\,dBm$

**3. (2):** $8\,\mu W=8\cdot10^{-3}\,mW$ ⇐ $10\log(0.008)=10\cdot(-2.10)\approx-21\,dBm$

**4. (3):** $1m\cdot10^{3.8}=1m\cdot6310\approx6.3\,W$

**5. (4):** $1m\cdot10^{-3.8}=1m\cdot1.58\cdot10^{-4}\approx0.16\,\mu W$

> ⚠️ בפתרון המקורי נכתב $5000\,mW$ – זה $5\,W$. $5\,kW=5\cdot10^6\,mW$ (התוצאה 67 dBm נכונה).""",
        {1: "השתמש בוואט במקום במיליוואט כייחוס.", 2: "הספק קטן מ-1 mW נותן dBm **שלילי**.", 3: "השתמש ב-$20\\log$ – להספק זה $10\\log$."}),
    mcq("161c98d1-57a1-429b-882f-16b013581452",
        "מגבר עם $A_v=1000$, ליניארי בתחום מוצא $-10V$ עד $+10V$. מה אמפליטודת המוצא עבור גל ריבועי במבוא באמפליטודה: $0.5mV$, $1mV$, $10mV$, $100mV$?",
        ["$0.5V$, $1V$, $10V$, $10V$ (קטום)", "$0.5V$, $1V$, $10V$, $100V$", "$0.5V$, $1V$, $10V$, $0V$ (נשרף)", "$0.5mV$, $1mV$, $10mV$, $100mV$"], 0,
        r"""**1. בתחום הליניארי:** $v_O=A_vv_I$, כל עוד $|v_O|\le10\,V$ ⇐ גבול הכניסה: $|v_I|\le\dfrac{10}{1000}=10\,mV$

**2. $0.5\,mV$:** $1000\cdot0.5m=0.5\,V$ ✓ ליניארי

**3. $1\,mV$:** $1\,V$ ✓

**4. $10\,mV$:** $10\,V$ – בדיוק בקצה התחום ✓

**5. $100\,mV$:** $1000\cdot0.1=100\,V>10$ ⇐ **רוויה**: המוצא נקטם ל-$\pm10\,V$ (גל ריבועי של 10 V).""",
        {1: "המוצא לא יכול לעבור את גבולות הרוויה.", 2: "רוויה = קטימה בגבול, לא אפס.", 3: "שכח את ההגבר."},
        "בודקים תמיד אם $A_vv_I$ נשאר בתוך $[L_-,L_+]$."),
    mcq("320d8cba-e427-4569-8e68-cf3384a68de5",
        "מגבר מ-$\\pm10V$, מושך $9.5mA$ מכל ספק. מבוא: סינוס $1V$ שיא, $0.1mA$ שיא. מוצא: סינוס $9V$ שיא על $R_L=1k\\Omega$. מה הגבר ההספק, ההספק לחום והנצילות?",
        ["$A_p=810\\,(29.1dB)$, $P_{diss}\\approx149.6mW$, $\\eta\\approx21.3\\%$", "$A_p=810\\,(58.2dB)$, $P_{diss}\\approx149.6mW$, $\\eta\\approx21.3\\%$",
         "$A_p=1620\\,(32.1dB)$, $P_{diss}\\approx109mW$, $\\eta\\approx42.6\\%$", "$A_p=810\\,(29.1dB)$, $P_{diss}\\approx54.5mW$, $\\eta\\approx42.6\\%$"], 0,
        r"""**1. הגברים:** $A_v=\frac91=9\;(20\log9=19.1\,dB)$; $\;I_o=\frac{9}{1k}=9\,mA$ ⇐ $A_i=\frac{9m}{0.1m}=90\;(39.1\,dB)$

**2. הספק בעומס (ערכי שיא ⇐ חלקי 2):** $P_L=\dfrac{V_pI_p}{2}=\dfrac{9\cdot9m}{2}=40.5\,mW$; $\;P_I=\dfrac{1\cdot0.1m}{2}=0.05\,mW$

**3. הגבר הספק:** $A_p=\dfrac{P_L}{P_I}=810=A_vA_i$ ⇐ $10\log810=29.1\,dB$

**4. ספקים:** $P_{DC}=2\cdot10\cdot9.5m=190\,mW$

**5. מאזן:** $P_{diss}=P_{DC}+P_I-P_L=190+0.05-40.5\approx149.6\,mW$

**6. נצילות:** $\eta=\dfrac{P_L}{P_{DC}}=\dfrac{40.5}{190}\approx21.3\%$

> ⚠️ בפתרון המקורי $P_{diss}=190-40.5$ – בלי הספק המבוא (הבדל זניח, אבל במבחן כותבים את המאזן המלא).""",
        {1: "הספק ב-dB הוא $10\\log$, לא $20\\log$.", 2: "שכח לחלק ב-2 (ערכי שיא).", 3: "ספר רק ספק אחד (95 mW)."},
        "מה שנכנס (ספקים + מבוא) = מה שיוצא (עומס) + חום."),
    mcq("b27aa2be-c986-4858-9d31-984430b84d20",
        "אופיין התמסורת של מגבר טרנזיסטורי: $v_O=10-10^{-11}e^{40v_I}$ (תקף ל-$v_I>0$, $v_O\\ge0.3V$). מה מתח הממתח שנותן $v_O=5V$, ומה הגבר המתח שם?",
        ["$V_I\\approx0.673V$, $A_v=-200$", "$V_I\\approx0.673V$, $A_v=+200$", "$V_I\\approx0.690V$, $A_v=-388$", "$V_I=0.5V$, $A_v=-40$"], 0,
        r"""**1. גבולות:** $v_I\to0^+$ ⇐ $L_+\approx10\,V$. $\;L_-=0.3\,V$: $10^{-11}e^{40v_I}=9.7$ ⇐ $v_I=\dfrac{\ln(9.7\cdot10^{11})}{40}\approx0.690\,V$

**2. ממתח ($V_O=5$):** $10^{-11}e^{40V_I}=5$ ⇐ $V_I=\dfrac{\ln(5\cdot10^{11})}{40}=\dfrac{26.94}{40}\approx0.673\,V$

**3. הגבר לאות קטן = שיפוע בנקודה:** $A_v=\dfrac{dv_O}{dv_I}=-40\cdot10^{-11}e^{40V_I}=-40(10-V_O)$

**4. הצבה:** $A_v=-40\cdot(10-5)=-200\,V/V$

> ⚠️ בפתרון המקורי ההגבר נכתב $200$ – הסימן שלילי (מגבר מהפך: מוצא יורד כשהכניסה עולה).""",
        {1: "השיפוע שלילי – $v_O$ יורד כש-$v_I$ עולה.", 2: "זה $v_I$ של $L_-$ (0.3 V), לא של 5 V.", 3: "שכח את $10^{-11}e^{40V_I}=5$ בגזירה."},
        "ממתח קובע את נקודת העבודה; ההגבר לאות קטן הוא שיפוע האופיין בה."),
    mcq("9f29e3c8-35ef-4f3a-a62a-264dfa2ec890",
        "מגבר שלוש דרגות, $R_s=100k\\Omega$, $R_L=100\\Omega$. דרגה 1: $R_i=1M$, $A_{vo}=10$, $R_o=1k$. דרגה 2: $R_i=100k$, $A_{vo}=100$, $R_o=1k$. דרגה 3: $R_i=10k$, $A_{vo}=1$, $R_o=10\\Omega$. "
        "מה $A_v=v_L/v_{i1}$ ומה $v_L/v_s$?",
        ["$A_v\\approx818\\,(58.3dB)$, $v_L/v_s\\approx744$", "$A_v=1000\\,(60dB)$, $v_L/v_s\\approx909$",
         "$A_v\\approx818$, $v_L/v_s\\approx818$", "$A_v\\approx751$, $v_L/v_s\\approx683$"], 0,
        r"""**1. הכלי – מחלק מתח בכל חיבור:** $A_{vk}=A_{vo,k}\dfrac{R_{i,k+1}}{R_{i,k+1}+R_{o,k}}$

**2. צימוד המבוא:** $\dfrac{v_{i1}}{v_s}=\dfrac{1M}{1.1M}=0.909$

**3. דרגות:** $A_{v1}=10\cdot\frac{100k}{101k}=9.9$; $\;A_{v2}=100\cdot\frac{10k}{11k}=90.9$; $\;A_{v3}=1\cdot\frac{100}{110}=0.909$

**4. כולל:** $A_v=9.9\cdot90.9\cdot0.909\approx818$ ⇐ $20\log818\approx58.3\,dB$

**5. מהמקור:** $\dfrac{v_L}{v_s}=0.909\cdot818\approx744\;(57.4\,dB)$""",
        {1: "מכפלת ההגברים בלי עומס – בלי המחלקים.", 2: "שכח את המחלק של המקור.", 3: "השתמש ב-$R_{o1}=10k$ (נתון של גרסה אחרת)."},
        "דרגה 1 – כניסה גבוהה לצימוד; דרגה 2 – הגבר; דרגה 3 – מוצא נמוך לעומס."),
]

W3 = [
    {**mcq("", "מסכם משוקלל (מהפך): $R_f=20k\\Omega$, $R_1=10k\\Omega$, $R_2=5k\\Omega$, $v_1=0.3V$, $v_2=0.2V$. מה $v_O$?",
           ["$-1.4V$", "$+1.4V$", "$-0.5V$", "$-2.0V$"], 0,
           r"""**1. אדמה וירטואלית:** ההדק המינוס ב-0 V ⇐ כל כניסה נותנת זרם $\dfrac{v_k}{R_k}$, בלי השפעה על האחרות.

**2. KCL (אין זרם לתוך המגבר):** $\dfrac{v_1}{R_1}+\dfrac{v_2}{R_2}=-\dfrac{v_O}{R_f}$

**3. נוסחה (מהלוח):** $v_O=-\left(\dfrac{R_f}{R_1}v_1+\dfrac{R_f}{R_2}v_2\right)$

**4. הצבה:** $v_O=-\left(\dfrac{20}{10}\cdot0.3+\dfrac{20}{5}\cdot0.2\right)=-(0.6+0.8)$

**5. תוצאה:** $v_O=-1.4\,V$""",
           {1: "מסכם מהפך – הסימן שלילי.", 2: "חיבר $v_1+v_2$ בלי המשקלות.", 3: "החליף את המשקלות ($R_f/R_2$ על $v_1$)."},
           "כל ערוץ מקבל משקל $R_f/R_k$ – כמו פיידר בשולחן ערבוב."),
     "id": None, "add": True, "kind": "lecture", "number": 3, "week": 3, "title": "מסכם משוקלל: מתח המוצא"},
    {**mcq("", "מגבר לוגריתמי (דיודה במשוב): $v_O=-nV_T\\ln\\dfrac{v_I}{I_sR}$, עם $n=1$, $V_T=25mV$. הכניסה גדלה מ-$0.1V$ ל-$1V$ (פי 10). כמה משתנה $v_O$?",
           ["יורד ב-$\\approx57.6mV$", "יורד פי 10", "עולה ב-$\\approx57.6mV$", "יורד ב-$25mV$"], 0,
           r"""**1. נוסחה (מהלוח):** $v_O=-nV_T\ln\dfrac{v_I}{I_sR}$

**2. הפרש בין שתי כניסות** ($I_sR$ מצטמצם): $\Delta v_O=-nV_T\ln\dfrac{v_{I2}}{v_{I1}}$

**3. הצבה:** $\Delta v_O=-1\cdot25m\cdot\ln10=-25m\cdot2.303$

**4. תוצאה:** $\Delta v_O\approx-57.6\,mV$ – כניסה גדלה פי 10, המוצא זז רק ב-57.6 mV: **דחיסת התחום הדינמי**.

(החלפת הדיודה והנגד ⇐ מגבר אקספוננציאלי.)""",
           {1: "המוצא לוגריתמי, לא ליניארי בכניסה.", 2: "יש מינוס – מגבר מהפך.", 3: "שכח את $\\ln10=2.303$."},
           "האופיין המעריכי של הדיודה במשוב הופך ללוגריתם במוצא."),
     "id": None, "add": True, "kind": "lecture", "number": 3, "week": 3, "title": "מגבר לוגריתמי: דחיסת התחום הדינמי"},
]

# the weeks, lecture N first, then practice N (his flow); class / lecture examples + practice exercises on their topics
WEEKS = {
    1: ["94a5949d", "c1439767", "272e9e57", "09c12485", "70038c31", "6a1e17c3"],
    2: ["13339d66", "161c98d1", "320d8cba", "b27aa2be", "9f29e3c8", "1261c5ba"],
    3: ["dc984255", "40f38d24", "d47baffd", "36d4b197", "258f4f74", "8539b42d", "c580b9a6", "b8898460"],  # incl. the two new lecture-3 ones
}

if __name__ == "__main__":
    check()
    for x in W3:
        x.pop("id")
    out = Path(__file__).resolve().parents[1] / "mcq-1911-linear-weeks.json"
    out.write_text(json.dumps(W1 + W2 + W3, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(W1 + W2 + W3))
    for w, ids in WEEKS.items():
        print(w, ",".join(ids))
