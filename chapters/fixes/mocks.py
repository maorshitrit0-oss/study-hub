"""Full mock exams in the REAL exam format (his request 09/11/2026: "if it is MCQ - MCQ, the real number of questions,
show the solution and check yourself"). Adds "mock" (+ the format line) to chapters/<key>_forecast.json.
Every number here was recomputed in Python before publishing."""
import json
from pathlib import Path

CH = Path(__file__).resolve().parents[1]
M = {}


def mcq(topic, points, chance, q, options, answer, sol, source=""):
    return {"type": "mcq", "topic": topic, "points": points, "chance": chance, "question_md": q, "options": options,
            "answer": answer, "solution_md": sol, "source": source}


def open_q(topic, points, chance, q, sol, source=""):
    return {"type": "open", "topic": topic, "points": points, "chance": chance, "question_md": q, "solution_md": sol, "source": source}


# ---------------- Random signals: 4 open questions, answer 1, 2 and 3 or 4 (his exam, moed B summer 5786) -------------
M["rnd"] = ("4 שאלות פתוחות, שעה וחצי (כשעתיים עם תוספת): עונים על 1, 2 ועל 3 או 4. מותרים 3 דפים (6 עמודים).", [
    open_q("סמ\"ר – משרעות אקראיות", 30, 95, r"""
$X(t)=A\cos(2\pi f_0t)+B\sin(2\pi f_0t)$, כאשר $A,B$ בלתי תלויים, $E[A]=E[B]=0$ ו-$\mathrm{Var}A=\mathrm{Var}B=2$.
1. (10) מצא/י את $E[X(t)]$ ואת $R_X(t_1,t_2)$.
2. (10) האם $X(t)$ סמ"ר? נמק/י.
3. (10) $Y(t)=A\cos(2\pi f_0t)-B\sin(2\pi f_0t)$. מצא/י את $R_{XY}(t_1,t_2)$. האם $X,Y$ סמ"ר במשותף?""", r"""
**1.** $E[X]=E[A]\cos+E[B]\sin=0$.
$R_X=E[A^2]c_1c_2+E[AB](\dots)+E[B^2]s_1s_2=2c_1c_2+2s_1s_2=2\cos\big(2\pi f_0(t_1-t_2)\big)$
(בלתי תלויים ⇐ $E[AB]=E[A]E[B]=0$; $\cos a\cos b+\sin a\sin b=\cos(a-b)$.)

**2.** כן: תוחלת קבועה (0), ו-$R_X=2\cos(2\pi f_0\tau)$ תלוי רק ב-$\tau=t_2-t_1$. (זה עובד **כי** $\mathrm{Var}A=\mathrm{Var}B$ – לכתוב את זה!)

**3.** $R_{XY}=2c_1c_2-2s_1s_2=2\cos\big(2\pi f_0(t_1+t_2)\big)$ – תלוי ב-$t_1+t_2$ ⇐ **לא** סמ"ר במשותף (כל אחד לבד כן).""",
           "כמו שאלה 1 במבחן שלך"),
    open_q("רעש דרך מסנן", 30, 95, r"""
רעש לבן עם $S_X(f)=1$ עובר במסנן $H(f)=1-\frac{|f|}{2}$ עבור $|f|\le2$ ו-$0$ אחרת.
1. (10) מצא/י את $S_Y(f)$ ושרטט/י (עם ערכים על הצירים).
2. (10) חשב/י את הספק המוצא.
3. (10) הרעש גאוסי. חשב/י $P(Y(t)>1)$.""", r"""
**1.** $S_Y=|H|^2S_X=\left(1-\frac{|f|}2\right)^2$ עבור $|f|\le2$, **ו-0 אחרת**. שרטוט: 1 ב-$f=0$, יורד ל-0 ב-$f=\pm2$ (משיק לציר).

**2.** $P_Y=\int S_Y=2\int_0^2\left(1-\frac f2\right)^2df$. עם $u=1-\frac f2$, $df=-2du$: $2\cdot2\int_0^1u^2du=\frac43$.

**3.** $m_Y=m_X H(0)=0$, $\sigma_Y^2=R_Y(0)=P_Y=\frac43$. $Y\sim N(0,\frac43)$:
$P(Y>1)=Q\!\left(\frac{1}{\sqrt{4/3}}\right)=Q(0.866)\approx0.193$.""", "כמו שאלה 2 במבחן שלך"),
    open_q("תהליך פואסון", 20, 80, r"""
לקוחות מגיעים לפי תהליך פואסון בקצב $\lambda=2$ לדקה.
1. (7) מה ההסתברות שבשלוש הדקות הראשונות יגיעו בדיוק 4 לקוחות?
2. (7) מה ההסתברות שבדקה הראשונה לא יגיע אף אחד, ובשלוש הדקות הראשונות יגיעו בדיוק 4?
3. (6) ידוע שבדקה הראשונה הגיעו 2. מה מספר הלקוחות הצפוי עד סוף הדקה השלישית?""", r"""
**1.** $\lambda t=6$: $P=\frac{6^4}{4!}e^{-6}=54e^{-6}\approx0.134$.

**2.** קטעים זרים: 0 ב-$[0,1]$ ו-4 ב-$[1,3]$ ($\lambda t=4$):
$e^{-2}\cdot\frac{4^4}{4!}e^{-4}=\frac{32}3e^{-6}\approx0.026$.

**3.** תוספות בלתי תלויות: $E[N(3)\mid N(1)=2]=2+\lambda\cdot2=2+4=6$.""", "כמו שאלה 3 במבחן שלך"),
    open_q("משערך לינארי – משתנים רציפים", 20, 80, r"""
$X\sim U[0,2]$, $N\sim\text{Exp}(2)$ (צפיפות $2e^{-2n}$, $n\ge0$), בלתי תלויים, ו-$Y=X+N$.
נתון: $\int_0^\infty xe^{-ax}dx=\frac1{a^2}$, $\int_0^\infty x^2e^{-ax}dx=\frac2{a^3}$.
1. (10) חשב/י $E[Y]$, $\mathrm{Var}(Y)$ ו-$\mathrm{Cov}(X,Y)$.
2. (10) מצא/י את המשערך הלינארי האופטימלי של $X$ בהינתן $Y$ ואת השגיאה.""", r"""
**1.** $E[X]=1$, $\mathrm{Var}X=\frac{2^2}{12}=\frac13$. $E[N]=2\cdot\frac1{4}=\frac12$, $E[N^2]=2\cdot\frac2{8}=\frac12$, $\mathrm{Var}N=\frac12-\frac14=\frac14$.
$E[Y]=\frac32$, $\mathrm{Var}Y=\frac13+\frac14=\frac7{12}$, $\mathrm{Cov}(X,Y)=\mathrm{Var}X=\frac13$.

**2.** $\hat X=1+\frac{1/3}{7/12}\left(Y-\frac32\right)=1+\frac47\left(Y-\frac32\right)$.
שגיאה: $\frac13-\frac{(1/3)^2}{7/12}=\frac13-\frac4{21}=\frac17$.""", "כמו שאלה 4 במבחן שלך"),
])

