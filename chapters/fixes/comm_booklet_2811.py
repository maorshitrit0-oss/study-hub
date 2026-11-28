"""Comm, Prof. Pinchasi's practice booklet (no official solutions) + Lurie's solved booklet (28/11/2026): solved by
Claude from the booklet PDF; numbers in python (Bessel values computed). Assumptions written in each solution.
Writes chapters/fix_2811_comm_booklet.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OK = "\n\n> 🔎 נבדק מחדש (28/11): הושווה לפתרון בחוברת הפתורה של ד\"ר לוריא – נכון."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נפתר במלואו מתוך החוברת (בלי פתרון רשמי); המספרים חושבו מחדש."
S, UNC = {}, set()

S["da021d87"] = r"""### 📘 מה צריך לדעת קודם
- $\cos^2a=\frac{1+\cos2a}{2}$.
- הספק על עומס $R$: טון במשרעת $V$ ⇐ $\frac{V^2}{2R}$. PEP = ההספק כשהמעטפה בשיאה.
- נצילות AM: הספק פסי הצד ÷ ההספק הכולל.
- גילוי קוהרנטי של AM (עם חסימת DC): $(S/N)_D=\eta\,\gamma$, $\gamma=\frac{S_R}{N_0W}$, $N_0=kT_0F$ ($-174+NF$ dBm/Hz).
- פריס: $F=F_1+\frac{F_2-1}{G_1}+\dots$; קו באורך $d$: $L=0.4\,d$ dB, $F=L$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $y_{AM}=A_c\cos^2(2\pi f_mt)\cos\omega_ct=\frac{A_c}{2}\left[1+\cos(4\pi f_mt)\right]\cos\omega_ct$ – AM בעומק $m=1$ עם טון ב-$2f_m$. המעטפה מגיעה ל-$A_c$ ⇐ $A_c=10\text{ V}$.
- נשא: משרעת $5\text{ V}$ ⇐ $P_c=\frac{25}{100}=0.25\text{ W}$; כל פס צד: משרעת $2.5\text{ V}$ ⇐ $0.0625\text{ W}$, שניים ⇐ $0.125\text{ W}$.
- ✅ $P=0.375\text{ W}$ ($25.7\text{ dBm}$); $PEP=\frac{10^2}{2\cdot50}=1\text{ W}$; $V_{rms}=\sqrt{0.375\cdot50}=4.33\text{ V}$; $\eta=\frac{0.125}{0.375}=\frac13$.

**ב.** נדרש $(S/N)_D=15\text{ dB}$ ⇐ $\gamma=15-10\log_{10}\frac13=19.77\text{ dB}$.
$N_0W=-174+12+10\log_{10}5000=-125.0\text{ dBm}$ ⇐ $S_R=-125.0+19.77=-105.2\text{ dBm}$.
הפסד מותר: $25.74-(-105.24)=130.98\text{ dB}$ ⇐ $d=\frac{130.98}{0.4}$
✅ $d\approx327\text{ m}$.

**ג.** עם LNA ($F=2$, $G=L$) באמצע, ושני קטעי קו זהים ($L=10^{13.1}$):
$$F=L+\frac{2-1}{1/L}+\frac{L-1}{1}+\frac{F_R-1}{1/L}\approx L(1+1+1+14.85)=17.85L$$
בלי ה-LNA (סעיף ב): $F=L\cdot F_R=15.85L$, ואותו אות מגיע למקלט (ההגבר הכולל שוב $\frac1L$).
$$SNR_{out}=15-10\log_{10}\frac{17.85}{15.85}=15-0.52$$
✅ $\approx14.5\text{ dB}$ – כמעט בלי פגיעה, בטווח כפול.

**ד.** מופע שגוי $\theta$ מכפיל את האות ב-$\cos\theta$ (הרעש לא משתנה) ⇐ $SNR\propto\cos^2\theta$:
$$10\log_{10}\cos^2\theta\ge-5\ \Rightarrow\ |\cos\theta|\ge0.562$$
✅ $|\theta|\le55.8^\circ$.

