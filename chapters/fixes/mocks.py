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
M["rnd"] = ("4 שאלות פתוחות, 90 דקות (עם תוספת כשעתיים). עונים על כל השאלות; במילואים בוחרים בין 3 ל-4 – ואם עונים על שתיהן, ניקוד כפול על שני הסעיפים הטובים. מותרים 6 עמודים + דף נוסחאות רשמי בטופס.", [
    open_q("תהליך בזמן בדיד עם מקדמים אקראיים", 30, 95, r"""
$X[n]=A+B(-1)^n$, כאשר $A,B$ בלתי תלויים, $E[A]=E[B]=0$, $E[A^2]=\sigma_A^2$, $E[B^2]=\sigma_B^2$.
א. (10) מצאו את $\mu_X[n]$ ואת $R_X[n_1,n_2]$.
ב. (10) האם $X[n]$ סמ"ר? נמקו.
ג. (10) מגדירים $Y[n]=X[n]+X[n+1]$. האם $Y[n]$ סמ"ר? נמקו.""", r"""
**א.** $\mu_X=E[A]+(-1)^nE[B]=0$. $R_X=E[A^2]+\big((-1)^{n_1}+(-1)^{n_2}\big)E[AB]+(-1)^{n_1+n_2}E[B^2]=\sigma_A^2+(-1)^{n_1+n_2}\sigma_B^2$.

**ב.** נראה כאילו $(-1)^{n_1+n_2}$ תלוי בזמנים – **אבל** $(-1)^{n_1+n_2}=(-1)^{n_2-n_1}\cdot(-1)^{2n_1}=(-1)^{n_2-n_1}$.
⇐ $R_X[k]=\sigma_A^2+(-1)^k\sigma_B^2$ – תלוי **רק בהפרש** $k=n_2-n_1$, והתוחלת קבועה ⇐ **כן סמ"ר**.
(מלכודת: תמיד לבדוק אם ביטוי שנראה "תלוי בזמן" הוא בעצם פונקציה של ההפרש. בשאלה שלך, $n_1n_2$ – באמת לא.)

**ג.** $Y[n]=2A+B\big((-1)^n+(-1)^{n+1}\big)=2A$ – קבוע ⇐ $R_Y=4\sigma_A^2$ ⇐ **סמ"ר**.""", "בסגנון שאלה 1 במבחן שלך (A+nB וההפרש)"),
    open_q("מסנן על אות מוגבל-סרט", 30, 95, r"""
$X(t)$ סמ"ר, תוחלת 0, $S_X(f)=1$ עבור $|f|\le2$ ו-0 אחרת. המערכת: $H(f)=1-\frac{|f|}2$ עבור $|f|\le2$ ו-0 אחרת.
א. (10) מצאו את $S_Y(f)$ ושרטטו (עם תחום וערכים).
ב. (10) חשבו את $E[|Y(t)|^2]$.
ג. (10) תנו מסנן $H_2(f)\ne0$ שעבורו $E[|Y(t)|^2]=0$.""", r"""
**א.** $S_Y=\left(1-\frac{|f|}2\right)^2$ עבור $|f|\le2$, **ו-0 אחרת**. שיא 1 ב-$f=0$, מתאפס ב-$\pm2$ (משיק לציר), לא משולש.

**ב.** $E[|Y|^2]=2\int_0^2\left(1-\frac f2\right)^2df=\frac43$.

**ג.** כל $H_2$ שמתאפס ב-$|f|\le2$, למשל $H_2=0$ ב-$|f|\le2$ ו-$1$ מחוץ.""", "בסגנון שאלה 2 במבחן שלך"),
    open_q("תהליך פואסון", 20, 80, r"""
לקוחות מגיעים לפי פואסון. בממוצע מגיע לקוח כל 30 שניות.
א. (7) מצאו את $\lambda$ (ללקוחות לדקה).
ב. (7) בשתי הדקות האחרונות הגיעו 5 לקוחות. מה ההסתברות שבדקה הקרובה לא יגיע אף אחד?
ג. (6) מה ההסתברות שבשלוש הדקות הקרובות יגיעו בדיוק 4?""", r"""
**א.** $\frac1\lambda=\frac12$ דקה ⇐ $\lambda=2$ לדקה.

**ב.** קטעים זרים – העבר לא משנה: $P(0\text{ בדקה})=e^{-2}\approx0.135$.

**ג.** $\lambda t=6$: $\frac{6^4}{4!}e^{-6}=54e^{-6}\approx0.134$.""", "בסגנון שאלה 3 במבחן שלך"),
    open_q("משערך לינארי – משתנים רציפים", 20, 80, r"""
$X\sim U[0,2]$, $N\sim\text{Exp}(2)$ (צפיפות $2e^{-2n}$), בלתי תלויים, ו-$Y=X+N$.
נתון: $\int_0^\infty xe^{-ax}dx=\frac1{a^2}$, $\int_0^\infty x^2e^{-ax}dx=\frac2{a^3}$.
א. (10) חשבו $E[Y]$ ו-$\mathrm{Var}(Y)$.
ב. (10) מצאו את המשערך הלינארי האופטימלי של $X$ בהינתן $Y$.""", r"""
**א.** $E[X]=1$, $\mathrm{Var}X=\frac4{12}=\frac13$. $E[N]=2\cdot\frac14=\frac12$, $E[N^2]=2\cdot\frac28=\frac12$, $\mathrm{Var}N=\frac14$.
$E[Y]=\frac32$, $\mathrm{Var}Y=\frac13+\frac14=\frac7{12}$.

**ב.** $\mathrm{Cov}(X,Y)=\mathrm{Var}X=\frac13$ ⇐ $\hat X=1+\frac{1/3}{7/12}\left(Y-\frac32\right)=1+\frac47\left(Y-\frac32\right)$ (שגיאה $\frac17$).""", "בסגנון שאלה 4 במבחן שלך"),
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
        [r"ב-50%, ונשאר פעיל ($V_{CE}\approx2.5\,V$)", "ב-50%, ונכנס לרוויה", "ב-33%, ונשאר פעיל", "לא משתנה – $I_C$ נקבע ע״י $R_C$"], 0, r"""
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
