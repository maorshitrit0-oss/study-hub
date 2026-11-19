"""Linear circuits week exercises (weeks 1-3) in the EXAM FORMAT (his decision 19/11/2026: the exam is multiple
choice with 4 options; after answering he sees the FULL notebook method even when he was right, because in the
exam he must also show the work in the notebook). Every number below is re-computed in `check()` (python).
  python mcq_linear_1911.py -> chapters/mcq-1911-linear.json (publish inspect=exercises; "lock" keeps it)"""
import json
import math
from pathlib import Path

L = "אבגד"
_SPOT = iter([2, 0, 3, 1, 0, 2, 1, 3] * 10)  # where the right answer lands, spread over א-ד


def mcq(id_, q, opts, ans, steps, why_not, idea=""):
    """opts: 4 strings; ans: index of the right one; steps: the full notebook method (formula -> substitution -> result)."""
    want = next(_SPOT)
    order = [i for i in range(4) if i != ans]
    order.insert(want, ans)
    opts = [opts[i] for i in order]
    why_not = {order.index(i): w for i, w in why_not.items()}
    body = (q.strip() + "\n\n" + "\n\n".join(f"**{L[i]}.** {o}" for i, o in enumerate(opts))
            + "\n\n✍️ *לבחור תשובה, לכתוב במחברת את הדרך – ורק אחר כך לבדוק.*")
    sol = (f"### התשובה: **{L[want]}** ✅\n\n**הדרך המלאה (כמו במחברת):**\n\n{steps.strip()}\n\n**למה לא האחרות:**\n"
           + "\n".join(f"- **{L[i]}** – {w}" for i, w in sorted(why_not.items()))
           + (f"\n\n💡 **הרעיון:** {idea}" if idea else ""))
    return {"id": id_, "question_md": body, "solution_md": sol, "exam_style": True, "lock": True}


def check():
    """Every number used below, recomputed."""
    ok = lambda x, y, tol=0.006: abs(x - y) <= tol * max(1e-12, abs(y))  # noqa: E731
    rp, rm = 2.5e3, 10e6
    assert ok(100 + rp * rm / (rp + rm), 2600, 0.01) and ok(rp / (rp + rm), 2.5e-4) and ok(40e-3 * rp, 100)
    assert ok(1 / 100e3 + 40e-3 * rp / (rp + rm), 2e-5)
    assert ok(10e-3 / 1.1, 9.09e-3) and ok(10e-3 / 11, 0.909e-3) and ok(10e-3 / 100e3, 0.1e-6)
    assert ok(3 + 0 * 1, 3) and ok(4e3 + 1e3, 5e3)
    assert ok(100 / 110 * 100 * 0.5, 45.5)
    assert ok((5 - 0.65) / 1.02, 4.265) and ok(0.65 + 4.265e-3 * 20, 0.735)
    assert ok(0.025 / 1e-3, 25) and ok(101 * 25, 2525) and ok(0.99e-3 / 0.025, 39.6e-3) and ok(100 / 0.99e-3, 101e3)
    assert ok(20 * math.log10(100), 40) and ok(10 * math.log10(1e5), 50) and ok(20 * math.log10(0.5), -6.02)
    assert ok(8 ** 2 / 2e3, 32e-3) and ok(1 * 0.1e-3 / 2, 0.05e-3) and ok(32 / 0.05, 640) and ok(10 * math.log10(640), 28.06)
    assert ok(20 * 9.5e-3, 190e-3) and ok(190 + 0.05 - 32, 158.05) and ok(32 / 190, 0.168, 0.01)
    g = 10 * 100 / 110 * 100 * 10 / 11 * 100 / 110
    assert ok(g, 751.3) and ok(20 * math.log10(g), 57.5) and ok(g / 1.1, 683)
    ib = (5 - 0.7) / 100e3
    assert ok(100 * ib, 4.3e-3) and ok(10 - 100 * ib * 2e3, 1.4)
    assert ok(-1 * (-3) * 1, 3)  # second stage inverts -3 Vin -> 3 Vin
    assert ok(1 / (2 * math.pi * 0.05), 3.18) and ok(50 / 20, 2.5) and ok(1 / (2 * math.pi * 1e4 * 1e-7), 159.15)
    for a, gg in ((1e3, -90.83), (1e4, -99.0), (1e5, -99.9)):
        assert ok(-100 / (1 + 101 / a), gg)