💡 **הרעיון:** $\cos^2$ = AM מלא; LNA בתחילת קטע הקו השני כמעט מבטל את השפעת ההפסד שאחריו."""

S["b30ccd1c"] = r"""### 📘 מה צריך לדעת קודם
- ב-SSB רוחב הסרט ב-RF = רוחב אות המידע.
- $\mathcal F\{\text{sinc}^2(f_mt)\}=\frac{1}{f_m}\Lambda\!\left(\frac{f}{f_m}\right)$ (משולש ברוחב $\pm f_m$); כפל ב-$\cos(2\pi f_mt)$ מזיז ל-$\pm f_m$.
- מקלט סופרהטרודין: $f_{IF}=|f_{LO1}-f_{RF}|$; LO מעל ה-RF הופך את הספקטרום (USB⇄LSB).

### ✍️ הדרך המלאה (כמו במחברת)
**א.** ✅ רוחב מידע מרבי $4\text{ kHz}$ (רוחב ה-IF), ו-$B=4\text{ kHz}$ – פחות קוטע מידע, יותר מכניס רעש.

**ב.** המשולש סביב $f_m$ ובסביבת $-f_m$ (גובה $\frac{1}{2f_m}$), כל אחד מ-0 עד $2f_m$ ⇐ הספקטרום בין $0$ ל-$2f_m$ (וב-0 גובה 0).
✅ $2f_m\le4\text{ kHz}$ ⇐ $f_m\le2\text{ kHz}$.

**ג.** USB ב-$14.2\text{ MHz}$ תופס $14.200$–$14.204\text{ MHz}$; מסנן ה-IF מעביר $10.698$–$10.702\text{ MHz}$.
- LO מתחת: $f_{LO1}=14.200-10.698=3.502\text{ MHz}$ (נשאר USB, הנשא ב-$10.698$) ⇐ $f_{LO2}=10.698\text{ MHz}$.
- או LO מעל: $f_{LO1}=14.204+10.698=24.902\text{ MHz}$ (הופך ל-LSB, הנשא ב-$10.702$) ⇐ $f_{LO2}=10.702\text{ MHz}$.
✅ בקירוב: $f_{LO1}\approx3.5$ או $24.9\text{ MHz}$, $f_{LO2}\approx10.7\text{ MHz}$ (בדיוק – מוזז $2\text{ kHz}$ לקצה המסנן).

**ד.** LSB ב-$7.1\text{ MHz}$ תופס $7.096$–$7.100$. LO מתחת אינו אפשרי ($7.1-10.7<0$) ⇐ LO מעל, והספקטרום מתהפך (LSB⇐USB ב-IF):
$f_{LO1}=7.100+10.698=17.798\text{ MHz}$, $f_{LO2}=10.698\text{ MHz}$ ✅ (בקירוב $17.8$ ו-$10.7$).

💡 **הרעיון:** ב-SSB הנשא צריך לשבת בקצה מסנן ה-IF, לא באמצעו; LO מעל ה-RF הופך פס צד."""

S["16a13834"] = r"""> ⚠️ שני דברים בנוסח לא מסתדרים, והפתרון מציין את ההנחה: (1) $V_{peak}\cos^2(2\pi f_mt)=\frac{V_{peak}}{2}+\frac{V_{peak}}{2}\cos(2\pi\cdot2f_mt)$ – יש רכיב DC שמזיז את מרכז ה-FM ב-$k\frac{V_{peak}}{2}$, וטון ב-$2f_m=30\text{ kHz}$; (2) מסנן ה-LPF במוצא ($18\text{ kHz}$) צר מהטון הזה. נפתר לפי הכוונה המקובלת: "אין רכיב בתדר הנשא" ⇐ $J_0(\beta)=0$.