# ---------------- Linear circuits: 6 MCQ, each solved in the notebook (moed A 5786, 9/2/2026) --------------------
M["linear"] = ("6 שאלות רב-ברירה (כמו מועד א' תשפ\"ו), לכל אחת פתרון מלא במחברת – בלי פתרון אין ניקוד. שעה וחצי.", [
    mcq("נקודת עבודה של BJT", None, 90, r"""
במעגל פולט משותף: $V_{CC}=10\,V$, $R_C=1\,k\Omega$, $R_B=10\,k\Omega$ בין $V_{BB}$ לבסיס, אמיטר מוארק. $\beta=50$, $V_{BE}=0.7\,V$.
מה צריך להיות $V_{BB}$ כדי ש-$V_{CE}=5\,V$?""", [r"$1.7\,V$", r"$1.9\,V$", r"$2.1\,V$", r"$2.3\,V$"], 0, r"""
$I_C=\frac{V_{CC}-V_{CE}}{R_C}=\frac{5}{1k}=5\,mA$ ⇐ $I_B=\frac{I_C}\beta=0.1\,mA$ ⇐ $V_{BB}=V_{BE}+I_BR_B=0.7+0.1m\cdot10k=1.7\,V$.""",
        "שאלה 1, מועד א' תשפ\"ו"),
    mcq("יציבות נקודת העבודה", None, 85, r"""
$V_{CC}=12\,V$, $R_C=560\,\Omega$, $R_B=100\,k\Omega$ מ-$V_{CC}$ לבסיס, $V_{BE}=0.7\,V$. $\beta$ משתנה מ-100 ל-150.
בכמה אחוזים גדל $I_C$, והאם הטרנזיסטור נשאר פעיל?""",
        ["ב-50%, ונשאר פעיל ($V_{CE}\approx2.5\,V$)", "ב-50%, ונכנס לרוויה", "ב-33%, ונשאר פעיל", "לא משתנה – $I_C$ נקבע ע״י $R_C$"], 0, r"""
$I_B=\frac{12-0.7}{100k}=0.113\,mA$ (לא תלוי ב-$\beta$).
$\beta=100$: $I_C=11.3\,mA$, $V_{CE}=12-11.3m\cdot560=5.67\,V$.
$\beta=150$: $I_C=16.95\,mA$ (+50%), $V_{CE}=12-9.49=2.51\,V>0.2$ ⇐ עדיין פעיל.
(עם $R_E=100\,\Omega$ השינוי יורד רק ל-44% – ממתח בסיס כזה $R_E$ לא מספיק.)""", "שאלה 2, מועד ב' תשפ\"ד"),
    mcq("ביטוי להגבר – מגבר שרת", None, 95, r"""
מסכם מהפך: $V_1$ דרך $R_1$, $V_2$ דרך $R_2$ להדק המינוס, משוב $R_f$, הדק הפלוס מוארק. בוחרים $R_f=30\,k\Omega$.
אילו נגדים נותנים $V_o=-\left(3V_1+\frac12V_2\right)$?""",
        [r"$R_1=10k,\ R_2=60k$", r"$R_1=90k,\ R_2=15k$", r"$R_1=10k,\ R_2=15k$", r"$R_1=3k,\ R_2=60k$"], 0, r"""
אדמה וירטואלית ⇐ $V_o=-\left(\frac{R_f}{R_1}V_1+\frac{R_f}{R_2}V_2\right)$.
$\frac{30k}{R_1}=3$ ⇐ $R_1=10k$; $\frac{30k}{R_2}=\frac12$ ⇐ $R_2=60k$.""", "סוג שאלה 4, מועד א' תשפ\"ו"),
    mcq("מגבר מהפך עם A סופי", None, 70, r"""
מגבר מהפך עם $R_1=1\,k\Omega$, $R_2=100\,k\Omega$ ומגבר שרת עם הגבר חוג פתוח $A=1000$. מה ההגבר בחוג סגור?""",
        [r"$-90.8$", r"$-100$", r"$-99.0$", r"$-110$"], 0, r"""
$G=\frac{-R_2/R_1}{1+\frac{1+R_2/R_1}A}=\frac{-100}{1+\frac{101}{1000}}=\frac{-100}{1.101}\approx-90.8$.""", "הרצאה 3"),
    mcq("הגבר CE עם נגד אמיטר", None, 75, r"""
מגבר פולט משותף: $I_C=10.26\,mA$, $V_T=25\,mV$, $\beta=100$, $R_C=560\,\Omega$, ונגד $R_E=100\,\Omega$ **לא מקוצר**. מה ההגבר בקירוב?""",
        [r"$\approx-5.5$", r"$\approx-230$", r"$\approx-56$", r"$\approx+5.5$"], 0, r"""
$r_e=\frac{V_T}{I_E}\approx\frac{25mV}{10.36mA}\approx2.4\,\Omega$.
$A_v\approx-\frac{R_C}{r_e+R_E}=-\frac{560}{102.4}\approx-5.5$.
(בלי $R_E$: $-g_mR_C\approx-230$ – הנגד מקטין את ההגבר פי 40 תמורת יציבות.)""", "שאלה 2ד, מועד ב' תשפ\"ד"),
    mcq("משוב בשלוש דרגות", None, 85, r"""
מגבר תלת-דרגתי ($Q_1,Q_2,Q_3$) עם נגד משוב $R_F=1\,k\Omega$ בין האמיטר של $Q_3$ לאמיטר של $Q_1$; $R_{E1}=100\,\Omega$, $R_{E2}=150\,\Omega$.
מה סוג המשוב, $\beta$, וההגבר בחוג סגור כשההגבר בחוג פתוח אינסופי?""",
        [r"טור-טור, $\beta=12\,\Omega$, $A_f=0.0833\,℧$", r"טור-טור, $\beta=12\,A/A$, $A_f=0.0833\,A/A$",
         r"מקביל-מקביל, $\beta=12\,℧$, $A_f=0.0833\,\Omega$", r"טור-מקביל, $\beta=12\,V/V$, $A_f=0.0833\,V/V$"], 0, r"""
דוגמים **זרם** במוצא (באמיטר $Q_3$) ומחזירים **מתח** בטור לכניסה (באמיטר $Q_1$) ⇐ טור-טור (מגבר טרנס-מוליכות).
$\beta=\frac{V_f}{I_o}=\frac{R_{E1}R_{E2}}{R_{E1}+R_F+R_{E2}}=\frac{100\cdot150}{1250}=12\,\Omega$.
$A\to\infty$ ⇐ $A_f\approx\frac1\beta=0.0833\,℧$ (יחידות של מוליכות!).""", "שאלה 2, מועד א' תשפ\"ו + שאלה 3, מועד ב' תשפ\"ד"),
])

if __name__ == "__main__":
    for key, (fmt, mock) in M.items():
        p = CH / f"{key}_forecast.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["format"], d["mock"] = fmt, mock
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(key, len(mock))