Q = [
    # ---------------- week 1 ----------------
    mcq("94a5949d-1234-4dd9-b1b6-dbae96dc500f",
        "מודל פאי היברידי (פולט משותף): $r_x=100\\Omega$, $r_\\pi=2.5k\\Omega$, $r_\\mu=10M\\Omega$, $g_m=40mA/V$, $r_o=100k\\Omega$. "
        "מה ארבעת פרמטרי ה-$h$?",
        ["$h_{ie}\\approx2.6k\\Omega$, $h_{re}\\approx2.5\\cdot10^{-4}$, $h_{fe}=100$, $h_{oe}\\approx20\\mu S$",
         "$h_{ie}=2.5k\\Omega$, $h_{re}\\approx2.5\\cdot10^{-4}$, $h_{fe}=100$, $h_{oe}=10\\mu S$",
         "$h_{ie}\\approx2.6k\\Omega$, $h_{re}\\approx2.5\\cdot10^{-4}$, $h_{fe}=40$, $h_{oe}\\approx20\\mu S$",
         "$h_{ie}\\approx2.6k\\Omega$, $h_{re}=4000$, $h_{fe}=100$, $h_{oe}\\approx20mS$"], 0,
        r"""**1. $h_{11}=\left.\frac{V_1}{I_1}\right|_{V_2=0}$:** קצר במוצא ⇐ $r_\mu\parallel r_\pi\approx r_\pi$ ⇐ $h_{ie}=r_x+r_\pi=100+2500=2.6\,k\Omega$

**2. $h_{12}=\left.\frac{V_1}{V_2}\right|_{I_1=0}$:** אין זרם ב-$r_x$ ⇐ מחלק מתח: $h_{re}=\frac{r_\pi}{r_\pi+r_\mu}=\frac{2.5k}{10.0025M}\approx2.5\cdot10^{-4}$

**3. $h_{21}=\left.\frac{I_2}{I_1}\right|_{V_2=0}$:** $V_\pi=I_1r_\pi$, $I_2=g_mV_\pi$ ⇐ $h_{fe}=g_mr_\pi=40m\cdot2.5k=100$

**4. $h_{22}=\left.\frac{I_2}{V_2}\right|_{I_1=0}$:** $h_{oe}=\frac1{r_o}+\frac{g_mr_\pi}{r_\pi+r_\mu}\approx\frac{1}{100k}+\frac{100}{10M}=10\mu+10\mu=20\,\mu S$

> ⚠️ בשקף נכתב $mmho$ – היחידה הנכונה $S$ (מהו), $20\,\mu S$.""",
        {1: "שכח את $r_x$ ב-$h_{ie}$ ואת תרומת המשוב ב-$h_{oe}$.", 2: "$h_{fe}$ הוא $g_mr_\\pi$, לא $g_m$ במ\"א/וולט.", 3: "הפך את היחס ב-$h_{re}$ וטעה ביחידות ב-$h_{oe}$."},
        "כל פרמטר = תנאי שפה אחד (קצר $V=0$ או נתק $I=0$) על מעגל התמורה."),
    mcq("c1439767-fb88-47c5-b043-ca46e45a0083",
        "מיקרופון: $v_s=10mV$, $R_s=100k\\Omega$. מה המתח בכניסת מגבר עם (א) $R_{in}=1M\\Omega$; (ב) $R_{in}=10k\\Omega$?",
        ["(א) $9.09mV$; (ב) $0.91mV$", "(א) $10mV$; (ב) $10mV$", "(א) $0.91mV$; (ב) $9.09mV$", "(א) $9.09mV$; (ב) $1mV$"], 0,
        r"""**1. נוסחה (מחלק מתח):** $v_{in}=v_s\dfrac{R_{in}}{R_{in}+R_s}$

**2. (א):** $v_{in}=10m\cdot\dfrac{1M}{1.1M}\approx9.09\,mV$ – כמעט כל האות.

**3. (ב):** $v_{in}=10m\cdot\dfrac{10k}{110k}\approx0.91\,mV$ – הולכים לאיבוד 91%.

**4. נורטון שקול:** $i_s=\dfrac{v_s}{R_s}=\dfrac{10m}{100k}=0.1\,\mu A$ במקביל ל-$100\,k\Omega$.""",
        {1: "התעלם מ-$R_s$ – מקור לא אידאלי.", 2: "החליף בין המקרים.", 3: "חישב $R_{in}/R_s$ במקום מחלק מתח."},
        "לצימוד מתח צריך $R_{in}\\gg R_s$."),
    mcq("09c12485-6696-4a9d-a682-8692ab25dd04",
        "רשת T: $R_1=1k$ בכניסה, $R_2=2k$ ביציאה, $R_3=3k$ מהצומת לאדמה. מה פרמטרי ה-$z$?",
        ["$z_{11}=4k, z_{12}=z_{21}=3k, z_{22}=5k$", "$z_{11}=1k, z_{12}=z_{21}=3k, z_{22}=2k$",
         "$z_{11}=4k, z_{12}=3k, z_{21}=-3k, z_{22}=5k$", "$z_{11}=6k, z_{12}=z_{21}=3k, z_{22}=6k$"], 0,
        r"""**1. $z_{11}=\left.\frac{V_1}{I_1}\right|_{I_2=0}$:** הזרם עובר ב-$R_1$ וב-$R_3$ ⇐ $z_{11}=1k+3k=4\,k\Omega$

**2. $z_{21}=\left.\frac{V_2}{I_1}\right|_{I_2=0}$:** אין זרם ב-$R_2$ ⇐ $V_2=I_1R_3$ ⇐ $z_{21}=3\,k\Omega$

**3. $z_{12}=\left.\frac{V_1}{I_2}\right|_{I_1=0}$:** באותו אופן ⇐ $z_{12}=R_3=3\,k\Omega$

**4. $z_{22}=\left.\frac{V_2}{I_2}\right|_{I_1=0}$:** $z_{22}=R_2+R_3=5\,k\Omega$

**5. בדיקה:** $z_{12}=z_{21}$ ✓ רשת פסיבית הדדית.""",
        {1: "שכח את $R_3$ שמשותף לשני השערים.", 2: "ברשת פסיבית $z_{12}=z_{21}$, בלי סימן הפוך.", 3: "חיבר את כל שלושת הנגדים."}),
    mcq("70038c31-2d1e-465c-8767-076574814e1c",
        "מגבר מתח: $R_i=100k$, $A_{vo}=100$, $R_o=1k$. מקור $R_s=10k$, עומס $R_L=1k$. מה $v_o/v_s$?",
        ["$\\approx45.5$", "$100$", "$\\approx90.9$", "$50$"], 0,
        r"""**1. נוסחה (מחלק בכניסה × הגבר × מחלק ביציאה):** $\dfrac{v_o}{v_s}=\dfrac{R_i}{R_i+R_s}\cdot A_{vo}\cdot\dfrac{R_L}{R_L+R_o}$

**2. הצבה:** $\dfrac{100k}{110k}\cdot100\cdot\dfrac{1k}{2k}=0.909\cdot100\cdot0.5$

**3. תוצאה:** $\dfrac{v_o}{v_s}\approx45.5\,V/V$""",
        {1: "זה הגבר בלי עומס ובלי מקור – אידאלי.", 2: "שכח את המחלק ביציאה.", 3: "שכח את המחלק בכניסה."}),
    mcq("7481fc52-e3ed-4948-b6a5-bf9c4cae84a4",
        "$V_{DD}=5V$, $R=1k\\Omega$ ודיודה בטור. מה הזרם ומתח הדיודה במודל הליניארי ($V_{D0}=0.65V$, $r_D=20\\Omega$)?",
        ["$I_D\\approx4.26mA$, $V_D\\approx0.735V$", "$I_D=4.3mA$, $V_D=0.7V$", "$I_D=4.35mA$, $V_D=0.65V$", "$I_D\\approx4.26mA$, $V_D=0.65V$"], 0,
        r"""**1. KVL:** $V_{DD}=I_D(R+r_D)+V_{D0}$ ⇐ $I_D=\dfrac{V_{DD}-V_{D0}}{R+r_D}$

**2. הצבה:** $I_D=\dfrac{5-0.65}{1000+20}=\dfrac{4.35}{1.02k}$

**3. תוצאה:** $I_D\approx4.265\,mA$

**4. מתח הדיודה:** $V_D=V_{D0}+I_Dr_D=0.65+4.265m\cdot20=0.65+0.085=0.735\,V$

(במודל מפל קבוע: $I_D=\frac{5-0.7}{1k}=4.3\,mA$, $V_D=0.7\,V$.)""",
        {1: "זו תוצאת מודל המפל הקבוע (סעיף א).", 2: "התעלם מ-$r_D$.", 3: "שכח את המפל על $r_D$ במתח הדיודה."}),
    mcq("02e76b3d-0ed1-4979-b544-b483b0ea72e2",
        "BJT: $\\beta=100$, $I_E=1mA$, $I_C=0.99mA$, $V_A=100V$, $V_T=25mV$. מה $r_\\pi$, $g_m$, $r_o$?",
        ["$r_\\pi\\approx2.53k\\Omega$, $g_m=39.6mA/V$, $r_o\\approx101k\\Omega$", "$r_\\pi=25\\Omega$, $g_m=39.6mA/V$, $r_o\\approx101k\\Omega$",
         "$r_\\pi\\approx2.53k\\Omega$, $g_m=0.0396mA/V$, $r_o=100\\Omega$", "$r_\\pi=2.5M\\Omega$, $g_m=40A/V$, $r_o\\approx101k\\Omega$"], 0,
        r"""**1. $r_e=\dfrac{V_T}{I_E}=\dfrac{25m}{1m}=25\,\Omega$**

**2. $r_\pi=(\beta+1)r_e=101\cdot25=2525\,\Omega\approx2.53\,k\Omega$**

**3. $g_m=\dfrac{I_C}{V_T}=\dfrac{0.99m}{25m}=39.6\,mA/V$**

**4. $r_o=\dfrac{V_A}{I_C}=\dfrac{100}{0.99m}\approx101\,k\Omega$**""",
        {1: "זה $r_e$, לא $r_\\pi$.", 2: "טעויות יחידות ב-$g_m$ וב-$r_o$.", 3: "טעויות של פי 1000."}),
    # ---------------- week 2 ----------------
    mcq("1261c5ba-a23f-412b-a083-5f23930fa5f9",
        "(א) $A_v=100$ – כמה dB? (ב) $A_v=100$, $A_i=1000$ – מה הגבר ההספק ב-dB? (ג) $A_v=0.5$ – כמה dB?",
        ["$40dB$; $50dB$; $\\approx-6dB$", "$20dB$; $50dB$; $\\approx-3dB$", "$40dB$; $100dB$; $\\approx-6dB$", "$40dB$; $50dB$; $\\approx+6dB$"], 0,
        r"""**1. נוסחאות:** מתח/זרם: $20\log|A|$; הספק: $10\log A_p$

**2. (א):** $20\log100=20\cdot2=40\,dB$

**3. (ב):** $A_p=A_vA_i=10^5$ ⇐ $10\log10^5=50\,dB$

**4. (ג):** $20\log0.5=20\cdot(-0.301)\approx-6\,dB$ – הנחתה.""",
        {1: "השתמש ב-$10\\log$ למתח.", 2: "השתמש ב-$20\\log$ להספק.", 3: "הגבר קטן מ-1 נותן dB **שלילי**."}),
    mcq("39a78ac1-8388-4daa-9859-8ea3bd96b59c",
        "מגבר מוזן מ-$\\pm10V$, מושך $9.5mA$ מכל ספק. מוצא: סינוס $8V$ שיא על $1k\\Omega$. מבוא: $1V$ שיא, $0.1mA$ שיא. מה הגבר ההספק, ההספק שמתבזבז לחום והנצילות?",
        ["$A_p=640\\,(28dB)$, $P_{diss}\\approx158mW$, $\\eta\\approx16.8\\%$", "$A_p=640\\,(56dB)$, $P_{diss}\\approx158mW$, $\\eta\\approx16.8\\%$",
         "$A_p=640\\,(28dB)$, $P_{diss}\\approx126mW$, $\\eta\\approx33.7\\%$", "$A_p=1280\\,(31dB)$, $P_{diss}\\approx126mW$, $\\eta\\approx33.7\\%$"], 0,
        r"""**1. הספק בעומס (שיא ⇐ חלקי 2):** $P_L=\dfrac{V_p^2}{2R_L}=\dfrac{64}{2\cdot1k}=32\,mW$

**2. הספק במבוא:** $P_I=\dfrac{V_pI_p}{2}=\dfrac{1\cdot0.1m}{2}=0.05\,mW$

**3. הגברים:** $A_v=8\,(18\,dB)$; $A_i=\frac{8m}{0.1m}=80\,(38\,dB)$; $A_p=\frac{32}{0.05}=640$ ⇐ $10\log640=28\,dB$

**4. ספקים:** $P_{DC}=10\cdot9.5m+10\cdot9.5m=190\,mW$

**5. מאזן:** $P_{diss}=P_{DC}+P_I-P_L=190+0.05-32\approx158\,mW$

**6. נצילות:** $\eta=\dfrac{P_L}{P_{DC}}=\dfrac{32}{190}\approx16.8\%$""",
        {1: "הספק ב-dB הוא $10\\log$.", 2: "ספר רק ספק אחד (95 mW).", 3: "שכח את החלוקה ב-2 (ערך שיא, לא אפקטיבי)."},
        "מה שנכנס (ספקים + מבוא) = מה שיוצא (עומס) + חום."),
    mcq("b9e4e6c0-e330-4e33-8ff1-beaca83c47ba",
        "$R_s=100k$. דרגה 1: $R_i=1M, A_{vo}=10, R_o=10k$. דרגה 2: $R_i=100k, A_{vo}=100, R_o=1k$. דרגה 3: $R_i=10k, A_{vo}=1, R_o=10\\Omega$. $R_L=100\\Omega$. מה $v_o/v_s$?",
        ["$\\approx683$", "$1000$", "$\\approx751$", "$\\approx909$"], 0,
        r"""**1. כניסה:** $\dfrac{v_{i1}}{v_s}=\dfrac{1M}{1.1M}=0.909$

**2. דרגה 1 (עמוסה ב-$R_{i2}$):** $A_1=10\cdot\dfrac{100k}{110k}=9.09$

**3. דרגה 2 (עמוסה ב-$R_{i3}$):** $A_2=100\cdot\dfrac{10k}{11k}=90.9$

**4. דרגה 3 (עמוסה ב-$R_L$):** $A_3=1\cdot\dfrac{100}{110}=0.909$

**5. כולל:** $\dfrac{v_o}{v_{i1}}=9.09\cdot90.9\cdot0.909\approx751\;(57.5\,dB)$ ⇐ $\dfrac{v_o}{v_s}=0.909\cdot751\approx683$""",
        {1: "מכפלת ההגברים בלי עומס – מתעלם מכל המחלקים.", 2: "זה $v_o/v_{i1}$, בלי המחלק של המקור.", 3: "לקח רק חלק מהמחלקים."}),
    mcq("e936fb16-b6f2-41b0-bbf3-d38c67af6bce",
        "NPN, $\\beta=100$: $V_{CC}=10V$, $R_C=2k$; הבסיס דרך $R_B=100k$ ל-$+5V$; אמיטר מוארק. מה $I_C$ ו-$V_C$?",
        ["$I_C=4.3mA$, $V_C=1.4V$", "$I_C=5mA$, $V_C=0V$", "$I_C=9.3mA$, $V_C<0$", "$I_C=0.043mA$, $V_C\\approx9.9V$"], 0,
        r"""**1. זרם בסיס (KVL בלולאת הבסיס):** $I_B=\dfrac{V_{BB}-V_{BE}}{R_B}=\dfrac{5-0.7}{100k}=0.043\,mA$

**2. הנחה – פעיל:** $I_C=\beta I_B=100\cdot0.043m=4.3\,mA$, $\;I_E=(\beta+1)I_B\approx4.34\,mA$

**3. מתח הקולקטור:** $V_C=V_{CC}-I_CR_C=10-4.3\cdot2=1.4\,V$

**4. בדיקה:** $V_{CE}=1.4>0.2$ ✓ פעיל; $V_B=0.7\,V$.""",
        {1: "הניח רוויה בלי לחשב.", 2: "השתמש ב-$V_{CC}=10$ בלולאת הבסיס.", 3: "זה $I_B$, לא $I_C$."}),
    # ---------------- week 3 ----------------
    mcq("dc984255-2361-4781-9ec4-5955c1ee700e",
        "מגבר מהפך: נגד כניסה $R_1$, במשוב $R_2\\parallel C_2$. מה פונקציית התמסורת ותדר הקוטב?",
        ["$-\\dfrac{R_2/R_1}{1+sR_2C_2}$, $\\ \\omega_0=\\dfrac1{R_2C_2}$", "$-\\dfrac{R_2/R_1}{1+sR_1C_2}$, $\\ \\omega_0=\\dfrac1{R_1C_2}$",
         "$-\\dfrac{sR_2C_2}{1+sR_2C_2}$, $\\ \\omega_0=\\dfrac1{R_2C_2}$", "$-\\dfrac{1}{sR_1C_2}$, $\\ \\omega_0=0$"], 0,
        r"""**1. עכבת המשוב:** $Z_2=R_2\parallel\dfrac1{sC_2}=\dfrac{R_2\cdot\frac1{sC_2}}{R_2+\frac1{sC_2}}$ ⇐ (כפל ב-$sC_2$) $Z_2=\dfrac{R_2}{1+sR_2C_2}$

**2. מגבר מהפך:** $H(s)=-\dfrac{Z_2}{Z_1}=-\dfrac{R_2/R_1}{1+sR_2C_2}$

**3. קוטב:** המכנה מתאפס ב-$s=-\frac1{R_2C_2}$ ⇐ $\omega_0=\dfrac1{R_2C_2}$ – מסנן מעביר נמוכים.""",
        {1: "הקוטב נקבע מרכיבי המשוב, לא מנגד הכניסה.", 2: "זה מעביר גבוהים – הקבל לא בכניסה.", 3: "זה אינטגרטור בלי $R_2$."}),
    mcq("258f4f74-7732-4159-bee1-ca3eb7e03fa4",
        "שני מגברי שרת: הראשון מהפך ($10k$ כניסה, $30k$ משוב), השני מהפך ($40k$, $40k$), ונגד משוב גלובלי $20k$ מהמוצא לכניסה. מה $A_v$ ו-$R_{in}$?",
        ["$A_v=3$, $R_{in}\\to\\infty$", "$A_v=-3$, $R_{in}=10k$", "$A_v=3$, $R_{in}=10k$", "$A_v=3$, $R_{in}=6.67k$"], 0,
        r"""**1. מגבר 1 (אדמה מדומה):** $\dfrac{V_{in}}{10k}=\dfrac{-V_x}{30k}$ ⇐ $V_x=-3V_{in}$

**2. מגבר 2:** $\dfrac{V_x}{40k}=\dfrac{-V_{out}}{40k}$ ⇐ $V_{out}=-V_x=3V_{in}$ ⇐ $A_v=3$

**3. זרם הכניסה:** $I_{in}=\dfrac{V_{in}}{10k}+\dfrac{V_{in}-V_{out}}{20k}=\dfrac{V_{in}}{10k}+\dfrac{-2V_{in}}{20k}=0$

**4. תוצאה:** $R_{in}=\dfrac{V_{in}}{I_{in}}\to\infty$""",
        {1: "שני מהפכים ⇐ הסימן חיובי.", 2: "שכח את הזרם דרך המשוב הגלובלי.", 3: "חיבר את הנגדים במקביל בלי לשים לב שהזרם במשוב **חוזר** לכניסה."},
        "המשוב הגלובלי מחזיר בדיוק את הזרם שהמגבר הראשון לוקח."),
    mcq("8539b42d-a6e8-4e12-bd28-a190e933f550",
        "מעביר נמוכים פעיל: $R_1=20k$, $R_2=50k$, $C=1\\mu F$ (במקביל ל-$R_2$). מה הגבר ה-DC ותדר החיתוך?",
        ["$-2.5$, $f_c\\approx3.18Hz$", "$-2.5$, $f_c=20Hz$", "$-0.4$, $f_c\\approx7.96Hz$", "$-2.5$, $f_c\\approx7.96Hz$"], 0,
        r"""**1. עכבת משוב:** $Z_f=\dfrac{R_2}{1+j\omega R_2C}$, $\;R_2C=50k\cdot1\mu=0.05\,s$

**2. תמסורת:** $H=-\dfrac{Z_f}{R_1}=\dfrac{-R_2/R_1}{1+j\omega R_2C}=\dfrac{-2.5}{1+j0.05\omega}$ ⇐ הגבר DC $=-2.5$ ($\approx8\,dB$)

**3. חיתוך:** $\omega_c=\dfrac1{R_2C}=20\,rad/s$ ⇐ $f_c=\dfrac{20}{2\pi}\approx3.18\,Hz$""",
        {1: "20 הוא $\\omega_c$ ב-rad/s, לא ב-Hz.", 2: "הפך את יחס הנגדים והשתמש ב-$R_1$ בקוטב.", 3: "הקוטב עם $R_1C$ – הקבל במקביל ל-$R_2$."}),
    mcq("c580b9a6-a3a4-4049-97df-99524b351737",
        "מעביר גבוהים פעיל: הגבר $0dB$ בתדרים גבוהים, $f_c=10kHz$, קבל כניסה $C=0.1\\mu F$. מה $R_1$ ו-$R_2$?",
        ["$R_1=R_2\\approx159\\Omega$", "$R_1=R_2=1k\\Omega$", "$R_1\\approx159\\Omega$, $R_2=0$", "$R_1=R_2\\approx1.59k\\Omega$"], 0,
        r"""**1. הגבר בתדר גבוה:** הקבל קצר ⇐ $|H|=\dfrac{R_2}{R_1}$; $\;20\log\dfrac{R_2}{R_1}=0$ ⇐ $R_2=R_1$

**2. חיתוך (ענף הכניסה $R_1$ בטור עם $C$):** $f_c=\dfrac{1}{2\pi R_1C}$ ⇐ $R_1=\dfrac1{2\pi f_cC}$

**3. הצבה:** $R_1=\dfrac{1}{2\pi\cdot10^4\cdot10^{-7}}=\dfrac{1}{6.283\cdot10^{-3}}$

**4. תוצאה:** $R_1=R_2\approx159\,\Omega$""",
        {1: "ניחוש, לא מחושב.", 2: "0 dB פירושו הגבר 1, לא 0.", 3: "טעות של פי 10 בחזקות של $C$."}),
    mcq("b8898460-7086-4056-9bf0-19559bcadda1",
        "מגבר מהפך ($R_1$, $R_2$) עם הגבר חוג פתוח סופי $A$. מה ההגבר בחוג סגור?",
        ["$-\\dfrac{R_2/R_1}{1+\\frac1A\\left(1+\\frac{R_2}{R_1}\\right)}$", "$-\\dfrac{R_2/R_1}{1+\\frac{1}{A}}$",
         "$-\\dfrac{R_2}{R_1}\\left(1+\\frac1A\\right)$", "$-\\dfrac{A}{1+A\\frac{R_2}{R_1}}$"], 0,
        r"""**1. המגבר:** $V_{out}=-AV_-$ ⇐ $V_-=-\dfrac{V_{out}}{A}$ (כבר לא אדמה מדומה מושלמת)

**2. KCL בהדק המינוס:** $\dfrac{V_{in}-V_-}{R_1}=\dfrac{V_--V_{out}}{R_2}$

**3. הצבה:** $\dfrac{V_{in}+V_{out}/A}{R_1}=\dfrac{-V_{out}/A-V_{out}}{R_2}$ ⇐ כפל ב-$R_2$ ובידוד:

$$\frac{V_{out}}{V_{in}}=-\frac{R_2/R_1}{1+\frac1A\left(1+\frac{R_2}{R_1}\right)}$$

**4. גבול:** $A\to\infty$ ⇐ $-\dfrac{R_2}{R_1}$ ✓ האידאלי.""",
        {1: "חסר ה\"הגבר רעש\" $1+R_2/R_1$ בתיקון.", 2: "התיקון במכנה, לא כפל.", 3: "ביטוי של מגבר לא מהפך במשוב הפוך – לא מתכנס ל-$-R_2/R_1$."}),
    mcq("40f38d24-6dfa-4e67-ac39-962d596444fd",
        "מגבר מהפך: $R_1=1k$, $R_2=100k$ (אידאלי $-100$). מה ההגבר ואחוז השגיאה עבור $A=10^3$?",
        ["$-90.83$, שגיאה $\\approx9.2\\%$", "$-99.9$, שגיאה $0.1\\%$", "$-90.91$, שגיאה $\\approx9.1\\%$", "$-100$, שגיאה $0$"], 0,
        r"""**1. נוסחה:** $G=\dfrac{-R_2/R_1}{1+\frac{1+R_2/R_1}{A}}$, $\;R_2/R_1=100$ ⇐ התיקון $\frac{101}{A}$

**2. הצבה ($A=10^3$):** $G=\dfrac{-100}{1+0.101}=\dfrac{-100}{1.101}$

**3. תוצאה:** $G\approx-90.83$; שגיאה $=\dfrac{100-90.83}{100}\approx9.17\%$

**4. השוואה:** $A=10^4$ ⇐ $-99.0$ (1%); $\;A=10^5$ ⇐ $-99.9$ (0.1%).""",
        {1: "זה עבור $A=10^5$.", 2: "השתמש ב-$1+\\frac{100}{A}$ – חסר ה-1.", 3: "זה האידאלי – $A$ סופי."},
        "השגיאה $\\approx\\frac{1+R_2/R_1}{A}$."),
    mcq("76240755-63a7-42b6-96b6-e48bdad2ddd9",
        "(1) מגבר לא מהפך: $10k$ לאדמה מהדק המינוס, $100k$ משוב. (2) מגבר מהפך: $10k$ כניסה, $100k$ משוב. מה ההגברים?",
        ["(1) $11$; (2) $-10$", "(1) $10$; (2) $-10$", "(1) $11$; (2) $-11$", "(1) $-10$; (2) $11$"], 0,
        r"""**1. לא מהפך:** $G=1+\dfrac{R_2}{R_1}=1+\dfrac{100k}{10k}=11$

**2. מהפך:** $G=-\dfrac{R_2}{R_1}=-\dfrac{100k}{10k}=-10$""",
        {1: "בלא מהפך יש $1+$.", 2: "במהפך אין $1+$.", 3: "החליף בין המעגלים."}),
]

if __name__ == "__main__":
    check()
    root = Path(__file__).resolve().parents[1]
    (root / "mcq-1911-linear.json").write_text(json.dumps(Q, ensure_ascii=False, indent=1), encoding="utf-8")
    print("linear", len(Q))