### 📘 מה צריך לדעת קודם
- FM בטון: קווים ב-$f_c\pm nf'$ במשרעות $J_n(\beta)$; $J_0(\beta)=0$ לראשונה ב-$\beta=2.405$.
- קרסון: $BW=2(\Delta f+f_{max})$. הספק FM קבוע: $\frac{A^2}{2R}$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** טון המידע ב-$f'=2f_m=30\text{ kHz}$, $\Delta f=k\frac{V_{peak}}{2}$, $\beta=\frac{\Delta f}{30\text{k}}$. $J_0=0$ ⇐ $\beta=2.405$ ⇐ $\Delta f=72.1\text{ kHz}$ ⇐
$$V_{peak}=\frac{2\cdot72.1\text{k}}{12\text{k}}=12.0\text{ V}$$
$BW\approx2(72.1+30)=204\text{ kHz}$; $P=\frac{100^2}{2\cdot50}=100\text{ W}=50\text{ dBm}$.
✅ $V_{peak}\approx12\text{ V}$, $BW\approx204\text{ kHz}$, $P=100\text{ W}$. (המרכז עצמו זז ב-$+72\text{ kHz}$ בגלל ה-DC.)

**ב.** $P_n=100\text{ W}\cdot J_n^2(2.405)$, בכל צד:

| $n$ | $J_n$ | הספק | dBm |
|---|---|---|---|
| 0 | 0 | 0 | – |
| 1 | 0.519 | 26.95 W | 44.3 |
| 2 | 0.432 | 18.64 W | 42.7 |
| 3 | 0.199 | 3.96 W | 36.0 |
| 4 | 0.065 | 0.42 W | 26.2 |

✅ קווים ב-$\pm30$, $\pm60$, $\pm90\text{ kHz}$ (ובשולי קרסון $\pm120$) מהמרכז.

**ג-ד.** סף FM: $\gamma_{th}=20(\beta+1)=68.1$ ($18.3\text{ dB}$) עם $\gamma=\frac{S_R}{N_0W}$, $N_0=-174+12=-162\text{ dBm/Hz}$, $W=18\text{ kHz}$ ($42.6\text{ dB}$):
$$S_{R,th}=-162+42.6+18.3=-101.1\text{ dBm}=7.8\cdot10^{-14}\text{ W}\ \Rightarrow\ V_{rms}=\sqrt{P\cdot300}=4.8\ \mu\text{V}$$
$SNR_{out}=\frac32\beta^2\gamma=\frac32\cdot5.78\cdot68.1=590$ ⇐ $27.7\text{ dB}$.
ל-$50\text{ dB}$: $\gamma=\frac{10^5}{1.5\cdot5.78}=11530$ ($40.6\text{ dB}$) ⇐ $S_R=-162+42.6+40.6=-78.8\text{ dBm}$. $f_{LO}=100\pm10.7\text{ MHz}$ (89.3 או 110.7).
✅ (לפי ההנחות למעלה.)

💡 **הרעיון:** $J_0(\beta)=0$ ⇐ $\beta=2.405$; הסף ב-FM קובע את ההספק המינימלי, ומעליו $SNR_{out}=\frac32\beta^2\gamma$."""
UNC.add("16a13834")

S["1f0ed0ca"] = r"""### 📘 מה צריך לדעת קודם
- גל ריבועי $0\to A_0$ עם $k_v=0.5$: $v(t)=\frac{A_0}{2}+\frac{2A_0}{\pi}\left[\cos\omega_0t-\frac13\cos3\omega_0t+\dots\right]$ (רק הרמוניות אי-זוגיות).
- $f_0=\frac{1}{T_0}=4\text{ kHz}$; מסנן עד $10\text{ kHz}$ מעביר DC ו-$4\text{ kHz}$ ($12\text{ kHz}$ נחתך; $8\text{ kHz}$ לא קיים).
- NBFM: $\beta\ll1$ ⇐ נשא + זוג קווים בגובה $\frac\beta2$; רוחב $2f_m$. מוצא מקלט FM: $SNR=\frac32\beta^2\gamma$ (טון).

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $x(t)=2\text{ mV}+\frac{8}{\pi}\text{ mV}\cdot\cos(2\pi\cdot4000t)=2+2.546\cos(2\pi\cdot4000t)\ [\text{mV}]$
$$P_x=2^2+\frac{2.546^2}{2}=4+3.24=7.24\ (\text{mV})^2=7.24\cdot10^{-6}$$
✅ (על נגד 1 Ω).

**ב.** ✅ FM צר-סרט (NBFM): $\Delta f=4\frac{\text{kHz}}{\text{V}}\cdot2.546\text{ mV}=10.2\text{ Hz}$ ⇐ $\beta=\frac{10.2}{4000}=2.55\cdot10^{-3}$; ה-DC מזיז את הנשא ב-$8\text{ Hz}$ ⇐ $f_c'=95\text{ MHz}+8\text{ Hz}$.
$$y(t)\approx A\left[\cos\omega_c't-\beta\sin(2\pi\cdot4000t)\sin\omega_c't\right],\qquad BW=2\cdot4=8\text{ kHz}$$

**ג.** $P_y=30\text{ dBm}=1\text{ W}$. נשא $\approx1\text{ W}$ ($30\text{ dBm}$); שני קווים ב-$f_c'\pm4\text{ kHz}$, כל אחד $\left(\frac\beta2\right)^2\cdot1\text{ W}=1.6\cdot10^{-6}\text{ W}$ ⇐ ✅ $-27.9\text{ dBm}$.

**ד.** מוצא הגלאי פרופורציוני לסטיית התדר: $z(t)\propto2.546\cos(2\pi\cdot4000t)$ (ה-DC נחסם).
$\gamma=\frac{S_R}{N_0W}$: $-70-(-174+3+40)=61\text{ dB}$ ⇐
$$SNR_{out}=\frac32\beta^2\gamma=1.5\cdot6.5\cdot10^{-6}\cdot1.26\cdot10^6=12.2$$
✅ $\approx10.9\text{ dB}$ – $\beta$ זעיר ⇐ FM כמעט לא משפר.

💡 **הרעיון:** אחרי המסנן נשאר DC + הרמוניה ראשונה; NBFM נראה כמו AM עם פסי צד בגובה $\frac\beta2$."""

S["71454527"] = r"""### 📘 מה צריך לדעת קודם
- $\sin(a-\frac\pi2)=-\cos a$, $\cos(a+\pi)=-\cos a$.
- SSB-LSB "בלי הגבר": כל טון $A\cos\omega t$ ⇐ $A\cos(\omega_c-\omega)t$ – אותו הספק כמו המידע.
- מנחת: $F=L$; פריס; ב-SSB קוהרנטי $SNR_{out}=\frac{S_R}{kT_0F\,B}$.

### ✍️ הדרך המלאה (כמו במחברת)
**א.** $2\pi f_0t_0=2\pi\cdot5\text{k}\cdot50\mu=\frac\pi2$:
$$x(t)=2A_0\sin(\omega_0t-\tfrac\pi2)-A_0\cos(2\omega_0t+\pi)=-2A_0\cos\omega_0t+A_0\cos2\omega_0t$$
קווים: $5\text{ kHz}$ (משרעת $4\text{ mV}$, זווית $\pi$), $10\text{ kHz}$ ($2\text{ mV}$, זווית 0). ✅ $BW=10\text{ kHz}$, DC $=0$, $P_x=\frac{(2A_0)^2+A_0^2}{2}=2.5A_0^2=10^{-5}$ ($-20\text{ dBm}$ על 1 Ω).

**ב.** $y_{LSB}(t)=-2A_0\cos[(\omega_c-\omega_0)t]+A_0\cos[(\omega_c-2\omega_0)t]$ – קווים ב-$f_c-5$ ו-$f_c-10\text{ kHz}$. ✅ $BW=10\text{ kHz}$, $P_y=P_x=10^{-5}$.

**ג.** לפי האיור: קו $40\text{ dB}$ ⇐ מגבר ($20\text{ dB}$, $F=10\text{ dB}$) ⇐ קו $40\text{ dB}$ ⇐ מגבר ⇐ קו $40\text{ dB}$. הגבר כולל $-80\text{ dB}$:
$$F=10^4+\frac{10-1}{10^{-4}}+\frac{10^4-1}{10^{-2}}+\frac{10-1}{10^{-6}}+\frac{10^4-1}{10^{-4}}=1.1\cdot10^8\ (80.4\text{ dB})$$
✅ $P_{y'}=-20-80=-100\text{ dBm}$.

**ד.** $z(t)\propto x(t)$. עם המקלט ($F_R=2$): $F_{tot}=1.1\cdot10^8+\frac{1}{10^{-8}}=2.1\cdot10^8$ ($83.2\text{ dB}$); $N=-174+83.2+40=-50.8\text{ dBm}$ ⇐
$SNR_{out}=-100+50.8\approx-49\text{ dB}$.
> ⚠️ לפי הקריאה הזו של האיור הקו לא שמיש (המגברים, $20\text{ dB}$, לא מפצים על קטעים של $40\text{ dB}$). אם הקטעים הם $4.0\text{ dB}$ או המגברים $40\text{ dB}$ – התוצאה שונה לגמרי. לבדוק מול האיור בחוברת.

💡 **הרעיון:** לפשט את $x(t)$ לטונים, SSB מעתיק אותם לפס אחד, ופריס על שרשרת קווים ומגברים."""
UNC.add("71454527")

FINE = ["e682a5c6", "722fecfe"]

FM14 = r"""### 📘 מה צריך לדעת קודם
- $SNR_B=\gamma=\frac{P}{kT_0FB}$ – יחס אות לרעש בכניסה, ברוחב סרט אות המידע $B$.
- מוצא מקלט FM: $SNR_{out}=3\beta^2\left(\frac{X_{rms}}{X_{max}}\right)^2\gamma$, כל עוד מעל הסף $\gamma\ge20(\beta+1)$.

### ✍️ הדרך המלאה (כמו במחברת)
1. $F=10^{0.4}=2.512$, $P=10^{-11.7}=2.0\cdot10^{-12}\text{ W}$ ($-87\text{ dBm}$).
2. $$\gamma=\frac{2.0\cdot10^{-12}}{1.38\cdot10^{-23}\cdot290\cdot2.512\cdot5\cdot10^5}=\frac{2.0\cdot10^{-12}}{5.03\cdot10^{-15}}=397\ \Rightarrow\ 26.0\text{ dB}$$
3. סף: $20(\beta+1)=100$ ⇐ $397>100$ ✓ (מעל הסף).
4. $$SNR_{out}=3\cdot4^2\cdot\frac{1}{12}\cdot397=4\cdot397=1588\ \Rightarrow\ 32.0\text{ dB}$$
✅ $\gamma\approx26\text{ dB}$, $SNR_{out}\approx32\text{ dB}$ (בבחינה 14.2.21, שאלה 2 – תשובה ג).

💡 **הרעיון:** קודם $\gamma$ ובדיקת סף, ואז שיפור ה-FM: $3\beta^2$ כפול יחס ההספק של האות."""


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "comm_todo.json").read_text(encoding="utf-8"))}
    out = [{"id": xs[k]["id"], "title": xs[k]["title"], "solution_md": s + DONE, "uncertain": k in UNC} for k, s in S.items()]
    out += [{"id": xs[k]["id"], "title": xs[k]["title"], "solution_md": xs[k]["solution_md"].rstrip() + OK, "uncertain": False} for k in FINE]
    # the student's notebook (CamScanner) repeats exam questions already fixed: hidden; the FM one is right
    for k in ("648b0f04", "c40d5113", "3111e585"):
        out.append({"id": xs[k]["id"], "title": xs[k]["title"], "duplicate": True})
    x = xs["5049a0ed"]
    out.append({"id": x["id"], "title": x["title"], "uncertain": False, "solution_md": FM14 + DONE})
    (HERE.parent / "fix_2811_comm_booklet.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
